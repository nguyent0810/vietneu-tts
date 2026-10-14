"""Test cho cl_risk_gate_orchestrator.py (Gate B, task #241). Mock các hàm
scoring/generation/review CẤP THẤP (đã có test riêng ở module của chúng) để
cô lập test ĐÚNG logic orchestration (dedupe routing, tier routing, claim-
gate routing, backfill, deficit validation, audit_log) -- không test lại
logic bên trong C1-C7/generation/Phase A review."""
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import cl_risk_gate as g  # noqa: E402
import cl_risk_gate_orchestrator as O  # noqa: E402
import cl_case_generation as CG  # noqa: E402
import cl_risk_gate_lifecycle as L  # noqa: E402


def _candidate(case_id="c1", case_key=None):
    return g.CandidateCase(case_id=case_id, case_key=case_key or f"k_{case_id}", working_title=f"Case {case_id}")


def _criterion(cid, passed, evidence="ok"):
    return g.CriterionResult(cid, passed, evidence, "test")


def _dedupe_result(is_duplicate=False, confidence="high", evidence="ok"):
    return g.DedupeResult(
        is_duplicate=is_duplicate, verdict=None, matched_case_id=None, matched_case_status=None,
        related_case_ids=[], method="test", dedupe_confidence=confidence, candidates_compared=[], evidence=evidence,
    )


def _low_score():
    return g.RiskScoreResult(tier="LOW", criteria=[], failing_criteria=[], high_risk_triggers=[], rationale="r", scorer_version="v", allowlist_version="v", scored_at="t")


def _claim_pass():
    return type("R", (), {"passed": True, "reason_code": None, "evidence": "ok", "claim_ledger": []})()


def _claim_fail(reason_code="CLAIM_LEDGER_UNMAPPED"):
    return type("R", (), {"passed": False, "reason_code": reason_code, "evidence": "vi phạm", "claim_ledger": []})()


def _mock_scoring_and_claim_gate_pass(monkeypatch):
    monkeypatch.setattr(O, "run_full_risk_score", lambda c: _low_score())
    monkeypatch.setattr(O, "score_claim_exposure_gate", lambda c: _claim_pass())
    monkeypatch.setattr(g, "rank_candidates", lambda cands: cands)


# =============================================================================
# run_full_risk_score()
# =============================================================================

def test_run_full_risk_score_all_pass_gives_low_tier(monkeypatch):
    candidate = _candidate()
    for name in ("score_c1", "score_c2", "score_c3", "score_c6"):
        monkeypatch.setattr(g, name, lambda c, n=name: _criterion(n[-2:].upper(), True))
    monkeypatch.setattr(O, "score_c4_adversarial", lambda c: _criterion("C4", True))
    monkeypatch.setattr(O, "score_c5_adjudicated", lambda c: _criterion("C5", True))
    monkeypatch.setattr(O, "score_c7_adversarial", lambda c: _criterion("C7", True))
    result = O.run_full_risk_score(candidate)
    assert result.tier == "LOW"
    assert result.failing_criteria == []
    assert result.scorer_version == g.SCORER_VERSION


def test_run_full_risk_score_structural_failure_gives_high_tier(monkeypatch):
    candidate = _candidate()
    monkeypatch.setattr(g, "score_c1", lambda c: _criterion("C1", True))
    monkeypatch.setattr(g, "score_c2", lambda c: _criterion("C2", True))
    monkeypatch.setattr(g, "score_c3", lambda c: _criterion("C3", True))
    monkeypatch.setattr(g, "score_c6", lambda c: _criterion("C6", False, "role chưa cross-verified"))
    monkeypatch.setattr(O, "score_c4_adversarial", lambda c: _criterion("C4", True))
    monkeypatch.setattr(O, "score_c5_adjudicated", lambda c: _criterion("C5", True))
    monkeypatch.setattr(O, "score_c7_adversarial", lambda c: _criterion("C7", True))
    result = O.run_full_risk_score(candidate)
    assert result.tier == "HIGH"
    assert "C6" in result.failing_criteria
    assert any("C6" in t for t in result.high_risk_triggers)


