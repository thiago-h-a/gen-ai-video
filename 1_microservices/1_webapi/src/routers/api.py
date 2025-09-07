
from __future__ import annotations
import os
from typing import Optional
import boto3
from botocore.client import Config
import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

from ..settings import settings
from ..util.logging import logger

router = APIRouter()

async def _forward_json(url: str, body: dict, headers: dict) -> JSONResponse:
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.post(url, json=body, headers=headers)
        return JSONResponse(status_code=r.status_code, content=r.json() if r.content else {})

@router.post("/prompts/image")
async def prompts_image(req: Request):
    data = await req.json()
    creator = req.headers.get("X-User-Id") or data.get("creator_id") or "anonymous"
    data["creator_id"] = creator
    url = settings.prompt_url.rstrip("/") + "/prompts/image"
    return await _forward_json(url, data, {"x-user-id": creator})

@router.post("/prompts/video")
async def prompts_video(req: Request):
    data = await req.json()
    creator = req.headers.get("X-User-Id") or data.get("creator_id") or "anonymous"
    data["creator_id"] = creator
    url = settings.prompt_url.rstrip("/") + "/prompts/video"
    return await _forward_json(url, data, {"x-user-id": creator})

@router.get("/catalog/models")
async def catalog_models(request: Request):
    # proxy query string
    qs = request.url.query
    url = settings.catalog_url.rstrip("/") + "/models"
    if qs:
        url += "?" + qs
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)
        return JSONResponse(status_code=r.status_code, content=r.json())

def _s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        region_name=settings.s3_region,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        config=Config(signature_version="s3v4"),
    )

@router.get("/artifacts/{key:path}")
async def artifact(key: str):
    if not settings.sign_artifacts:
        # Return a best-effort local-style URL for dev
        return {"url": f"/local/{key}", "signed": False}
    client = _s3_client()
    ctype = "application/octet-stream"
    if key.endswith(".png"): ctype = "image/png"
    elif key.endswith(".gif"): ctype = "image/gif"
    elif key.endswith(".mp4"): ctype = "video/mp4"
    elif key.endswith(".webm"): ctype = "video/webm"
    try:
        url = client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.artifacts_bucket, "Key": key, "ResponseContentType": ctype},
            ExpiresIn=3600,
        )
        return RedirectResponse(url)
    except Exception as e:
        logger.exception("signing failed")
        raise HTTPException(500, str(e))
