"""Streamlit dashboard — main UI for the AI Code Review Agent."""

from __future__ import annotations

import re
from typing import Any, List

import streamlit as st

from agent.orchestrator import start_review
from agent.state_manager import ReviewState
from app.config import get_github_token
from app.constants import SAMPLE_REPO_URL, SAMPLE_REPO_LABEL
from formatter.json_formatter import to_json
from formatter.markdown_formatter import to_markdown
from ingestion.repo_validator import validate_repo_url
from schemas.review_schema import ReviewIssue
from ui.charts import (
    render_severity_chart,
    render_issue_type_chart,
    render_confidence_histogram,
    render_file_heatmap,
    render_severity_over_files,
)
from ui.components import (
    render_issue_card,
    render_issues_table,
    render_summary_metrics,
)
from utils.helpers import group_by_file


# ──────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ──────────────────────────────────────────────────────────────

def _init_session() -> None:
    defaults = {
        "repo_url": "",
        "state": None,
        "running": False,
        "logs": [],
        "review_history": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────

def _render_sidebar() -> int:
    with st.sidebar:
        st.header("⚙️ Settings")
        max_files = st.slider("Max files to review", 1, 100, 30)

        st.divider()

        st.header("🎯 Sample Repository")
        st.caption(SAMPLE_REPO_LABEL)
        if st.button("Load Sample Repo", use_container_width=True):
            st.session_state.repo_url = SAMPLE_REPO_URL
            st.rerun()

        st.divider()

        st.header("🕐 Recent Reviews")
        history: list = st.session_state.review_history
        if history:
            for url, count in reversed(history[-5:]):
                label = url.split("github.com/")[-1]
                with st.expander(f"🖥 {label}", expanded=False):
                    st.caption(f"{count} issue(s) found")
                    if st.button("Load", key=f"load_{url}"):
                        st.session_state.repo_url = url
                        st.rerun()
            if st.button("🗑 Clear History", use_container_width=True):
                st.session_state.review_history = []
                st.rerun()
        else:
            st.caption("No reviews yet.")

        st.divider()

        with st.expander("ℹ️ How it works"):
            st.markdown(
                """
1. Enter a public GitHub URL
2. Click **Start Review**
3. Agent clones, parses & chunks code
4. `qwen2.5-coder` reviews each chunk
5. Results appear with confidence scores
6. Download JSON or Markdown report
"""
            )

    return max_files


# ──────────────────────────────────────────────────────────────
# LIVE REVIEW RUN
# ──────────────────────────────────────────────────────────────

def _run_review_sync(
    repo_url: str,
    max_files: int,
    log_placeholder: Any,       # st.empty() instance — no type hint to avoid import
    progress_placeholder: Any,
    status_placeholder: Any,
) -> ReviewState:
    """
    Run the pipeline synchronously while updating Streamlit placeholders live.
    Each log_cb call updates the log box so the user sees real-time output.
    """
    log_lines: List[str] = []

    def log_cb(msg: str) -> None:
        log_lines.append(msg)
        st.session_state.logs = log_lines.copy()
        log_placeholder.text_area(
            "📋 Live Logs",
            value="\n".join(log_lines[-80:]),
            height=260,
            disabled=True,
            key=f"live_log_{len(log_lines)}",
        )

    def file_progress_cb(done: int, total: int, current_file: str) -> None:
        pct = done / max(total, 1)
        progress_placeholder.progress(
            pct,
            text=f"File {done}/{total}: `{current_file}`",
        )
        status_placeholder.info(f"⏳ Reviewing `{current_file}` ({done}/{total})...")

    return start_review(
        repo_url=repo_url,
        log_cb=log_cb,
        file_progress_cb=file_progress_cb,
        max_files=max_files,
    )


# ──────────────────────────────────────────────────────────────
# RESULTS
# ──────────────────────────────────────────────────────────────

def _render_results(state: ReviewState) -> None:
    issues = state.issues

    render_summary_metrics(issues)

    if state.status == "error":
        st.error(f"❌ Review failed: {state.error}")
    elif state.status == "done":
        if issues:
            st.success(
                f"✅ Review complete — **{len(issues)} issue(s)** found "
                f"across **{state.files_total} file(s)**."
            )
        else:
            st.warning(
                f"⚠️ Review complete — **0 issues** found across "
                f"**{state.files_total} file(s)**. "
                f"Try upgrading to `qwen2.5-coder:7b` for better results."
            )

    tab_names = ["📋 Overview", "📊 Table", "📁 By File", "📈 Charts", "📜 Logs", "⬇️ Export", "🐙 Post to PR"]
    tabs = st.tabs(tab_names)
    tab_overview, tab_table, tab_byfile, tab_charts, tab_logs, tab_export, tab_pr = tabs

    with tab_overview:
        _tab_overview(issues)
    with tab_table:
        _tab_table(issues)
    with tab_byfile:
        _tab_byfile(issues)
    with tab_charts:
        _tab_charts(issues)
    with tab_logs:
        _tab_logs(state)
    with tab_export:
        _tab_export(issues, state.repo_url)
    with tab_pr:
        _tab_pr(issues, state.repo_url)


def _tab_overview(issues: List[ReviewIssue]) -> None:
    if not issues:
        st.info("No issues to display.")
        return
    for issue in issues:
        render_issue_card(issue)


def _tab_table(issues: List[ReviewIssue]) -> None:
    st.subheader("All Issues")
    if not issues:
        st.info("No issues found.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        sev_opts = ["critical", "high", "medium", "low", "info"]
        sel_sev = st.multiselect("Severity", sev_opts, default=sev_opts)
    with col2:
        type_opts = ["bug", "security", "performance", "bad_practice", "style"]
        sel_types = st.multiselect("Issue Type", type_opts, default=type_opts)
    with col3:
        min_conf = st.slider("Min Confidence", 0, 100, 0)

    filtered = [
        i for i in issues
        if i.severity in sel_sev
        and i.issue_type in sel_types
        and i.confidence >= min_conf
    ]
    st.caption(f"Showing {len(filtered)} of {len(issues)} issues")
    render_issues_table(filtered)


def _tab_byfile(issues: List[ReviewIssue]) -> None:
    if not issues:
        st.info("No issues found.")
        return
    grouped = group_by_file(issues)
    for filepath, file_issues in sorted(grouped.items(), key=lambda x: -len(x[1])):
        counts: dict = {}
        for i in file_issues:
            counts[i.severity] = counts.get(i.severity, 0) + 1
        summary = "  ".join(f"{s}: {c}" for s, c in counts.items())
        with st.expander(f"📄 `{filepath}` — {len(file_issues)} issue(s)  |  {summary}"):
            for issue in file_issues:
                render_issue_card(issue)


def _tab_charts(issues: List[ReviewIssue]) -> None:
    if not issues:
        st.info("No issues to chart.")
        return
    col1, col2 = st.columns(2)
    with col1:
        render_severity_chart(issues)
    with col2:
        render_issue_type_chart(issues)
    render_confidence_histogram(issues)
    render_file_heatmap(issues)
    render_severity_over_files(issues)


def _tab_logs(state: ReviewState) -> None:
    logs = state.logs if state else st.session_state.get("logs", [])
    if not logs:
        st.info("No logs yet. Logs appear here during and after a review.")
        return
    st.text_area("Review Logs", value="\n".join(logs), height=400, disabled=True)
    st.caption(f"{len(logs)} log lines total")


def _tab_export(issues: List[ReviewIssue], repo_url: str) -> None:
    st.subheader("⬇️ Download Results")
    col1, col2 = st.columns(2)
    with col1:
        json_data = to_json(issues)
        st.download_button(
            "⬇️ Download JSON",
            data=json_data,
            file_name="review_results.json",
            mime="application/json",
            use_container_width=True,
        )
    with col2:
        md_data = to_markdown(issues, repo_url)
        st.download_button(
            "⬇️ Download Markdown",
            data=md_data,
            file_name="review_results.md",
            mime="text/markdown",
            use_container_width=True,
        )
    st.subheader("JSON Preview")
    st.code(json_data[:3000] + ("..." if len(json_data) > 3000 else ""), language="json")


def _tab_pr(issues: List[ReviewIssue], repo_url: str) -> None:
    st.subheader("🐙 Post Review to GitHub Pull Request")
    st.caption(
        "Posts a summary comment + one comment per issue directly onto a GitHub PR. "
        "Requires **GITHUB_TOKEN** to be set in your `.env`."
    )

    token = get_github_token()
    if not token:
        st.error("❌ GITHUB_TOKEN not set. Add it to your `.env` file.")
        return

    # Verify token directly with PyGithub to avoid name clash between
    # your local github/ folder and the installed PyGithub package.
    try:
        from github import Github, GithubException
        _check = Github(token)
        _check.get_user().login
        st.success("✅ GitHub token verified and ready.")
    except Exception:
        st.error("❌ GitHub token is invalid or expired. Check your .env.")
        return

    pr_url = st.text_input(
        "Pull Request URL",
        placeholder="https://github.com/owner/repo/pull/42",
    )

    sev_choices = ["critical", "high", "medium", "low", "info"]
    sel_sev = st.multiselect(
        "Only post issues with severity:",
        sev_choices,
        default=sev_choices,
    )

    filtered = [i for i in issues if i.severity in sel_sev]
    st.info(f"{len(filtered)} issue(s) will be posted based on selected severities.")

    col1, _ = st.columns([2, 3])
    with col1:
        post_btn = st.button(
            "🐙 Post Comments to PR",
            disabled=(not pr_url or not filtered),
            use_container_width=True,
        )

    if post_btn and pr_url:
        _do_post_pr(pr_url, filtered, repo_url, token)


def _do_post_pr(pr_url: str, issues: List[ReviewIssue], repo_url: str, token: str) -> None:
    m = re.match(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)", pr_url)
    if not m:
        st.error("Invalid PR URL. Format: https://github.com/owner/repo/pull/42")
        return

    repo_full = m.group(1)
    pr_number = int(m.group(2))

    def _severity_label(sev: str) -> str:
        return {
            "critical": "🔴 CRITICAL", "high": "🟠 HIGH",
            "medium": "🟡 MEDIUM", "low": "🔵 LOW", "info": "⚪ INFO",
        }.get(sev, sev.upper())

    def _issue_body(issue: ReviewIssue) -> str:
        label = _severity_label(issue.severity)
        verify = "\n\n> ⚠️ **VERIFY THIS** — confidence below 70%" if issue.needs_verification else ""
        return (
            f"**[{label}] {issue.issue_type.replace('_', ' ').title()}**\n\n"
            f"{issue.comment}\n\n"
            f"💡 **Suggestion:** {issue.suggestion}\n\n"
            f"🎯 Confidence: {issue.confidence}% — {issue.confidence_reason}"
            f"{verify}"
        )

    def _summary_body() -> str:
        counts: dict = {}
        for i in issues:
            counts[i.severity] = counts.get(i.severity, 0) + 1
        lines = ["## 🤖 AI Code Review Summary\n"]
        if repo_url:
            lines.append(f"**Repository:** {repo_url}\n")
        lines.append(f"**Total issues found:** {len(issues)}\n\n")
        for sev in ("critical", "high", "medium", "low", "info"):
            if sev in counts:
                lines.append(f"- {sev.capitalize()}: {counts[sev]}\n")
        return "".join(lines)

    try:
        from github import Github, GithubException
        client = Github(token)
        repo_obj = client.get_repo(repo_full)
        pr = repo_obj.get_pull(pr_number)
        with st.spinner("Posting comments to PR..."):
            pr.create_issue_comment(_summary_body())
            for issue in issues:
                pr.create_issue_comment(_issue_body(issue))
        st.success(f"✅ Posted summary + {len(issues)} comment(s) to PR #{pr_number}")
    except Exception as exc:
        st.error(f"Failed to post PR comments: {exc}")


# ──────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────

def render_dashboard() -> None:
    _init_session()

    max_files = _render_sidebar()

    st.title("🤖 AI Code Review Agent")
    st.caption(
        "Autonomous code review powered by **qwen2.5-coder** · "
        "AST parsing · Token-aware chunking · Plotly analytics"
    )

    repo_url = st.text_input(
        "GitHub Repository URL",
        value=st.session_state.repo_url,
        placeholder="https://github.com/owner/repo",
    )
    st.session_state.repo_url = repo_url

    col1, col2 = st.columns([3, 1])
    with col1:
        start_btn = st.button(
            "🚀 Start Review",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.running,
        )
    with col2:
        clear_btn = st.button(
            "🗑 Clear",
            use_container_width=True,
            disabled=st.session_state.running,
        )

    if clear_btn:
        st.session_state.state = None
        st.session_state.logs = []
        st.session_state.repo_url = ""
        st.rerun()

    if start_btn and repo_url:
        result = validate_repo_url(repo_url)
        if not result.valid:
            st.error(f"❌ {result.error}")
        else:
            st.session_state.running = True
            st.session_state.logs = []

            status_ph = st.empty()
            progress_ph = st.empty()
            log_ph = st.empty()
            status_ph.info("🚀 Starting review — cloning repository...")

            try:
                state = _run_review_sync(
                    repo_url=repo_url,
                    max_files=max_files,
                    log_placeholder=log_ph,
                    progress_placeholder=progress_ph,
                    status_placeholder=status_ph,
                )
                st.session_state.state = state
                st.session_state.logs = state.logs
                st.session_state.review_history.append((repo_url, len(state.issues)))
            except Exception as exc:
                st.error(f"❌ Unexpected error: {exc}")
            finally:
                st.session_state.running = False
                status_ph.empty()
                progress_ph.empty()
                log_ph.empty()

            st.rerun()

    if st.session_state.state is not None:
        st.divider()
        _render_results(st.session_state.state)