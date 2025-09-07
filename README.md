# Video Generator API (FastAPI)

This backend exposes a tiny API to generate short videos from a text prompt.
It tries Stability AI first (text→image→video). If not configured, it falls back to a local
placeholder animation so your UI keeps working.

## Endpoints (unchanged)

- `POST /signup` – `{ email, password }` → registers a user  
- `POST /login` – OAuth2 password flow; use form fields `username` (email) and `password`  
  Returns `{ access_token, token_type }`  
- `POST /generate` – body `{ "prompt": "..." }` with `Authorization: Bearer <token>`  
  Returns `{ "video_url": "<https://...>", "video_id": "<id>" }`  
- `GET /videos` – lists the caller's previously generated videos

## Environment

Create a `.env` (or set env vars in your deploy):

```env
# JWT
JWT_SECRET_KEY=replace-me
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Mongo
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=manim_videos

# Cloudinary
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

# Stability AI (optional; if missing, local placeholder will be used)
STABILITY_API_KEY=...
STABILITY_T2I_URL=https://api.stability.ai/v2beta/stable-image/generate/sd3
STABILITY_I2V_URL=https://api.stability.ai/v2beta/image-to-video
STABILITY_I2V_RESULT_URL=https://api.stability.ai/v2beta/image-to-video/result/{id}
STABILITY_POLL_INTERVAL_SECONDS=3
STABILITY_TIMEOUT_SECONDS=600

# Video defaults (match the UI)
VIDEO_WIDTH=1280
VIDEO_HEIGHT=720
VIDEO_FPS=24
VIDEO_DURATION_SECONDS=8
```

## Run locally

```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

## Notes

- The API surface is stable versus the previous version, so your front-end layout/behavior remains intact.
- The codebase was reorganized into a `backend/` package with clearer modules and heavy inline comments.
