
from __future__ import annotations

import os
from dataclasses import dataclass

@dataclass
class Settings:
    artifacts_root: str = os.getenv("ARTIFACTS_ROOT", "/data/artifacts")
    img_width: int = int(os.getenv("IMG_WIDTH", "768"))
    img_height: int = int(os.getenv("IMG_HEIGHT", "512"))
    seed: int | None = int(os.getenv("SEED", "0")) if os.getenv("SEED") else None

settings = Settings()
