
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class Settings:
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    queue_key: str = os.getenv("QUEUE_KEY", "queue:generate")
    notify_url: str = os.getenv("NOTIFY_URL", "http://localhost:8083")
    gpu_workers: list[str] = tuple(
        w.strip() for w in os.getenv("GPU_WORKERS", "http://localhost:8090").split(",") if w.strip()
    )
    worker_timeout: int = int(os.getenv("WORKER_TIMEOUT", "60"))
    autostart: bool = os.getenv("ORCH_AUTOSTART", "0") in {"1", "true", "yes"}

settings = Settings()
