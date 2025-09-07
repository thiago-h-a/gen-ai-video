
from __future__ import annotations

from enum import Enum
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class JobState(str, Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"


class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    model_id: str = Field(...)
    params: Dict[str, float] = Field(default_factory=dict)


class SubmitResponse(BaseModel):
    job_id: UUID


class JobStatus(BaseModel):
    job_id: UUID
    state: JobState
    progress: float = 0.0
    artifact_key: Optional[str] = None
    error: Optional[str] = None

    @classmethod
    def from_redis(cls, data: Dict[str, str]):
        from uuid import UUID

        return cls(
            job_id=UUID(data["job_id"]),
            state=JobState(data.get("state", "queued")),
            progress=float(data.get("progress", 0.0)),
            artifact_key=data.get("artifact_key"),
            error=data.get("error"),
        )


class JobResponse(BaseModel):
    job: JobStatus
    artifact: Optional[Dict[str, str]] = None
