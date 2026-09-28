"""Chạy S8 (Toàn vẹn văn bản) + tín hiệu chẩn đoán bằng code trên script của
Baseline snapshot (ticket 20, D78–D81). Lệnh thủ công; kết quả là DỮ LIỆU cho
calibration sau này -- không điểm, không ngưỡng, không đạt/không đạt.

Quy tắc:
- Chỉ dùng script có `script_provenance` ∈ {exact, revision, rendered};
  `source_only` (đoạn trích nguồn) TUYỆT ĐỐI không được đo như script đã đăng.
- n tính THEO TỪNG TIÊU CHÍ (chỉ đếm Short chấm được tiêu chí đó), không có
  một n chung.
- `rendered` (text .srt sau normalize: `**` đã bị bóc, số thành chữ) không
  kiểm được markup sót -> loại khỏi n của tiêu chí đó kèm lý do; mật độ số
  của `rendered` cũng không đo được (số đã thành chữ).
- Báo cáo tách theo Domain và theo `script_provenance`.

    uv run python baseline_script_measures.py --snapshot <baseline_snapshot_*.json>
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import script_diagnostics
import script_integrity

REPORT_VERSION = 1
MEASURABLE_PROVENANCE = ("exact", "revision", "rendered")
DEFAULT_OUT_DIR = Path(__file__).parent / ".scratch" / "improve-short-content-pipeline" / "baseline" / "measures"

CRITERIA = ("repeated_sentence", "leftover_markup", "truncated", "first_sentence_words", "sentence_words",
            "density_numbers", "density_names", "density_terms", "fingerprint")
# Tiêu chí không đo được trên text rendered (.srt đã normalize), kèm lý do.
RENDERED_EXCLUDED = {
    "leftover_markup": "rendered: `**` và markup đã bị bóc trước khi render, không kiểm được markup sót",
    "density_numbers": "rendered: số đã được normalize thành chữ, không đếm được token số",
}


def measure_script(script: str, provenance: str) -> dict:
    """Số đo của một script (hàm thuần). Tiêu chí không đo được -> None + lý do."""
    integ = script_integrity.check(script)
    diag = script_diagnostics.diagnostics(script)
    kinds = Counter(f.reason_code for f in integ.findings)
    values = {
        "repeated_sentence": kinds.get(script_integrity.SCR_REPEATED_SENTENCE, 0) > 0,
        "leftover_markup": kinds.get(script_integrity.SCR_LEFTOVER_MARKUP, 0) > 0,
        "truncated": kinds.get(script_integrity.SCR_TRUNCATED, 0) > 0,
        "first_sentence_words": diag["first_sentence_words"],
        "sentence_words": diag["sentence_words"],
        "density_numbers": [d["numbers"] for d in diag["density"]],
        "density_names": [d["names"] for d in diag["density"]],
        "density_terms": [d["terms"] for d in diag["density"]],
        "fingerprint": diag["fingerprint"],
    }
    excluded = {}
    if provenance == "rendered":
        for crit, reason in RENDERED_EXCLUDED.items():
            values[crit] = None
            excluded[crit] = reason
    return {"values": values, "excluded": excluded}


def _dist(nums: list[float]) -> dict:
    if not nums:
        return {"n_values": 0}
    out = {"n_values": len(nums), "median": statistics.median(nums), "min": min(nums), "max": max(nums)}
    if len(nums) > 1:
        q = statistics.quantiles(nums, n=4, method="inclusive")
        out.update(p25=q[0], p75=q[2])
    return out


def summarize(items: list[dict]) -> dict:
    """items: [{"values", "excluded"}] -> n và phân bố theo TỪNG tiêu chí."""
    out = {}
    for crit in CRITERIA:
        measured = [it["values"][crit] for it in items if it["values"].get(crit) is not None]
        excluded = Counter(it["excluded"][crit] for it in items if crit in it["excluded"])
        entry = {"n": len(measured)}
        if excluded:
            entry["excluded"] = dict(excluded)
        if crit in ("repeated_sentence", "leftover_markup", "truncated"):
            entry["count_true"] = sum(1 for v in measured if v)
            entry["share_true"] = round(entry["count_true"] / len(measured), 4) if measured else None
        elif crit == "first_sentence_words":
            entry["distribution"] = _dist(measured)
        elif crit == "fingerprint":
            entry["top"] = [{"fingerprint": fp, "count": c} for fp, c in Counter(measured).most_common(10)]
        else:  # danh sách theo câu -> phân bố trên mọi câu
            entry["distribution_per_sentence"] = _dist([x for per_short in measured for x in per_short])
        out[crit] = entry
    return out


def build_report(snapshot: dict, *, created_at: str | None = None) -> dict:
    measured, skipped = [], Counter()
    for row in snapshot.get("rows", []):
        prov = row.get("script_provenance")
        if prov not in MEASURABLE_PROVENANCE or not isinstance(row.get("script"), str) or not row["script"].strip():
            skipped[prov or "unknown"] += 1
            continue
        m = measure_script(row["script"], prov)
        measured.append({"domain": row.get("domain"), "provenance": prov, **m})

    def groups(key_fn):
        buckets: dict[str, list[dict]] = {}
        for it in measured:
            buckets.setdefault(key_fn(it), []).append(it)
        return {k: summarize(v) for k, v in sorted(buckets.items())}

    return {
        "report_version": REPORT_VERSION,
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        "snapshot_created_at": snapshot.get("created_at"),
        "diagnostics_version": script_diagnostics.DIAGNOSTICS_VERSION,
        "note": "Chỉ số đo -- không điểm, không ngưỡng, không đạt/không đạt. n theo TỪNG tiêu chí.",
        "excluded_rows": dict(skipped),
        "by_domain": groups(lambda it: str(it["domain"])),
        "by_domain_and_provenance": groups(lambda it: f"{it['domain']}|{it['provenance']}"),
        "by_provenance": groups(lambda it: it["provenance"]),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Chạy S8 + chẩn đoán code trên script của Baseline snapshot.")
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR))
    args = ap.parse_args(argv)
    snapshot = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    report = build_report(snapshot)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"baseline_script_measures_v{REPORT_VERSION}_{datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"-> {out}")
    print(json.dumps({d: {c: v["n"] for c, v in s.items()} for d, s in report["by_domain"].items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
