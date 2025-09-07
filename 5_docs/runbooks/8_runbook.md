
# Runbook — ai-microgen (Step 1)

This runbook covers local development, common tasks, and troubleshooting for
the early scaffold of ai-microgen.

## Local Setup

1. Prerequisites
   - Docker Desktop/Engine
   - Python 3.11+
   - `make`

2. Start infra dependencies (Redis + MinIO):
   ```bash
   docker compose up --build
   ```

3. (Optional) Seed MinIO buckets using the `mc` client:
   ```bash
   mc alias set local http://localhost:9000 minioadmin minioadmin
   mc mb -p local/artifacts || true
   mc mb -p local/models || true
   mc ls local
   ```

## Common Tasks

- **Format** (if tools installed):
  ```bash
  make fmt
  ```
- **Lint** (if tools installed):
  ```bash
  make lint
  ```
- **Run tests** (placeholder):
  ```bash
  make test
  ```

## Operational Notes

- **Queues & State**: Redis holds job state and queue depth; prefer a
  dedicated DB later if retention/history are needed.
- **Artifacts**: store outputs under `artifacts/` bucket with deterministic
  keys and signed URL access.
- **Models**: store model weights under `models/` bucket; manage via
  Model Registry service.

## Troubleshooting

- Redis not healthy: ensure port 6379 is free; check container logs.
- MinIO not healthy: ensure ports 9000/9001 are free; check health endpoints.
- Permission denied (MinIO): verify `MINIO_ROOT_USER/PASSWORD` and bucket
  existence.

## Next Steps (future patches)

- Implement Web/API, Prompt Service, and Orchestrator.
- Add real Redis client libs and S3 SDKs; wire to settings.
- Provide Helm charts and Terraform for production infra.
