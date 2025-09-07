
# Prompt Service (image & video)

Validates prompt payloads, sets `job_id`, computes `cost_estimate`, and
enqueues via **Fair Scheduler** with `creator_id` for DRR fairness.

## Endpoints
- `GET  /healthz`
- `POST /prompts/image`
- `POST /prompts/video`

## Env
- `FAIR_SCHEDULER_URL` (default: `http://fair-scheduler.ai-microgen.svc:8087`)
- `MAX_PROMPT_LEN` (default: `2000`)
