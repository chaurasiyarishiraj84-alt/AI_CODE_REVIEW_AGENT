"""Post AI review comments to a GitHub Pull Request."""

from __future__ import annotations

from typing import List

from github import Github, GithubException

from app.logger import get_logger
from formatter.github_formatter import format_pr_comment, format_summary_comment
from schemas.review_schema import ReviewIssue

logger = get_logger(__name__)


def post_pr_comments(
    client: Github,
    repo_full_name: str,
    pr_number: int,
    issues: List[ReviewIssue],
    repo_url: str = "",
) -> bool:
    """Post a summary comment and individual issue comments to a PR.

    Args:
        client: Authenticated PyGithub client.
        repo_full_name: e.g. "owner/repo"
        pr_number: Pull request number.
        issues: Reviewed issues to post.
        repo_url: Original repository URL for the summary.

    Returns:
        True on success, False on failure.
    """
    try:
        repo = client.get_repo(repo_full_name)
        pr = repo.get_pull(pr_number)

        summary = format_summary_comment(issues, repo_url)
        pr.create_issue_comment(summary)
        logger.info("Posted summary comment to PR #%d", pr_number)

        for issue in issues:
            body = format_pr_comment(issue)
            pr.create_issue_comment(body)

        logger.info("Posted %d issue comment(s) to PR #%d", len(issues), pr_number)
        return True

    except GithubException as exc:
        logger.error("Failed to post PR comments: %s", exc)
        return False