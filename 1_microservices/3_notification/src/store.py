
"""Redis connection and FakeRedis fallback used by the broker."""
from __future__ import annotations
from typing import Dict, Optional

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


class FakePubSub:
    """Very small in-memory pub/sub for local dev and tests."""
    def __init__(self):
        self._channels: Dict[str, list] = {}

    async def publish(self, channel: str, message: str) -> int:
        subs = self._channels.get(channel, [])
        for q in subs:
            await q.put(message)
        return len(subs)

    async def subscribe(self, channel: str):
        import asyncio
        q: asyncio.Queue[str] = asyncio.Queue()
        self._channels.setdefault(channel, []).append(q)
        try:
            while True:
                msg = await q.get()
                yield msg
        finally:
            self._channels[channel].remove(q)
            if not self._channels[channel]:
                self._channels.pop(channel, None)


class RedisPubSub:
    def __init__(self, url: str):
        if redis is None:
            raise RuntimeError("redis library not available")
        self.client = redis.Redis.from_url(url, decode_responses=True)
        self.pubsub = self.client.pubsub()

    async def publish(self, channel: str, message: str) -> int:
        # redis-py publish is sync; run in thread
        import asyncio
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.client.publish, channel, message)

    async def subscribe(self, channel: str):
        import asyncio
        self.pubsub.subscribe(channel)
        loop = asyncio.get_running_loop()
        try:
            while True:
                # non-blocking get_message in thread, with timeout
                def _get():
                    return self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                msg = await loop.run_in_executor(None, _get)
                if msg and msg.get('type') == 'message':
                    yield msg['data']
                await asyncio.sleep(0.01)
        finally:
            try:
                self.pubsub.unsubscribe(channel)
            except Exception:
                pass


def get_pubsub(url: str):
    if redis is None:
        return FakePubSub()
    try:
        # verify connectivity
        client = redis.Redis.from_url(url, decode_responses=True)
        client.ping()
        return RedisPubSub(url)
    except Exception:
        return FakePubSub()
