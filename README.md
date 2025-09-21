
# Documentation — Video Generative AI Platform

Welcome! This folder documents the platform: a microservices
system where ~20 creatives people submit prompts to generate images/videos using GPU
workers. The stack: FastAPI services, Redis queue, S3-compatible artifact
storage, and a file-backed Model Registry.

## Navigation

- **Overview**: [Architecture](2_architecture.md), [Microservices](microservices.md)
- **How it works**: [Flows](3_flows.md), [Data models](data-models.md)
- **APIs**:
  - [Web/API](endpoints/webapi.md)
  - [Prompt Service](endpoints/prompt-service.md)
  - [Notify Service](endpoints/notify-service.md)
  - [Orchestrator](endpoints/orchestrator.md)
  - [GPU Worker](endpoints/gpu-worker.md)
  - [Model Registry](endpoints/model-registry.md)
- **Build & Run**: see `deploy/README.md` and `infra/README.md`
- **Operate**: [Operations](operations.md), [Security](security.md)
- **Quality**: [Testing](testing.md), [Troubleshooting](troubleshooting.md)
- **Process**: [Contributing](contributing.md), [Styleguide](styleguide.md)
- **Business**: [SLA](sla.md), [Capacity Planning](capacity-planning.md)
- **Change history**: [Postmortem Template](postmortem-template.md), [Changelog](changelog-template.md)
- **Reference**: [Glossary](zzz_glossary.md), [FAQ](zz_faq.md)
- **Decisions**: ADRs in [`adr/`](discussions/)

## Principles

1. **Simple first** → Redis list for queue, S3 for artifacts, clear DTOs.
2. **Contracts over tight coupling** → each service owns its API spec.
3. **Observe everything** → queue depth, job state transitions, durations.
4. **Fail loud, fail early** → strict validation with Pydantic, small blast radius.
5. **Secure by default** → private buckets, presigned URLs, least privilege.
