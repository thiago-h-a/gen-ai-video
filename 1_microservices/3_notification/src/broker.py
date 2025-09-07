
from __future__ import annotations
import asyncio
import json
from dataclasses import dataclass
from typing import AsyncGenerator, Dict

from .store import get_pubsub
from .settings import settings

@dataclass
class JobEvent:
    type: str
    job_id: str
    data: Dict[str, object]


class Broker:
    def __init__(self, url: str):
        self._pubsub = get_pubsub(url)

    async def publish(self, channel: str, evt: JobEvent) -> int:
        payload = json.dumps({"type": evt.type, "job_id": evt.job_id, **evt.data}, ensure_ascii=False)
        return await self._pubsub.publish(channel, payload)

    async def subscribe(self, channel: str) -> AsyncGenerator[JobEvent, None]:
        async for raw in self._pubsub.subscribe(channel):
            try:
                obj = json.loads(raw)
                yield JobEvent(type=str(obj.get("type", "job.event")), job_id=str(obj.get("job_id", "")), data={k: v for k, v in obj.items() if k not in {"type", "job_id"}})
            except Exception:
                # best-effort: emit as opaque event
                yield JobEvent(type="job.event", job_id="", data={"raw": raw})


_singleton: Broker | None = None

def get_broker(url: str | None = None) -> Broker:
    global _singleton
    if _singleton is None:
        _singleton = Broker(url or settings.redis_url)
    return _singleton
