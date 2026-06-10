"""Tests for the chunking engine."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from chunking.token_counter import count_tokens
from chunking.chunk_engine import chunk_file


def test_count_tokens_basic():
    assert count_tokens("hello world") == 2


def test_count_tokens_empty():
    assert count_tokens("") == 0


def test_chunk_file_single_chunk():
    source = "x = 1\n" * 10
    chunks = chunk_file(source, "test.py")
    assert len(chunks) == 1
    assert chunks[0].index == 1
    assert chunks[0].total == 1


def test_chunk_file_large():
    source = "x = 'aaaa'\n" * 800
    chunks = chunk_file(source, "big.py", max_tokens=500)
    assert len(chunks) > 1
    for c in chunks:
        assert c.token_count <= 600


def test_chunk_metadata():
    source = "a = 1\n" * 5
    chunks = chunk_file(source, "meta.py")
    for c in chunks:
        assert c.file == "meta.py"
        assert c.token_count > 0