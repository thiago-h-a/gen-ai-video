
# Model Catalog (SMR + DynamoDB)

A service that exposes a **rich model catalog** beyond just weights:
- Searchable model metadata (modalities, tags, safety, license)
- Versioned records with parameters and evaluation metrics
- **Model Cards** (Markdown/JSON) for governance & transparency
- Optional integration with **SageMaker Model Registry** for canonical
  package groups & versions

## Endpoints

- `GET  /healthz`
- `GET  /models?modality=image|video&tag=safety:allowed`
- `GET  /models/{id}`
- `GET  /models/{id}/versions`
- `GET  /models/{id}/versions/{ver}`
- `GET  /models/{id}/card`  → Markdown or JSON
- `POST /models` (admin; optional in v1)
- `POST /models/{id}/versions` (admin; optional in v1)

## Environment

- `AWS_REGION` (optional for local)
- `CATALOG_DDB_MODELS`   (default: `model_catalog_models`)
- `CATALOG_DDB_VERSIONS` (default: `model_catalog_versions`)
- `CATALOG_DDB_CARDS`    (default: `model_catalog_cards`)
- `CATALOG_MUTABLE`      (`1` enables POST endpoints)
- `SMR_ENABLED`          (`1` to query SageMaker Model Registry)
- `SMR_PACKAGE_GROUP_TAG` (optional hint for mapping ids→groups)

In AWS, prefer **IRSA** to grant this pod DynamoDB read/write and SMR read.
