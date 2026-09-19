"""P1 (E2E validation remediation) -- tests for the Director Bible cache
cross-channel collision fix.

BUG THẬT phát hiện qua full E2E validation (2026-08-07): cache key cũ chỉ
là `{episode_id}.json` (không có domain/channel) -- 3 kênh đều đánh số tập
riêng từ EP001, nên `build_director_bible("EP001", ...)` cho kênh CL âm
thầm trả về bible ĐÃ CACHE của kênh BUD (Địa Tạng/Phật giáo), làm ô nhiễm
mọi prompt sinh ảnh AI mới của CL bằng hình ảnh chùa/tượng Phật -- lỗi này
từng bị CHE GIẤU bởi bug G3 (0 beat IMAGE tự do trước khi G3 fix, nên
không có prompt nào để ô nhiễm), sẽ LỘ RA ngay khi G3 hoạt động đúng.

Fix: cache key giờ namespace theo domain_id ĐÃ RESOLVE (không phải arg thô
có thể None) + version format cache -- xem director_bible.py docstring."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

import director_bible
import domain_creative_profiles as cp


def _isolated_cache_dir(tmp_path, monkeypatch):
    cache_dir = tmp_path / "director_bibles"
    monkeypatch.setattr(director_bible, "DIRECTOR_BIBLE_CACHE_DIR", cache_dir)
    monkeypatch.setattr(director_bible, "_LEGACY_AMBIGUOUS_DIR", cache_dir / "_legacy_ambiguous_pre_namespace")
    return cache_dir


def _fake_bible(marker: str) -> dict:
    return {
        "creative_vision": f"marker={marker}",
        "emotion_curve": [], "color_palette": {}, "camera_language": {},
        "editing_rhythm": {}, "typography_policy": {},
        "image_policy": {"favor_subjects": [marker], "avoid_subjects": []},
        "ai_video_policy": {}, "pexels_acceptance_policy": {},
        "transition_style": {}, "consistency_rules": [],
    }


# --- resolve_domain_id() -----------------------------------------------------


def test_resolve_domain_id_none_falls_back_to_default():
    assert cp.resolve_domain_id(None) == cp.DEFAULT_DOMAIN_ID == "BUD"


def test_resolve_domain_id_known_domain_returns_itself():
    assert cp.resolve_domain_id("CL") == "CL"
    assert cp.resolve_domain_id("FS") == "FS"


def test_resolve_domain_id_unknown_domain_falls_back_to_default(capsys):
    assert cp.resolve_domain_id("NOT_A_REAL_DOMAIN") == "BUD"


# --- cache_filename() namespacing --------------------------------------------


def test_cache_filename_differs_by_domain_for_the_same_episode():
    names = {director_bible.cache_filename(d, "EP001") for d in ("BUD", "FS", "CL")}
    assert len(names) == 3, "all 3 channels must get distinct cache filenames for the same episode_id"


def test_cache_filename_includes_version_suffix():
    name = director_bible.cache_filename("BUD", "EP001")
    assert name.endswith(f"_{director_bible._BIBLE_CACHE_VERSION}.json")


# --- build_director_bible(): the actual collision fix, cache-hit path -------


def test_bud_and_cl_get_independent_cached_bibles_for_the_same_episode_id(tmp_path, monkeypatch):
    """The core regression test: pre-seed BOTH BUD's and CL's cache entries
    for episode_id="EP001" with distinct, known content -- confirm each
    domain's build_director_bible() call returns ONLY its own, never the
    other's, and never triggers a live generation call (which would mean
    the cache wasn't actually hit)."""
    cache_dir = _isolated_cache_dir(tmp_path, monkeypatch)
    cache_dir.mkdir(parents=True)

    bud_bible = _fake_bible("BUD-real-content")
    cl_bible = _fake_bible("CL-real-content")
    (cache_dir / director_bible.cache_filename("BUD", "EP001")).write_text(json.dumps(bud_bible), encoding="utf-8")
    (cache_dir / director_bible.cache_filename("CL", "EP001")).write_text(json.dumps(cl_bible), encoding="utf-8")

    with patch.object(director_bible, "_call_gemini_api", side_effect=AssertionError("must not regenerate -- cache should hit")), \
         patch.object(director_bible, "_call_agy", side_effect=AssertionError("must not regenerate -- cache should hit")):
        result_bud = director_bible.build_director_bible("EP001", domain_id="BUD")
        result_cl = director_bible.build_director_bible("EP001", domain_id="CL")

    assert result_bud["creative_vision"] == "marker=BUD-real-content"
    assert result_cl["creative_vision"] == "marker=CL-real-content"
    assert result_bud != result_cl, "BUD and CL must never resolve to the same bible for the same episode_id"


