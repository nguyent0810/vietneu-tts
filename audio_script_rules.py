"""Small, deterministic audio contract; no media, TTS or network operations."""
from __future__ import annotations

import re
import json
from pathlib import Path

# Lead fills in the actual merge date. Never backdate scheduled legacy plans.
AUDIO_SCRIPT_FROM: str | None = "2026-11-18"
SHORT_WIN_PROFILE = "short_win_9_18"
FS_LOOKUP_STYLES = {"yeartable", "month_sheet", "daytable", "ngaytot"}
FS_LOOKUP_LANES = {"lookup", "hoangdao_daily", "ngaytot", "lich"}


def is_fs_lookup(row: dict) -> bool:
    return row.get("series") == "fs" and (
        row.get("style") in FS_LOOKUP_STYLES or row.get("lane") in FS_LOOKUP_LANES
    )


def apply_fs_short_defaults(rows: list[dict], existing_rows=()) -> list[dict]:
    """Set the FS lookup audio contract on new rows; preserve on-disk rows by id."""
    existing = {row.get("id"): row for row in existing_rows if row.get("id")}
    out = []
    for row in rows:
        old = existing.get(row.get("id")) if row.get("id") else None
        if old is not None:
            out.append(old)
            continue
        if is_fs_lookup(row):
            row = dict(row)
            row["audio_profile"] = SHORT_WIN_PROFILE
            row["duration_band"] = [10, 16]
        out.append(row)
    return out


def prepare_fs_short_plan(rows: list[dict], path: str | Path) -> list[dict]:
    """Add defaults to new rows while retaining matching rows already on disk."""
    target = Path(path)
    try:
        existing = json.loads(target.read_text(encoding="utf-8")) if target.is_file() else []
    except (OSError, json.JSONDecodeError):
        existing = []
    return apply_fs_short_defaults(rows, existing if isinstance(existing, list) else [])


def effective_date(row: dict) -> str:
    return str(row.get("effective_date") or row.get("day") or row.get("publish_at") or "")[:10]


def new_audio_plan(row: dict) -> bool:
    return bool(row.get("pause_ctx")) or bool((row.get("tts") or {}).get("pause_ctx")) or bool(
        AUDIO_SCRIPT_FROM and effective_date(row) >= AUDIO_SCRIPT_FROM
    )


def short_audio_profile(row: dict) -> str:
    # Existing daily tables inherit a profile, rather than needing a waiver.
    if row.get("style") == "daytable":
        return SHORT_WIN_PROFILE
    return str(row.get("audio_profile") or "short_v2")


def comma_ending(text: str) -> bool:
    return text.rstrip().rstrip('\"”’»\')').rstrip().endswith(",")


_MARKUP = re.compile(
    r'https?://|www\.|"\w+"\s*:|\{[^{}]*\}|\[PAUSE(?:\b[^\]]*)?\]', re.I
)


def markup_leaks(script: list[str], silence=()) -> list[tuple[int, str]]:
    mute = set(silence)
    return [(i, line) for i, line in enumerate(script, 1)
            if i not in mute and _MARKUP.search(line.replace("**", ""))]
