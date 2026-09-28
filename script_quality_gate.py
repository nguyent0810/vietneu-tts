"""S7 -- Script Quality Gate (ticket 14/16, D84/D87/D88/D89/D91).

Gọi ngay sau Content Quality Gate (S1), tại cùng điểm hội tụ. Chạy:
- S8 Toàn vẹn văn bản (`script_integrity`) -- gate DUY NHẤT có quyền chặn;
- tín hiệu chẩn đoán bằng code (`script_diagnostics`) -- chỉ ghi, không điểm;
- đọc Content invariant (S6) để biết Short có đủ điều kiện Script rewrite.

Gate status:
- PASS: không có finding S8 thuộc loại chặn (chẩn đoán/invariant KHÔNG BAO
  GIỜ làm đổi Gate status -- invariant chỉ quyết định có được rewrite không).
- FAIL: có finding S8 chặn VÀ invariant đủ -> đủ điều kiện Script rewrite (S11).
- Needs review: có finding S8 chặn nhưng invariant không đủ -> không được
  rewrite (D83), thêm `SCR_INVARIANT_INCOMPLETE`.
- Outcome không nhận diện được -> `INTERNAL_UNMAPPED` + Needs review.

Record ghi vào CÙNG kho Quality record của Spec 1 (D87), `layer: "script"`,
`rubric_version = "script-instrumentation-v0"` (D89). Ghi lỗi -> fail closed.
Không dùng khoá chỉ có trên Unix.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import content_invariant
import content_quality_gate as cqg
import script_diagnostics
import script_integrity

RUBRIC_VERSION = "script-instrumentation-v0"
LAYER = "script"
SCHEMA_VERSION = 1

SCR_INVARIANT_INCOMPLETE = cqg.SCR_INVARIANT_INCOMPLETE


@dataclass
class ScriptGateDecision:
    gate_status: str
    reason_codes: list[str]
    evidence: list[dict]
    rewrite_eligible: bool

    @property
    def publishable(self) -> bool:
        return self.gate_status == cqg.PASS


@dataclass
class ScriptGateResult:
    decision: ScriptGateDecision
    record: dict | None
    record_path: Path | None
    record_error: str | None = None
    integrity: script_integrity.IntegrityResult | None = None
    extra: dict = field(default_factory=dict)

    @property
    def publishable(self) -> bool:
        return self.decision.publishable and self.record_error is None


def decide(integrity: script_integrity.IntegrityResult, invariant: dict | None) -> ScriptGateDecision:
    """Hàm thuần: Gate decision tầng Script từ kết quả S8 + invariant."""
    sufficient, missing = content_invariant.sufficiency(invariant)
    evidence = [{"reason_code": f.reason_code, "kind": f.kind, "span": f.span, "sentence": f.position,
                 "blocking": f.blocking} for f in integrity.findings]
    if not integrity.failed:
        return ScriptGateDecision(cqg.PASS, [], evidence, rewrite_eligible=False)
    codes = integrity.reason_codes
    if sufficient:
        return ScriptGateDecision(cqg.FAIL, codes, evidence, rewrite_eligible=True)
    evidence.append({"reason_code": SCR_INVARIANT_INCOMPLETE, "detail": missing})
    return ScriptGateDecision(cqg.NEEDS_REVIEW, codes + [SCR_INVARIANT_INCOMPLETE], evidence, rewrite_eligible=False)


def build_record(*, domain: str, script: str, decision: ScriptGateDecision, diagnostics: dict,
                 invariant: dict | None, identity: dict, content_quality_record_id: str | None,
                 versions: dict | None = None, extra: dict | None = None) -> dict:
    sufficient, missing = content_invariant.sufficiency(invariant)
    return {
        "schema_version": SCHEMA_VERSION,
        "quality_record_id": uuid.uuid4().hex,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "layer": LAYER,
        "domain": domain,
        "identity": {k: identity.get(k) for k in ("content_id", "video_id", "case_id", "category", "generator",
                                                  "short_kind", "long_source")},
        "rubric_version": RUBRIC_VERSION,
        "versions": {"diagnostics_version": script_diagnostics.DIAGNOSTICS_VERSION, **(versions or {})},
        "gate_status": decision.gate_status,
        "reason_codes": list(decision.reason_codes),
        "evidence": list(decision.evidence),
        "rewrite_eligible": decision.rewrite_eligible,
        "bypass": False,
        "script": script,
        "diagnostics": diagnostics,
        "fingerprint": diagnostics.get("fingerprint"),
        "invariant": {"sufficient": sufficient, "missing": missing},
        "content_quality_record_id": content_quality_record_id,
        **(extra or {}),
    }


def evaluate(script: str, *, domain: str, identity: dict, invariant: dict | None,
             content_quality_record_id: str | None, versions: dict | None = None) -> ScriptGateResult:
    """S7: quyết định + ghi record `layer: script`. Không raise khi ghi lỗi
    (fail closed cho Short này, batch chạy tiếp)."""
    try:
        integrity = script_integrity.check(script)
        diag = script_diagnostics.diagnostics(script)
        decision = decide(integrity, invariant)
    except Exception as exc:  # noqa: BLE001 -- outcome không nhận diện được: không đoán
        integrity, diag = None, {}
        decision = ScriptGateDecision(cqg.NEEDS_REVIEW, [cqg.INTERNAL_UNMAPPED],
                                      [{"reason_code": cqg.INTERNAL_UNMAPPED,
                                        "detail": f"{type(exc).__name__}: {exc}"}], rewrite_eligible=False)
    record = build_record(domain=domain, script=script, decision=decision, diagnostics=diag, invariant=invariant,
                          identity=identity, content_quality_record_id=content_quality_record_id, versions=versions)
    try:
        path = cqg.append_record(record)
    except cqg.QualityRecordWriteError as exc:
        return ScriptGateResult(decision, record, None, record_error=str(exc), integrity=integrity)
    return ScriptGateResult(decision, record, path, integrity=integrity)


def evaluate_after_content_gate(content_gate: cqg.GateResult, *, invariant: dict | None,
                                versions: dict | None = None) -> ScriptGateResult:
    """Tiện ích cho call site: chạy S7 cho script mà S1 vừa cho PASS, lấy
    identity/domain từ record Content."""
    rec = content_gate.record or {}
    return evaluate(content_gate.decision.script or "", domain=rec.get("domain"), identity=rec.get("identity") or {},
                    invariant=invariant, content_quality_record_id=rec.get("quality_record_id"), versions=versions)


def report(gate: ScriptGateResult, log=print) -> bool:
    log(f"Script Quality Gate: {gate.decision.gate_status} {gate.decision.reason_codes} -> {gate.record_path}")
    if gate.record_error:
        log(f"DỪNG (fail closed): {gate.record_error}")
        return False
    if not gate.publishable:
        log("DỪNG: Script Quality Gate chưa PASS -- không ghi file Short.")
        return False
    return True
