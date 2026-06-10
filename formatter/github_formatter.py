"""Format review issues as GitHub PR review comments."""

from __future__ import annotations

from typing import List

from schemas.review_schema import ReviewIssue

_SEVERITY_LABEL = {
    "critical": "🔴 CRITICAL",
    "high": "🟠 HIGH",
    "medium": "🟡 MEDIUM",
    "low": "🔵 LOW",
    "info": "⚪ INFO",
}


def format_pr_comment(issue: ReviewIssue) -> str:
    """Build the body text of a single PR comment for *issue*."""
    label = _SEVERITY_LABEL.get(issue.severity, issue.severity.upper())
    verify = (
        "\n\n> ⚠️ **VERIFY THIS** — confidence below 70%"
        if issue.needs_verification
        else ""
    )
    return (
        f"**[{label}] {issue.issue_type.replace('_', ' ').title()}**\n\n"
        f"{issue.comment}\n\n"
        f"💡 **Suggestion:** {issue.suggestion}\n\n"
        f"🎯 Confidence: {issue.confidence}% — {issue.confidence_reason}"
        f"{verify}"
    )


def format_summary_comment(issues: List[ReviewIssue], repo_url: str = "") -> str:
    """Build a top-level PR summary comment."""
    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1

    lines = ["## 🤖 AI Code Review Summary\n"]
    if repo_url:
        lines.append(f"**Repository:** {repo_url}\n")
    lines.append(f"**Total issues found:** {len(issues)}\n\n")
    for sev in ("critical", "high", "medium", "low", "info"):
        if sev in counts:
            lines.append(f"- {sev.capitalize()}: {counts[sev]}\n")
    return "".join(lines)