
# Data models & storage keys

## Redis

- Queue list: `queue:generate`
- Job hash: `job:{job_id}` with fields:
  - `state` ∈ {queued,running,done,failed}
  - `prompt`, `model_id`, `params`
  - `artifact_key` (when done)
  - `error` (when failed)

## S3

- Artifacts: `artifacts/<model_id>/<job_id>.(png|gif)`
- Weights:   `models/<model_id>/weights.*`

## DTO examples

```jsonc
// POST /prompts
{"prompt":"neon city","model_id":"base-v1","params":{"steps":30}}
// 200
{"job_id":"abc123"}
```

```jsonc
// POST /generate
{"job_id":"abc123","prompt":"neon city","model_id":"base-v1","params":{"frames":1}}
// 200
{"artifact_key":"artifacts/base-v1/abc123.png","duration_ms":245}
```