def test_run_full_risk_score_medium_eligible_only_gives_medium_tier(monkeypatch):
    candidate = _candidate()
    monkeypatch.setattr(g, "score_c1", lambda c: _criterion("C1", False, "nguồn yếu"))
    monkeypatch.setattr(g, "score_c2", lambda c: _criterion("C2", True))
    monkeypatch.setattr(g, "score_c3", lambda c: _criterion("C3", True))
    monkeypatch.setattr(g, "score_c6", lambda c: _criterion("C6", True))
    monkeypatch.setattr(O, "score_c4_adversarial", lambda c: _criterion("C4", True))
    monkeypatch.setattr(O, "score_c5_adjudicated", lambda c: _criterion("C5", True))
    monkeypatch.setattr(O, "score_c7_adversarial", lambda c: _criterion("C7", True))
    result = O.run_full_risk_score(candidate)
    assert result.tier == "MEDIUM"
    assert result.high_risk_triggers == []  # C1 không phải STRUCTURAL


# =============================================================================
# run_cl_case_gate() -- deficit validation (regression High #2)
# =============================================================================

def test_run_cl_case_gate_rejects_negative_deficit():
    with pytest.raises(ValueError):
        O.run_cl_case_gate([_candidate()], g.CaseLedger({}), deficit=-1)


def test_run_cl_case_gate_rejects_non_int_deficit():
    with pytest.raises(ValueError):
        O.run_cl_case_gate([_candidate()], g.CaseLedger({}), deficit=1.5)
    with pytest.raises(ValueError):
        O.run_cl_case_gate([_candidate()], g.CaseLedger({}), deficit="5")


def test_run_cl_case_gate_accepts_zero_deficit(monkeypatch):
    result = O.run_cl_case_gate([], g.CaseLedger({}), deficit=0)
    assert result.auto_selected == []


# =============================================================================
# Dedupe routing (bao gồm regression High #3: intra-batch dedupe)
# =============================================================================

def test_run_cl_case_gate_rejects_duplicate_without_scoring(monkeypatch):
    candidate = _candidate()
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: _dedupe_result(is_duplicate=True))
    scoring_called = MagicMock()
    monkeypatch.setattr(O, "run_full_risk_score", lambda c: scoring_called() or None)

    result = O.run_cl_case_gate([candidate], g.CaseLedger({}), deficit=5)
    assert len(result.rejected_duplicate) == 1
    assert result.rejected_duplicate[0][0].case_id == "c1"
    scoring_called.assert_not_called()  # dedupe reject -> KHÔNG tốn chi phí scoring
    assert any(e["outcome"] == "REJECTED_DUPLICATE" for e in result.audit_log)


def test_run_cl_case_gate_escalates_low_confidence_dedupe(monkeypatch):
    candidate = _candidate()
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: _dedupe_result(confidence="low"))
    result = O.run_cl_case_gate([candidate], g.CaseLedger({}), deficit=5)
    assert len(result.escalated_low_confidence_dedupe) == 1


def test_run_cl_case_gate_intra_batch_dedupe_catches_same_case_key(monkeypatch):
    """Regression High #3: 2 candidate CÙNG case_key trong 1 lần gọi (ledger
    chưa kịp cập nhật giữa 2 candidate) -- candidate THỨ 2 PHẢI bị reject,
    KHÔNG được cùng lọt qua với candidate đầu."""
    same_key_candidates = [_candidate("c1", case_key="SAME_KEY"), _candidate("c2", case_key="SAME_KEY")]
    dedupe_calls = []
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: dedupe_calls.append(c.case_id) or _dedupe_result())
    _mock_scoring_and_claim_gate_pass(monkeypatch)
    monkeypatch.setattr(O, "generate_cl_final_content", lambda c, **kw: CG.CLGenerationResult(True, "s", {"title": "t"}, None, {}, {}))
    monkeypatch.setattr(O, "run_phase_a_final_review", lambda c, s, e: L.PhaseAFinalReviewResult(True, None, "ok", "h"))

    result = O.run_cl_case_gate(same_key_candidates, g.CaseLedger({}), deficit=5)
    assert dedupe_calls == ["c1"]  # candidate thứ 2 KHÔNG tốn chi phí gọi dedupe_against_ledger (chặn sớm hơn)
    assert len(result.auto_selected) == 1
    assert result.auto_selected[0][0].case_id == "c1"
    assert any(item[0].case_id == "c2" and item[1].method == "intra_batch_case_key_match" for item in result.rejected_duplicate)


