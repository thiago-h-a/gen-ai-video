
# Video Worker (isolated GPU pool)

Generates short videos from synthetic frames using Pillow + ffmpeg.
Intended to run on a dedicated GPU node group, separate from image workers.

## Endpoints

- `GET  /healthz` — liveness
- `GET  /readyz`  — readiness (checks artifact dir and ffmpeg availability)
- `GET  /info`    — version & codec defaults
- `POST /generate/video` — single video render
- `POST /generate/video/batch` — batch render (sequential in v1)

## Request example

```jsonc
POST /generate/video
{
  "job_id": "vid-123",
  "prompt": "flying through neon city",
  "model_id": "video-lite",
  "params": {"width": 640, "height": 360, "fps": 12, "seconds": 3, "codec": "h264"}
}
```

## Environment

- `ARTIFACTS_ROOT`  (default: `/data/artifacts`)
- `DEFAULT_CODEC`   (default: `h264`) — alternatives: `vp9`
- `IMG_WIDTH`/`IMG_HEIGHT` fallback
- `MAX_CONCURRENCY` (default: `1` in v1)
- `S3_UPLOAD` + `S3_ENDPOINT`/`S3_REGION`/`S3_ACCESS_KEY`/`S3_SECRET_KEY`/`ARTIFACTS_BUCKET`

## Run locally

```bash
uvicorn src.main:app --reload --port 8091
# or
docker build -t video-worker .
mkdir -p _artifacts
docker run --rm -p 8091:8091 -v $(pwd)/_artifacts:/data video-worker
```
