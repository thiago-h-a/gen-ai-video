
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, List

class VideoGenerateRequest(BaseModel):
    job_id: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1, max_length=2000)
    model_id: str = Field(..., min_length=1)
    params: Dict[str, float | int | str] = Field(default_factory=dict)

class VideoBatchItem(VideoGenerateRequest):
    pass

class VideoBatchRequest(BaseModel):
    items: List[VideoBatchItem]
