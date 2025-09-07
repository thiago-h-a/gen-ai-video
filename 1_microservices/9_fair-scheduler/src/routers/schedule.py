
from __future__ import annotations
import json, time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query

from ..util.logging import logger
from ..settings import settings
from ..models import EnqueueRequest, CompleteRequest, NextResponse
from ..store import Store
from ..drr import next_job, estimate_cost
from ..metrics import note_enqueue, note_complete

router = APIRouter()
store = Store()

@router.post("/enqueue")
async def enqueue(req: EnqueueRequest):
    cost = float(req.cost_estimate) if req.cost_estimate is not None else estimate_cost({
        "type": req.type,
        "payload": json.dumps(req.payload),
    })
    meta = {
        "creator_id": req.creator_id,
        "type": req.type,
        "state": "queued",
        "enqueued_ts": str(int(time.time()*1000)),
        "cost": str(cost),
        "payload": json.dumps(req.payload),
    }
    await store.put_job_meta(req.job_id, meta)
    await store.ensure_in_ring(req.type, req.creator_id)
    await store.enqueue(req.type, req.creator_id, req.job_id)
    note_enqueue(req.type)
    return {"ok": True, "job_id": req.job_id, "cost": cost}

@router.get("/next")
async def pick_next(type: str = Query(..., pattern="^(image|video)$")):
    job = await next_job(store, type)
    if job is None:
        from fastapi import Response
        return Response(status_code=204)
    job_id = job["job_id"]
    job["state"] = "running"
    await store.put_job_meta(job_id, {**job, "state": "running"})
    payload = json.loads(job.get("payload", "{}")) if isinstance(job.get("payload"), str) else job.get("payload", {})
    return NextResponse(job_id=job_id, creator_id=job["creator_id"], type=job["type"], cost=float(job.get("cost", 1)), payload=payload)

@router.post("/complete")
async def complete(req: CompleteRequest):
    meta = await store.get_job_meta(req.job_id)
    if not meta:
        raise HTTPException(404, "unknown job")
    new_state = "done" if req.success else "failed"
    meta.update({"state": new_state, "duration_ms": str(req.duration_ms or 0), "error": req.error or ""})
    await store.put_job_meta(req.job_id, meta)
    # metrics
    t = meta.get("type", "image")
    try:
        dur = int(meta.get("duration_ms", "0"))
    except Exception:
        dur = 0
    note_complete(t, req.success, dur)
    return {"ok": True}