def test_new_domain_scoped_lookup_does_not_see_a_legacy_bare_named_entry(tmp_path, monkeypatch):
    """Reproduces the ACTUAL bug shape: an old bare `{episode_id}.json`
    file (simulating BUD's real pre-fix cache, exact content captured from
    a real reproduction run of this bug -- see
    scratchpad/e2e_remediation/p1/REPRODUCTION_before_fix.json) sits in the
    cache dir. A fresh CL lookup for the same episode_id must NOT find it
    (must fall through to generation, not silently inherit it)."""
    cache_dir = _isolated_cache_dir(tmp_path, monkeypatch)
    cache_dir.mkdir(parents=True)

    legacy_bare_path = cache_dir / "EP001.json"
    legacy_bare_path.write_text(json.dumps(_fake_bible("LEGACY-BUD-bare-name-EP001")), encoding="utf-8")

    generated = _fake_bible("freshly-generated-for-CL")
    with patch.object(director_bible, "_call_gemini_api", return_value=None), \
         patch.object(director_bible, "_call_agy", return_value=generated) as mock_agy:
        result = director_bible.build_director_bible("EP001", domain_id="CL", gemini_api_key=None)

    assert mock_agy.called, "must have fallen through to a real generation attempt, not a silent cache hit on the legacy file"
    assert result["creative_vision"] == "marker=freshly-generated-for-CL"
    assert result["image_policy"]["favor_subjects"] != ["LEGACY-BUD-bare-name-EP001"]
    # The legacy file itself must be left untouched (not deleted/modified by a lookup miss).
    assert legacy_bare_path.is_file()
    assert json.loads(legacy_bare_path.read_text(encoding="utf-8"))["creative_vision"] == "marker=LEGACY-BUD-bare-name-EP001"


def test_real_captured_contamination_fixture_is_no_longer_reachable(tmp_path, monkeypatch):
    """Uses the EXACT real bible content captured live from this repo
    before the fix (a genuine reproduction of the bug, not a synthetic
    example) as the legacy bare-named cache entry, and confirms a fresh
    CL lookup no longer resolves to it."""
    fixture_path = Path(__file__).parent / "test_fixtures_director_bible_before_fix.json"
    if not fixture_path.exists():
        pytest.skip(f"real reproduction fixture not present: {fixture_path}")
    real_contaminated_bible = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert "Địa Tạng" in real_contaminated_bible["image_policy"]["favor_subjects"][0], (
        "sanity check on the fixture itself -- must contain the real captured Buddhist-imagery contamination"
    )

    cache_dir = _isolated_cache_dir(tmp_path, monkeypatch)
    cache_dir.mkdir(parents=True)
    (cache_dir / "EP001.json").write_text(json.dumps(real_contaminated_bible, ensure_ascii=False), encoding="utf-8")

    generated = _fake_bible("fresh-CL-bible")
    with patch.object(director_bible, "_call_gemini_api", return_value=None), \
         patch.object(director_bible, "_call_agy", return_value=generated):
        result = director_bible.build_director_bible("EP001", domain_id="CL", gemini_api_key=None)

    assert "Địa Tạng" not in json.dumps(result, ensure_ascii=False), (
        "the real captured Buddhist-imagery contamination must never reach a fresh CL build_director_bible() call"
    )


def test_force_refresh_still_works_per_domain(tmp_path, monkeypatch):
    cache_dir = _isolated_cache_dir(tmp_path, monkeypatch)
    cache_dir.mkdir(parents=True)
    (cache_dir / director_bible.cache_filename("BUD", "EP001")).write_text(
        json.dumps(_fake_bible("stale")), encoding="utf-8",
    )
    fresh = _fake_bible("refreshed")
    with patch.object(director_bible, "_call_gemini_api", return_value=None), \
         patch.object(director_bible, "_call_agy", return_value=fresh):
        result = director_bible.build_director_bible("EP001", domain_id="BUD", force_refresh=True, gemini_api_key=None)
    assert result["creative_vision"] == "marker=refreshed"


