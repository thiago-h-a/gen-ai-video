
from __future__ import annotations

from typing import Optional

from .settings import settings
from .redis_queue import get_redis
from .models import JobState
from .state import set_status, publish_event
from .dispatcher import dispatch_generate, dry_run


async def consume_once() -> bool:
    """Pop one job ID and process it. Returns True if a job was processed."""
    r = get_redis(settings.redis_url)
    job_id = r.rpop(settings.queue_key)
    if not job_id:
        return False

    key = f"job:{job_id}"
    data = r.hgetall(key)
    if not data:
        # job disappeared; skip
        return False

    # running
    set_status(job_id, state=JobState.running, progress=0.1)
    await publish_event(job_id, "job.running", progress=0.1)

    ok, info = await dispatch_generate({"job_id": job_id, **data})
    if ok:
        set_status(job_id, state=JobState.done, progress=1.0, artifact_key=info)
        await publish_event(job_id, "job.done", artifact_key=info)
    else:
        set_status(job_id, state=JobState.failed, error=info)
        await publish_event(job_id, "job.failed", error=info)

    return True


async def dry_run_dispatch():
    return await dry_run()
