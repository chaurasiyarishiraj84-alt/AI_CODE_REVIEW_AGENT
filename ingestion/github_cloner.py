"""Clone a GitHub repository to a local temp directory."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Callable, Optional

import git

from app.logger import get_logger

logger = get_logger(__name__)


def clone_repo(
    url: str,
    token: str = "",
    progress_cb: Optional[Callable[[str], None]] = None,
) -> Path:
    """Clone *url* and return the path to the local checkout."""
    if token:
        url = url.replace("https://", f"https://x-access-token:{token}@")

    tmp_dir = tempfile.mkdtemp(prefix="ai_review_")
    dest = Path(tmp_dir)

    def _log(msg: str) -> None:
        logger.info(msg)
        if progress_cb:
            progress_cb(msg)

    _log(f"Cloning {url} → {dest} …")
    git.Repo.clone_from(url, dest, depth=1)
    _log("Clone complete.")
    return dest