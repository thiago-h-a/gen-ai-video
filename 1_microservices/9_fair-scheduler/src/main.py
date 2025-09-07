
from __future__ import annotations
import asyncio
from fastapi import FastAPI, Response
from .version import __version__
from .routers import health, schedule
from .metrics import refresher_task, render_latest
from .store import Store

app = FastAPI(title="ai-microgen — Fair Scheduler", version=__version__)
app.include_router(health.router)
app.include_router(schedule.router)

@app.on_event("startup")
async def _start_metrics_refresher():
    store = Store()
    asyncio.create_task(refresher_task(store))

@app.get("/metrics")
async def metrics() -> Response:
    data = render_latest()
    return Response(content=data, media_type="text/plain; version=0.0.4")
