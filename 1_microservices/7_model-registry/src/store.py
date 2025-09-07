
    from __future__ import annotations
    import json
    from pathlib import Path
    from typing import Dict, Iterable, List, Optional

    from .models import ModelManifest
    from .settings import settings
    from .util.logging import logger

    def _iter_manifest_paths() -> Iterable[Path]:
        base = Path(settings.data_dir)
        if not base.exists():
            return []
        return sorted(p for p in base.glob("*.json") if p.is_file())

    def list_models() -> List[ModelManifest]:
        items: List[ModelManifest] = []
        for path in _iter_manifest_paths():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                items.append(ModelManifest.model_validate(data))
            except Exception as e:
                logger.warning("invalid manifest %s: %s", path, e)
        return items

    def get_model(model_id: str) -> Optional[ModelManifest]:
        path = Path(settings.data_dir) / f"{model_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return ModelManifest.model_validate(data)
        except Exception as e:
            logger.warning("invalid manifest %s: %s", path, e)
            return None

    def upsert_model(manifest: ModelManifest) -> None:
        if not settings.mutable:
            raise PermissionError("registry is read-only; set REGISTRY_MUTABLE=1 to enable writes")
        path = Path(settings.data_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / f"{manifest.id}.json").write_text(
            json.dumps(manifest.model_dump(), indent=2, ensure_ascii=False) + "
",
            encoding="utf-8",
        )
