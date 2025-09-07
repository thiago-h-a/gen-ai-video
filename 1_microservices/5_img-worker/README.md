
# GPU Worker

The GPU Worker exposes `/generate`, which accepts a prompt payload and
returns an `artifact_key`. In this scaffold, the "generation" is a simple
Pillow-based image with the prompt text over a colored background. Swap the
`engine.generate_png` function with a real inference engine later.

## Endpoints

- `GET  /healthz` — liveness
- `GET  /` — tiny HTML for quick testing
- `POST /generate` — perform synthetic generation and store artifact

## Request/Response

**POST /generate**
```json
{
  "job_id": "uuid-or-string",
  "prompt": "a moody portrait photo of a robot violinist",
  "model_id": "base-v1",
  "params": {"steps": 30, "guidance": 7.5}
}
```

**200 OK**
```json
{"artifact_key": "artifacts/base-v1/<job_id>.png", "duration_ms": 245}
```

## Environment

- `ARTIFACTS_ROOT`  (default: `/data/artifacts`)
- `IMG_WIDTH`       (default: `768`)
- `IMG_HEIGHT`      (default: `512`)
- `SEED`            (default: random)

## Local run

```bash
uvicorn src.main:app --reload --port 8090
# or container
docker build -t gpu-worker .
docker run --rm -p 8090:8090 -v $(pwd)/_artifacts:/data gpu-worker
```

Artifacts will be written under `/data/artifacts/` inside the container.
