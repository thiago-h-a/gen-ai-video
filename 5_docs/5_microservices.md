
# Microservices (responsibilities & contracts)

Each service is autonomous and communicates via HTTP. Shared DTOs are
documented in [data-models.md](data-models.md) and service API pages.

## Web/API
- Hosts the SPA
- Proxies `/api/*` to internal services
- Signs/pre-signs artifact URLs

## Prompt Service
- Validates prompt payloads
- Assigns job IDs and enqueues to Redis
- Returns `job_id` synchronously

## Orchestrator
- Dequeues jobs from Redis, updates job state
- Calls `/generate` on GPU Worker(s)
- On success: records `artifact_key`; on failure: records `error`

## GPU Worker
- Synthetic image/GIF generation via Pillow
- Concurrency-limited; optional S3 upload

## Notify Service
- Publishes job events to SSE/WS stream

## Model Registry
- Serves JSON manifests of available models
