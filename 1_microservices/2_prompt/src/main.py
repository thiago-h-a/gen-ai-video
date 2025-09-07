
from __future__ import annotations
from fastapi import FastAPI
from .routers import routes

app = FastAPI(title="ai-microgen — Prompt Service", version="0.2.0")
app.include_router(routes.router)
