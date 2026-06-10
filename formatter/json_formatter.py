"""Format review results as JSON."""

from __future__ import annotations

import json
from typing import List

from schemas.review_schema import ReviewIssue


def to_json(issues: List[ReviewIssue], indent: int = 2) -> str:
    """Serialize a list of ReviewIssue objects to a JSON string."""
    return json.dumps(
        [issue.model_dump() for issue in issues],
        indent=indent,
        ensure_ascii=False,
    )