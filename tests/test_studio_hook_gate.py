"""Cổng 3 giây đầu của Short (#253, ROT-03) trong studio.py:
- Áp cho BUD, FS, Văn Sử Địa (VSD).
- Cổng kiểm: ảnh đầu tối, câu 1 chữ trần, chữ hook hiện trễ quá 0,8 giây.
- Mặc định: CẢNH BÁO, không chặn.
- Có cờ --strict-hook để chặn.
"""
from pathlib import Path
import copy
import json
import shutil
import pytest
from PIL import Image

import studio


@pytest.fixture
def sample_spec(tmp_path):
    bright = tmp_path / "bright.jpg"
    Image.new("RGB", (32, 32), (180, 180, 180)).save(bright)
    dark = tmp_path / "dark.jpg"
    Image.new("RGB", (32, 32), (20, 20, 20)).save(dark)

    return {
        "id": "test_hook_01",
        "channel": "fs",
        "theme": "tet-poster",
        "kicker": "TỬ VI 2027",
        "lines": ["Sinh năm 2027 mệnh Thiên Hà Thủy.", "Lưu lại để tra cứu nhé."],
        "scenes": [
            {"device": "photo", "line": 0, "img": str(bright), "head": "BẢNG NĂM SINH"},
            {"device": "split", "line": 1, "head": "KẾT LUẬN"}
        ],
        "_tmp": tmp_path,
        "_bright": bright,
        "_dark": dark,
    }


def test_hook_gate_channels():
    assert studio.is_hook_gate_channel({"channel": "fs"}) is True
    assert studio.is_hook_gate_channel({"channel": "bud"}) is True
    assert studio.is_hook_gate_channel({"channel": "vsd"}) is True
    assert studio.is_hook_gate_channel({"channel": "Văn Sử Địa"}) is True
    assert studio.is_hook_gate_channel({"series": "fs"}) is True
    assert studio.is_hook_gate_channel({"voice_series": "bud"}) is True
    assert studio.is_hook_gate_channel({"channel": "other_random_channel"}) is False


def test_good_spec_passes_hook(sample_spec):
    errs = studio.hook_errors(sample_spec)
    assert errs == []


def test_gate_dark_image(sample_spec):
    bad = copy.deepcopy(sample_spec)
    bad["scenes"][0]["img"] = str(sample_spec["_dark"])
    errs = studio.hook_errors(bad)
    assert any("quá tối" in e for e in errs)


def test_gate_text_only_first_scene(sample_spec):
    bad = copy.deepcopy(sample_spec)
    bad["scenes"][0] = {"device": "hook_slam", "line": 0, "head": "TEXT ONLY"}
    errs = studio.hook_errors(bad)
    assert any("chỉ có chữ" in e for e in errs)

    # Thêm ảnh nền -> ĐẠT
    ok = copy.deepcopy(bad)
    ok["scenes"][0]["bg"] = str(sample_spec["_bright"])
    assert not any("chỉ có chữ" in e for e in studio.hook_errors(ok))


def test_gate_late_hook_text(sample_spec):
    bad = copy.deepcopy(sample_spec)
    bad["scenes"][0] = {
        "device": "photo",
        "line": 0,
        "img": str(sample_spec["_bright"]),
        "headAt": 1.2
    }
    errs = studio.hook_errors(bad)
    assert any("hiện lúc 1.20s (> 0.8s)" in e for e in errs)

    # Chữ hiện sớm <= 0.8s -> ĐẠT
    ok = copy.deepcopy(sample_spec)
    ok["scenes"][0]["headAt"] = 0.4
    assert not any("hiện lúc" in e for e in studio.hook_errors(ok))


def test_gate_late_hook_text_with_scene_at_zero(sample_spec):
    # Scene có "at": 0.0 kết hợp headAt: 1.2s -> vẫn phải bắt được lỗi trễ chữ hook
    bad = copy.deepcopy(sample_spec)
    bad["scenes"][0] = {
        "device": "photo",
        "line": 0,
        "at": 0.0,
        "img": str(sample_spec["_bright"]),
        "headAt": 1.2
    }
    errs = studio.hook_errors(bad)
    assert any("hiện lúc 1.20s (> 0.8s)" in e for e in errs)


