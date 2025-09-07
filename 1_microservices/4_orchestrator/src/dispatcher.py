
from __future__ import annotations

import itertools
from typing import Dict, Tuple

import httpx

from .settings import settings

# Simple round-robin iterator over configured workers
_workers_cycle = itertools.cycle(settings.gpu_workers or ["http://localhost:8090"])

async def dispatch_generate(job: Dict[str, str]) -> Tuple[bool, str]:
    """Send the generation request to a GPU worker.

    Expects job dict with at least: job_id, prompt, model_id.
    Returns (ok, artifact_key_or_error).
    """
    target = next(_workers_cycle).rstrip('/') + "/generate"
    payload = {
        "job_id": job["job_id"],
        "prompt": job.get("prompt", ""),
        "model_id": job.get("model_id", "base-v1"),
        "params": {k.split(":",1)[1]: float(v) for k, v in job.items() if k.startswith("param:")},
    }
    try:
        async with httpx.AsyncClient(timeout=settings.worker_timeout) as client:
            r = await client.post(target, json=payload)
            r.raise_for_status()
            data = r.json()
            art = data.get("artifact_key") or data.get("artifact") or ""
            if not art:
                return False, "worker returned no artifact_key"
            return True, str(art)
    except httpx.HTTPStatusError as e:
        return False, f"worker status {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return False, str(e)

async def dry_run() -> Tuple[bool, str]:
    # Try a GET to the worker root as a reachability check
    target = next(_workers_cycle).rstrip('/')
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(target)
            return True, f"GET {target} -> {r.status_code}"
    except Exception as e:
        return False, f"GET {target} failed: {e}"
