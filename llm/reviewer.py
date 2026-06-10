"""
Send code chunks to Groq and return parsed issues.
Ollama is kept as fallback only.

Setup:
  1. Go to https://console.groq.com/keys
  2. Create free API key
  3. Add to .env:  GROQ_API_KEY=gsk_xxxx
  4. pip install groq
"""

from __future__ import annotations

import time
from typing import Callable, List, Optional

from app.config import get_groq_api_key
from app.logger import get_logger
from chunking.chunk_engine import Chunk
from llm.prompt_builder import build_review_prompt
from llm.response_parser import parse_llm_response
from schemas.review_schema import ReviewIssue

logger = get_logger(__name__)

GROQ_MODEL = "llama-3.3-70b-versatile"
OLLAMA_MODEL = "llama3.1:8b"


# ──────────────────────────────────────────────────────────────
# GROQ
# ──────────────────────────────────────────────────────────────

def _call_groq(messages: list[dict]) -> str:
    from groq import Groq
    client = Groq(api_key=get_groq_api_key())
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages, #type: ignore
        temperature=0.1,
        max_tokens=2048,
    )
    return resp.choices[0].message.content or ""


# ──────────────────────────────────────────────────────────────
# OLLAMA FALLBACK
# ──────────────────────────────────────────────────────────────

def _call_ollama(messages: list[dict]) -> str:
    import ollama
    resp = ollama.chat(
        model=OLLAMA_MODEL,
        messages=messages,
        options={"temperature": 0.1, "num_predict": 2048, "num_ctx": 8192},
    )
    return resp["message"]["content"]


# ──────────────────────────────────────────────────────────────
# DISPATCH — Groq first, Ollama if no key
# ──────────────────────────────────────────────────────────────

def _call_llm(messages: list[dict], log_cb) -> tuple[str, str]:
    groq_key = get_groq_api_key()

    if groq_key:
        try:
            log_cb(f"  ⏳ Calling Groq [{GROQ_MODEL}] ...")
            return _call_groq(messages), "Groq"
        except Exception as e:
            log_cb(f"  ⚠️ Groq failed: {e}")

    # Ollama fallback
    try:
        log_cb(f"  ⏳ Calling Ollama [{OLLAMA_MODEL}] ...")
        return _call_ollama(messages), "Ollama"
    except Exception as e:
        log_cb(f"  ❌ Ollama failed: {e}")
        log_cb("  💡 Add GROQ_API_KEY to .env — free at console.groq.com/keys")
        return "", "none"


# ──────────────────────────────────────────────────────────────
# REVIEW SINGLE CHUNK
# ──────────────────────────────────────────────────────────────

def review_chunk(
    chunk: Chunk,
    log_cb: Optional[Callable[[str], None]] = None,
) -> List[ReviewIssue]:

    messages = build_review_prompt(chunk)

    def _log(msg: str) -> None:
        logger.info(msg)
        if log_cb:
            log_cb(msg)

    _log(f"  🔍 [{chunk.index}/{chunk.total}] {chunk.file} ({chunk.token_count} tokens)")

    start = time.time()
    raw, provider = _call_llm(messages, _log)
    elapsed = time.time() - start

    if not raw:
        return []

    raw = raw.strip()
    preview = raw[:300].replace("\n", " ")
    _log(f"  📝 {provider} ({elapsed:.1f}s): {preview}{'...' if len(raw) > 300 else ''}")

    if "[" not in raw and "{" not in raw:
        _log("  ⚠️ No JSON found in response")
        return []

    issues = parse_llm_response(raw=raw, filepath=chunk.file)
    _log(f"  {'✅' if issues else '✓'} {len(issues)} issue(s) found")
    return issues


# ──────────────────────────────────────────────────────────────
# REVIEW ENTIRE FILE
# ──────────────────────────────────────────────────────────────

def review_file(
    source: str,
    filepath: str,
    chunks: List[Chunk],
    log_cb: Optional[Callable[[str], None]] = None,
    progress_cb: Optional[Callable[[int, int], None]] = None,
) -> List[ReviewIssue]:

    all_issues: List[ReviewIssue] = []
    for i, chunk in enumerate(chunks):
        issues = review_chunk(chunk=chunk, log_cb=log_cb)
        all_issues.extend(issues)
        if progress_cb:
            progress_cb(i + 1, len(chunks))
    return all_issues