def test_gate_anchor_timing_resolution(sample_spec):
    # Test mốc thời gian anchor dạng danh sách [line_idx, "word"] khi có truyền L
    spec = copy.deepcopy(sample_spec)
    L = [
        {"text": "Sinh năm 2027 mệnh Thiên Hà Thủy", "start": 0.0, "end": 2.0,
         "words": [{"w": "Sinh", "t": 0.0}, {"w": "năm", "t": 0.4}, {"w": "Thủy", "t": 1.5}]},
        {"text": "Lưu lại nhé", "start": 2.0, "end": 4.0, "words": [{"w": "Lưu", "t": 2.0}]}
    ]
    # Mốc anchor rơi vào 1.5s (> 0.8s) -> cảnh báo
    spec["scenes"][0]["headAt"] = [0, "Thủy"]
    errs = studio.hook_errors(spec, L=L)
    assert any("hiện lúc 1.50s (> 0.8s)" in e for e in errs)

    # Mốc anchor rơi vào 0.4s (<= 0.8s) -> ĐẠT
    spec["scenes"][0]["headAt"] = [0, "năm"]
    errs = studio.hook_errors(spec, L=L)
    assert not any("hiện lúc" in e for e in errs)


def test_gate_dark_image_no_duplicate_warning(sample_spec, tmp_path):
    # Tránh nhân đôi cảnh báo ảnh tối khi ảnh xuất hiện cả ở relative path và job/assets
    bad = copy.deepcopy(sample_spec)
    job_dir = tmp_path / "job_dedup"
    assets_dir = job_dir / "assets"
    assets_dir.mkdir(parents=True)
    dark_in_assets = assets_dir / "dark.jpg"
    shutil.copy(sample_spec["_dark"], dark_in_assets)

    bad["scenes"][0]["img"] = "assets/dark.jpg"
    errs = studio.hook_errors(bad, job_dir=job_dir)
    dark_errs = [e for e in errs if "quá tối" in e]
    assert len(dark_errs) == 1


def test_gate_late_scene_start(sample_spec):
    bad = copy.deepcopy(sample_spec)
    bad["scenes"][0]["line"] = 1
    errs = studio.hook_errors(bad)
    assert any("phải bắt đầu ở câu 0" in e for e in errs)


def test_warn_only_by_default(sample_spec, monkeypatch, tmp_path):
    # Spec vi phạm chữ trần (dạng bảng năm sinh FS)
    bad_spec = {k: v for k, v in sample_spec.items() if not k.startswith("_")}
    bad_spec["scenes"][0] = {"device": "hook_poster", "line": 0, "head": "BẢNG"}

    spec_file = tmp_path / "spec.json"
    spec_file.write_text(json.dumps(bad_spec, ensure_ascii=False), encoding="utf-8")

    # Mặc định strict_hook=False: cảnh báo nhưng KHÔNG chặn (không raise SystemExit)
    L_mock = [
        {"text": "Sinh năm 2027", "start": 0.0, "end": 2.0, "words": []},
        {"text": "Lưu lại", "start": 2.0, "end": 4.0, "words": []}
    ]
    monkeypatch.setattr(studio, "line_words", lambda *a: L_mock)
    monkeypatch.setattr(studio, "variety", lambda *a: [])
    monkeypatch.setattr(studio, "compose", lambda *a: "<html></html>")
    monkeypatch.setattr(studio, "JOBS", tmp_path / "jobs")

    import hf_batch_render as R
    def dummy_render_tts(txt, wav, clean, voice, **kw):
        wav.write_bytes(b"dummy")
        wav.with_suffix(".json").write_text(json.dumps({"segments": []}), encoding="utf-8")
        return True
    monkeypatch.setattr(R, "render_tts", dummy_render_tts)

    # build(..., strict_hook=False) -> không raise
    res = studio.build(spec_file, render=False, do_qa=False, strict=False, use_ledger=False, strict_hook=False)
    assert res is True

    # build(..., strict_hook=True) -> raise SystemExit do có cờ chặn (khi do_qa=False)
    with pytest.raises(SystemExit) as excinfo:
        studio.build(spec_file, render=False, do_qa=False, strict=False, use_ledger=False, strict_hook=True)
    assert "cổng 3 giây đầu" in str(excinfo.value)


def test_qa_gate_strict_hook(monkeypatch, tmp_path):
    rep = {"lint": {"ok": True}, "check": {"ok": True}, "hook": {"ok": False, "warnings": ["lỗi hook"]}}
    monkeypatch.setattr(studio, "qa", lambda *a, **k: rep)
    # qa_gate không có strict_hook -> vẫn True
    assert studio.qa_gate(tmp_path, 10.0, [], None, strict=True, strict_hook=False) is True
    # qa_gate có strict_hook -> False
    assert studio.qa_gate(tmp_path, 10.0, [], None, strict=True, strict_hook=True) is False


