#!/usr/bin/env python3
"""Đánh giá luật dừng CK từ bản xuất analytics, không gọi API."""
import argparse
import json
import re
import statistics
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

VN = timezone(timedelta(hours=7))


def date_range(value):
    try:
        a, b = (date.fromisoformat(s) for s in value.split(":"))
        if a > b:
            raise ValueError("ngày đầu sau ngày cuối")
        return a, b
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Khoảng ngày không hợp lệ: {value}") from exc


def duration_seconds(value):
    match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value or "")
    if not match or not any(match.groups()):
        return None
    h, m, s = (int(x or 0) for x in match.groups())
    return h * 3600 + m * 60 + s


def assess(videos, daily, days):
    results = []
    seen = {}
    for video in videos:
        ident = video["id"]
        if ident in seen:
            if any(seen[ident].get(key) != video.get(key) for key in ("published_at", "privacy", "duration")):
                raise ValueError(f"Conflicting metadata for video {ident}")
            continue
        seen[ident] = video
        duration = duration_seconds(video.get("duration"))
        if video.get("privacy") != "public" or duration is None or duration > 180:
            continue
        published = datetime.fromisoformat(video["published_at"].replace("Z", "+00:00"))
        if published.tzinfo is None:
            raise ValueError("published_at thiếu múi giờ: " + video["id"])
        start = published.astimezone(VN).date()
        wanted = [start + timedelta(days=i) for i in range(days)]
        item = daily.get(video["id"], {})
        rows = item.get("rows", []) if item.get("ok") is True else []
        indexed = {}
        for row in rows:
            day = date.fromisoformat(row["day"])
            if day in indexed:
                raise ValueError(f"Ngày trùng cho {video['id']}: {day}")
            views = row["views"]
            if not isinstance(views, int) or isinstance(views, bool) or views < 0:
                raise ValueError(f"Lượt xem không hợp lệ: {video['id']} {day}")
            indexed[day] = views
        last = max(indexed, default=None)
        if last is None or last < wanted[-1]:
            status, views = "chưa đủ tuổi", None
        elif any(day not in indexed for day in wanted):
            status, views = "thiếu ngày dữ liệu", None
        else:
            status, views = "đủ dữ liệu", sum(indexed[day] for day in wanted)
        results.append(dict(id=video["id"], title=video.get("title", ""), published=start, status=status, views=views))
    return results


def median(items):
    values = [x["views"] for x in items if x["views"] is not None]
    return statistics.median(values) if values else None


def decision(items, threshold):
    values = [x for x in items if x["views"] is not None]
    if len(values) < 20:
        return "chưa đủ dữ liệu"
    return "DỪNG: quay về 2–3/ngày" if median(values) < threshold else "GIỮ 5/ngày"


def fmt(value):
    return "—" if value is None else f"{value:g}"


