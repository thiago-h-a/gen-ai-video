
"""Shared data models for ai-microgen microservices.

These Pydantic models define the DTOs passed between the Web/API, Prompt
Service, Orchestrator, and GPU Workers.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, validator


class JobState(str, Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"


class PromptRequest(BaseModel):
    """Payload submitted by a creative via the SPA."""
    prompt: str = Field(..., min_length=1, max_length=2000)
    model_id: str = Field(..., description="Target model identifier")
    params: Dict[str, float] = Field(default_factory=dict)

    @validator("model_id")
    def _model_nonempty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("model_id must be non-empty")
        return v


class QueueJob(BaseModel):
    """Internal job representation put onto the queue."""
    job_id: UUID = Field(default_factory=uuid4)
    prompt: str
    model_id: str
    params: Dict[str, float] = Field(default_factory=dict)

    def redis_payload(self) -> Dict[str, str]:
        """Serialize to a flat dict suitable for Redis HASH set."""
        return {
            "job_id": str(self.job_id),
            "prompt": self.prompt,
            "model_id": self.model_id,
            **{f"param:{k}": str(v) for k, v in self.params.items()},
        }


class JobStatus(BaseModel):
    """Lightweight job status stored in Redis (hash)."""
    job_id: UUID
    state: JobState = JobState.queued
    progress: float = 0.0
    artifact_key: Optional[str] = None
    error: Optional[str] = None

    @classmethod
    def from_redis(cls, data: Dict[str, str]) -> "JobStatus":
        jid = UUID(data.get("job_id"))
        st = JobState(data.get("state", JobState.queued))
        prog = float(data.get("progress", 0.0))
        art = data.get("artifact_key")
        err = data.get("error")
        return cls(job_id=jid, state=st, progress=prog, artifact_key=art, error=err)

    def to_redis(self) -> Dict[str, str]:
        return {
            "job_id": str(self.job_id),
            "state": self.state.value,
            "progress": str(self.progress),
            **({"artifact_key": self.artifact_key} if self.artifact_key else {}),
            **({"error": self.error} if self.error else {}),
        }


class ArtifactInfo(BaseModel):
    """Artifact location and metadata."""
    key: str
    content_type: str = "image/png"
    size_bytes: Optional[int] = None
    url: Optional[HttpUrl] = None


class SubmitResponse(BaseModel):
    job_id: UUID


class JobResponse(BaseModel):
    job: JobStatus
    artifact: Optional[ArtifactInfo] = None


# Example helpers for service implementations (not coupled to frameworks)

def make_queue_job(req: PromptRequest) -> QueueJob:
    return QueueJob(prompt=req.prompt, model_id=req.model_id, params=req.params)


def initial_job_status(job: QueueJob) -> JobStatus:
    return JobStatus(job_id=job.job_id, state=JobState.queued, progress=0.0)


def mark_running(status: JobStatus) -> JobStatus:
    status.state = JobState.running
    status.progress = max(status.progress, 0.1)
    return status


def mark_done(status: JobStatus, artifact_key: str) -> JobStatus:
    status.state = JobState.done
    status.progress = 1.0
    status.artifact_key = artifact_key
    return status


def mark_failed(status: JobStatus, error: str) -> JobStatus:
    status.state = JobState.failed
    status.error = error
    return status
