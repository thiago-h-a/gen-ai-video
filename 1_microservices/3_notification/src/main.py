
"""FastAPI app for the Notify Service."""
from __future__ import annotations

import asyncio
import json
import os
from typing import AsyncGenerator, Dict, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse

from .settings import settings
from .broker import get_broker, JobEvent
from .sse import format_sse

app = FastAPI(title="ai-microgen — Notify Service")

BROADCAST = "events:jobs"

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/events")
async def sse_events(job_id: Optional[str] = Query(default=None)):
    """Server-Sent Events endpoint.

    If `job_id` is provided, subscribe to the per-job channel; otherwise, listen
    to the broadcast channel.
    """
    broker = get_broker(settings.redis_url)
    channel = f"events:job:{job_id}" if job_id else BROADCAST

    async def event_stream() -> AsyncGenerator[bytes, None]:
        async for evt in broker.subscribe(channel):
            # evt is JobEvent
            payload = {"type": evt.type, "job_id": evt.job_id, **evt.data}
            yield format_sse(event=evt.type, data=json.dumps(payload)).encode("utf-8")

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/ws")
async def ws_endpoint(websocket: WebSocket, job_id: Optional[str] = None):
    await websocket.accept()
    broker = get_broker(settings.redis_url)
    channel = f"events:job:{job_id}" if job_id else BROADCAST
    try:
        async for evt in broker.subscribe(channel):
            payload = {"type": evt.type, "job_id": evt.job_id, **evt.data}
            await websocket.send_text(json.dumps(payload))
    except WebSocketDisconnect:
        # client disconnected
        return


@app.post("/notify/job/{job_id}")
async def publish_job(job_id: str, body: Dict[str, object]):
    """Publish a job event to broadcast and per-job channels.

    Body should contain at least `type` (e.g. job.running, job.done, job.failed)
    and may include arbitrary fields like `progress`, `artifact_key`, `error`.
    """
    evt_type = str(body.get("type") or "job.event")
    data = {k: v for k, v in body.items() if k != "type"}

    broker = get_broker(settings.redis_url)
    evt = JobEvent(type=evt_type, job_id=job_id, data=data)
    # broadcast to both channels
    await broker.publish(BROADCAST, evt)
    await broker.publish(f"events:job:{job_id}", evt)
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=int(os.getenv("SERVICE_PORT", 8083)), reload=True)
