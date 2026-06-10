"""Centralized logging with Rich formatting for console output."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

_console = Console(stderr=True)

_rich_handler = RichHandler(
    console=_console,
    show_time=True,
    show_path=False,
    markup=True,
    rich_tracebacks=True,
)
_rich_handler.setFormatter(logging.Formatter("%(message)s", datefmt="[%X]"))

_file_handler = logging.FileHandler(LOG_DIR / "agent.log", encoding="utf-8")
_file_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)


def get_logger(name: str) -> logging.Logger:
    """Return a Rich-enabled logger for *name*."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.addHandler(_rich_handler)
        logger.addHandler(_file_handler)
        logger.setLevel(logging.DEBUG if os.getenv("DEBUG") else logging.INFO)
        logger.propagate = False
    return logger


def get_console() -> Console:
    """Return the shared Rich console instance."""
    return _console