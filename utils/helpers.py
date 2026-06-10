"""Miscellaneous helper utilities."""

from __future__ import annotations

import re
from typing import Any, Dict, List

from rich.table import Table
from rich.console import Console

from schemas.review_schema import ReviewIssue


def group_by_file(issues: List[ReviewIssue]) -> Dict[str, List[ReviewIssue]]:
    """Group issues by their file path."""
    result: Dict[str, List[ReviewIssue]] = {}
    for issue in issues:
        result.setdefault(issue.file, []).append(issue)
    return result


def extract_owner_repo(url: str) -> tuple[str, str]:
    """Parse 'owner' and 'repo' from a GitHub URL."""
    m = re.search(r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if m:
        return m.group(1), m.group(2)
    return "", ""


def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert a value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def print_rich_summary(issues: List[ReviewIssue], console: Console | None = None) -> None:
    """Print a Rich-formatted summary table to the console."""
    from app.logger import get_console
    con = console or get_console()

    table = Table(title="Code Review Summary", show_lines=True)
    table.add_column("File", style="cyan", no_wrap=False)
    table.add_column("Line", style="white", justify="right")
    table.add_column("Severity", style="bold", justify="center")
    table.add_column("Type", style="magenta")
    table.add_column("Comment", style="white")
    table.add_column("Confidence", justify="right")

    _SEV_STYLE = {
        "critical": "bold red",
        "high": "bold yellow",
        "medium": "yellow",
        "low": "green",
        "info": "dim",
    }

    for issue in issues:
        style = _SEV_STYLE.get(issue.severity, "")
        verify = " ⚠" if issue.needs_verification else ""
        table.add_row(
            issue.file,
            str(issue.line),
            f"[{style}]{issue.severity.upper()}[/{style}]",
            issue.issue_type.replace("_", " ").title(),
            issue.comment[:80] + ("…" if len(issue.comment) > 80 else ""),
            f"{issue.confidence}%{verify}",
        )

    con.print(table)