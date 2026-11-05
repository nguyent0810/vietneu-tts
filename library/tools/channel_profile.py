"""Nạp và nhận diện hồ sơ kênh trong :mod:`library.channels`.

Các tệp ``.yaml`` ở đây là JSON hợp lệ; giữ phần mở rộng để tương thích với
những công cụ đã có, nhưng không âm thầm chấp nhận một định dạng khác.
"""
from __future__ import annotations

import json
from pathlib import Path


CHANNELS_DIR = Path(__file__).resolve().parents[1] / "channels"

# 2026-11-05: đổi tên hồ sơ lịch sử; giữ lối gọi cũ cho các caller chưa migrate.
LEGACY_IDS = {"_thu_lich_su": "lich_su"}

_OPTIONAL_TYPES = {
    "kenh": str,
    "ngach": list,
    "khuon": list,
    "bao_ve": list,
    "assets": dict,
    "canh": dict,
    "typography": dict,
    "motion": dict,
    "sound": dict,
    "tts": dict,
    "kho_loc": dict,
}


def ids() -> list[str]:
    """Trả stem mọi hồ sơ thực (không gồm mẫu/hồ sơ ẩn)."""
    if not CHANNELS_DIR.is_dir():
        return []
    return sorted(p.stem for p in CHANNELS_DIR.glob("*.yaml") if not p.stem.startswith("_"))


def _validate(data: object, stem: str) -> dict:
    if not isinstance(data, dict):
        raise ValueError(f"{stem}: hồ sơ phải là object JSON")
    for key, expected in _OPTIONAL_TYPES.items():
        if key in data and not isinstance(data[key], expected):
            raise ValueError(f"{stem}: khoá {key!r} phải là {expected.__name__}")
    if data.get("kenh") != stem:
        raise ValueError(f"{stem}: khoá 'kenh' phải trùng stem {stem!r}")
    if "khuon" in data:
        for index, item in enumerate(data["khuon"]):
            if not isinstance(item, dict):
                raise ValueError(f"{stem}: khoá 'khuon[{index}]' phải là dict")
    return data


def load(id: str) -> dict:
    """Nạp một hồ sơ, kiểm tra schema tối thiểu và compatibility ID cũ."""
    requested = str(id)
    stem = LEGACY_IDS.get(requested, requested)
    if stem not in ids():
        raise ValueError(f"Không có hồ sơ kênh {requested!r}")
    path = CHANNELS_DIR / f"{stem}.yaml"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{stem}: JSON không hợp lệ: {exc.msg}") from exc
    return _validate(data, stem)


def _matches(value: object) -> set[str]:
    if not isinstance(value, str) or not value.strip():
        return set()
    needle = LEGACY_IDS.get(value.strip(), value.strip()).casefold()
    found: set[str] = set()
    for stem in ids():
        profile = load(stem)
        names = [stem, profile.get("ten_hien_thi"), *(profile.get("alias") or [])]
        if any(isinstance(name, str) and name.casefold() == needle for name in names):
            found.add(stem)
    return found


def _one(matches: set[str], source: str) -> str:
    if len(matches) == 1:
        return next(iter(matches))
    if not matches:
        raise ValueError(f"Không nhận diện được kênh từ {source}")
    raise ValueError(f"Kênh mơ hồ từ {source}: {', '.join(sorted(matches))}")


def resolve(item: dict | None = None, *, channel: str | None = None, slug: str | None = None) -> str:
    """Nhận diện kênh theo item, cờ ``--channel``, rồi tiền tố slug.

    Không có fallback mặc định: một slug chung hay đầu vào thiếu phải dừng rõ ràng.
    """
    if item is not None and not isinstance(item, dict):
        raise ValueError("item phải là dict hoặc None")
    item = item or {}
    explicit = item.get("channel") or item.get("kenh")
    if explicit:
        return _one(_matches(explicit), "item.channel/item.kenh")
    if channel:
        return _one(_matches(channel), "--channel")
    if slug:
        found: set[str] = set()
        for stem in ids():
            prefixes = load(stem).get("slug_prefix") or []
            if isinstance(prefixes, str):
                prefixes = [prefixes]
            if any(isinstance(prefix, str) and prefix and slug.casefold().startswith(prefix.casefold())
                   for prefix in prefixes):
                found.add(stem)
        return _one(found, "slug")
    raise ValueError("Thiếu channel/kenh, --channel và slug; không có kênh mặc định")
