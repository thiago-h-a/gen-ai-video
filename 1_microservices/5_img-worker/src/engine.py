
from __future__ import annotations

import io
import math
import random
from datetime import datetime
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

# Try to use a common sans-serif font; Pillow falls back to default otherwise.
try:
    FONT = ImageFont.truetype("DejaVuSans.ttf", 20)
except Exception:  # pragma: no cover
    from PIL import ImageFont as _IF
    FONT = _IF.load_default()


def _noise_color(seed: int, x: int, y: int, w: int, h: int) -> Tuple[int, int, int]:
    # Simple deterministic pseudo-noise based on coordinates
    rnd = (seed * 73856093 ^ (x + 1) * 19349663 ^ (y + 1) * 83492791) & 0xFFFFFF
    r = (rnd >> 16) & 0xFF
    g = (rnd >> 8) & 0xFF
    b = rnd & 0xFF
    return r, g, b


def generate_png(prompt: str, model_id: str, *, width: int, height: int, seed: int | None = None) -> bytes:
    """Generate a synthetic PNG with the prompt text over a colored field.

    This is a stand-in for a real GPU model inference. It creates a gradient/noise
    background and overlays the prompt and model id.
    """
    if seed is None:
        seed = int(datetime.utcnow().timestamp())
    img = Image.new("RGB", (width, height))
    px = img.load()

    # Fill with deterministic pseudo-noise
    for y in range(height):
        for x in range(width):
            px[x, y] = _noise_color(seed, x, y, width, height)

    draw = ImageDraw.Draw(img)

    # translucent ribbon
    ribbon_h = min(120, height // 4)
    ribbon_color = (0, 0, 0)
    draw.rectangle([(0, 0), (width, ribbon_h)], fill=ribbon_color)

    # titles
    text1 = f"Model: {model_id}"
    text2 = prompt[:120] + ("…" if len(prompt) > 120 else "")
    draw.text((10, 10), text1, font=FONT, fill=(255, 255, 255))
    draw.text((10, 40), text2, font=FONT, fill=(255, 255, 255))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
