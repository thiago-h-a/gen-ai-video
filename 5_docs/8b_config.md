
# config/ (env & configuration)

Central reference for environment variables across services and examples of
`.env` files for local development and CI.

## Common variables

| Variable | Default | Description |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `S3_ENDPOINT` | `http://localhost:9000` | S3/MinIO endpoint |
| `S3_REGION` | `us-east-1` | Region for S3 signatures |
| `S3_ACCESS_KEY` | `minioadmin` | Access key for dev |
| `S3_SECRET_KEY` | `minioadmin` | Secret key for dev |
| `ARTIFACTS_BUCKET` | `artifacts` | Where generated media is stored |

## Service-specific

### webapi
- `PROMPT_SERVICE_URL` (default: `http://localhost:8082`)
- `NOTIFY_SERVICE_URL` (default: `http://localhost:8083`)

### prompt-service
- `REDIS_URL` (queue and job status store)

### notify-service
- `REDIS_URL` (pub/sub)

### orchestrator
- `REDIS_URL`
- `QUEUE_KEY` (default: `queue:generate`)
- `NOTIFY_URL` (default: `http://localhost:8083`)
- `GPU_WORKERS` (comma-separated host URLs)
- `ORCH_AUTOSTART` (set `1` to run background loop)

### gpu-worker
- `ARTIFACTS_ROOT` (default: `/data/artifacts`)
- `IMG_WIDTH`, `IMG_HEIGHT` (fallbacks)
- `MAX_CONCURRENCY` (default: `2`)
- `S3_UPLOAD` (`1` to upload artifacts)

### model-registry
- `REGISTRY_DATA_DIR` (default: `./data/models`)
- `REGISTRY_MUTABLE` (`1` to allow POST /models)

## Sample `.env` (compose)

```dotenv
REDIS_URL=redis://redis:6379/0
S3_ENDPOINT=http://minio:9000
S3_REGION=us-east-1
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
ARTIFACTS_BUCKET=artifacts
PROMPT_SERVICE_URL=http://prompt-service:8082
NOTIFY_SERVICE_URL=http://notify-service:8083
```

## Sample `.env.ci` (CI runners)

```dotenv
REDIS_URL=redis://localhost:6379/0
S3_ENDPOINT=http://localhost:9000
S3_REGION=us-east-1
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
ARTIFACTS_BUCKET=artifacts
```
