
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ModelSummary(BaseModel):
    id: str
    name: str
    family: str | None = None
    modalities: List[str] = Field(default_factory=list)
    default_version: str | None = None
    tags: List[str] = Field(default_factory=list)

class ModelVersion(BaseModel):
    model_id: str
    version: str
    params: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    evals: List[Dict[str, Any]] = Field(default_factory=list)

class ModelCard(BaseModel):
    model_id: str
    version: str | None = None
    format: str = "markdown"  # or "json"
    content: str

class UpsertModel(BaseModel):
    id: str
    name: str
    family: str | None = None
    modalities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    default_version: str | None = None

class UpsertVersion(BaseModel):
    model_id: str
    version: str
    params: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    evals: List[Dict[str, Any]] = Field(default_factory=list)
