
from __future__ import annotations
import httpx
from typing import Dict

from .settings import settings
from .models import JobStatus, JobState
from .redis_queue import get_redis


async def publish_event(job_id: str, type: str, **data):
    url = settings.notify_url.rstrip('/') + f"/notify/job/{job_id}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            await client.post(url, json={"type": type, **data})
        except Exception:
            # best-effort; don't crash orchestration if notify is unavailable
            pass


def set_status(job_id: str, *, state: JobState, progress: float | None = None, artifact_key: str | None = None, error: str | None = None) -> JobStatus:
    r = get_redis(settings.redis_url)
    key = f"job:{job_id}"
    update: Dict[str, str] = {"state": state.value}
    if progress is not None:
        update["progress"] = str(progress)
    if artifact_key:
        update["artifact_key"] = artifact_key
    if error:
        update["error"] = error
    r.hset(key, update)
    data = r.hgetall(key)
    status = JobStatus.from_redis(data)
    return status
