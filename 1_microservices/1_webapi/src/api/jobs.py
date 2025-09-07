
from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException

from ..settings import settings

router = APIRouter()

@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    url = settings.prompt_service_url.rstrip('/') + f"/jobs/{job_id}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
