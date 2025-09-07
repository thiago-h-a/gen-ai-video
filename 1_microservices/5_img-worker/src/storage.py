
from __future__ import annotations

import os
from pathlib import Path

from .settings import settings


def ensure_root() -> Path:
    root = Path(settings.artifacts_root)
    (root).mkdir(parents=True, exist_ok=True)
    return root


def save_artifact_png(model_id: str, job_id: str, data: bytes) -> str:
    """Save PNG under ARTIFACTS_ROOT/model_id/job_id.png and return artifact_key.

    The returned `artifact_key` follows the convention used by Web/API:
    "artifacts/<model_id>/<job_id>.png". Web/API can turn this into a URL.
    """
    root = ensure_root()
    out_dir = root / model_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{job_id}.png"
    out_path.write_bytes(data)

    # Return relative key starting with artifacts/
    # If ARTIFACTS_ROOT ends with "/artifacts", use that name; otherwise default "artifacts".
    base = Path(settings.artifacts_root).name
    if base == "/":
        base = "artifacts"
    if base != "artifacts":
        # normalize to artifacts/<model>/<file>
        return f"artifacts/{model_id}/{job_id}.png"
    return f"{base}/{model_id}/{job_id}.png"
