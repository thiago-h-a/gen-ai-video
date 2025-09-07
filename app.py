from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

# Internal modules (renamed & reorganized)
from backend.media.generator import generate_video
from backend.storage import upload_video
from backend.db import save_video_url, get_user_videos
from backend.security import create_access_token, register_user, authenticate_user, get_current_user


# -----------------------------------------------------------------------------
# FastAPI app with permissive CORS (unchanged surface so the front-end works)
# -----------------------------------------------------------------------------
app = FastAPI(title="Video Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # keep as-is to avoid breaking existing clients
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Schemas (kept identical to preserve front-end contract)
# -----------------------------------------------------------------------------
class PromptRequest(BaseModel):
    prompt: str


class UserRegister(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# -----------------------------------------------------------------------------
# Auth endpoints (surface unchanged)
# -----------------------------------------------------------------------------
@app.post("/signup")
async def signup(user: UserRegister):
    """
    Register a user by email & password.
    Returns 400 if the email already exists.
    """
    result = register_user(user.email, user.password)
    if not result:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"message": "User registered successfully"}


@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 Password flow-compatible login.
    - username field carries the user's email (kept for compatibility).
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["user_id"]})
    return {"access_token": access_token, "token_type": "bearer"}


# -----------------------------------------------------------------------------
# Core feature endpoints (surface unchanged)
# -----------------------------------------------------------------------------
@app.post("/generate")
async def generate(req: PromptRequest, current_user: dict = Depends(get_current_user)):
    """
    Generate a video from a text prompt, upload it, and save the URL.
    Behavior notes:
    - Uses Stability (text→image→video) when configured.
    - Falls back to a local placeholder animation if not configured.
    - Always normalizes to H.264/AAC MP4, 1280x720 @ 24 fps.
    """
    local_video_path: str | None = None
    try:
        # 1) Produce a video artifact (remote pipeline with safe local fallback)
        local_video_path = generate_video(
            req.prompt,
            width=1280,
            height=720,
            fps=24,
            duration=int(os.getenv("VIDEO_DURATION_SECONDS", "8")),
        )
        if not local_video_path or not os.path.exists(local_video_path):
            raise HTTPException(status_code=500, detail="Failed to generate video")

        # 2) Ship to Cloudinary and persist the resulting URL
        video_url = upload_video(local_video_path)
        if not video_url:
            raise HTTPException(status_code=500, detail="Failed to upload video")

        # 3) Persist for the authenticated user
        video_id = save_video_url(current_user["user_id"], video_url)
        if not video_id:
            raise HTTPException(status_code=500, detail="Failed to save video URL")

        return {"video_url": video_url, "video_id": video_id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        # Always tidy up the local artifact
        try:
            if local_video_path and os.path.exists(local_video_path):
                os.remove(local_video_path)
        except Exception:
            pass


@app.get("/videos")
async def get_videos(current_user: dict = Depends(get_current_user)):
    """
    List previously generated videos for the authenticated user.
    """
    return {"videos": get_user_videos(current_user["user_id"])}
