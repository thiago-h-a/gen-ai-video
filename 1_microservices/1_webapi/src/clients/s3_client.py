
from __future__ import annotations
from urllib.parse import quote

from ..settings import settings


def sign_artifact_url(key: str, ttl_seconds: int = 900) -> str:
    """Return a pseudo-signed URL for local dev.

    In production, generate a proper pre-signed URL with boto3/MinIO SDK.
    """
    # if already a full URL, return as-is
    if key.startswith("http://") or key.startswith("https://"):
        return key
    base = settings.s3_endpoint.rstrip('/')
    # allow bucket prefix or assume artifacts bucket
    if key.startswith("artifacts/"):
        path = key
    else:
        path = f"{settings.artifacts_bucket}/{key}"
    return f"{base}/{quote(path)}?mockSigned=1&ttl={ttl_seconds}"
