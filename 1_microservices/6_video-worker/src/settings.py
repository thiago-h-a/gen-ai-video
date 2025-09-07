
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class Settings:
    artifacts_root: str = os.getenv("ARTIFACTS_ROOT", "/data/artifacts")
    img_width: int = int(os.getenv("IMG_WIDTH", "640"))
    img_height: int = int(os.getenv("IMG_HEIGHT", "360"))
    default_codec: str = os.getenv("DEFAULT_CODEC", "h264")  # or vp9
    max_concurrency: int = int(os.getenv("MAX_CONCURRENCY", "1"))
    seed: int | None = int(os.getenv("SEED")) if os.getenv("SEED") else None
    # S3
    s3_upload: bool = os.getenv("S3_UPLOAD", "0") in {"1","true","yes"}
    s3_endpoint: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    s3_region: str = os.getenv("S3_REGION", "us-east-1")
    s3_access_key: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY", "minioadmin")
    artifacts_bucket: str = os.getenv("ARTIFACTS_BUCKET", "artifacts")

settings = Settings()
