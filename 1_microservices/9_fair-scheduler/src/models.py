
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, Any, Literal

JobType = Literal["image", "video"]

class EnqueueRequest(BaseModel):
    job_id: str = Field(..., min_length=1)
    creator_id: str = Field(..., min_length=1)
    type: JobType
    cost_estimate: float | None = None
    payload: Dict[str, Any] = Field(default_factory=dict)

class NextResponse(BaseModel):
    job_id: str
    creator_id: str
    type: JobType
    cost: float
    payload: Dict[str, Any]

class CompleteRequest(BaseModel):
    job_id: str
    success: bool = True
    duration_ms: int | None = None
    error: str | None = None
