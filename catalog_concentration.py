"""S13 -- Concentration signal của Opening pattern theo Domain (ticket 19,
D71/D72/D73/D86/D87). CHỈ ADVISORY.

Sau khi một Short qua S7, đọc các Quality record `layer: script` PASS gần nhất
của cùng Domain (window tính theo SỐ LƯỢNG record, kích thước là tham số --
không phải ngưỡng), tính tỷ trọng theo fingerprint mở đầu, và ghi một record
`layer: catalog`.

Record catalog KHÔNG có Gate status, cờ đạt/không đạt, ngưỡng, whitelist hay
blacklist; không có đường nào từ signal tới Gate status hay tới prompt của
writer. Mô tả Opening pattern tự do (từ evaluator, nếu có) được giữ nguyên để
chuẩn hoá sau khi có baseline -- chưa có taxonomy.

Đọc/ghi qua kho Quality record của Spec 1 (không store mới, không khoá Unix).
"""
from __future__ import annotations

import uuid
from collections import Counter
from datetime import datetime, timezone

import content_quality_gate as cqg

LAYER = "catalog"
SCHEMA_VERSION = 1
DEFAULT_WINDOW = 30  # tham số đo, KHÔNG phải ngưỡng


def recent_script_records(domain: str, window: int) -> list[dict]:
    if window < 1:
        raise ValueError("window phải >= 1")
    passed = [r for r in cqg.read_records(domain) if r.get("layer") == "script" and r.get("gate_status") == cqg.PASS
              and r.get("fingerprint")]
    return passed[-window:]


def concentration(records: list[dict]) -> list[dict]:
    counts = Counter(r["fingerprint"] for r in records)
    total = sum(counts.values())
    return [{"fingerprint": fp, "count": c, "share": round(c / total, 4)} for fp, c in counts.most_common()]


def build_record(script_record: dict, *, window: int = DEFAULT_WINDOW) -> dict:
    domain = script_record["domain"]
    recent = recent_script_records(domain, window)
    shares = concentration(recent)
    own = next((s for s in shares if s["fingerprint"] == script_record.get("fingerprint")), None)
    return {
        "schema_version": SCHEMA_VERSION,
        "quality_record_id": uuid.uuid4().hex,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "layer": LAYER,
        "domain": domain,
        "identity": script_record.get("identity"),
        "advisory": True,
        "script_quality_record_id": script_record.get("quality_record_id"),
        "window": {"size": window, "records_in_window": len(recent)},
        "fingerprint": script_record.get("fingerprint"),
        "this_fingerprint_share": own["share"] if own else None,
        "fingerprint_shares": shares,
        "opening_pattern_descriptions": [
            {"script_quality_record_id": r.get("quality_record_id"),
             "description": (r.get("opening_pattern") or {}).get("description")}
            for r in recent if (r.get("opening_pattern") or {}).get("description")
        ],
    }


def record_after_script(script_record: dict, *, window: int = DEFAULT_WINDOW) -> dict | None:
    """Ghi record catalog sau một record Script PASS. Advisory: mọi lỗi được
    nuốt và trả None -- KHÔNG BAO GIỜ ảnh hưởng Gate hay luồng sinh."""
    try:
        rec = build_record(script_record, window=window)
        cqg.append_record(rec)
        return rec
    except Exception:  # noqa: BLE001
        return None
