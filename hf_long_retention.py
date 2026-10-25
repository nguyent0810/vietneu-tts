"""Đo giữ chân Long FS/BUD đã công khai. Chỉ đọc Analytics + Data API.

Theo V2 (motion/stier/monitor.py, variety.minute_retention / suggested_share):
  * % còn xem = audienceWatchRatio của mốc elapsedVideoTimeRatio GẦN NHẤT, không nội suy.
  * % đề xuất = view RELATED_VIDEO / tổng view insightTrafficSourceType.
Khác V2: chờ đủ 3 ngày lịch Việt Nam (Analytics trễ), thêm mốc 25% và 50%,
so với trung vị 5 Long mới nhất cùng kênh, ghi sổ append theo ngày đo.
Cùng một ngày đo + cùng kênh thì thay snapshot đó; ngày khác giữ nguyên.

    .venv/bin/python hf_long_retention.py fs
    .venv/bin/python hf_long_retention.py bud --json

Không đọc nội dung credential. Không dùng kênh Hình Sự.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "output" / "cl_staging" / "long" / "retention_ledger.json"
UPLOADED = ROOT / "output" / "cl_staging" / "long" / "uploaded.json"
CHANNELS = {
    "fs": ".youtube_channels/phong_thuy.json",
    "bud": ".youtube_channels/phat_giao.json",
}
PREFIX = {"fs": "L_fs_", "bud": "L_bud_"}
MIN_AGE_DAYS = 3
MEDIAN_N = 5
PT = ZoneInfo("America/Los_Angeles")
VN = ZoneInfo("Asia/Ho_Chi_Minh")
_DUR = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")
_SECRET = re.compile(r"(?i)(access_token|refresh_token|client_secret|client_id|Bearer)\s*[\"'=:\s]+\S+")
METRIC_KEYS = (
    "views",
    "average_view_duration_s",
    "average_view_percentage",
    "ret_min1",
    "ret_min2",
    "ret_25",
    "ret_50",
    "suggested_pct",
)


def credentials_for(channel: str) -> Path:
    if channel not in CHANNELS or "hinh_su" in CHANNELS[channel]:
        raise ValueError("chỉ đo kênh fs hoặc bud")
    return ROOT / CHANNELS[channel]


def ids_for(uploaded: dict, channel: str) -> list[tuple[str, str]]:
    prefix = PREFIX[channel]
    out = []
    for rid, vid in uploaded.items():
        if isinstance(rid, str) and rid.startswith(prefix) and isinstance(vid, str) and vid:
            out.append((rid, vid))
    out.sort()
    return out


def parse_duration(iso: str) -> int:
    m = _DUR.match(iso or "")
    if not m:
        return 0
    return int(m[1] or 0) * 3600 + int(m[2] or 0) * 60 + int(m[3] or 0)


def parse_utc(raw: str) -> datetime:
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


def age_days(published: datetime, now: datetime) -> int:
    """Số ngày lịch Việt Nam từ ngày lên sóng tới ngày đo. Đủ đo khi >= 3."""
    return (now.astimezone(VN).date() - published.astimezone(VN).date()).days


def analytics_window(published: datetime, now: datetime) -> tuple[str, str]:
    """startDate lùi 1 ngày UTC như V2. endDate là ngày giờ Thái Bình Dương
    vì Analytics từ chối ngày tương lai so với múi đó."""
    start = published.astimezone(timezone.utc).date() - timedelta(days=1)
    end = now.astimezone(PT).date()
    if start > end:
        start = end
    return start.isoformat(), end.isoformat()


def as_dicts(report: dict | None) -> list[dict]:
    if not report:
        return []
    headers = [h["name"] for h in report.get("columnHeaders") or []]
    return [dict(zip(headers, row)) for row in report.get("rows") or []]


def _r1(value) -> float:
    return float(round(float(value), 1))


def watch_pct(curve: list[dict], dur_s: float, *, at_sec: float | None = None, at_ratio: float | None = None) -> float | None:
    """% còn xem (0–100+, 1 số lẻ). None nếu không có đường, không có độ dài,
    hoặc mốc phút nằm sau hết video. Hoà khoảng cách thì lấy mốc sớm hơn."""
    if not curve or not dur_s or dur_s <= 0:
        return None
    if at_sec is not None:
        if at_sec > dur_s:
            return None
        target = at_sec / dur_s
    elif at_ratio is not None:
        target = at_ratio
    else:
        raise ValueError("cần at_sec hoặc at_ratio")
    ordered = sorted(curve, key=lambda c: float(c["elapsedVideoTimeRatio"]))
    hit = min(ordered, key=lambda c: abs(float(c["elapsedVideoTimeRatio"]) - target))
    return _r1(float(hit["audienceWatchRatio"]) * 100)


def _views(value) -> int:
    return int(round(float(value)))


def suggested_share(sources: list[dict]) -> float | None:
    """% view từ RELATED_VIDEO. 0 nếu có view mà không có đề xuất. None nếu chưa có số."""
    if not sources:
        return None
    total = sum(_views(s["views"]) for s in sources)
    if not total:
        return None
    related = next((_views(s["views"]) for s in sources if s["insightTrafficSourceType"] == "RELATED_VIDEO"), 0)
    return _r1(related / total * 100)


def safe_err(msg: str) -> str:
    return _SECRET.sub(r"\1=…", msg).replace("\n", " ")[:180]


def _median(values: list) -> float | None:
    if not values:
        return None
    return _r1(statistics.median(values))


def median5(rows: list[dict]) -> dict:
    """Trung vị tối đa 5 Long mới nhất (published_at, rồi rid). Gồm cả video đang so."""
    cohort = sorted(rows, key=lambda r: (r["published_at"], r["rid"]), reverse=True)[:MEDIAN_N]
    out: dict = {"n": len(cohort), "rids": [r["rid"] for r in cohort]}
    for key in METRIC_KEYS:
        out[key] = _median([r[key] for r in cohort if r.get(key) is not None])
    return out


def deltas(row: dict, med: dict) -> dict:
    out = {}
    for key in METRIC_KEYS:
        left, right = row.get(key), med.get(key)
        out[key] = None if left is None or right is None else _r1(float(left) - float(right))
    return out


def _cell(value, digits=1, signed=False) -> str:
    if value is None:
        return "—"
    return f"{float(value):+.{digits}f}" if signed else f"{float(value):.{digits}f}"


def _title(text: str, limit: int = 40) -> str:
    text = " ".join((text or "").replace("|", "/").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _clock(seconds: int) -> str:
    seconds = int(seconds or 0)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def _minutes(seconds) -> float | None:
    if seconds is None:
        return None
    return _r1(float(seconds) / 60)


def render_table(result: dict) -> str:
    med = result["median5"]
    lines = [
        f"{result['channel']} — đo {result['measured_on']} — {len(result['rows'])} Long đủ {MIN_AGE_DAYS} ngày, bỏ qua {len(result['skipped'])}",
        (
            f"Trung vị {med['n']} Long gần nhất ({', '.join(med['rids']) or '—'}): "
            f"view {_cell(med.get('views'))} | "
            f"AVD {_cell(_minutes(med.get('average_view_duration_s')))} phút | "
            f"% xem {_cell(med.get('average_view_percentage'))} | "
            f"phút 1 {_cell(med.get('ret_min1'))}% | "
            f"phút 2 {_cell(med.get('ret_min2'))}% | "
            f"25% {_cell(med.get('ret_25'))}% | "
            f"50% {_cell(med.get('ret_50'))}% | "
            f"đề xuất {_cell(med.get('suggested_pct'))}%"
        ),
        f"Δ = video − trung vị {med['n']} Long mới nhất cùng kênh.",
        "",
        "| Long | Tên | Lên sóng | Tuổi | Dài | View | Δview | AVD phút | ΔAVD | % xem | Δ% | Phút 1 | Δ1 | Phút 2 | Δ2 | 25% | Δ25 | 50% | Δ50 | Đề xuất | Δđx |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in result["rows"]:
        vs = row["vs_median5"]
        lines.append(
            "| {rid} | {title} | {day} | {age} | {dur} | {views} | {dviews} | {avd} | {davd} | {pct} | {dpct} | "
            "{p1} | {d1} | {p2} | {d2} | {p25} | {d25} | {p50} | {d50} | {sug} | {dsug} |".format(
                rid=row["rid"],
                title=_title(row["title"]),
                day=row["published_vn"],
                age=row["age_days"],
                dur=_clock(row["duration_s"]),
                views=row["views"] if row["views"] is not None else "—",
                dviews=_cell(vs.get("views"), signed=True),
                avd=_cell(_minutes(row.get("average_view_duration_s"))),
                davd=_cell(_minutes(vs.get("average_view_duration_s")), signed=True),
                pct=_cell(row.get("average_view_percentage")),
                dpct=_cell(vs.get("average_view_percentage"), signed=True),
                p1=_cell(row.get("ret_min1")),
                d1=_cell(vs.get("ret_min1"), signed=True),
                p2=_cell(row.get("ret_min2")),
                d2=_cell(vs.get("ret_min2"), signed=True),
                p25=_cell(row.get("ret_25")),
                d25=_cell(vs.get("ret_25"), signed=True),
                p50=_cell(row.get("ret_50")),
                d50=_cell(vs.get("ret_50"), signed=True),
                sug=_cell(row.get("suggested_pct")),
                dsug=_cell(vs.get("suggested_pct"), signed=True),
            )
        )
    if result["skipped"]:
        lines += ["", "Bỏ qua:"]
        for item in result["skipped"]:
            lines.append(f"- {item['rid']}: {item['reason']}")
    return "\n".join(lines) + "\n"


def load_ledger(path: Path) -> dict:
    if not path.exists():
        return {"snapshots": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"sổ {path.name} không phải JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("snapshots"), list):
        raise RuntimeError(f"sổ {path.name} không có danh sách snapshots")
    return data


def upsert_snapshot(ledger: dict, snap: dict) -> dict:
    kept = [s for s in ledger["snapshots"] if not (s.get("measured_on") == snap["measured_on"] and s.get("channel") == snap["channel"])]
    kept.append(snap)
    kept.sort(key=lambda s: (s.get("measured_on", ""), s.get("channel", "")))
    return {"snapshots": kept}


def save_ledger(path: Path, ledger: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def default_query(credentials_path, params: dict) -> dict:
    import youtube_analytics
    return youtube_analytics._query(credentials_path, params)


def default_catalog(credentials_path, url: str, params: dict) -> dict:
    import youtube_catalog
    return youtube_catalog._get(credentials_path, url, params)


def call_query(query, credentials_path, params: dict, pauses=(1.0, 2.0)):
    """Gọi lại khi Analytics trả 429/5xx. Lỗi khác thì dừng ngay."""
    import youtube_analytics
    last = None
    waits = (*pauses, None)
    for wait in waits:
        try:
            return query(credentials_path, params)
        except youtube_analytics.YouTubeAnalyticsError as exc:
            last = exc
            if wait is None or not any(code in str(exc) for code in ("(429)", "(500)", "(502)", "(503)", "(504)")):
                raise
            time.sleep(wait)
    raise last


def _report(query, cred, *, start: str, end: str, metrics: str, video_id: str, dimensions: str | None = None, pauses=(1.0, 2.0)) -> dict:
    # Đường giữ chân chỉ lọc được một video (ràng buộc API). Không đặt maxResults:
    # bản V2 và hf_shorts_report bỏ trống và nhận đủ các mốc.
    params = {
        "ids": "channel==MINE",
        "startDate": start,
        "endDate": end,
        "metrics": metrics,
        "filters": f"video=={video_id}",
    }
    if dimensions:
        params["dimensions"] = dimensions
    return call_query(query, cred, params, pauses=pauses)


def _metric_row(report: dict) -> dict:
    rows = as_dicts(report)
    return rows[0] if rows else {}


def _build_row(rid: str, video_id: str, item: dict, published: datetime, now: datetime, start: str, end: str, metrics: dict, curve: list[dict], sources: list[dict]) -> dict:
    dur = item["duration_s"]
    views = _views(metrics["views"]) if "views" in metrics and metrics["views"] is not None else None
    avd = _r1(metrics["averageViewDuration"]) if metrics.get("averageViewDuration") is not None else None
    avp = _r1(metrics["averageViewPercentage"]) if metrics.get("averageViewPercentage") is not None else None
    return {
        "rid": rid,
        "video_id": video_id,
        "title": item["title"],
        "published_at": published.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "published_vn": published.astimezone(VN).date().isoformat(),
        "age_days": age_days(published, now),
        "duration_s": dur,
        "window_start": start,
        "window_end": end,
        "views": views,
        "average_view_duration_s": avd,
        "average_view_percentage": avp,
        "ret_min1": watch_pct(curve, dur, at_sec=60),
        "ret_min2": watch_pct(curve, dur, at_sec=120),
        "ret_25": watch_pct(curve, dur, at_ratio=0.25),
        "ret_50": watch_pct(curve, dur, at_ratio=0.50),
        "suggested_pct": suggested_share(sources),
        "curve_n": len(curve),
    }


def _normalize(item: dict) -> dict:
    snippet = item.get("snippet") or {}
    status = item.get("status") or {}
    details = item.get("contentDetails") or {}
    raw = snippet.get("publishedAt")
    return {
        "privacy": status.get("privacyStatus") or "",
        "publish_at": status.get("publishAt") or "",
        "published": parse_utc(raw) if raw else None,
        "title": snippet.get("title") or "",
        "duration_s": parse_duration(details.get("duration") or ""),
    }


def _fetch_meta(catalog, cred: str, video_ids: list[str]) -> dict[str, dict]:
    from youtube_catalog import VIDEOS_URL
    meta = {}
    uniq = list(dict.fromkeys(video_ids))
    for offset in range(0, len(uniq), 50):
        chunk = uniq[offset:offset + 50]
        data = catalog(cred, VIDEOS_URL, {"part": "snippet,contentDetails,status", "id": ",".join(chunk)})
        for item in data.get("items") or []:
            meta[item["id"]] = _normalize(item)
    return meta


def _empty(channel: str, measured_on: str) -> dict:
    return {
        "channel": channel,
        "measured_on": measured_on,
        "min_age_days": MIN_AGE_DAYS,
        "rows": [],
        "skipped": [],
        "median5": {"n": 0, "rids": [], **{key: None for key in METRIC_KEYS}},
    }


def collect(
    channel: str,
    *,
    now: datetime | None = None,
    uploaded: dict | None = None,
    query=None,
    catalog=None,
    ledger_path: Path | None = None,
    write: bool = True,
    pauses=(1.0, 2.0),
) -> dict:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now phải có timezone")
    query = query or default_query
    catalog = catalog or default_catalog
    if uploaded is None:
        uploaded = json.loads(UPLOADED.read_text(encoding="utf-8"))
    cred = str(credentials_for(channel))
    if "hinh_su" in cred:
        raise ValueError("chỉ đo kênh fs hoặc bud")
    measured_on = now.astimezone(VN).date().isoformat()
    pairs = ids_for(uploaded, channel)
    result = _empty(channel, measured_on)
    if not pairs:
        return result
    meta = _fetch_meta(catalog, cred, [vid for _, vid in pairs])
    rows, skipped = [], []
    for rid, video_id in pairs:
        item = meta.get(video_id)
        if item is None:
            skipped.append({"rid": rid, "video_id": video_id, "reason": "không thấy trên YouTube"})
            continue
        if item["privacy"] != "public":
            when = f", hẹn {item['publish_at'][:10]}" if item.get("publish_at") else ""
            skipped.append({"rid": rid, "video_id": video_id, "reason": f"chưa công khai ({item['privacy']}{when})"})
            continue
        published = item["published"]
        if published is None:
            skipped.append({"rid": rid, "video_id": video_id, "reason": "không có ngày lên sóng"})
            continue
        if age_days(published, now) < MIN_AGE_DAYS:
            skipped.append({
                "rid": rid,
                "video_id": video_id,
                "reason": f"chưa đủ {MIN_AGE_DAYS} ngày (lên {published.astimezone(VN).date().isoformat()})",
            })
            continue
        start, end = analytics_window(published, now)
        print(f"đo {rid}", file=sys.stderr, flush=True)
        try:
            metrics_report = _report(query, cred, start=start, end=end, metrics="views,averageViewDuration,averageViewPercentage", video_id=video_id, pauses=pauses)
            curve_report = _report(query, cred, start=start, end=end, metrics="audienceWatchRatio", video_id=video_id, dimensions="elapsedVideoTimeRatio", pauses=pauses)
            source_report = _report(query, cred, start=start, end=end, metrics="views", video_id=video_id, dimensions="insightTrafficSourceType", pauses=pauses)
        except Exception as exc:  # noqa: BLE001 -- một video lỗi không bỏ cả lô; lỗi đã cắt bí mật
            import youtube_analytics
            text = str(exc)
            # 401/403 và lỗi refresh là lỗi cả kênh, không phải một video.
            if not isinstance(exc, youtube_analytics.YouTubeAnalyticsError) or any(
                mark in text for mark in ("(401)", "(403)", "Refresh access_token", "Chưa có credentials")
            ):
                raise
            skipped.append({"rid": rid, "video_id": video_id, "reason": "Analytics lỗi: " + safe_err(text)})
            continue
        if not (metrics_report.get("rows") or curve_report.get("rows") or source_report.get("rows")):
            skipped.append({"rid": rid, "video_id": video_id, "reason": "Analytics chưa có số"})
            continue
        rows.append(_build_row(rid, video_id, item, published, now, start, end, _metric_row(metrics_report), as_dicts(curve_report), as_dicts(source_report)))
    rows.sort(key=lambda r: (r["published_at"], r["rid"]))
    med = median5(rows)
    for row in rows:
        row["vs_median5"] = deltas(row, med)
    skipped.sort(key=lambda item: item["rid"])
    result["rows"] = rows
    result["skipped"] = skipped
    result["median5"] = med
    if write and rows:
        path = ledger_path if ledger_path is not None else LEDGER
        save_ledger(path, upsert_snapshot(load_ledger(path), {
            "measured_on": measured_on,
            "channel": channel,
            "min_age_days": MIN_AGE_DAYS,
            "median5": med,
            "rows": rows,
        }))
    return result


def _ssl() -> None:
    try:
        import certifi
    except ImportError:
        return
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())


def main(argv: list[str] | None = None) -> int:
    _ssl()
    ap = argparse.ArgumentParser(description="Đo giữ chân Long FS hoặc BUD đã công khai >= 3 ngày")
    ap.add_argument("channel", choices=("fs", "bud"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    cred = credentials_for(args.channel)
    if not cred.is_file():
        print(f"LỖI: chưa có credential kênh {args.channel}", file=sys.stderr)
        return 1
    if not UPLOADED.is_file():
        print("LỖI: chưa có uploaded.json của Long", file=sys.stderr)
        return 1
    try:
        result = collect(args.channel)
    except Exception as exc:  # noqa: BLE001
        import youtube_analytics
        import youtube_catalog
        if isinstance(exc, (youtube_analytics.YouTubeAnalyticsError, youtube_analytics.YouTubeAuthError, youtube_catalog.YouTubeCatalogError, RuntimeError, ValueError)):
            print(f"LỖI kênh {args.channel}: {safe_err(str(exc))}", file=sys.stderr)
            return 1
        raise
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_table(result), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
