
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Settings:
    data_dir: str = os.getenv("REGISTRY_DATA_DIR", str(Path(__file__).resolve().parents[1] / "data" / "models"))
    mutable: bool = os.getenv("REGISTRY_MUTABLE", "0") in {"1", "true", "yes"}

settings = Settings()
