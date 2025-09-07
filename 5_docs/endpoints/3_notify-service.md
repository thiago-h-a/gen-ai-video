
# API — Notify Service

Base: `http://localhost:8083`

| Method | Path               | Description |
|--------|--------------------|-------------|
| GET    | /healthz           | Liveness |
| GET    | /events            | SSE stream |
| POST   | /notify/job/{id}   | Internal publish |

**Events**: `job.running`, `job.done`, `job.failed`.