def test_run_cl_case_gate_different_case_keys_both_proceed(monkeypatch):
    candidates = [_candidate("c1", case_key="KEY1"), _candidate("c2", case_key="KEY2")]
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: _dedupe_result())
    _mock_scoring_and_claim_gate_pass(monkeypatch)
    monkeypatch.setattr(O, "generate_cl_final_content", lambda c, **kw: CG.CLGenerationResult(True, "s", {"title": "t"}, None, {}, {}))
    monkeypatch.setattr(O, "run_phase_a_final_review", lambda c, s, e: L.PhaseAFinalReviewResult(True, None, "ok", "h"))
    result = O.run_cl_case_gate(candidates, g.CaseLedger({}), deficit=5)
    assert len(result.auto_selected) == 2
    assert result.rejected_duplicate == []


# =============================================================================
# Tier routing (bao gồm regression Medium #5: unknown tier fail-closed)
# =============================================================================

def test_run_cl_case_gate_escalates_high_tier_without_generation(monkeypatch):
    candidate = _candidate()
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: _dedupe_result())
    monkeypatch.setattr(O, "run_full_risk_score", lambda c: g.RiskScoreResult(
        tier="HIGH", criteria=[], failing_criteria=["C6"], high_risk_triggers=["C6: x"],
        rationale="r", scorer_version="v", allowlist_version="v", scored_at="t",
    ))
    generation_called = MagicMock()
    monkeypatch.setattr(O, "generate_cl_final_content", lambda *a, **kw: generation_called() or None)

    result = O.run_cl_case_gate([candidate], g.CaseLedger({}), deficit=5)
    assert len(result.escalated_high) == 1
    generation_called.assert_not_called()  # HIGH tier -> KHÔNG tự sinh nội dung


def test_run_cl_case_gate_unknown_tier_fails_closed_to_escalated_high(monkeypatch):
    """Regression Medium #5: tier lạ/rỗng (không phải LOW/MEDIUM/HIGH) PHẢI
    fail-closed như HIGH, KHÔNG được âm thầm coi là LOW rồi đi generate."""
    candidate = _candidate()
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: _dedupe_result())
    monkeypatch.setattr(O, "run_full_risk_score", lambda c: g.RiskScoreResult(
        tier="", criteria=[], failing_criteria=[], high_risk_triggers=[],
        rationale="r", scorer_version="v", allowlist_version="v", scored_at="t",
    ))
    generation_called = MagicMock()
    monkeypatch.setattr(O, "generate_cl_final_content", lambda *a, **kw: generation_called() or None)

    result = O.run_cl_case_gate([candidate], g.CaseLedger({}), deficit=5)
    assert len(result.escalated_high) == 1
    generation_called.assert_not_called()


# =============================================================================
# Claim-and-Exposure Gate routing (regression High #1)
# =============================================================================

