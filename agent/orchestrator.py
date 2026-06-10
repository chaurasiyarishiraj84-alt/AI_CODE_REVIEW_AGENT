"""Master workflow orchestrator — entry point for starting a review."""

from __future__ import annotations

from typing import Callable, Optional

from agent.pipeline import run_pipeline
from agent.state_manager import ReviewState
from app.config import get_github_token
from app.logger import get_logger

logger = get_logger(__name__)


def start_review(
    repo_url: str,
    log_cb: Optional[Callable[[str], None]] = None,
    file_progress_cb: Optional[Callable[[int, int, str], None]] = None,
    max_files: int = 30,
) -> ReviewState:
    """
    Orchestrate a full code review for a GitHub repository.

    Args:
        repo_url: Public GitHub URL to review.
        log_cb: Optional callback receiving log strings.
        file_progress_cb: Optional callback(done, total, current_file).
        max_files: Maximum number of files to review.

    Returns:
        Completed ReviewState object.
    """

    state = ReviewState(repo_url=repo_url)

    github_token = get_github_token()

    logger.info(
        "Starting review for %s (max_files=%d)",
        repo_url,
        max_files,
    )

    return run_pipeline(
        state=state,
        github_token=github_token,
        log_cb=log_cb,
        file_progress_cb=file_progress_cb,
        max_files=max_files,
    )