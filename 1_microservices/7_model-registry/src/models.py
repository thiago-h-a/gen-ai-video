
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

Task = Literal["image", "video", "text", "multimodal"]

class Weights(BaseModel):
    type: Literal["s3", "uri", "fs"] = Field(..., description="Where weights live")
    bucket: Optional[str] = None
    key: Optional[str] = None
    uri: Optional[str] = None

class ModelManifest(BaseModel):
    id: str
    name: str
    task: Task
    version: str
    weights: Weights
    tags: List[str] = Field(default_factory=list)
    params: Dict[str, Any] = Field(default_factory=dict)

class ModelList(BaseModel):
    items: List[ModelManifest]
