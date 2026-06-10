from __future__ import annotations

import json
import re
from typing import List

from app.logger import get_logger
from schemas.review_schema import ReviewIssue

logger = get_logger(__name__)


def _extract_json_array(text: str) -> str | None:
    """
    Extract the first valid JSON array from text.
    Works even if the model adds explanations.
    """

    start = text.find("[")

    if start == -1:
        return None

    depth = 0

    for i in range(start, len(text)):

        if text[i] == "[":
            depth += 1

        elif text[i] == "]":
            depth -= 1

            if depth == 0:
                return text[start : i + 1]

    return None


def parse_llm_response(
    raw: str,
    filepath: str,
) -> List[ReviewIssue]:

    raw = raw.strip()

    raw = raw.replace("```json", "")
    raw = raw.replace("```", "")

    json_text = _extract_json_array(raw)

    if not json_text:

        logger.warning(
            "No JSON array found for %s",
            filepath,
        )

        logger.warning(
            "Raw response:\n%s",
            raw[:1000],
        )

        return []

    try:

        data = json.loads(json_text)

    except Exception as exc:

        logger.error(
            "JSON decode error for %s: %s",
            filepath,
            exc,
        )

        logger.error(
            "Failed JSON:\n%s",
            json_text[:1000],
        )

        return []

    if not isinstance(data, list):

        logger.warning(
            "Expected list but got %s",
            type(data).__name__,
        )

        return []

    issues: List[ReviewIssue] = []

    for item in data:

        if not isinstance(item, dict):
            continue

        item.setdefault("file", filepath)
        item.setdefault("line", "?")
        item.setdefault("confidence_reason", "")

        try:

            confidence = int(
                item.get("confidence", 80)
            )

            item["confidence"] = confidence

            item["needs_verification"] = (
                confidence < 70
            )

            issue = ReviewIssue(**item)

            issues.append(issue)

        except Exception as exc:

            logger.warning(
                "Skipping malformed issue in %s: %s",
                filepath,
                exc,
            )

            logger.warning(
                "Bad issue data: %s",
                item,
            )

    logger.info(
        "Parsed %d issue(s) from %s",
        len(issues),
        filepath,
    )

    return issues