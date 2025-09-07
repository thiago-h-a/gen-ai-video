
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

    def to_redis(self) -> Dict[str, str]:
        return {
            "job_id": str(self.job_id),
            "state": self.state.value,
            "progress": str(self.progress),
            **({"artifact_key": self.artifact_key} if self.artifact_key else {}),
            **({"error": self.error} if self.error else {}),
        }
