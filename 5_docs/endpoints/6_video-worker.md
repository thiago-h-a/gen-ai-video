
# API — Video Worker (isolated)

Base: `http://video-worker.ai-microgen.svc:8091`

| Method | Path                     | Description |
|--------|--------------------------|-------------|
| GET    | /healthz                 | Liveness |
| GET    | /readyz                  | Readiness (ffmpeg present?) |
| GET    | /info                    | Default codec & defaults |
| POST   | /generate/video          | Single video generation |
| POST   | /generate/video/batch    | Batch generation |

**/generate/video request**
```jsonc
{"job_id":"vid-1","prompt":"neon city flythrough","model_id":"video-lite","params":{"fps":12,"seconds":3,"codec":"h264"}}
```
