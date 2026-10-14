"""Test cho cl_claim_exposure_gate.py (§1.6 Claim-and-Exposure Gate, Phase A
text-only). Mock ceg._run_agy/_run_codex (module-level trong
cl_claim_exposure_gate) đúng pattern test_cl_risk_gate_verification.py."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import cl_risk_gate as g  # noqa: E402
import cl_claim_exposure_gate as ceg  # noqa: E402


def _fake_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False)


def _claim_dict(category=None, about=None, evidence_fact_ids=None, strength=None):
    return {"category": category, "about_individual": about, "evidence_fact_ids": evidence_fact_ids or [], "entailment_strength": strength}


def _segment_response(*claims_per_segment):
    """claims_per_segment: 1 list các claim dict (từ _claim_dict) cho MỖI
    đoạn theo thứ tự -- builds full {"segments": [...]} response đúng
    schema mới (0..N claim/đoạn)."""
    return {"segments": [{"index": i, "claims": list(claims)} for i, claims in enumerate(claims_per_segment)]}


def _candidate(named_individuals=None, core_facts=None, draft=""):
    return g.CandidateCase(
        case_id="c1", case_key="c1", working_title="Vụ án Test",
        named_individuals=named_individuals or [], core_facts=core_facts or [],
        risk_review_draft=draft,
    )


def _victim(name="Nguyễn Văn A"):
    return g.NamedIndividual(canonical_name=name, identity_confidence="high", role="victim")


# =============================================================================
# _segment_script()
# =============================================================================

def test_segment_script_splits_on_newline():
    segs = ceg._segment_script("Câu 1.\nCâu 2.\nCâu 3.")
    assert segs == ["Câu 1.", "Câu 2.", "Câu 3."]


def test_segment_script_empty_or_non_string_returns_empty_list():
    assert ceg._segment_script("") == []
    assert ceg._segment_script("   ") == []
    assert ceg._segment_script(None) == []


# =============================================================================
# _mechanical_second_pass_trigger()
# =============================================================================

def test_mechanical_trigger_question_mark():
    candidate = _candidate()
    assert ceg._mechanical_second_pass_trigger("Chuyện gì đã xảy ra?", candidate) is True


def test_mechanical_trigger_legal_term():
    candidate = _candidate()
    assert ceg._mechanical_second_pass_trigger("Người này bị nghi phạm liên quan.", candidate) is True


def test_mechanical_trigger_evaluative_adjective():
    candidate = _candidate()
    assert ceg._mechanical_second_pass_trigger("Hành vi này thật tàn ác.", candidate) is True


def test_mechanical_trigger_person_reference():
    candidate = _candidate()
    assert ceg._mechanical_second_pass_trigger("Ông ta rời khỏi hiện trường.", candidate) is True


def test_mechanical_trigger_none_for_plain_context_sentence():
    candidate = _candidate()
    assert ceg._mechanical_second_pass_trigger("Sự kiện xảy ra vào năm 2020 tại địa phương.", candidate) is False


def test_mechanical_trigger_canonical_name_regression():
    """Codex review round 1, Blocker #1: probe chính xác reviewer đưa ra --
    "Nguyễn Văn A sở hữu công ty X." không chứa dấu ?/legal term/adjective/
    đại từ cố định, nhưng CHỨA canonical_name -- PHẢI trigger."""
    candidate = _candidate(named_individuals=[_victim("Nguyễn Văn A")])
    assert ceg._mechanical_second_pass_trigger("Nguyễn Văn A sở hữu công ty X.", candidate) is True


def test_mechanical_trigger_short_form_alias_regression():
    person = g.NamedIndividual(canonical_name="Nguyễn Văn A", identity_confidence="high", role="victim", short_form_alias="A")
    candidate = _candidate(named_individuals=[person])
    assert ceg._mechanical_second_pass_trigger("A sở hữu công ty X.", candidate) is True


def test_mechanical_trigger_name_case_insensitive():
    candidate = _candidate(named_individuals=[_victim("Nguyễn Văn A")])
    assert ceg._mechanical_second_pass_trigger("nguyễn văn a sở hữu công ty x.", candidate) is True


# =============================================================================
# build_claim_ledger()
# =============================================================================

def test_build_claim_ledger_fails_closed_on_empty_draft():
    candidate = _candidate(draft="   ")
    with pytest.raises(ceg.ClaimGateError):
        ceg.build_claim_ledger(candidate)


def test_build_claim_ledger_fails_closed_on_agy_exception(monkeypatch):
    def _boom(prompt):
        raise RuntimeError("lỗi giả lập")
    monkeypatch.setattr(ceg, "_run_agy", _boom)
    candidate = _candidate(named_individuals=[_victim()], draft="Câu 1.")
    with pytest.raises(ceg.ClaimGateError):
        ceg.build_claim_ledger(candidate)


def test_build_claim_ledger_fails_closed_on_missing_index(monkeypatch):
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: _fake_json({"segments": [{"index": 0, "claims": []}]}))
    candidate = _candidate(named_individuals=[_victim()], draft="Câu 1.\nCâu 2.")
    with pytest.raises(ceg.ClaimGateError):
        ceg.build_claim_ledger(candidate)


def test_build_claim_ledger_fails_closed_on_duplicate_index(monkeypatch):
    """Codex review round 1, High #4: index trùng lặp phải raise lỗi rõ
    ràng, không được để dict âm thầm ghi đè (mất hẳn 1 segment)."""
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: _fake_json({"segments": [
        {"index": 0, "claims": []}, {"index": 0, "claims": []},
    ]}))
    candidate = _candidate(named_individuals=[_victim()], draft="Câu 1.\nCâu 2.")
    with pytest.raises(ceg.ClaimGateError):
        ceg.build_claim_ledger(candidate)


def test_build_claim_ledger_fails_closed_on_claims_not_list(monkeypatch):
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: _fake_json({"segments": [{"index": 0, "claims": "not a list"}]}))
    candidate = _candidate(named_individuals=[_victim()], draft="Câu 1.")
    with pytest.raises(ceg.ClaimGateError):
        ceg.build_claim_ledger(candidate)


def test_build_claim_ledger_fails_closed_on_non_dict_response(monkeypatch):
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: "not json {{{")
    candidate = _candidate(named_individuals=[_victim()], draft="Câu 1.")
    with pytest.raises(ceg.ClaimGateError):
        ceg.build_claim_ledger(candidate)


def test_build_claim_ledger_skips_segments_with_no_claims(monkeypatch):
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: _fake_json(_segment_response([], [])))
    candidate = _candidate(named_individuals=[_victim()], draft="Bối cảnh chung.\nThời tiết hôm đó xấu.")
    claims = ceg.build_claim_ledger(candidate)
    assert claims == []


def test_build_claim_ledger_keeps_claim_bearing_segment(monkeypatch):
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: _fake_json(_segment_response(
        [_claim_dict(category="identity", about="Nguyễn Văn A", evidence_fact_ids=["F1"], strength="full")],
    )))
    candidate = _candidate(named_individuals=[_victim()], core_facts=[g.CoreFact(fact_id="F1", statement="A là nạn nhân", fact_type="identity")], draft="Nguyễn Văn A là nạn nhân.")
    claims = ceg.build_claim_ledger(candidate)
    assert len(claims) == 1
    assert claims[0].category == "identity"
    assert claims[0].about_individual == "Nguyễn Văn A"
    assert claims[0].evidence_fact_ids == ["F1"]


def test_build_claim_ledger_multi_claim_per_segment_regression():
    """Codex review round 1, Blocker #2: 1 đoạn có thể chứa NHIỀU claim về
    NHIỀU người -- phải tạo NHIỀU ClaimRecord, không chỉ 1."""
    import cl_claim_exposure_gate as ceg_mod

    def _fake_agy(prompt):
        return _fake_json(_segment_response([
            _claim_dict(category="guilt_or_culpability", about="A", evidence_fact_ids=["F1"], strength="full"),
            _claim_dict(category="chronology", about="B", evidence_fact_ids=["F2"], strength="full"),
        ]))
    person_a = g.NamedIndividual(canonical_name="A", identity_confidence="high", role="convicted_perpetrator")
    person_b = g.NamedIndividual(canonical_name="B", identity_confidence="high", role="acquitted")
    candidate = _candidate(
        named_individuals=[person_a, person_b],
        core_facts=[g.CoreFact(fact_id="F1", statement="A gây án", fact_type="t"), g.CoreFact(fact_id="F2", statement="B được tuyên vô tội", fact_type="t")],
        draft="A cáo buộc gây án, còn B được tòa tuyên vô tội.",
    )
    import unittest.mock as mock
    with mock.patch.object(ceg_mod, "_run_agy", _fake_agy):
        claims = ceg_mod.build_claim_ledger(candidate)
    assert len(claims) == 2
    assert {c.about_individual for c in claims} == {"A", "B"}


def test_build_claim_ledger_invalid_category_coerced_to_other_claim_bearing(monkeypatch):
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: _fake_json(_segment_response(
        [_claim_dict(category="not_a_real_category", about="Nguyễn Văn A")],
    )))
    candidate = _candidate(named_individuals=[_victim()], draft="Câu 1.")
    claims = ceg.build_claim_ledger(candidate)
    assert claims[0].category == "other_claim_bearing"


def test_build_claim_ledger_unresolved_about_individual_kept_as_raw_string():
    """Codex review round 1, High #2: tên không khớp danh sách phải GIỮ
    NGUYÊN chuỗi thô (không âm thầm đổi thành None) để bị bắt là unmapped
    ở find_unmapped_or_unsupported_claims(), không lặng lẽ bị bỏ qua."""
    import cl_claim_exposure_gate as ceg_mod
    import unittest.mock as mock

    def _fake_agy(prompt):
        return _fake_json(_segment_response([_claim_dict(category="identity", about="Người Lạ Không Có Trong Danh Sách")]))
    candidate = _candidate(named_individuals=[_victim()], draft="Câu 1.")
    with mock.patch.object(ceg_mod, "_run_agy", _fake_agy):
        claims = ceg_mod.build_claim_ledger(candidate)
    assert claims[0].about_individual == "Người Lạ Không Có Trong Danh Sách"


def test_build_claim_ledger_about_individual_case_insensitive_resolves_to_canonical():
    import cl_claim_exposure_gate as ceg_mod
    import unittest.mock as mock

    def _fake_agy(prompt):
        return _fake_json(_segment_response([_claim_dict(category="identity", about="nguyễn văn a")]))
    candidate = _candidate(named_individuals=[_victim("Nguyễn Văn A")], draft="Câu 1.")
    with mock.patch.object(ceg_mod, "_run_agy", _fake_agy):
        claims = ceg_mod.build_claim_ledger(candidate)
    assert claims[0].about_individual == "Nguyễn Văn A"


def test_build_claim_ledger_second_pass_overrides_first_pass(monkeypatch):
    """Segment "Ông ta là nghi phạm?" bị pass 1 gắn nhầm 0 claim (agy) --
    trigger cơ học (dấu ?, "nghi phạm", "ông") phải kích hoạt pass 2
    (codex) re-classify thành có claim thật."""
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: _fake_json(_segment_response([])))
    monkeypatch.setattr(ceg, "_run_codex", lambda prompt: _fake_json(_segment_response(
        [_claim_dict(category="guilt_or_culpability", about="Nguyễn Văn A", evidence_fact_ids=["F1"], strength="partial")],
    )))
    candidate = _candidate(named_individuals=[_victim()], draft="Ông ta là nghi phạm?")
    claims = ceg.build_claim_ledger(candidate)
    assert len(claims) == 1
    assert claims[0].category == "guilt_or_culpability"


def test_build_claim_ledger_non_dict_claim_element_fails_closed(monkeypatch):
    """Codex review round 2, High #4: trước đây phần tử claims không phải
    dict bị ÂM THẦM bỏ qua (list vẫn truthy -> không trigger second-pass
    -> claim thật biến mất, gate PASS oan -- reviewer tái hiện probe
    end-to-end thật). Giờ PHẢI raise ClaimGateError, fail-closed toàn bộ
    candidate thay vì mất 1 claim trong im lặng."""
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: _fake_json({"segments": [{"index": 0, "claims": ["not a dict"]}]}))
    candidate = _candidate(named_individuals=[_victim()], draft="Câu 1.")
    with pytest.raises(ceg.ClaimGateError):
        ceg.build_claim_ledger(candidate)


def test_score_claim_exposure_gate_round2_regression_malformed_claim_element_fails_closed_not_pass(monkeypatch):
    """Đúng end-to-end probe reviewer dùng để tái hiện PASS oan ở vòng 2:
    draft="Nguyễn Văn A sở hữu công ty X.", pass1 trả 1 claim malformed
    (không phải dict) -- TRƯỚC ĐÂY: passed=True, claim_ledger=[] (claim
    thật biến mất). GIỜ: phải fail-closed, KHÔNG được PASS."""
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: _fake_json({"segments": [{"index": 0, "claims": ["malformed-but-truthy"]}]}))
    monkeypatch.setattr(ceg, "_run_codex", lambda prompt: _fake_json({"inflated": False, "inflated_phrases": []}))
    candidate = _candidate(named_individuals=[_victim("Nguyễn Văn A")], draft="Nguyễn Văn A sở hữu công ty X.")
    result = ceg.score_claim_exposure_gate(candidate)
    assert result.passed is False


def test_build_claim_ledger_evidence_fact_ids_filters_non_string_elements(monkeypatch):
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: _fake_json(_segment_response(
        [_claim_dict(category="identity", about="Nguyễn Văn A", evidence_fact_ids=["F1", None, 123, ["F2"]], strength="full")],
    )))
    candidate = _candidate(named_individuals=[_victim()], draft="Câu 1.")
    claims = ceg.build_claim_ledger(candidate)
    assert claims[0].evidence_fact_ids == ["F1"]


# =============================================================================
# verify_entailment_strength()
# =============================================================================

def _claim(**overrides):
    base = dict(claim_id="C1", text="claim text", surface="script", segment_index=0, category="identity", about_individual="Nguyễn Văn A", evidence_fact_ids=["F1"], entailment_strength="full", necessity_verified=None, verified=False)
    base.update(overrides)
    return g.ClaimRecord(**base)


def test_verify_entailment_strength_downgrades_to_challenged_value(monkeypatch):
    monkeypatch.setattr(ceg, "_run_codex", lambda prompt: _fake_json({"entailment_strength": "partial"}))
    candidate = _candidate(core_facts=[g.CoreFact(fact_id="F1", statement="x", fact_type="t")])
    result = ceg.verify_entailment_strength([_claim(entailment_strength="full")], candidate)
    assert result[0].entailment_strength == "partial"


def test_verify_entailment_strength_keeps_lower_of_self_reported_and_challenged(monkeypatch):
    """Self-reported 'partial' nhưng codex phản biện 'full' -- PHẢI giữ
    'partial' (thấp hơn, bảo thủ hơn), không nâng lên."""
    monkeypatch.setattr(ceg, "_run_codex", lambda prompt: _fake_json({"entailment_strength": "full"}))
    candidate = _candidate(core_facts=[g.CoreFact(fact_id="F1", statement="x", fact_type="t")])
    result = ceg.verify_entailment_strength([_claim(entailment_strength="partial")], candidate)
    assert result[0].entailment_strength == "partial"


def test_verify_entailment_strength_skips_claims_with_no_evidence():
    candidate = _candidate()
    result = ceg.verify_entailment_strength([_claim(entailment_strength="none", evidence_fact_ids=[])], candidate)
    assert result[0].entailment_strength == "none"


def test_verify_entailment_strength_fails_closed_to_none_on_fabricated_fact_id():
    candidate = _candidate(core_facts=[])  # F1 không tồn tại
    result = ceg.verify_entailment_strength([_claim(entailment_strength="full", evidence_fact_ids=["F1"])], candidate)
    assert result[0].entailment_strength == "none"


def test_verify_entailment_strength_fails_closed_on_codex_exception(monkeypatch):
    def _boom(prompt):
        raise RuntimeError("lỗi giả lập")
    monkeypatch.setattr(ceg, "_run_codex", _boom)
    candidate = _candidate(core_facts=[g.CoreFact(fact_id="F1", statement="x", fact_type="t")])
    result = ceg.verify_entailment_strength([_claim(entailment_strength="full")], candidate)
    assert result[0].entailment_strength == "none"


# =============================================================================
# find_unmapped_or_unsupported_claims()
# =============================================================================

def test_find_unmapped_flags_unresolved_about_individual():
    """Codex review round 1, High #2: about_individual không resolve được
    thành người thật PHẢI tự nó là violation, không được lọt qua chỉ vì
    evidence/category/strength khác đều hợp lệ."""
    candidate = _candidate(named_individuals=[_victim("Nguyễn Văn A")])
    violations = ceg.find_unmapped_or_unsupported_claims([_claim(about_individual="Người Không Tồn Tại", entailment_strength="full", evidence_fact_ids=["F1"], category="identity")], candidate)
    assert len(violations) == 1


def test_find_unmapped_flags_none_about_individual():
    candidate = _candidate(named_individuals=[_victim("Nguyễn Văn A")])
    violations = ceg.find_unmapped_or_unsupported_claims([_claim(about_individual=None)], candidate)
    assert len(violations) == 1


def test_find_unmapped_flags_claim_without_evidence_ids():
    candidate = _candidate(named_individuals=[_victim("Nguyễn Văn A")])
    violations = ceg.find_unmapped_or_unsupported_claims([_claim(about_individual="Nguyễn Văn A", evidence_fact_ids=[])], candidate)
    assert len(violations) == 1


def test_find_unmapped_flags_other_claim_bearing_category():
    candidate = _candidate(named_individuals=[_victim("Nguyễn Văn A")])
    violations = ceg.find_unmapped_or_unsupported_claims([_claim(about_individual="Nguyễn Văn A", category="other_claim_bearing")], candidate)
    assert len(violations) == 1


def test_find_unmapped_flags_partial_or_none_entailment():
    candidate = _candidate(named_individuals=[_victim("Nguyễn Văn A")])
    violations = ceg.find_unmapped_or_unsupported_claims([_claim(about_individual="Nguyễn Văn A", entailment_strength="partial")], candidate)
    assert len(violations) == 1
    violations = ceg.find_unmapped_or_unsupported_claims([_claim(about_individual="Nguyễn Văn A", entailment_strength="none")], candidate)
    assert len(violations) == 1


def test_find_unmapped_clean_for_full_entailment_with_evidence_and_resolved_identity():
    candidate = _candidate(named_individuals=[_victim("Nguyễn Văn A")])
    violations = ceg.find_unmapped_or_unsupported_claims([_claim(about_individual="Nguyễn Văn A", entailment_strength="full", evidence_fact_ids=["F1"], category="identity")], candidate)
    assert violations == []


# =============================================================================
# check_necessity() / find_necessity_violations()
# =============================================================================

def test_check_necessity_skips_non_sensitive_category():
    candidate = _candidate()
    claims = ceg.check_necessity([_claim(category="identity")], candidate)
    assert claims[0].necessity_verified is None


def test_check_necessity_true_when_llm_says_necessary(monkeypatch):
    monkeypatch.setattr(ceg, "_run_codex", lambda prompt: _fake_json({"necessary": True}))
    candidate = _candidate()
    claims = ceg.check_necessity([_claim(category="victim_behavior")], candidate)
    assert claims[0].necessity_verified is True


def test_check_necessity_fails_closed_on_exception(monkeypatch):
    def _boom(prompt):
        raise RuntimeError("lỗi giả lập")
    monkeypatch.setattr(ceg, "_run_codex", _boom)
    candidate = _candidate()
    claims = ceg.check_necessity([_claim(category="sexual_conduct")], candidate)
    assert claims[0].necessity_verified is False


def test_check_necessity_fails_closed_on_non_bool_response(monkeypatch):
    monkeypatch.setattr(ceg, "_run_codex", lambda prompt: _fake_json({"necessary": "yes"}))
    candidate = _candidate()
    claims = ceg.check_necessity([_claim(category="biographical_location_detail")], candidate)
    assert claims[0].necessity_verified is False


def test_find_necessity_violations_flags_unverified_sensitive_claim():
    violations = ceg.find_necessity_violations([_claim(category="sexual_conduct", necessity_verified=False)])
    assert len(violations) == 1


def test_find_necessity_violations_clean_when_verified_true():
    violations = ceg.find_necessity_violations([_claim(category="sexual_conduct", necessity_verified=True)])
    assert violations == []


def test_find_necessity_violations_ignores_non_sensitive_category():
    violations = ceg.find_necessity_violations([_claim(category="identity", necessity_verified=None)])
    assert violations == []


# =============================================================================
# check_relative_associate_claims()
# =============================================================================

def test_relative_associate_violation_when_named_and_implicated():
    relative = g.NamedIndividual(canonical_name="Người Thân B", identity_confidence="high", role="named_relative_or_associate")
    candidate = _candidate(named_individuals=[relative])
    claims = [_claim(category="guilt_or_culpability", about_individual="Người Thân B")]
    violations = ceg.check_relative_associate_claims(claims, candidate)
    assert len(violations) == 1


def test_relative_associate_no_violation_when_category_not_emphasis():
    relative = g.NamedIndividual(canonical_name="Người Thân B", identity_confidence="high", role="named_relative_or_associate")
    candidate = _candidate(named_individuals=[relative])
    claims = [_claim(category="chronology", about_individual="Người Thân B")]
    assert ceg.check_relative_associate_claims(claims, candidate) == []


def test_relative_associate_no_violation_when_role_is_not_relative():
    person = g.NamedIndividual(canonical_name="Nguyễn Văn A", identity_confidence="high", role="victim")
    candidate = _candidate(named_individuals=[person])
    claims = [_claim(category="guilt_or_culpability", about_individual="Nguyễn Văn A")]
    assert ceg.check_relative_associate_claims(claims, candidate) == []


def test_relative_associate_no_violation_when_about_individual_none():
    candidate = _candidate(named_individuals=[])
    claims = [_claim(category="guilt_or_culpability", about_individual=None)]
    assert ceg.check_relative_associate_claims(claims, candidate) == []


# =============================================================================
# check_acquitted_disproportionate_emphasis()
# =============================================================================

def _acquitted(name="Nguyễn Văn A", cross_verified=True):
    rv = g.RoleVerificationRecord(role_cross_verified=cross_verified)
    return g.NamedIndividual(canonical_name=name, identity_confidence="high", role="acquitted", role_verification=rv)


def test_acquitted_emphasis_violation_opening_hook():
    candidate = _candidate(named_individuals=[_acquitted()])
    claims = [_claim(category="guilt_or_culpability", about_individual="Nguyễn Văn A", segment_index=0, text="A đã giết người.")]
    violations = ceg.check_acquitted_disproportionate_emphasis(claims, candidate)
    assert len(violations) == 1


def test_acquitted_emphasis_violation_late_underweighted_acquittal():
    candidate = _candidate(named_individuals=[_acquitted()])
    claims = [
        _claim(claim_id="C1", category="guilt_or_culpability", about_individual="Nguyễn Văn A", segment_index=4, text="A bị buộc tội giết người."),
        _claim(claim_id="C2", category="guilt_or_culpability", about_individual="Nguyễn Văn A", segment_index=5, text="A đã ra tay tàn nhẫn."),
        _claim(claim_id="C3", category="chronology", about_individual="Nguyễn Văn A", segment_index=9, text="A được tòa tuyên vô tội."),
    ]
    violations = ceg.check_acquitted_disproportionate_emphasis(claims, candidate)
    assert len(violations) == 1


def test_acquitted_emphasis_violation_repeated_more_in_guilt_isolated():
    """Cô lập RIÊNG điều kiện (c) -- không kích hoạt (a) (guilt claims
    không ở đoạn mở đầu) hay (b) (tha bổng được nhắc SỚM, không muộn)."""
    candidate = _candidate(named_individuals=[_acquitted()])
    claims = [
        _claim(claim_id="C0", category="chronology", about_individual="Nguyễn Văn A", segment_index=0, text="A ban đầu bị nghi ngờ nhưng sau đó được tòa tuyên vô tội."),
        _claim(claim_id="C1", category="guilt_or_culpability", about_individual="Nguyễn Văn A", segment_index=5, text="A bị nghi liên quan."),
        _claim(claim_id="C2", category="association", about_individual="Nguyễn Văn A", segment_index=6, text="A có liên hệ."),
    ]
    violations = ceg.check_acquitted_disproportionate_emphasis(claims, candidate)
    assert len(violations) == 1


def test_acquitted_emphasis_no_violation_when_balanced_and_not_in_opening():
    candidate = _candidate(named_individuals=[_acquitted()])
    claims = [
        _claim(claim_id="C1", category="chronology", about_individual="Nguyễn Văn A", segment_index=3, text="A xuất hiện trong vụ án."),
        _claim(claim_id="C2", category="guilt_or_culpability", about_individual="Nguyễn Văn A", segment_index=4, text="A từng bị nghi ngờ."),
        _claim(claim_id="C3", category="chronology", about_individual="Nguyễn Văn A", segment_index=5, text="Sau đó A được tòa tuyên vô tội."),
    ]
    violations = ceg.check_acquitted_disproportionate_emphasis(claims, candidate)
    assert violations == []


def test_acquitted_emphasis_ignores_non_acquitted_people():
    candidate = _candidate(named_individuals=[_victim()])
    claims = [_claim(category="guilt_or_culpability", about_individual="Nguyễn Văn A", segment_index=0)]
    assert ceg.check_acquitted_disproportionate_emphasis(claims, candidate) == []


def test_acquitted_emphasis_violation_when_role_not_cross_verified():
    """Codex review round 1, High #3: role='acquitted' nhưng CHƯA
    cross-verified -- PHẢI tự là 1 violation (fail-closed), không được
    âm thầm bỏ qua check cho người này."""
    candidate = _candidate(named_individuals=[_acquitted(cross_verified=False)])
    claims = []
    violations = ceg.check_acquitted_disproportionate_emphasis(claims, candidate)
    assert len(violations) == 1


def test_acquitted_emphasis_no_false_positive_when_role_verification_none():
    person = g.NamedIndividual(canonical_name="Nguyễn Văn A", identity_confidence="high", role="acquitted", role_verification=None)
    candidate = _candidate(named_individuals=[person])
    violations = ceg.check_acquitted_disproportionate_emphasis([], candidate)
    assert len(violations) == 1


# =============================================================================
# check_no_claim_inflation()
# =============================================================================

def test_no_claim_inflation_empty_surface_passes():
    passed, evidence = ceg.check_no_claim_inflation([], "   ", "script")
    assert passed is True


def test_no_claim_inflation_passes_when_llm_says_not_inflated(monkeypatch):
    monkeypatch.setattr(ceg, "_run_codex", lambda prompt: _fake_json({"inflated": False, "inflated_phrases": []}))
    passed, evidence = ceg.check_no_claim_inflation([_claim(entailment_strength="full")], "Nội dung script.", "script")
    assert passed is True


def test_no_claim_inflation_fails_when_llm_flags_inflation(monkeypatch):
    monkeypatch.setattr(ceg, "_run_codex", lambda prompt: _fake_json({"inflated": True, "inflated_phrases": ["kẻ giết người máu lạnh"]}))
    passed, evidence = ceg.check_no_claim_inflation([_claim(entailment_strength="full")], "Kẻ giết người máu lạnh.", "script")
    assert passed is False


def test_no_claim_inflation_fails_closed_on_exception(monkeypatch):
    def _boom(prompt):
        raise RuntimeError("lỗi giả lập")
    monkeypatch.setattr(ceg, "_run_codex", _boom)
    passed, evidence = ceg.check_no_claim_inflation([], "text", "script")
    assert passed is False


def test_no_claim_inflation_fails_closed_on_malformed_response(monkeypatch):
    monkeypatch.setattr(ceg, "_run_codex", lambda prompt: _fake_json({"foo": "bar"}))
    passed, evidence = ceg.check_no_claim_inflation([], "text", "script")
    assert passed is False


# =============================================================================
# score_claim_exposure_gate() -- orchestration + malformed-input fail-closed
# =============================================================================

def test_score_claim_exposure_gate_fails_closed_on_ledger_build_error():
    candidate = _candidate(draft="")
    result = ceg.score_claim_exposure_gate(candidate)
    assert result.passed is False
    assert result.reason_code == "CLAIM_LEDGER_BUILD_FAILED"


def test_score_claim_exposure_gate_unmapped_short_circuits(monkeypatch):
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: _fake_json(_segment_response(
        [_claim_dict(category="identity", about="Nguyễn Văn A", evidence_fact_ids=[], strength="none")],
    )))
    candidate = _candidate(named_individuals=[_victim()], draft="Câu 1.")
    result = ceg.score_claim_exposure_gate(candidate)
    assert result.passed is False
    assert result.reason_code == "CLAIM_LEDGER_UNMAPPED"


def test_score_claim_exposure_gate_full_pass_path(monkeypatch):
    """Không có claim nào -> ledger rỗng -> mọi check sau đều trivially
    pass (không có gì để vi phạm) -> PASS toàn gate; verified=True được
    set trên mọi claim còn lại trong kết quả cuối (rỗng ở đây)."""
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: _fake_json(_segment_response([])))
    monkeypatch.setattr(ceg, "_run_codex", lambda prompt: _fake_json({"inflated": False, "inflated_phrases": []}))
    candidate = _candidate(named_individuals=[_victim()], draft="Bối cảnh chung không nhắc ai cụ thể.")
    result = ceg.score_claim_exposure_gate(candidate)
    assert result.passed is True
    assert result.reason_code is None


def test_score_claim_exposure_gate_acquitted_emphasis_short_circuits(monkeypatch):
    def _classify(prompt):
        return _fake_json(_segment_response(
            [_claim_dict(category="guilt_or_culpability", about="Nguyễn Văn A", evidence_fact_ids=["F1"], strength="full")],
        ))
    monkeypatch.setattr(ceg, "_run_agy", _classify)
    monkeypatch.setattr(ceg, "_run_codex", lambda prompt: _fake_json({"entailment_strength": "full"}))
    candidate = _candidate(
        named_individuals=[_acquitted()],
        core_facts=[g.CoreFact(fact_id="F1", statement="A bị buộc tội", fact_type="chronology")],
        draft="A đã giết người.",
    )
    result = ceg.score_claim_exposure_gate(candidate)
    assert result.passed is False
    assert result.reason_code == "ACQUITTED_DISPROPORTIONATE_EMPHASIS"


def test_score_claim_exposure_gate_verified_field_set_true_on_full_pass(monkeypatch):
    def _classify(prompt):
        return _fake_json(_segment_response(
            [_claim_dict(category="identity", about="Nguyễn Văn A", evidence_fact_ids=["F1"], strength="full")],
        ))
    monkeypatch.setattr(ceg, "_run_agy", _classify)

    def _codex_route(prompt):
        if "inflated" in prompt.lower() or "SURFACE" in prompt:
            return _fake_json({"inflated": False, "inflated_phrases": []})
        return _fake_json({"entailment_strength": "full"})
    monkeypatch.setattr(ceg, "_run_codex", _codex_route)
    candidate = _candidate(
        named_individuals=[_victim()],
        core_facts=[g.CoreFact(fact_id="F1", statement="A là nạn nhân", fact_type="identity")],
        draft="Nguyễn Văn A là nạn nhân.",
    )
    result = ceg.score_claim_exposure_gate(candidate)
    assert result.passed is True
    assert all(c.verified is True for c in result.claim_ledger)


# --- Codex review round 1, High #1: malformed-input fail-closed probes ---

def test_score_claim_exposure_gate_candidate_none_fails_closed():
    result = ceg.score_claim_exposure_gate(None)
    assert result.passed is False
    assert result.reason_code == "CLAIM_GATE_INVALID_INPUT"


def test_score_claim_exposure_gate_candidate_bogus_object_fails_closed():
    class _Bogus:
        pass
    result = ceg.score_claim_exposure_gate(_Bogus())
    assert result.passed is False
    assert result.reason_code == "CLAIM_GATE_INVALID_INPUT"


def test_score_claim_exposure_gate_named_individuals_none_fails_closed():
    candidate = _candidate(draft="Câu 1.")
    candidate.named_individuals = None
    result = ceg.score_claim_exposure_gate(candidate)
    assert result.passed is False
    assert result.reason_code == "CLAIM_GATE_INVALID_INPUT"


def test_score_claim_exposure_gate_core_facts_none_fails_closed():
    candidate = _candidate(named_individuals=[_victim()], draft="Câu 1.")
    candidate.core_facts = None
    result = ceg.score_claim_exposure_gate(candidate)
    assert result.passed is False
    assert result.reason_code == "CLAIM_GATE_INVALID_INPUT"


def test_score_claim_exposure_gate_named_individuals_bad_element_fails_closed():
    candidate = _candidate(named_individuals=["not a NamedIndividual"], draft="Câu 1.")
    result = ceg.score_claim_exposure_gate(candidate)
    assert result.passed is False
    assert result.reason_code == "CLAIM_GATE_INVALID_INPUT"


def test_score_claim_exposure_gate_core_facts_bad_element_fails_closed():
    candidate = _candidate(named_individuals=[_victim()], core_facts=["not a CoreFact"], draft="Câu 1.")
    result = ceg.score_claim_exposure_gate(candidate)
    assert result.passed is False
    assert result.reason_code == "CLAIM_GATE_INVALID_INPUT"


def test_score_claim_exposure_gate_unexpected_exception_after_ledger_fails_closed(monkeypatch):
    """Mô phỏng lỗi runtime KHÔNG dự kiến (không phải ClaimGateError) xảy
    ra sau khi ledger xây xong -- lớp except Exception cuối phải bắt được,
    không để thoát ra ngoài."""
    monkeypatch.setattr(ceg, "_run_agy", lambda prompt: _fake_json(_segment_response([])))

    def _boom(claims, candidate):
        raise TypeError("lỗi giả lập không dự kiến")
    monkeypatch.setattr(ceg, "verify_entailment_strength", _boom)
    candidate = _candidate(named_individuals=[_victim()], draft="Câu 1.")
    result = ceg.score_claim_exposure_gate(candidate)
    assert result.passed is False
    assert result.reason_code == "CLAIM_GATE_UNEXPECTED_ERROR"
