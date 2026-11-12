"""Gợi ý 1–3 cảnh style bổ sung (#258) cho plan Long mới.

Hàm `suggest` không ghi đĩa và không sửa dict đầu vào. `apply_suggestions` chỉ ghi
khi `adopt=True` (builder plan mới). Plan cũ, `legacy`, hoặc `"style_suggest": false`
giữ nguyên. Cảnh ghi vào `visuals` với `type` rõ — người viết xoá được.

Đặt sau giây 40, không liền nhau, không quá 3 (kể cả cảnh style người viết đã ghi).
Nhịp giây khi chưa có TTS: 185 tiếng/phút kể cả nghỉ (skill long-script).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

STYLE_TYPES = ("woodcut", "papercut", "oneline", "film16", "blueprint", "pencil")
OPENING_S = 40.0
SYLLABLES_PER_MIN = 185.0
CAP = 3

# Thứ tự trong bảng là thứ tự ưu tiên khi một loại chỗ hợp nhiều style.
CHANNEL_STYLES = {
    "bud": ("papercut", "oneline", "woodcut"),
    "fs": ("woodcut", "blueprint", "papercut"),
    "vsd": ("film16", "blueprint", "papercut", "pencil"),
    "cl": ("film16", "pencil", "woodcut"),
}
_ALIAS = {
    "bud": "bud", "phat": "bud",
    "fs": "fs", "phongthuy": "fs", "phong_thuy": "fs",
    "vsd": "vsd", "vansudia": "vsd", "van_su_dia": "vsd", "vănsửđịa": "vsd",
    "cl": "cl", "hinh_su": "cl", "hinhsu": "cl", "hìnhsự": "cl",
}
_PREFER = {
    "chapter": ("film16", "woodcut", "papercut", "oneline", "pencil"),
    "floor": ("blueprint", "papercut", "pencil", "woodcut"),
    "number": ("woodcut", "film16", "pencil"),
    "archive": ("film16", "pencil", "woodcut", "papercut"),
}
_WHY = {
    "chapter": "thẻ chương",
    "floor": "mặt bằng",
    "number": "số liệu",
    "archive": "tư liệu",
}
_FLOOR = re.compile(r"mặt bằng|bản đồ|hướng nhà|thành luỹ|thành lũy|luỹ |lũy |kinh thành|bốn phương|mặt cắt", re.I)
_CITADEL = re.compile(r"thành|luỹ|lũy|tường|cổng", re.I)
_MOUNTAIN = re.compile(r"núi|non", re.I)
_VILLAGE = re.compile(r"làng|xóm", re.I)
_YEAR = re.compile(r"\b(\d{3,4})\b")
_SPAN_KEYS = ("steps", "items", "pins", "rows", "notes", "bars")


def channel_of(row: dict) -> str | None:
    raw = row.get("series") or row.get("channel") or row.get("kenh") or ""
    key = str(raw).strip().lower().replace(" ", "")
    return _ALIAS.get(key)


def is_long_row(row: dict) -> bool:
    if row.get("lane") == "long":
        return True
    return str(row.get("style") or "").endswith("_long")


def line_text(line) -> str:
    if isinstance(line, str):
        return line
    if isinstance(line, dict):
        return str(line.get("t") or line.get("text") or "")
    return str(line or "")


def plain(line) -> str:
    return re.sub(r"\*+", "", line_text(line)).strip()


def is_heading(line) -> bool:
    t = line_text(line).strip()
    return t.startswith("**") and t.endswith("**") and t.count("**") == 2 and len(plain(t)) > 0


def line_starts(script: list, segments: list | None = None) -> list[float]:
    if segments and len(segments) == len(script):
        try:
            return [float(s["start"]) for s in segments]
        except (KeyError, TypeError, ValueError):
            pass
    rate = SYLLABLES_PER_MIN / 60.0
    t = 0.0
    out = []
    for line in script:
        out.append(t)
        n = len(plain(line).split()) or 1
        t += n / rate
    return out


def _until(sid: int, spec: dict) -> int:
    if spec.get("type") in STYLE_TYPES:
        import hyperframes_bridge as HB
        return HB.style_until(sid, spec)
    ats = [sid]
    for key in _SPAN_KEYS:
        for item in spec.get(key) or []:
            if isinstance(item, dict) and isinstance(item.get("at"), int):
                ats.append(int(item["at"]))
    try:
        return int(spec.get("until") or max(ats))
    except (TypeError, ValueError):
        return sid


def _occupied(row: dict) -> set[int]:
    ids: set[int] = set()
    for key in (row.get("media") or {}):
        if str(key).isdigit():
            ids.add(int(key))
    for key, spec in (row.get("visuals") or {}).items():
        if str(key).isdigit() and isinstance(spec, dict):
            sid = int(key)
            ids.update(range(sid, _until(sid, spec) + 1))
    for key, spec in (row.get("figures") or {}).items():
        if str(key).isdigit() and isinstance(spec, dict) and spec.get("type") not in (None, "none"):
            ids.add(int(key))
    return ids


def _style_spans(visuals: dict) -> list[tuple[int, int, str]]:
    spans = []
    for key, spec in (visuals or {}).items():
        if not str(key).isdigit() or not isinstance(spec, dict):
            continue
        if spec.get("type") not in STYLE_TYPES:
            continue
        sid = int(key)
        spans.append((sid, _until(sid, spec), spec["type"]))
    return sorted(spans)


def _year(text: str) -> int | None:
    for match in _YEAR.finditer(text):
        year = int(match.group(1))
        if 100 <= year <= 2100:
            return year
    return None


TITLE_MAX = 32


def _short(text: str, limit: int = TITLE_MAX) -> str:
    """Chữ trên thẻ style: cả câu/tiêu đề nếu đủ ngắn, không thì rỗng (bỏ đề xuất).

    Không cắt mấy chữ đầu câu: ngày 12/11 cắt 22 ký tự ra thẻ cụt "Làm sao từ một đồng",
    "Do đó, suốt ba mươi" trên 3 Long đã render."""
    t = re.sub(r"\s+", " ", text).strip(" .,;:…")
    return t if len(t) <= limit else ""


def _first_word(text: str) -> str:
    words = re.findall(r"\w+", text, flags=re.UNICODE)
    return words[0] if words else ""


def _paper_scene(text: str, channel: str) -> str:
    if _CITADEL.search(text):
        return "citadel"
    if _MOUNTAIN.search(text):
        return "mountain"
    if _VILLAGE.search(text):
        return "village"
    return {"bud": "pagoda", "fs": "village"}.get(channel, "citadel")


def _spec(typ: str, sid: int, text: str, channel: str, kind: str) -> dict:
    word = _first_word(text)
    step = {"at": sid, "word": word} if word else {"at": sid}
    title = _short(text)
    spec: dict = {"type": typ, "suggested": True, "role": _WHY[kind]}
    if typ == "woodcut":
        spec.update({
            "text": title,
            "tone": "paper" if channel == "bud" else "dark" if channel == "fs" else "paper",
            "steps": [step],
        })
        if kind == "number" and (year := _year(text)):
            spec["value"] = year
        else:
            spec["motif"] = "lotus" if channel == "bud" else "gate"
    elif typ == "papercut":
        spec.update({
            "scene": _paper_scene(text, channel),
            "time": {"bud": "night", "fs": "dawn", "cl": "dusk"}.get(channel, "day"),
            "text": title,
            "steps": [step],
        })
    elif typ == "oneline":
        spec.update({
            "title": title,
            "items": [{"motif": "lotus" if channel == "bud" else "gate", "label": title, "at": sid, **({"word": word} if word else {})}],
        })
        if channel == "fs":
            spec["tone"] = "dark"
    elif typ == "film16":
        spec.update({"kicker": "Tư liệu", "title": title, "steps": [step]})
        if year := _year(text):
            spec["year"] = year
    elif typ == "blueprint":
        spec.update({
            "scene": "wall" if _CITADEL.search(text) else "house",
            "title": title or "Mặt bằng",
            "steps": [step],
        })
    elif typ == "pencil":
        scene = "mountain" if _MOUNTAIN.search(text) else "pagoda" if channel == "bud" else "gate"
        spec.update({"scene": scene, "title": title, "steps": [step]})
    return spec


def _kind_of(text: str, heading: bool) -> str | None:
    if heading:
        return "chapter"
    if _FLOOR.search(text):
        return "floor"
    if _year(text):
        return "number"
    if re.search(r"tư liệu|toàn thư|sử ký|bia", text, re.I):
        return "archive"
    return None


def _pick_type(kind: str, allowed: tuple[str, ...], used: set[str]) -> str:
    for name in _PREFER[kind]:
        if name in allowed and name not in used:
            return name
    for name in _PREFER[kind]:
        if name in allowed:
            return name
    return allowed[0]


def _adjacent(sid: int, spans: list[tuple[int, int, str]]) -> bool:
    for start, end, _typ in spans:
        if sid <= end + 1 and start <= sid + 1:
            return True
    return False


def suggest(row: dict, segments: list | None = None) -> list[dict]:
    """Danh sách đề xuất. Không sửa `row`."""
    channel = channel_of(row)
    allowed = CHANNEL_STYLES.get(channel or "")
    script = [line_text(x) for x in (row.get("script") or [])]
    if not allowed or not script or row.get("style_suggest") is False or row.get("legacy"):
        return []
    starts = line_starts(script, segments)
    busy = _occupied(row)
    spans = _style_spans(row.get("visuals") or {})
    room = CAP - len(spans)
    if room <= 0:
        return []
    buckets: dict[str, list[tuple[int, str]]] = {k: [] for k in _WHY}
    for index, text in enumerate(script):
        sid = index + 1
        if starts[index] < OPENING_S or sid in busy:
            continue
        if "**" in text and not is_heading(text):
            continue
        kind = _kind_of(plain(text), is_heading(text))
        if kind:
            buckets[kind].append((sid, text))
    import hf_batch_render as HBR  # noqa: PLC0415

    sim_visuals = dict(row.get("visuals") or {})
    sim = dict(row, visuals=sim_visuals)
    bare = set(HBR.bare_lines(sim))
    picked: list[dict] = []
    used = {typ for _s, _e, typ in spans}
    while len(picked) < room:
        grew = False
        for kind in ("chapter", "floor", "number", "archive"):
            if len(picked) >= room:
                break
            bucket = buckets[kind]
            while bucket:
                sid, text = bucket.pop(0)
                if not _short(plain(text)):
                    continue
                if _adjacent(sid, spans + [(p["sid"], _until(p["sid"], p["spec"]), p["type"]) for p in picked]):
                    continue
                typ = _pick_type(kind, allowed, used)
                spec = _spec(typ, sid, plain(text), channel, kind)
                sim_visuals[str(sid)] = spec
                now = set(HBR.bare_lines(sim))
                if now - bare:
                    # Ticket 046: câu đang giữ ảnh mà gắn style thì câu sau thành câu trần -> xét ứng viên kế.
                    del sim_visuals[str(sid)]
                    continue
                bare = now
                used.add(typ)
                picked.append({
                    "sid": sid,
                    "type": typ,
                    "why": _WHY[kind],
                    "start": starts[sid - 1],
                    "spec": spec,
                })
                grew = True
                break
        if not grew:
            break
    return picked


def apply_suggestions(row: dict, *, adopt: bool = False, segments: list | None = None) -> list[int]:
    """Ghi đề xuất vào `visuals` của plan mới. Trả về số câu đã thêm.

    `adopt=False` không sửa gì (plan cũ, lần đọc lại). Không đè visual đã có.
    """
    if not adopt or not is_long_row(row):
        return []
    props = suggest(row, segments)
    if not props:
        return []
    visuals = row.get("visuals")
    if not isinstance(visuals, dict):
        visuals = {}
        row["visuals"] = visuals
    import hf_batch_render as HBR  # noqa: PLC0415

    added = []
    for prop in props:
        key = str(prop["sid"])
        if key in visuals:
            continue
        before = set(HBR.bare_lines(row))
        visuals[key] = prop["spec"]
        if set(HBR.bare_lines(row)) - before:
            # Ticket 046: cảnh style trên câu đang giữ ảnh làm câu sau mất ảnh giữ -> câu trần.
            del visuals[key]
            continue
        added.append(prop["sid"])
    return added


def warning_line(row: dict, segments: list | None = None) -> str | None:
    """Một dòng cảnh báo nhẹ. None khi không cần nhắc."""
    if not is_long_row(row) or row.get("legacy") or row.get("style_suggest") is False:
        return None
    if channel_of(row) not in CHANNEL_STYLES or _style_spans(row.get("visuals") or {}):
        return None
    props = suggest(row, segments)
    if props:
        bits = ", ".join(f"câu {p['sid']} {p['type']} ({p['why']})" for p in props)
        where = f" Gợi ý: {bits}."
    else:
        where = " Không thấy chỗ đặt sau giây 40."
    return (f"    CẢNH BÁO style: Long mới {row.get('id')} có 0 cảnh style "
            f"(không chặn, tối đa 3, không liền nhau).{where} "
            f"Thêm vào visuals hoặc ghi \"style_suggest\": false.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="In gợi ý cảnh style cho plan Long. Không ghi file.")
    ap.add_argument("plan")
    ap.add_argument("--dry-run", action="store_true", help="Chỉ in. Lệnh không có cờ này cũng không ghi.")
    args = ap.parse_args(argv)
    path = Path(args.plan)
    before = path.read_bytes()
    data = json.loads(before)
    rows = data if isinstance(data, list) else [data]
    import hyperframes_bridge as HB
    for row in rows:
        if not isinstance(row, dict):
            continue
        props = suggest(row)
        bits = ", ".join(f"câu {p['sid']} {p['type']} ({p['why']})" for p in props) or "(không chỗ sau giây 40)"
        spans = [(p["sid"], _until(p["sid"], p["spec"]), p["type"]) for p in props]
        issues = HB.style_scene_issues(spans)
        early = [p["sid"] for p in props if p["start"] < OPENING_S]
        wrong = [p["type"] for p in props if p["type"] not in CHANNEL_STYLES.get(channel_of(row) or "", ())]
        print(f"{row.get('id')} kênh={channel_of(row) or '?'} gợi ý {len(props)}: {bits}")
        print(f"  trần/liền: {issues or 'ĐẠT'} | trước 40s: {early or 'không'} | lệch bảng: {wrong or 'không'}")
    after = path.read_bytes()
    print("file gốc không đổi" if after == before else "file gốc ĐÃ ĐỔI")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
