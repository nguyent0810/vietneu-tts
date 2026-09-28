"""S6 -- Content invariant (ticket 13/15, D67/D83).

Phần Content phải giữ nguyên khi chỉ viết lại Script: Content hook (chi tiết
móc), Claim ledger, thứ tự ý, Payoff, và đoạn trích nguồn nếu Short trích từ
Long. Lưu thành sidecar JSON cạnh file bundle staged:

    <episode>_Short.txt  ->  <episode>_Short.invariant.json

Trường:
- `claim_source` {kind, data}: nguồn claim do CODE ghi (facts của generator,
  fact pack CL, đoạn trích...) -- không qua LLM.
- `source_excerpt`: đoạn trích nguồn nếu có.
- `content_hook`, `idea_order`, `payoff`: mỗi trường {value, derived_by, evidence}
  với derived_by ∈ {"code", "story_plan", "llm"}; chưa có thì nằm trong
  `missing` kèm lý do (không bỏ trống lặng lẽ).
- `versions`, `schema_version`.
"""
from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

SCHEMA_VERSION = 1
DERIVED_BY = frozenset({"code", "story_plan", "llm"})
DERIVED_FIELDS = ("content_hook", "idea_order", "payoff")
NOT_EXTRACTED_YET = "chưa trích (phần LLM làm ở Script evaluator, ticket 17)"


def sidecar_path(bundle_path: str | Path) -> Path:
    bundle_path = Path(bundle_path)
    if not bundle_path.name.endswith("_Short.txt"):
        raise ValueError(f"Không phải file bundle Short: {bundle_path.name}")
    return bundle_path.with_name(bundle_path.name[: -len("_Short.txt")] + "_Short.invariant.json")


def derived(value, derived_by: str, evidence: list | None = None) -> dict:
    if derived_by not in DERIVED_BY:
        raise ValueError(f"derived_by không hợp lệ: {derived_by!r}")
    return {"value": value, "derived_by": derived_by, "evidence": list(evidence or [])}


def build(*, claim_source_kind: str, claim_source_data, source_excerpt: str | None = None,
          content_hook: dict | None = None, idea_order: dict | None = None, payoff: dict | None = None,
          missing_reasons: dict | None = None, versions: dict | None = None) -> dict:
    """Dựng invariant. Trường derived thiếu -> vào `missing` kèm lý do
    (mặc định: chưa trích)."""
    fields = {"content_hook": content_hook, "idea_order": idea_order, "payoff": payoff}
    missing = []
    for name, value in fields.items():
        if value is None:
            missing.append({"field": name, "reason": (missing_reasons or {}).get(name, NOT_EXTRACTED_YET)})
    if claim_source_data is None:
        missing.append({"field": "claim_source", "reason": (missing_reasons or {}).get("claim_source",
                                                                                      "đường sinh không có nguồn claim")})
    return {
        "schema_version": SCHEMA_VERSION,
        "claim_source": None if claim_source_data is None else {"kind": claim_source_kind, "data": claim_source_data},
        "source_excerpt": source_excerpt,
        **{k: v for k, v in fields.items() if v is not None},
        "missing": missing,
        "versions": dict(versions or {}),
    }


def sufficiency(invariant: dict | None) -> tuple[bool, list[str]]:
    """Invariant có đủ để Script rewrite không (D83): cần nguồn claim (claim
    source hoặc đoạn trích) VÀ đủ Content hook, thứ tự ý, Payoff."""
    if not invariant:
        return False, ["không có Content invariant"]
    reasons = []
    if not invariant.get("claim_source") and not invariant.get("source_excerpt"):
        reasons.append("thiếu nguồn claim")
    for name in DERIVED_FIELDS:
        if not invariant.get(name):
            reasons.append(f"thiếu {name}")
    return not reasons, reasons


def write_sidecar(bundle_path: str | Path, invariant: dict) -> Path:
    path = sidecar_path(bundle_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp{uuid.uuid4().hex[:8]}")
    tmp.write_text(json.dumps(invariant, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)
    return path


def read_sidecar(bundle_path: str | Path) -> dict | None:
    path = sidecar_path(bundle_path)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
