
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from typing import Dict

from ..models import ModelList, ModelManifest
from ..store import list_models, get_model, upsert_model
from ..settings import settings

router = APIRouter()

@router.get("/healthz")
def healthz():
    return {"ok": True}

@router.get("/models", response_model=ModelList)
def models():
    return ModelList(items=list_models())

@router.get("/models/{model_id}", response_model=ModelManifest)
def model_detail(model_id: str):
    m = get_model(model_id)
    if not m:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found"}})
    return m

@router.get("/models/{model_id}/weights")
def model_weights(model_id: str) -> Dict[str, str | None]:
    m = get_model(model_id)
    if not m:
        raise HTTPException(status_code=404, detail={"error": {"code": "not_found"}})
    w = m.weights
    return {"type": w.type, "bucket": w.bucket, "key": w.key, "uri": w.uri}

@router.post("/models", response_model=ModelManifest)
def upsert(body: ModelManifest):
    if not settings.mutable:
        raise HTTPException(status_code=403, detail="registry is read-only; set REGISTRY_MUTABLE=1")
    upsert_model(body)
    return body
