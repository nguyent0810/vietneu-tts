"""P4b (E2E validation remediation) -- symbol_asset_path is resolved ONCE
and baked into shot_list_final.json at shot-list-creation time
(creative_director.py). Real incident (FS channel, found during E2E
validation): the symbol_library naming convention changed later (flat
filename -> 3-color rotation) with no flat file left on disk at all --
resuming/re-rendering an OLD shot list crashed deep inside ffmpeg with a
generic "No such file or directory" instead of self-healing via the
CURRENT config (which still has a perfectly valid replacement asset)."""
from __future__ import annotations

import json

import pytest

import domain_creative_profiles as cp


def _write_profiles(tmp_path, monkeypatch, profiles: dict):
    profiles_file = tmp_path / "domain_creative_profiles.json"
    profiles_file.write_text(json.dumps(profiles, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(cp, "PROFILES_FILE", profiles_file)


def _write_shot_list(tmp_path, beats):
    shot_list_path = tmp_path / "shot_list_final.json"
    shot_list_path.write_text(json.dumps({"beats": beats}), encoding="utf-8")
    return shot_list_path


# --- get_symbol_entry_by_key() ----------------------------------------------


def test_get_symbol_entry_by_key_finds_the_right_entry():
    profile = {"symbol_library": [{"key": "a"}, {"key": "b", "note": "x"}]}
    assert cp.get_symbol_entry_by_key(profile, "b") == {"key": "b", "note": "x"}


def test_get_symbol_entry_by_key_returns_none_if_missing():
    profile = {"symbol_library": [{"key": "a"}]}
    assert cp.get_symbol_entry_by_key(profile, "not_there") is None


# --- heal_stale_symbol_asset_paths() -----------------------------------------


def test_noop_when_everything_still_exists(tmp_path, monkeypatch):
    asset = tmp_path / "bat_quai.png"
    asset.write_bytes(b"x")
    _write_profiles(tmp_path, monkeypatch, {
        "FS": {"symbol_library": [{"key": "bat_quai", "asset_path": str(asset)}]},
    })
    shot_list_path = _write_shot_list(tmp_path, [
        {"symbol_key": "bat_quai", "asset_path": str(asset), "treatment": "image"},
    ])
    mtime_before = shot_list_path.stat().st_mtime_ns

    healed = cp.heal_stale_symbol_asset_paths(str(shot_list_path), "FS")

    assert healed == 0
    assert shot_list_path.stat().st_mtime_ns == mtime_before, "must not rewrite the shot list when nothing is stale"


def test_beats_without_symbol_key_are_never_touched(tmp_path, monkeypatch):
    _write_profiles(tmp_path, monkeypatch, {"FS": {"symbol_library": []}})
    shot_list_path = _write_shot_list(tmp_path, [
        {"treatment": "video", "asset_path": str(tmp_path / "nonexistent_video.mp4")},
    ])
    healed = cp.heal_stale_symbol_asset_paths(str(shot_list_path), "FS")
    assert healed == 0


def test_reproduces_the_real_fs_incident_shape_flat_file_replaced_by_rotation(tmp_path, monkeypatch):
    """Exact real bug shape: shot list references a flat filename that no
    longer exists on disk; the CURRENT profile config has moved to a
    3-color-rotation `asset_paths` list instead. Healing must pick up a
    valid current variant and rewrite the shot list."""
    stale_flat_path = tmp_path / "bat_quai_hau_thien.png"  # never created -- simulates "deleted/renamed away"
    gold = tmp_path / "bat_quai_hau_thien_gold.png"
    jade = tmp_path / "bat_quai_hau_thien_jade.png"
    gold.write_bytes(b"gold")
    jade.write_bytes(b"jade")
    monkeypatch.setattr(cp, "SYMBOL_VARIANT_ROTATION_STATE_PATH", tmp_path / "rotation_state.json")
    _write_profiles(tmp_path, monkeypatch, {
        "FS": {"symbol_library": [{"key": "bat_quai_hau_thien", "asset_paths": [str(gold), str(jade)]}]},
    })
    shot_list_path = _write_shot_list(tmp_path, [
        {"symbol_key": "bat_quai_hau_thien", "asset_path": str(stale_flat_path), "symbol_asset_path": str(stale_flat_path), "treatment": "image"},
    ])

    healed = cp.heal_stale_symbol_asset_paths(str(shot_list_path), "FS")

    assert healed == 1
    data = json.loads(shot_list_path.read_text(encoding="utf-8"))
    new_path = data["beats"][0]["asset_path"]
    assert new_path in (str(gold), str(jade)), "must re-resolve to one of the CURRENT valid variants"
    assert data["beats"][0]["symbol_asset_path"] == new_path, "symbol_asset_path must stay in sync with asset_path"


def test_raises_when_symbol_key_no_longer_exists_in_current_profile(tmp_path, monkeypatch):
    _write_profiles(tmp_path, monkeypatch, {"FS": {"symbol_library": []}})  # entry removed entirely
    shot_list_path = _write_shot_list(tmp_path, [
        {"symbol_key": "removed_symbol", "asset_path": str(tmp_path / "gone.png"), "treatment": "image"},
    ])
    with pytest.raises(RuntimeError, match="KHÔNG còn entry"):
        cp.heal_stale_symbol_asset_paths(str(shot_list_path), "FS")


def test_raises_when_current_entry_also_points_at_a_missing_file(tmp_path, monkeypatch):
    _write_profiles(tmp_path, monkeypatch, {
        "FS": {"symbol_library": [{"key": "bat_quai", "asset_path": str(tmp_path / "also_missing.png")}]},
    })
    shot_list_path = _write_shot_list(tmp_path, [
        {"symbol_key": "bat_quai", "asset_path": str(tmp_path / "old_missing.png"), "treatment": "image"},
    ])
    with pytest.raises(RuntimeError, match="không thể tự hồi phục"):
        cp.heal_stale_symbol_asset_paths(str(shot_list_path), "FS")


def test_heals_only_the_stale_beats_leaves_valid_ones_alone(tmp_path, monkeypatch):
    valid_asset = tmp_path / "valid.png"
    valid_asset.write_bytes(b"x")
    fresh_asset = tmp_path / "fresh_replacement.png"
    fresh_asset.write_bytes(b"y")
    _write_profiles(tmp_path, monkeypatch, {
        "FS": {"symbol_library": [
            {"key": "still_valid", "asset_path": str(valid_asset)},
            {"key": "needs_healing", "asset_path": str(fresh_asset)},
        ]},
    })
    shot_list_path = _write_shot_list(tmp_path, [
        {"symbol_key": "still_valid", "asset_path": str(valid_asset), "treatment": "image"},
        {"symbol_key": "needs_healing", "asset_path": str(tmp_path / "stale.png"), "treatment": "image"},
    ])

    healed = cp.heal_stale_symbol_asset_paths(str(shot_list_path), "FS")

    assert healed == 1
    data = json.loads(shot_list_path.read_text(encoding="utf-8"))
    assert data["beats"][0]["asset_path"] == str(valid_asset), "untouched beat must be byte-identical"
    assert data["beats"][1]["asset_path"] == str(fresh_asset)


def test_healed_path_passes_through_the_g5_safety_gate(tmp_path, monkeypatch):
    """Re-resolution reuses pick_symbol_asset_path() -- confirms the G5
    asset-safety gate still fires on a healed path, not just a fresh one."""
    import asset_safety

    unsafe_asset = tmp_path / "symbol_UNSAFE.png"
    unsafe_asset.write_bytes(b"x")
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    _write_profiles(tmp_path, monkeypatch, {
        "FS": {"symbol_library": [{"key": "bad_symbol", "asset_path": str(unsafe_asset)}]},
    })
    shot_list_path = _write_shot_list(tmp_path, [
        {"symbol_key": "bad_symbol", "asset_path": str(tmp_path / "stale.png"), "treatment": "image"},
    ])
    with pytest.raises(asset_safety.AssetSafetyBlockedError):
        cp.heal_stale_symbol_asset_paths(str(shot_list_path), "FS")
