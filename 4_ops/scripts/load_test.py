
from __future__ import annotations
import asyncio, json, os, random, string, time

import httpx

BASE = os.getenv("BASE", "http://localhost:8080")

def rid(n=10):
    return ''.join(random.choices(string.ascii_lowercase+string.digits, k=n))

async def submit(client: httpx.AsyncClient):
    body = {"prompt": "city at night "+rid(4), "model_id": "base-v1"}
    r = await client.post(f"{BASE}/api/prompts", json=body)
    r.raise_for_status()
    return r.json()["job_id"]

async def poll(client: httpx.AsyncClient, job_id: str, timeout=15.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        r = await client.get(f"{BASE}/api/jobs/{job_id}")
        if r.status_code == 200:
            j = r.json()
            if j.get("job", {}).get("state") in {"done", "failed"}:
                return j
        await asyncio.sleep(0.5)
    return {"timeout": True, "job_id": job_id}

async def worker(stop_at: float):
    async with httpx.AsyncClient(timeout=10.0) as client:
        while time.time() < stop_at:
            try:
                job = await submit(client)
                res = await poll(client, job)
                state = res.get("job", {}).get("state") or ("timeout" if res.get("timeout") else "?")
                print("job=", job, "state=", state, flush=True)
            except Exception as e:
                print("error:", e, flush=True)

async def main(concurrency=5, seconds=30):
    stop_at = time.time() + seconds
    await asyncio.gather(*[worker(stop_at) for _ in range(concurrency)])

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--concurrency", type=int, default=5)
    ap.add_argument("--seconds", type=int, default=30)
    args = ap.parse_args()
    asyncio.run(main(args.concurrency, args.seconds))
