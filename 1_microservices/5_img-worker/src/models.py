
from __future__ import annotations

from typing import Dict
from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    job_id: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1, max_length=2000)
    model_id: str = Field(..., min_length=1)
    params: Dict[str, float] = Field(default_factory=dict)
