
"""FastAPI entrypoint for the Orchestrator."""
from __future__ import annotations

import asyncio
import os
from typing import Dict

from fastapi import FastAPI, Query

from .settings import settings
from .scheduler import consume_once, dry_run_dispatch

app = FastAPI(title="ai-microgen — Orchestrator")

@app.get("/healthz")
def healthz() -> Dict[str, bool]:
    return {"ok": True}

@app.post("/tick")
async def tick(max: int = Query(default=1, ge=1, le=50)):
    processed = 0
    for _ in range(max):
        did = await consume_once()
        if not did:
            break
        processed += 1
    return {"processed": processed}

@app.post("/dispatch/test")
async def dispatch_test():
    ok, detail = await dry_run_dispatch()
    return {"ok": ok, "detail": detail}

@app.on_event("startup")
async def on_startup():
    if settings.autostart:
        loop = asyncio.get_running_loop()
        loop.create_task(_bg_loop())

async def _bg_loop():
    # best-effort background consumer
    while True:
        try:
            did = await consume_once()
        except Exception as e:
            # Keep loop alive on unexpected errors
            did = False
        await asyncio.sleep(0.1 if did else 0.5)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=int(os.getenv("SERVICE_PORT", 8084)), reload=True)
