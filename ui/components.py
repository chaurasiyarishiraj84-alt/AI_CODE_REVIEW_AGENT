"""Reusable Streamlit UI components."""

from __future__ import annotations

from typing import List

import pandas as pd
import streamlit as st

from llm.confidence_engine import label_issue
from schemas.review_schema import ReviewIssue

_SEVERITY_COLOR = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🔵",
    "info": "⚪",
}

_ISSUE_TYPE_BADGE = {
    "bug": "🐛 Bug",
    "security": "🔒 Security",
    "performance": "⚡ Performance",
    "bad_practice": "⚠️ Bad Practice",
    "style": "✏️ Style",
}


def render_issue_card(issue: ReviewIssue) -> None:
    """Render a single issue as an expander card."""
    emoji = _SEVERITY_COLOR.get(issue.severity, "⚪")
    badge = _ISSUE_TYPE_BADGE.get(issue.issue_type, issue.issue_type)
    title = f"{emoji} [{issue.severity.upper()}] {badge} — line {issue.line}"

    with st.expander(title, expanded=issue.severity in ("critical", "high")):
        st.markdown(f"**{issue.comment}**")
        st.markdown(f"💡 **Suggestion:** {issue.suggestion}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Confidence", f"{issue.confidence}%")
        with col2:
            st.markdown(f"**Label:** {label_issue(issue)}")
        with col3:
            if issue.needs_verification:
                st.warning("⚠️ VERIFY THIS")

        if issue.confidence_reason:
            st.caption(f"Reason: {issue.confidence_reason}")


def render_issues_table(issues: List[ReviewIssue]) -> None:
    """Render a filterable dataframe table of all issues."""
    if not issues:
        st.info("No issues found.")
        return

    rows = [
        {
            "File": i.file,
            "Line": i.line,
            "Type": i.issue_type,
            "Severity": i.severity,
            "Confidence": i.confidence,
            "Comment": i.comment[:120] + ("…" if len(i.comment) > 120 else ""),
            "Verify?": "⚠️ YES" if i.needs_verification else "✅ No",
        }
        for i in issues
    ]
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_log_box(logs: List[str]) -> None:
    """Render a scrollable log output box."""
    log_text = "\n".join(logs[-100:])
    st.text_area("Live Logs", value=log_text, height=220, disabled=True, key="log_box")


def render_summary_metrics(issues: List[ReviewIssue]) -> None:
    """Render top-level count metrics."""
    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1

    verify_count = sum(1 for i in issues if i.needs_verification)

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("🔴 Critical", counts.get("critical", 0))
    col2.metric("🟠 High", counts.get("high", 0))
    col3.metric("🟡 Medium", counts.get("medium", 0))
    col4.metric("🔵 Low", counts.get("low", 0))
    col5.metric("⚠️ Verify", verify_count)
    col6.metric("📋 Total", len(issues))