
from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from .version import __version__
from .routers import health, generate_video

app = FastAPI(title="ai-microgen — Video Worker", version=__version__)
app.include_router(health.router)
app.include_router(generate_video.router)

@app.get("/")
def index():
    from pathlib import Path
    html = (Path(__file__).resolve().parent / 'static' / 'demo.html').read_text(encoding='utf-8')
    return HTMLResponse(html)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=int(os.getenv("SERVICE_PORT", 8091)), reload=True)
