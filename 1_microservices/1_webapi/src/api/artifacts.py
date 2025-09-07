
from __future__ import annotations

from fastapi import APIRouter

from ..clients.s3_client import sign_artifact_url

router = APIRouter()

@router.get("/artifacts/{artifact_key:path}")
async def get_artifact(artifact_key: str):
    return {"url": sign_artifact_url(artifact_key)}
