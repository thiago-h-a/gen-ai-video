
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class Settings:
    prompt_url: str = os.getenv("PROMPT_SERVICE_URL", "http://prompt-service.ai-microgen.svc:8082")
    catalog_url: str = os.getenv("MODEL_CATALOG_URL", "http://model-catalog.ai-microgen.svc:8086")
    sign_artifacts: bool = os.getenv("SIGN_ARTIFACTS", "0") in {"1","true","yes"}
    artifacts_bucket: str = os.getenv("ARTIFACTS_BUCKET", "artifacts")
    s3_endpoint: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    s3_region: str = os.getenv("S3_REGION", "us-east-1")
    s3_access_key: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    s3_secret_key: str = os.getenv("S3_SECRET_KEY", "minioadmin")

settings = Settings()
