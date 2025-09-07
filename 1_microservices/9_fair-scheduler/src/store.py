
from __future__ import annotations
import json, time, asyncio
from typing import Any, Dict, List, Optional
import orjson
from redis.asyncio import Redis

from .settings import settings

# Key helpers
def k_ring_list(t: str) -> str: return f"fair:ring:list:{t}"
def k_ring_set(t: str) -> str:  return f"fair:ring:set:{t}"
def k_ring_ptr(t: str) -> str:  return f"fair:ring:ptr:{t}"
def k_deficit(t: str) -> str:   return f"fair:deficit:{t}"
def k_creator_q(t: str, c: str) -> str: return f"creator:list:{t}:{c}"
def k_job(j: str) -> str: return f"job:{j}"
def k_lock(t: str) -> str: return f"fair:lock:{t}"

class Store:
    def __init__(self):
        self.redis = Redis.from_url(settings.redis_url, decode_responses=False)

    async def close(self):
        await self.redis.aclose()

    # --------------- Locks ---------------
    async def try_lock(self, t: str) -> bool:
        # SET key value NX PX ttl
        ok = await self.redis.set(k_lock(t), b"1", nx=True, px=settings.lock_ttl_ms)
        return bool(ok)

    async def unlock(self, t: str) -> None:
        await self.redis.delete(k_lock(t))

    # --------------- Ring & deficits ---------------
    async def ensure_in_ring(self, t: str, creator: str) -> None:
        # Check membership set; if not present, add to set and to list tail
        pipe = self.redis.pipeline()
        pipe.sismember(k_ring_set(t), creator.encode())
        res = await pipe.execute()
        in_set = bool(res[0])
        if not in_set:
            pipe = self.redis.pipeline()
            pipe.sadd(k_ring_set(t), creator.encode())
            pipe.rpush(k_ring_list(t), creator.encode())
            await pipe.execute()

    async def get_ring(self, t: str) -> List[str]:
        data = await self.redis.lrange(k_ring_list(t), 0, -1)
        return [d.decode() for d in data]

    async def get_ptr(self, t: str) -> int:
        v = await self.redis.get(k_ring_ptr(t))
        return int(v) if v else 0

    async def set_ptr(self, t: str, i: int) -> None:
        await self.redis.set(k_ring_ptr(t), str(i).encode())

    async def incr_deficit(self, t: str, creator: str, by: int) -> int:
        v = await self.redis.hincrby(k_deficit(t), creator.encode(), by)
        return int(v)

    async def get_deficits(self, t: str) -> Dict[str, int]:
        h = await self.redis.hgetall(k_deficit(t))
        return {k.decode(): int(v.decode()) for k, v in h.items()}

    # --------------- Creator queues ---------------
    async def enqueue(self, t: str, creator: str, job_id: str) -> None:
        await self.redis.rpush(k_creator_q(t, creator), job_id.encode())

    async def pop_if_affordable(self, t: str, creator: str, max_cost: float) -> Optional[Dict[str, Any]]:
        # Peek first job, read its cost; if affordable, pop and return job
        q = k_creator_q(t, creator)
        pipe = self.redis.pipeline()
        pipe.lindex(q, 0)
        pipe.hgetall(k_job("_dummy"))  # placeholder to align indexes
        res = await pipe.execute()
        head = res[0]
        if not head:
            return None
        job_id = head.decode()
        meta = await self.redis.hgetall(k_job(job_id))
        if not meta:
            # inconsistent, drop the head
            await self.redis.lpop(q)
            return None
        cost = float(meta.get(b"cost", b"1").decode())
        if cost <= max_cost:
            # POP now
            await self.redis.lpop(q)
            meta_s = {k.decode(): v.decode() for k, v in meta.items()}
            meta_s["job_id"] = job_id
            return meta_s
        return None

    async def put_job_meta(self, job_id: str, meta: Dict[str, Any]) -> None:
        enc = {k: (str(v).encode() if not isinstance(v, (bytes, bytearray)) else v) for k, v in meta.items()}
        await self.redis.hset(k_job(job_id), mapping=enc)

    async def get_job_meta(self, job_id: str) -> Dict[str, Any]:
        h = await self.redis.hgetall(k_job(job_id))
        return {k.decode(): v.decode() for k, v in h.items()}

    async def del_job(self, job_id: str) -> None:
        await self.redis.delete(k_job(job_id))

    # --------------- Stats ---------------
    async def qlen(self, t: str, creator: str) -> int:
        v = await self.redis.llen(k_creator_q(t, creator))
        return int(v)
