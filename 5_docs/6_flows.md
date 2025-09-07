
# Flows (E2E)

## Submit & generate (happy path)

```mermaid
sequenceDiagram
  participant C as SPA Client
  participant W as Web/API
  participant P as Prompt Service
  participant Q as Redis Queue
  participant O as Orchestrator
  participant G as GPU Worker
  participant S as S3/MinIO
  participant N as Notify

  C->>W: POST /api/prompts
  W->>P: POST /prompts
  P->>Q: LPUSH queue:generate job_id
  O->>Q: RPOP -> job_id
  O->>G: POST /generate
  G->>S: PUT object
  G-->>O: 200 {artifact_key}
  O->>N: POST /notify/job/{id}
  N-->>C: SSE job.done
  C->>W: GET /api/artifacts/{id}
  W-->>C: 302 to presigned S3 URL
```

## Failure: worker error

```mermaid
sequenceDiagram
  O->>G: /generate
  G-->>O: 500 error
  O->>O: job:{id}.state=failed
  O->>N: notify failed
  N-->>C: SSE job.failed
```

## Idempotency & retries (guidelines)

- Prompt Service should be idempotent for duplicate payloads (same client token)
- Orchestrator may retry a job once if worker returns 5xx in <2s.
