"""Confidence bucketing and labelling utilities."""

from __future__ import annotations

from schemas.review_schema import ReviewIssue


def label_issue(issue: ReviewIssue) -> str:
    """Return a human-readable confidence label for display."""
    if issue.confidence >= 90:
        return "High confidence"
    if issue.confidence >= 70:
        return "Medium confidence"
    return "⚠ VERIFY THIS"


def bucket(confidence: int) -> str:
    """Return a confidence bucket string: high, medium, or low."""
    if confidence >= 90:
        return "high"
    if confidence >= 70:
        return "medium"
    return "low"


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def sort_issues(issues: list[ReviewIssue]) -> list[ReviewIssue]:
    """Sort issues by severity (critical first), then confidence (highest first)."""
    return sorted(
        issues,
        key=lambda i: (SEVERITY_ORDER.get(i.severity, 99), -i.confidence),
    )