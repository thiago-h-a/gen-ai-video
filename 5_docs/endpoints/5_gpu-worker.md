
# API — GPU Worker

Base: `http://localhost:8090`

| Method | Path            | Description |
|--------|-----------------|-------------|
| GET    | /               | Demo HTML |
| GET    | /healthz        | Liveness |
| GET    | /readyz         | Readiness |
| GET    | /info           | Env summary (+CUDA flag if torch available) |
| POST   | /generate       | Single render |
| POST   | /generate/batch | Batch renders |

**/generate request**
```jsonc
{"job_id":"id","prompt":"...","model_id":"base-v1","params":{"frames":1}}
```

**Response**
```json
{"artifact_key":"artifacts/base-v1/id.png","duration_ms":245}
```
