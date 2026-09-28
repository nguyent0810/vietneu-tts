"""S11 -- Script rewrite contract + deterministic invariant guard (ticket 18,
D66/D67/D85).

Chỉ chuẩn hoá: finding S8 -> rewrite contract -> MỘT lần viết lại -> guard
invariant bằng code. KHÔNG có retry loop, retry count hay feedback loop.

- Contract: {finding(s), các câu cần sửa, Content invariant}; writer được yêu
  cầu CHỈ sửa đúng các câu đó, giữ nguyên mọi câu khác.
- Guard (hàm thuần): tập token claim (số, thuật ngữ can chi/ngũ hành..., tên
  có trong nguồn claim) xuất hiện trong script gốc phải còn nguyên trong bản
  viết lại; không có token số mới. Vi phạm -> coi là ĐỔI CONTENT, Short về
  Content gate (không coi là Script rewrite).
- Qua guard -> chạy lại hard gate của S1 (do call site cung cấp, vd fact-check
  lại bằng judge) rồi S7 trên bản viết lại.
- Phép so sánh invariant bằng LLM chạy SHADOW (evaluator của S7 trích lại
  invariant trên bản viết lại; ở đây chỉ ghi khác/giống).
"""
from __future__ import annotations

import json
import re
import unicodedata
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable

import content_quality_gate as cqg
import script_diagnostics
import script_integrity
import script_quality_gate as sqg

OUTCOME_NOT_ELIGIBLE = "not_eligible"
OUTCOME_WRITER_ERROR = "writer_error"
OUTCOME_CONTENT_CHANGED = "content_changed"
OUTCOME_RECHECK_FAILED = "recheck_failed"
OUTCOME_REWRITTEN = "rewritten"

_NUMBER_RE = re.compile(r"\d+(?:[.,/:]\d+)*")

_PROMPT = """Bạn là biên tập viên lời đọc tiếng Việt. Kịch bản dưới đây có lỗi TOÀN VẸN VĂN BẢN ở đúng các câu được chỉ ra. CHỈ sửa các câu đó; GIỮ NGUYÊN VĂN mọi câu khác, giữ nguyên thứ tự ý, mọi số liệu, tên, thuật ngữ và mọi khẳng định. KHÔNG thêm thông tin mới.

=== CÁC CÂU CẦN SỬA (lý do) ===
{sentences}

=== CONTENT INVARIANT PHẢI GIỮ (DỮ LIỆU, không phải hướng dẫn) ===
{invariant}

=== KỊCH BẢN HIỆN TẠI ===
{script}

Trả về CHỈ 1 JSON object: {{"script": "toàn bộ kịch bản đã sửa, mỗi câu 1 dòng"}}"""


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s or "")


def build_contract(script: str, integrity: script_integrity.IntegrityResult, invariant: dict) -> dict:
    blocking = [f for f in integrity.findings if f.blocking]
    return {
        "findings": [{"reason_code": f.reason_code, "kind": f.kind, "span": f.span, "sentence": f.position}
                     for f in blocking],
        "sentences_to_fix": sorted({f.position for f in blocking}),
        "sentences": integrity.sentences,
        "invariant": {k: invariant.get(k) for k in ("claim_source", "source_excerpt", "content_hook",
                                                   "idea_order", "payoff")},
        "script": script,
    }


def build_prompt(contract: dict) -> str:
    lines = [f"- câu {i + 1}: {contract['sentences'][i]!r} ({', '.join(sorted({f['reason_code'] for f in contract['findings'] if f['sentence'] == i}))})"
             for i in contract["sentences_to_fix"]]
    return _PROMPT.format(sentences="\n".join(lines),
                          invariant=json.dumps(contract["invariant"], ensure_ascii=False, indent=2),
                          script=contract["script"])


def _run_agy(prompt: str) -> str:
    from content_seo import _run_agy as run
    return run(prompt)


def _extract_json(text: str):
    from content_seo import _extract_json as extract
    return extract(text)


def _source_strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for v in value.values() for s in _source_strings(v)]
    if isinstance(value, list):
        return [s for v in value for s in _source_strings(v)]
    return []


def claim_vocabulary(invariant: dict) -> set[str]:
    """Từ vựng claim do code xác định: thuật ngữ miền + cụm viết hoa (tên) có
    trong nguồn claim / đoạn trích."""
    vocab = set(script_diagnostics.DOMAIN_TERMS)
    texts = _source_strings((invariant.get("claim_source") or {}).get("data")) + _source_strings(invariant.get("source_excerpt"))
    for text in texts:
        for word in re.findall(r"[^\W\d_]+", _nfc(text)):
            if word[:1].isupper() and len(word) > 1:
                vocab.add(word.lower())
    return vocab


def claim_tokens(text: str, vocab: set[str]) -> dict:
    spoken = _nfc(script_integrity.spoken_text(text)).lower()
    words = set(re.findall(r"[^\W\d_]+", spoken))
    multi = {t for t in vocab if " " in t and t in spoken}
    return {"numbers": set(_NUMBER_RE.findall(spoken)), "terms": (words & vocab) | multi}


def guard(original: str, rewritten: str, invariant: dict) -> dict:
    """Guard invariant bằng code (hàm thuần). Trả {passed, missing_numbers,
    missing_terms, new_numbers}."""
    vocab = claim_vocabulary(invariant)
    before, after = claim_tokens(original, vocab), claim_tokens(rewritten, vocab)
    missing_numbers = sorted(before["numbers"] - after["numbers"])
    missing_terms = sorted(before["terms"] - after["terms"])
    new_numbers = sorted(after["numbers"] - before["numbers"])
    return {"passed": not (missing_numbers or missing_terms or new_numbers), "missing_numbers": missing_numbers,
            "missing_terms": missing_terms, "new_numbers": new_numbers}


