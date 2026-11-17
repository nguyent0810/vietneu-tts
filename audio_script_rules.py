"""Small, deterministic audio contract; no media, TTS or network operations."""
from __future__ import annotations

import re

# Lead fills in the actual merge date. Never backdate scheduled legacy plans.
AUDIO_SCRIPT_FROM: str | None = "2026-11-18"
SHORT_WIN_PROFILE = "short_win_9_18"


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
