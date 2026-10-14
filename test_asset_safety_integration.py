"""G5 (Video Generation remediation) -- integration tests: confirms the
content-safety gate (asset_safety.py) is actually WIRED into the real
selection/cache/resume chokepoints, not just correct in isolation (see
test_asset_safety.py for the gate's own unit tests).

Covers the 3 main-repo chokepoints:
  1. domain_creative_profiles.pick_symbol_asset_path() -- symbol_library
     curated-asset path.
  2. asset_generation.get_or_fetch_stock_video() -- Long-form stock-video
     cache (both the cache-HIT resume path and the fresh-fetch write path).
  3. short_batch_runner.process_one_segment() -- Short-form video_ready
     status transition (registry resume path)."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import asset_generation
import asset_safety
import domain_creative_profiles as cp
import short_batch_runner as sbr
from asset_safety import AssetSafetyBlockedError, AssetSafetyStatus


# --- 1. pick_symbol_asset_path() --------------------------------------------


def test_pick_symbol_asset_path_allows_a_clean_safe_asset(tmp_path, monkeypatch):
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    asset = tmp_path / "bat_quai_variant_1.png"
    asset.write_bytes(b"fake png")
    entry = {"key": "test_symbol", "asset_path": str(asset)}

    result = cp.pick_symbol_asset_path(entry)

    assert result == str(asset)


def test_pick_symbol_asset_path_blocks_legacy_marked_asset(tmp_path, monkeypatch):
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    asset = tmp_path / "nam_cam_UNSAFE_DO_NOT_USE.png"
    asset.write_bytes(b"fake png")
    entry = {"key": "phap_luat_can_can_cong_ly", "asset_path": str(asset)}

    with pytest.raises(AssetSafetyBlockedError):
        cp.pick_symbol_asset_path(entry)


def test_pick_symbol_asset_path_blocks_explicitly_unsafe_record(tmp_path, monkeypatch):
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    asset = tmp_path / "clean_name.png"
    asset.write_bytes(b"fake png")
    asset_safety.write_asset_safety_record(asset, AssetSafetyStatus.UNSAFE, "flagged after use", "manual_human_review")
    entry = {"key": "test_symbol", "asset_path": str(asset)}

    with pytest.raises(AssetSafetyBlockedError):
        cp.pick_symbol_asset_path(entry)


# --- 2. asset_generation.get_or_fetch_stock_video() -------------------------


def test_get_or_fetch_stock_video_writes_a_safe_record_on_fresh_fetch(tmp_path, monkeypatch):
    monkeypatch.setattr(asset_generation, "ASSET_CACHE_DIR", tmp_path)
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    monkeypatch.setattr(asset_generation, "VIDEO_TOOL_VENV_PYTHON", tmp_path / "fake_python")
    (tmp_path / "fake_python").write_bytes(b"")  # just needs to exist

    output_path = tmp_path / f"vid_{asset_generation._prompt_hash('nature sunset')}.mp4"

    class FakeResult:
        stdout = json.dumps({"ok": True, "output_path": str(output_path)})
        stderr = ""

    with patch("subprocess.run", return_value=FakeResult()):
        result = asset_generation.get_or_fetch_stock_video("nature sunset")

    assert result == output_path
    record = asset_safety.read_asset_safety_record(output_path)
    assert record is not None
    assert record["status"] == "safe"
    assert record["source"] == "fetched_stock_video_no_content_review"


def test_get_or_fetch_stock_video_raises_immediately_if_freshly_fetched_path_has_legacy_marker(tmp_path, monkeypatch):
    """G5 Codex review round 1 finding #4: before this fix, a fresh fetch
    wrote a 'safe' record and returned WITHOUT ever calling the gate on
    that exact path -- only the NEXT cache-hit (a later run) would have
    caught a legacy-marker filename here. Now the gate fires immediately,
    on the same call that just fetched it."""
    monkeypatch.setattr(asset_generation, "ASSET_CACHE_DIR", tmp_path)
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    monkeypatch.setattr(asset_generation, "VIDEO_TOOL_VENV_PYTHON", tmp_path / "fake_python")
    (tmp_path / "fake_python").write_bytes(b"")

    # fetch_stock.py returning an alternate/renamed path carrying a legacy
    # marker -- not the normal deterministic cache path, but a real
    # downloader is external code this pipeline doesn't fully control.
    output_path = tmp_path / "vid_UNSAFE_weird_output.mp4"

    class FakeResult:
        stdout = json.dumps({"ok": True, "output_path": str(output_path)})
        stderr = ""

    with patch("subprocess.run", return_value=FakeResult()):
        with pytest.raises(AssetSafetyBlockedError):
            asset_generation.get_or_fetch_stock_video("some query")


def test_get_or_fetch_stock_video_does_not_overwrite_a_preexisting_unsafe_record_at_the_fetch_destination(tmp_path, monkeypatch):
    """G5 Codex review round 2 finding #4: round 1's fix only asserted
    AFTER write_asset_safety_record(), which unconditionally OVERWRITES
    whatever sidecar already existed at that exact path -- so a pre-existing
    explicit 'unsafe' record (e.g. left over from a prior flagged asset at
    the same cache destination, or the downloader returning an alternate
    path) would be silently clobbered by the fresh 'safe' write before the
    post-write assert ever saw it. Must now assert BEFORE the write too, so
    the fetch is blocked and the pre-existing unsafe record survives
    untouched."""
    monkeypatch.setattr(asset_generation, "ASSET_CACHE_DIR", tmp_path)
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    monkeypatch.setattr(asset_generation, "VIDEO_TOOL_VENV_PYTHON", tmp_path / "fake_python")
    (tmp_path / "fake_python").write_bytes(b"")

    # Clean filename (no legacy marker) but an EXISTING explicit unsafe
    # record already sitting at this exact path before the fetch.
    output_path = tmp_path / "vid_clean_but_prerecorded_unsafe.mp4"
    asset_safety.write_asset_safety_record(output_path, AssetSafetyStatus.UNSAFE, "flagged previously", "manual_human_review")

    class FakeResult:
        stdout = json.dumps({"ok": True, "output_path": str(output_path)})
        stderr = ""

    with patch("subprocess.run", return_value=FakeResult()):
        with pytest.raises(AssetSafetyBlockedError):
            asset_generation.get_or_fetch_stock_video("some query")

    # The pre-existing unsafe record must have survived, NOT been
    # overwritten by a fresh "safe" write before the check ran.
    record = asset_safety.read_asset_safety_record(output_path)
    assert record["status"] == "unsafe"
    assert record["reason"] == "flagged previously"


def test_get_or_fetch_stock_video_cache_hit_is_gated(tmp_path, monkeypatch):
    """The exact 'resume path' gap flagged by this session's research
    agent: a cache-hit must be re-checked EVERY time, not just at first
    fetch -- a clip flagged unsafe AFTER being cached must not silently
    reappear on the next pipeline run."""
    monkeypatch.setattr(asset_generation, "ASSET_CACHE_DIR", tmp_path)
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")

    query = "prison courtroom generic legal"
    cache_path = tmp_path / f"vid_{asset_generation._prompt_hash(query)}.mp4"
    cache_path.write_bytes(b"fake cached clip")
    asset_safety.write_asset_safety_record(
        cache_path, AssetSafetyStatus.UNSAFE, "flagged by human after review", "manual_human_review",
    )

    with pytest.raises(AssetSafetyBlockedError):
        asset_generation.get_or_fetch_stock_video(query)


def test_get_or_fetch_stock_video_cache_hit_allowed_when_safe(tmp_path, monkeypatch):
    monkeypatch.setattr(asset_generation, "ASSET_CACHE_DIR", tmp_path)
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    query = "quiet nature sunset"
    cache_path = tmp_path / f"vid_{asset_generation._prompt_hash(query)}.mp4"
    cache_path.write_bytes(b"fake cached clip")

    result = asset_generation.get_or_fetch_stock_video(query)

    assert result == cache_path


# --- 3. short_batch_runner.process_one_segment() video_ready gate ----------


def _base_segment(key="EP001_00", episode="EP001"):
    return {"key": key, "episode": episode, "segment_index": 0, "text": "câu test", "start": 0.0, "end": 5.0}


def _audio_ready_entry(key):
    return {
        "key": key, "episode": "EP001", "segment_index": 0, "status": "audio_ready",
        "final_script": "câu test", "hook_score": 90, "needs_human_review_hook": False,
    }


def test_video_ready_transition_blocked_when_output_dir_has_legacy_unsafe_file(tmp_path, monkeypatch):
    """Reproduces the exact real incident shape: a stray sibling file in
    the segment's output directory carries a legacy unsafe marker (even
    though the REGISTRY's own video_path points to the normally-named
    file) -- the pipeline must refuse to advance to video_ready/SEO/upload
    until a human clears it, not silently continue past a flagged sibling."""
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    key = "EP001_00"
    seg = _base_segment(key)
    out_dir = tmp_path / "out"
    seg_dir = out_dir / seg["episode"]
    seg_dir.mkdir(parents=True)

    # The "real" (normally-named) output the pipeline is about to write --
    # doesn't exist yet (render hasn't happened), matching a fresh run.
    # A stray, manually-flagged sibling from a PRIOR human review sits here.
    stray_unsafe = seg_dir / "01_short_render_v3_UNSAFE_broll_DO_NOT_USE.mp4"
    stray_unsafe.write_bytes(b"a bad clip a human already flagged")

    registry = {key: _audio_ready_entry(key)}

    def fake_run_video_render(*args, **kwargs):
        # Simulate a successful render -- writes the STANDARD-named output
        # (the file the registry will actually track), but does NOT touch
        # the stray sibling above.
        (seg_dir / f"{seg['segment_index']:02d}_short_render.mp4").write_bytes(b"a fresh, legitimately fine render")
        return {"ok": True}

    monkeypatch.setattr(sbr, "run_video_render", fake_run_video_render)
    monkeypatch.setattr(sbr, "run_tts", lambda *a, **kw: {"ok": True})
    monkeypatch.setattr(sbr.bgm_tracks, "pick_bgm_for_topic", lambda topic: None)
    monkeypatch.setattr(sbr, "load_registry", lambda topic: registry)
    monkeypatch.setattr(sbr, "save_registry", lambda reg, topic: None)
    monkeypatch.setattr(sbr, "save_registry_entry", lambda key, entry, topic: None)

    result = sbr.process_one_segment(
        seg, out_dir, credentials_path="fake", time_slots=[], registry=registry,
        playlist_title=None, hook_pass_threshold=80, dry_run=True,
    )

    assert result["status"] == "needs_review"
    assert "needs_human_review_asset_safety" in result
    assert "UNSAFE" in result["needs_human_review_asset_safety"] or "unsafe" in result["needs_human_review_asset_safety"].lower()


def test_render_step_scan_catches_stray_unsafe_file_on_every_retry_not_just_first(tmp_path, monkeypatch):
    """G5 Codex review round 1 finding #1 (real bug): scan_for_legacy_
    unsafe_assets() used to OMIT already-flagged files from its return
    value on a LATER scan of the same directory (its own idempotence check
    treated 'don't rewrite the sidecar' as 'don't report it either') --
    short_batch_runner.py's gate only blocks when that list is non-empty,
    so a stray unsafe sibling flagged on run 1 stopped blocking on any
    later re-scan, e.g. after resetting the entry back to audio_ready and
    retrying. Reproduces exactly that: run 1 finds+flags+blocks; entry is
    reset to audio_ready (simulating a retry); run 2 must ALSO block."""
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    key = "EP001_00"
    seg = _base_segment(key)
    out_dir = tmp_path / "out"
    seg_dir = out_dir / seg["episode"]
    seg_dir.mkdir(parents=True)

    stray_unsafe = seg_dir / "01_short_render_v3_UNSAFE_broll_DO_NOT_USE.mp4"
    stray_unsafe.write_bytes(b"a bad clip a human already flagged")

    registry = {key: _audio_ready_entry(key)}

    def fake_run_video_render(*args, **kwargs):
        (seg_dir / f"{seg['segment_index']:02d}_short_render.mp4").write_bytes(b"a fresh, legitimately fine render")
        return {"ok": True}

    monkeypatch.setattr(sbr, "run_video_render", fake_run_video_render)
    monkeypatch.setattr(sbr, "run_tts", lambda *a, **kw: {"ok": True})
    monkeypatch.setattr(sbr.bgm_tracks, "pick_bgm_for_topic", lambda topic: None)
    monkeypatch.setattr(sbr, "load_registry", lambda topic: registry)
    monkeypatch.setattr(sbr, "save_registry", lambda reg, topic: None)
    monkeypatch.setattr(sbr, "save_registry_entry", lambda key, entry, topic: None)

    # Run 1: must block -- this session's own scan writes the sidecar record
    # for the stray file for the first time.
    result1 = sbr.process_one_segment(
        seg, out_dir, credentials_path="fake", time_slots=[], registry=registry,
        playlist_title=None, hook_pass_threshold=80, dry_run=True,
    )
    assert result1["status"] == "needs_review"

    # Simulate a retry: reset the SAME entry back to audio_ready (registry
    # is the live dict process_one_segment mutates in place).
    registry[key] = _audio_ready_entry(key)

    # Run 2: the stray file's sidecar record ALREADY exists from run 1 --
    # must STILL block, not silently advance to video_ready just because
    # the record already exists and won't be rewritten.
    result2 = sbr.process_one_segment(
        seg, out_dir, credentials_path="fake", time_slots=[], registry=registry,
        playlist_title=None, hook_pass_threshold=80, dry_run=True,
    )
    assert result2["status"] == "needs_review", (
        "the stray unsafe sibling must still block on a SECOND scan even though its sidecar "
        "record was already written by the first scan (Codex review round 1 finding #1)"
    )


def test_video_ready_resume_is_blocked_when_output_dir_has_legacy_unsafe_file(tmp_path, monkeypatch):
    """G5 Codex review round 1 finding #2 (real bug): the content-safety
    scan previously only ran inline with the RENDER step itself
    (status=='audio_ready'). An entry resumed straight into
    status='video_ready' (e.g. a registry snapshot from a prior run) used
    to skip straight to SEO with NO re-scan, even if a human renamed/added
    an unsafe sibling file into seg_dir, or the tracked video itself picked
    up an explicit unsafe record, AFTER that prior run completed."""
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    key = "EP001_00"
    seg = _base_segment(key)
    out_dir = tmp_path / "out"
    seg_dir = out_dir / seg["episode"]
    seg_dir.mkdir(parents=True)

    video_path = seg_dir / f"{seg['segment_index']:02d}_short_render.mp4"
    video_path.write_bytes(b"a previously-rendered, clean video")
    stray_unsafe = seg_dir / "01_short_render_v3_UNSAFE_broll_DO_NOT_USE.mp4"
    stray_unsafe.write_bytes(b"a bad clip that appeared AFTER the prior run's video_ready transition")

    entry = {
        "key": key, "episode": "EP001", "segment_index": 0, "status": "video_ready",
        "final_script": "câu test", "video_path": str(video_path),
        "hook_score": 90, "needs_human_review_hook": False,
    }
    registry = {key: entry}

    seo_mock = MagicMock(side_effect=AssertionError("SEO must not run once the content-safety gate blocks a resumed video_ready entry"))
    monkeypatch.setattr(sbr, "generate_short_seo_with_review", seo_mock)
    monkeypatch.setattr(sbr, "load_registry", lambda topic: registry)
    monkeypatch.setattr(sbr, "save_registry", lambda reg, topic: None)
    monkeypatch.setattr(sbr, "save_registry_entry", lambda key, entry, topic: None)

    result = sbr.process_one_segment(
        seg, out_dir, credentials_path="fake", time_slots=[], registry=registry,
        playlist_title=None, hook_pass_threshold=80, dry_run=True,
    )

    assert result["status"] == "needs_review"
    assert "needs_human_review_asset_safety" in result
    seo_mock.assert_not_called()


def test_seo_ready_resume_is_blocked_when_output_dir_has_legacy_unsafe_file(tmp_path, monkeypatch):
    """Same finding #2, one step later: an entry resumed straight into
    status='seo_ready' must not reach the truly irreversible upload step
    without a fresh content-safety re-check either."""
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    key = "EP001_00"
    seg = _base_segment(key)
    out_dir = tmp_path / "out"
    seg_dir = out_dir / seg["episode"]
    seg_dir.mkdir(parents=True)

    video_path = seg_dir / f"{seg['segment_index']:02d}_short_render.mp4"
    video_path.write_bytes(b"a previously-rendered, clean video")
    stray_unsafe = seg_dir / "01_short_render_v3_UNSAFE_broll_DO_NOT_USE.mp4"
    stray_unsafe.write_bytes(b"a bad clip that appeared AFTER SEO already ran in a prior run")

    entry = {
        "key": key, "episode": "EP001", "segment_index": 0, "status": "seo_ready",
        "final_script": "câu test", "video_path": str(video_path),
        "hook_score": 90, "needs_human_review_hook": False, "needs_human_review_seo": False,
        "seo": {"title": "t", "description": "d"},
    }
    registry = {key: entry}

    monkeypatch.setattr(sbr, "load_registry", lambda topic: registry)
    monkeypatch.setattr(sbr, "save_registry", lambda reg, topic: None)
    monkeypatch.setattr(sbr, "save_registry_entry", lambda key, entry, topic: None)

    result = sbr.process_one_segment(
        seg, out_dir, credentials_path="fake", time_slots=[], registry=registry,
        playlist_title=None, hook_pass_threshold=80, dry_run=True,
    )

    assert result["status"] == "needs_review"
    assert "needs_human_review_asset_safety" in result


def test_video_ready_transition_proceeds_normally_when_output_dir_is_clean(tmp_path, monkeypatch):
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    key = "EP001_00"
    seg = _base_segment(key)
    out_dir = tmp_path / "out"
    seg_dir = out_dir / seg["episode"]
    seg_dir.mkdir(parents=True)

    registry = {key: _audio_ready_entry(key)}

    def fake_run_video_render(*args, **kwargs):
        (seg_dir / f"{seg['segment_index']:02d}_short_render.mp4").write_bytes(b"fine render")
        return {"ok": True}

    monkeypatch.setattr(sbr, "run_video_render", fake_run_video_render)
    monkeypatch.setattr(sbr, "run_tts", lambda *a, **kw: {"ok": True})
    monkeypatch.setattr(sbr.bgm_tracks, "pick_bgm_for_topic", lambda topic: None)
    monkeypatch.setattr(sbr, "load_registry", lambda topic: registry)
    monkeypatch.setattr(sbr, "save_registry", lambda reg, topic: None)
    monkeypatch.setattr(sbr, "save_registry_entry", lambda key, entry, topic: None)
    # Stop right after video_ready -- don't exercise SEO/upload in this test.
    monkeypatch.setattr(sbr, "generate_short_seo_with_review", lambda *a, **kw: (_ for _ in ()).throw(SystemExit("stop after video_ready for this test")))

    with pytest.raises(SystemExit):
        sbr.process_one_segment(
            seg, out_dir, credentials_path="fake", time_slots=[], registry=registry,
            playlist_title=None, hook_pass_threshold=80, dry_run=True,
        )

    assert registry[key]["status"] == "video_ready"
