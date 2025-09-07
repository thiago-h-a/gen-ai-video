
from __future__ import annotations
import asyncio, time
from fastapi import APIRouter, HTTPException
from ..settings import settings
from ..models import VideoGenerateRequest, VideoBatchRequest
from ..engine import make_video
from ..storage import local_save, maybe_upload_s3
from ..util.logging import logger

router = APIRouter()
_sem = asyncio.Semaphore(settings.max_concurrency)

@router.post("/generate/video")
async def generate_video(req: VideoGenerateRequest):
    async with _sem:
        t0 = time.time()
        width = int(req.params.get("width", settings.img_width))
        height = int(req.params.get("height", settings.img_height))
        fps = int(req.params.get("fps", 12))
        seconds = int(req.params.get("seconds", 3))
        codec = str(req.params.get("codec", settings.default_codec)).lower()
        if codec not in {"h264", "vp9"}:
            codec = settings.default_codec
        try:
            data, ext = make_video(req.prompt, req.model_id, width=width, height=height, fps=fps, seconds=seconds, codec=codec, seed=settings.seed)
            key = local_save(req.model_id, req.job_id, ext, data)
            ctype = "video/mp4" if ext == "mp4" else "video/webm"
            uploaded, key2 = maybe_upload_s3(key, data, ctype)
            dt = int((time.time() - t0) * 1000)
            return {"artifact_key": key2, "duration_ms": dt, "uploaded": uploaded, "fps": fps, "seconds": seconds}
        except Exception as e:
            logger.exception("video generation failed")
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/video/batch")
async def generate_video_batch(batch: VideoBatchRequest):
    results = []
    for item in batch.items:
        try:
            r = await generate_video(item)  # reuse
        except HTTPException as e:
            r = {"error": str(e.detail), "job_id": item.job_id}
        results.append(r)
    return {"items": results}
