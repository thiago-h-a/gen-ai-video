
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class Settings:
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    quantum: int = int(os.getenv("QUANTUM", "2"))
    lock_ttl_ms: int = int(os.getenv("LOCK_TTL_MS", "500"))
    max_scan: int = int(os.getenv("MAX_SCAN", "128"))

settings = Settings()
