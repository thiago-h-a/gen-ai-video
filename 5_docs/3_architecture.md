
# Architecture

## System context

```text
┌─────────────────────────── Internet / Creatives ───────────────────────────┐
│ React SPA (Web)                                                            │
│   ↕ HTTPS                                                                  │
│ Web/API (FastAPI)                                                          │
└────────────────────────────────────────────────────────────────────────────┘
                   │
                   ▼
            Prompt Service (FastAPI)
                   │  enqueue (creator_id, cost)
                   ▼
            Fair Scheduler (DRR, Redis)
                   │  /next, /complete
       ┌───────────┴───────────┐
       │                       │
       ▼                       ▼
  Orchestrator            Orchestrator
       │                       │
       ▼                       ▼
  gpu‑worker (images)     video‑worker (videos)
       │                       │
       ▼                       ▼
     S3 (artifacts bucket)  — presign via Web/API
       ▲
       │
  Model Catalog (SMR + DDB) — /models for SPA
```

## Components (C4‑ish)

- **Web/API** — Edge API for SPA; proxies prompt submissions; signs artifacts; proxies model catalog.
- **Prompt Service** — Validates payloads; computes cost; enqueues to Fair Scheduler.
- **Fair Scheduler** — DRR fairness across creators; Redis‑backed ring & queues.
- **Orchestrator** — Polls `/next`, dispatches to image or video workers; posts `/complete`.
- **GPU Image Worker** — Generates PNG/GIF.
- **Video Worker** — Generates MP4/WebM with ffmpeg; isolated GPU pool.
- **Model Catalog** — Lists models by reading SMR + DDB metadata.

## AWS mapping

- **EKS**: all services as Deployments
- **ECR**: container registries per service
- **IRSA**: service accounts mapped to IAM roles
- **S3**: artifacts bucket (versioned, SSE)
- **ElastiCache Redis**: scheduler state & queues
- **SageMaker Model Registry**: model packages, versions
- **DynamoDB**: model metadata (papers, licenses, domains)

## Scalability

- HPAs on **gpu‑worker** and **video‑worker** use backlog metrics from the
  scheduler and CPU utilization as a safety signal. See
  [`discussions/0004-adaptive-split-control.md`](./discussions/0004-adaptive-split-control.md).
