"""G5 (Video Generation remediation) -- tests for asset_safety.py, the
content-safety asset gate that replaces filename/manual-only safety
handling.

Includes a REAL regression test against the actual incident file found by
the audit (output/shorts/Hình Sự/LUATHS_AnTreo/
01_short_render_v3_UNSAFE_broll_DO_NOT_USE.mp4) -- read-only, never
modifies/moves/deletes it, only confirms the scan detects it and the gate
blocks it (this session already ran scan_for_legacy_unsafe_assets('output')
once for real, which is how that file first got its sidecar record -- see
G5_PATCH_SUMMARY.md)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import asset_safety
from asset_safety import AssetSafetyBlockedError, AssetSafetyStatus


# --- detect_legacy_unsafe_filename() ----------------------------------------


@pytest.mark.parametrize("filename", [
    "01_short_render_v3_UNSAFE_broll_DO_NOT_USE.mp4",
    "clip_DO_NOT_USE.mp4",
    "broll_not_safe_v2.mp4",
    "unsafe.mp4",  # case-insensitive
])
def test_detects_legacy_unsafe_filename_markers(filename):
    assert asset_safety.detect_legacy_unsafe_filename(filename) is not None


@pytest.mark.parametrize("filename", [
    "01_short_render.mp4",
    "img_a1b2c3d4e5f6.jpg",
    "vid_deadbeef00112233.mp4",
    "bat_quai_variant_2.png",
])
def test_does_not_false_positive_on_normal_filenames(filename):
    assert asset_safety.detect_legacy_unsafe_filename(filename) is None


def test_marker_detection_is_case_insensitive_and_returns_the_matched_marker():
    assert asset_safety.detect_legacy_unsafe_filename("clip_unsafe_v2.mp4") == "UNSAFE"
    assert asset_safety.detect_legacy_unsafe_filename("clip_Do_Not_Use.mp4") == "DO_NOT_USE"


# --- sidecar record read/write ----------------------------------------------


def test_write_then_read_round_trips(tmp_path, monkeypatch):
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    asset_path = tmp_path / "clip.mp4"
    asset_path.write_bytes(b"fake")

    asset_safety.write_asset_safety_record(asset_path, AssetSafetyStatus.UNSAFE, "test reason", "test_source")
    record = asset_safety.read_asset_safety_record(asset_path)

    assert record["status"] == "unsafe"
    assert record["reason"] == "test reason"
    assert record["source"] == "test_source"
    assert "written_at" in record


def test_read_returns_none_when_no_record_exists(tmp_path):
    assert asset_safety.read_asset_safety_record(tmp_path / "no_record.mp4") is None


def test_sidecar_path_is_colocated_next_to_the_asset(tmp_path):
    asset_path = tmp_path / "sub" / "clip.mp4"
    expected = tmp_path / "sub" / "clip.mp4.safety.json"
    assert asset_safety.safety_record_path(asset_path) == expected


def test_read_tolerates_corrupt_sidecar_json(tmp_path):
    asset_path = tmp_path / "clip.mp4"
    asset_safety.safety_record_path(asset_path).write_text("{not valid json", encoding="utf-8")
    assert asset_safety.read_asset_safety_record(asset_path) is None


def test_write_appends_audit_log_entry(tmp_path, monkeypatch):
    log_path = tmp_path / "audit.log"
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", log_path)
    asset_path = tmp_path / "clip.mp4"

    asset_safety.write_asset_safety_record(asset_path, AssetSafetyStatus.SAFE, "ok", "test_source")

    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["event"] == "record_written"
    assert entry["status"] == "safe"
    assert entry["asset_path"] == str(asset_path)
    assert "logged_at" in entry


# --- assert_asset_safe_for_assembly() -- the gate ---------------------------


def test_gate_allows_asset_with_no_record_and_clean_filename(tmp_path):
    asset_path = tmp_path / "clip.mp4"
    asset_safety.assert_asset_safe_for_assembly(asset_path)  # must not raise


def test_gate_allows_asset_with_explicit_safe_record(tmp_path, monkeypatch):
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    asset_path = tmp_path / "clip.mp4"
    asset_safety.write_asset_safety_record(asset_path, AssetSafetyStatus.SAFE, "reviewed", "manual_human_review")
    asset_safety.assert_asset_safe_for_assembly(asset_path)  # must not raise


def test_gate_blocks_legacy_unsafe_filename_even_with_no_record(tmp_path, monkeypatch):
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    asset_path = tmp_path / "clip_UNSAFE_broll_DO_NOT_USE.mp4"
    with pytest.raises(AssetSafetyBlockedError, match="UNSAFE"):
        asset_safety.assert_asset_safe_for_assembly(asset_path)


def test_gate_blocks_explicit_unsafe_record(tmp_path, monkeypatch):
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    asset_path = tmp_path / "clip.mp4"  # clean filename, no legacy marker
    asset_safety.write_asset_safety_record(asset_path, AssetSafetyStatus.UNSAFE, "human flagged it", "manual_human_review")
    with pytest.raises(AssetSafetyBlockedError, match="unsafe"):
        asset_safety.assert_asset_safe_for_assembly(asset_path)


def test_gate_blocks_explicit_review_required_record(tmp_path, monkeypatch):
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    asset_path = tmp_path / "clip.mp4"
    asset_safety.write_asset_safety_record(asset_path, AssetSafetyStatus.REVIEW_REQUIRED, "unsure", "manual_human_review")
    with pytest.raises(AssetSafetyBlockedError, match="review_required"):
        asset_safety.assert_asset_safe_for_assembly(asset_path)


def test_legacy_filename_marker_wins_even_over_an_explicit_safe_record(tmp_path, monkeypatch):
    """A stale 'safe' record can't be used to silently launder a file whose
    NAME still carries the manual unsafe marker -- the marker always wins
    (the human must rename the file to clear it, not just edit a record)."""
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    asset_path = tmp_path / "clip_UNSAFE.mp4"
    asset_safety.write_asset_safety_record(asset_path, AssetSafetyStatus.SAFE, "trying to launder", "manual_human_review")
    with pytest.raises(AssetSafetyBlockedError, match="UNSAFE"):
        asset_safety.assert_asset_safe_for_assembly(asset_path)


def test_gate_blocks_unparseable_corrupt_sidecar_json(tmp_path, monkeypatch):
    """G5 Codex review round 1 finding #3: a sidecar record file that
    EXISTS but is unparseable (truncated write, merge conflict...) must
    fail CLOSED like an explicit unsafe record -- NOT be silently treated
    the same as 'no record at all' (which read_asset_safety_record()'s own
    tolerant behavior would otherwise cause, see that function's docstring
    for why it stays lenient for OTHER callers)."""
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    asset_path = tmp_path / "clean_name.mp4"  # no legacy filename marker
    asset_safety.safety_record_path(asset_path).write_text("{not valid json", encoding="utf-8")
    with pytest.raises(asset_safety.AssetSafetyRecordCorruptError):
        asset_safety.assert_asset_safe_for_assembly(asset_path)
    # subclass of AssetSafetyBlockedError -- existing callers still catch it
    asset_safety.safety_record_path(asset_path).write_text("{not valid json", encoding="utf-8")
    with pytest.raises(AssetSafetyBlockedError):
        asset_safety.assert_asset_safe_for_assembly(asset_path)


def test_gate_blocks_sidecar_with_unrecognized_status_value(tmp_path, monkeypatch):
    """Same finding #3 -- a sidecar record that parses as valid JSON but
    whose `status` field isn't one of the 3 recognized values (schema
    drift, typo) must also fail closed, not be silently treated as safe."""
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    asset_path = tmp_path / "clean_name2.mp4"
    asset_safety.safety_record_path(asset_path).write_text(
        json.dumps({"status": "review-required", "reason": "typo'd status"}), encoding="utf-8",
    )
    with pytest.raises(asset_safety.AssetSafetyRecordCorruptError):
        asset_safety.assert_asset_safe_for_assembly(asset_path)


def test_gate_still_allows_asset_with_no_sidecar_file_at_all(tmp_path, monkeypatch):
    """Sanity control for finding #3's fix: a TRULY absent sidecar (no
    `.safety.json` file at all) is still allowed -- only an EXISTING but
    corrupt/invalid record fails closed, per the module's documented
    compatibility policy for the overwhelming majority of pre-gate assets."""
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    asset_safety.assert_asset_safe_for_assembly(tmp_path / "no_sidecar_at_all.mp4")  # must not raise


def test_read_asset_safety_record_stays_tolerant_for_other_callers(tmp_path):
    """read_asset_safety_record() itself (used by scan_for_legacy_unsafe_
    assets()'s self-healing rewrite check) must keep its ORIGINAL tolerant
    contract -- returns None for corrupt JSON, does not raise. Only the
    gate (assert_asset_safe_for_assembly, via the private strict helper)
    changed behavior."""
    asset_path = tmp_path / "clip.mp4"
    asset_safety.safety_record_path(asset_path).write_text("{not valid json", encoding="utf-8")
    assert asset_safety.read_asset_safety_record(asset_path) is None


def test_gate_blocks_both_events_are_audit_logged(tmp_path, monkeypatch):
    log_path = tmp_path / "audit.log"
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", log_path)

    with pytest.raises(AssetSafetyBlockedError):
        asset_safety.assert_asset_safe_for_assembly(tmp_path / "x_UNSAFE.mp4")

    asset_path2 = tmp_path / "clean.mp4"
    asset_safety.write_asset_safety_record(asset_path2, AssetSafetyStatus.UNSAFE, "r", "s")
    with pytest.raises(AssetSafetyBlockedError):
        asset_safety.assert_asset_safe_for_assembly(asset_path2)

    events = [json.loads(l)["event"] for l in log_path.read_text(encoding="utf-8").strip().splitlines()]
    assert "blocked_legacy_filename_marker" in events
    assert "blocked_explicit_record" in events


# --- scan_for_legacy_unsafe_assets() -----------------------------------------


def test_scan_flags_matching_files_and_writes_unsafe_records(tmp_path, monkeypatch):
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    bad = tmp_path / "sub" / "01_render_v3_UNSAFE_broll_DO_NOT_USE.mp4"
    bad.parent.mkdir(parents=True)
    bad.write_bytes(b"fake")
    good = tmp_path / "sub" / "01_render.mp4"
    good.write_bytes(b"fake")

    flagged = asset_safety.scan_for_legacy_unsafe_assets(tmp_path)

    assert flagged == [bad]
    record = asset_safety.read_asset_safety_record(bad)
    assert record["status"] == "unsafe"
    assert record["source"] == "legacy_filename_scan"
    assert asset_safety.read_asset_safety_record(good) is None


def test_scan_is_idempotent_does_not_rewrite_already_flagged_files(tmp_path, monkeypatch):
    """G5 Codex review round 1 finding #1: 'idempotent' means the sidecar
    record is not REWRITTEN on a later scan (written_at stays identical) --
    it does NOT mean the already-flagged file disappears from the returned
    list. The caller (short_batch_runner.py) relies on this list being
    non-empty on EVERY scan of a directory that still contains a
    legacy-marked file, not just the first one that wrote its sidecar."""
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    bad = tmp_path / "clip_UNSAFE.mp4"
    bad.write_bytes(b"fake")

    first = asset_safety.scan_for_legacy_unsafe_assets(tmp_path)
    written_at_1 = asset_safety.read_asset_safety_record(bad)["written_at"]
    second = asset_safety.scan_for_legacy_unsafe_assets(tmp_path)
    written_at_2 = asset_safety.read_asset_safety_record(bad)["written_at"]

    assert first == [bad]
    assert second == [bad], "already-flagged file must still be REPORTED on a later scan, just not re-written"
    assert written_at_1 == written_at_2, "already-flagged file's sidecar record must not be rewritten (written_at unchanged)"


def test_scan_never_flags_or_deletes_the_asset_itself_only_writes_sidecar(tmp_path, monkeypatch):
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    bad = tmp_path / "clip_UNSAFE.mp4"
    original_bytes = b"original video bytes, must survive untouched"
    bad.write_bytes(original_bytes)

    asset_safety.scan_for_legacy_unsafe_assets(tmp_path)

    assert bad.read_bytes() == original_bytes, "scan must be purely additive -- never touch the flagged asset's own content"
    assert bad.is_file()


def test_scan_does_not_recurse_into_its_own_sidecar_files(tmp_path, monkeypatch):
    """Updated for the finding #1 fix: the second scan now legitimately
    still REPORTS `bad` (already-flagged files are reported on every scan,
    not omitted -- see test_scan_is_idempotent_does_not_rewrite_already_
    flagged_files). What this test actually guards against is narrower:
    the sidecar file `clip_UNSAFE.mp4.safety.json` itself must never be
    treated as a NEW asset needing its own recursive
    `.safety.json.safety.json` sidecar."""
    monkeypatch.setattr(asset_safety, "AUDIT_LOG_PATH", tmp_path / "audit.log")
    bad = tmp_path / "clip_UNSAFE.mp4"
    bad.write_bytes(b"fake")
    asset_safety.scan_for_legacy_unsafe_assets(tmp_path)
    flagged_again = asset_safety.scan_for_legacy_unsafe_assets(tmp_path)
    assert flagged_again == [bad], "the original asset must still be reported (not the sidecar file itself)"
    assert not (tmp_path / "clip_UNSAFE.mp4.safety.json.safety.json").exists()


# --- real production incident regression (read-only) ------------------------


REAL_INCIDENT_FILE = (
    Path(__file__).parent / "output" / "shorts" / "Hình Sự" / "LUATHS_AnTreo"
    / "01_short_render_v3_UNSAFE_broll_DO_NOT_USE.mp4"
)


def test_real_incident_file_is_detected_as_legacy_unsafe():
    """The exact real file the G5 audit finding is about -- confirms the
    detection logic actually matches production reality, not just a
    synthetic tmp_path example. Read-only: only calls the pure detection
    function, never writes/moves/deletes anything."""
    if not REAL_INCIDENT_FILE.exists():
        pytest.skip(f"real incident fixture not present: {REAL_INCIDENT_FILE}")
    assert asset_safety.detect_legacy_unsafe_filename(REAL_INCIDENT_FILE) == "UNSAFE"


def test_real_incident_file_is_blocked_by_the_gate():
    """This session's own scan_for_legacy_unsafe_assets('output') run
    already wrote a real 'unsafe' sidecar record for this exact file (see
    G5_PATCH_SUMMARY.md) -- confirms the gate function blocks it end to
    end, using the REAL sidecar record now sitting on disk, not a mock."""
    if not REAL_INCIDENT_FILE.exists():
        pytest.skip(f"real incident fixture not present: {REAL_INCIDENT_FILE}")
    with pytest.raises(AssetSafetyBlockedError):
        asset_safety.assert_asset_safe_for_assembly(REAL_INCIDENT_FILE)


def test_real_incident_sidecar_record_has_expected_shape():
    if not REAL_INCIDENT_FILE.exists():
        pytest.skip(f"real incident fixture not present: {REAL_INCIDENT_FILE}")
    record = asset_safety.read_asset_safety_record(REAL_INCIDENT_FILE)
    assert record is not None, "expected a sidecar record from this session's scan run"
    assert record["status"] == "unsafe"
    assert record["source"] == "legacy_filename_scan"
