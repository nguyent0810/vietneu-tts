from pathlib import Path
import sys
import shutil
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "stier"), str(ROOT / "motion"), str(ROOT)]
import build as B


def spec(scene_type, theme="ck"):
    # #270: preflight kiểm schema, nên cảnh mẫu phải có đủ trường bắt buộc của loại đó.
    fields = {"kinetic": {"items": [{"text": "A", "at": 0}]}, "chart": {"bars": [{"v": 1, "at": 0}]},
              "cards3d": {"cards": [{"k": "A", "v": "1", "at": 0}]}}.get(scene_type, {})
    return {"lines": ["lời kể " * 30], "theme": theme, "scenes": [{"type": scene_type, **fields}]}


def test_preflight_rejects_unknown_and_accepts_registered_scenes():
    assert any("loại cảnh lạ" in e for e in B.spec_preflight_errors("x", spec("clip")))
    for scene_type in ("kinetic", "chart", "cards3d"):
        assert not B.spec_preflight_errors("x", spec(scene_type))
    assert not B.spec_preflight_errors("x", spec("hf_wheel", "bud"))
    assert any("loại cảnh lạ" in e for e in B.spec_preflight_errors("x", spec("hf_wheel")))
    assert any("loại cảnh lạ" in e for e in B.spec_preflight_errors("x", spec("hf_missing", "bud")))
    assert any("loại cảnh lạ" in e for e in B.spec_preflight_errors("x", spec(None)))


def test_hfs_loading_uses_registered_device_file():
    tags = B.hfs_tags({"theme": "bud"}, [{"type": "hf_count_ring"}])
    assert 'hfs/bridge.js' in tags and 'hfs/number.js' in tags
    assert B.hfs_tags({"theme": "ck"}, [{"type": "kinetic"}]) == ""


def test_registry_executes_actual_js_and_ignores_comments(tmp_path, monkeypatch):
    shutil.copytree(B.HF / "assets" / "engine", tmp_path / "assets" / "engine")
    monkeypatch.setattr(B, "HF", tmp_path)
    engine = tmp_path / "assets" / "engine" / "casefile.js"
    source = engine.read_text(encoding="utf-8")
    source = source.replace('  if (window.__SCENE_TYPES_ONLY)',
                            '  /* B.clip = () => {}; */\n  B["new_scene"] = () => {}; B.null_scene = null; B.object_scene = {};\n  if (window.__SCENE_TYPES_ONLY)')
    engine.write_text(source, encoding="utf-8")
    assert not B.spec_preflight_errors("x", spec("new_scene"))
    for invalid in ("clip", "null_scene", "object_scene"):
        assert any("loại cảnh lạ" in e for e in B.spec_preflight_errors("x", spec(invalid)))


def test_missing_registry_hook_fails_closed(tmp_path, monkeypatch):
    shutil.copytree(B.HF / "assets" / "engine", tmp_path / "assets" / "engine")
    monkeypatch.setattr(B, "HF", tmp_path)
    engine = tmp_path / "assets" / "engine" / "casefile.js"
    engine.write_text('/* no registry hook */', encoding="utf-8")
    with pytest.raises(RuntimeError, match="registry"):
        B.spec_preflight_errors("x", spec("kinetic"))


def test_unsupported_hfs_devices_remain_rejected():
    for name in ("hf_bars", "hf_ledger", "hf_source_card"):
        assert any("loại cảnh lạ" in e for e in B.spec_preflight_errors("x", spec(name, "bud")))


def test_invalid_device_definition_fails_closed(tmp_path, monkeypatch):
    shutil.copytree(B.HF / "assets" / "engine", tmp_path / "assets" / "engine")
    monkeypatch.setattr(B, "HF", tmp_path)
    (tmp_path / "assets" / "engine" / "hfs" / "cycle.js").write_text(
        'HFS.device("wheel", {build: null});', encoding="utf-8")
    with pytest.raises(RuntimeError, match="registry"):
        B.spec_preflight_errors("x", spec("hf_wheel", "bud"))
