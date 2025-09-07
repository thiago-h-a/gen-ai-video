
from __future__ import annotations
import shutil
from fastapi import APIRouter
from ..settings import settings
from ..storage import ensure_root

router = APIRouter()

@router.get("/healthz")
def healthz():
    return {"ok": True}

@router.get("/readyz")
def readyz():
    ff = bool(shutil.which("ffmpeg"))
    return {"ok": ff, "ffmpeg": ff, "artifacts_root": str(ensure_root())}

@router.get("/info")
def info():
    return {"codec_default": settings.default_codec, "width": settings.img_width, "height": settings.img_height}
