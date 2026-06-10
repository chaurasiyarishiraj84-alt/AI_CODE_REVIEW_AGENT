"""Validate a GitHub repository URL before cloning."""

from __future__ import annotations

import re
from dataclasses import dataclass

import requests

from app.logger import get_logger

logger = get_logger(__name__)

_GITHUB_RE = re.compile(
    r"^https?://github\.com/(?P<owner>[\w.\-]+)/(?P<repo>[\w.\-]+?)(?:\.git)?/?$"
)


@dataclass
class ValidationResult:
    valid: bool
    owner: str = ""
    repo: str = ""
    error: str = ""


def validate_repo_url(url: str) -> ValidationResult:
    """Return a ValidationResult after checking URL format and GitHub accessibility."""
    url = url.strip()
    m = _GITHUB_RE.match(url)
    if not m:
        return ValidationResult(valid=False, error="URL must be a valid GitHub repository URL.")

    owner, repo = m.group("owner"), m.group("repo")

    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        resp = requests.get(api_url, timeout=10, headers={"Accept": "application/vnd.github+json"})
        if resp.status_code == 404:
            return ValidationResult(valid=False, error="Repository not found (may be private or deleted).")
        if resp.status_code == 403:
            return ValidationResult(valid=False, error="Access denied — repository is private. Provide a GITHUB_TOKEN.")
        if resp.status_code != 200:
            return ValidationResult(valid=False, error=f"GitHub API returned HTTP {resp.status_code}.")
    except requests.RequestException as exc:
        logger.warning("GitHub API check failed: %s", exc)
        return ValidationResult(valid=False, error=f"Network error while validating: {exc}")

    logger.info("Validated repository: %s/%s", owner, repo)
    return ValidationResult(valid=True, owner=owner, repo=repo)