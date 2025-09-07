
from __future__ import annotations
import httpx
from fastapi import APIRouter, Request, HTTPException

from ..settings import settings
from ..models import PromptRequest
from ..util import new_job_id, estimate_cost

router = APIRouter()

@router.get("/healthz")
def healthz():
    return {"ok": True}

async def _enqueue(type_: str, body: dict, creator: str) -> dict:
    job_id = new_job_id()
    cost = estimate_cost(body, type_)
    payload = {"prompt": body["prompt"], "model_id": body["model_id"], "params": body.get("params", {})}
    req = {
        "job_id": job_id,
        "creator_id": creator,
        "type": type_,
        "cost_estimate": cost,
        "payload": payload,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(settings.fair_url.rstrip("/") + "/enqueue", json=req)
        if r.status_code >= 300:
            raise HTTPException(r.status_code, r.text)
    return {"job_id": job_id}

@router.post("/prompts/image")
async def prompts_image(req: Request, body: PromptRequest):
    creator = req.headers.get("X-User-Id") or (body.creator_id or "anonymous")
    return await _enqueue("image", body.model_dump(), creator)

@router.post("/prompts/video")
async def prompts_video(req: Request, body: PromptRequest):
    creator = req.headers.get("X-User-Id") or (body.creator_id or "anonymous")
    return await _enqueue("video", body.model_dump(), creator)
