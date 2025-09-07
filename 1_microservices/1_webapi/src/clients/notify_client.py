
from __future__ import annotations

import httpx

async def publish_notify(base_url: str, job_id: str, payload: dict) -> bool:
    url = base_url.rstrip('/') + f"/notify/job/{job_id}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        return True
