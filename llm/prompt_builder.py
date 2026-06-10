"""Prompt builder - works well with llama3.1:8b and larger models."""

from __future__ import annotations

from chunking.chunk_engine import Chunk

SYSTEM_PROMPT = """\
You are a strict code reviewer. Your job is to find real problems in code.

You MUST return a JSON array. Nothing else. No markdown. No explanation before or after.

Each issue must have these exact fields:
- file: filename string
- line: line number as string  
- issue_type: one of: bug, security, performance, bad_practice, style
- severity: one of: critical, high, medium, low, info
- comment: what is wrong (be specific)
- suggestion: how to fix it
- confidence: integer 0-100
- confidence_reason: one sentence why

IMPORTANT: Real code always has issues. Look hard for:
- Missing error handling
- Security risks (injections, hardcoded secrets, unvalidated input)
- Performance problems (unnecessary loops, repeated computation)
- Bad practices (broad exceptions, missing types, dead code)
- Style issues (magic numbers, poor naming)

Return [] ONLY if the code is truly perfect with zero issues at all.
""".strip()


def build_review_prompt(chunk: Chunk) -> list[dict[str, str]]:
    user_prompt = f"""Review this code carefully. File: {chunk.file}

```
{chunk.content}
```

Find every bug, security issue, bad practice, and performance problem.
Return ONLY a JSON array. Start your response with [ and end with ].
""".strip()

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]