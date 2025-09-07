
# API — Web/API (edge)

| Method | Path                 | Description |
|--------|----------------------|-------------|
| GET    | /healthz             | Liveness |
| POST   | /api/prompts/image   | Submit image job (propagates `creator_id`) |
| POST   | /api/prompts/video   | Submit video job (propagates `creator_id`) |
| GET    | /api/catalog/models  | Proxy to Model Catalog `/models` |
| GET    | /api/artifacts/{key} | Presigned S3 URL redirect |
