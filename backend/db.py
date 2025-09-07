"""
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
