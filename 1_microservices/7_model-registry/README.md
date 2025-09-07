
# Model Registry Service

The Model Registry serves model manifests from JSON files on disk. Designed
for simplicity and transparency; production can swap the store for a DB.

## Endpoints

- `GET  /healthz` — liveness
- `GET  /` — tiny HTML index
- `GET  /models` — list all models
- `GET  /models/{id}` — fetch a manifest
- `GET  /models/{id}/weights` — pointer to weights (bucket/key/uri)
- `POST /models` — add/overwrite manifest (enabled iff `REGISTRY_MUTABLE=1`)

## Environment

- `REGISTRY_DATA_DIR` (default: `./data/models`) — folder containing `*.json`
- `REGISTRY_MUTABLE`  (default: `0`) — set `1` to allow POST /models

## Local run

```bash
uvicorn src.main:app --reload --port 8086
# or container
docker build -t model-registry .
docker run --rm -p 8086:8086 -v $(pwd)/data:/app/data model-registry
```

## Manifest shape (pydantic)

- `id: str` (unique)
- `name: str`
- `task: Literal["image", "video", "text", "multimodal"]`
- `version: str` (e.g., semver)
- `weights: { type: "s3"|"uri"|"fs", bucket?: str, key?: str, uri?: str }`
- `tags: list[str]`
- `params: dict[str, Any]` (free-form)