def test_run_cl_case_gate_escalates_claim_exposure_gate_failure_before_generation(monkeypatch):
    """Regression High #1: bản đầu import score_claim_exposure_gate NHƯNG
    KHÔNG BAO GIỜ gọi -- case LOW-tier nhưng fail claim-gate PHẢI bị chặn
    TRƯỚC generation, không lãng phí chi phí generate."""
    candidate = _candidate()
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: _dedupe_result())
    monkeypatch.setattr(O, "run_full_risk_score", lambda c: _low_score())
    monkeypatch.setattr(O, "score_claim_exposure_gate", lambda c: _claim_fail("NECESSITY_NOT_VERIFIED"))
    generation_called = MagicMock()
    monkeypatch.setattr(O, "generate_cl_final_content", lambda *a, **kw: generation_called() or None)

    result = O.run_cl_case_gate([candidate], g.CaseLedger({}), deficit=5)
    assert len(result.escalated_claim_exposure_failed) == 1
    assert result.escalated_claim_exposure_failed[0][1].reason_code == "NECESSITY_NOT_VERIFIED"
    generation_called.assert_not_called()
    assert any(e["outcome"] == "ESCALATED_NECESSITY_NOT_VERIFIED" for e in result.audit_log)


def test_run_cl_case_gate_claim_exposure_gate_pass_proceeds_to_generation(monkeypatch):
    candidate = _candidate()
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: _dedupe_result())
    _mock_scoring_and_claim_gate_pass(monkeypatch)
    monkeypatch.setattr(O, "generate_cl_final_content", lambda c, **kw: CG.CLGenerationResult(True, "s", {"title": "t"}, None, {}, {}))
    monkeypatch.setattr(O, "run_phase_a_final_review", lambda c, s, e: L.PhaseAFinalReviewResult(True, None, "ok", "h"))
    result = O.run_cl_case_gate([candidate], g.CaseLedger({}), deficit=5)
    assert len(result.auto_selected) == 1


# =============================================================================
# Deficit cap + backfill (regression Medium #6/#7)
# =============================================================================

def test_run_cl_case_gate_backfills_from_next_ranked_on_generation_failure(monkeypatch):
    """Regression Medium #7: candidate hạng 1 generation FAIL -- PHẢI thử
    candidate hạng 2 (backfill), KHÔNG dừng lại với deficit chưa lấp dù còn
    candidate LOW-tier hợp lệ khác."""
    candidates = [_candidate("c1"), _candidate("c2")]
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: _dedupe_result())
    _mock_scoring_and_claim_gate_pass(monkeypatch)

    def fake_generate(c, **kw):
        if c.case_id == "c1":
            return CG.CLGenerationResult(False, None, None, "SCRIPT_GENERATION_FAILED", {}, None)
        return CG.CLGenerationResult(True, "s", {"title": "t"}, None, {}, {})

    monkeypatch.setattr(O, "generate_cl_final_content", fake_generate)
    monkeypatch.setattr(O, "run_phase_a_final_review", lambda c, s, e: L.PhaseAFinalReviewResult(True, None, "ok", "h"))

    result = O.run_cl_case_gate(candidates, g.CaseLedger({}), deficit=1)
    assert len(result.auto_selected) == 1
    assert result.auto_selected[0][0].case_id == "c2"  # backfill thành công
    assert len(result.escalated_generation_failed) == 1
    assert result.escalated_generation_failed[0][0].case_id == "c1"


def test_run_cl_case_gate_defers_low_tier_candidates_beyond_deficit(monkeypatch):
    """Regression Medium #6: LOW-tier candidate hợp lệ nhưng KHÔNG được thử
    (đã đủ deficit) PHẢI vào deferred_deficit, KHÔNG bị bỏ sót hoàn toàn."""
    candidates = [_candidate("c1"), _candidate("c2"), _candidate("c3")]
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: _dedupe_result())
    _mock_scoring_and_claim_gate_pass(monkeypatch)
    monkeypatch.setattr(O, "generate_cl_final_content", lambda c, **kw: CG.CLGenerationResult(True, "s", {"title": "t"}, None, {}, {}))
    monkeypatch.setattr(O, "run_phase_a_final_review", lambda c, s, e: L.PhaseAFinalReviewResult(True, None, "ok", "h"))

    result = O.run_cl_case_gate(candidates, g.CaseLedger({}), deficit=1)
    assert len(result.auto_selected) == 1
    assert len(result.deferred_deficit) == 2
    deferred_ids = {c.case_id for c in result.deferred_deficit}
    assert deferred_ids == {"c2", "c3"}
    assert any(e["outcome"] == "DEFERRED_DEFICIT" for e in result.audit_log)


