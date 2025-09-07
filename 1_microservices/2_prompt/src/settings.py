
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class Settings:
    fair_url: str = os.getenv("FAIR_SCHEDULER_URL", "http://fair-scheduler.ai-microgen.svc:8087")
    max_prompt_len: int = int(os.getenv("MAX_PROMPT_LEN", "2000"))

settings = Settings()
