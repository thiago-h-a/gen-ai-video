
from __future__ import annotations
from fastapi import FastAPI
from .routers import api, health

app = FastAPI(title="ai-microgen — Web/API", version="0.2.0")
app.include_router(health.router)
app.include_router(api.router, prefix="/api")

@app.get("/healthz")
def healthz():
    return {"ok": True}
