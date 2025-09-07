
from __future__ import annotations
import json
from typing import Any, Dict, Optional

from .settings import settings
from .store import Store

def estimate_cost(meta: Dict[str, Any]) -> float:
    t = meta.get("type", "image")
    p = json.loads(meta.get("payload", "{}")) if isinstance(meta.get("payload"), str) else meta.get("payload", {})
    width = int(p.get("params", {}).get("width", 768))
    height = int(p.get("params", {}).get("height", 512))
    area_factor = (width * height) / (768 * 512)
    if t == "image":
        frames = int(p.get("params", {}).get("frames", 1))
        return max(1.0, frames * area_factor)
    else:
        fps = int(p.get("params", {}).get("fps", 8))
        seconds = int(p.get("params", {}).get("seconds", 2))
        return max(1.0, fps * seconds * area_factor / 4)

async def next_job(store: Store, type_: str) -> Optional[Dict[str, Any]]:
    if not await store.try_lock(type_):
        return None  # let caller retry shortly
    try:
        ring = await store.get_ring(type_)
        if not ring:
            return None
        ptr = await store.get_ptr(type_)
        n = len(ring)
        scans = min(n, settings.max_scan)
        for i in range(scans):
            idx = (ptr + i) % n
            creator = ring[idx]
            deficit = await store.incr_deficit(type_, creator, settings.quantum)
            job = await store.pop_if_affordable(type_, creator, deficit)
            if job is not None:
                # charge cost
                cost = float(job.get("cost", 1))
                await store.incr_deficit(type_, creator, -int(cost))
                # advance pointer past the creator we just scheduled
                await store.set_ptr(type_, (idx + 1) % n)
                return job
        # if we scanned and found nothing affordable, advance pointer by 1 to avoid stickiness
        await store.set_ptr(type_, (ptr + 1) % n)
        return None
    finally:
        await store.unlock(type_)
