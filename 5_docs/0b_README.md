
# ai‑microgen — Documentation

Welcome! This folder is the living documentation for **ai‑microgen**, a
microservices platform where 20 creatives submit prompts that generate
images and videos with generative AI.

**What to read first**
- [Overview / Index](./index.md)
- [Architecture](./architecture.md)
- [APIs Overview](./apis-overview.md)
- [Runbooks](./runbooks/operational-checklist.md)
- [Discussions (ADRs)](./discussions/)

**Fast links**
- Web/API → `services/webapi/`
- Prompt Service → `services/prompt-service/`
- Fair Scheduler → `services/fair-scheduler/`
- GPU Image Worker → `services/gpu-worker/`
- Video Worker → `services/video-worker/`
- Model Catalog (SMR + DDB) → `services/model-catalog/`

**Diagrams**
- ASCII architecture: [`diagrams/architecture.ascii`](./diagrams/architecture.ascii)
- Mermaid: [`diagrams/architecture.mmd`](./diagrams/architecture.mmd)
- Flows: [image](./diagrams/flow-image.mmd), [video](./diagrams/flow-video.mmd), [fairness](./diagrams/flow-fairness.mmd)
