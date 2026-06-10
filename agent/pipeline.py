"""Module chaining — runs each pipeline stage in sequence."""

from __future__ import annotations

from typing import Callable, Optional

from agent.state_manager import ReviewState
from chunking.chunk_engine import chunk_file
from ingestion.cleanup import cleanup_repo
from ingestion.file_scanner import scan_files
from ingestion.github_cloner import clone_repo
from llm.confidence_engine import sort_issues
from llm.reviewer import review_file
from parser.ast_parser import parse_file
from utils.file_utils import relative_path
from app.logger import get_logger

logger = get_logger(__name__)


def run_pipeline(
    state: ReviewState,
    github_token: str = "",
    log_cb: Optional[Callable[[str], None]] = None,
    file_progress_cb: Optional[Callable[[int, int, str], None]] = None,
    max_files: int = 30,
) -> ReviewState:
    """Execute the full review pipeline."""

    def _log(msg: str) -> None:
        state.log(msg)
        logger.info(msg)

        if log_cb:
            log_cb(msg)

    state.status = "running"

    # =========================================================
    # 1. Clone Repository
    # =========================================================

    try:
        _log(f"Cloning {state.repo_url} ...")

        state.clone_path = clone_repo(
            state.repo_url,
            token=github_token,
            progress_cb=_log,
        )

    except Exception as exc:
        state.status = "error"
        state.error = f"Clone failed: {exc}"

        _log(f"ERROR: {state.error}")
        return state

    # =========================================================
    # 2. Scan Files
    # =========================================================

    try:
        all_files = scan_files(state.clone_path)

        state.source_files = all_files[:max_files]
        state.files_total = len(state.source_files)

        _log(
            f"Found {len(all_files)} source file(s); "
            f"reviewing first {state.files_total}."
        )

    except Exception as exc:
        state.status = "error"
        state.error = f"File scan failed: {exc}"

        cleanup_repo(state.clone_path)
        return state

    if state.files_total == 0:
        _log("No supported source files found.")

        state.status = "done"

        cleanup_repo(state.clone_path)
        return state

    # =========================================================
    # 3. Parse + Chunk + Review
    # =========================================================

    for idx, fpath in enumerate(state.source_files):

        rel = relative_path(fpath, state.clone_path)

        state.current_file = rel

        _log(f"[{idx + 1}/{state.files_total}] Processing {rel} ...")

        if file_progress_cb:
            file_progress_cb(
                idx + 1,
                state.files_total,
                rel,
            )

        try:
            parsed = parse_file(fpath)

            source = parsed.get("source", "")

            if not source.strip():
                _log(f"  Skipping empty file: {rel}")

                state.files_done += 1
                continue

            chunks = chunk_file(source, rel)

            _log(f"  {len(chunks)} chunk(s) to review.")

            file_issues = review_file(
                source=source,
                filepath=rel,
                chunks=chunks,
                log_cb=_log,
            )

            state.issues.extend(file_issues)

        except Exception as exc:

            logger.warning(
                "Error processing %s: %s",
                rel,
                exc,
            )

            _log(f"  ⚠ Skipped {rel} due to error: {exc}")

        state.files_done += 1

    # =========================================================
    # 4. Sort Issues
    # =========================================================

    state.issues = sort_issues(state.issues)

    # =========================================================
    # 5. Cleanup
    # =========================================================

    cleanup_repo(state.clone_path)

    _log("Temporary clone deleted.")

    state.status = "done"

    _log(
        f"✅ Review complete — "
        f"{len(state.issues)} total issue(s) found."
    )

    return state