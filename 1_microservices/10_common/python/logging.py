
"""Logging utilities for ai-microgen.

Provides a single function `get_logger(name, json=False)` that returns a
configured logger. In dev (default), logs are human-readable. Set `json=True`
for structured logs suitable for ingestion into log pipelines.
"""
from __future__ import annotations

import json as _json
import logging
import os
import sys
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        # Attach extras (any custom attributes)
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process",
            }:
                payload[key] = value
        return _json.dumps(payload, ensure_ascii=False)


def get_logger(name: str = "ai-microgen", *, json: bool | None = None, level: int | None = None) -> logging.Logger:
    """Return a configured logger.

    Args:
        name: Logger name.
        json: Force JSON format (True/False). If None, read from ENV `LOG_JSON`.
        level: Log level. If None, read from ENV `LOG_LEVEL` or default to INFO.
    """
    if json is None:
        json = os.getenv("LOG_JSON", "false").lower() in {"1", "true", "yes"}
    if level is None:
        level_name = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Avoid duplicate handlers if re-created in notebooks/hot-reloaders
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler = logging.StreamHandler(sys.stdout)
        if json:
            handler.setFormatter(JsonFormatter())
        else:
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
            )
        logger.addHandler(handler)
    return logger


# Convenience default logger
logger = get_logger()
