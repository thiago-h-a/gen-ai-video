
# API — Model Registry

Base: `http://localhost:8086`

| Method | Path                 | Description |
|--------|----------------------|-------------|
| GET    | /healthz             | Liveness |
| GET    | /models              | List manifests |
| GET    | /models/{id}         | Manifest detail |
| GET    | /models/{id}/weights | Weights pointer |
| POST   | /models              | Upsert (if enabled) |