# =============================================================================
# Generation / Phase A review failure routing (bao gồm regression Low/Medium
# #8: escalated_phase_a_review_failed TÁCH khỏi escalated_generation_failed)
# =============================================================================

def test_run_cl_case_gate_escalates_generation_failure(monkeypatch):
    candidate = _candidate()
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: _dedupe_result())
    _mock_scoring_and_claim_gate_pass(monkeypatch)
    monkeypatch.setattr(O, "generate_cl_final_content", lambda c, **kw: CG.CLGenerationResult(False, None, None, "SCRIPT_GENERATION_FAILED", {}, None))
    review_called = MagicMock()
    monkeypatch.setattr(O, "run_phase_a_final_review", lambda *a: review_called() or None)

    result = O.run_cl_case_gate([candidate], g.CaseLedger({}), deficit=5)
    assert len(result.escalated_generation_failed) == 1
    assert result.escalated_generation_failed[0][1].reason == "SCRIPT_GENERATION_FAILED"
    review_called.assert_not_called()  # generation fail -> KHÔNG chạy Phase A review


def test_run_cl_case_gate_escalates_phase_a_review_failure_separately(monkeypatch):
    candidate = _candidate()
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: _dedupe_result())
    _mock_scoring_and_claim_gate_pass(monkeypatch)
    monkeypatch.setattr(O, "generate_cl_final_content", lambda c, **kw: CG.CLGenerationResult(True, "script", {"title": "t"}, None, {}, {}))
    monkeypatch.setattr(O, "run_phase_a_final_review", lambda c, s, e: L.PhaseAFinalReviewResult(False, "PHASE_A_C4_FAILED", "vi phạm C4"))

    result = O.run_cl_case_gate([candidate], g.CaseLedger({}), deficit=5)
    assert result.escalated_generation_failed == []
    assert len(result.escalated_phase_a_review_failed) == 1
    failed_candidate, failed_gen_result, failed_review_result = result.escalated_phase_a_review_failed[0]
    assert failed_review_result.reason_code == "PHASE_A_C4_FAILED"
    assert failed_gen_result.final_script == "script"  # đối xứng với auto_selected: giữ nội dung đã fail để người review xem lại
    assert result.auto_selected == []


def test_run_cl_case_gate_full_pass_reaches_auto_selected(monkeypatch):
    candidate = _candidate()
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: _dedupe_result())
    _mock_scoring_and_claim_gate_pass(monkeypatch)
    monkeypatch.setattr(O, "generate_cl_final_content", lambda c, **kw: CG.CLGenerationResult(True, "script an toàn", {"title": "t"}, None, {}, {}))
    monkeypatch.setattr(O, "run_phase_a_final_review", lambda c, s, e: L.PhaseAFinalReviewResult(True, None, "PASS", "hash123"))

    result = O.run_cl_case_gate([candidate], g.CaseLedger({}), deficit=5)
    assert len(result.auto_selected) == 1
    selected_candidate, gen_result, review_result = result.auto_selected[0]
    assert selected_candidate.case_id == "c1"
    assert review_result.reviewed_editorial_hash == "hash123"
    assert any(e["outcome"] == "PASSED_READY_FOR_PHASE_B" for e in result.audit_log)


