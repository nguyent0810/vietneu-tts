import json

import pytest

from library.tools import lib


def _profile(monkeypatch, data):
    monkeypatch.setattr(lib, "load_profile", lambda channel: data if channel == "fs" else {})


def test_retire_chặn_hold_cảnh_báo_và_lane_thiếu(monkeypatch, capsys):
    _profile(monkeypatch, {"khuon": [
        {"ten": "nguhanh", "quyet_dinh": "retire", "ly_do_quyet_dinh": "không hiệu quả", "thay_bang": ["tuoi"]},
        {"ten": "nhao", "quyet_dinh": "hold", "ly_do_quyet_dinh": "chờ dữ liệu", "thay_bang": ["tuoi"]},
    ]})
    with pytest.raises(SystemExit, match="DỪNG:.*không hiệu quả.*tuoi"):
        lib.enforce_lane("fs", "nguhanh")
    assert lib.enforce_lane("fs", "nhao") ["quyet_dinh"] == "hold"
    assert "CẢNH BÁO" in capsys.readouterr().out
    assert lib.enforce_lane("fs", "khong_khai") is None


def test_co_the_vuot_retire(monkeypatch, capsys):
    _profile(monkeypatch, {"khuon": [{"ten": "nguhanh", "quyet_dinh": "retire", "ly_do_quyet_dinh": "x", "thay_bang": ["tuoi"]}]})
    lib.enforce_lane("fs", "nguhanh", allow_retire=True)
    assert "VƯỢT RETIRE" in capsys.readouterr().out


def test_sync_channels_giu_quyet_dinh(tmp_path, monkeypatch):
    channel_dir = tmp_path / "library" / "channels"
    channel_dir.mkdir(parents=True)
    brief_dir = tmp_path / "output" / "cl_staging" / "briefs"
    brief_dir.mkdir(parents=True)
    (tmp_path / "output" / "cl_staging" / "grok").mkdir(parents=True)
    (tmp_path / "output" / "cl_staging" / "grok" / "rules.md").write_text("5. luật FS. BUD: luật BUD\n")
    for channel in ("fs", "bud"):
        (brief_dir / f"{channel}.md").write_text("## Short — luật dừng khuôn\n| khuôn | n | kết luận |\n|---|---|---|\n| test | 1 | giữ |\n")
        existing = {"kenh": channel, "khuon": [{"ten": "test", "khai_tay": True, "quyet_dinh": "retire", "quyet_dinh_ngay": "2026-11-02", "thay_bang": ["tuoi"]}]}
        (channel_dir / f"{channel}.yaml").write_text(json.dumps(existing))
    monkeypatch.setattr(lib, "CHANNELS", channel_dir)
    lib.sync_channels(tmp_path)
    for channel in ("fs", "bud"):
        saved = json.loads((channel_dir / f"{channel}.yaml").read_text())
        decision = next(x for x in saved["khuon"] if x["ten"] == "test")
        assert decision["quyet_dinh"] == "retire"
        assert decision["quyet_dinh_ngay"] == "2026-11-02"


def test_sync_channels_bao_loi_ten_trung(tmp_path, monkeypatch):
    channel_dir = tmp_path / "library" / "channels"
    channel_dir.mkdir(parents=True)
    brief_dir = tmp_path / "output" / "cl_staging" / "briefs"
    brief_dir.mkdir(parents=True)
    (tmp_path / "output" / "cl_staging" / "grok").mkdir(parents=True)
    (tmp_path / "output" / "cl_staging" / "grok" / "rules.md").write_text("5. luật FS. BUD: luật BUD\n")
    (brief_dir / "fs.md").write_text("## Short — luật dừng khuôn\n| khuôn | n | kết luận |\n|---|---|---|\n| test | 1 | giữ |\n")
    (brief_dir / "bud.md").write_text("## Short — luật dừng khuôn\n| khuôn | n | kết luận |\n|---|---|---|\n| test | 1 | giữ |\n")
    duplicate = {"ten": "same", "quyet_dinh": "retire"}
    (channel_dir / "fs.yaml").write_text(json.dumps({"khuon": [duplicate, dict(duplicate, quyet_dinh="hold")]}))
    monkeypatch.setattr(lib, "CHANNELS", channel_dir)
    with pytest.raises(ValueError, match="ten.*trùng.*same"):
        lib.sync_channels(tmp_path)
