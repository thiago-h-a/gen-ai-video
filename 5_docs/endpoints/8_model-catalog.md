
# API — Model Catalog (SMR + DynamoDB)

Base: `http://model-catalog.ai-microgen.svc:8086`

| Method | Path                           | Description |
|--------|--------------------------------|-------------|
| GET    | /healthz                       | Liveness |
| GET    | /models?modality=&tag=         | List models |
| GET    | /models/{id}                   | Model summary |
| GET    | /models/{id}/versions          | Versions |
| GET    | /models/{id}/versions/{ver}    | Version detail |
| GET    | /models/{id}/card              | Model card (Markdown/JSON) |
| POST   | /models                         | Upsert (if `CATALOG_MUTABLE=1`) |
| POST   | /models/{id}/versions           | Upsert (if `CATALOG_MUTABLE=1`) |

Environment variables:
- `CATALOG_DDB_MODELS`, `CATALOG_DDB_VERSIONS`, `CATALOG_DDB_CARDS`
- `SMR_ENABLED=1` to query SageMaker Model Registry (read-only)
- `CATALOG_MUTABLE=1` to allow POST upserts
