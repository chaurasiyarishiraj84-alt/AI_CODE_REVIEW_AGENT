"""Remove temporary cloned repository directories."""

from __future__ import annotations

import shutil
from pathlib import Path

from app.logger import get_logger

logger = get_logger(__name__)


def cleanup_repo(path: Path) -> None:
    """Recursively delete *path* (the temp clone directory)."""
    if path and path.exists():
        shutil.rmtree(path, ignore_errors=True)
        logger.info("Cleaned up temp directory: %s", path)