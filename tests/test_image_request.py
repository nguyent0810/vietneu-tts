from __future__ import annotations

import importlib.util
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("image_request", ROOT / "library/tools/image_request.py")
image_request = importlib.util.module_from_spec(spec)
spec.loader.exec_module(image_request)


def _asset(asset_id: str, scope: str, *, ai: bool = False, used: list | None = None) -> dict:
    return {
        "asset_id": asset_id, "kind": "img", "path": f"images/{asset_id}.png",
        "paths": [f"images/{asset_id}.png"], "sha256": asset_id[0] * 64,
        "byte": 1, "w": 1200, "h": 800, "pham_vi": scope,
        "tags": {"core": ["ngoi_chua"], "domain": ["ngoi_chua"]},
        "source": {"type": "internal", "ref": f"{asset_id}.png"},
        "license": {"type": "CC0 1.0", "commercial_allowed": True},
        "ai_generated": ai, "video_da_dung": used or [],
    }


def _repo(tmp_path: Path, *, channel: str = "demo", policy: dict | None = None,
          records: list[dict] | None = None) -> Path:
    repo = tmp_path / "repo"
    (repo / "library/channels").mkdir(parents=True)
    (repo / "library/assets/lexicon").mkdir(parents=True)
    profile = {
        "kenh": channel,
        "assets": {"phong_cach": "A {shot} photo of {subject}", "shot": ["wide"],
                   "lens": ["50mm"], "nen": ["dark"], "van_hoa": "Vietnamese",
                   "anh_sang": "soft light"},
        "kho_loc": policy or {},
    }
    (repo / f"library/channels/{channel}.yaml").write_text(json.dumps(profile), encoding="utf-8")
    (repo / "library/assets/lexicon/chung.json").write_text(json.dumps({
        "muc": [{"vi": "ngôi chùa", "en": "an old Vietnamese pagoda", "nhom": "chua"}]
    }), encoding="utf-8")
    (repo / "library/assets/lexicon/demo.json").write_text(json.dumps({"muc": []}), encoding="utf-8")
    manifest = repo / "library/assets/manifest.jsonl"
    manifest.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in (records or [])), encoding="utf-8")
    return repo


def test_real_manifest_prefers_channel_then_shared_and_uses_root_default(tmp_path):
    repo = _repo(tmp_path, records=[_asset("a" * 16, "chung"), _asset("b" * 16, "demo")])
    found = image_request.resolve_image("ngôi chùa", "demo", root=repo, today=date(2026, 11, 5))
    assert found["scope"] == "kenh" and found["asset"]["asset_id"] == "b" * 16

    (repo / "library/assets/manifest.jsonl").write_text(json.dumps(_asset("a" * 16, "chung")) + "\n")
    found = image_request.resolve_image("ngôi chùa", "demo", root=repo, today=date(2026, 11, 5))
    assert found["scope"] == "chung" and found["asset"]["asset_id"] == "a" * 16


def test_real_manifest_applies_kho_loc_and_excludes_recently_used(tmp_path):
    repo = _repo(tmp_path, policy={"license_cho_phep": ["PD"]}, records=[
        _asset("a" * 16, "chung", used=[{"kenh": "demo", "ngay": "2026-11-01", "video_id": "old"}]),
    ])
    result = image_request.resolve_image("ngôi chùa", "demo", root=repo, today=date(2026, 11, 5))
    assert result["asset"] is None
    assert result["snapshot"]["fallback"] is False


def test_real_manifest_blocks_ai_for_cl_and_unmatched_need_builds_stable_fallback(tmp_path):
    repo = _repo(tmp_path, channel="cl", policy={"cam_anh_ai": True}, records=[
        _asset("a" * 16, "cl", ai=True),
    ])
    # The profile/manifest in root are used even when manifest_path is omitted.
    first = image_request.resolve_image("một mô tả cảnh tự do", "cl", root=repo, today=date(2026, 11, 5))
    second = image_request.resolve_image("một mô tả cảnh tự do", "cl", root=repo, today=date(2026, 11, 5))
    assert first["asset"] is None and first["prompt"]
    assert first["snapshot"]["fallback"] is True
    assert first["snapshot"]["entry"]["en"] == "một mô tả cảnh tự do"
    assert first["snapshot"] == second["snapshot"]
    assert first["snapshot"]["sha256"]
