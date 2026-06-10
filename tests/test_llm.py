"""Tests for LLM response parsing and confidence engine."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from llm.response_parser import parse_llm_response
from llm.confidence_engine import label_issue, bucket, sort_issues
from schemas.review_schema import ReviewIssue


VALID_JSON = '''[
  {
    "file": "app.py",
    "line": "10",
    "issue_type": "bug",
    "severity": "high",
    "comment": "Potential null dereference",
    "suggestion": "Check for None before access",
    "confidence": 85,
    "confidence_reason": "Clear pattern"
  }
]'''

LOW_CONFIDENCE_JSON = '''[
  {
    "file": "app.py",
    "line": "5",
    "issue_type": "style",
    "severity": "low",
    "comment": "Possibly bad naming",
    "suggestion": "Rename variable",
    "confidence": 60,
    "confidence_reason": "Subjective"
  }
]'''


def test_parse_valid_json():
    issues = parse_llm_response(VALID_JSON, "app.py")
    assert len(issues) == 1
    assert issues[0].severity == "high"
    assert issues[0].confidence == 85


def test_parse_empty_array():
    issues = parse_llm_response("[]", "app.py")
    assert issues == []


def test_parse_malformed_json():
    issues = parse_llm_response("not json at all", "app.py")
    assert issues == []


def test_needs_verification_flag():
    issues = parse_llm_response(LOW_CONFIDENCE_JSON, "app.py")
    assert len(issues) == 1
    assert issues[0].needs_verification is True


def test_label_high_confidence():
    issue = parse_llm_response(VALID_JSON, "app.py")[0]
    assert "confidence" in label_issue(issue).lower()


def test_label_low_confidence():
    issue = parse_llm_response(LOW_CONFIDENCE_JSON, "app.py")[0]
    assert "VERIFY" in label_issue(issue)


def test_sort_issues():
    sorted_issues = sort_issues(parse_llm_response(VALID_JSON, "app.py"))
    assert isinstance(sorted_issues, list)


def test_bucket():
    assert bucket(95) == "high"
    assert bucket(75) == "medium"
    assert bucket(50) == "low"