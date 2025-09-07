"""
High-level video generation pipeline:
1) Try Stability AI (text->image->video) if configured.
2) Fall back to a local animated placeholder.
3) Normalize to a streaming-friendly MP4 (size/fps fixed) to preserve front-end layout.

This module intentionally mirrors the previous public function: generate_video(prompt, width, height, fps, duration) -> str
"""
from __future__ import annotations
import os
import io
import time
import json
import tempfile
import uuid
from typing import Optional

import requests

from ..config includes import (
    STABILITY_API_KEY,
    STABILITY_T2I_URL,
    STABILITY_I2V_URL,
    STABILITY_I2V_RESULT_URL,
    STABILITY_POLL_INTERVAL_SECONDS,
    STABILITY_TIMEOUT_SECONDS,
    DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_FPS, DEFAULT_DURATION,
)
from .transcode import reencode_to_spec, placeholder_video


class VideoGenError(RuntimeError):
    pass


def _stability_headers(accept: str) -> dict:
    if not STABILITY_API_KEY:
        raise VideoGenError("STABILITY_API_KEY not set")
    return {"Authorization": f"Bearer {STABILITY_API_KEY}", "Accept": accept}


def _download_to(path: str, resp: requests.Response) -> None:
    with open(path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def _stability_text_to_image(prompt: str, aspect_ratio: str = "16:9") -> str:
    """
    Call Stability Text-to-Image. Returns a local PNG path on success.
    """
    headers = _stability_headers("image/*")
    data = {"prompt": prompt, "aspect_ratio": aspect_ratio, "output_format": "png"}
    resp = requests.post(STABILITY_T2I_URL, headers=headers, data=data, timeout=60)
    ctype = resp.headers.get("content-type", "")
    if resp.status_code != 200 or not ctype.startswith("image"):
        # Bubble up any structured error details if present
        try:
            raise VideoGenError(f"T2I error {resp.status_code}: {resp.json()}")
        except Exception:
            raise VideoGenError(f"T2I error {resp.status_code}: {resp.text[:200]}")

    tmp_img = os.path.join(tempfile.gettempdir(), f"sd_kf_{uuid.uuid4().hex}.png")
    _download_to(tmp_img, resp)
    return tmp_img


def _stability_image_to_video(image_path: str, duration: int = 6) -> str:
    """
    Submit image to Stability's image-to-video, poll for a video result, and return local MP4 path.
    """
    headers = _stability_headers("application/json")
    with open(image_path, "rb") as imgf:
        files = {"image": (os.path.basename(image_path), imgf, "image/png")}
        dur = max(2, min(int(duration), 14))  # clamp to common SVD window
        data = {
            "seed": os.getenv("STABILITY_SEED", "0"),
            "cfg_scale": os.getenv("STABILITY_CFG_SCALE", "1.8"),
            "motion_bucket_id": os.getenv("STABILITY_MOTION_BUCKET_ID", "15"),
            "duration_seconds": str(dur),
        }
        resp = requests.post(STABILITY_I2V_URL, headers=headers, files=files, data=data, timeout=60)

    ctype = resp.headers.get("content-type", "")
    if resp.status_code == 200 and ctype.startswith("video"):
        out_path = os.path.join(tempfile.gettempdir(), f"svd_{uuid.uuid4().hex}.mp4")
        _download_to(out_path, resp)
        return out_path

    if resp.status_code not in (200, 202):
        try:
            raise VideoGenError(f"I2V submit error {resp.status_code}: {resp.json()}")
        except Exception:
            raise VideoGenError(f"I2V submit error {resp.status_code}: {resp.text[:200]}")

    try:
        job = resp.json()
    except Exception:
        raise VideoGenError(f"I2V submit returned non-JSON with content-type {ctype}")

    job_id = job.get("id") or job.get("job", {}).get("id")
    if not job_id:
        raise VideoGenError(f"I2V submit missing job id: {job}")

    # Poll until the video is ready (202 = still processing)
    deadline = time.time() + STABILITY_TIMEOUT_SECONDS
    result_url = STABILITY_I2V_RESULT_URL.format(id=job_id)
    while time.time() < deadline:
        r = requests.get(result_url, headers=_stability_headers("video/*"), timeout=60, stream=True)
        if r.status_code == 202:
            time.sleep(STABILITY_POLL_INTERVAL_SECONDS)
            continue
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("video"):
            out_path = os.path.join(tempfile.gettempdir(), f"svd_{uuid.uuid4().hex}.mp4")
            _download_to(out_path, r)
            return out_path
        # Provide structured error if possible
        try:
            raise VideoGenError(f"I2V result error {r.status_code}: {r.json()}")
        except Exception:
            raise VideoGenError(f"I2V result error {r.status_code}: {r.text[:200]}")

    raise VideoGenError("Timed out waiting for Stable Video Diffusion result")


def generate_video(prompt: str, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT,
                   fps: int = DEFAULT_FPS, duration: int = DEFAULT_DURATION) -> str:
    """
    Public entry point used by the FastAPI app.
    Returns a path to a normalized local MP4 file.
    """
    tmp_path: Optional[str] = None
    try:
        # Attempt the remote pipeline first
        img_path = _stability_text_to_image(prompt, aspect_ratio="16:9")
        tmp_path = _stability_image_to_video(img_path, duration=duration)
    except Exception as e:
        print(f"Stability pipeline error: {e}. Falling back to placeholder generation.")

    if not tmp_path:
        tmp_path = placeholder_video(prompt, width=width, height=height, fps=fps, duration=duration)

    normalized_path = os.path.join(tempfile.gettempdir(), f"gen_{uuid.uuid4().hex}_normalized.mp4")
    reencode_to_spec(tmp_path, normalized_path, width=width, height=height, fps=fps)
    return normalized_path
