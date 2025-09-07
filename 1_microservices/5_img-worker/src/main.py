
"""FastAPI entrypoint for the GPU Worker."""
from __future__ import annotations

import os
import time
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .settings import settings
from .models import GenerateRequest
from .engine import generate_png
from .storage import save_artifact_png

app = FastAPI(title="ai-microgen — GPU Worker")

@app.get("/healthz")
def healthz() -> Dict[str, bool]:
    return {"ok": True}

@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (
        "<html><head><title>gpu-worker</title></head><body>"
        "<h1>gpu-worker</h1>"
        "<p>POST /generate with JSON: {job_id, prompt, model_id, params}</p>"
        "</body></html>"
    )

@app.post("/generate")
def generate(req: GenerateRequest):
    try:
        t0 = time.time()
        img = generate_png(
            req.prompt,
            req.model_id,
            width=settings.img_width,
            height=settings.img_height,
            seed=settings.seed,
        )
        key = save_artifact_png(req.model_id, req.job_id, img)
        dur = int((time.time() - t0) * 1000)
        return {"artifact_key": key, "duration_ms": dur}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=int(os.getenv("SERVICE_PORT", 8090)), reload=True)
