"""Count tokens using tiktoken."""

from __future__ import annotations

import tiktoken

_ENCODING = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Return the number of tokens in *text*."""
    return len(_ENCODING.encode(text))