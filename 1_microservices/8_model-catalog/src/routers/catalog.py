
    from __future__ import annotations
    from fastapi import APIRouter, HTTPException, Query
    from typing import List, Dict, Any
    from ..util.logging import logger
    from ..aws_clients import ddb, smr
    from ..settings import settings
    from ..models import ModelSummary, ModelVersion, ModelCard, UpsertModel, UpsertVersion

    router = APIRouter()

    # -------- Helpers --------
    def _table(name: str):
        r = ddb()
        if r is None:
            return None
        return r.Table(name)

    def _seed_data() -> Dict[str, Any]:
        # Used when DynamoDB is not reachable (local dev convenience)
        return {
            "models": [
                {"id":"base-v1","name":"Base Image Model","modalities":["image"],"family":"sdxl","default_version":"1.0","tags":["safety:allowed"]},
                {"id":"video-lite","name":"Video Lite","modalities":["video"],"family":"latent-video","default_version":"0.1","tags":["beta"]}
            ],
            "versions": {
                ("base-v1","1.0"): {"params":{"max_res":[1024,1024]},"artifacts":[{"type":"weights","uri":"smr:base-v1:1.0"}],"evals":[{"metric":"clipscore","value":0.31}]},
                ("video-lite","0.1"): {"params":{"fps":8,"seconds":4},"artifacts":[{"type":"weights","uri":"smr:video-lite:0.1"}],"evals":[{"metric":"vbench","value":0.12}]}
            },
            "cards": {
                ("base-v1","1.0"): "# Base Image Model
Intended use: concept art.
Limitations: low text fidelity.",
                ("video-lite","0.1"): "# Video Lite
Short clips for previews."
            }
        }

    # -------- Routes --------
    @router.get("/models")
    def list_models(modality: str | None = Query(default=None), tag: str | None = Query(default=None)) -> Dict[str, List[ModelSummary]]:
        t = _table(settings.ddb_models)
        items: List[Dict[str, Any]] = []
        if t is None:
            items = _seed_data()["models"]
        else:
            # Scan is acceptable for v1; add GSIs (by modality/tags) for prod
            resp = t.scan()
            items = resp.get("Items", [])
        if modality:
            items = [m for m in items if modality in m.get("modalities", [])]
        if tag:
            items = [m for m in items if tag in m.get("tags", [])]
        return {"items": [ModelSummary(**m).model_dump() for m in items]}

    @router.get("/models/{model_id}")
    def get_model(model_id: str) -> ModelSummary:
        t = _table(settings.ddb_models)
        if t is None:
            m = next((m for m in _seed_data()["models"] if m["id"] == model_id), None)
            if not m:
                raise HTTPException(404, "not found")
            return ModelSummary(**m)
        resp = t.get_item(Key={"model_id": model_id})
        item = resp.get("Item")
        if not item:
            raise HTTPException(404, "not found")
        return ModelSummary(**item)

    @router.get("/models/{model_id}/versions")
    def list_versions(model_id: str) -> Dict[str, List[ModelVersion]]:
        t = _table(settings.ddb_versions)
        items: List[Dict[str, Any]] = []
        if t is None:
            items = []
            for (mid, ver), body in _seed_data()["versions"].items():
                if mid == model_id:
                    x = {"model_id": mid, "version": ver, **body}
                    items.append(x)
        else:
            resp = t.query(KeyConditionExpression="model_id = :m", ExpressionAttributeValues={":m": model_id})
            items = resp.get("Items", [])
        items.sort(key=lambda x: x.get("version",""))
        return {"items": [ModelVersion(**v).model_dump() for v in items]}

    @router.get("/models/{model_id}/versions/{ver}")
    def get_version(model_id: str, ver: str) -> ModelVersion:
        t = _table(settings.ddb_versions)
        if t is None:
            body = _seed_data()["versions"].get((model_id, ver))
            if not body:
                raise HTTPException(404, "not found")
            return ModelVersion(model_id=model_id, version=ver, **body)
        resp = t.get_item(Key={"model_id": model_id, "version": ver})
        item = resp.get("Item")
        if not item:
            raise HTTPException(404, "not found")
        return ModelVersion(**item)

    @router.get("/models/{model_id}/card")
    def get_card(model_id: str, ver: str | None = None) -> ModelCard:
        # choose default_version if ver not set
        if ver is None:
            ms = get_model(model_id)
            if not ms.default_version:
                raise HTTPException(400, "version not provided and no default_version set")
            ver = ms.default_version
        t = _table(settings.ddb_cards)
        if t is None:
            content = _seed_data()["cards"].get((model_id, ver))
            if not content:
                raise HTTPException(404, "not found")
            return ModelCard(model_id=model_id, version=ver, content=content)
        resp = t.get_item(Key={"model_id": model_id, "version": ver})
        item = resp.get("Item")
        if not item:
            raise HTTPException(404, "not found")
        return ModelCard(model_id=model_id, version=ver, format=item.get("format","markdown"), content=item.get("content",""))

    # ---- Admin (optional) ----
    @router.post("/models")
    def upsert_model(payload: UpsertModel):
        if not settings.mutable:
            raise HTTPException(403, "mutations disabled")
        t = _table(settings.ddb_models)
        if t is None:
            return {"ok": True, "dev_mode": True}
        item = {
            "model_id": payload.id,
            "name": payload.name,
            "family": payload.family,
            "modalities": payload.modalities,
            "tags": payload.tags,
            "default_version": payload.default_version,
        }
        t.put_item(Item=item)
        return {"ok": True}

    @router.post("/models/{model_id}/versions")
    def upsert_version(model_id: str, payload: UpsertVersion):
        if not settings.mutable:
            raise HTTPException(403, "mutations disabled")
        if payload.model_id != model_id:
            raise HTTPException(400, "model_id mismatch")
        t = _table(settings.ddb_versions)
        if t is None:
            return {"ok": True, "dev_mode": True}
        item = {
            "model_id": payload.model_id,
            "version": payload.version,
            "params": payload.params,
            "artifacts": payload.artifacts,
            "evals": payload.evals,
        }
        t.put_item(Item=item)
        return {"ok": True}
