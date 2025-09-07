
"""Redis access with FakeRedis fallback, plus queue helpers."""
from __future__ import annotations
from typing import Dict, Optional
import time

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


class FakeRedis:
    def __init__(self) -> None:
        self._hash: Dict[str, Dict[str, str]] = {}
        self._lists: Dict[str, list[str]] = {}

    # Hash ops
    def hset(self, key: str, mapping: Dict[str, str]) -> int:
        d = self._hash.setdefault(key, {})
        before = len(d)
        d.update({str(k): str(v) for k, v in mapping.items()})
        return len(d) - before

    def hgetall(self, key: str) -> Dict[str, str]:
        return dict(self._hash.get(key, {}))

    # List ops
    def lpush(self, key: str, value: str) -> int:
        lst = self._lists.setdefault(key, [])
        lst.insert(0, str(value))
        return len(lst)

    def rpop(self, key: str) -> Optional[str]:
        lst = self._lists.get(key)
        if not lst:
            return None
        return lst.pop()

    def blpop(self, key: str, timeout: int = 0) -> Optional[str]:
        end = time.time() + max(timeout, 0)
        while True:
            item = self.rpop(key)
            if item is not None:
                return item
            if timeout and time.time() >= end:
                return None
            time.sleep(0.05)


_cache = {"client": None}


def get_redis(url: str):
    if _cache.get("client") is not None:
        return _cache["client"]
    if redis is None:
        _cache["client"] = FakeRedis()
        return _cache["client"]
    try:
        client = redis.Redis.from_url(url, decode_responses=True)
        client.ping()
        _cache["client"] = client
        return client
    except Exception:
        _cache["client"] = FakeRedis()
        return _cache["client"]
