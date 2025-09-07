
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class Settings:
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

settings = Settings()
