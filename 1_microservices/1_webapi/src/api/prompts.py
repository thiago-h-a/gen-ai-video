
from __future__ import annotations

from typing import Dict

import httpx
from fastapi import APIRouter, Body, HTTPException, Request
from pydantic import BaseModel, Field

from ..settings import settings

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    model_id: str = Field(...)
    params: Dict[str, float] = Field(default_factory=dict)

@router.post("/prompts")
async def submit_prompt(request: Request, payload: PromptRequest | None = None):
    """Accept JSON or form-encoded fields and forward to Prompt Service."""
    if payload is None:
        # Allow HTML form on index page
        form = await request.form()
        payload = PromptRequest(prompt=str(form.get("prompt")), model_id=str(form.get("model_id")))

    url = settings.prompt_service_url.rstrip('/') + "/prompts"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(url, json=payload.model_dump())
            r.raise_for_status()
            return r.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
