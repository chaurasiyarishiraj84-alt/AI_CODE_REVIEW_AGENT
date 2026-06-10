"""Simple in-memory cache for review results within a session."""

from __future__ import annotations

from typing import Any, Dict, Optional


class ReviewCache:
    """Thread-unsafe in-memory cache keyed by repo URL."""

    def __init__(self) -> None:
        self._store: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def clear(self) -> None:
        self._store.clear()

    def has(self, key: str) -> bool:
        return key in self._store


_global_cache = ReviewCache()


def get_cache() -> ReviewCache:
    return _global_cache