
from __future__ import annotations
import json, uuid

def new_job_id() -> str:
    return uuid.uuid4().hex[:12]

def estimate_cost(req: dict, type_: str) -> float:
    p = req.get("params", {}) or {}
    width = int(p.get("width", 768))
    height = int(p.get("height", 512))
    area = (width * height) / (768 * 512)
    if type_ == "image":
        frames = int(p.get("frames", 1))
        return max(1.0, frames * area)
    fps = int(p.get("fps", 8))
    seconds = int(p.get("seconds", 2))
    return max(1.0, fps * seconds * area / 4)
