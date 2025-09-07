
"""Shared settings and lightweight client helpers for ai-microgen.

This module provides:
- Pydantic `Settings` reading env vars (with sensible local defaults)
- A minimal in-memory `FakeRedis` used if `redis` lib isn't installed
- Thin wrappers (`get_redis`, `sign_artifact_url`) that microservices can import

*Note*: These helpers avoid heavy dependencies in the scaffold. Replace with
real clients (redis-py/aioredis, boto3/minio) in later steps.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    from pydantic import BaseSettings
except Exception:  # pragma: no cover - pydantic should be available later
    class BaseSettings:  # minimal shim to avoid runtime import errors in bare env
        def __init__(self, **kwargs: Any):
            for k, v in kwargs.items():
                setattr(self, k, v)


class Settings(BaseSettings):
    # Core
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # S3/MinIO
    s3_endpoint: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    s3_region: str = os.getenv("S3_REGION", "us-east-1")
    s3_access_key: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY", "minioadmin")
    artifacts_bucket: str = os.getenv("ARTIFACTS_BUCKET", "artifacts")
    models_bucket: str = os.getenv("MODELS_BUCKET", "models")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_json: bool = os.getenv("LOG_JSON", "false").lower() in {"1", "true", "yes"}


settings = Settings()


# ---------------------------- Redis helper -----------------------------

class FakeRedis:
    """A tiny in-memory Redis-like store used for scaffolding.

    Provides a subset of methods used by microservices in this repo. This lets you
    run the scaffolding without installing external clients.
    """

    def __init__(self) -> None:
        self._hash: Dict[str, Dict[str, str]] = {}
        self._lists: Dict[str, list[str]] = {}

    # Hash operations
    def hset(self, key: str, mapping: Dict[str, str]) -> int:
        d = self._hash.setdefault(key, {})
        before = len(d)
        d.update({str(k): str(v) for k, v in mapping.items()})
        after = len(d)
        return int(after - before)

    def hgetall(self, key: str) -> Dict[str, str]:
        return dict(self._hash.get(key, {}))

    # List operations
    def lpush(self, key: str, value: str) -> int:
        lst = self._lists.setdefault(key, [])
        lst.insert(0, str(value))
        return len(lst)

    def rpop(self, key: str) -> Optional[str]:
        lst = self._lists.get(key)
        if not lst:
            return None
        return lst.pop() if lst else None

    def blpop(self, key: str, timeout: int = 0) -> Optional[str]:
        """Very naive blocking pop (busy-waits). For demo only."""
        end = time.time() + max(timeout, 0)
        while True:
            item = self.rpop(key)
            if item is not None:
                return item
            if timeout and time.time() >= end:
                return None
            time.sleep(0.05)


def get_redis(url: str | None = None):
    """Return a Redis-like client.

    - If redis-py is available, use it.
    - Otherwise, return FakeRedis.
    """
    url = url or settings.redis_url
    try:  # prefer real client if available
        import redis  # type: ignore

        return redis.Redis.from_url(url, decode_responses=True)
    except Exception:
        return FakeRedis()


# ---------------------------- S3 helper --------------------------------

def sign_artifact_url(key: str, ttl_seconds: int = 900) -> str:
    """Return a pseudo-signed URL for the given artifact key.

    In production, use `boto3` (AWS S3) or MinIO SDK to generate a pre-signed
    URL. This scaffold returns a deterministic HTTP URL against the configured
    endpoint to keep dependencies light.
    """
    if key.startswith("http://") or key.startswith("https://"):
        return key
    base = settings.s3_endpoint.rstrip("/")
    if not key.startswith("/"):
        key = "/" + key
    # Add a very naive signature marker for clarity (non-secure placeholder)
    return f"{base}{key}?mockSigned=1&ttl={ttl_seconds}"
