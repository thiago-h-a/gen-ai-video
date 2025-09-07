
from __future__ import annotations
from typing import Dict

from .store import get_store
from .settings import settings

QUEUE_KEY = "queue:generate"

def enqueue_job(job_id: str) -> int:
    store = get_store(settings.redis_url)
    return store.lpush(QUEUE_KEY, job_id)
