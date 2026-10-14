"""G5 (Video Generation remediation): content-safety asset gate.

Audit finding: a real B-roll clip that a human judged unsafe was "fixed"
purely by renaming the file to
`01_short_render_v3_UNSAFE_broll_DO_NOT_USE.mp4` (see
`output/shorts/Hình Sự/LUATHS_AnTreo/`) -- confirmed via a full-repo grep
that NO code anywhere ever reads that filename convention. It was pure
human note-taking with zero enforcement: nothing would have stopped that
exact file from being picked up by any future glob/reuse/resume path.

This module replaces filename-only, manual-only safety handling with an
explicit, machine-readable safety record (a small `<asset>.safety.json`
sidecar file next to the asset) plus a single fail-closed gate function
that every asset-selection chokepoint in this pipeline calls before an
asset is allowed to enter assembly. Two kinds of protection compose:

  1. Legacy filename markers (UNSAFE/DO_NOT_USE/...) are still detected
     and always block -- kept as a defense-in-depth safety net for exactly
     the incident above (a human's only recourse before this fix existed),
     NOT as the primary mechanism.
  2. An explicit sidecar safety record (status: safe/unsafe/review_required)
     is the primary, durable mechanism -- written by every caller that
     fetches/generates/reuses an asset, and checked before that asset (or a
     later CACHED copy of it) is handed to a beat/scene for assembly.

Scope (deliberately bounded, matches the audit finding): stock B-roll VIDEO
(Pexels/Pixabay -- the audit's actual incident, and the class of asset with
an uncontrolled external catalog) and the symbol_library curated-asset path
(real-person-name/diagram substitutes, already the one safety-critical path
in this codebase). AI-generated IMAGE assets (ComfyUI/Cursor/Codex/agy) are
NOT gated here -- they are freshly generated from a developer-controlled
prompt each beat, not pulled from an external catalog, and were not part of
the audit's finding; gating them is a larger, separately-scoped change, not
attempted in this patch.

Fail-closed here means: an asset carrying an EXPLICIT unsafe/review_required
record, or a legacy-marker filename, is always refused. An asset with NO
record at all (the overwhelming majority of the existing cache, fetched
before this gate existed) is NOT refused -- there is no real content-
moderation signal in this pipeline to justify blocking literally everything
already on disk, and doing so would brick the working pipeline for no
safety benefit (see module docstring above: the actual incident was a
human-flagged file with zero enforcement, not an unclassified-by-default
asset). New fetches/downloads write a default "safe" record at write time
(so every asset from this point forward carries an explicit, audited
record) -- callers with an actual safety signal (a human review, a future
moderation check) should write "unsafe"/"review_required" explicitly via
write_asset_safety_record(), which then takes effect immediately and
persists across cache reuse/resume.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

AUDIT_LOG_PATH = Path(__file__).parent / "chunks_cache" / "asset_safety_audit.log"

LEGACY_UNSAFE_FILENAME_MARKERS = ("UNSAFE", "DO_NOT_USE", "NOT_SAFE")


class AssetSafetyStatus:
    SAFE = "safe"
    UNSAFE = "unsafe"
    REVIEW_REQUIRED = "review_required"


class AssetSafetyBlockedError(RuntimeError):
    """Raised by assert_asset_safe_for_assembly() -- caller must NOT catch
    this and silently fall back to a different asset source without human
    review; that would defeat the entire point of a fail-closed gate (same
    philosophy as domain_creative_profiles.SafetyCriticalAssetMissingError)."""
    pass


class AssetSafetyRecordCorruptError(AssetSafetyBlockedError):
    """Subclass of AssetSafetyBlockedError, raised by
    assert_asset_safe_for_assembly() -- G5 Codex review round 1 finding #3:
    a sidecar `.safety.json` file that EXISTS but can't be parsed (truncated
    write, merge conflict, disk/permissions error) or whose `status` value
    isn't one of the 3 recognized values (typo, schema drift) must fail
    CLOSED, the same as an explicit unsafe record -- it must NOT be silently
    treated the same as "no record at all" (which IS allowed, see module
    docstring). Being a subclass of AssetSafetyBlockedError, every existing
    `except AssetSafetyBlockedError` caller already catches this too,
    nothing else needs to change to pick this up."""
    pass


def detect_legacy_unsafe_filename(asset_path: str | Path) -> str | None:
    """Returns the matched marker (e.g. "UNSAFE") if `asset_path`'s
    filename contains one of LEGACY_UNSAFE_FILENAME_MARKERS
    (case-insensitive), else None."""
    name_upper = Path(asset_path).name.upper()
    for marker in LEGACY_UNSAFE_FILENAME_MARKERS:
        if marker in name_upper:
            return marker
    return None


def safety_record_path(asset_path: str | Path) -> Path:
    return Path(str(asset_path) + ".safety.json")


def _append_audit_log(event: dict) -> None:
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {"logged_at": datetime.now(timezone.utc).isoformat(), **event}
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def write_asset_safety_record(asset_path: str | Path, status: str, reason: str, source: str) -> None:
    """Writes/overwrites the sidecar safety record for `asset_path` and
    appends an audit-log entry. `source` identifies WHAT classified this
    asset (e.g. "legacy_filename_scan", "fetched_pexels_no_content_review",
    "manual_human_review", "symbol_library_curated") -- never omitted, so
    the audit trail always shows provenance, not just the verdict."""
    record = {"status": status, "reason": reason, "source": source, "written_at": datetime.now(timezone.utc).isoformat()}
    safety_record_path(asset_path).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    _append_audit_log({"event": "record_written", "asset_path": str(asset_path), **record})


def read_asset_safety_record(asset_path: str | Path) -> dict | None:
    """Tolerant read: returns None both when no sidecar file exists AND
    when one exists but can't be parsed -- intentionally kept this lenient
    for callers like scan_for_legacy_unsafe_assets() (see there) where
    treating a corrupt existing record the same as "no valid record" is the
    correct, self-healing behavior (it gets rewritten). The GATE itself
    (assert_asset_safe_for_assembly) does NOT use this function for that
    reason -- see _read_asset_safety_record_or_raise_if_corrupt()."""
    path = safety_record_path(asset_path)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


_VALID_STATUS_VALUES = (AssetSafetyStatus.SAFE, AssetSafetyStatus.UNSAFE, AssetSafetyStatus.REVIEW_REQUIRED)


def _read_asset_safety_record_or_raise_if_corrupt(asset_path: str | Path) -> dict | None:
    """G5 Codex review round 1 finding #3: like read_asset_safety_record(),
    but raises AssetSafetyRecordCorruptError instead of silently returning
    None when a sidecar file EXISTS but is unparseable or carries an
    unrecognized `status` value -- used ONLY by the gate
    (assert_asset_safe_for_assembly), which must fail closed on accidental
    corruption (a truncated write, a merge conflict, a permissions error, a
    typo'd status value), not treat it the same as "no record at all"."""
    path = safety_record_path(asset_path)
    if not path.is_file():
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        _append_audit_log({"event": "blocked_corrupt_record", "asset_path": str(asset_path), "error": str(exc)})
        raise AssetSafetyRecordCorruptError(
            f"Asset '{asset_path}' bị CHẶN: sidecar safety record '{path}' TỒN TẠI nhưng KHÔNG đọc/parse "
            f"được ({exc}) -- coi record hỏng NGANG với unsafe (an toàn hơn là im lặng bỏ qua như 'không "
            f"có record'). Kiểm tra/sửa file record, hoặc ghi lại record tường minh (write_asset_safety_record) "
            f"trước khi dùng lại."
        ) from exc
    if not isinstance(record, dict) or record.get("status") not in _VALID_STATUS_VALUES:
        bad_status = record.get("status") if isinstance(record, dict) else record
        _append_audit_log({"event": "blocked_corrupt_record", "asset_path": str(asset_path), "status": bad_status})
        raise AssetSafetyRecordCorruptError(
            f"Asset '{asset_path}' bị CHẶN: sidecar safety record '{path}' có 'status' không hợp lệ/không "
            f"nhận diện được ({bad_status!r}) -- coi record hỏng NGANG với unsafe. Kiểm tra/sửa file record "
            f"trước khi dùng lại."
        )
    return record


def assert_asset_safe_for_assembly(asset_path: str | Path) -> None:
    """THE single fail-closed gate -- call this immediately before handing
    an asset path to a beat/scene for assembly (whether freshly
    fetched/generated or returned from a cache-hit). Raises
    AssetSafetyBlockedError (never returns a value; caller must not swallow
    it) if:
      - the filename matches a legacy unsafe marker (always wins, cannot be
        overridden by a stale "safe" sidecar record -- rename/remove the
        file, or delete the marker from its name, to clear this), or
      - an explicit sidecar record exists with status unsafe/review_required, or
      - a sidecar record file exists but is corrupt/unparseable/has an
        unrecognized status value (AssetSafetyRecordCorruptError, G5 Codex
        review round 1 finding #3 -- fails closed on accidental corruption,
        not just on an explicit unsafe verdict).
    Silently allows (returns None) an asset with a "safe" record, or with
    NO record at all -- see module docstring for why "no record" isn't
    treated as blocked here."""
    marker = detect_legacy_unsafe_filename(asset_path)
    if marker is not None:
        _append_audit_log({"event": "blocked_legacy_filename_marker", "asset_path": str(asset_path), "marker": marker})
        raise AssetSafetyBlockedError(
            f"Asset '{asset_path}' bị CHẶN: tên file chứa dấu hiệu an toàn thủ công '{marker}' -- quy ước "
            f"cũ này PHẢI được tôn trọng, không được bỏ qua (đây chính xác là bug đã xảy ra thật: 1 file "
            f"UNSAFE bị đổi tên nhưng không có gì đọc tên đó). Xem lại nội dung, xoá/thay file nếu thật sự "
            f"không an toàn, hoặc nếu đã xác nhận an toàn thì đổi tên KHÔNG còn chứa '{marker}' và ghi "
            f"safety record 'safe' tường minh (write_asset_safety_record) trước khi dùng lại."
        )

    record = _read_asset_safety_record_or_raise_if_corrupt(asset_path)
    if record is not None and record.get("status") in (AssetSafetyStatus.UNSAFE, AssetSafetyStatus.REVIEW_REQUIRED):
        _append_audit_log({
            "event": "blocked_explicit_record", "asset_path": str(asset_path),
            "status": record.get("status"), "reason": record.get("reason"),
        })
        raise AssetSafetyBlockedError(
            f"Asset '{asset_path}' bị CHẶN: safety record hiện tại là '{record.get('status')}' "
            f"(lý do: {record.get('reason')!r}, nguồn: {record.get('source')!r}) -- không được vào assembly "
            f"tự động. Cần con người xem lại và ghi đè record thành 'safe' tường minh trước khi dùng lại."
        )


def scan_for_legacy_unsafe_assets(root_dir: str | Path) -> list[Path]:
    """Walks `root_dir` for files whose name matches a legacy unsafe
    marker and writes an UNSAFE sidecar record for each one that doesn't
    already have one (idempotent -- safe to re-run: an already-flagged file
    is NOT re-written, its `written_at` stays unchanged). Returns EVERY
    currently legacy-marked path found this call -- newly flagged AND
    already-flagged alike (G5 Codex review round 1 finding #1: an earlier
    version of this function OMITTED already-flagged paths from its return
    value, which meant "idempotent" silently became "invisible to the
    caller on retry" -- short_batch_runner.py's video_ready gate only
    blocks when this list is non-empty, so a stray unsafe sibling flagged
    on run 1 would stop blocking on any LATER re-scan of the same
    directory, e.g. after a manual reset back to audio_ready -- reproducing
    the exact incident class this gate exists to prevent). Idempotence here
    means "don't rewrite the sidecar record," never "omit the asset from
    the result." Purely additive: never touches/moves/deletes the flagged
    asset itself, only writes a new small sidecar file next to it -- this
    is how the ALREADY-EXISTING incident file
    (`01_short_render_v3_UNSAFE_broll_DO_NOT_USE.mp4`) gets real,
    persistent, machine-enforced protection without needing to move or
    republish anything."""
    flagged = []
    for path in Path(root_dir).rglob("*"):
        if not path.is_file() or path.name.endswith(".safety.json"):
            continue
        marker = detect_legacy_unsafe_filename(path)
        if marker is None:
            continue
        existing = read_asset_safety_record(path)
        if existing is not None and existing.get("status") == AssetSafetyStatus.UNSAFE:
            flagged.append(path)  # already flagged -- still reported, just not re-written
            continue
        write_asset_safety_record(
            path, AssetSafetyStatus.UNSAFE,
            reason=f"legacy filename marker '{marker}' detected by scan_for_legacy_unsafe_assets",
            source="legacy_filename_scan",
        )
        flagged.append(path)
    return flagged