def test_run_cl_case_gate_auto_selected_preserves_approved_content(monkeypatch):
    """Regression cho HIGH mới ở review độc lập vòng 2 (Cursor/Grok):
    auto_selected KHÔNG được vứt mất final_script/final_editorial đã PASS
    -- Phase B (caller) cần đúng nội dung này để TTS/render, KHÔNG được
    phải regenerate (sẽ cho hash khác, không còn khớp reviewed_editorial_hash)."""
    candidate = _candidate()
    monkeypatch.setattr(g, "dedupe_against_ledger", lambda c, ledger: _dedupe_result())
    _mock_scoring_and_claim_gate_pass(monkeypatch)
    monkeypatch.setattr(O, "generate_cl_final_content", lambda c, **kw: CG.CLGenerationResult(
        True, "Kịch bản đã duyệt thật.", {"title": "Tiêu đề đã duyệt", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}, None, {}, {},
    ))
    monkeypatch.setattr(O, "run_phase_a_final_review", lambda c, s, e: L.PhaseAFinalReviewResult(True, None, "PASS", "hash123"))

    result = O.run_cl_case_gate([candidate], g.CaseLedger({}), deficit=5)
    _, gen_result, review_result = result.auto_selected[0]
    assert gen_result.final_script == "Kịch bản đã duyệt thật."
    assert gen_result.final_editorial["title"] == "Tiêu đề đã duyệt"
    assert gen_result.final_editorial["thumbnail_brief"] == "b"


def test_run_cl_case_gate_no_candidate_silently_dropped(monkeypatch):
    """Mọi candidate PHẢI xuất hiện Ở ĐÂU ĐÓ trong kết quả (auto_selected,
    deferred_deficit, HOẶC 1 trong các escalated_*/rejected_*) -- không rơi
    rớt case nào, VÀ mọi candidate có ít nhất 1 dòng audit_log."""
    candidates = [_candidate("dup"), _candidate("lowconf"), _candidate("high"), _candidate("claimfail"), _candidate("genfail"), _candidate("ok")]

    def fake_dedupe(c, ledger):
        return {
            "dup": _dedupe_result(is_duplicate=True),
            "lowconf": _dedupe_result(confidence="low"),
        }.get(c.case_id, _dedupe_result())

    def fake_score(c):
        if c.case_id == "high":
            return g.RiskScoreResult(tier="HIGH", criteria=[], failing_criteria=["C6"], high_risk_triggers=[], rationale="r", scorer_version="v", allowlist_version="v", scored_at="t")
        return _low_score()

    def fake_claim_gate(c):
        return _claim_fail() if c.case_id == "claimfail" else _claim_pass()

    def fake_generate(c, **kw):
        if c.case_id == "genfail":
            return CG.CLGenerationResult(False, None, None, "SCRIPT_GENERATION_FAILED", {}, None)
        return CG.CLGenerationResult(True, "script", {"title": "t"}, None, {}, {})

    monkeypatch.setattr(g, "dedupe_against_ledger", fake_dedupe)
    monkeypatch.setattr(O, "run_full_risk_score", fake_score)
    monkeypatch.setattr(O, "score_claim_exposure_gate", fake_claim_gate)
    monkeypatch.setattr(g, "rank_candidates", lambda cands: cands)
    monkeypatch.setattr(O, "generate_cl_final_content", fake_generate)
    monkeypatch.setattr(O, "run_phase_a_final_review", lambda c, s, e: L.PhaseAFinalReviewResult(True, None, "ok", "h"))

    result = O.run_cl_case_gate(candidates, g.CaseLedger({}), deficit=5)
    all_ids = set()
    for bucket in (result.auto_selected, result.escalated_high, result.escalated_medium_exhausted,
                   result.rejected_duplicate, result.escalated_low_confidence_dedupe,
                   result.escalated_claim_exposure_failed, result.escalated_generation_failed,
                   result.escalated_phase_a_review_failed):
        for item in bucket:
            all_ids.add(item[0].case_id)
    for c in result.deferred_deficit:
        all_ids.add(c.case_id)
    assert all_ids == {"dup", "lowconf", "high", "claimfail", "genfail", "ok"}

    logged_ids = {e["case_id"] for e in result.audit_log}
    assert {"dup", "lowconf", "high", "claimfail", "genfail", "ok"} <= logged_ids
