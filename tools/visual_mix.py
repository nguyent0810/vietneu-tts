"""Engine-independent visual budget, measured in seconds (stdlib only).

Each input is one displayed scene: kind, t0, t1, image, style. Adapters must
merge held scenes and identify static images; clips have image=None. Optional
images lists additional panel images without adding duration to the timeline.
Styles form separate reuse identities; crops/camera/layout never do. Unique
images/minute counts original files, not style variants.
"""
from __future__ import annotations

import math
import os
from collections import Counter

VISUAL_MIX_SINCE = "2026-11-18"
TEXT_WARN = 0.12
TEXT_ERROR = 0.15
REPEAT_WARN = 4
REPEAT_ERROR = 6
MIN_IMAGES_PER_MINUTE = 4.0
TEXT_KINDS = frozenset({"kinetic", "slam", "quote", "question", "date", "counter",
                        "word", "ask", "chữ khoá", "list"})
# These are full-screen text treatments even with decorative photo/video beds.
# An actual keyword overlay on a photo must arrive as a media kind instead.
FULLSCREEN_TEXT_KINDS = frozenset({"kinetic", "slam", "quote", "question"})


def measure(scenes) -> dict:
    seconds, counts, repeats = Counter(), Counter(), Counter()
    images = set()
    text_seconds = 0.0
    for scene in scenes:
        t0, t1 = float(scene["t0"]), float(scene["t1"])
        if not math.isfinite(t0) or not math.isfinite(t1) or t1 < t0:
            raise ValueError(f"visual_mix: invalid interval {t0}..{t1}")
        if t1 == t0:
            continue
        kind = scene.get("kind") or "unknown"
        duration = t1 - t0
        seconds[kind] += duration
        counts[kind] += 1
        refs = {os.path.normpath(str(ref)) if "://" not in str(ref) else str(ref)
                for ref in [scene.get("image"), *(scene.get("images") or [])] if ref}
        images.update(refs)
        for ref in refs:
            repeats[(ref, scene.get("style") or None)] += 1
        if kind in TEXT_KINDS and (kind in FULLSCREEN_TEXT_KINDS or not refs):
            text_seconds += duration
    total = sum(seconds.values())
    return {"seconds": total, "scenes": sum(counts.values()),
            "by_kind": {k: {"seconds": seconds[k], "scenes": counts[k],
                             "share": seconds[k] / total if total else 0.0}
                        for k in sorted(seconds, key=lambda k: (-seconds[k], k))},
            "text_seconds": text_seconds, "text_share": text_seconds / total if total else 0.0,
            "unique_images": len(images),
            "images_per_minute": len(images) * 60 / total if total else 0.0,
            "max_repeat": max(repeats.values(), default=0),
            "repeated_images": [{"image": ref, "style": style, "count": count}
                                for (ref, style), count in repeats.most_common() if count > REPEAT_WARN]}


def issues(metrics, *, is_new, is_long, reason=None) -> list[tuple[str, str]]:
    if not is_new or not is_long:
        return []
    out = []
    share = metrics["text_share"]
    if share > TEXT_WARN:
        level = "ERROR" if share > TEXT_ERROR and not str(reason or "").strip() else "WARN"
        suffix = f"; lý do: {reason}" if str(reason or "").strip() else ""
        out.append((level, f"chữ {share:.2%} thời lượng (cảnh báo > {TEXT_WARN:.0%}, lỗi > {TEXT_ERROR:.0%}){suffix}"))
    repeat = metrics["max_repeat"]
    if repeat > REPEAT_WARN:
        # A text-budget exception never excuses repeated images.
        out.append(("ERROR" if repeat > REPEAT_ERROR else "WARN",
                    f"ảnh tĩnh lặp tối đa {repeat} lần (cảnh báo > {REPEAT_WARN}, lỗi > {REPEAT_ERROR})"))
    if metrics["images_per_minute"] < MIN_IMAGES_PER_MINUTE:
        out.append(("WARN", f"{metrics['images_per_minute']:.2f} ảnh khác nhau/phút (< {MIN_IMAGES_PER_MINUTE:g})"))
    return out


def format_table(metrics) -> str:
    rows = ["Loại cảnh | Giây | % thời lượng | Số cảnh", "--- | ---: | ---: | ---:"]
    rows.extend(f"{kind} | {item['seconds']:.2f} | {item['share']:.2%} | {item['scenes']}"
                for kind, item in metrics["by_kind"].items())
    rows.append(f"TỔNG | {metrics['seconds']:.2f} | {'100%' if metrics['seconds'] else '0%'} | {metrics['scenes']}")
    rows.append(f"Chữ {metrics['text_share']:.2%}; ảnh lặp max {metrics['max_repeat']}; "
                f"{metrics['unique_images']} ảnh khác nhau; {metrics['images_per_minute']:.2f} ảnh/phút")
    return "\n".join(rows)
