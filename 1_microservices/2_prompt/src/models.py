
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, Any

class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    model_id: str = Field(..., min_length=1)
    params: Dict[str, Any] = Field(default_factory=dict)
    creator_id: str | None = None
