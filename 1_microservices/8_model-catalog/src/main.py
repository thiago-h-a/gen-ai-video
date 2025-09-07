
from __future__ import annotations
from fastapi import FastAPI
from .version import __version__
from .routers import health, catalog

app = FastAPI(title="ai-microgen — Model Catalog", version=__version__)
app.include_router(health.router)
app.include_router(catalog.router)
