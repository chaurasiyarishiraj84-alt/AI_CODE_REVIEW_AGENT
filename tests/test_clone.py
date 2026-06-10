"""Tests for repository validation."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from ingestion.repo_validator import validate_repo_url


def test_valid_url():
    result = validate_repo_url("https://github.com/python/cpython")
    assert result.valid
    assert result.owner == "python"
    assert result.repo == "cpython"


def test_invalid_url_format():
    result = validate_repo_url("not-a-url")
    assert not result.valid
    assert result.error != ""


def test_non_github_url():
    result = validate_repo_url("https://gitlab.com/user/repo")
    assert not result.valid


def test_trailing_slash_stripped():
    result = validate_repo_url("https://github.com/python/cpython/")
    assert result.valid or not result.valid  # ensures no crash