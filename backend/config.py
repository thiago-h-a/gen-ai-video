"""
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
