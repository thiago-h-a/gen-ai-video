
from __future__ import annotations
import logging, os, sys, json
from datetime import datetime

def get_logger(name: str = "model-catalog") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    json_mode = os.getenv("LOG_JSON", "false").lower() in {"1","true","yes"}
    if json_mode:
        class _JF(logging.Formatter):
            def format(self, r: logging.LogRecord) -> str:
                return json.dumps({
                    "ts": datetime.utcfromtimestamp(r.created).isoformat()+"Z",
                    "lvl": r.levelname,
                    "name": r.name,
                    "msg": r.getMessage(),
                }, ensure_ascii=False)
        handler.setFormatter(_JF())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger

logger = get_logger()