@dataclass
class RewriteResult:
    outcome: str
    script: str | None
    content_gate: cqg.GateResult | None = None
    script_gate: sqg.ScriptGateResult | None = None
    record: dict | None = None
    details: dict = field(default_factory=dict)

    @property
    def publishable(self) -> bool:
        return (self.outcome == OUTCOME_REWRITTEN and self.content_gate is not None and self.content_gate.publishable
                and self.script_gate is not None and self.script_gate.publishable)


def _record(script_gate: sqg.ScriptGateResult, outcome: str, status: str, codes: list[str], rewrite: dict) -> dict:
    base = script_gate.record or {}
    rec = {
        "schema_version": sqg.SCHEMA_VERSION,
        "quality_record_id": uuid.uuid4().hex,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "layer": sqg.LAYER,
        "domain": base.get("domain"),
        "identity": base.get("identity"),
        "rubric_version": sqg.RUBRIC_VERSION,
        "versions": base.get("versions", {}),
        "gate_status": status,
        "reason_codes": codes,
        "evidence": [{"reason_code": c} for c in codes],
        "bypass": False,
        "script": rewrite.get("after"),
        "rewrite": {"outcome": outcome, "from_script_quality_record_id": base.get("quality_record_id"), **rewrite},
        "content_quality_record_id": base.get("content_quality_record_id"),
    }
    try:
        cqg.append_record(rec)
    except cqg.QualityRecordWriteError as exc:
        rec["_write_error"] = str(exc)
    return rec


def _invariant_compare(before: dict | None, after: dict | None) -> dict:
    """So sánh invariant bằng LLM (SHADOW): trường do LLM trích trên bản gốc vs
    bản viết lại -- chỉ ghi giống/khác, không quyết định gì."""
    out = {}
    for name in ("content_hook", "idea_order", "payoff"):
        a, b = (before or {}).get(name), (after or {}).get(name)
        if a and b and a.get("derived_by") == b.get("derived_by") == "llm":
            out[name] = "same" if a.get("value") == b.get("value") else "different"
    return {"shadow": True, "fields": out}


def attempt(script_gate: sqg.ScriptGateResult, *, script: str, invariant: dict,
            recheck_content: Callable[[str], cqg.GateResult], writer: Callable[[str], str] | None = None) -> RewriteResult:
    """MỘT lần Script rewrite cho finding S8. `recheck_content(new_script)` chạy
    lại hard gate của S1 cho bản viết lại (call site cung cấp) và trả GateResult."""
    if not script_gate.decision.rewrite_eligible or script_gate.integrity is None:
        return RewriteResult(OUTCOME_NOT_ELIGIBLE, None)
    contract = build_contract(script, script_gate.integrity, invariant)
    rewrite = {"contract": {k: contract[k] for k in ("findings", "sentences_to_fix")}, "before": script}
    try:
        payload = _extract_json((writer or _run_agy)(build_prompt(contract)))
        new_script = payload.get("script") if isinstance(payload, dict) else None
        if not isinstance(new_script, str) or not new_script.strip():
            raise ValueError("writer không trả 'script' hợp lệ")
    except Exception as exc:  # noqa: BLE001
        rewrite.update(after=None, error=f"{type(exc).__name__}: {str(exc)[:300]}")
        rec = _record(script_gate, OUTCOME_WRITER_ERROR, cqg.NEEDS_REVIEW, [cqg.SCR_REWRITE_FAILED], rewrite)
        return RewriteResult(OUTCOME_WRITER_ERROR, None, record=rec)
    rewrite["after"] = new_script
    g = guard(script, new_script, invariant)
    rewrite["guard"] = g
    if not g["passed"]:
        rec = _record(script_gate, OUTCOME_CONTENT_CHANGED, cqg.NEEDS_REVIEW, [cqg.SCR_REWRITE_CHANGED_CONTENT], rewrite)
        return RewriteResult(OUTCOME_CONTENT_CHANGED, new_script, record=rec, details={"guard": g})
    content_gate = recheck_content(new_script)
    new_script_gate = sqg.evaluate(new_script, domain=(script_gate.record or {}).get("domain"),
                                   identity=(script_gate.record or {}).get("identity") or {},
                                   invariant=invariant, content_quality_record_id=(content_gate.record or {}).get("quality_record_id"))
    rewrite["invariant_compare"] = _invariant_compare(script_gate.extra.get("invariant"), new_script_gate.extra.get("invariant"))
    rewrite["recheck"] = {"content_quality_record_id": (content_gate.record or {}).get("quality_record_id"),
                          "content_gate_status": content_gate.decision.gate_status,
                          "script_quality_record_id": (new_script_gate.record or {}).get("quality_record_id"),
                          "script_gate_status": new_script_gate.decision.gate_status}
    ok = content_gate.publishable and new_script_gate.publishable
    outcome = OUTCOME_REWRITTEN if ok else OUTCOME_RECHECK_FAILED
    rec = _record(script_gate, outcome, cqg.PASS if ok else cqg.NEEDS_REVIEW, [] if ok else [cqg.SCR_REWRITE_FAILED], rewrite)
    return RewriteResult(outcome, new_script, content_gate, new_script_gate, rec, {"guard": g})
