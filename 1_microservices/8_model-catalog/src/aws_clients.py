
from __future__ import annotations
import os
try:
    import boto3  # type: ignore
except Exception:  # pragma: no cover
    boto3 = None

from .settings import settings

def ddb():
    if boto3 is None:
        return None
    return boto3.resource("dynamodb", region_name=settings.region)

def smr():
    if boto3 is None or not settings.smr_enabled or not settings.region:
        return None
    return boto3.client("sagemaker", region_name=settings.region)
