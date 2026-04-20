"""
Logging Configuration Module
------------------------------
Sets up structured, production-grade logging with both
console and file handlers.

Responsibilities:
    - Configure root logger with proper formatting
    - Create rotating file handler for persistent logs
    - Provide module-level logger factory
    - Support different log levels per environment
"""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from app.core.config import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
) -> None:
    """
    Initialize the application logging system.

    Args:
        log_level: Override log level (defaults to settings.LOG_LEVEL)
        log_file: Override log file path (defaults to settings.LOG_FILE)
    """
    level = getattr(logging, (log_level or settings.LOG_LEVEL).upper(), logging.INFO)
    file_path = log_file or settings.LOG_FILE

    # ── Root Logger ──────────────────────────────────────────────
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers to prevent duplicate logs on reload
    root_logger.handlers.clear()

    formatter = logging.Formatter(
        fmt=settings.LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── Console Handler ──────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # ── File Handler (Rotating) ──────────────────────────────────
    if file_path:
        log_dir = os.path.dirname(file_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=file_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # ── Suppress Noisy Libraries ─────────────────────────────────
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

    root_logger.info("Logging initialized — level=%s, file=%s", level, file_path)


def get_logger(name: str) -> logging.Logger:
    """
    Factory for creating module-level loggers.

    Usage:
        logger = get_logger(__name__)
        logger.info("Something happened")
    """
    return logging.getLogger(name)
