"""Application-wide constants and enumerations."""

from __future__ import annotations

from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueType(str, Enum):
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BAD_PRACTICE = "bad_practice"
    STYLE = "style"


SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx"}

MAX_CHUNK_TOKENS = 4000
CHUNK_OVERLAP = 200
CONFIDENCE_VERIFY_THRESHOLD = 70

LLM_MODEL = "llama-3.1-8b-instant"
LLM_MAX_TOKENS = 2048
LLM_TEMPERATURE = 0.1
LLM_MAX_RETRIES = 3

SAMPLE_REPO_URL = "https://github.com/getsentry/sentry-python"
SAMPLE_REPO_LABEL = "sentry-sdk (Python error monitoring)"

# Severity colour palette (used by Plotly charts)
SEVERITY_COLORS: dict[str, str] = {
    "critical": "#E53935",
    "high":     "#FB8C00",
    "medium":   "#FDD835",
    "low":      "#43A047",
    "info":     "#90A4AE",
}

ISSUE_TYPE_COLORS: dict[str, str] = {
    "bug":          "#E53935",
    "security":     "#7B1FA2",
    "performance":  "#1565C0",
    "bad_practice": "#E65100",
    "style":        "#00695C",
}

SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]