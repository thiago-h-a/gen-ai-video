
# Fair Scheduler (DRR)

This control-plane service enforces **per‑creative fairness** across image
and video job streams using **Deficit Round Robin (DRR)**. Orchestrator pods
call `GET /next?type=image|video` to fetch the next job atomically.

## Why DRR?
- Low overhead, handles variable job sizes via "cost" estimates.
- Long‑term fairness: heavy jobs consume more deficit, light jobs interleave.

## Endpoints
- `POST /enqueue`  — enqueue a job into a creator subqueue
- `GET  /next`     — choose the next job (DRR, single atomic pick)
- `POST /complete` — record completion & basic metrics
- `GET  /stats/fairness` — inspect ring, deficits, queue depths

## Env
- `REDIS_URL` (default: `redis://localhost:6379/0`)
- `QUANTUM` (default: `2`) — deficit units added each scan
- `LOCK_TTL_MS` (default: `500`) — critical section lock TTL
- `MAX_SCAN` (default: `128`) — max creators to scan per /next
