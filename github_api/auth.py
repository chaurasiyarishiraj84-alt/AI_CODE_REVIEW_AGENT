"""GitHub API authentication helpers."""

from __future__ import annotations

from github import Github, GithubException

from app.config import get_github_token
from app.logger import get_logger

logger = get_logger(__name__)


def get_github_client() -> Github | None:
    """Return an authenticated PyGithub client, or None if no token is set."""
    token = get_github_token()
    if not token:
        logger.warning("GITHUB_TOKEN not set — PR commenting unavailable.")
        return None
    return Github(token)


def verify_token() -> bool:
    """Return True if the stored GitHub token is valid."""
    client = get_github_client()
    if not client:
        return False
    try:
        _ = client.get_user().login
        return True
    except GithubException as exc:
        logger.error("GitHub token verification failed: %s", exc)
        return False