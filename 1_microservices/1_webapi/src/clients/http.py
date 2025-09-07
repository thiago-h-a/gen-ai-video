
from __future__ import annotations
import httpx

# Lightweight shared async HTTP client factory (optionally expand to reuse session)

def create_client(timeout: float = 10.0) -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=timeout)
