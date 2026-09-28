"""Baseline snapshot của các Short đã đăng + xuất tập gán nhãn (ticket 10,
D20/D35/D37/D41, D78–D81).

Chỉ ĐỌC file người vận hành đặt vào baseline raw (gitignore) -- KHÔNG tự kết
nối Hub DB (credential do người vận hành giữ). Phần ghép là hàm thuần
(`build_snapshot`), phần lệnh chỉ đọc/ghi file.

Bố cục `--raw-dir` (mặc định `.scratch/improve-short-content-pipeline/baseline/raw/`),
mọi phần đều tuỳ chọn -- thiếu phần nào thì trường tương ứng ghi "thiếu" kèm lý do:

    registry/<topic>/registry.json      copy output/shorts/<topic>/registry.json (máy production)
    hub/videos.json                     export bảng video: [{youtube_video_id, duration_seconds, published_at, ...}]
    hub/video_daily_metric.json         export: [{youtube_video_id, date, views, average_view_percentage, ...}]
    hub/content_revisions.json          export content_revision: [{youtube_video_id, audio_script, created_at}]
    youtube_analytics_*.json            output của baseline_analytics_fetch.py (ticket 09)
    rendered/**/<NN>_short.srt (+ .json) .srt/manifest lấy từ Drive (lời đã đọc sau normalize)
    staged/<topic>/*_Short.txt          file staged (đoạn trích nguồn, KHÔNG phải script đã đăng)
    known_violations.json               {"<video_id|registry_key>": {"cr1": n, "safety": n, "source": "..."}}

Ledger đăng (`creator_specs/WEEKLY_PUBLISHING_LEDGER_v1.json`) và PR-5
(`creator_specs/PR5_AUDIT_REPORT_v1.md`, số vi phạm CR-1 theo registry key) là
dữ liệu đã commit, đọc thẳng.

script_provenance (D78): exact (registry final_script) -> revision (Hub
audio_script; verified chỉ khi là bản mới nhất KHÔNG sau thời điểm đăng) ->
rendered (.srt) -> source_only -> missing. `source_only` KHÔNG BAO GIỜ nằm
trong trường script đã đăng (D79) -- chỉ ở `source_reference`.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent
DEFAULT_RAW_DIR = REPO_ROOT / ".scratch" / "improve-short-content-pipeline" / "baseline" / "raw"
DEFAULT_OUT_DIR = REPO_ROOT / ".scratch" / "improve-short-content-pipeline" / "baseline" / "snapshots"
LEDGER_PATH = REPO_ROOT / "creator_specs" / "WEEKLY_PUBLISHING_LEDGER_v1.json"
PR5_PATH = REPO_ROOT / "creator_specs" / "PR5_AUDIT_REPORT_v1.md"
SNAPSHOT_VERSION = 1

TOPIC_TO_DOMAIN = {"Phật giáo": "BUD", "Phong Thủy": "FS", "Hình Sự": "CL"}
LEDGER_PREFIX_TO_DOMAIN = {"BUD_": "BUD", "FS_": "FS", "CL_": "CL"}

# Tiền tố key registry -> (generator, category). Thứ tự: tiền tố dài trước.
KEY_PREFIXES = [
    ("CONGIAPTHANG", "zodiac_month_short_generator", "grounded_data"),
    ("CONGIAP", "zodiac_short_generator", "grounded_data"),
    ("LICH", "lich_hoang_dao_generator", "grounded_data"),
    ("THAN", "twelve_gods_short_generator", "grounded_data"),
    ("MENHNGAY", "element_luck_short_generator", "grounded_data"),
    ("MENH_", "element_color_short_generator", "grounded_data"),
    ("KINHDICH_", "iching_short_generator", "interpretation"),
    ("CUNGHD_", "western_zodiac_short_generator", "creative_astrology"),
    ("KIENTHUC_", "educational_short_generator", "educational"),
    ("CHUYENKE_", "storytelling_short_generator", "storytelling"),
    ("TRENDING_", "trending_short_generator", "trending"),
    ("ANDAXU_", "criminal_law_short_generator", "storytelling"),
    ("CLGATE_", "cl_case_orchestrator", "storytelling"),
]

PROVENANCE_ORDER = ("exact", "revision", "rendered", "source_only", "missing")


def missing(reason: str) -> dict:
    """Giá trị thiếu có lý do -- KHÔNG BAO GIỜ nhầm với 0."""
    return {"missing": True, "reason": reason}


def is_missing(value) -> bool:
    return isinstance(value, dict) and value.get("missing") is True


# --------------------------------------------------------------------------
# Đọc dữ liệu (lệnh)
# --------------------------------------------------------------------------

def _read_json(path: Path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _pick(row: dict, *names):
    for n in names:
        if n in row and row[n] not in (None, ""):
            return row[n]
    return None


def parse_pr5(text: str) -> dict:
    """{registry_key: {"cr1": subtotal, "generator": ..., "source": "PR-5"}} từ report PR-5."""
    out, current = {}, None
    for line in text.splitlines():
        m = re.match(r"^### #\d+ `([^`]+)` \(([^)]+)\)", line)
        if m:
            current = m.group(1)
            out[current] = {"cr1": None, "generator": m.group(2), "source": "PR-5"}
            continue
        # Mọi dạng dòng tổng trong report: "**Subtotal: 5**", "**Subtotal: 3 confirmed,
        # 0 disputed**", "**Subtotal (a/d): 0.**" -- lấy số đầu tiên sau dấu ":".
        m = re.match(r"^\*\*Subtotal[^:*]*:\s*(\d+)", line)
        if m and current:
            out[current]["cr1"] = int(m.group(1))
            current = None
    return out


def read_srt_text(path: Path) -> str:
    lines = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.isdigit() or "-->" in line:
            continue
        lines.append(line)
    return " ".join(lines)


def load_raw(raw_dir: Path, ledger_path: Path = LEDGER_PATH, pr5_path: Path = PR5_PATH) -> dict:
    raw_dir = Path(raw_dir)
    registries = {}
    for reg in sorted((raw_dir / "registry").glob("*/registry.json")):
        registries[reg.parent.name] = _read_json(reg, {}) or {}
    analytics = {}
    for f in sorted(raw_dir.glob("youtube_analytics_*.json")):
        for v in (_read_json(f, {}) or {}).get("videos", []):
            analytics[v.get("youtube_video_id")] = v  # file sau (mới hơn) ghi đè
    rendered = {}
    for srt in sorted((raw_dir / "rendered").rglob("*_short.srt")) if (raw_dir / "rendered").exists() else []:
        manifest = _read_json(srt.with_suffix(".json"), None)
        rendered[(srt.parent.name, srt.name.split("_")[0])] = {
            "text": read_srt_text(srt), "path": str(srt.relative_to(raw_dir)), "manifest": manifest is not None}
    staged = {}
    for txt in sorted((raw_dir / "staged").rglob("*_Short.txt")) if (raw_dir / "staged").exists() else []:
        staged[txt.name[: -len("_Short.txt")]] = txt.read_text(encoding="utf-8")
    return {
        "registries": registries,
        "hub_videos": _read_json(raw_dir / "hub" / "videos.json", None),
        "hub_metrics": _read_json(raw_dir / "hub" / "video_daily_metric.json", None),
        "hub_revisions": _read_json(raw_dir / "hub" / "content_revisions.json", None),
        "analytics": analytics,
        "rendered": rendered,
        "staged": staged,
        "known_violations": _read_json(raw_dir / "known_violations.json", {}) or {},
        "ledger": (_read_json(ledger_path, {}) or {}).get("items", []),
        "pr5": parse_pr5(Path(pr5_path).read_text(encoding="utf-8")) if Path(pr5_path).exists() else {},
    }


# --------------------------------------------------------------------------
# Ghép (hàm thuần)
# --------------------------------------------------------------------------

def _generator_and_category(key: str | None):
    for prefix, gen, cat in KEY_PREFIXES:
        if key and key.startswith(prefix):
            return gen, cat
    return None, None


def _parse_ts(value):
    if not value:
        return None
    try:
        ts = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    # Chuỗi không có múi giờ (vd export Hub) coi là UTC: không so sánh lẫn naive/aware.
    return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)


def resolve_script(entry: dict | None, video_id: str | None, publish_at, revisions: list | None,
                   rendered: dict, staged: dict) -> dict:
    """Thứ bậc provenance D78. Trả {script, script_provenance, verified,
    source_reference, script_missing_reason}."""
    out = {"script": None, "script_provenance": "missing", "verified": False, "source_reference": None,
           "script_missing_reason": None}
    key = (entry or {}).get("key")
    episode = (entry or {}).get("episode")
    if episode and episode in staged:
        out["source_reference"] = {"kind": "source_only", "text": staged[episode]}
    final_script = (entry or {}).get("final_script")
    if isinstance(final_script, str) and final_script.strip():
        return {**out, "script": final_script, "script_provenance": "exact", "verified": True}
    if revisions is not None and video_id:
        revs = [r for r in revisions if _pick(r, "youtube_video_id", "youtubeVideoId", "video_id") == video_id
                and isinstance(_pick(r, "audio_script", "audioScript"), str)]
        if revs:
            publish_ts = _parse_ts(publish_at)
            before = [r for r in revs if publish_ts and _parse_ts(_pick(r, "created_at", "createdAt"))
                      and _parse_ts(_pick(r, "created_at", "createdAt")) <= publish_ts]
            chosen = max(before or revs, key=lambda r: str(_pick(r, "created_at", "createdAt") or ""))
            return {**out, "script": _pick(chosen, "audio_script", "audioScript"), "script_provenance": "revision",
                    "verified": bool(before)}
    if episode and entry and entry.get("segment_index") is not None:
        rend = rendered.get((episode, f"{int(entry['segment_index']):02d}"))
        if rend:
            return {**out, "script": rend["text"], "script_provenance": "rendered", "verified": rend["manifest"]}
    if out["source_reference"] is not None:
        return {**out, "script_provenance": "source_only",
                "script_missing_reason": "chỉ có đoạn trích staged (source_only) -- không phải script đã đăng (D79)"}
    return {**out, "script_missing_reason": "không có registry final_script, revision Hub, .srt hay file staged"
            if key or video_id else "không có registry entry"}


def _metrics(video_id: str | None, hub_metrics: list | None) -> dict:
    if hub_metrics is None:
        return {"views": missing("chưa có export video_daily_metric"),
                "average_view_percentage": missing("chưa có export video_daily_metric")}
    rows = [r for r in hub_metrics if _pick(r, "youtube_video_id", "youtubeVideoId", "video_id") == video_id]
    if not rows:
        return {"views": missing("video không có dòng metric nào"),
                "average_view_percentage": missing("video không có dòng metric nào")}
    views = [int(_pick(r, "views") or 0) for r in rows]
    pct = [(v, float(_pick(r, "average_view_percentage", "averageViewPercentage")))
           for v, r in zip(views, rows) if _pick(r, "average_view_percentage", "averageViewPercentage") is not None]
    total = sum(views)
    if not pct:
        avp = missing("metric không có average_view_percentage")
    elif sum(v for v, _ in pct) > 0:
        avp = sum(v * p for v, p in pct) / sum(v for v, _ in pct)  # trung bình theo views
    else:
        avp = missing("tổng views = 0, không tính được average view %")
    return {"views": total, "average_view_percentage": avp}


def _analytics_field(video_id, analytics: dict, name: str):
    if not analytics:
        return missing("chưa chạy baseline_analytics_fetch (ticket 09)")
    row = analytics.get(video_id)
    if row is None:
        return missing("video không có trong output analytics")
    part = row.get(name) or {}
    if part.get("status") == "ok":
        return part.get("data")
    return missing(f"{part.get('status')}: {part.get('reason')}")


def build_snapshot(raw: dict, *, created_at: str | None = None) -> dict:
    """Ghép mọi nguồn thành snapshot (hàm thuần)."""
    ledger_by_vid = {i.get("youtube_video_id"): i for i in raw["ledger"] if i.get("youtube_video_id")}
    rows, seen = [], set()
    status_counts: dict[str, dict] = {}

    for topic, registry in raw["registries"].items():
        domain = TOPIC_TO_DOMAIN.get(topic)
        counts = status_counts.setdefault(domain or topic, {})
        for key, entry in registry.items():
            counts[entry.get("status") or "unknown"] = counts.get(entry.get("status") or "unknown", 0) + 1
            vid = entry.get("video_id")
            if not vid:
                continue  # chưa đăng
            seen.add(vid)
            rows.append(_row(domain, key, entry, vid, ledger_by_vid.get(vid), raw))

    for vid, item in ledger_by_vid.items():
        if vid in seen:
            continue
        domain = next((d for p, d in LEDGER_PREFIX_TO_DOMAIN.items() if item.get("content_id", "").startswith(p)), None)
        rows.append(_row(domain, None, None, vid, item, raw))

    return {
        "snapshot_version": SNAPSHOT_VERSION,
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        "sources": {"registry_topics": sorted(raw["registries"]), "hub_videos": raw["hub_videos"] is not None,
                    "hub_metrics": raw["hub_metrics"] is not None, "hub_revisions": raw["hub_revisions"] is not None,
                    "analytics_videos": len(raw["analytics"]), "rendered_srt": len(raw["rendered"]),
                    "staged_files": len(raw["staged"]), "ledger_items": len(raw["ledger"]),
                    "pr5_keys": len(raw["pr5"])},
        "rows": rows,
        "stats": domain_stats(rows, status_counts),
    }


def _row(domain, key, entry, vid, ledger_item, raw) -> dict:
    generator, category = _generator_and_category(key)
    publish_at = (entry or {}).get("publish_at") or (ledger_item or {}).get("final_publish_datetime_utc")
    script = resolve_script(entry, vid, publish_at, raw["hub_revisions"], raw["rendered"], raw["staged"])
    known = raw["known_violations"].get(vid) or (raw["known_violations"].get(key) if key else None)
    pr5 = raw["pr5"].get(key) if key else None
    hook = (entry or {}).get("hook_score") if entry and "hook_score" in entry else missing(
        "registry không có hook_score" if entry else "không có registry entry")
    return {
        "youtube_video_id": vid,
        "registry_key": key,
        "domain": domain or missing("không xác định được Domain"),
        "category": category or missing("không suy ra được category từ key"),
        "generator": generator or missing("không suy ra được generator từ key"),
        "ledger_content_id": (ledger_item or {}).get("content_id"),
        "ledger_category": (ledger_item or {}).get("category"),
        "publish_at": publish_at or missing("không có publish_at"),
        **script,
        "hook_score": hook,
        **_metrics(vid, raw["hub_metrics"]),
        "retention_curve": _analytics_field(vid, raw["analytics"], "retention_curve"),
        "traffic_sources": _analytics_field(vid, raw["analytics"], "traffic_sources"),
        "known_cr1_violations": _cr1(pr5, known),
        "known_safety_violations": (known or {}).get("safety", missing("không có dữ liệu vi phạm Safety")),
        "violations_source": (pr5 or {}).get("source") or (known or {}).get("source"),
    }


def _cr1(pr5: dict | None, known: dict | None):
    if pr5 is not None:
        return pr5["cr1"] if pr5.get("cr1") is not None else missing("PR-5 có key này nhưng không đọc được dòng Subtotal")
    if known and "cr1" in known:
        return known["cr1"]
    return missing("không có trong PR-5/known_violations")


def _quantiles(values: list[float]) -> dict:
    """Median và phân vị (không chỉ trung bình, D20)."""
    if not values:
        return {"n": 0}
    if len(values) == 1:
        v = values[0]
        return {"n": 1, "median": v, "p10": v, "p25": v, "p75": v, "p90": v, "min": v, "max": v}
    deciles = statistics.quantiles(values, n=10, method="inclusive")
    quartiles = statistics.quantiles(values, n=4, method="inclusive")
    return {"n": len(values), "median": statistics.median(values), "p10": deciles[0], "p25": quartiles[0],
            "p75": quartiles[2], "p90": deciles[8], "min": min(values), "max": max(values)}


def domain_stats(rows: list[dict], status_counts: dict) -> dict:
    stats = {}
    for domain in sorted({r["domain"] for r in rows if isinstance(r["domain"], str)} | set(status_counts)):
        drows = [r for r in rows if r["domain"] == domain]
        avp = [r["average_view_percentage"] for r in drows if not is_missing(r["average_view_percentage"])]
        counts = status_counts.get(domain, {})
        decided = sum(counts.values())
        stats[domain] = {
            "published": len(drows),
            "average_view_percentage": _quantiles(avp),
            "script_provenance": {p: sum(1 for r in drows if r["script_provenance"] == p) for p in PROVENANCE_ORDER},
            "script_verified": sum(1 for r in drows if r["verified"]),
            "registry_status_counts": counts or missing("không có registry cho Domain này"),
            "publish_rate": (counts.get("uploaded", 0) / decided) if decided else missing("không có registry"),
        }
    return stats


# --------------------------------------------------------------------------
# Tập gán nhãn (D37)
# --------------------------------------------------------------------------

LABEL_SCRIPT_PROVENANCE = ("exact", "revision", "rendered")


def _label_item(row: dict) -> dict:
    """Gán nhãn mù: script + provenance, KHÔNG kèm metrics hay điểm cũ."""
    return {"youtube_video_id": row["youtube_video_id"], "registry_key": row["registry_key"], "domain": row["domain"],
            "category": row["category"], "script": row["script"], "script_provenance": row["script_provenance"],
            "verified": row["verified"]}


def labeling_set(snapshot: dict, *, bud_anchor_pcts=(31.0, 25.0), n_fs=10, n_bud=10) -> dict:
    """FS 10 từ PR-5; BUD 10 gồm bắt buộc 2 video retention 31%/25% + 8 trải
    đều theo average view %; CL = mọi CL đã đăng. Chỉ Short có script đã đăng
    thật (exact/revision/rendered) -- source_only không bao giờ vào tập nhãn."""
    rows = [r for r in snapshot["rows"] if r["script_provenance"] in LABEL_SCRIPT_PROVENANCE]
    notes = []
    fs = sorted((r for r in rows if r["domain"] == "FS" and r["violations_source"] == "PR-5"),
                key=lambda r: r["registry_key"] or "")[:n_fs]
    if len(fs) < n_fs:
        notes.append(f"FS: chỉ {len(fs)}/{n_fs} Short PR-5 có script đã đăng")
    bud_all = [r for r in rows if r["domain"] == "BUD" and not is_missing(r["average_view_percentage"])]
    anchors = []
    for target in bud_anchor_pcts:
        cand = [r for r in bud_all if round(r["average_view_percentage"]) == round(target) and r not in anchors]
        if cand:
            anchors.append(cand[0])
        else:
            notes.append(f"BUD: không tìm thấy video average view % ≈ {target}")
    rest = sorted((r for r in bud_all if r not in anchors), key=lambda r: r["average_view_percentage"])
    k = max(n_bud - len(anchors), 0)
    if len(rest) <= k:
        spread = rest
    elif k == 1:
        spread = [rest[len(rest) // 2]]
    else:
        # trải đều theo average view %: lấy các vị trí cách đều trên danh sách đã sắp xếp
        spread = [rest[round(i * (len(rest) - 1) / (k - 1))] for i in range(k)] if k else []
    bud = anchors + spread
    if len(bud) < n_bud:
        notes.append(f"BUD: chỉ {len(bud)}/{n_bud} Short có script đã đăng + average view %")
    cl = [r for r in rows if r["domain"] == "CL"]
    return {"created_from_snapshot": snapshot["created_at"], "notes": notes,
            "FS": [_label_item(r) for r in fs], "BUD": [_label_item(r) for r in bud],
            "CL": [_label_item(r) for r in cl]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Dựng Baseline snapshot + tập gán nhãn từ baseline raw (chỉ đọc file).")
    ap.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR))
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--ledger", default=str(LEDGER_PATH))
    ap.add_argument("--pr5", default=str(PR5_PATH))
    args = ap.parse_args(argv)
    raw = load_raw(Path(args.raw_dir), ledger_path=Path(args.ledger), pr5_path=Path(args.pr5))
    snap = build_snapshot(raw)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    (out_dir / f"baseline_snapshot_v{SNAPSHOT_VERSION}_{stamp}.json").write_text(
        json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / f"labeling_set_{stamp}.json").write_text(
        json.dumps(labeling_set(snap), ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(snap["stats"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
