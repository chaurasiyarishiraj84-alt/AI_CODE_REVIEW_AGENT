"""Integration-style tests for the pipeline (mocked LLM)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import patch, MagicMock
from agent.state_manager import ReviewState


def test_review_state_initial():
    state = ReviewState(repo_url="https://github.com/test/repo")
    assert state.status == "idle"
    assert state.issues == []
    assert state.progress() == 0.0


def test_review_state_progress():
    state = ReviewState(repo_url="https://github.com/test/repo")
    state.files_total = 10
    state.files_done = 5
    assert state.progress() == 0.5


def test_review_state_log():
    state = ReviewState(repo_url="https://github.com/test/repo")
    state.log("hello")
    assert "hello" in state.logs


def test_review_state_zero_total():
    state = ReviewState(repo_url="")
    assert state.progress() == 0.0