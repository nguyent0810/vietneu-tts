#!/usr/bin/env python3
"""Chọn motion preset cho ảnh tĩnh. Độc lập với scene_picker (ticket #52).

Đọc hồ sơ kênh, khoá `motion`. Không đọc và không ghi `assets` hay `canh`.
Chống lặp liền nhau và trong cửa sổ K. Tất định: không random, không giờ hệ thống.
Ảnh giữ lâu hơn hold_split_s được chia 2–3 shot tại ranh giới câu.
Không có focus thì không chọn pan_focus / highlight.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHANNELS = ROOT / "library" / "channels"
KNOWN = ("slow_zoom", "pan_focus", "push_detail", "parallax", "highlight", "reveal")
STILL = {"image", "local", "commons", "museum", "ext", "openverse", "asset"}
HOLD_MAX_S = 22.0
_NUM = ("scale_from", "scale_to", "pan", "min_s", "max_s")


def load_yaml_or_json(path: Path):
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        import yaml
        return yaml.safe_load(raw)


def load_profile(path: str | None, channel: str) -> dict:
    p = Path(path) if path else CHANNELS / f"{channel}.yaml"
    data = load_yaml_or_json(p)
    if "motion" not in data:
        raise ValueError(f"profile thiếu khối motion: {p}")
    return data["motion"]


def _focus_ok(focus) -> bool:
    if not isinstance(focus, (list, tuple)) or len(focus) != 4:
        return False
    try:
        x, y, w, h = (float(v) for v in focus)
    except (TypeError, ValueError):
        return False
    return 0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1 and x + w <= 1.001 and y + h <= 1.001


def _segments(row: dict) -> tuple[list[dict], str]:
    lines = row.get("lines")
    if isinstance(lines, list) and lines and isinstance(lines[0], dict):
        out = []
        for i, ln in enumerate(lines):
            start = float(ln["start"]) if ln.get("start") is not None else i * 4.0
            end = float(ln["end"]) if ln.get("end") is not None else start + 4.0
            out.append({**ln, "sentence_id": int(ln.get("sentence_id") or i + 1), "start": start, "end": end})
        return out, "timings"
    script = list(row.get("script") or [])
    return [
        {"sentence_id": i + 1, "start": i * 4.0, "end": (i + 1) * 4.0, "text": t}
        for i, t in enumerate(script)
    ], "estimate"


def _holds(lines: list[dict], media_ids: set[int], blocked: set[int]) -> dict[int, int]:
    """sentence_id có ảnh -> chỉ số dòng cuối ảnh còn hiện."""
    out = {}
    for i, ln in enumerate(lines):
        sid = ln["sentence_id"]
        if sid not in media_ids:
            continue
        k = i
        start = ln["start"]
        while k + 1 < len(lines):
            nxt = lines[k + 1]
            if (nxt["sentence_id"] in media_ids or nxt["sentence_id"] in blocked
                    or nxt.get("heading") or nxt.get("visual") or nxt.get("visual_cont")
                    or (nxt.get("figure") or {}).get("type", "none") not in (None, "none")
                    or nxt["end"] - start > HOLD_MAX_S):
                break
            k += 1
        out[sid] = k
    return out


def _cuts(lines: list[dict], i0: int, i1: int, min_shot: float) -> list[int]:
    t0, t1 = lines[i0]["start"], lines[i1]["end"]
    found = []
    for j in range(i0 + 1, i1 + 1):
        t = lines[j]["start"]
        if t - t0 >= min_shot and t1 - t >= min_shot:
            found.append(j)
    return found


def _sample(cuts: list[int], need: int) -> list[int]:
    if need <= 0 or not cuts:
        return []
    if len(cuts) <= need:
        return list(cuts)
    picked = []
    for i in range(need):
        idx = int((i + 0.5) * len(cuts) / need)
        idx = min(len(cuts) - 1, max(0, idx))
        if not picked or cuts[idx] != picked[-1]:
            picked.append(cuts[idx])
    return picked


def _payload(at: int, name: str, spec: dict, focus) -> dict:
    item = {"at": at, "preset": name}
    if focus:
        item["focus"] = [round(float(v), 4) for v in focus]
    for key in _NUM:
        if spec.get(key) is not None:
            item[key] = float(spec[key])
    return item


def choose(row: dict, profile: dict) -> tuple[dict, list[dict]]:
    presets = profile.get("presets") or {}
    order = [name for name in presets if name in KNOWN]
    window_k = max(0, int(profile.get("window_k") or 0))
    hold_split = float(profile.get("hold_split_s") or 8)
    max_shots = max(1, min(3, int(profile.get("max_shots") or 3)))
    min_shot = float(profile.get("min_shot_s") or 2.5)
    lines, clock = _segments(row)
    media = {int(k): v for k, v in (row.get("media") or {}).items() if isinstance(v, dict)}
    blocked = {int(k) for k in (row.get("visuals") or {})}
    holds = _holds(lines, set(media), blocked)
    counts: dict[str, int] = {}
    recent: list[str] = []
    prev = None
    patch: dict[str, dict] = {}
    log: list[dict] = []

    def pool(dur: float, has_focus: bool, n_shots: int, block_prev: bool, block_window: bool):
        cands, notes = [], []
        for name in order:
            spec = presets[name]
            why = []
            if spec.get("needs_focus") and not has_focus:
                why.append("không có focus")
            if dur + 1e-9 < float(spec.get("min_s") or 0):
                why.append("ngắn hơn min_s")
            if n_shots > 1 and name == "parallax":
                why.append("parallax chiếm cả khoảng giữ")
            if block_prev and name == prev:
                why.append("trùng liền trước")
            if block_window and window_k and name in recent[-window_k:]:
                why.append("trùng trong cửa sổ")
            if why:
                notes.append({"preset": name, "eligible": False, "reason": ", ".join(why)})
            else:
                notes.append({"preset": name, "eligible": True, "reason": "đạt"})
                cands.append(name)
        return cands, notes

    for i, ln in enumerate(lines):
        sid = ln["sentence_id"]
        spec = media.get(sid)
        if not spec:
            continue
        kind = (spec.get("kind") or "video").lower()
        if kind not in STILL:
            log.append({"sentence": sid, "preset": None, "reason": "không phải ảnh tĩnh", "focus": False})
            continue
        if spec.get("preset") or spec.get("shots"):
            log.append({"sentence": sid, "preset": spec.get("preset"), "reason": "plan đã ghi preset", "focus": _focus_ok(spec.get("focus"))})
            continue
        end_i = holds.get(sid, i)
        hold_s = lines[end_i]["end"] - ln["start"]
        focus = spec.get("focus") if _focus_ok(spec.get("focus")) else None
        cuts = _cuts(lines, i, end_i, min_shot) if hold_s > hold_split else []
        n_shots = 1
        if cuts and hold_s > hold_split:
            n_shots = 3 if hold_s >= min_shot * 3 and len(cuts) >= 2 else 2
            n_shots = min(n_shots, max_shots)
        chosen_idx = [i]
        if n_shots > 1:
            chosen_idx += _sample(cuts, n_shots - 1)
            chosen_idx = sorted(set(chosen_idx))[:max_shots]
        shots = []
        for n, a in enumerate(chosen_idx):
            if n + 1 < len(chosen_idx):
                dur = lines[chosen_idx[n + 1]]["start"] - lines[a]["start"]
            else:
                dur = lines[end_i]["end"] - lines[a]["start"]
            notes = []
            picked = None
            why = "không có preset đủ điều kiện"
            for block_prev, block_window, tag in (
                (True, True, "đủ cửa sổ"),
                (True, False, "nới cửa sổ"),
                (False, False, "nới cả liền trước"),
            ):
                cands, notes = pool(dur, bool(focus), len(chosen_idx), block_prev, block_window)
                if cands:
                    picked = min(cands, key=lambda name: (counts.get(name, 0), order.index(name)))
                    why = f"{tag}; ít dùng nhất theo thứ tự hồ sơ"
                    break
            entry = {
                "sentence": sid, "at": lines[a]["sentence_id"], "preset": picked, "reason": why,
                "focus": bool(focus), "hold_s": round(hold_s, 3), "shot_s": round(dur, 3),
                "shot_index": n + 1, "shot_count": len(chosen_idx), "timeline": clock,
                "candidates": notes,
            }
            log.append(entry)
            if not picked:
                continue
            shots.append(_payload(lines[a]["sentence_id"], picked, presets[picked], focus))
            counts[picked] = counts.get(picked, 0) + 1
            recent.append(picked)
            prev = picked
        if shots:
            patch[str(sid)] = {"preset": shots[0]["preset"], "shots": shots}
            if focus:
                patch[str(sid)]["focus"] = shots[0]["focus"]
    return patch, log


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--id")
    ap.add_argument("--profile")
    ap.add_argument("--channel")
    ap.add_argument("--log")
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    data = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    row = data
    if isinstance(data, list):
        row = next((x for x in data if isinstance(x, dict) and str(x.get("id")) == str(args.id)), None)
        if row is None:
            raise SystemExit(f"plan row id not found: {args.id}")
    channel = args.channel or str(row.get("series") or "fs")
    profile = load_profile(args.profile, channel)
    patch, decisions = choose(row, profile)
    if args.log:
        Path(args.log).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in decisions), encoding="utf-8")
    if args.out:
        Path(args.out).write_text(json.dumps(patch, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"quyet_dinh": len(decisions), "anh": len(patch)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
