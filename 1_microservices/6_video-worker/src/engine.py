
from __future__ import annotations
import io, os, random, subprocess, tempfile
from typing import List, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    FONT = ImageFont.truetype("DejaVuSans.ttf", 20)
except Exception:  # pragma: no cover
    FONT = ImageFont.load_default()

def _frame(width: int, height: int, seed: int, text: List[str]) -> Image.Image:
    rng = np.random.default_rng(seed)
    arr = rng.integers(0, 255, size=(height, width, 3), dtype=np.uint8)
    img = Image.fromarray(arr, mode="RGB")
    draw = ImageDraw.Draw(img)
    y = 8
    for line in text[:5]:
        draw.text((8, y), line, fill=(255,255,255), font=FONT)
        y += 24
    return img

def _write_frames_tmp(width: int, height: int, fps: int, seconds: int, prompt: str, model_id: str, seed: int | None) -> Tuple[str, int]:
    if seed is None:
        import time
        seed = int(time.time() * 1000) % (2**31-1)
    total = max(1, fps * seconds)
    tmpdir = tempfile.mkdtemp(prefix="vw_frames_")
    for i in range(total):
        text = [f"Model: {model_id}", f"{prompt}", f"frame {i+1}/{total}"]
        img = _frame(width, height, seed + i, text)
        img.save(os.path.join(tmpdir, f"f_{i:05d}.png"), format="PNG")
    return tmpdir, total

def _encode_ffmpeg(frames_dir: str, total: int, fps: int, width: int, height: int, codec: str) -> bytes:
    out = tempfile.NamedTemporaryFile(prefix="vw_out_", suffix=(".mp4" if codec=="h264" else ".webm"), delete=False)
    out_path = out.name
    out.close()
    if codec == "h264":
        cmd = [
            "ffmpeg", "-y", "-framerate", str(fps), "-f", "image2",
            "-i", os.path.join(frames_dir, "f_%05d.png"),
            "-vf", f"scale={width}:{height}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            out_path,
        ]
    else:  # vp9/webm
        cmd = [
            "ffmpeg", "-y", "-framerate", str(fps), "-f", "image2",
            "-i", os.path.join(frames_dir, "f_%05d.png"),
            "-vf", f"scale={width}:{height}",
            "-c:v", "libvpx-vp9", "-pix_fmt", "yuv420p",
            out_path,
        ]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    data = open(out_path, "rb").read()
    try:
        os.remove(out_path)
    except Exception:
        pass
    return data

def make_video(prompt: str, model_id: str, *, width: int, height: int, fps: int, seconds: int, codec: str, seed: int | None) -> tuple[bytes, str]:
    frames_dir, total = _write_frames_tmp(width, height, fps, seconds, prompt, model_id, seed)
    data = _encode_ffmpeg(frames_dir, total, fps, width, height, codec)
    try:
        import shutil
        shutil.rmtree(frames_dir, ignore_errors=True)
    except Exception:
        pass
    ext = "mp4" if codec == "h264" else "webm"
    return data, ext
