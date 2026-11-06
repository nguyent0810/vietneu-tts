import importlib.util
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_mark_library_used_is_idempotent_across_days(tmp_path, monkeypatch, capsys):
    publish = load("publish_long_198", REPO / "creator_v2/motion/long/publish_long.py")
    assets = load("assets_198", REPO / "library/tools/assets.py")
    manifest = tmp_path / "manifest.jsonl"
    assets.write_manifest(manifest, [{"asset_id": "a", "video_da_dung": []}])
    img = tmp_path / "img"
    img.mkdir()
    (img / "a.json").write_text(json.dumps({"asset_id": "a"}), encoding="utf-8")
    (img / "b.json").write_text(json.dumps({"asset_id": "missing"}), encoding="utf-8")
    (img / "c.json").write_text("{}", encoding="utf-8")
    original = assets.mark_used
    calls = []
    def mark(asset_id, video_id, channel, day, *, ngay_public):
        calls.append((asset_id, video_id, channel, day, ngay_public))
        return original(asset_id, video_id, channel, day, manifest, ngay_public)
    class Loader:
        def exec_module(self, module):
            module.mark_used = mark
    class Spec:
        loader = Loader()
    monkeypatch.setattr(publish.importlib.util, "spec_from_file_location", lambda *a: Spec())
    monkeypatch.setattr(publish.importlib.util, "module_from_spec", lambda spec: type("Fake", (), {})())
    class FirstDay:
        @staticmethod
        def today():
            from datetime import date
            return date(2026, 11, 6)
    class SecondDay:
        @staticmethod
        def today():
            from datetime import date
            return date(2026, 11, 7)
    monkeypatch.setattr(publish, "date", FirstDay)
    publish.mark_library_used(img, "video", "MIM", "2026-11-10T12:00:00Z")
    monkeypatch.setattr(publish, "date", SecondDay)
    publish.mark_library_used(img, "video", "MIM", "2026-11-10T12:00:00Z")
    assert calls[0] == ("a", "video", "MIM", "2026-11-06", "2026-11-10")
    assert assets.load_manifest(manifest)[0]["video_da_dung"] == [
        {"video_id": "video", "kenh": "MIM", "ngay": "2026-11-06", "ngay_public": "2026-11-10"}]
    assert "Không ghi được" in capsys.readouterr().out
