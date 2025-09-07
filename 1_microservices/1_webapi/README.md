
# Web/API (edge)

Public edge for the SPA. Proxies prompt submission to Prompt Service,
surfaces Model Catalog to the UI, and signs artifact keys to presigned S3
URLs for direct download/streaming.

## Endpoints
- `GET  /healthz`
- `POST /api/prompts/image` — forwards with `creator_id`
- `POST /api/prompts/video` — forwards with `creator_id`
- `GET  /api/catalog/models` — proxy to Model Catalog
- `GET  /api/artifacts/{key}` — presigned S3 URL for PNG/GIF/MP4/WebM

## Env
- `PROMPT_SERVICE_URL` (default: `http://prompt-service.ai-microgen.svc:8082`)
- `MODEL_CATALOG_URL` (default: `http://model-catalog.ai-microgen.svc:8086`)
- `ARTIFACTS_BUCKET`, `S3_ENDPOINT`, `S3_REGION`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`
- `SIGN_ARTIFACTS` ("1" to enable presigned URLs)
