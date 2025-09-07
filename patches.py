#!/usr/bin/env python3
"""
This script materializes the upgraded backend structure, fully writing every file's contents
and deleting deprecated modules from the previous layout. It prints each created/overwritten
or deleted path so you can verify the changes.

IMPORTANT (API stability):
- Endpoints and request/response shapes are unchanged:
  POST /signup, POST /login, POST /generate, GET /videos
- This keeps your front-end layout/positioning intact.
"""
from __future__ import annotations
import os
import io
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()

# --- Desired project files (full contents embedded) --------------------------------------
FILES: dict[str, str] = {

    "app.py": r'''from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

# Internal modules (renamed & reorganized)
from backend.media.generator import generate_video
from backend.storage import upload_video
from backend.db import save_video_url, get_user_videos
from backend.security import create_access_token, register_user, authenticate_user, get_current_user


# -----------------------------------------------------------------------------
# FastAPI app with permissive CORS (unchanged surface so the front-end works)
# -----------------------------------------------------------------------------
app = FastAPI(title="Video Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # keep as-is to avoid breaking existing clients
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Schemas (kept identical to preserve front-end contract)
# -----------------------------------------------------------------------------
class PromptRequest(BaseModel):
    prompt: str


class UserRegister(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# -----------------------------------------------------------------------------
# Auth endpoints (surface unchanged)
# -----------------------------------------------------------------------------
@app.post("/signup")
async def signup(user: UserRegister):
    """
    Register a user by email & password.
    Returns 400 if the email already exists.
    """
    result = register_user(user.email, user.password)
    if not result:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"message": "User registered successfully"}


@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 Password flow-compatible login.
    - username field carries the user's email (kept for compatibility).
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["user_id"]})
    return {"access_token": access_token, "token_type": "bearer"}


# -----------------------------------------------------------------------------
# Core feature endpoints (surface unchanged)
# -----------------------------------------------------------------------------
@app.post("/generate")
async def generate(req: PromptRequest, current_user: dict = Depends(get_current_user)):
    """
    Generate a video from a text prompt, upload it, and save the URL.
    Behavior notes:
    - Uses Stability (text→image→video) when configured.
    - Falls back to a local placeholder animation if not configured.
    - Always normalizes to H.264/AAC MP4, 1280x720 @ 24 fps.
    """
    local_video_path: str | None = None
    try:
        # 1) Produce a video artifact (remote pipeline with safe local fallback)
        local_video_path = generate_video(
            req.prompt,
            width=1280,
            height=720,
            fps=24,
            duration=int(os.getenv("VIDEO_DURATION_SECONDS", "8")),
        )
        if not local_video_path or not os.path.exists(local_video_path):
            raise HTTPException(status_code=500, detail="Failed to generate video")

        # 2) Ship to Cloudinary and persist the resulting URL
        video_url = upload_video(local_video_path)
        if not video_url:
            raise HTTPException(status_code=500, detail="Failed to upload video")

        # 3) Persist for the authenticated user
        video_id = save_video_url(current_user["user_id"], video_url)
        if not video_id:
            raise HTTPException(status_code=500, detail="Failed to save video URL")

        return {"video_url": video_url, "video_id": video_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        # Always tidy up the local artifact
        try:
            if local_video_path and os.path.exists(local_video_path):
                os.remove(local_video_path)
        except Exception:
            pass


@app.get("/videos")
async def get_videos(current_user: dict = Depends(get_current_user)):
    """
    List previously generated videos for the authenticated user.
    """
    return {"videos": get_user_videos(current_user["user_id"])}
''',

    "backend/__init__.py": r'''"""Backend package root (empty by design)."""''',

    "backend/config.py": r'''"""
Centralized configuration so components share consistent settings.
Environment variables are read once at import-time and exposed as constants.
"""
from __future__ import annotations
import os

# --- JWT ---------------------------------------------------------------------
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback-secret-key")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# --- MongoDB -----------------------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "manim_videos")

# --- Cloudinary --------------------------------------------------------------
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

# --- Stability AI ------------------------------------------------------------
STABILITY_T2I_URL = os.getenv(
    "STABILITY_T2I_URL",
    "https://api.stability.ai/v2beta/stable-image/generate/sd3",
)
STABILITY_I2V_URL = os.getenv(
    "STABILITY_I2V_URL",
    "https://api.stability.ai/v2beta/image-to-video",
)
STABILITY_I2V_RESULT_URL = os.getenv(
    "STABILITY_I2V_RESULT_URL",
    "https://api.stability.ai/v2beta/image-to-video/result/{id}",
)
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_POLL_INTERVAL_SECONDS = int(os.getenv("STABILITY_POLL_INTERVAL_SECONDS", "3"))
STABILITY_TIMEOUT_SECONDS = int(os.getenv("STABILITY_TIMEOUT_SECONDS", "600"))

# --- Video defaults (match front-end expectations to avoid layout changes) ---
DEFAULT_WIDTH = int(os.getenv("VIDEO_WIDTH", "1280"))
DEFAULT_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "720"))
DEFAULT_FPS = int(os.getenv("VIDEO_FPS", "24"))
DEFAULT_DURATION = int(os.getenv("VIDEO_DURATION_SECONDS", "8"))
''',

    "backend/security.py": r'''"""
Authentication & authorization helpers:
- Password hashing (bcrypt via passlib)
- JWT creation & verification
- User registration & login helpers backed by MongoDB

NOTE: API surface intentionally mirrors the previous module so the app remains drop-in compatible.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pymongo import MongoClient

from .config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    MONGO_URI,
    MONGO_DB_NAME,
)

# OAuth2 token dependency (tokenUrl MUST stay "login" for compatibility)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Password hashing context
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mongo (very light abstraction)
_client = MongoClient(MONGO_URI)
_db = _client[MONGO_DB_NAME]
_users = _db["users"]


def _verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)


def _hash_password(plain: str) -> str:
    return _pwd_ctx.hash(plain)


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Produce a signed JWT carrying the payload in `data` plus an expiry (`exp`).
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """
    Extract the current user from the Authorization: Bearer token.
    Raises 401 if invalid or the user no longer exists.
    """
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if not user_id:
            raise cred_exc
    except JWTError:
        raise cred_exc

    user = _users.find_one({"_id": user_id})
    if not user:
        raise cred_exc

    return {"user_id": user["_id"], "email": user["email"]}


def register_user(email: str, password: str) -> Optional[Dict[str, str]]:
    """
    Create a new user document with a random ID and hashed password.
    Returns None if the email already exists or the insert fails.
    """
    try:
        if _users.find_one({"email": email}):
            return None
        user_id = __import__("os").urandom(16).hex()
        user_doc = {
            "_id": user_id,
            "email": email,
            "hashed_password": _hash_password(password),
        }
        _users.insert_one(user_doc)
        return {"user_id": user_id, "email": email}
    except Exception:
        return None


def authenticate_user(email: str, password: str) -> Optional[Dict[str, str]]:
    """
    Return minimal user info if the provided credentials are valid, else None.
    """
    user = _users.find_one({"email": email})
    if not user or not _verify_password(password, user.get("hashed_password", "")):
        return None
    return {"user_id": user["_id"], "email": user["email"]}
''',

    "backend/db.py": r'''"""
MongoDB data access layer for video metadata.
Kept intentionally tiny and explicit to remain easy to swap out later.
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional, List, Dict
from pymongo import MongoClient
from .config import MONGO_URI, MONGO_DB_NAME

_client = MongoClient(MONGO_URI)
_db = _client[MONGO_DB_NAME]
_videos = _db["videos"]

def save_video_url(user_id: str, video_url: str) -> Optional[str]:
    """
    Persist a generated video's URL for a user. Returns the inserted ID (as str).
    """
    try:
        doc = {"user_id": user_id, "video_url": video_url, "created_at": datetime.utcnow()}
        result = _videos.insert_one(doc)
        return str(result.inserted_id)
    except Exception:
        return None

def get_user_videos(user_id: str) -> List[Dict[str, str]]:
    """
    Return a list of the user's videos (id, url, created_at). Empty on error.
    """
    try:
        items = _videos.find({"user_id": user_id})
        return [
            {"id": str(it["_id"]), "url": it["video_url"], "created_at": it["created_at"]}
            for it in items
        ]
    except Exception:
        return []
''',

    "backend/storage.py": r'''"""
Cloud storage integration (Cloudinary).
Encapsulated so we can swap providers in the future.
"""
from __future__ import annotations
import os
from typing import Optional

import cloudinary
import cloudinary.uploader

from .config import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)

# Configure on import (no-ops if values are None; Cloudinary will error lazily)
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
)

def upload_video(video_path: str) -> Optional[str]:
    """
    Upload a local MP4 to Cloudinary as a 'video' resource.
    Returns the secure URL or None on failure.
    """
    try:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file {video_path} not found")
        result = cloudinary.uploader.upload_large(video_path, resource_type="video")
        return result.get("secure_url")
    except Exception:
        return None
''',

    "backend/media/__init__.py": r'''"""Media subpackage (video generation & processing)."""''',

    "backend/media/transcode.py": r'''"""
Video utilities:
- reencode_to_spec: normalize arbitrary input to a web-friendly MP4 (H.264/AAC)
- placeholder_video: quick local animated placeholder when remote generation is unavailable
"""
from __future__ import annotations
import os
from typing import List
import numpy as np
import cv2
import ffmpeg  # ffmpeg-python
from moviepy.editor import VideoClip, AudioFileClip


def reencode_to_spec(in_path: str, out_path: str, width: int = 1280, height: int = 720, fps: int = 24) -> None:
    """
    Re-encode to a widely compatible MP4:
    - Video: H.264 (yuv420p), letterboxed 16:9 without stretching
    - Audio: AAC 128 kbps
    - 'faststart' for progressive streaming
    """
    (
        ffmpeg
        .input(in_path)
        .output(
            out_path,
            vcodec="libx264",
            acodec="aac",
            vf=f"scale=w={width}:h={height}:force_original_aspect_ratio=decrease,"
               f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
            r=fps,
            movflags="+faststart",
            preset="fast",
            crf=23,
            audio_bitrate="128k",
        )
        .overwrite_output()
        .run(quiet=True)
    )


def _uuid4_hex() -> str:
    import uuid
    return uuid.uuid4().hex


def _wrap_text(text: str, max_chars: int = 40) -> List[str]:
    """
    Minimal word-wrap to ~max_chars per line (naive, but sufficient for overlay).
    """
    words = text.split()
    lines, line = [], []
    for w in words:
        # include spaces between words in the count
        if sum(len(x) for x in line) + len(line) + len(w) > max_chars:
            lines.append(" ".join(line))
            line = [w]
        else:
            line.append(w)
    if line:
        lines.append(" ".join(line))
    return lines


def _animate_frame(t: float, W: int, H: int, seed: int, text_lines: List[str]):
    """
    Generate a frame of animated procedural noise with a subtle vignette and moving text.
    """
    rng = np.random.default_rng(seed + int(t * 10))
    noise = (rng.random((H, W, 1)) * 255).astype(np.uint8)
    frame = np.concatenate([noise, noise, noise], axis=2)

    # Vignette (radial falloff)
    Y, X = np.ogrid[:H, :W]
    cx, cy = W / 2, H / 2
    dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    vignette = 1 - (dist / dist.max()) * 0.5
    frame = (frame * vignette[..., None]).astype(np.uint8)

    # Overlay prompt lines with a little vertical motion
    y = int(H * 0.2)
    for i, line in enumerate(text_lines[:5]):
        dy = int(5 * np.sin(t + i))
        cv2.putText(
            frame, line, (int(W * 0.08), y + dy),
            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA
        )
        y += int(H * 0.08)
    return frame


def placeholder_video(prompt: str, width: int = 1280, height: int = 720, fps: int = 24, duration: int = 8) -> str:
    """
    Produce a small placeholder MP4 locally so the UX remains intact even without remote providers.
    """
    lines = _wrap_text(prompt)
    seed = np.random.default_rng().integers(0, 2**31 - 1)

    def make_frame(t: float):
        return _animate_frame(t, width, height, int(seed), lines)

    clip = VideoClip(make_frame=make_frame, duration=duration)

    # Attach silent audio for better player compatibility (looped 1s WAV)
    silent_wav = os.path.join(os.getcwd(), "_silence.wav")
    if not os.path.exists(silent_wav):
        import wave, struct
        framerate = 44100
        with wave.open(silent_wav, "w") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(framerate)
            for _ in range(framerate):  # 1 second of silence
                wf.writeframes(struct.pack("<h", 0))

    try:
        from moviepy.audio.fx.all import audio_loop
        audio = AudioFileClip(silent_wav)
        audio = audio_loop(audio, duration=duration)
        clip = clip.set_audio(audio)
    except Exception:
        # No audio is fine; some environments may lack codecs
        pass

    tmp_path = os.path.join(os.getcwd(), f"placeholder_{_uuid4_hex()}.mp4")
    clip.write_videofile(tmp_path, fps=fps, codec="libx264", audio_codec="aac", preset="fast", verbose=False, logger=None)
    return tmp_path
''',

    "backend/media/generator.py": r'''"""
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
''',

    "Dockerfile": r'''FROM python:3.11-slim

# System dependencies (ffmpeg for encoding; X libs for OpenCV headless drawing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Keep using the project's existing requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

EXPOSE 8000

# Keep the same entrypoint to avoid front-end changes
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
''',

    "README.md": r'''# Video Generator API (FastAPI)

This backend exposes a tiny API to generate short videos from a text prompt.
It tries Stability AI first (text→image→video). If not configured, it falls back to a local
placeholder animation so your UI keeps working.

## Endpoints (unchanged)

- `POST /signup` – `{ email, password }` → registers a user  
- `POST /login` – OAuth2 password flow; use form fields `username` (email) and `password`  
  Returns `{ access_token, token_type }`  
- `POST /generate` – body `{ "prompt": "..." }` with `Authorization: Bearer <token>`  
  Returns `{ "video_url": "<https://...>", "video_id": "<id>" }`  
- `GET /videos` – lists the caller's previously generated videos

## Environment

Create a `.env` (or set env vars in your deploy):

```env
# JWT
JWT_SECRET_KEY=replace-me
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Mongo
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=manim_videos

# Cloudinary
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

# Stability AI (optional; if missing, local placeholder will be used)
STABILITY_API_KEY=...
STABILITY_T2I_URL=https://api.stability.ai/v2beta/stable-image/generate/sd3
STABILITY_I2V_URL=https://api.stability.ai/v2beta/image-to-video
STABILITY_I2V_RESULT_URL=https://api.stability.ai/v2beta/image-to-video/result/{id}
STABILITY_POLL_INTERVAL_SECONDS=3
STABILITY_TIMEOUT_SECONDS=600

# Video defaults (match the UI)
VIDEO_WIDTH=1280
VIDEO_HEIGHT=720
VIDEO_FPS=24
VIDEO_DURATION_SECONDS=8
```

## Run locally

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

## Notes

- The API surface is stable versus the previous version, so your front-end layout/behavior remains intact.
- The codebase was reorganized into a `backend/` package with clearer modules and heavy inline comments.
''',
}

# --- Deprecated files that should be removed after upgrade -------------------
DEPRECATED = [
    "video_tools.py",
    "auth_utils.py",
    "video_generator.py",
    "database_client.py",
    "cloudinary_service.py",
]

def main() -> int:
    created, overwritten, deleted = [], [], []

    # Ensure parent folders exist
    for relpath in sorted(FILES.keys()):
        path = ROOT / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        content = FILES[relpath]
        action_list = created if not path.exists() else overwritten
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        action_list.append(str(path.relative_to(ROOT)))

    # Remove deprecated modules if present
    for relpath in DEPRECATED:
        path = ROOT / relpath
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            deleted.append(str(path.relative_to(ROOT)))

    # Print a concise change log
    for p in created:
        print(f"CREATED: {p}")
    for p in overwritten:
        print(f"OVERWRITTEN: {p}")
    for p in deleted:
        print(f"DELETED: {p}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