# --- migrate_legacy_ambiguous_cache() ----------------------------------------


def test_migrate_moves_only_legacy_bare_named_files_not_new_format(tmp_path, monkeypatch):
    cache_dir = _isolated_cache_dir(tmp_path, monkeypatch)
    cache_dir.mkdir(parents=True)
    legacy = cache_dir / "EP001.json"
    legacy.write_text(json.dumps(_fake_bible("legacy")), encoding="utf-8")
    new_format = cache_dir / director_bible.cache_filename("BUD", "EP004")
    new_format.write_text(json.dumps(_fake_bible("new")), encoding="utf-8")

    moved = director_bible.migrate_legacy_ambiguous_cache()

    assert len(moved) == 1
    assert not legacy.exists()
    assert new_format.exists(), "new-format cache file must NOT be migrated/touched"
    quarantined = director_bible._LEGACY_AMBIGUOUS_DIR / "EP001.json"
    assert quarantined.is_file()
    assert json.loads(quarantined.read_text(encoding="utf-8"))["creative_vision"] == "marker=legacy"


def test_migrate_is_idempotent(tmp_path, monkeypatch):
    cache_dir = _isolated_cache_dir(tmp_path, monkeypatch)
    cache_dir.mkdir(parents=True)
    (cache_dir / "EP001.json").write_text(json.dumps(_fake_bible("legacy")), encoding="utf-8")

    first = director_bible.migrate_legacy_ambiguous_cache()
    second = director_bible.migrate_legacy_ambiguous_cache()

    assert len(first) == 1
    assert len(second) == 0


def test_migrate_never_deletes_content_only_moves_it(tmp_path, monkeypatch):
    cache_dir = _isolated_cache_dir(tmp_path, monkeypatch)
    cache_dir.mkdir(parents=True)
    original_bytes = json.dumps(_fake_bible("preserve-me"), ensure_ascii=False).encode("utf-8")
    (cache_dir / "EP004.json").write_bytes(original_bytes)

    director_bible.migrate_legacy_ambiguous_cache()

    quarantined = director_bible._LEGACY_AMBIGUOUS_DIR / "EP004.json"
    assert quarantined.read_bytes() == original_bytes


def test_migrate_on_empty_or_missing_dir_is_a_safe_noop(tmp_path, monkeypatch):
    monkeypatch.setattr(director_bible, "DIRECTOR_BIBLE_CACHE_DIR", tmp_path / "does_not_exist")
    monkeypatch.setattr(director_bible, "_LEGACY_AMBIGUOUS_DIR", tmp_path / "does_not_exist" / "_legacy")
    assert director_bible.migrate_legacy_ambiguous_cache() == []


# --- creative_director.py call-site wiring -----------------------------------


def test_creative_director_main_resolves_and_passes_domain_id(monkeypatch, tmp_path):
    """Confirms the actual call site (creative_director.py::main()) passes
    a RESOLVED domain_id through to build_director_bible(), not the raw
    (possibly None) --domain arg -- this is the actual fix wiring, not
    just the underlying primitive."""
    import creative_director
    captured = {}

    def fake_build_director_bible(episode_id, *a, **kw):
        captured["domain_id"] = kw.get("domain_id")
        return _fake_bible("x")

    segments = {"segments": [{"start": 0.0, "end": 3.0, "text": "câu test đủ để không lỗi."}]}
    segments_json = tmp_path / "segments.json"
    segments_json.write_text(json.dumps(segments), encoding="utf-8")
    output_path = tmp_path / "shot_list.json"

    monkeypatch.setattr(creative_director.director_bible, "build_director_bible", fake_build_director_bible)
    monkeypatch.setattr(
        "sys.argv",
        ["creative_director.py", "--segments-json", str(segments_json), "--output", str(output_path),
         "--domain", "CL", "--no-gemini", "--episode-id", "EP001"],
    )
    creative_director.main()

    assert captured["domain_id"] == "CL"
