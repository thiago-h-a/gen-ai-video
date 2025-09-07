
from __future__ import annotations
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .routers import registry as registry_router

app = FastAPI(title="ai-microgen — Model Registry")
app.include_router(registry_router.router)

@app.get("/", response_class=HTMLResponse)
def index() -> str:
    html = (Path(__file__).resolve().parent / 'static' / 'index.html').read_text(encoding='utf-8')
    return html

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=int(os.getenv("SERVICE_PORT", 8086)), reload=True)
