"""Content Quality Gate (S1) + kho Quality record.

Điểm hội tụ duy nhất mà outcome của mọi đường sinh Short phải đi qua trước
Publish (spec `.scratch/improve-short-content-pipeline/spec.md`, D40–D54):

- Nhận một **source outcome** (dữ liệu gốc do nơi phát sinh cung cấp: engine
  judge panel, BUD review, CL gate...) và trả về một **Gate decision**
  (Gate status + reason codes + evidence + bypass flag).
- Bảng ánh xạ source outcome → Gate decision nằm DUY NHẤT trong module này
  (`_MAPPERS`). Outcome chưa có trong bảng → `INTERNAL_UNMAPPED` + Needs
  review, không map ngầm vào reason code gần giống (D54).
- Mỗi quyết định được ghi thành 1 dòng Quality record trong kho append-only,
  một file JSONL mỗi Domain, giữ nguyên source outcome gốc bên cạnh Gate
  decision. Không dùng khoá chỉ có trên Unix (D51) — chạy được trên Windows.
- Không đổi ngưỡng/rubric nào: chỉ đặt tên cho kết quả hiện có.
  `rubric_version` của mọi record Content trong spec này là "legacy" (D53).

Module này KHÔNG được import code cần `fcntl` (registry_lock,
rotation_state, domain_creative_profiles...).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

SCHEMA_VERSION = 1
RUBRIC_VERSION_LEGACY = "legacy"

# Gate status (CONTEXT.md: Gate status).
PASS = "pass"
FAIL = "fail"
NEEDS_REVIEW = "needs_review"
INSUFFICIENT_SOURCE = "insufficient_source"
GATE_STATUSES = frozenset({PASS, FAIL, NEEDS_REVIEW, INSUFFICIENT_SOURCE})

DOMAINS = frozenset({"BUD", "FS", "CL"})

# Tập reason code ĐÓNG (D54, D88). Thêm code mới phải thêm vào đây.
ACC_NO_CANDIDATE_PASSED_FACTCHECK = "ACC_NO_CANDIDATE_PASSED_FACTCHECK"
JUDGE_BELOW_HOOK_THRESHOLD = "JUDGE_BELOW_HOOK_THRESHOLD"
JUDGE_GENERATE_ERROR = "JUDGE_GENERATE_ERROR"
JUDGE_CALL_ERROR = "JUDGE_CALL_ERROR"
JUDGE_VERDICT_REJECTED = "JUDGE_VERDICT_REJECTED"
BYPASS_JUDGE = "BYPASS_JUDGE"
INTERNAL_UNMAPPED = "INTERNAL_UNMAPPED"
INTERNAL_RECORD_WRITE_FAILED = "INTERNAL_RECORD_WRITE_FAILED"
SAF_TRENDING_REQUIRES_HUMAN_REVIEW = "SAF_TRENDING_REQUIRES_HUMAN_REVIEW"
ACC_PUBLISH_REVERIFY_FAILED = "ACC_PUBLISH_REVERIFY_FAILED"
ACC_DRAFT_INVALID = "ACC_DRAFT_INVALID"
SRC_INSUFFICIENT_SOURCE_MATERIAL = "SRC_INSUFFICIENT_SOURCE_MATERIAL"
SRC_NO_QUALITY_RECORD = "SRC_NO_QUALITY_RECORD"
SRC_GATE_NOT_PASSED = "SRC_GATE_NOT_PASSED"
SRC_SCRIPT_CHANGED_AFTER_GATE = "SRC_SCRIPT_CHANGED_AFTER_GATE"
# CL sidecar gate của runner (bằng chứng Phase A cho đúng script sắp TTS).
SAF_CL_SIDECAR_MISSING = "SAF_CL_SIDECAR_MISSING"
SAF_CL_SIDECAR_UNREADABLE = "SAF_CL_SIDECAR_UNREADABLE"
SAF_CL_SIDECAR_INCOMPLETE = "SAF_CL_SIDECAR_INCOMPLETE"
SAF_CL_SCRIPT_HASH_MISMATCH = "SAF_CL_SCRIPT_HASH_MISMATCH"
SAF_CL_FACT_VERIFICATION_INVALID = "SAF_CL_FACT_VERIFICATION_INVALID"
SAF_CL_PROVENANCE_INVALID = "SAF_CL_PROVENANCE_INVALID"
# CL Phase A (storytelling / provenance).
ACC_C4_BLOCKED = "ACC_C4_BLOCKED"
ACC_CLAIM_LEDGER_BLOCKED = "ACC_CLAIM_LEDGER_BLOCKED"
ACC_PROVENANCE_FAILED = "ACC_PROVENANCE_FAILED"
SAF_UNVETTED_PERSON_REFERENCE = "SAF_UNVETTED_PERSON_REFERENCE"
STR_SEO_FAILED = "STR_SEO_FAILED"
SRC_FACT_LEDGER_MISSING = "SRC_FACT_LEDGER_MISSING"
INTERNAL_CLAIM_LEDGER_ERROR = "INTERNAL_CLAIM_LEDGER_ERROR"
INTERNAL_PHASE_A_ERROR = "INTERNAL_PHASE_A_ERROR"
# CL orchestrator (case pipeline): mỗi loại escalation một reason code.
SAF_CL_ESCALATED_HIGH_RISK = "SAF_CL_ESCALATED_HIGH_RISK"
SAF_CL_ESCALATED_MEDIUM_RISK = "SAF_CL_ESCALATED_MEDIUM_RISK"
SAF_CL_CLAIM_EXPOSURE_FAILED = "SAF_CL_CLAIM_EXPOSURE_FAILED"
SRC_CL_DUPLICATE_CASE = "SRC_CL_DUPLICATE_CASE"
SRC_CL_LOW_CONFIDENCE_DEDUPE = "SRC_CL_LOW_CONFIDENCE_DEDUPE"
SRC_CL_DEFERRED_DEFICIT = "SRC_CL_DEFERRED_DEFICIT"
JUDGE_CL_GENERATION_FAILED = "JUDGE_CL_GENERATION_FAILED"
ACC_CL_PHASE_A_REVIEW_FAILED = "ACC_CL_PHASE_A_REVIEW_FAILED"
# Tầng Script (D88): Toàn vẹn văn bản (S8, script_integrity.py).
SCR_REPEATED_SENTENCE = "SCR_REPEATED_SENTENCE"
SCR_LEFTOVER_MARKUP = "SCR_LEFTOVER_MARKUP"
SCR_TRUNCATED = "SCR_TRUNCATED"

REASON_CODES = frozenset({
    ACC_NO_CANDIDATE_PASSED_FACTCHECK,
    JUDGE_BELOW_HOOK_THRESHOLD,
    JUDGE_GENERATE_ERROR,
    JUDGE_CALL_ERROR,
    JUDGE_VERDICT_REJECTED,
    BYPASS_JUDGE,
    INTERNAL_UNMAPPED,
    INTERNAL_RECORD_WRITE_FAILED,
    SAF_TRENDING_REQUIRES_HUMAN_REVIEW,
    ACC_PUBLISH_REVERIFY_FAILED,
    ACC_DRAFT_INVALID,
    SRC_INSUFFICIENT_SOURCE_MATERIAL,
    SRC_NO_QUALITY_RECORD,
    SRC_GATE_NOT_PASSED,
    SRC_SCRIPT_CHANGED_AFTER_GATE,
    SAF_CL_SIDECAR_MISSING,
    SAF_CL_SIDECAR_UNREADABLE,
    SAF_CL_SIDECAR_INCOMPLETE,
    SAF_CL_SCRIPT_HASH_MISMATCH,
    SAF_CL_FACT_VERIFICATION_INVALID,
    SAF_CL_PROVENANCE_INVALID,
    ACC_C4_BLOCKED,
    ACC_CLAIM_LEDGER_BLOCKED,
    ACC_PROVENANCE_FAILED,
    SAF_UNVETTED_PERSON_REFERENCE,
    STR_SEO_FAILED,
    SRC_FACT_LEDGER_MISSING,
    INTERNAL_CLAIM_LEDGER_ERROR,
    INTERNAL_PHASE_A_ERROR,
    SAF_CL_ESCALATED_HIGH_RISK,
    SAF_CL_ESCALATED_MEDIUM_RISK,
    SAF_CL_CLAIM_EXPOSURE_FAILED,
    SRC_CL_DUPLICATE_CASE,
    SRC_CL_LOW_CONFIDENCE_DEDUPE,
    SRC_CL_DEFERRED_DEFICIT,
    JUDGE_CL_GENERATION_FAILED,
    ACC_CL_PHASE_A_REVIEW_FAILED,
    SCR_REPEATED_SENTENCE,
    SCR_LEFTOVER_MARKUP,
    SCR_TRUNCATED,
})

# Tên nguồn của source outcome.
SOURCE_JUDGE_PANEL_ENGINE = "judge_panel_engine"
# TRENDING: bước draft (engine judge panel, LUÔN cần người duyệt) và bước
# publish (fact-check lại script sắp ghi so với nguồn, độc lập với draft).
SOURCE_TRENDING_DRAFT = "trending_draft"
SOURCE_TRENDING_PUBLISH = "trending_publish_reverify"
# BUD: Short trích từ Long, viết lại qua short_content_review (engine judge panel).
SOURCE_BUD_REVIEW = "bud_short_review"
# Runner nhận một script staged do generator ghi: đối chiếu với Quality
# record mà generator đã ghi lúc sinh (không tự diễn giải theo topic).
SOURCE_RUNNER_STAGED = "runner_staged_script"
# CL: sidecar gate của runner và Phase A (storytelling_v1 / provenance_v1).
SOURCE_CL_SIDECAR_GATE = "cl_sidecar_gate"
SOURCE_CL_PHASE_A = "cl_phase_a"
SOURCE_CL_ORCHESTRATOR = "cl_case_orchestrator"

DEFAULT_STORE_DIR = Path(__file__).parent / "output" / "quality_records"
STORE_DIR_ENV = "VIETNEU_QUALITY_RECORD_DIR"


# Engine judge panel gọi Codex qua `codex exec` (model mặc định của CLI) và tự
# fallback sang cursor-agent model "auto" (content_seo._run_codex) -- model thật
# của từng lần gọi không được CLI trả về, nên ghi đúng mô tả này thay vì đoán.
JUDGE_MODEL_JUDGE_PANEL = "codex exec (model mặc định CLI; fallback cursor-agent --model auto)"


def content_fingerprint(*parts: str) -> str:
    """Version theo nội dung (sha256 rút gọn) cho generator/prompt: đổi 1 ký
    tự là đổi version, không phụ thuộc người nhớ tăng số."""
    digest = hashlib.sha256()
    for part in parts:
        digest.update(part.encode("utf-8"))
        digest.update(b"\x00")
    return digest.hexdigest()[:12]


def file_fingerprint(path: str | Path) -> str:
    return content_fingerprint(Path(path).read_text(encoding="utf-8"))


class QualityRecordWriteError(RuntimeError):
    """Ghi Quality record thất bại. Caller PHẢI chặn Short đó khỏi Publish
    path (fail closed, D52) nhưng không bắt buộc dừng cả batch."""


@dataclass
class SourceOutcome:
    """Dữ liệu gốc do nơi phát sinh outcome cung cấp.

    `raw` là outcome nguyên bản (vd dict trả về của engine judge panel) và
    được lưu nguyên vẹn trong Quality record."""
    source: str
    domain: str
    raw: dict
    content_id: str | None = None
    video_id: str | None = None
    case_id: str | None = None
    category: str | None = None
    generator: str | None = None
    short_kind: str | None = None  # "standalone" | "extracted_from_long"
    long_source: str | None = None
    facts: Any = None
    source_excerpt: str | None = None
    versions: dict = field(default_factory=dict)  # generator_version, prompt_version, judge_model


@dataclass
class GateDecision:
    gate_status: str
    reason_codes: list[str]
    evidence: list[dict]
    bypass: bool = False
    script: str | None = None

    @property
    def publishable(self) -> bool:
        return self.gate_status == PASS


# --------------------------------------------------------------------------
# Bảng ánh xạ (một chỗ duy nhất)
# --------------------------------------------------------------------------

def _choice(verdict: dict):
    """Ứng viên judge chọn: `candidate_id` (contract hiện hành, ticket 07);
    `winner` chỉ để đọc outcome cũ."""
    return verdict.get("candidate_id", verdict.get("winner"))


def _round_issue_codes(history: list[dict]) -> tuple[list[str], list[dict]]:
    """Reason code + evidence cho từng vòng có vấn đề trong lịch sử engine."""
    codes: list[str] = []
    evidence: list[dict] = []
    for entry in history or []:
        stage = entry.get("stage")
        rnd = entry.get("round")
        if stage == "generate":
            codes.append(JUDGE_GENERATE_ERROR)
            evidence.append({"round": rnd, "reason_code": JUDGE_GENERATE_ERROR, "detail": entry.get("error")})
        elif stage == "judge":
            codes.append(JUDGE_CALL_ERROR)
            evidence.append({"round": rnd, "reason_code": JUDGE_CALL_ERROR, "detail": entry.get("error")})
        elif stage == "judge_rejected":
            codes.append(JUDGE_VERDICT_REJECTED)
            evidence.append({"round": rnd, "reason_code": JUDGE_VERDICT_REJECTED, "detail": entry.get("error")})
        elif isinstance(entry.get("verdict"), dict) and _choice(entry["verdict"]) == "NONE":
            codes.append(ACC_NO_CANDIDATE_PASSED_FACTCHECK)
            evidence.append({"round": rnd, "reason_code": ACC_NO_CANDIDATE_PASSED_FACTCHECK,
                             "detail": entry["verdict"].get("fact_check")})
    return codes, evidence


def _dedupe(codes: list[str]) -> list[str]:
    return list(dict.fromkeys(codes))


def _is_bypass(engine_raw: dict) -> bool:
    """Outcome engine đi qua VIETNEU_SKIP_JUDGE_PANEL (history có skipped_judge)."""
    history = engine_raw.get("history") if isinstance(engine_raw, dict) else None
    if not isinstance(history, list):
        history = engine_raw.get("round_history") if isinstance(engine_raw, dict) else None
    return any(isinstance(h, dict) and h.get("skipped_judge") for h in history or [])


def _map_judge_panel_engine(raw: dict) -> GateDecision | None:
    """Outcome của `short_judge_panel_engine.generate_verified_script`.

    Trả None nếu hình dạng outcome không nhận ra được (→ INTERNAL_UNMAPPED)."""
    if not isinstance(raw, dict) or "passed" not in raw or "history" not in raw:
        return None
    history = raw.get("history") or []
    script = raw.get("script")

    if _is_bypass(raw):
        return GateDecision(NEEDS_REVIEW, [BYPASS_JUDGE],
                            [{"reason_code": BYPASS_JUDGE, "detail": "VIETNEU_SKIP_JUDGE_PANEL=1: không qua judge/fact-check"}],
                            bypass=True, script=script)

    round_codes, round_evidence = _round_issue_codes(history)

    if raw.get("passed") is True and isinstance(script, str) and script.strip() and not raw.get("needs_human_review"):
        return GateDecision(PASS, [], [], script=script)

    if raw.get("passed") is False and isinstance(script, str) and script.strip():
        # Có bản tốt nhất đã qua fact-check nhưng dưới ngưỡng hook_score hiện hành.
        evidence = [{"reason_code": JUDGE_BELOW_HOOK_THRESHOLD, "detail": {"hook_score": raw.get("hook_score")}}]
        return GateDecision(NEEDS_REVIEW, _dedupe([JUDGE_BELOW_HOOK_THRESHOLD] + round_codes),
                            evidence + round_evidence, script=script)

    if raw.get("passed") is False and script is None:
        if not round_codes:
            return None
        return GateDecision(FAIL, _dedupe(round_codes), round_evidence, script=None)

    return None


def _map_trending_draft(raw: dict) -> GateDecision | None:
    """Draft TRENDING = outcome engine, nhưng chính sách kênh: MỌI draft cần
    người duyệt (tin tức có thể nhắc người thật / còn diễn biến) -- PASS của
    engine thành Needs review, không bao giờ PASS."""
    base = _map_judge_panel_engine(raw)
    if base is None or base.gate_status != PASS:
        return base
    return GateDecision(NEEDS_REVIEW, [SAF_TRENDING_REQUIRES_HUMAN_REVIEW],
                        [{"reason_code": SAF_TRENDING_REQUIRES_HUMAN_REVIEW,
                          "detail": "draft TRENDING luôn chờ người duyệt trước bước publish"}],
                        script=base.script)


def _map_trending_publish(raw: dict) -> GateDecision | None:
    """Bước publish TRENDING. raw: {stage: "precheck"|"reverify", ok: bool,
    reason: str, script: str|None, error: str|None}."""
    if not isinstance(raw, dict) or raw.get("stage") not in {"precheck", "reverify"} or not isinstance(raw.get("ok"), bool):
        return None
    script = raw.get("script") if isinstance(raw.get("script"), str) else None
    evidence = {"stage": raw["stage"], "detail": raw.get("reason")}
    # Draft sinh qua VIETNEU_SKIP_JUDGE_PANEL: vẫn publish được sau khi người
    # duyệt + fact-check lại, nhưng record giữ cờ bypass để loại khỏi calibration.
    bypass = raw.get("draft_bypass") is True
    if raw["stage"] == "precheck":
        if raw["ok"]:
            return None  # precheck chỉ ghi khi FAIL; PASS thật phải đi qua reverify
        return GateDecision(FAIL, [ACC_DRAFT_INVALID], [{"reason_code": ACC_DRAFT_INVALID, **evidence}], bypass=bypass, script=script)
    if raw.get("error"):
        return GateDecision(FAIL, [JUDGE_CALL_ERROR], [{"reason_code": JUDGE_CALL_ERROR, **evidence,
                                                        "error": raw["error"]}], bypass=bypass, script=script)
    if raw["ok"] and script and script.strip():
        return GateDecision(PASS, [], [evidence], bypass=bypass, script=script)
    if not raw["ok"]:
        return GateDecision(FAIL, [ACC_PUBLISH_REVERIFY_FAILED],
                            [{"reason_code": ACC_PUBLISH_REVERIFY_FAILED, **evidence}], bypass=bypass, script=script)
    return None


def _map_bud_review(raw: dict) -> GateDecision | None:
    """Outcome của `short_content_review.review_and_optimize_short` (khoá
    final_script/round_history thay cho script/history của engine).

    Source không đủ (D12): judge đánh dấu `source_insufficient: true` ở MỌI
    vòng có verdict và không vòng nào chọn được bản thắng -- nghĩa là đoạn
    trích quá mỏng để viết Short mà không thêm thắt, không phải lỗi writer."""
    if not isinstance(raw, dict) or "passed" not in raw or "round_history" not in raw:
        return None
    history = raw.get("round_history") or []
    verdicts = [h["verdict"] for h in history if isinstance(h, dict) and isinstance(h.get("verdict"), dict)]
    if (raw.get("final_script") is None and verdicts
            and all(_choice(v) == "NONE" and v.get("source_insufficient") is True for v in verdicts)):
        return GateDecision(INSUFFICIENT_SOURCE, [SRC_INSUFFICIENT_SOURCE_MATERIAL],
                            [{"reason_code": SRC_INSUFFICIENT_SOURCE_MATERIAL, "round": h.get("round"),
                              "detail": h["verdict"].get("fact_check")}
                             for h in history if isinstance(h, dict) and isinstance(h.get("verdict"), dict)])
    engine_shape = {"script": raw.get("final_script"), "passed": raw.get("passed"),
                    "hook_score": raw.get("hook_score"), "history": history,
                    "needs_human_review": raw.get("needs_human_review")}
    return _map_judge_panel_engine(engine_shape)


def _map_runner_staged(raw: dict) -> GateDecision | None:
    """raw: {record: Quality record Content của generator cho content_id này
    hoặc None, script: script staged runner sắp dùng}."""
    if not isinstance(raw, dict) or "script" not in raw or not isinstance(raw.get("script"), str):
        return None
    script = raw["script"]
    record = raw.get("record")
    if record is None:
        return GateDecision(NEEDS_REVIEW, [SRC_NO_QUALITY_RECORD],
                            [{"reason_code": SRC_NO_QUALITY_RECORD,
                              "detail": "script staged không có Quality record Content nào của generator"}],
                            script=script)
    ref = {"quality_record_id": record.get("quality_record_id"), "gate_status": record.get("gate_status")}
    if record.get("gate_status") != PASS:
        return GateDecision(NEEDS_REVIEW, [SRC_GATE_NOT_PASSED],
                            [{"reason_code": SRC_GATE_NOT_PASSED, **ref,
                              "detail": record.get("reason_codes")}], script=script)
    if (record.get("script") or "").strip() != script.strip():
        return GateDecision(NEEDS_REVIEW, [SRC_SCRIPT_CHANGED_AFTER_GATE],
                            [{"reason_code": SRC_SCRIPT_CHANGED_AFTER_GATE, **ref}], script=script)
    return GateDecision(PASS, [], [ref], script=script)


_CL_SIDECAR_CODES = {
    "missing": SAF_CL_SIDECAR_MISSING,
    "unreadable": SAF_CL_SIDECAR_UNREADABLE,
    "incomplete": SAF_CL_SIDECAR_INCOMPLETE,
    "script_hash_mismatch": SAF_CL_SCRIPT_HASH_MISMATCH,
    "fact_verification_invalid": SAF_CL_FACT_VERIFICATION_INVALID,
    "provenance_invalid": SAF_CL_PROVENANCE_INVALID,
}


def _map_cl_sidecar_gate(raw: dict) -> GateDecision | None:
    """raw: {ok: bool, kind: None|khoá của _CL_SIDECAR_CODES, reason: str, script, ...}."""
    if not isinstance(raw, dict) or not isinstance(raw.get("ok"), bool):
        return None
    script = raw.get("script") if isinstance(raw.get("script"), str) else None
    if raw["ok"]:
        return GateDecision(PASS, [], [{k: raw.get(k) for k in ("case_id", "phase_a_variant", "reviewed_script_hash")}],
                            script=script)
    code = _CL_SIDECAR_CODES.get(raw.get("kind"))
    if code is None:
        return None
    return GateDecision(FAIL, [code], [{"reason_code": code, "detail": raw.get("reason")}], script=script)


_CL_PHASE_A_CODES = {
    "STORYTELLING_C4_FAILED": (FAIL, ACC_C4_BLOCKED),
    "STORYTELLING_BLOCKED_FACT": (FAIL, ACC_CLAIM_LEDGER_BLOCKED),
    "STORYTELLING_PROVENANCE_FAILED": (FAIL, ACC_PROVENANCE_FAILED),
    "STORYTELLING_UNVETTED_PERSON_REFERENCE": (FAIL, SAF_UNVETTED_PERSON_REFERENCE),
    "STORYTELLING_SEO_FAILED": (NEEDS_REVIEW, STR_SEO_FAILED),
    "STORYTELLING_CLAIM_LEDGER_ERROR": (NEEDS_REVIEW, INTERNAL_CLAIM_LEDGER_ERROR),
    "STORYTELLING_PHASE_A_UNEXPECTED_ERROR": (NEEDS_REVIEW, INTERNAL_PHASE_A_ERROR),
    "FACT_LEDGER_MISSING": (NEEDS_REVIEW, SRC_FACT_LEDGER_MISSING),
}


def _map_cl_phase_a(raw: dict) -> GateDecision | None:
    """raw: StorytellingPhaseAResult dạng dict (passed, reason_code, evidence,
    evidence_details, fact_verification, ...) + script."""
    if not isinstance(raw, dict) or not isinstance(raw.get("passed"), bool):
        return None
    script = raw.get("script") if isinstance(raw.get("script"), str) else None
    if raw["passed"]:
        return GateDecision(PASS, [], [{"detail": raw.get("evidence"),
                                        "fact_verification": raw.get("fact_verification")}], script=script)
    mapped = _CL_PHASE_A_CODES.get(raw.get("reason_code"))
    if mapped is None:
        return None
    status, code = mapped
    evidence = {"reason_code": code, "source_reason_code": raw.get("reason_code"), "detail": raw.get("evidence")}
    details = raw.get("evidence_details") or {}
    # C4 (storytelling) và C4 drift detector (provenance) đều lưu các câu bị chặn.
    if code in (ACC_C4_BLOCKED, ACC_PROVENANCE_FAILED) and details.get("blocking_claims") is not None:
        evidence["blocked_sentences"] = details["blocking_claims"]
    if details.get("guard_violations"):
        evidence["guard_violations"] = details["guard_violations"]
    return GateDecision(status, [code], [evidence], script=script)


_CL_ORCHESTRATOR_BUCKETS = {
    "escalated_high": (NEEDS_REVIEW, SAF_CL_ESCALATED_HIGH_RISK),
    "escalated_medium_exhausted": (NEEDS_REVIEW, SAF_CL_ESCALATED_MEDIUM_RISK),
    "escalated_claim_exposure_failed": (FAIL, SAF_CL_CLAIM_EXPOSURE_FAILED),
    "rejected_duplicate": (FAIL, SRC_CL_DUPLICATE_CASE),
    "escalated_low_confidence_dedupe": (NEEDS_REVIEW, SRC_CL_LOW_CONFIDENCE_DEDUPE),
    # LOW-tier, qua claim-gate nhưng chưa sinh vì đã đủ deficit: KHÔNG phải
    # lỗi, chưa có script -- ghi để không outcome nào chỉ nằm trên màn hình.
    "deferred_deficit": (NEEDS_REVIEW, SRC_CL_DEFERRED_DEFICIT),
    "escalated_generation_failed": (FAIL, JUDGE_CL_GENERATION_FAILED),
    "escalated_phase_a_review_failed": (FAIL, ACC_CL_PHASE_A_REVIEW_FAILED),
}


def _map_cl_orchestrator(raw: dict) -> GateDecision | None:
    """raw: {bucket, detail, source_reason_code, script, ...} từ CLGateResult."""
    if not isinstance(raw, dict):
        return None
    script = raw.get("script") if isinstance(raw.get("script"), str) else None
    script_result = raw.get("script_result") if isinstance(raw.get("script_result"), dict) else {}
    if _is_bypass(script_result):
        return GateDecision(NEEDS_REVIEW, [BYPASS_JUDGE],
                            [{"reason_code": BYPASS_JUDGE, "bucket": raw.get("bucket"),
                              "detail": "VIETNEU_SKIP_JUDGE_PANEL=1: script CL không qua judge/fact-check"}],
                            bypass=True, script=script)
    if raw.get("bucket") == "auto_selected":
        return GateDecision(PASS, [], [{"detail": raw.get("detail")}], script=script)
    mapped = _CL_ORCHESTRATOR_BUCKETS.get(raw.get("bucket"))
    if mapped is None:
        return None
    status, code = mapped
    return GateDecision(status, [code], [{"reason_code": code, "bucket": raw["bucket"],
                                          "source_reason_code": raw.get("source_reason_code"),
                                          "detail": raw.get("detail")}], script=script)


_MAPPERS: dict[str, Callable[[dict], GateDecision | None]] = {
    SOURCE_JUDGE_PANEL_ENGINE: _map_judge_panel_engine,
    SOURCE_CL_ORCHESTRATOR: _map_cl_orchestrator,
    SOURCE_CL_SIDECAR_GATE: _map_cl_sidecar_gate,
    SOURCE_CL_PHASE_A: _map_cl_phase_a,
    SOURCE_BUD_REVIEW: _map_bud_review,
    SOURCE_RUNNER_STAGED: _map_runner_staged,
    SOURCE_TRENDING_DRAFT: _map_trending_draft,
    SOURCE_TRENDING_PUBLISH: _map_trending_publish,
}


def decide(outcome: SourceOutcome) -> GateDecision:
    """Chuẩn hoá source outcome thành Gate decision (hàm thuần)."""
    mapper = _MAPPERS.get(outcome.source)
    decision = mapper(outcome.raw) if mapper else None
    if decision is None:
        return GateDecision(NEEDS_REVIEW, [INTERNAL_UNMAPPED],
                            [{"reason_code": INTERNAL_UNMAPPED,
                              "detail": f"outcome chưa có trong bảng ánh xạ (source={outcome.source!r})"}],
                            script=(outcome.raw or {}).get("script") if isinstance(outcome.raw, dict) else None)
    assert decision.gate_status in GATE_STATUSES
    assert all(code in REASON_CODES for code in decision.reason_codes), decision.reason_codes
    return decision


# --------------------------------------------------------------------------
# Quality record
# --------------------------------------------------------------------------

def _flatten_candidates(history: list[dict]) -> list[dict]:
    """Mọi ứng viên của mọi vòng, kèm fact-check, nhãn Hook formula và điểm
    (engine hiện chỉ trả hook_score cho ứng viên thắng)."""
    rows = []
    for entry in history or []:
        if not isinstance(entry, dict):
            continue
        verdict = entry.get("verdict") if isinstance(entry.get("verdict"), dict) else {}
        fact_check = verdict.get("fact_check") if isinstance(verdict.get("fact_check"), dict) else {}
        winner = _choice(verdict)
        for cand in entry.get("candidates") or []:
            if not isinstance(cand, dict):
                continue
            strategy = cand.get("strategy")
            rows.append({
                "round": entry.get("round"),
                "candidate_id": strategy,
                "hook_formula": strategy,
                "script": cand.get("script"),
                "fact_check": fact_check.get(strategy),
                "is_winner": winner == strategy,
                "hook_score": verdict.get("hook_score") if winner == strategy else None,
            })
    return rows


def _history_of(raw: dict) -> list:
    for key in ("history", "round_history"):
        if isinstance(raw.get(key), list):
            return raw[key]
    return []


def build_record(outcome: SourceOutcome, decision: GateDecision, *, layer: str = "content",
                 rubric_version: str = RUBRIC_VERSION_LEGACY) -> dict:
    raw = outcome.raw if isinstance(outcome.raw, dict) else {"value": outcome.raw}
    return {
        "schema_version": SCHEMA_VERSION,
        "quality_record_id": uuid.uuid4().hex,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "layer": layer,
        "domain": outcome.domain,
        "identity": {
            "content_id": outcome.content_id,
            "video_id": outcome.video_id,
            "case_id": outcome.case_id,
            "category": outcome.category,
            "generator": outcome.generator,
            "short_kind": outcome.short_kind,
            "long_source": outcome.long_source,
        },
        "rubric_version": rubric_version,
        "versions": dict(outcome.versions),
        "gate_status": decision.gate_status,
        "reason_codes": list(decision.reason_codes),
        "evidence": list(decision.evidence),
        "bypass": decision.bypass,
        "script": decision.script,
        "facts": outcome.facts,
        "source_excerpt": outcome.source_excerpt,
        "candidates": _flatten_candidates(_history_of(raw)),
        "source_outcome": {"source": outcome.source, "raw": raw},
    }


def store_dir() -> Path:
    override = os.environ.get(STORE_DIR_ENV)
    return Path(override) if override else DEFAULT_STORE_DIR


def store_path(domain: str) -> Path:
    if domain not in DOMAINS:
        raise ValueError(f"Domain không hợp lệ cho Quality record: {domain!r} (phải thuộc {sorted(DOMAINS)})")
    return store_dir() / f"{domain}.jsonl"


def append_record(record: dict) -> Path:
    """Append đúng 1 dòng JSON vào kho của Domain. Không bao giờ sửa/xoá dòng
    cũ. Một lần `os.write` trên fd mở với O_APPEND (không khoá Unix)."""
    try:
        path = store_path(record.get("domain"))
    except ValueError as exc:
        raise QualityRecordWriteError(str(exc)) from exc
    line = (json.dumps(record, ensure_ascii=False, default=str) + "\n").encode("utf-8")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Lần ghi trước bị ngắt giữa chừng -> dòng cuối thiếu "\n": bắt đầu
        # dòng mới để record này không dính vào dòng hỏng.
        if path.exists() and path.stat().st_size > 0:
            with open(path, "rb") as fh:
                fh.seek(-1, os.SEEK_END)
                if fh.read(1) != b"\n":
                    line = b"\n" + line
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_BINARY", 0), 0o644)
        try:
            written = os.write(fd, line)
            if written != len(line):
                raise OSError(f"ghi thiếu {written}/{len(line)} byte")
            os.fsync(fd)
        finally:
            os.close(fd)
    except (OSError, TypeError, ValueError) as exc:
        raise QualityRecordWriteError(f"Không ghi được Quality record vào {path}: {exc}") from exc
    return path


def read_records(domain: str) -> list[dict]:
    """Mọi record của Domain theo thứ tự append. Dòng hỏng (vd lần ghi trước
    bị ngắt giữa chừng -- Short đó đã bị chặn fail closed) được bỏ qua kèm
    cảnh báo, không làm hỏng việc đọc cả kho."""
    path = store_path(domain)
    if not path.exists():
        return []
    records = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"CẢNH BÁO: bỏ qua dòng Quality record hỏng {path}:{lineno}", file=sys.stderr)
    return records


def latest_record(domain: str, content_id: str, *, layer: str = "content",
                  exclude_sources: tuple[str, ...] = ()) -> dict | None:
    """Record mới nhất (theo thứ tự append) của content_id ở tầng `layer`."""
    found = None
    for rec in read_records(domain):
        if (rec.get("layer") == layer and (rec.get("identity") or {}).get("content_id") == content_id
                and (rec.get("source_outcome") or {}).get("source") not in exclude_sources):
            found = rec
    return found


@dataclass
class GateResult:
    decision: GateDecision
    record: dict | None
    record_path: Path | None
    record_error: str | None = None

    @property
    def publishable(self) -> bool:
        """Chỉ Publish được khi Gate PASS VÀ record đã ghi thành công (D52)."""
        return self.decision.publishable and self.record_error is None


def evaluate(outcome: SourceOutcome) -> GateResult:
    """S1: quyết định + ghi Quality record. Ghi lỗi → fail closed cho Short
    này (publishable=False), không raise để batch chạy tiếp Short khác."""
    decision = decide(outcome)
    record = build_record(outcome, decision)
    try:
        path = append_record(record)
    except QualityRecordWriteError as exc:
        return GateResult(decision, record, None, record_error=str(exc))
    return GateResult(decision, record, path)


# --------------------------------------------------------------------------
# Call site dùng chung cho các generator Short dựa trên engine judge panel
# --------------------------------------------------------------------------

def content_id_for_bundle(bundle_path: str | Path, segment_index: int = 1) -> str:
    """content_id = key registry mà runner sẽ dùng cho đoạn này: tên file
    bundle bỏ đuôi `_Short.txt` (= `episode` của short_segment_discovery) +
    `_{idx:02d}`."""
    name = Path(bundle_path).name
    if not name.endswith("_Short.txt"):
        raise ValueError(f"Không phải file bundle Short: {name}")
    return f"{name[: -len('_Short.txt')]}_{segment_index:02d}"


def judge_panel_outcome(*, domain: str, generator: str, generator_file: str | Path, category: str | None,
                        facts: Any, result: dict, content_id: str, prompts: tuple[str, ...],
                        short_kind: str = "standalone", source_excerpt: str | None = None,
                        long_source: str | None = None, source: str = SOURCE_JUDGE_PANEL_ENGINE) -> SourceOutcome:
    """Source outcome cho outcome của `generate_verified_script`.

    `prompts`: mọi template/khối prompt thực sự đưa vào writer và judge (kể
    cả khối retention dùng chung của engine) -- prompt_version là dấu vân
    tay nội dung của chúng."""
    return SourceOutcome(
        source=source,
        domain=domain,
        raw=result,
        content_id=content_id,
        category=category,
        generator=generator,
        short_kind=short_kind,
        long_source=long_source,
        facts=facts,
        source_excerpt=source_excerpt,
        versions={
            "generator_version": file_fingerprint(generator_file),
            "prompt_version": content_fingerprint(*prompts),
            "judge_model": JUDGE_MODEL_JUDGE_PANEL,
        },
    )


def report(gate: GateResult, log=print) -> bool:
    """In Gate decision; trả True nếu Short được phép đi tiếp (ghi script /
    Publish). Ghi record lỗi → fail closed."""
    log(f"Content Quality Gate: {gate.decision.gate_status} {gate.decision.reason_codes} -> {gate.record_path}")
    if gate.record_error:
        log(f"DỪNG (fail closed): {gate.record_error}")
        return False
    if not gate.publishable:
        log("DỪNG: không tự động ghi file Short -- Gate chưa PASS, cần người xem lại.")
        return False
    return True
