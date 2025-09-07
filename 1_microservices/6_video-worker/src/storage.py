
from __future__ import annotations
from pathlib import Path
from typing import Tuple
import boto3
from botocore.client import Config

from .settings import settings
from .util.logging import logger

def ensure_root() -> Path:
    root = Path(settings.artifacts_root)
    root.mkdir(parents=True, exist_ok=True)
    return root

def local_save(model_id: str, job_id: str, ext: str, data: bytes) -> str:
    root = ensure_root() / model_id
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{job_id}.{ext}"
    path.write_bytes(data)
    return f"artifacts/{model_id}/{job_id}.{ext}"

def maybe_upload_s3(artifact_key: str, data: bytes, content_type: str) -> Tuple[bool, str]:
    if not settings.s3_upload:
        return False, artifact_key
    try:
        client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            config=Config(signature_version="s3v4"),
        )
        client.put_object(Bucket=settings.artifacts_bucket, Key=artifact_key, Body=data, ContentType=content_type)
        return True, artifact_key
    except Exception as e:
        logger.warning("S3 upload failed: %s", e)
        return False, artifact_key
