"""Scan a cloned repository for supported source files."""

from __future__ import annotations

from pathlib import Path
from typing import List, Set

from app.constants import SUPPORTED_EXTENSIONS
from app.logger import get_logger

logger = get_logger(__name__)

_SKIP_DIRS: Set[str] = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    "dist", "build", ".tox", ".mypy_cache", ".pytest_cache",
}


def scan_files(repo_path: Path, extensions: Set[str] | None = None) -> List[Path]:
    """Recursively collect source files with supported extensions."""
    exts = extensions or SUPPORTED_EXTENSIONS
    found: List[Path] = []

    for path in repo_path.rglob("*"):
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix in exts:
            found.append(path)

    found.sort()
    logger.info("Found %d source files in %s", len(found), repo_path)
    return found