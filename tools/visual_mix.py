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
from urllib.parse import urlsplit

VISUAL_MIX_SINCE = "2026-11-18"
TEXT_WARN = 0.10
TEXT_ERROR = 0.10
REPEAT_WARN = 4
REPEAT_ERROR = 6
MIN_IMAGES_PER_MINUTE = 4.0
VIDEO_EXT = (".mp4", ".mov", ".webm", ".m4v", ".mkv", ".avi", ".ogv")
MIN_VIDEO_SHARE = 0.10
VIDEO_FLOOR_MIN_SECONDS = 600
SECONDS_PER_VIDEO_SCENE = 180
TEXT_KINDS = frozenset({"kinetic", "slam", "quote", "question", "date", "counter",
                        "word", "ask", "chữ khoá", "list"})
# These are full-screen text treatments even with decorative photo/video beds.
# An actual keyword overlay on a photo must arrive as a media kind instead.
FULLSCREEN_TEXT_KINDS = frozenset({"kinetic", "slam", "quote", "question"})


def media_motion_kind(spec, *, video_ext=VIDEO_EXT) -> str | None:
    """Clip, panorama or depth parallax, independent of source. Plain push_in/zoom is none."""
    if not isinstance(spec, dict):
        return None
    kind = str(spec.get("kind") or "").lower()
    refs = (spec.get(k) for k in ("path", "url", "file", "src", "ref"))
    if kind in {"clip", "video", "pexels_video", "flow", "pdvideo"} or any(
        os.path.splitext(urlsplit(str(ref)).path)[1].lower() in video_ext for ref in refs if ref
    ):
        return "video"
    if isinstance(spec.get("pan"), dict) or kind == "pano" or spec.get("type") == "pano":
        return "pano"
    # PO 21/11: hiệu ứng chiều sâu (parallax 2.5D) đạt như ảnh lia, miễn có chất nghệ thuật.
    cine = spec.get("cine") if isinstance(spec.get("cine"), dict) else {}
    shots = spec.get("shots") if isinstance(spec.get("shots"), list) else []
    if (spec.get("layout") == "depth" or spec.get("layers") or cine.get("depth") is True
            or cine.get("cam") == "dolly_parallax" or spec.get("preset") == "parallax"
            or any(isinstance(s, dict) and s.get("preset") == "parallax" for s in shots)):
        return "parallax"
    return None


def measure(scenes) -> dict:
    seconds, counts, repeats = Counter(), Counter(), Counter()
    images = set()
    text_seconds = 0.0
    video_seconds, clip_count, pano_count, parallax_count = 0.0, 0, 0, 0
    stock_video_seconds = stock_image_seconds = 0.0
    sources = Counter()
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
        sources[scene.get("source") or "unknown"] += duration
        if scene.get("stock_kind") == "video":
            stock_video_seconds += duration
        elif scene.get("stock_kind") == "image":
            stock_image_seconds += duration
        motion = scene.get("motion") or kind
        if motion in {"video", "clip", "pano", "parallax"}:
            video_seconds += duration
            clip_count += motion in {"video", "clip"}
            pano_count += motion == "pano"
            parallax_count += motion == "parallax"
        refs = {os.path.normpath(str(ref)) if "://" not in str(ref) else str(ref)
                for ref in [scene.get("image"), *(scene.get("images") or [])] if ref}
        images.update(refs)
        for ref in refs:
            repeats[(ref, scene.get("style") or None)] += 1
        if kind in TEXT_KINDS and (kind in FULLSCREEN_TEXT_KINDS or not refs):
            text_seconds += duration
    total = sum(seconds.values())
    return {"seconds": total, "scenes": sum(counts.values()),
            "by_source": {k: {"seconds": v, "share": v / total if total else 0}
                          for k, v in sorted(sources.items())},
            "by_kind": {k: {"seconds": seconds[k], "scenes": counts[k],
                             "share": seconds[k] / total if total else 0.0}
                        for k in sorted(seconds, key=lambda k: (-seconds[k], k))},
            "text_seconds": text_seconds, "text_share": text_seconds / total if total else 0.0,
            "video_seconds": video_seconds, "video_share": video_seconds / total if total else 0.0,
            "stock_video_seconds": stock_video_seconds,
            "stock_video_share": stock_video_seconds / total if total else 0.0,
            "stock_image_seconds": stock_image_seconds,
            "stock_image_share": stock_image_seconds / total if total else 0.0,
            "clip_count": clip_count, "pano_count": pano_count, "parallax_count": parallax_count,
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
    if metrics["seconds"] >= VIDEO_FLOOR_MIN_SECONDS:
        if metrics["video_share"] < MIN_VIDEO_SHARE:
            out.append(("WARN", f"video_share {metrics['video_share']:.2%} clip + pano + parallax (< {MIN_VIDEO_SHARE:.0%})"))
        count = metrics["clip_count"] + metrics["pano_count"] + metrics.get("parallax_count", 0)
        required = math.ceil(metrics["seconds"] / SECONDS_PER_VIDEO_SCENE)
        if count < required:
            out.append(("WARN", f"clip/pano/parallax {count} cảnh / {metrics['seconds'] / 60:.2f} phút "
                        f"(< {required} cảnh; ít nhất 1 cảnh mỗi 3 phút)"))
    return out


def format_table(metrics) -> str:
    rows = ["Loại cảnh | Giây | % thời lượng | Số cảnh", "--- | ---: | ---: | ---:"]
    rows.extend(f"{kind} | {item['seconds']:.2f} | {item['share']:.2%} | {item['scenes']}"
                for kind, item in metrics["by_kind"].items())
    rows.append(f"TỔNG | {metrics['seconds']:.2f} | {'100%' if metrics['seconds'] else '0%'} | {metrics['scenes']}")
    rows.append(f"Chữ {metrics['text_share']:.2%}; ảnh lặp max {metrics['max_repeat']}; "
                f"{metrics['unique_images']} ảnh khác nhau; {metrics['images_per_minute']:.2f} ảnh/phút")
    rows.append(f"Pexels/stock video {metrics.get('stock_video_share', 0):.2%} "
                f"({metrics.get('stock_video_seconds', 0):.2f}s); stock ảnh "
                f"{metrics.get('stock_image_share', 0):.2%} ({metrics.get('stock_image_seconds', 0):.2f}s)")
    rows.append(f"video_share {metrics['video_share']:.2%} ({metrics['video_seconds']:.2f}s clip + pano + parallax); "
                f"clip {metrics['clip_count']} cảnh; pano {metrics['pano_count']} cảnh; "
                f"parallax {metrics.get('parallax_count', 0)} cảnh")
    return "\n".join(rows)
