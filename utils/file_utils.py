"""File I/O utilities."""

from __future__ import annotations

from pathlib import Path


def read_text(path: Path, encoding: str = "utf-8") -> str:
    """Read a text file, falling back to latin-1 on decode errors."""
    try:
        return path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1", errors="replace")


def relative_path(path: Path, base: Path) -> str:
    """Return *path* relative to *base*, or the absolute string if not relative."""
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)