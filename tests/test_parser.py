"""Tests for the Python AST parser."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from parser.python_parser import parse_python_file


SAMPLE_CODE = '''
import os
from pathlib import Path

def greet(name: str) -> str:
    """Return a greeting."""
    return f"Hello, {name}"

class Dog:
    def bark(self):
        pass
'''


def test_parse_returns_dict():
    result = parse_python_file(SAMPLE_CODE, "test.py")
    assert isinstance(result, dict)
    assert result["language"] == "python"


def test_functions_extracted():
    result = parse_python_file(SAMPLE_CODE, "test.py")
    names = [e["name"] for e in result["entities"] if e["type"] == "function"]
    assert "greet" in names


def test_class_extracted():
    result = parse_python_file(SAMPLE_CODE, "test.py")
    names = [e["name"] for e in result["entities"] if e["type"] == "class"]
    assert "Dog" in names


def test_imports_extracted():
    result = parse_python_file(SAMPLE_CODE, "test.py")
    assert any("os" in imp for imp in result["imports"])


def test_syntax_error_handled():
    result = parse_python_file("def broken(:", "broken.py")
    assert result["language"] == "python"
    assert "parse_error" in result