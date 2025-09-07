
# Orchestrator Service

Dequeues jobs from Redis (`queue:generate`), selects a GPU worker, calls the
worker's `/generate` endpoint, updates job state in Redis, and notifies the
Notify Service about status changes.

## Endpoints

- `GET  /healthz` — liveness
- `POST /tick?max=1` — process up to `max` jobs once
- `POST /dispatch/test` — dry-run call to the first configured worker

## Env

- `REDIS_URL`           (default: `redis://localhost:6379/0`)
- `GPU_WORKERS`         (comma-separated list of base URLs; default uses localhost)
- `NOTIFY_URL`          (default: `http://localhost:8083`)
- `WORKER_TIMEOUT`      (seconds, default `60`)
- `QUEUE_KEY`           (default `queue:generate`)
- `ORCH_AUTOSTART`      (1 to run background consume loop)

## Local run

```bash
uvicorn src.main:app --reload --port 8084
# or container
docker build -t orchestrator .
docker run --rm -p 8084:8084       -e REDIS_URL=redis://host.docker.internal:6379/0       -e GPU_WORKERS=http://host.docker.internal:8090       -e NOTIFY_URL=http://host.docker.internal:8083 orchestrator
```
