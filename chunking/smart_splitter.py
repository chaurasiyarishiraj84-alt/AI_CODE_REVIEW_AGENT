"""Split source text into logical chunks, preserving function/class boundaries."""

from __future__ import annotations

import ast
from typing import List, Tuple


def _get_top_level_boundaries(source: str) -> List[Tuple[int, int]]:
    """Return (start_line, end_line) for each top-level definition in *source*."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    boundaries: List[Tuple[int, int]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1
            end = getattr(node, "end_lineno", node.lineno) - 1
            boundaries.append((start, end))
    return boundaries


def split_source(source: str, max_lines: int = 200) -> List[str]:
    """Split *source* into chunks of at most *max_lines* lines.

    Tries to break at top-level definition boundaries for Python files.
    Falls back to line-based splitting for other languages.
    """
    lines = source.splitlines(keepends=True)
    total = len(lines)
    if total <= max_lines:
        return [source]

    boundaries = _get_top_level_boundaries(source)

    if not boundaries:
        chunks: List[str] = []
        for i in range(0, total, max_lines):
            chunks.append("".join(lines[i : i + max_lines]))
        return chunks

    chunks = []
    current_start = 0

    for idx, (start, end) in enumerate(boundaries):
        if end - current_start >= max_lines and start > current_start:
            chunks.append("".join(lines[current_start:start]))
            current_start = start

    if current_start < total:
        remaining = "".join(lines[current_start:])
        if remaining.strip():
            chunks.append(remaining)

    return chunks or [source]