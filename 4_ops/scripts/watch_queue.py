
from __future__ import annotations
import os, time
try:
    import redis  # type: ignore
except Exception:
    redis = None

def main():
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    if redis is None:
        print("redis library not installed. pip install redis")
        return
    r = redis.Redis.from_url(url, decode_responses=True)
    key = os.getenv("QUEUE_KEY", "queue:generate")
    while True:
        depth = r.llen(key)
        print(f"{time.strftime('%H:%M:%S')} depth={depth}", flush=True)
        time.sleep(1.0)

if __name__ == "__main__":
    main()
