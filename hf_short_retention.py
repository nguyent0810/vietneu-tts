"""Read-only Shorts audience-retention helpers for YouTube Analytics API."""
from __future__ import annotations

from collections.abc import Callable, Mapping


def normalize_curve(rows: list[list[float]]) -> list[dict[str, float]]:
    """Convert API [elapsedVideoTimeRatio, audienceWatchRatio] rows."""
    points = sorted((float(r[0]), float(r[1])) for r in rows if len(r) >= 2)
    return [{"elapsed": x, "audience": y} for x, y in points]


def steepest_drop(curve: list[dict[str, float]]) -> dict | None:
    """Largest adjacent decline, expressed as percentage points of audience."""
    candidates = []
    for left, right in zip(curve, curve[1:]):
        drop = left["audience"] - right["audience"]
        candidates.append({"from": left["elapsed"], "to": right["elapsed"],
                           "drop": drop, "drop_percentage_points": drop * 100})
    return max(candidates, key=lambda x: x["drop"], default=None)


def fetch_curve(query: Callable[[str, Mapping], dict], credentials: str,
                video_id: str, start: str, end: str) -> list[dict[str, float]]:
    report = query(credentials, {
        "ids": "channel==MINE", "startDate": start, "endDate": end,
        "dimensions": "elapsedVideoTimeRatio", "metrics": "audienceWatchRatio",
        "filters": f"video=={video_id}",
    })
    return normalize_curve(report.get("rows", []))


def analyze_video(query: Callable[[str, Mapping], dict], credentials: str,
                  video_id: str, start: str, end: str) -> dict:
    curve = fetch_curve(query, credentials, video_id, start, end)
    return {"video_id": video_id, "start": start, "end": end,
            "points": curve, "steepest_drop": steepest_drop(curve)}
