"""Regression coverage for Long's profile-backed channel table."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "motion" / "long"), str(ROOT / "motion"), str(ROOT / "motion" / "stier")]

import build_long as build_long  # noqa: E402
import channel_table  # noqa: E402
import themes  # noqa: E402
import variety  # noqa: E402


# Snapshot copied from build_long._channels on 2026-11-05, base 6aaaf68a76d75f00df27624fe0cf1113324c3055.
LEGACY_CHANNELS = {
    "CL": {"voice": "Anh Khôi", "quote": "Minh Đức", "voice_fx": themes.VOICE_FX_CL},
    "MIM": {"voice": "Thanh Bình", "quote": "Ngọc Huyền", "theme": "lab", "brand": "MIND IN THE MACHINE",
            "accent": "#22d3ee", "pools": themes.THEMES["mim"]["pools"], "no_sa": True},
    "CK": {"voice": "Ngọc Huyền", "quote": "Xuân Vĩnh", "ask": "Phạm Tuyên", "theme": "chart", "brand": "BIỂU ĐỒ BIẾT NÓI",
           "accent": "#fbbf24", "pools": themes.THEMES["mim"]["pools"], "no_sa": True},
}


def test_profile_channel_table_matches_legacy_snapshot():
    assert build_long._channels() == LEGACY_CHANNELS


def test_variety_channel_theme_matches_legacy_dict():
    assert variety.CHANNEL_THEME == {"MIM": "lab", "CK": "chart"}


def test_every_current_long_spec_resolves_a_channel():
    for path in sorted((ROOT / "data" / "long").glob("*/spec.json")):
        spec = json.loads(path.read_text(encoding="utf-8"))
        assert channel_table.resolve_long_channel(spec) in {"CL", "MIM", "CK"}, path


def test_long_spec_without_channel_is_refused():
    with pytest.raises(ValueError, match="Thiếu channel"):
        channel_table.resolve_long_channel({"title": "t", "chapters": []})
