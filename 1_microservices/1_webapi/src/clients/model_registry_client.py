
from __future__ import annotations

import httpx

async def get_model(base_url: str, model_id: str):
    url = base_url.rstrip('/') + f"/models/{model_id}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()
