
# Overview

**ai‑microgen** orchestrates prompt‑driven **image** and **video**
generation. Key choices:

- **Model storage**: *SageMaker Model Registry* (artifacts) + *DynamoDB* (rich metadata)
- **Isolation**: Dedicated **video‑worker** microservice + GPU node pool
- **Fairness**: **DRR** (Deficit Round Robin) scheduler w/ Redis queues
- **Workers**: `gpu-worker` (images), `video-worker` (videos)
- **Redis as MQ**: used by the scheduler for per‑creator queues and ring state

### Core request path

1. SPA → **Web/API** → **Prompt Service**
2. Prompt Service validates, estimates cost, enqueues in **Fair Scheduler** (Redis)
3. **Orchestrator** polls `/next` and dispatches to **gpu‑worker** or **video‑worker**
4. Workers render artifacts → write local → upload to **S3** (artifacts bucket)
5. Web/API signs S3 object for SPA download/streaming

See [architecture](./architecture.md) and [APIs overview](./apis-overview.md).
