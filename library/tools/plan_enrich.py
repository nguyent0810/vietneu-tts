"""Enrich Long rows with deterministic scene and motion suggestions.

Ask cards from the picker are capped at one per two minutes and at 25% of
visuals. Hand-written asks are kept; a warning is printed when they exceed
the cap. ``kinetic_suggest`` lists 3–6 opt-in presets (the renderer ignores
this key until a writer copies ``preset`` onto the host visual).

``apply_to_new_long_plan`` is the one call a Long builder makes for a new
plan file. An existing destination file is returned as stored and is not
rewritten.

``scene_decision`` is indexed by 1-based script line (string keys). Each entry
contains ``scene`` (picker payload and reason/candidates), ``motion`` (preset
and reason), and ``source`` (``picker`` or ``editor``). Existing visuals/media
keys are editorial choices and are retained without running either picker for
that line.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from library.tools import motion_picker, scene_picker

# Cùng mốc của long_script_lint / retention_issues: 185 tiếng mỗi phút khi chưa có TTS.
RATE = 185 / 60
ASK_WINDOW_S = 120.0
COLD_OPEN_S = 40.0
KINETIC_MIN = 3
KINETIC_MAX = 6
KINETIC_HOST = {
    "number_impact": "stat",
    "quote_reveal": "quote",
    "contrast_split": "compare",
    "question_answer": "ask",
    "keyword_spotlight": "word",
    "kinetic_punch": "word",
}
_KINETIC_ORDER = tuple(KINETIC_HOST)
_CONTRAST_SPLIT = re.compile(
    r"\s*\b(?:nhưng|trái lại|ngược lại|so với|trong khi)\b\s*", re.I)
_CONTRAST_WORD = re.compile(
    r"\b(?:nhưng|trái lại|ngược lại|so với|trong khi|không phải)\b", re.I)
_YEAR_RE = re.compile(r"\b(?:1[0-9]{3}|20[0-9]{2})\b")
_ILLUS_KEYS = (
    ("lotus", ("sen", "hoa sen", "đầm")),
    ("moon", ("trăng",)),
    ("house", ("nhà", "cung", "đền", "chùa")),
    ("road", ("đường", "ngựa")),
    ("sunrise", ("bình minh", "mặt trời")),
)
_ILLUS_SCENES = ("sunrise", "lotus", "moon", "house", "road")


def _line_count(row: dict[str, Any]) -> int:
    lines = row.get("script") or row.get("sentences") or row.get("lines") or []
    return len(lines) if isinstance(lines, list) else 0


def _keys(mapping: Any) -> set[int]:
    if not isinstance(mapping, dict):
        return set()
    return {int(key) for key in mapping if str(key).isdigit()}


def _lines(row: dict[str, Any]) -> list[Any]:
    lines = row.get("script") or row.get("sentences") or row.get("lines") or []
    return lines if isinstance(lines, list) else []


def _sha(seed: str, purpose: str, line: int) -> int:
    return int(hashlib.sha256(f"{seed}:{purpose}:{line}".encode()).hexdigest()[:8], 16)


def tie_key(seed: str, line: int, ideal: float) -> tuple:
    """Khoảng cách tới mốc, rồi băm theo id video. Cùng id thì cùng thứ tự."""
    return (abs(line - ideal), _sha(seed, "kin", line), line)


def ask_cap(duration_s: float, n_visuals: int) -> tuple[int, int, int]:
    """(trần, trần theo 2 phút, trần 25%). Trần = min hai trần, làm tròn xuống."""
    time_cap = int(duration_s // ASK_WINDOW_S) if duration_s > 0 else 0
    frac_cap = int(n_visuals * 0.25) if n_visuals > 0 else 0
    return max(0, min(time_cap, frac_cap)), time_cap, frac_cap


def line_spans(row: dict[str, Any]) -> tuple[list[tuple[float, float]], str]:
    """Giây đầu/cuối từng dòng. TTS thật nếu có; không thì 185 tiếng/phút."""
    lines = _lines(row)
    n = len(lines)
    segs, flag = scene_picker._clock(row, n)
    if segs and n and len(segs) >= n:
        return [(float(s["start"]), float(s["end"])) for s in segs[:n]], flag
    out: list[tuple[float, float]] = []
    t = 0.0
    for line in lines:
        words = len(str(line).replace("**", "").split()) or 1
        d = words / RATE
        out.append((t, t + d))
        t += d
    return out, "ước 185 tiếng/phút"


def visual_counts(row: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    visuals = row.get("visuals") or {}
    if not isinstance(visuals, dict):
        return counts
    for spec in visuals.values():
        if isinstance(spec, dict):
            typ = str(spec.get("type") or "?")
            counts[typ] = counts.get(typ, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def _window(spans: list[tuple[float, float]], line: int) -> int:
    start = spans[line - 1][0] if 0 < line <= len(spans) else 0.0
    return int(start // ASK_WINDOW_S)


def _allowed(typ: str, forbidden: set[str], ok: set[str]) -> bool:
    return typ not in forbidden and typ in ok


def _short(text: str, n: int = 8) -> str:
    return " ".join(str(text).split()[:n])


def _list_items(text: str) -> list[str]:
    raw = text or ""
    m = re.search(
        r"(?:bao gồm|gồm có|các loại|ví dụ|chẳng hạn|gồm)\s*:?\s*([^.]{0,200})",
        raw, re.I)
    if not m:
        return []
    parts = [p.strip(" *:") for p in re.split(r",|\s+và\s+|\s+hay\s+", m.group(1)) if p.strip(" *:")]
    parts = [p for p in parts if p and len(p.split()) <= 8]
    return parts if len(parts) >= 2 else []


def _illus_scene(text: str, seed: str, line: int) -> str:
    n = (text or "").lower()
    for scene, keys in _ILLUS_KEYS:
        for key in keys:
            if re.search(rf"\b{re.escape(key)}\b", n):
                return scene
    return _ILLUS_SCENES[_sha(seed, "illus", line) % len(_ILLUS_SCENES)]


def _replace_ask(text: str, line: int, seed: str, forbidden: set[str], ok: set[str]) -> dict[str, Any] | None:
    """Đổi thẻ ask dư sang loại kho đã có, chỉ khi rút được dữ liệu từ chính câu."""
    nums = scene_picker.quantities(text)
    if nums and _allowed("stat", forbidden, ok):
        value = nums[0]
        spec: dict[str, Any] = {"type": "stat", "value": int(value) if value == int(value) else value}
        if "%" in (text or ""):
            spec["suffix"] = "%"
        return spec
    tags = {t["tag"] for t in scene_picker.classify(text)}
    if "trich_dan" in tags and _allowed("quote", forbidden, ok):
        return {"type": "quote"}
    items = _list_items(text)
    if items and _allowed("list", forbidden, ok):
        return {"type": "list", "items": [{"text": it, "at": line} for it in items[:6]]}
    years = _YEAR_RE.findall(text or "")
    if years and _allowed("timeline", forbidden, ok):
        return {"type": "timeline", "items": [{"yr": y, "at": line} for y in years[:4]]}
    if _allowed("map", forbidden, ok):
        found = scene_picker.places_in(text)
        if found:
            countries: list[str] = []
            pins = []
            for name in found[:6]:
                lon, lat, country = scene_picker.gazetteer()[name]
                if country not in countries:
                    countries.append(country)
                pins.append({"name": name, "lon": float(lon), "lat": float(lat), "at": line})
            return {"type": "map", "countries": countries, "pins": pins}
    parts = _CONTRAST_SPLIT.split(text or "", maxsplit=1)
    if (len(parts) == 2 and all(p.strip() for p in parts)
            and (scene_picker.two_measurable_sides(text) or _CONTRAST_WORD.search(text or ""))
            and _allowed("compare", forbidden, ok)):
        return {"type": "compare",
                "left": {"title": _short(parts[0].strip(" ,.;:"))},
                "right": {"title": _short(parts[1].strip(" ,.;:"))}}
    if "khai_niem" in tags and _allowed("word", forbidden, ok):
        return {"type": "word"}
    if _allowed("illus", forbidden, ok):
        return {"type": "illus", "scene": _illus_scene(text, seed, line)}
    if _allowed("word", forbidden, ok):
        return {"type": "word"}
    return None


def _apply_ask_cap(row: dict[str, Any], decisions: dict[str, dict[str, Any]],
                   hand_lines: set[int], spans: list[tuple[float, float]],
                   forbidden: set[str], ok: set[str]) -> int:
    """Đổi ask do bộ chọn khi vượt trần. Ask ghi tay giữ nguyên, chỉ cảnh báo."""
    visuals = row.get("visuals") or {}
    lines = _lines(row)
    seed = str(row.get("id") or "")
    n_visuals = sum(1 for spec in visuals.values() if isinstance(spec, dict))
    duration = spans[-1][1] if spans else 0.0
    cap, time_cap, frac_cap = ask_cap(duration, n_visuals)
    editor_asks = sorted(
        i for i in hand_lines
        if isinstance(visuals.get(str(i)), dict) and visuals[str(i)].get("type") == "ask")
    auto_asks = sorted(
        int(i) for i, dec in decisions.items()
        if str(i).isdigit() and dec.get("source") == "picker" and int(i) not in hand_lines
        and isinstance(visuals.get(str(i)), dict) and visuals[str(i)].get("type") == "ask")
    if len(editor_asks) > cap:
        print(f"!! ask trần: {seed} có {len(editor_asks)} thẻ ask ghi tay, trần {cap} "
              f"(1/120s={time_cap}, ≤25%={frac_cap}, n={n_visuals}) — giữ nguyên")
    by_window: dict[int, list[int]] = {}
    for line in editor_asks:
        by_window.setdefault(_window(spans, line), []).append(line)
    for window, group in sorted(by_window.items()):
        if len(group) > 1:
            print(f"!! ask trần: {seed} có {len(group)} thẻ ask ghi tay trong cùng 2 phút "
                  f"(câu {', '.join(str(x) for x in group)}) — giữ nguyên")
    used_windows = set(by_window)
    slots = max(0, cap - len(editor_asks))
    pool: dict[int, list[int]] = {}
    for line in auto_asks:
        window = _window(spans, line)
        if window in used_windows:
            continue
        pool.setdefault(window, []).append(line)
    kept: set[int] = set()
    for window in sorted(pool):
        if len(kept) >= slots:
            break
        group = pool[window]

        def rank(line: int, group: list[int] = group) -> tuple:
            text = str(lines[line - 1]) if 0 < line <= len(lines) else ""
            return (0 if "?" in text else 1, _sha(seed, "ask", line), line)

        chosen = min(group, key=rank)
        kept.add(chosen)
        used_windows.add(window)
    converted = 0
    for line in auto_asks:
        if line in kept:
            continue
        text = str(lines[line - 1]) if 0 < line <= len(lines) else ""
        spec = _replace_ask(text, line, seed, forbidden, ok)
        if spec is None:
            print(f"!! ask trần: {seed} câu {line} không đổi được (kho không có loại thay) — giữ ask")
            continue
        visuals[str(line)] = spec
        dec = decisions.get(str(line)) or {}
        scene = dec.get("scene")
        if isinstance(scene, dict):
            scene["picked"] = spec
            scene["ly_do"] = (scene.get("ly_do") or "") + "; đổi từ ask vì trần"
        converted += 1
    row["_ask_mix"] = {"cap": cap, "time_cap": time_cap, "frac_cap": frac_cap,
                       "converted": converted, "clock_s": duration}
    return converted


def _is_quote(text: str) -> bool:
    raw = text or ""
    n = raw.lower()
    return any(ch in raw for ch in '"“”') or any(w in n for w in ("theo lời", "trích", "ghi rằng", "viết rằng"))


def _is_punch(text: str) -> bool:
    n = (text or "").lower()
    return any(w in n for w in ("chính là", "mới là", "đây mới"))


def _marked(text: str) -> bool:
    s = (text or "").strip()
    if s.startswith("**") and s.endswith("**") and s.count("**") == 2:
        return False
    return "**" in (text or "")


def _preset_for(text: str) -> tuple[str, str] | None:
    if scene_picker.quantities(text):
        return "number_impact", "câu số liệu"
    if _is_quote(text):
        return "quote_reveal", "câu trích"
    if scene_picker.two_measurable_sides(text) or _CONTRAST_WORD.search(text or ""):
        return "contrast_split", "câu đối lập"
    if "?" in (text or ""):
        return "question_answer", "câu hỏi"
    if _marked(text):
        return "keyword_spotlight", "câu nhấn"
    if _is_punch(text):
        return "kinetic_punch", "câu nhấn"
    return None


def _clip_starts(clips: Any) -> list[int]:
    if not isinstance(clips, dict):
        return []
    found: list[int] = []
    for key in clips:
        if str(key).isdigit():
            n = int(key)
            if n >= 1:
                found.append(n)
    return sorted(set(found))


def _cold_lines(lines: list[Any], clips: Any) -> set[int]:
    """Dòng thuộc cold open, chưa cắt trần 40 giây.

    Có thẻ chương: các dòng trước thẻ nội dung đầu tiên. Thẻ ở dòng 1 là tiêu
    đề mở, mốc chặn là thẻ kế; không có thẻ kế thì tới hết kịch bản. Không có
    thẻ: từ dòng 1 tới clip kế. Một clip trơ: cả kịch bản. Trần 40 giây nằm ở
    ``suggest_kinetic`` (``start < COLD_OPEN_S``), không cắt ở đây.
    """
    headings = [i for i, line in enumerate(lines, 1) if scene_picker._is_heading(str(line))]
    if headings and headings[0] == 1:
        end = headings[1] if len(headings) > 1 else (len(lines) + 1)
    elif headings:
        end = headings[0]
    else:
        end = None
    if end is not None:
        return set(range(1, end))
    starts = _clip_starts(clips)
    if len(starts) >= 2 and starts[1] > starts[0]:
        return set(range(1, starts[1]))
    if len(starts) == 1:
        return set(range(1, len(lines) + 1))
    return set()


def _fits(line: int, used: set[int]) -> bool:
    return all(abs(line - other) >= 2 for other in used)


def _best(group: list[dict[str, Any]], ideal: float, used: set[int], seed: str) -> dict[str, Any] | None:
    opts = [c for c in group if _fits(c["line"], used)]
    if not opts:
        return None
    return min(opts, key=lambda c: tie_key(seed, c["line"], ideal))


def suggest_kinetic(row: dict[str, Any], hand_lines: set[int],
                    spans: list[tuple[float, float]]) -> list[dict[str, Any]]:
    """3–6 gợi ý opt-in. Không liền nhau, không đè visual ghi tay, không vào 40s đầu của cold open."""
    if isinstance(row.get("kinetic_suggest"), list):
        return row["kinetic_suggest"]
    lines = _lines(row)
    seed = str(row.get("id") or "")
    cold = _cold_lines(lines, row.get("clips"))
    visuals = row.get("visuals") or {}
    groups: dict[str, list[dict[str, Any]]] = {name: [] for name in _KINETIC_ORDER}
    for index, line in enumerate(lines, 1):
        if index in hand_lines or scene_picker._is_heading(str(line)):
            continue
        start = spans[index - 1][0] if index - 1 < len(spans) else 0.0
        if index in cold and start < COLD_OPEN_S:
            continue
        hit = _preset_for(str(line))
        if hit is None:
            continue
        preset, reason = hit
        item = {"line": index, "preset": preset, "host": KINETIC_HOST[preset],
                "opt_in": True, "ly_do": reason}
        current = visuals.get(str(index))
        if isinstance(current, dict) and current.get("type"):
            item["visual_hien_co"] = current.get("type")
        groups[preset].append(item)
    cands = [c for name in _KINETIC_ORDER for c in groups[name]]
    if not cands:
        return []
    cands.sort(key=lambda c: c["line"])
    lo, hi = cands[0]["line"], cands[-1]["line"]
    picked: list[dict[str, Any]] = []
    used: set[int] = set()
    present = [name for name in _KINETIC_ORDER if groups[name]]
    for i, name in enumerate(present):
        if len(picked) >= KINETIC_MAX:
            break
        ideal = lo + (hi - lo) * ((i + 0.5) / max(1, len(present)))
        choice = _best(groups[name], ideal, used, seed)
        if choice is None:
            continue
        picked.append(choice)
        used.add(choice["line"])
    rest = [c for c in cands if c["line"] not in used]
    while len(picked) < KINETIC_MAX and rest:
        ideal = lo + (hi - lo) * ((len(picked) + 0.5) / KINETIC_MAX)
        choice = _best(rest, ideal, used, seed)
        if choice is None:
            break
        picked.append(choice)
        used.add(choice["line"])
        rest = [c for c in rest if c["line"] not in used]
    picked.sort(key=lambda c: c["line"])
    return picked


def format_visual_mix(row: dict[str, Any]) -> str:
    counts = visual_counts(row)
    n = sum(counts.values())
    parts = [f"{k} {v} ({round(100 * v / n) if n else 0}%)" for k, v in counts.items()]
    mix = row.get("_ask_mix") or {}
    kin = row.get("kinetic_suggest") or []
    body = ", ".join(parts) if parts else "(trống)"
    return (f"visuals {row.get('id')}: {body} | n={n} | trần ask {mix.get('cap', 0)} "
            f"(1/120s={mix.get('time_cap', 0)}, ≤25%={mix.get('frac_cap', 0)}, "
            f"đổi {mix.get('converted', 0)}) | kinetic_suggest {len(kin)} | "
            f"~{float(mix.get('clock_s') or 0):.0f}s")


def _finish_mix(row: dict[str, Any], decisions: dict[str, dict[str, Any]], hand_lines: set[int],
                forbidden: set[str], ok: set[str]) -> None:
    spans, clock = line_spans(row)
    _apply_ask_cap(row, decisions, hand_lines, spans, forbidden, ok)
    if "kinetic_suggest" not in row:
        row["kinetic_suggest"] = suggest_kinetic(row, hand_lines, spans)
    mix = row.get("_ask_mix") or {}
    mix["clock"] = clock
    print(format_visual_mix(row) + f" ({clock})")
    kin_n = len(row.get("kinetic_suggest") or [])
    if kin_n < KINETIC_MIN and float(mix.get("clock_s") or 0) >= ASK_WINDOW_S:
        print(f"!! kinetic: {row.get('id')} có {kin_n} gợi ý, mục tiêu {KINETIC_MIN}–{KINETIC_MAX}")
    row.pop("_ask_mix", None)


def apply_to_new_long_plan(plan: Any, channel: str, dest: Path | str | None = None) -> Any:
    """Làm giàu plan Long mới. File đích đã có thì giữ nguyên từng byte.

    ``dest`` trống: trả bản enrich, không ghi đĩa.
    ``dest`` chưa có: enrich rồi ghi. Một row được ghi thành list một phần tử,
    đúng khuôn ``pilot_plan_build``. List thì ghi nguyên list đã enrich.
    ``dest`` đã có: trả JSON trên đĩa, không gọi enrich, không ghi.
    ``dest`` là ``str`` hoặc ``Path`` đều được.
    """
    dest = Path(dest) if dest is not None else None
    if dest is not None and dest.is_file():
        return json.loads(dest.read_text(encoding="utf-8"))
    enriched = enrich_long_plan(plan, channel)
    if dest is None:
        return enriched
    payload = enriched if isinstance(plan, list) else [enriched]
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return payload


def _is_overlay(spec: Any) -> bool:
    """Cùng luật với hyperframes_bridge.is_overlay_visual; import trễ để giữ thư viện nhẹ."""
    import hyperframes_bridge as HB  # noqa: PLC0415
    return HB.is_overlay_visual(spec)


def enrich_long_plan(plan: Any, channel: str) -> Any:
    """Return enriched copy; accept a plan row or a list of rows."""
    rows = plan if isinstance(plan, list) else [plan]
    out = copy.deepcopy(rows)
    scene_profile = scene_picker.load_profile(None, channel)
    motion_profile = motion_picker.load_profile(None, channel)
    catalog = scene_picker.load_json(scene_picker.CATALOG)
    forbidden = set(scene_profile.get("forbidden_types") or [])

    for row in out:
        if not isinstance(row, dict) or row.get("lane") != "long":
            continue
        visuals = row.setdefault("visuals", {})
        media = row.setdefault("media", {})
        hand_lines = _keys(visuals)
        edited = hand_lines | _keys(media)
        scene_input = copy.deepcopy(row)
        # Selectors regard these keys as occupied. Retain editor selections and
        # temporarily expose only the remaining lines to scene_picker.
        scene_input["visuals"] = {k: v for k, v in visuals.items() if str(k).isdigit() and int(k) in edited}
        scene_input["media"] = {k: v for k, v in media.items() if str(k).isdigit() and int(k) in edited}
        scene_patch, scene_log = scene_picker.choose(scene_input, scene_profile, catalog)

        # Motion picker consumes media entries. Add newly picked scenes to a
        # temporary media view before merging visuals, so they are not blocked.
        motion_input = copy.deepcopy(row)
        motion_media = copy.deepcopy(media)
        for key, spec in scene_patch.items():
            if int(key) not in edited:
                motion_media[key] = {"kind": "image", "scene": spec}
        motion_input["media"] = motion_media
        motion_input["visuals"] = copy.deepcopy(visuals)
        motion_patch, motion_log = motion_picker.choose(motion_input, motion_profile)

        decisions: dict[str, dict[str, Any]] = {}
        scene_by_line = {d["sentence"]: d for d in scene_log["decisions"]}
        motion_by_line: dict[int, list[dict[str, Any]]] = {}
        for decision in motion_log:
            motion_by_line.setdefault(int(decision["sentence"]), []).append(decision)

        for index in range(1, _line_count(row) + 1):
            key = str(index)
            if index in edited:
                decisions[key] = {"source": "editor"}
                continue
            if key not in scene_patch:
                continue
            scene_decision = scene_by_line.get(index, {})
            if scene_patch[key].get("type") in forbidden:
                raise AssertionError(f"scene picker returned forbidden type on line {index}")
            motion_decision = motion_by_line.get(index, [])
            motion_payload = motion_patch.get(key, {})
            motion_choice = motion_payload.get("preset") or (motion_decision[0].get("preset") if motion_decision else None)
            motion_reason = "; ".join(dict.fromkeys(d.get("reason", "") for d in motion_decision if d.get("reason")))
            decisions[key] = {
                "scene": {"picked": scene_patch[key], "ly_do": scene_decision.get("reason", ""),
                          "ung_vien": scene_decision.get("candidates", [])},
                "motion": {"preset": motion_choice, "ly_do": motion_reason,
                           **({"picked": motion_payload} if motion_payload else {})},
                "source": "picker",
            }
            placed = visuals.setdefault(key, scene_patch[key])
            # Sơ đồ không phủ (overlay) chiếm trọn câu: renderer cấm câu vừa có media vừa nằm trong sơ đồ
            # (hyperframes_bridge.apply_visuals). Preset chuyển động khi ấy chỉ ghi ở scene_decision.
            if key in motion_patch and _is_overlay(placed):
                for field, value in motion_patch[key].items():
                    media.setdefault(key, {}).setdefault(field, value)
        _finish_mix(row, decisions, hand_lines, forbidden, {x["type"] for x in catalog["scenes"]
                    if (x.get("qa") or {}).get("trang_thai") == "dat"})
        row["scene_decision"] = decisions
    return out if isinstance(plan, list) else out[0]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan", type=Path)
    ap.add_argument("--channel", choices=("bud", "fs"), required=True)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    original = json.loads(args.plan.read_text(encoding="utf-8"))
    enriched = enrich_long_plan(original, args.channel)
    if args.write:
        args.plan.write_text(json.dumps(enriched, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = enriched if isinstance(enriched, list) else [enriched]
    selected = sum(1 for row in rows if isinstance(row, dict) for v in (row.get("scene_decision") or {}).values() if v.get("source") == "picker")
    kin = sum(len(row.get("kinetic_suggest") or []) for row in rows if isinstance(row, dict))
    print(json.dumps({"rows": len(rows), "filled_lines": selected, "kinetic_suggest": kin,
                      "mode": "write" if args.write else "dry-run"}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
