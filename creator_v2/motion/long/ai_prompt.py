#!/usr/bin/env python3
"""Prompt ảnh dự phòng, tất định, cho các khoảng Long thiếu hình.

Không gọi model hay API. Hồ sơ kênh là JSON hợp lệ YAML để không phụ thuộc
thư viện YAML khi chạy trong môi trường sản xuất.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LEXICON = ROOT / ".ref" / "vietneu-main" / "library" / "assets" / "lexicon" / "chung.json"
CHANNEL_LEXICONS = {
    "mim": ROOT / "docs" / "pm" / "ai-image" / "lexicon_mim.json",
    "ck": ROOT / "docs" / "pm" / "ai-image" / "lexicon_ck.json",
}


def _fold(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower().replace("đ", "d"))
    return "".join(ch for ch in value if unicodedata.category(ch) != "Mn")


def load_profile(path: str | Path) -> dict[str, Any]:
    """Load the repository's JSON-in-YAML channel profile."""
    with Path(path).open(encoding="utf-8") as handle:
        result = json.load(handle)
    if not isinstance(result, dict):
        raise ValueError(f"Hồ sơ không phải object: {path}")
    return result


def _lexicon_entries(path: Path = LEXICON) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return [item for item in data.get("muc", []) if isinstance(item, dict)]


def lexicon_for_profile(profile: dict[str, Any]) -> Path:
    """Use a channel lexicon when the profile identifies MIM or CK."""
    channel = _fold(str(profile.get("kenh") or ""))
    return CHANNEL_LEXICONS.get(channel, LEXICON)


def select_subject(narration: str, profile: dict[str, Any], *, lexicon_path: Path | None = None,
                   previous_subject: str | None = None) -> tuple[str, bool]:
    """Select the most specific spoken subject and record whether it is a fallback.

    Ties retain lexicon order.  If the adjacent prompt would repeat exactly, use
    the next matching subject; two fallback prompts rotate through safe neutral
    alternatives so a sequence is not visually identical.
    """
    lexicon_path = lexicon_path or lexicon_for_profile(profile)
    haystack = _fold(narration)
    matches: list[tuple[int, int, str]] = []
    for index, entry in enumerate(_lexicon_entries(lexicon_path)):
        vietnamese = entry.get("vi")
        values = [vietnamese] if isinstance(vietnamese, str) else vietnamese if isinstance(vietnamese, list) else []
        for value in values:
            folded = _fold(str(value))
            english = str(entry.get("en") or "").strip()
            if folded and english and re.search(r"(?<!\w)" + re.escape(folded) + r"(?!\w)", haystack):
                matches.append((len(folded), index, english))
    if matches:
        matches.sort(key=lambda match: (-match[0], match[1]))
        for _, _, subject in matches:
            if subject != previous_subject:
                return subject, False
        return matches[0][2] + ", from a distinct editorial angle", False
    assets = profile.get("assets") if isinstance(profile.get("assets"), dict) else {}
    fallback = str(assets.get("fallback_subject") or "an abstract editorial visual related to the narration")
    if fallback == previous_subject:
        alternatives = assets.get("fallback_subject_alternatives") or []
        if isinstance(alternatives, str):
            alternatives = [alternatives]
        for alternative in alternatives:
            if str(alternative).strip() and str(alternative) != previous_subject:
                return str(alternative), True
        fallback += ", from a distinct editorial angle"
    return fallback, True


def _subject(narration: str, profile: dict[str, Any], lexicon_path: Path | None = None) -> str:
    """Compatibility wrapper for callers that only need the visual subject."""
    return select_subject(narration, profile, lexicon_path=lexicon_path)[0]


def generate_prompt(narration: str, profile: dict[str, Any], image_number: int = 1,
                    lexicon_path: Path | None = None, previous_subject: str | None = None) -> str:
    """Make a repeatable, safe English prompt from narration and a channel profile."""
    del image_number  # Kept as an explicit stable API for future deterministic variants.
    assets = profile.get("assets") if isinstance(profile.get("assets"), dict) else {}
    style = str(assets.get("phong_cach") or "editorial illustration")
    subject, _ = select_subject(narration, profile, lexicon_path=lexicon_path,
                                previous_subject=previous_subject)
    culture = str(assets.get("van_hoa") or "")
    lighting = str(assets.get("anh_sang") or "soft directional light")
    affirmations = assets.get("cum_khang_dinh") or []
    if isinstance(affirmations, str):
        affirmations = [affirmations]
    forbidden = assets.get("cam_cum") or []
    if isinstance(forbidden, str):
        forbidden = [forbidden]
    parts = [style, subject, culture, lighting, *map(str, affirmations)]
    prompt = ". ".join(part.strip(" .") for part in parts if str(part).strip())
    if forbidden:
        prompt += ". Avoid " + ", ".join(str(part) for part in forbidden if str(part).strip())
    return re.sub(r"\s+", " ", prompt).strip() + "."


def generate_prompt_details(narration: str, profile: dict[str, Any], image_number: int = 1,
                            *, previous_subject: str | None = None,
                            lexicon_path: Path | None = None) -> dict[str, Any]:
    """Return a prompt plus provenance used by coverage-gap generation/reporting."""
    subject, used_fallback = select_subject(narration, profile, lexicon_path=lexicon_path,
                                            previous_subject=previous_subject)
    return {
        "prompt": generate_prompt(narration, profile, image_number, lexicon_path, previous_subject),
        "subject": subject,
        "used_fallback_subject": used_fallback,
        "lexicon": str((lexicon_path or lexicon_for_profile(profile)).relative_to(ROOT)),
    }

