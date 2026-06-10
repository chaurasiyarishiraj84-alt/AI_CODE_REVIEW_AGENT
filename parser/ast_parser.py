"""Base AST loader — dispatches to language-specific parsers."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

from app.logger import get_logger
from parser.python_parser import parse_python_file

logger = get_logger(__name__)


def parse_file(path: Path) -> Dict[str, Any]:
    """Parse *path* and return a metadata dict."""
    suffix = path.suffix.lower()
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        logger.error("Cannot read %s: %s", path, exc)
        return {"source": "", "language": "unknown", "entities": [], "error": str(exc)}

    if suffix == ".py":
        return parse_python_file(source, str(path))

    return {
        "source": source,
        "language": "javascript" if suffix in {".js", ".jsx"} else "typescript",
        "entities": [],
    }