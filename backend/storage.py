"""
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
