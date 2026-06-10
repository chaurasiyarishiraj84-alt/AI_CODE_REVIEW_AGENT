"""Runtime state container for a single review run."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Callable

from schemas.review_schema import ReviewIssue


@dataclass
class ReviewState:
    repo_url: str = ""
    clone_path: Optional[Path] = None
    source_files: List[Path] = field(default_factory=list)
    issues: List[ReviewIssue] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    current_file: str = ""
    files_done: int = 0
    files_total: int = 0
    status: str = "idle"  # idle | running | done | error
    error: Optional[str] = None

    # Optional UI callback — called every time a log line is added
    # so the dashboard can update in real-time
    _ui_log_cb: Optional[Callable[[str], None]] = field(
        default=None, repr=False, compare=False
    )

    def log(self, msg: str) -> None:
        self.logs.append(msg)
        if self._ui_log_cb:
            try:
                self._ui_log_cb(msg)
            except Exception:
                pass  # Never crash the pipeline because of a UI callback

    def progress(self) -> float:
        """Return completion fraction 0.0–1.0."""
        if self.files_total == 0:
            return 0.0
        return self.files_done / self.files_total  # BUG FIX: was self.files_totals