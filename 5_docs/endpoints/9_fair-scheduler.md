
# API — Fair Scheduler (DRR)

Base: `http://fair-scheduler.ai-microgen.svc:8087`

| Method | Path             | Description |
|--------|------------------|-------------|
| GET    | /healthz         | Liveness |
| POST   | /enqueue         | Enqueue a job (per-creator queue) |
| GET    | /next?type=...   | Pick next job via DRR (204 if none/contended) |
| POST   | /complete        | Mark job done/failed |
| GET    | /stats/fairness  | Ring, pointer, deficits, queue depths |

**Enqueue body**
```jsonc
{
  "job_id": "j42",
  "creator_id": "alice",
  "type": "video",
  "payload": {"prompt":"neon city","model_id":"video-lite","params":{"fps":12,"seconds":3}},
  "cost_estimate": 6.0
}
```

**Next response**
```json
{"job_id":"j42","creator_id":"alice","type":"video","cost":6.0,"payload":{...}}
```
