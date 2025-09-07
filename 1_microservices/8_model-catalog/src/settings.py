
from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class Settings:
    region: str | None = os.getenv("AWS_REGION")
    ddb_models: str = os.getenv("CATALOG_DDB_MODELS", "model_catalog_models")
    ddb_versions: str = os.getenv("CATALOG_DDB_VERSIONS", "model_catalog_versions")
    ddb_cards: str = os.getenv("CATALOG_DDB_CARDS", "model_catalog_cards")
    mutable: bool = os.getenv("CATALOG_MUTABLE", "0") in {"1","true","yes"}
    smr_enabled: bool = os.getenv("SMR_ENABLED", "0") in {"1","true","yes"}
    smr_pkg_group_tag: str | None = os.getenv("SMR_PACKAGE_GROUP_TAG")

settings = Settings()
