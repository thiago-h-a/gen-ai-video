
# Notify Service

Real-time notification gateway for **ai-microgen**. Provides **SSE** and
**WebSocket** endpoints that stream job events, backed by Redis pub/sub
(in-memory fallback included for local development).

## Endpoints

- `GET  /healthz` — service health
- `GET  /events` — **SSE** stream (optional `?job_id=...` to filter)
- `GET  /ws` — **WebSocket** (optional `?job_id=...` to filter)
- `POST /notify/job/{job_id}` — publish job event (JSON body)

## Channels

- Broadcast: `events:jobs`
- Per-job:  `events:job:{job_id}`

## Local run

```bash
uvicorn src.main:app --reload --port 8083
# Or container:
docker build -t notify-service .
docker run --rm -p 8083:8083         -e REDIS_URL=redis://host.docker.internal:6379/0 notify-service
```

## Env

- `REDIS_URL`   (default: `redis://localhost:6379/0`)
- `SERVICE_PORT` (default: `8083`)
