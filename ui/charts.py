"""Plotly-powered chart helpers for the Streamlit dashboard."""

from __future__ import annotations

from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.constants import SEVERITY_COLORS, ISSUE_TYPE_COLORS, SEVERITY_ORDER
from schemas.review_schema import ReviewIssue


def render_severity_chart(issues: List[ReviewIssue]) -> None:
    """Render a Plotly horizontal bar chart of issues by severity."""
    if not issues:
        st.info("No issues to chart.")
        return

    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue.severity] = counts.get(issue.severity, 0) + 1

    labels = [s for s in SEVERITY_ORDER if s in counts]
    values = [counts[s] for s in labels]
    colors = [SEVERITY_COLORS.get(s, "#90A4AE") for s in labels]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=[s.capitalize() for s in labels],
            orientation="h",
            marker_color=colors,
            text=values,
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Issues by Severity",
        xaxis_title="Count",
        yaxis_title="",
        height=300,
        margin=dict(l=10, r=30, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_issue_type_chart(issues: List[ReviewIssue]) -> None:
    """Render a Plotly pie chart of issues by type."""
    if not issues:
        st.info("No issues to chart.")
        return

    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue.issue_type] = counts.get(issue.issue_type, 0) + 1

    labels = [t.replace("_", " ").title() for t in counts]
    values = list(counts.values())
    colors = [ISSUE_TYPE_COLORS.get(t, "#607D8B") for t in counts]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            hole=0.4,
            textinfo="label+percent",
            hovertemplate="%{label}: %{value}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Issues by Type",
        height=320,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_confidence_histogram(issues: List[ReviewIssue]) -> None:
    """Render a Plotly histogram of confidence scores."""
    if not issues:
        st.info("No issues to chart.")
        return

    df = pd.DataFrame({"Confidence": [i.confidence for i in issues]})
    fig = px.histogram(
        df,
        x="Confidence",
        nbins=20,
        title="Confidence Score Distribution",
        labels={"Confidence": "Confidence (%)"},
        color_discrete_sequence=["#1565C0"],
    )
    fig.add_vline(
        x=70,
        line_dash="dash",
        line_color="red",
        annotation_text="Verify threshold (70%)",
        annotation_position="top right",
    )
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_file_heatmap(issues: List[ReviewIssue]) -> None:
    """Render a Plotly treemap showing issue density per file."""
    if not issues:
        return

    counts: dict[str, int] = {}
    for issue in issues:
        counts[issue.file] = counts.get(issue.file, 0) + 1

    df = pd.DataFrame(
        [{"File": f, "Issues": c} for f, c in counts.items()]
    ).sort_values("Issues", ascending=False).head(20)

    fig = px.treemap(
        df,
        path=["File"],
        values="Issues",
        title="Issue Density by File (top 20)",
        color="Issues",
        color_continuous_scale="Reds",
    )
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_severity_over_files(issues: List[ReviewIssue]) -> None:
    """Stacked bar: severity breakdown per file."""
    if not issues:
        return

    rows = [{"File": i.file, "Severity": i.severity.capitalize()} for i in issues]
    df = pd.DataFrame(rows)
    counts = df.groupby(["File", "Severity"]).size().reset_index(name="Count")

    top_files = (
        counts.groupby("File")["Count"].sum()
        .sort_values(ascending=False)
        .head(15)
        .index
    )
    counts = counts[counts["File"].isin(top_files)]

    fig = px.bar(
        counts,
        x="File",
        y="Count",
        color="Severity",
        title="Severity Breakdown per File (top 15)",
        color_discrete_map={s.capitalize(): c for s, c in SEVERITY_COLORS.items()},
        barmode="stack",
    )
    fig.update_layout(
        height=380,
        xaxis_tickangle=-35,
        margin=dict(l=10, r=10, t=40, b=80),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)