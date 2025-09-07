
from __future__ import annotations
from fastapi import APIRouter
from ..settings import settings

router = APIRouter()

@router.get("/healthz")
def healthz():
    return {"ok": True, "region": settings.region}
