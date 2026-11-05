"""Hồ sơ kênh phải là JSON tự mô tả, không chứa cấu hình bí mật."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from library.tools import channel_profile


ROOT = Path(__file__).resolve().parents[1]
CHANNELS = ROOT / "library" / "channels"
TYPE_KEYS = {
    "kenh": str, "ngach": list, "khuon": list, "bao_ve": list,
    "assets": dict, "canh": dict, "typography": dict, "motion": dict,
    "sound": dict, "tts": dict, "kho_loc": dict,
}


def test_channel_profiles_are_json_and_minimally_typed():
    for path in CHANNELS.glob("*.yaml"):
        if path.stem.startswith("_"):
            continue
        profile = json.loads(path.read_text(encoding="utf-8"))
        assert profile["kenh"] == path.stem
        for key, expected in TYPE_KEYS.items():
            if key in profile:
                assert isinstance(profile[key], expected), (path.name, key)
        assert all(isinstance(item, dict) for item in profile.get("khuon", []))
        names = [item.get("ten") for item in profile.get("khuon", [])]
        assert len(names) == len(set(names))
        raw = path.read_text(encoding="utf-8").casefold()
        assert "creds" not in raw and ".json\"" not in raw


def test_resolve_and_legacy_id():
    assert channel_profile.resolve({"channel": "CK"}) == "ck"
    assert channel_profile.resolve({"kenh": "Văn Sử Địa"}) == "vsd"
    assert channel_profile.resolve(slug="ck-abc") == "ck"
    with pytest.raises(ValueError):
        channel_profile.resolve(slug="long-abc")
    with pytest.raises(ValueError):
        channel_profile.resolve({})
    assert channel_profile.load("_thu_lich_su")["kenh"] == "lich_su"


def test_mim_ck_cl_are_copied_from_channel_tables():
    """Kiểm chứng các giá trị có nguồn code, không thêm lựa chọn dựng mới."""
    sys.path.insert(0, str(ROOT / "creator_v2" / "motion" / "long"))
    import build_long

    source = (ROOT / "creator_v2/motion/long/build_long.py").read_text(encoding="utf-8")
    short_source = (ROOT / "creator_v2/motion/stier/themes.py").read_text(encoding="utf-8")
    table = build_long._channels()
    expected = {
        "mim": ("Thanh Bình", "Ngọc Huyền", "lab", "MIND IN THE MACHINE", "mim"),
        "ck": ("Ngọc Huyền", "Xuân Vĩnh", "chart", "BIỂU ĐỒ BIẾT NÓI", "ck"),
        "cl": ("Anh Khôi", "Minh Đức", "case", None, "case"),   # bảng Long không có brand CL: không tự đặt
    }
    for ident, (voice, quote, long_theme, brand, short_theme) in expected.items():
        profile = channel_profile.load(ident)
        assert profile["voice_profile"]["tham_so"]["dan"] == voice
        assert profile["voice_profile"]["tham_so"]["trich"] == quote
        want = {"long": long_theme, "short": short_theme, **({"brand": brand} if brand else {})}
        assert profile["theme"] == want
        row = table[ident.upper()]
        assert row["voice"] == voice and row["quote"] == quote
        if ident in ("mim", "ck"):
            assert row["theme"] == long_theme and row["brand"] == brand
        assert short_theme in short_source
    assert "MIND IN THE MACHINE" in source and "BIỂU ĐỒ BIẾT NÓI" in source


def test_resolve_accepts_legacy_lich_su_id():
    assert channel_profile.resolve({"kenh": "_thu_lich_su"}) == "lich_su"


def test_broken_profile_fails_closed_for_lane_gate(monkeypatch):
    """Review #165: hồ sơ có mà hỏng thì cổng RETIRE/HOLD phải dừng, không được trả {} cho qua."""
    import pytest
    from library.tools import lib

    def broken(_channel):
        raise ValueError("khoá 'khuon' phải là list")

    monkeypatch.setattr(channel_profile, "load", broken)
    with pytest.raises(SystemExit):
        lib.enforce_lane("bud", "jataka")
    assert lib.load_profile("kenh_chua_khai") == {}