def safe(value):
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def report(results, trial, base, base_median, ratio, days, source):
    subset = lambda interval: [x for x in results if interval[0] <= x["published"] <= interval[1]]
    t, b = subset(trial), subset(base)
    threshold = base_median * ratio
    lines = ["# Đánh giá luật dừng 5 Short/ngày của CK", "", f"Nguồn: `{source}`. Ngày đăng quy đổi UTC+7; cửa sổ gồm ngày đăng và {days - 1} ngày tiếp theo.", "", f"**Kết luận: {decision(t, threshold)}.** Ngưỡng chính xác: {fmt(threshold)} = {fmt(ratio)} × {fmt(base_median)} lượt xem; so sánh nghiêm ngặt dưới ngưỡng.", "", "| Nhóm theo ngày đăng | Tổng Short công khai | Đủ dữ liệu | Chưa đủ tuổi | Thiếu ngày dữ liệu | Median lượt xem |", "|---|---:|---:|---:|---:|---:|"]
    for name, interval, group in [("Thử", trial, t), ("Gốc", base, b)]:
        counts = [sum(x["status"] == s for x in group) for s in ("đủ dữ liệu", "chưa đủ tuổi", "thiếu ngày dữ liệu")]
        lines.append(f"| {name} ({interval[0]}–{interval[1]}) | {len(group)} | {counts[0]} | {counts[1]} | {counts[2]} | {fmt(median(group))} |")
    bm = median(b)
    if bm is None:
        lines.append("\nKhông tính được median nhóm gốc để so với mức đã ghi.")
    else:
        diff = bm - base_median
        pct = abs(diff) / base_median * 100 if base_median else None
        lines.append(f"\nMedian nhóm gốc lệch {fmt(diff)} lượt so với {fmt(base_median)}" + (f" ({fmt(pct)}%); " if pct is not None else "; ") + ("lệch nhiều (từ 10% trở lên)." if pct is not None and pct >= 10 else "chưa vượt mức cảnh báo 10%."))
    lines += ["", "## Theo tuần đăng", "", "Tuần từ thứ Hai đến Chủ nhật; tổng chỉ gồm các Short đủ dữ liệu trong hai khoảng gốc và thử, không phải tổng lượt xem toàn kênh.", "", "| Tuần | Short đủ dữ liệu | Lượt xem trong cửa sổ | Short chưa tính |", "|---|---:|---:|---:|"]
    weeks = defaultdict(list)
    for x in results:
        if (base[0] <= x["published"] <= base[1]) or (trial[0] <= x["published"] <= trial[1]):
            weeks[x["published"] - timedelta(days=x["published"].weekday())].append(x)
    for week, group in sorted(weeks.items()):
        good = [x for x in group if x["views"] is not None]
        lines.append(f"| {week}–{week + timedelta(days=6)} | {len(good)} | {sum(x['views'] for x in good)} | {len(group)-len(good)} |")
    good = sorted((x for x in t if x["views"] is not None), key=lambda x: (x["views"], x["id"]))
    for label, ranking in [("Top 5", list(reversed(good[-5:]))), ("Bottom 5", good[:5])]:
        lines += ["", f"## {label} nhóm thử", "", f"| Tiêu đề | Lượt xem {days} ngày |", "|---|---:|"]
        lines.extend(f"| {safe(x['title'])} | {x['views']} |" for x in ranking)
        if not ranking:
            lines.append("| Không có dữ liệu đủ điều kiện | — |")
    lines += ["", "## Short chưa được tính", "", "| Nhóm | Ngày đăng VN | Tiêu đề | Trạng thái |", "|---|---|---|---|"]
    excluded = [(name, x) for name, group in (("Gốc", b), ("Thử", t)) for x in group if x["views"] is None]
    lines.extend(f"| {name} | {x['published']} | {safe(x['title'])} | {x['status']} |" for name, x in excluded)
    if not excluded:
        lines.append("| — | — | Không có | — |")
    lines += ["", "## Giới hạn dữ liệu", "", "- Chỉ tính video công khai dài tối đa 3 phút theo metadata; các ID lặp được tính một lần.", "- Ngày cuối của từng video chưa tới cuối cửa sổ hoặc không có bản ghi: chưa đủ tuổi. Nếu đã tới cuối cửa sổ nhưng thiếu ngày trong cửa sổ: thiếu ngày dữ liệu. Không suy ngày thiếu bằng 0; video này bị loại khỏi median và tổng.", "- Nhãn ngày trong video_x_day được dùng trực tiếp như ngày VN; bản xuất không chứng minh múi giờ của các ngày này. Nếu Analytics dùng múi giờ khác, không thể quy đổi chính xác từ dữ liệu tổng hợp theo ngày; cần kiểm tra trước khi ra quyết định.", "- Tổng theo tuần là tổng cửa sổ đầu của Short theo tuần đăng, không phải lượt xem phát sinh trong tuần; tuần có thể không đầy đủ. Không dùng tổng d7/d28 để bù ngày thiếu.", "- Dữ liệu có thể bị trễ hoặc thay đổi sau lần kéo. Áp dụng ngưỡng không chứng minh quan hệ nhân quả.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/analytics/CK/183"))
    parser.add_argument("--trial", type=date_range, default=date_range("2026-10-29:2026-11-11"))
    parser.add_argument("--base", type=date_range, default=date_range("2026-10-20:2026-10-26"))
    parser.add_argument("--base-median", type=float, default=322)
    parser.add_argument("--ratio", type=float, default=0.6)
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--out", type=Path, default=Path("docs/pm/2026-11-12-ck-stop-rule.md"))
    args = parser.parse_args()
    if args.days < 1 or not 0 <= args.ratio or not 0 <= args.base_median:
        parser.error("days phải dương; ratio và base-median phải không âm")
    with (args.data / "videos.json").open(encoding="utf-8") as f:
        videos = json.load(f)
    with (args.data / "video_x_day.json").open(encoding="utf-8") as f:
        daily = json.load(f)
    text = report(assess(videos, daily, args.days), args.trial, args.base, args.base_median, args.ratio, args.days, args.data.as_posix())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"Đã ghi {args.out}")


if __name__ == "__main__":
    main()
