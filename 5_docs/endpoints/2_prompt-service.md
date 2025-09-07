
# API — Prompt Service

| Method | Path             | Description |
|--------|------------------|-------------|
| GET    | /healthz         | Liveness |
| POST   | /prompts/image   | Validate, compute cost, enqueue via Fair Scheduler |
| POST   | /prompts/video   | Validate, compute cost, enqueue via Fair Scheduler |

**Body**
```jsonc
{"prompt":"...","model_id":"base-v1","params":{...},"creator_id":"alice"}
```

**Response**
```json
{"job_id":"a1b2c3d4e5f6"}
```