def test_integration_build_qa_strict_hook(sample_spec, monkeypatch, tmp_path):
    # Test luồng tích hợp: build(..., do_qa=True, strict_hook=True)
    # Kiểm tra qa.json được ghi nhận đúng schema rep["hook"] và qa_gate chặn thành công
    bad_spec = {k: v for k, v in sample_spec.items() if not k.startswith("_")}
    bad_spec["scenes"][0] = {"device": "hook_poster", "line": 0, "head": "BẢNG"}

    spec_file = tmp_path / "spec.json"
    spec_file.write_text(json.dumps(bad_spec, ensure_ascii=False), encoding="utf-8")

    L_mock = [
        {"text": "Sinh năm 2027", "start": 0.0, "end": 2.0, "words": []},
        {"text": "Lưu lại", "start": 2.0, "end": 4.0, "words": []}
    ]
    monkeypatch.setattr(studio, "line_words", lambda *a: L_mock)
    monkeypatch.setattr(studio, "variety", lambda *a: [])
    monkeypatch.setattr(studio, "compose", lambda *a: "<html></html>")
    monkeypatch.setattr(studio, "JOBS", tmp_path / "jobs")

    import hf_batch_render as R
    def dummy_render_tts(txt, wav, clean, voice, **kw):
        wav.write_bytes(b"dummy")
        wav.with_suffix(".json").write_text(json.dumps({"segments": []}), encoding="utf-8")
        return True
    monkeypatch.setattr(R, "render_tts", dummy_render_tts)

    import subprocess
    def dummy_hf(job, args, timeout=1800):
        if "lint" in args:
            return subprocess.CompletedProcess(args=[], returncode=0, stdout='{"ok": true, "findings": []}', stderr="")
        if "check" in args:
            return subprocess.CompletedProcess(args=[], returncode=0, stdout='{"ok": true, "runtime": {}, "layout": {}, "contrast": {}}', stderr="")
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="{}", stderr="")
    monkeypatch.setattr(studio, "hf", dummy_hf)

    # 1. Với strict_hook=True và do_qa=True:
    # build trả về False (qa_gate chặn), qa.json được sinh ra và ghi nhận rep["hook"]
    res = studio.build(spec_file, render=False, do_qa=True, strict=False, use_ledger=False, strict_hook=True)
    assert res is False

    qa_file = tmp_path / "jobs" / bad_spec["id"] / "qa.json"
    assert qa_file.exists()
    qa_data = json.loads(qa_file.read_text(encoding="utf-8"))
    assert "hook" in qa_data
    assert qa_data["hook"]["ok"] is False
    assert len(qa_data["hook"]["warnings"]) > 0

    # 2. Với strict_hook=False và do_qa=True (mặc định):
    # build trả về True (chỉ cảnh báo), qa.json vẫn ghi nhận hook không ok
    res_warn = studio.build(spec_file, render=False, do_qa=True, strict=False, use_ledger=False, strict_hook=False)
    assert res_warn is True


def test_gate_hook_text_at_exact_boundary_passes(sample_spec):
    spec = copy.deepcopy(sample_spec)
    spec["scenes"][0]["headAt"] = 0.8
    assert not any("hiện lúc" in e for e in studio.hook_errors(spec))


def test_gate_static_head_with_delayed_item_passes(sample_spec):
    spec = copy.deepcopy(sample_spec)
    spec["scenes"][0]["head"] = "TIÊU ĐỀ TĨNH"
    spec["scenes"][0]["items"] = [{"text": "Ý phụ", "at": 1.5}]
    assert not any("hiện lúc" in e for e in studio.hook_errors(spec))


def test_channel_non_fs_containing_fs_ignored():
    assert studio.is_hook_gate_channel({"channel": "drafts_channel"}) is False
    assert studio.is_hook_gate_channel({"channel": "offset_show"}) is False
    assert studio.is_hook_gate_channel({"channel": "cliffs"}) is False
    assert studio.is_hook_gate_channel({"channel": "briefs"}) is False
    # Nhưng kênh hợp lệ vẫn phải True
    assert studio.is_hook_gate_channel({"channel": "fs_daily"}) is True
    assert studio.is_hook_gate_channel({"channel": "kenh_bud"}) is True

