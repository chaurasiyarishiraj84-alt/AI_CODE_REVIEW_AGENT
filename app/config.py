"""Environment / configuration loader."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load local .env if present
_env_file = Path(__file__).parent.parent / ".env"
load_dotenv(_env_file, override=False)


# ─────────────────────────────────────────────────────────────
# API KEYS
# ─────────────────────────────────────────────────────────────

def get_openai_api_key() -> str:
    """
    Returns OpenAI API key.

    Does NOT crash if missing because
    Groq fallback may still exist.
    """
    return os.getenv("OPENAI_API_KEY", "").strip()


def get_groq_api_key() -> str:
    """
    Returns Groq API key.
    """
    return os.getenv("GROQ_API_KEY", "").strip()


def get_github_token() -> str:
    """
    Returns GitHub token.
    """
    return os.getenv("GITHUB_TOKEN", "").strip()


# ─────────────────────────────────────────────────────────────
# MODEL CONFIG
# ─────────────────────────────────────────────────────────────

def get_openai_model() -> str:
    """
    Default OpenAI model.
    """
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_groq_model() -> str:
    """
    Default Groq model.
    """
    return os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile",
    )


def get_llm_model() -> str:
    """
    Backward compatibility.
    """
    from app.constants import LLM_MODEL

    return os.getenv("LLM_MODEL", LLM_MODEL)


# ─────────────────────────────────────────────────────────────
# APP SETTINGS
# ─────────────────────────────────────────────────────────────

def get_log_level() -> str:
    return os.getenv("LOG_LEVEL", "INFO").upper()


def get_max_files() -> int:
    try:
        return int(os.getenv("MAX_FILES", "30"))
    except ValueError:
        return 30


# ─────────────────────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────────────────────

def validate_llm_keys() -> None:
    """
    Ensures at least ONE LLM provider exists.
    """

    openai_key = get_openai_api_key()
    groq_key = get_groq_api_key()

    if not openai_key and not groq_key:
        raise EnvironmentError(
            "No LLM API key found. "
            "Add OPENAI_API_KEY or GROQ_API_KEY "
            "to .env or HuggingFace Secrets."
        )

