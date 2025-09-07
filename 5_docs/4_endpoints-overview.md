
# APIs — Overview

| Service | Base | Key Endpoints |
|--------:|:-----|:--------------|
| Web/API | `/api` | `/prompts/image`, `/prompts/video`, `/catalog/models`, `/artifacts/{key}` |
| Prompt Service | `/` | `/prompts/image`, `/prompts/video`, `/healthz` |
| Fair Scheduler | `/` | `/enqueue`, `/next?type=image`|video`, `/complete`, `/stats/fairness`, `/metrics` |
| Orchestrator | n/a | internal polling of `/next`, `/complete` |
| GPU Worker | `/` | `/generate`, `/generate/batch`, `/models`, `/healthz` |
| Video Worker | `/` | `/generate/video`, `/generate/video/batch`, `/healthz` |
| Model Catalog | `/` | `/models?type=...`, `/healthz` |

See individual API docs in `docs/api/`.
