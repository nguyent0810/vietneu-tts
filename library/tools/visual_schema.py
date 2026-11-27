"""Validation contract for Long visual payloads."""
from __future__ import annotations

from typing import Any

# Each entry is a set of alternative field groups. A group means all fields in
# it must be present; any group is sufficient. Conditional scenes are checked
# by their actual renderer inputs (for example an image source).
REQUIRED: dict[str, tuple[tuple[str, ...], ...]] = {
    "wheel": (("title", "steps"),), "elements": (("title", "year", "steps"),),
    "years": (("items",),), "list": (("items",),), "timeline": (("items",),),
    "compare": (("left", "right"),), "stat": (("value", "label"),),
    "quote": ((),), "map": (("countries",), ("pins",)),
    "word": (("text",), ("fx",)), "illus": (("scene",),),
    "endcard": (("text", "sub"),), "doc": (("file",), ("query",), ("museum",)),
    "photo": (("file",), ("query",)), "clock": (("title", "steps"),),
    "ask": ((),), "shadow": (("scene",), ("text",)),
    "hexagram": (("hex",), ("name",)), "luoshu": (("value",),),
    "ledger": (("title",),), "breath": (("text",),), "museum": (("file",), ("query",), ("museum",)),
    "napam": (("chi", "year"), ("chi", "element")),
    "cuudieu": (("title",),), "eclipse": (("title",),),
    "lookup": (("title",),), "annot": (("text",),),
    "relic": (("file",), ("query",), ("museum",)),
    "chiwheel": (("chi",),), "pie": (("value",),),
    "compass": (("dirs",),), "teaser": (("text",),), "clues": (("items",),),
    "stamp": (("text",),), "scroll": (("text",),), "dialog": (("left", "right"),),
    "wind": (("direction",), ("dirs",)), "bagua": (("gua",), ("name",)),
    "studio": (("file",), ("query",), ("museum",)),
    "region": (("name",), ("region",)), "profile": (("name",), ("profile",)),
    "kinetic_punch": (("text",),), "keyword_spotlight": (("text",),),
    "number_impact": (("value",),), "quote_reveal": ((),),
    "contrast_split": (("left", "right"),), "decode_reveal": (("text",),),
    "image_text_fusion": (("src", "text"),), "question_answer": (("text",),),
}

META_FIELDS = {"type", "suggested", "role", "until", "at", "preset"}
IMAGE_SOURCE_TYPES = {"doc", "photo", "museum", "relic"}
# Renderer tự lấy chữ của chính câu (longform.js: ask dùng ln.words; quote/word dùng câu hoặc **chữ khoá**),
# nên spec chỉ có type vẫn hợp lệ ở cổng render (plan cũ dựa vào điều này).
LINE_TEXT_TYPES = {"ask", "quote", "word"}


def visual_empty(spec: Any) -> tuple[bool, list[str]]:
    """Only reject a truly payload-free spec or a source-less required image."""
    if not isinstance(spec, dict):
        return True, ["visual phải là object"]
    typ = str(spec.get("type") or "")
    payload = {k: v for k, v in spec.items() if k not in META_FIELDS
               and not (k == "preset" and v in (None, "", [], {}))
               and v not in (None, "", [], {})}
    if not payload and typ in LINE_TEXT_TYPES:
        return False, []
    if not payload:
        _, missing = visual_ready(spec)
        return True, missing or ["không có dữ liệu visual"]
    if typ in IMAGE_SOURCE_TYPES and not any(spec.get(k) for k in ("museum", "file", "query")):
        return True, ["museum, file hoặc query"]
    return False, []


def visual_ready(spec: Any) -> tuple[bool, list[str]]:
    """Return whether a visual has a renderable payload and its missing fields."""
    if not isinstance(spec, dict):
        return False, ["visual phải là object"]
    typ = str(spec.get("type") or "")
    if not typ:
        return False, ["type"]
    groups = REQUIRED.get(typ)
    if groups is None:
        return False, [f"type không có schema: {typ}"]
    missing_sets = [[key for key in group if key not in spec or spec[key] in (None, "", [], {})]
                    for group in groups]
    if any(not missing for missing in missing_sets):
        missing: list[str] = []
        if typ == "napam" and not any(spec.get(k) for k in ("file", "query", "museum")):
            missing.append("query, file hoặc museum (nguồn ảnh)")
        if typ == "list" and not spec.get("items"):
            missing.append("items (không rỗng)")
        if typ in {"timeline", "years", "clues"} and not spec.get("items"):
            missing.append("items (không rỗng)")
        if typ in {"wheel", "clock", "elements"} and not spec.get("steps"):
            missing.append("steps (không rỗng)")
        if typ in {"wheel", "clock", "elements"} and spec.get("steps"):
            valid_step = {
                "wheel": lambda s: s.get("at") is not None and any(s.get(k) for k in ("chi", "rel", "label")),
                "clock": lambda s: s.get("at") is not None and bool(s.get("chi")),
                "elements": lambda s: all(s.get(k) not in (None, "", [], {}) for k in ("at", "from", "to", "kind")),
            }[typ]
            if not all(isinstance(step, dict) and valid_step(step) for step in spec["steps"]):
                fields = "at/chi|rel|label" if typ == "wheel" else "at/chi" if typ == "clock" else "at/from/to/kind"
                missing.append(f"steps cần {fields}")
        if typ == "map" and not (spec.get("countries") or spec.get("pins")):
            missing.append("countries hoặc pins (không rỗng)")
        if typ in {"list", "timeline", "years", "clues"} and spec.get("items"):
            item_fields = {"list": ("at", "text"), "timeline": ("at", "yr", "label"),
                           "years": ("at", "yr"), "clues": ("text",)}[typ]
            if not all(isinstance(item, dict) and all(item.get(k) not in (None, "", [], {}) for k in item_fields)
                       for item in spec["items"]):
                missing.append("items cần " + ", ".join(item_fields))
        if typ == "compare" and any(not isinstance(spec.get(side), dict) or not
                                     any(spec[side].get(k) for k in ("title", "body")) for side in ("left", "right")):
            missing.append("left/right cần title hoặc body")
        if not missing:
            return True, []
        return False, missing
    return False, sorted(set(k for group in missing_sets for k in group))
