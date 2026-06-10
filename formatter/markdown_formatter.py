"""Format review results as Markdown."""

from __future__ import annotations

from typing import List

from llm.confidence_engine import label_issue
from schemas.review_schema import ReviewIssue

_SEVERITY_EMOJI = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🔵",
    "info": "⚪",
}


def to_markdown(issues: List[ReviewIssue], repo_url: str = "") -> str:
    """Render a Markdown report from *issues*."""
    lines: List[str] = ["# AI Code Review Report\n"]
    if repo_url:
        lines.append(f"**Repository:** {repo_url}\n")
    lines.append(f"**Total issues:** {len(issues)}\n\n---\n")

    files: dict[str, List[ReviewIssue]] = {}
    for issue in issues:
        files.setdefault(issue.file, []).append(issue)

    for filepath, file_issues in files.items():
        lines.append(f"\n## `{filepath}`\n")
        for issue in file_issues:
            emoji = _SEVERITY_EMOJI.get(issue.severity, "⚪")
            lines.append(
                f"### {emoji} [{issue.severity.upper()}] {issue.issue_type} — line {issue.line}\n"
            )
            lines.append(f"**{issue.comment}**\n\n")
            lines.append(f"💡 **Suggestion:** {issue.suggestion}\n\n")
            lines.append(
                f"🎯 Confidence: {issue.confidence}% — {label_issue(issue)}\n\n"
            )
            if issue.needs_verification:
                lines.append("> ⚠️ **VERIFY THIS** — confidence below 70%\n\n")
            lines.append("---\n")

    return "".join(lines)