"""Test cl_risk_gate.py (Stage 1 -- xem docstring đầu cl_risk_gate.py cho
phạm vi). KHÔNG gọi agy/codex thật -- mọi test dùng monkeypatch trên
cl_risk_gate._run_agy/_run_codex (đúng pattern test_trending_short_generator.py),
hoặc dựng CandidateCase/NamedIndividual/... trực tiếp bằng tay để test logic
mechanical (C1/C2/C3/C6/identifier_ok/tier_for) độc lập với LLM."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cl_risk_gate as g


def _fake_json(payload: dict) -> str:
    return json.dumps(payload)


# =============================================================================
# identifier_ok() -- §1.4.1 bước 8
# =============================================================================

def test_identifier_ok_inconsistent_always_fails():
    ls = g.LegalStatusRecord(decision_identifier_consistent=g.DecisionIdentifierConsistency.INCONSISTENT, evidentiary_path="allowlisted_public_record")
    assert g.identifier_ok(ls) is False


def test_identifier_ok_consistent_always_passes():
    ls = g.LegalStatusRecord(decision_identifier_consistent=g.DecisionIdentifierConsistency.CONSISTENT)
    assert g.identifier_ok(ls) is True


def test_identifier_ok_insufficient_evidence_needs_public_record_path():
    ls = g.LegalStatusRecord(decision_identifier_consistent=g.DecisionIdentifierConsistency.INSUFFICIENT_EVIDENCE)
    assert g.identifier_ok(ls) is False
    ls.evidentiary_path = "allowlisted_public_record"
    assert g.identifier_ok(ls) is True
    ls.evidentiary_path = "two_independent_qualified_sources"
    assert g.identifier_ok(ls) is False  # chỉ allowlisted_public_record tolerate INSUFFICIENT_EVIDENCE, path kia thì không


# =============================================================================
# C6 -- bảng đóng, §1.5. FIX (Codex review Stage 1, 2 Blocker thật): mọi
# nhánh miễn trừ/PASS giờ đòi role_verification.role_cross_verified=True
# (Blocker #1) VÀ, cho nhánh accused_unconvicted+deceased,
# legal_status.cross_verified=True (Blocker #2) -- test dưới đây build
# fixture với role_cross_verified=True TƯỜNG MINH khi test hành vi PASS
# thật, và có test riêng xác nhận role_cross_verified=False/
# legal_status.cross_verified=False LUÔN chặn PASS dù data khác đều "đẹp".
# =============================================================================

def _role_verified(pass1_role: str = ""):
    return g.RoleVerificationRecord(role_cross_verified=True, pass1_role=pass1_role, pass2_role=pass1_role)


def _convicted_final_verified(name="A", identity_confidence="high", role_cross_verified=True):
    ls = g.LegalStatusRecord(
        disposition=g.DispositionStatus.CONVICTED, finality_state=g.FinalityState.FINAL, cross_verified=True,
        decision_identifier_consistent=g.DecisionIdentifierConsistency.CONSISTENT,
    )
    rv = _role_verified("convicted_perpetrator") if role_cross_verified else g.RoleVerificationRecord()
    return g.NamedIndividual(canonical_name=name, identity_confidence=identity_confidence, role="convicted_perpetrator", legal_status=ls, role_verification=rv)


def test_c6_victim_exempt_only_when_role_cross_verified():
    person = g.NamedIndividual(canonical_name="Nạn nhân", identity_confidence="low", role="victim", role_verification=_role_verified("victim"))
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[person])
    assert g.score_c6(candidate).passed is True


def test_c6_blocker1_regression_role_not_cross_verified_never_passes_even_if_labeled_victim():
    """Regression test TRỰC TIẾP cho Blocker #1 (Codex review Stage 1): ở
    Stage 1, verify_sources() KHÔNG BAO GIỜ set role_cross_verified=True --
    1 người thật ra là accused_unconvicted còn sống nhưng bị LLM gán NHẦM
    role='victim' (single-pass, chưa xác minh) KHÔNG được PASS chỉ vì nhãn
    role trông "an toàn". Đây chính là con đường bypass Codex tìm thấy."""
    person = g.NamedIndividual(canonical_name="Bị gán nhầm", identity_confidence="high", role="victim")  # role_verification mặc định: role_cross_verified=False
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[person])
    assert g.score_c6(candidate).passed is False


def test_c6_blocker1_regression_acquitted_role_not_cross_verified_fails():
    person = g.NamedIndividual(canonical_name="X", identity_confidence="high", role="acquitted")
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[person])
    assert g.score_c6(candidate).passed is False


def test_c6_convicted_perpetrator_passes_when_final_cross_verified_and_role_verified():
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[_convicted_final_verified()])
    assert g.score_c6(candidate).passed is True


def test_c6_convicted_perpetrator_fails_when_role_not_cross_verified_even_if_legal_status_is():
    """Legal status hoàn hảo (CONVICTED+FINAL+cross_verified) nhưng ROLE
    chưa cross-verified -- vẫn FAIL (đúng vai trò gán bởi 1 pass có thể sai
    ngay từ đầu: người này có thể thật ra là accused_unconvicted)."""
    person = _convicted_final_verified(role_cross_verified=False)
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[person])
    assert g.score_c6(candidate).passed is False


def test_c6_convicted_perpetrator_fails_when_legal_status_not_cross_verified():
    """Chưa qua 2-pass độc lập (Stage 2) -- BẮT BUỘC FAIL, không được tin
    1 lần trích xuất duy nhất (đây chính là lý do Stage 1's verify_sources()
    luôn để cross_verified=False)."""
    person = _convicted_final_verified()
    person.legal_status.cross_verified = False
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[person])
    assert g.score_c6(candidate).passed is False


def test_c6_convicted_perpetrator_fails_when_under_appeal():
    person = _convicted_final_verified()
    person.legal_status.finality_state = g.FinalityState.UNDER_APPEAL
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[person])
    assert g.score_c6(candidate).passed is False


def test_c6_accused_unconvicted_living_always_fails_no_matter_what():
    """Presumption of innocence -- không có source count nào cứu được."""
    ls = g.LegalStatusRecord(life_status=g.LifeStatus.LIVING)
    person = g.NamedIndividual(canonical_name="Nghi phạm", identity_confidence="high", role="accused_unconvicted", legal_status=ls, role_verification=_role_verified("accused_unconvicted"))
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[person])
    assert g.score_c6(candidate).passed is False


def test_c6_accused_unconvicted_unknown_life_status_fails_closed():
    ls = g.LegalStatusRecord(life_status=g.LifeStatus.UNKNOWN)
    person = g.NamedIndividual(canonical_name="Nghi phạm", identity_confidence="high", role="accused_unconvicted", legal_status=ls, role_verification=_role_verified("accused_unconvicted"))
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[person])
    assert g.score_c6(candidate).passed is False


def test_c6_accused_unconvicted_deceased_passes_when_life_status_cross_verified():
    ls = g.LegalStatusRecord(life_status=g.LifeStatus.DECEASED, cross_verified=True)
    person = g.NamedIndividual(canonical_name="Nghi phạm đã mất", identity_confidence="high", role="accused_unconvicted", legal_status=ls, role_verification=_role_verified("accused_unconvicted"))
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[person])
    assert g.score_c6(candidate).passed is True


def test_c6_blocker2_regression_accused_unconvicted_deceased_but_not_cross_verified_fails():
    """Regression test TRỰC TIẾP cho Blocker #2: life_status=deceased
    nhưng CHƯA cross-verified (đúng trạng thái single-pass thật của Stage
    1's verify_sources()) -- KHÔNG được PASS chỉ vì nhãn 'deceased' trông
    an toàn. Kết hợp với grounding chỉ-là-substring (High #5), 1 excerpt
    yếu có thể khiến 1 người CÒN SỐNG bị gán nhầm deceased -- nếu không có
    fix này, C6 sẽ PASS oan ngay tại đây."""
    ls = g.LegalStatusRecord(life_status=g.LifeStatus.DECEASED, cross_verified=False)
    person = g.NamedIndividual(canonical_name="Nghi phạm", identity_confidence="high", role="accused_unconvicted", legal_status=ls, role_verification=_role_verified("accused_unconvicted"))
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[person])
    assert g.score_c6(candidate).passed is False


def test_c6_low_identity_confidence_living_fails_even_if_role_would_otherwise_pass():
    """Bảo vệ nhận nhầm người: identity_confidence=low + chưa xác nhận
    deceased + vai trò ngụ ý sai phạm -- FAIL bất kể gì khác."""
    person = _convicted_final_verified(identity_confidence="low")
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[person])
    assert g.score_c6(candidate).passed is False


def test_c6_named_relative_fails_closed_v1():
    person = g.NamedIndividual(canonical_name="Người thân", identity_confidence="high", role="named_relative_or_associate", role_verification=_role_verified("named_relative_or_associate"))
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[person])
    assert g.score_c6(candidate).passed is False


def test_c6_empty_named_individuals_fails_closed():
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[])
    assert g.score_c6(candidate).passed is False


def test_c6_unrecognized_role_fails_closed():
    person = g.NamedIndividual(canonical_name="X", identity_confidence="high", role="something_unmodeled", role_verification=_role_verified("something_unmodeled"))
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", named_individuals=[person])
    assert g.score_c6(candidate).passed is False


# =============================================================================
# tier_for() -- §1.8
# =============================================================================

def _result(failing):
    return g.RiskScoreResult(tier="", criteria=[], failing_criteria=failing, high_risk_triggers=[], rationale="", scorer_version="v", allowlist_version="v", scored_at="now")


def test_tier_low_when_nothing_fails():
    assert g.tier_for(_result([])) == "LOW"


def test_tier_medium_when_only_sourcing_criteria_fail():
    assert g.tier_for(_result(["C1", "C2"])) == "MEDIUM"


def test_tier_high_when_c5_fails():
    assert g.tier_for(_result(["C5"])) == "HIGH"


def test_tier_high_when_c6_fails():
    assert g.tier_for(_result(["C6"])) == "HIGH"


def test_tier_high_when_mixed_structural_and_sourcing_fail():
    assert g.tier_for(_result(["C1", "C6"])) == "HIGH"


def test_tier_high_fail_closed_on_unrecognized_criterion():
    assert g.tier_for(_result(["C99"])) == "HIGH"


# =============================================================================
# C1/C2/C3 -- mechanical, §1.5
# =============================================================================

def _source(sid, tier, lineage=None, independence_verified=False):
    return g.SourceRecord(
        source_id=sid, url=f"https://example.com/{sid}", publisher="x", publisher_tier=tier,
        source_lineage_id=lineage or sid, origin_claim="unstated", independence_verified=independence_verified,
        retrieved_at="now", page_content_hash="h", excerpt_hash="h", excerpt_context_window="",
        excerpt="", excerpt_entailment_note="",
    )


def test_c1_passes_with_one_reputable_press_source():
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", sources=[_source("s1", g.PublisherTier.REPUTABLE_PRESS)])
    assert g.score_c1(candidate).passed is True


def test_c1_fails_when_only_unknown_tier_sources():
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", sources=[_source("s1", g.PublisherTier.UNKNOWN)])
    assert g.score_c1(candidate).passed is False


def test_c2_fails_when_fact_has_only_1_verified_independent_lineage():
    fact = g.CoreFact(fact_id="F1", statement="x", fact_type="identity", corroborating_source_ids=["s1"], corroborating_verified_independent_lineage_ids=["lineage1"])
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", core_facts=[fact], sources=[_source("s1", g.PublisherTier.REPUTABLE_PRESS, independence_verified=True)])
    assert g.score_c2(candidate).passed is False


def test_c2_passes_when_fact_has_2_verified_independent_lineages():
    fact = g.CoreFact(fact_id="F1", statement="x", fact_type="identity", corroborating_source_ids=["s1", "s2"], corroborating_verified_independent_lineage_ids=["lineage1", "lineage2"])
    candidate = g.CandidateCase(
        case_id="x", case_key="x", working_title="x", core_facts=[fact],
        sources=[
            _source("s1", g.PublisherTier.REPUTABLE_PRESS, "lineage1", independence_verified=True),
            _source("s2", g.PublisherTier.PUBLIC_RECORD, "lineage2", independence_verified=True),
        ],
    )
    assert g.score_c2(candidate).passed is True


def test_c2_medium6_regression_fails_when_claimed_lineages_have_independence_verified_false():
    """Regression test cho Medium #6 (Codex review Stage 1): trước đây
    score_c2() tin THẲNG corroborating_verified_independent_lineage_ids mà
    không đối chiếu candidate.sources -- 1 danh sách bị dựng sai (2
    lineage_id claim là verified nhưng source thật có
    independence_verified=False) trước đây vẫn PASS. Giờ phải FAIL vì
    _verified_independent_lineages_for_fact() tính lại từ dữ liệu nguồn
    thật."""
    fact = g.CoreFact(fact_id="F1", statement="x", fact_type="identity", corroborating_source_ids=["s1", "s2"], corroborating_verified_independent_lineage_ids=["lineage1", "lineage2"])
    candidate = g.CandidateCase(
        case_id="x", case_key="x", working_title="x", core_facts=[fact],
        sources=[
            _source("s1", g.PublisherTier.REPUTABLE_PRESS, "lineage1", independence_verified=False),
            _source("s2", g.PublisherTier.PUBLIC_RECORD, "lineage2", independence_verified=False),
        ],
    )
    assert g.score_c2(candidate).passed is False


def test_c2_regression_fails_when_source_not_actually_cited_for_this_fact():
    """1 source có independence_verified=True + đúng lineage claimed,
    nhưng source_id đó KHÔNG nằm trong corroborating_source_ids của fact
    này (nguồn không thật sự trích dẫn cho fact này) -- không được tính."""
    fact = g.CoreFact(fact_id="F1", statement="x", fact_type="identity", corroborating_source_ids=["s1"], corroborating_verified_independent_lineage_ids=["lineage1", "lineage2"])
    candidate = g.CandidateCase(
        case_id="x", case_key="x", working_title="x", core_facts=[fact],
        sources=[
            _source("s1", g.PublisherTier.REPUTABLE_PRESS, "lineage1", independence_verified=True),
            _source("s2", g.PublisherTier.PUBLIC_RECORD, "lineage2", independence_verified=True),  # không trong corroborating_source_ids của F1
        ],
    )
    assert g.score_c2(candidate).passed is False


def test_c3_fails_when_load_bearing_fact_only_has_aggregator_sourcing():
    fact = g.CoreFact(fact_id="F1", statement="x", fact_type="appeal_status", corroborating_source_ids=["s1"])
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x", core_facts=[fact], sources=[_source("s1", g.PublisherTier.AGGREGATOR)])
    assert g.score_c3(candidate).passed is False


def test_c3_passes_when_every_fact_has_at_least_one_reputable_source():
    fact = g.CoreFact(fact_id="F1", statement="x", fact_type="appeal_status", corroborating_source_ids=["s1", "s2"])
    candidate = g.CandidateCase(
        case_id="x", case_key="x", working_title="x", core_facts=[fact],
        sources=[_source("s1", g.PublisherTier.AGGREGATOR), _source("s2", g.PublisherTier.REPUTABLE_PRESS)],
    )
    assert g.score_c3(candidate).passed is True


# =============================================================================
# C4/C5/C7 -- không implement ở Stage 1, phải raise rõ ràng (không âm thầm PASS)
# =============================================================================

def test_c4_raises_or_fails_closed_when_no_review_draft():
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x")
    result = g.score_c4(candidate)
    assert result.passed is False


def test_c5_not_yet_implemented_raises():
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x")
    with pytest.raises(NotImplementedError):
        g.score_c5(candidate)


def test_c7_fails_closed_when_no_review_draft():
    candidate = g.CandidateCase(case_id="x", case_key="x", working_title="x")
    result = g.score_c7(candidate)
    assert result.passed is False


# =============================================================================
# Ledger -- §1.10 atomic surface/upsert
# =============================================================================

def test_surface_candidate_creates_entry_once(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "CASE_LEDGER_PATH", tmp_path / "ledger.json")
    lock_dir = tmp_path / "locks"
    created = g.surface_candidate_locked("case1", "key1", "Vụ án X", "SRC.md", lock_dir=lock_dir)
    assert created is True
    data = json.loads((tmp_path / "ledger.json").read_text())
    assert data["case1"]["status"] == "surfaced"

    created_again = g.surface_candidate_locked("case1", "key1", "Vụ án X", "SRC.md", lock_dir=lock_dir)
    assert created_again is False  # idempotent -- không ghi đè


def test_ledger_load_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "CASE_LEDGER_PATH", tmp_path / "ledger.json")
    lock_dir = tmp_path / "locks"
    g.surface_candidate_locked("case1", "key1", "Vụ án X", "SRC.md", lock_dir=lock_dir)
    ledger = g.CaseLedger.load()
    entry = ledger.get("case1")
    assert entry is not None
    assert entry.status == g.CaseLedgerStatus.SURFACED
    assert entry.title_keywords == ["key1"]


def test_upsert_entry_locked_preserves_other_entries(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "CASE_LEDGER_PATH", tmp_path / "ledger.json")
    lock_dir = tmp_path / "locks"
    g.surface_candidate_locked("case1", "key1", "A", "SRC.md", lock_dir=lock_dir)
    g.surface_candidate_locked("case2", "key2", "B", "SRC.md", lock_dir=lock_dir)

    def _mark_low_cleared(current):
        current.status = g.CaseLedgerStatus.LOW_CLEARED
        return current

    g.upsert_entry_locked("case1", _mark_low_cleared, lock_dir=lock_dir)

    reloaded = g.CaseLedger.load()
    assert reloaded.get("case1").status == g.CaseLedgerStatus.LOW_CLEARED
    assert reloaded.get("case2").status == g.CaseLedgerStatus.SURFACED  # không bị mất


def test_upsert_entry_locked_medium8_regression_reads_fresh_state_inside_lock(tmp_path, monkeypatch):
    """Regression test cho Medium #8 (Codex review Stage 1, lost update):
    chữ ký CŨ nhận thẳng 1 entry đã load TRƯỚC lock -- 2 lần gọi dựa trên 2
    bản đọc CŨ khác nhau (mô phỏng 2 worker) sẽ làm lần sau ghi đè mất field
    lần trước sửa nếu không đọc lại state MỚI NHẤT bên trong lock. Với chữ
    ký MỚI (mutate_fn), mutate_fn LUÔN nhận state mới nhất tại thời điểm gọi
    -- 2 lần upsert liên tiếp, mỗi lần sửa 1 field khác nhau, PHẢI giữ được
    cả 2 thay đổi."""
    monkeypatch.setattr(g, "CASE_LEDGER_PATH", tmp_path / "ledger.json")
    lock_dir = tmp_path / "locks"
    g.surface_candidate_locked("case1", "key1", "A", "SRC.md", lock_dir=lock_dir)

    def _set_status(current):
        current.status = g.CaseLedgerStatus.LOW_CLEARED
        return current

    def _set_policy_trigger(current):
        current.policy_trigger = "C6"
        return current

    g.upsert_entry_locked("case1", _set_status, lock_dir=lock_dir)
    g.upsert_entry_locked("case1", _set_policy_trigger, lock_dir=lock_dir)

    final = g.CaseLedger.load().get("case1")
    assert final.status == g.CaseLedgerStatus.LOW_CLEARED  # thay đổi lần 1 KHÔNG bị mất
    assert final.policy_trigger == "C6"  # thay đổi lần 2 cũng có mặt


def test_upsert_entry_locked_medium_new2_regression_rejects_non_entry_return(tmp_path, monkeypatch):
    """Regression test cho Medium mới #2 (Codex review Stage 1 round 2):
    mutate_fn trả về sai kiểu (không phải CaseLedgerEntry) phải raise NGAY,
    KHÔNG được âm thầm ghi rác vào ledger."""
    monkeypatch.setattr(g, "CASE_LEDGER_PATH", tmp_path / "ledger.json")
    lock_dir = tmp_path / "locks"
    g.surface_candidate_locked("case1", "key1", "A", "SRC.md", lock_dir=lock_dir)
    with pytest.raises(g.CLRiskGateError):
        g.upsert_entry_locked("case1", lambda current: {"not": "an entry"}, lock_dir=lock_dir)


def test_upsert_entry_locked_medium_new2_regression_rejects_case_id_mismatch(tmp_path, monkeypatch):
    """mutate_fn đổi case_id -- phải raise, không được tạo entry mới lẫn
    với entry cũ vẫn còn nguyên trong ledger."""
    monkeypatch.setattr(g, "CASE_LEDGER_PATH", tmp_path / "ledger.json")
    lock_dir = tmp_path / "locks"
    g.surface_candidate_locked("case1", "key1", "A", "SRC.md", lock_dir=lock_dir)

    def _change_case_id(current):
        current.case_id = "case_other"
        return current

    with pytest.raises(g.CLRiskGateError):
        g.upsert_entry_locked("case1", _change_case_id, lock_dir=lock_dir)


# =============================================================================
# Discover -- §1.3, parse file thật trong content_repo_clone
# =============================================================================

def test_discover_candidates_parses_real_source_files():
    stubs = g.discover_candidates(dry_run=True)
    assert len(stubs) > 0
    titles = [s["working_title"] for s in stubs]
    assert any("Năm Cam" in t for t in titles)
    nam_cam = next(s for s in stubs if "Năm Cam" in s["working_title"])
    assert len(nam_cam["reference_urls"]) > 0
    assert all(u.startswith("http") for u in nam_cam["reference_urls"])


def test_discover_candidates_dry_run_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "CASE_LEDGER_PATH", tmp_path / "ledger.json")
    g.discover_candidates(dry_run=True, lock_dir=tmp_path / "locks")
    assert not (tmp_path / "ledger.json").exists()


def test_split_source_file_into_cases_basic():
    text = "intro\n\n## 1. Vụ án A\n\nnội dung A\n\n## 2. Vụ án B\n\nnội dung B\n"
    cases = g._split_source_file_into_cases(text)
    assert [t for t, _ in cases] == ["Vụ án A", "Vụ án B"]
    assert "nội dung A" in cases[0][1]
    assert "nội dung B" not in cases[0][1]


def test_extract_reference_urls():
    case_text = "## 1. Vụ án A\n\nnội dung\n\n### Nguồn tham khảo\n\n- Báo X: https://a.example.com/1\n- Báo Y: https://b.example.com/2\n\n## 2. Vụ án B\n"
    urls = g._extract_reference_urls(case_text)
    assert urls == ["https://a.example.com/1", "https://b.example.com/2"]


def test_strip_trailing_url_punctuation_regression_round4():
    """Regression test cho Medium/Low (Codex review Stage 1 round 4): dấu
    câu kết thúc câu văn dính vào cuối URL trần phải bị cắt, nhưng ')' hợp
    lệ trong URL (vd Wikipedia disambiguation) không bị cắt oan."""
    assert g._strip_trailing_url_punctuation("https://a.example.com/x.") == "https://a.example.com/x"
    assert g._strip_trailing_url_punctuation("https://a.example.com/x,") == "https://a.example.com/x"
    assert g._strip_trailing_url_punctuation('https://a.example.com/x".') == "https://a.example.com/x"
    assert g._strip_trailing_url_punctuation("https://en.wikipedia.org/wiki/X_(disambiguation)") == "https://en.wikipedia.org/wiki/X_(disambiguation)"
    assert g._strip_trailing_url_punctuation("https://en.wikipedia.org/wiki/X_(disambiguation))") == "https://en.wikipedia.org/wiki/X_(disambiguation)"


def test_extract_reference_urls_strips_trailing_sentence_punctuation():
    case_text = "## 1. Vụ án A\n\nnội dung\n\n### Nguồn tham khảo\n\n- Xem thêm tại https://a.example.com/1.\n\n## 2. Vụ án B\n"
    urls = g._extract_reference_urls(case_text)
    assert urls == ["https://a.example.com/1"]


# =============================================================================
# classify_publisher_tier -- allowlist thật
# =============================================================================

def test_classify_publisher_tier_known_reputable_press():
    tiers = g.load_source_tiers()
    assert g.classify_publisher_tier("https://vnexpress.net/abc", tiers) == g.PublisherTier.REPUTABLE_PRESS


def test_classify_publisher_tier_unknown_domain_defaults_unknown():
    tiers = g.load_source_tiers()
    assert g.classify_publisher_tier("https://totally-unlisted-domain-xyz.example/abc", tiers) == g.PublisherTier.UNKNOWN


def test_classify_publisher_tier_wikipedia_is_aggregator_not_reputable():
    tiers = g.load_source_tiers()
    assert g.classify_publisher_tier("https://vi.wikipedia.org/wiki/x", tiers) == g.PublisherTier.AGGREGATOR


# =============================================================================
# Dedupe -- §1.11
# =============================================================================

def _candidate_with_fingerprint(case_id, names, locations=None, orgs=None, decision_ids=None):
    ef = g.EventFingerprint(normalized_core_act="murder", date_range=None, locations=locations or [], organizations=orgs or [], all_named_individuals=names, decision_identifiers=decision_ids or [])
    person = g.NamedIndividual(canonical_name=names[0] if names else "X", identity_confidence="high", role="victim")
    return g.CandidateCase(case_id=case_id, case_key=case_id, working_title=f"Case {case_id}", named_individuals=[person], event_fingerprint=ef)


def _ledger_entry(case_id, names, status=g.CaseLedgerStatus.LOW_CLEARED, decision_ids=None):
    ef = g.EventFingerprint(normalized_core_act="murder", date_range=None, locations=[], organizations=[], all_named_individuals=names, decision_identifiers=decision_ids or [])
    return g.CaseLedgerEntry(
        case_id=case_id, canonical_names=names, title_keywords=[case_id], fingerprint=ef, status=status,
        policy_trigger=None, rejection_scope=None, recheck_policy=None, evidence_as_of=None,
        next_eligible_review_at=None, pending_alias_write=False, merged_into_case_id=None,
        first_seen_at="t0", last_updated_at="t0", history=[],
    )


def test_stage1_blocking_finds_name_collision():
    candidate = _candidate_with_fingerprint("new1", ["Nguyễn Văn A"])
    ledger = g.CaseLedger({"old1": _ledger_entry("old1", ["Nguyễn Văn A"])})
    collisions = g.stage1_blocking(candidate, ledger)
    assert len(collisions) == 1
    assert collisions[0].case_id == "old1"


def test_stage1_blocking_no_collision_when_no_overlap():
    candidate = _candidate_with_fingerprint("new1", ["Người Hoàn Toàn Khác"])
    ledger = g.CaseLedger({"old1": _ledger_entry("old1", ["Nguyễn Văn A"])})
    assert g.stage1_blocking(candidate, ledger) == []


def test_stage1_blocking_fail_closed_fallback_on_low_signal():
    """Candidate identity_confidence=low toàn bộ -> LUÔN so với toàn ledger,
    kể cả không overlap gì (§1.11 fail-closed fallback)."""
    ef = g.EventFingerprint(normalized_core_act="x", date_range=None, locations=[], organizations=[], all_named_individuals=[], decision_identifiers=[])
    person = g.NamedIndividual(canonical_name="?", identity_confidence="low", role="victim")
    candidate = g.CandidateCase(case_id="new1", case_key="new1", working_title="x", named_individuals=[person], event_fingerprint=ef)
    ledger = g.CaseLedger({"old1": _ledger_entry("old1", ["Ai Đó Khác Hẳn"])})
    assert len(g.stage1_blocking(candidate, ledger)) == 1


def test_stage1_blocking_high_regression_low_signal_fallback_excludes_self():
    """Regression test TRỰC TIẾP cho High mới (Codex review Stage 1 round
    3): fallback low-signal trước đây trả THẲNG all_entries KHÔNG lọc --
    discover_candidates() (§1.3) đã ghi SURFACED cho CHÍNH candidate này
    TRƯỚC KHI verify, nên ledger CÓ THỂ chứa entry của chính
    candidate.case_id. Nếu không lọc, candidate sẽ bị đưa đi adjudicate với
    CHÍNH NÓ ở stage2 -- gần như chắc chắn LLM trả SAME_EVENT, khiến
    candidate bị đánh duplicate oan ngay từ collision đầu tiên."""
    ef = g.EventFingerprint(normalized_core_act="x", date_range=None, locations=[], organizations=[], all_named_individuals=[], decision_identifiers=[])
    person = g.NamedIndividual(canonical_name="?", identity_confidence="low", role="victim")
    candidate = g.CandidateCase(case_id="new1", case_key="new1", working_title="x", named_individuals=[person], event_fingerprint=ef)
    self_entry = _ledger_entry("new1", ["?"], status=g.CaseLedgerStatus.SURFACED)
    ledger = g.CaseLedger({"new1": self_entry, "old1": _ledger_entry("old1", ["Ai Đó Khác Hẳn"])})
    collisions = g.stage1_blocking(candidate, ledger)
    assert "new1" not in [e.case_id for e in collisions]
    assert "old1" in [e.case_id for e in collisions]


def test_dedupe_against_ledger_high_regression_low_signal_does_not_self_match(monkeypatch):
    """Cùng kịch bản trên nhưng đi qua toàn bộ dedupe_against_ledger() --
    _run_codex bị monkeypatch để LUÔN trả SAME_EVENT (mô phỏng đúng rủi ro
    thật: so 1 case với chính nó gần như chắc chắn LLM nói 'giống nhau'
    thật). Nếu fix đúng, candidate KHÔNG được so với chính nó -- kết quả
    cuối chỉ phụ thuộc vào entry 'old1' (không trùng)."""
    ef = g.EventFingerprint(normalized_core_act="x", date_range=None, locations=[], organizations=[], all_named_individuals=[], decision_identifiers=[])
    person = g.NamedIndividual(canonical_name="?", identity_confidence="low", role="victim")
    candidate = g.CandidateCase(case_id="new1", case_key="new1", working_title="x", named_individuals=[person], event_fingerprint=ef)
    self_entry = _ledger_entry("new1", ["?"], status=g.CaseLedgerStatus.SURFACED)
    ledger = g.CaseLedger({"new1": self_entry, "old1": _ledger_entry("old1", ["Ai Đó Khác Hẳn"], status=g.CaseLedgerStatus.REJECTED_POLICY)})

    def _always_same_event(prompt):
        return _fake_json({"verdict": "SAME_EVENT", "reason": "giả lập"})

    monkeypatch.setattr(g, "_run_codex", _always_same_event)
    result = g.dedupe_against_ledger(candidate, ledger)
    # "old1" là REJECTED_POLICY -- nếu candidate bị so với "new1" (chính
    # nó) trước, method sẽ là stage2_llm_adjudication với matched_case_id
    # "new1"; nếu KHÔNG bị so với chính nó, "old1" adjudicate SAME_EVENT
    # (do mock) và matched_case_id phải là "old1", không phải "new1".
    assert result.matched_case_id != "new1"


def test_dedupe_against_ledger_same_event(monkeypatch):
    candidate = _candidate_with_fingerprint("new1", ["Nguyễn Văn A"])
    ledger = g.CaseLedger({"old1": _ledger_entry("old1", ["Nguyễn Văn A"])})
    monkeypatch.setattr(g, "_run_codex", lambda prompt: _fake_json({"verdict": "SAME_EVENT", "reason": "cùng vụ"}))
    result = g.dedupe_against_ledger(candidate, ledger)
    assert result.is_duplicate is True
    assert result.matched_case_id == "old1"
    assert result.dedupe_confidence == "high"


def test_dedupe_against_ledger_related_but_distinct_not_duplicate(monkeypatch):
    """FIX (Codex review Stage 1 round 3, Medium mới): verdict tổng hợp
    PHẢI giữ RELATED_BUT_DISTINCT khi không có SAME_EVENT/UNCLEAR nào --
    bản trước xoá mất thông tin này, tự ý gán "DIFFERENT_EVENT" dù
    related_case_ids không rỗng, khiến 1 consumer chỉ đọc `verdict` hiểu
    sai là "không liên quan gì cả"."""
    candidate = _candidate_with_fingerprint("new1", ["Nguyễn Văn A"])
    ledger = g.CaseLedger({"old1": _ledger_entry("old1", ["Nguyễn Văn A"])})
    monkeypatch.setattr(g, "_run_codex", lambda prompt: _fake_json({"verdict": "RELATED_BUT_DISTINCT", "reason": "khác vụ"}))
    result = g.dedupe_against_ledger(candidate, ledger)
    assert result.is_duplicate is False
    assert result.verdict == "RELATED_BUT_DISTINCT"
    assert "old1" in result.related_case_ids


def test_dedupe_against_ledger_pure_different_event_verdict(monkeypatch):
    candidate = _candidate_with_fingerprint("new1", ["Nguyễn Văn A"])
    ledger = g.CaseLedger({"old1": _ledger_entry("old1", ["Nguyễn Văn A"])})
    monkeypatch.setattr(g, "_run_codex", lambda prompt: _fake_json({"verdict": "DIFFERENT_EVENT", "reason": "không liên quan"}))
    result = g.dedupe_against_ledger(candidate, ledger)
    assert result.is_duplicate is False
    assert result.verdict == "DIFFERENT_EVENT"
    assert result.related_case_ids == []


def test_dedupe_against_ledger_unclear_verdict_reports_low_confidence(monkeypatch):
    """LƯU Ý (Codex review Stage 1 round 2, Low mới #1): test này CHỈ xác
    nhận dedupe_against_ledger() TRẢ VỀ dedupe_confidence='low' cho verdict
    UNCLEAR -- module này KHÔNG tự thực thi bất kỳ invariant nào ngăn
    consumer bỏ qua field đó rồi auto-select oan; việc "không auto-select
    khi confidence thấp" là trách nhiệm của run_cl_case_gate() orchestrator
    (Stage 3, CHƯA xây), không phải của DedupeResult tự nó. Tên test cũ
    ngụ ý rộng hơn những gì thật sự được kiểm tra -- đổi tên cho trung thực."""
    candidate = _candidate_with_fingerprint("new1", ["Nguyễn Văn A"])
    ledger = g.CaseLedger({"old1": _ledger_entry("old1", ["Nguyễn Văn A"])})
    monkeypatch.setattr(g, "_run_codex", lambda prompt: _fake_json({"verdict": "UNCLEAR", "reason": "không rõ"}))
    result = g.dedupe_against_ledger(candidate, ledger)
    assert result.is_duplicate is False
    assert result.dedupe_confidence == "low"


def test_dedupe_no_collision_low_confidence_when_date_range_unavailable():
    """FIX (Codex review Stage 1 round 2, High mới #1): verify_sources()
    Stage 1 LUÔN để date_range=None -- tiêu chí blocking ">=2/3 tín hiệu"
    thực chất chỉ còn 2 tín hiệu (location+organization), yếu hơn thiết kế.
    'Không có collision' trong điều kiện này phải là 'low' confidence
    (không đủ tự tin để coi là case mới), không phải 'high' như trước."""
    candidate = _candidate_with_fingerprint("new1", ["Người Không Trùng"])  # _candidate_with_fingerprint() luôn tạo date_range=None
    ledger = g.CaseLedger({})
    result = g.dedupe_against_ledger(candidate, ledger)
    assert result.is_duplicate is False
    assert result.dedupe_confidence == "low"


def test_dedupe_no_collision_high_confidence_when_date_range_available():
    ef = g.EventFingerprint(normalized_core_act="x", date_range=("2020-01-01", "2020-01-02"), locations=[], organizations=[], all_named_individuals=["Người Không Trùng"], decision_identifiers=[])
    person = g.NamedIndividual(canonical_name="Người Không Trùng", identity_confidence="high", role="victim")
    candidate = g.CandidateCase(case_id="new1", case_key="new1", working_title="Case new1", named_individuals=[person], event_fingerprint=ef)
    ledger = g.CaseLedger({})
    result = g.dedupe_against_ledger(candidate, ledger)
    assert result.is_duplicate is False
    assert result.dedupe_confidence == "high"


def test_dedupe_invalid_llm_verdict_fails_closed_to_unclear(monkeypatch):
    candidate = _candidate_with_fingerprint("new1", ["Nguyễn Văn A"])
    ledger = g.CaseLedger({"old1": _ledger_entry("old1", ["Nguyễn Văn A"])})
    monkeypatch.setattr(g, "_run_codex", lambda prompt: _fake_json({"verdict": "NOT_A_REAL_VERDICT", "reason": "x"}))
    result = g.dedupe_against_ledger(candidate, ledger)
    assert result.verdict == "UNCLEAR"
    assert result.dedupe_confidence == "low"


def test_dedupe_high_new2_regression_same_event_after_unclear_not_skipped(monkeypatch):
    """FIX (Codex review Stage 1 round 2, High mới #2): bản trước return
    NGAY khi gặp UNCLEAR đầu tiên trong vòng lặp collisions -- 1 collision
    SAU đó có thể là SAME_EVENT thật nhưng không bao giờ được xét, khiến
    duplicate thật bị bỏ sót chỉ vì thứ tự ngẫu nhiên. Dựng 2 collision:
    cái đầu adjudicate ra UNCLEAR, cái sau ra SAME_EVENT -- kết quả cuối
    PHẢI là is_duplicate=True (SAME_EVENT thắng), không phải UNCLEAR."""
    candidate = _candidate_with_fingerprint("new1", ["Nguyễn Văn A", "Trần Thị B"])
    ledger = g.CaseLedger({
        "old_unclear": _ledger_entry("old_unclear", ["Nguyễn Văn A"]),
        "old_same": _ledger_entry("old_same", ["Trần Thị B"]),
    })

    verdicts_in_order = iter(["UNCLEAR", "SAME_EVENT"])

    def _fake_codex(prompt):
        return _fake_json({"verdict": next(verdicts_in_order), "reason": "x"})

    monkeypatch.setattr(g, "_run_codex", _fake_codex)
    result = g.dedupe_against_ledger(candidate, ledger)
    assert result.is_duplicate is True
    assert result.verdict == "SAME_EVENT"
    assert result.matched_case_id == "old_same"


def test_dedupe_high3_regression_rejected_case_resurfacing_blocked():
    """Regression test TRỰC TIẾP cho High #3 (Codex review Stage 1):
    case_id được sinh TẤT ĐỊNH từ (discovery_source_file, working_title) --
    1 case đã REJECTED_POLICY rồi được discover LẠI (chạy lại
    discover_candidates() trên cùng file nguồn) sinh ra ĐÚNG case_id cũ.
    stage1_blocking() tự loại trừ entry.case_id==candidate.case_id (đúng,
    tránh so với chính nó) -- nhưng nếu không có check riêng, dedupe sẽ
    'không thấy' entry rejected đó và trả về is_duplicate=False oan."""
    candidate = _candidate_with_fingerprint("case_abc", ["Nguyễn Văn A"])
    rejected_entry = _ledger_entry("case_abc", ["Nguyễn Văn A"], status=g.CaseLedgerStatus.REJECTED_POLICY)
    ledger = g.CaseLedger({"case_abc": rejected_entry})
    result = g.dedupe_against_ledger(candidate, ledger)
    assert result.is_duplicate is True
    assert result.matched_case_id == "case_abc"
    assert result.matched_case_status == "rejected_policy"
    assert result.dedupe_confidence == "high"


def test_dedupe_high3_regression_merged_into_resurfacing_blocked():
    candidate = _candidate_with_fingerprint("case_xyz", ["B"])
    ledger = g.CaseLedger({"case_xyz": _ledger_entry("case_xyz", ["B"], status=g.CaseLedgerStatus.MERGED_INTO)})
    result = g.dedupe_against_ledger(candidate, ledger)
    assert result.is_duplicate is True


def _ledger_entry_merged_into(case_id, names, merged_into_case_id):
    entry = _ledger_entry(case_id, names, status=g.CaseLedgerStatus.MERGED_INTO)
    entry.merged_into_case_id = merged_into_case_id
    return entry


def test_dedupe_high_round4_regression_canonical_not_flagged_duplicate_of_its_own_alias(monkeypatch):
    """Regression test TRỰC TIẾP cho High mới (Codex review Stage 1 round
    4): case A (chính danh, canonical) từng có case B được merge làm alias
    của nó (status=MERGED_INTO, merged_into_case_id="A"). Khi A được xử lý
    lại (vd re-verify), B vẫn còn trong ledger và VẪN chia sẻ fingerprint
    với A -- nếu không loại B khỏi collision, A sẽ bị đưa đi adjudicate với
    B, LLM hợp lý trả SAME_EVENT (đúng thật -- chúng LÀ cùng 1 sự kiện),
    khiến A (case CHÍNH DANH) bị đánh nhầm là 'duplicate của chính alias
    của nó' -- ngược hoàn toàn logic merge. _run_codex bị mock LUÔN trả
    SAME_EVENT để mô phỏng đúng rủi ro thật (B và A THẬT SỰ giống nhau)."""
    candidate_a = _candidate_with_fingerprint("A", ["Nguyễn Văn A"])
    entry_b = _ledger_entry_merged_into("B", ["Nguyễn Văn A"], merged_into_case_id="A")
    ledger = g.CaseLedger({"B": entry_b})

    def _always_same_event(prompt):
        return _fake_json({"verdict": "SAME_EVENT", "reason": "giống nhau thật"})

    monkeypatch.setattr(g, "_run_codex", _always_same_event)
    result = g.dedupe_against_ledger(candidate_a, ledger)
    assert result.is_duplicate is False
    assert result.matched_case_id != "B"


def test_is_self_or_alias_of():
    entry_self = _ledger_entry("A", ["x"])
    entry_alias = _ledger_entry_merged_into("B", ["x"], merged_into_case_id="A")
    entry_unrelated = _ledger_entry("C", ["x"])
    assert g._is_self_or_alias_of(entry_self, "A") is True
    assert g._is_self_or_alias_of(entry_alias, "A") is True
    assert g._is_self_or_alias_of(entry_unrelated, "A") is False


def test_dedupe_surfaced_same_case_id_not_treated_as_rejected():
    """1 candidate đang ở trạng thái SURFACED (chưa có kết luận gì) với
    case_id trùng chính nó (bản thân nó, không phải rejected) -- KHÔNG bị
    chặn bởi check High #3 (chỉ chặn REJECTED_DUPLICATE/REJECTED_POLICY/
    MERGED_INTO), phải rơi xuống stage1_blocking bình thường."""
    candidate = _candidate_with_fingerprint("case_new", ["Người Mới"])
    ledger = g.CaseLedger({"case_new": _ledger_entry("case_new", ["Người Mới"], status=g.CaseLedgerStatus.SURFACED)})
    result = g.dedupe_against_ledger(candidate, ledger)
    assert result.is_duplicate is False  # không tự bị chặn chỉ vì SURFACED


def test_dedupe_high4_regression_non_content_seo_error_fails_closed_not_crash(monkeypatch):
    """Regression test cho High #4: trước đây stage2_adjudicate() chỉ bắt
    ContentSeoError -- 1 exception KHÁC (vd TypeError giả lập lỗi thật từ
    response dạng bất thường) sẽ crash NGUYÊN tiến trình đang xử lý nhiều
    candidate khác. Giờ phải fail-closed về UNCLEAR cho ĐÚNG 1 candidate
    này, không raise ra ngoài."""
    candidate = _candidate_with_fingerprint("new1", ["Nguyễn Văn A"])
    ledger = g.CaseLedger({"old1": _ledger_entry("old1", ["Nguyễn Văn A"])})

    def _boom(prompt):
        raise TypeError("lỗi giả lập không phải ContentSeoError")

    monkeypatch.setattr(g, "_run_codex", _boom)
    result = g.dedupe_against_ledger(candidate, ledger)  # KHÔNG được raise
    assert result.verdict == "UNCLEAR"
    assert result.dedupe_confidence == "low"


def test_dedupe_medium_new1_regression_exception_content_not_leaked_into_evidence(monkeypatch):
    """Regression test cho Medium mới #1 (Codex review Stage 1 round 3):
    round 2's fix chỉ CẮT NGẮN nội dung exception (200 ký tự đầu) trước khi
    đưa vào evidence -- vẫn có thể lộ path/token/nội dung nhạy cảm nằm
    trong 200 ký tự đó. Giờ evidence KHÔNG được chứa BẤT KỲ phần nào của
    str(exc), chỉ chứa tên loại exception."""
    candidate = _candidate_with_fingerprint("new1", ["Nguyễn Văn A"])
    ledger = g.CaseLedger({"old1": _ledger_entry("old1", ["Nguyễn Văn A"])})
    secret_marker = "BÍ_MẬT_KHÔNG_ĐƯỢC_LỌT_RA_ledger_secret_path_or_token_xyz123"

    def _boom(prompt):
        raise RuntimeError(secret_marker)

    monkeypatch.setattr(g, "_run_codex", _boom)
    verdict, reason = g.stage2_adjudicate(candidate, ledger.get("old1"))
    assert verdict == "UNCLEAR"
    assert secret_marker not in reason
    assert "RuntimeError" in reason


def test_dedupe_high4_regression_non_dict_response_fails_closed(monkeypatch):
    """_extract_json() thật luôn trả dict khi thành công (biên {}), nhưng
    defense-in-depth ở stage2_adjudicate() vẫn phải tự kiểm tra kiểu --
    giả lập bằng cách monkeypatch thẳng _extract_json để mô phỏng 1 caller/
    phiên bản tương lai trả về kiểu khác."""
    candidate = _candidate_with_fingerprint("new1", ["Nguyễn Văn A"])
    ledger = g.CaseLedger({"old1": _ledger_entry("old1", ["Nguyễn Văn A"])})
    monkeypatch.setattr(g, "_run_codex", lambda prompt: "irrelevant")
    monkeypatch.setattr(g, "_extract_json", lambda text: ["not", "a", "dict"])
    result = g.dedupe_against_ledger(candidate, ledger)
    assert result.verdict == "UNCLEAR"
    assert result.dedupe_confidence == "low"


# =============================================================================
# Rank -- §1.12
# =============================================================================

def test_rank_candidates_orders_by_source_quality():
    strong = g.CandidateCase(case_id="strong", case_key="strong", working_title="Strong", sources=[_source("s1", g.PublisherTier.PUBLIC_RECORD), _source("s2", g.PublisherTier.REPUTABLE_PRESS, "l2")])
    weak = g.CandidateCase(case_id="weak", case_key="weak", working_title="Weak", sources=[_source("s3", g.PublisherTier.AGGREGATOR)])
    ranked = g.rank_candidates([weak, strong])
    assert ranked[0].case_id == "strong"


def test_source_quality_score_round4_regression_does_not_double_count_duplicate_source_id():
    """Regression test cho Low (Codex review Stage 1 round 4): 2
    SourceRecord trùng source_id (vd URL tham khảo bị liệt kê lặp trong
    file nghiên cứu gốc) không được cộng weight 2 lần."""
    single = g.CandidateCase(case_id="single", case_key="single", working_title="Single", sources=[_source("s1", g.PublisherTier.PUBLIC_RECORD)])
    duplicated = g.CandidateCase(case_id="dup", case_key="dup", working_title="Dup", sources=[_source("s1", g.PublisherTier.PUBLIC_RECORD), _source("s1", g.PublisherTier.PUBLIC_RECORD)])
    assert g._source_quality_score(single) == g._source_quality_score(duplicated)


# =============================================================================
# verify_sources() -- LLM extraction, mocked
# =============================================================================

def test_verify_sources_grounds_excerpts_and_fails_closed_on_ungrounded_claim(monkeypatch):
    tiers = g.load_source_tiers()
    case_text = "## 1. Vụ án Test\n\nNguyễn Văn A đã bị kết án tử hình theo bản án phúc thẩm có hiệu lực.\n"
    stub = {"case_id": "c1", "case_key": "vu_an_test", "working_title": "Vụ án Test", "discovery_source_file": "X.md", "case_text": case_text, "reference_urls": ["https://vnexpress.net/x"]}

    fake_response = {
        "named_individuals": [{
            "canonical_name": "Nguyễn Văn A", "role": "convicted_perpetrator",
            "disposition": "convicted", "disposition_excerpt": "Nguyễn Văn A đã bị kết án tử hình theo bản án phúc thẩm có hiệu lực.",
            "life_status": "unknown", "life_status_excerpt": "",
            "finality_state": "final",
            "finality_excerpt": "CÂU BỊA KHÔNG CÓ TRONG NGUỒN",  # cố tình không grounding được
            "identity_confidence": "high",
        }],
        "core_facts": [{"fact_id": "F1", "statement": "bị kết án tử hình", "fact_type": "legal_outcome", "excerpt": "Nguyễn Văn A đã bị kết án tử hình theo bản án phúc thẩm có hiệu lực."}],
        "event_fingerprint": {"normalized_core_act": "giết người", "locations": [], "organizations": [], "decision_identifiers": []},
    }
    monkeypatch.setattr(g, "_run_agy", lambda prompt: _fake_json(fake_response))

    candidate = g.verify_sources(stub, tiers)
    person = candidate.named_individuals[0]
    assert person.legal_status.disposition == g.DispositionStatus.CONVICTED  # grounded -> giữ nguyên
    assert person.legal_status.finality_state == g.FinalityState.UNKNOWN  # KHÔNG grounding được -> fail-closed về UNKNOWN
    assert person.legal_status.cross_verified is False  # Stage 1 luôn False
    assert candidate.sources[0].publisher_tier == g.PublisherTier.REPUTABLE_PRESS


def test_verify_sources_medium7_regression_core_facts_have_no_fabricated_source_id(monkeypatch):
    """Regression test cho Medium #7 (Codex review Stage 1): bản trước gán
    corroborating_source_ids=["local_<case_id>"] cho MỌI core_fact -- 1 id
    KHÔNG khớp bất kỳ SourceRecord.source_id thật nào trong candidate.sources
    (những cái đó đều 'src_<hash url>'), khiến C1/C3 luôn FAIL vì lookup
    không bao giờ khớp (fail-closed đúng nhưng SAI LÝ DO). Giờ
    corroborating_source_ids PHẢI rỗng (Stage 1 trung thực: chưa xác định
    được excerpt trích từ URL cụ thể nào) -- và fact có excerpt KHÔNG
    grounding được phải bị LOẠI BỎ hoàn toàn khỏi core_facts, không giữ lại
    với corroborating rỗng lẫn lộn với fact grounding tốt."""
    tiers = g.load_source_tiers()
    case_text = "## 1. Vụ án Test\n\nNguyễn Văn A đã bị kết án tử hình.\n"
    stub = {"case_id": "c3", "case_key": "vu_an_test3", "working_title": "Vụ án Test 3", "discovery_source_file": "X.md", "case_text": case_text, "reference_urls": ["https://vnexpress.net/x"]}
    fake_response = {
        "named_individuals": [],
        "core_facts": [
            {"fact_id": "F1", "statement": "bị kết án tử hình", "fact_type": "legal_outcome", "excerpt": "Nguyễn Văn A đã bị kết án tử hình."},
            {"fact_id": "F2", "statement": "bịa đặt", "fact_type": "legal_outcome", "excerpt": "CÂU HOÀN TOÀN KHÔNG CÓ TRONG NGUỒN"},
        ],
        "event_fingerprint": {"normalized_core_act": "x", "locations": [], "organizations": [], "decision_identifiers": []},
    }
    monkeypatch.setattr(g, "_run_agy", lambda prompt: _fake_json(fake_response))
    candidate = g.verify_sources(stub, tiers)
    assert len(candidate.core_facts) == 1  # F2 (ungrounded) bị loại bỏ hoàn toàn
    assert candidate.core_facts[0].fact_id == "F1"
    assert candidate.core_facts[0].corroborating_source_ids == []  # không có ID giả


def test_verify_sources_unrecognized_role_fails_closed_to_accused_unconvicted(monkeypatch):
    tiers = g.load_source_tiers()
    case_text = "## 1. Vụ án Test\n\nMột người tên X xuất hiện.\n"
    stub = {"case_id": "c2", "case_key": "vu_an_test2", "working_title": "Vụ án Test 2", "discovery_source_file": "X.md", "case_text": case_text, "reference_urls": []}
    fake_response = {
        "named_individuals": [{"canonical_name": "X", "role": "not_a_real_role", "disposition": "unknown", "disposition_excerpt": "", "life_status": "unknown", "life_status_excerpt": "", "finality_state": "unknown", "finality_excerpt": "", "identity_confidence": "low"}],
        "core_facts": [],
        "event_fingerprint": {"normalized_core_act": "x", "locations": [], "organizations": [], "decision_identifiers": []},
    }
    monkeypatch.setattr(g, "_run_agy", lambda prompt: _fake_json(fake_response))
    candidate = g.verify_sources(stub, tiers)
    assert candidate.named_individuals[0].role == "accused_unconvicted"


# =============================================================================
# _extract_date_range() / verify_sources() date_range wiring -- task #261
# regression: EventFingerprint.date_range từng hardcode None vô điều kiện,
# khiến dedupe_against_ledger() coi MỌI candidate không va chạm blocking là
# "low signal" (xem comment lịch sử ở dedupe_against_ledger()). Test dưới
# đây xác nhận date_range giờ được trích thật khi có đủ định dạng + excerpt
# grounding, và vẫn fail-closed về None khi thiếu bất kỳ điều kiện nào.
#
# ROUND 1 (Codex adversarial review, đối kháng thật, tìm được 2 HIGH + nhiều
# MEDIUM): thêm test cho từng finding CONFIRMED, sửa test_extract_date_range_
# full_iso_dates (từng dùng ngày "kết thúc điều tra" làm date_range_end --
# tự vi phạm chính quy tắc "chỉ ngày hành vi chính" mà code hướng tới).
# =============================================================================

def test_extract_date_range_valid_grounded_pair():
    case_text = "Vụ án xảy ra trong khoảng 2001-2004 tại TP.HCM."
    ef = {"date_range_start": "2001", "date_range_end": "2004", "date_range_excerpt": "xảy ra trong khoảng 2001-2004 tại TP.HCM"}
    assert g._extract_date_range(ef, case_text) == ("2001", "2004")


def test_extract_date_range_full_iso_dates():
    """FIX (Codex review round 1, MEDIUM #2): bản trước dùng ngày "kết thúc
    điều tra" làm date_range_end -- đúng loại ngày PHẢI bị loại trừ theo
    _EXTRACT_CASE_FACTS_PROMPT (chỉ ngày hành vi chính). Sửa lại case_text/
    excerpt để CẢ HAI mốc đều là ngày hành vi phạm tội, không phải tố tụng."""
    case_text = "Hành vi phạm tội bắt đầu ngày 2001-03-15 và kết thúc ngày 2001-06-20."
    ef = {"date_range_start": "2001-03-15", "date_range_end": "2001-06-20", "date_range_excerpt": "Hành vi phạm tội bắt đầu ngày 2001-03-15 và kết thúc ngày 2001-06-20"}
    assert g._extract_date_range(ef, case_text) == ("2001-03-15", "2001-06-20")


def test_extract_date_range_recognizes_vietnamese_ddmmyyyy_format_real_case():
    """Regression TRỰC TIẾP trên dữ liệu THẬT (task #262): sau khi task #261's
    fix triển khai, chạy verify_sources() trên 8 case CL thật (Năm Cam, Lê
    Văn Luyện, O.J. Simpson...) cho thấy TẤT CẢ vẫn có date_range=None dù
    LLM trích ĐÚNG ngày (vd Lê Văn Luyện: date_range_start=end='2011-08-24',
    excerpt nguyên văn từ SOURCES thật "Đêm 24/8/2011, tại tiệm vàng Ngọc
    Bích..."). Nguyên nhân: nhánh full-date cũ đòi literal ISO substring
    ('2011-08-24') xuất hiện trong excerpt, nhưng nguồn tiếng Việt LUÔN viết
    ngày dạng DD/MM/YYYY, không bao giờ ISO -- khiến check gần như luôn
    fail trên dữ liệu thật, làm fix #261 vô hiệu trên thực tế dù test
    synthetic vẫn pass. _full_date_value_entailed_by_excerpt() giờ chấp
    nhận CẢ dạng DD/MM/YYYY (có/không số 0 đầu) lẫn ISO."""
    excerpt = (
        "Đêm 24/8/2011, tại tiệm vàng Ngọc Bích (huyện Lục Nam, tỉnh Bắc Giang), "
        "Lê Văn Luyện (sinh 18/10/1993) đã đột nhập, sát hại chủ tiệm vàng."
    )
    case_text = "## 2. Vụ án Lê Văn Luyện — thảm sát tiệm vàng Ngọc Bích, Bắc Giang (2011)\n\n" + excerpt
    ef = {"date_range_start": "2011-08-24", "date_range_end": "2011-08-24", "date_range_excerpt": excerpt}
    assert g._extract_date_range(ef, case_text) == ("2011-08-24", "2011-08-24")


def test_extract_date_range_ddmmyyyy_still_rejects_fabricated_wrong_date():
    """Đối chứng cho test trên: mở rộng định dạng KHÔNG được làm yếu fail-
    closed -- 1 ngày SAI (dù đúng định dạng DD/MM/YYYY) không có trong
    excerpt vẫn phải bị từ chối."""
    excerpt = "Vụ án xảy ra ngày 24/8/2011."
    ef = {"date_range_start": "2011-08-25", "date_range_end": "2011-08-25", "date_range_excerpt": excerpt}
    assert g._extract_date_range(ef, excerpt) is None


def test_extract_date_range_ddmmyyyy_rejects_substring_of_longer_code():
    """Regression TRỰC TIẾP cho Codex review round 1 (task #262), MEDIUM
    (repro của reviewer): '24/8/2011' là substring trần của '124/8/2011'
    (vd 1 phần mã hồ sơ dạng số/số/số dài hơn) -- _full_date_value_entailed_
    by_excerpt() giờ đòi ranh giới chữ số cả 2 đầu, cùng kỷ luật với
    _year_value_entailed_by_excerpt()."""
    excerpt = "Mã hồ sơ 124/8/2011 đã được lưu."
    ef = {"date_range_start": "2011-08-24", "date_range_end": "2011-08-24", "date_range_excerpt": excerpt}
    assert g._extract_date_range(ef, excerpt) is None


def test_extract_date_range_ddmmyyyy_rejects_substring_of_alnum_identifier():
    """Regression TRỰC TIẾP cho Codex review round 2 (task #262) (repro của
    reviewer -- round 1's fix `(?<!\\d)...(?!\\d)` vẫn CHƯA đóng đủ): ranh
    giới chỉ cấm CHỮ SỐ liền kề, không cấm CHỮ CÁI -- 'A24/8/2011B' và
    'A2011-08-24B' (mã định danh chữ-số, không phải ngày) vẫn bị xác nhận
    nhầm. Đổi sang ranh giới `\\w` (loại cả chữ cái lẫn chữ số/underscore)."""
    excerpt_vn = "Mã hồ sơ A24/8/2011B đã được lưu."
    ef_vn = {"date_range_start": "2011-08-24", "date_range_end": "2011-08-24", "date_range_excerpt": excerpt_vn}
    assert g._extract_date_range(ef_vn, excerpt_vn) is None

    excerpt_iso = "Mã hồ sơ A2011-08-24B đã được lưu."
    ef_iso = {"date_range_start": "2011-08-24", "date_range_end": "2011-08-24", "date_range_excerpt": excerpt_iso}
    assert g._extract_date_range(ef_iso, excerpt_iso) is None


def test_extract_date_range_year_rejects_letter_adjacent_substring():
    """Regression TRỰC TIẾP cho Codex review round 2 (task #262) áp dụng
    ngược lại cho nhánh 'YYYY': _year_value_entailed_by_excerpt() từng chỉ
    cấm chữ số liền kề (`.isdigit()`) -- 'A2001B' (mã định danh chữ-số,
    không phải năm) vẫn được xác nhận nếu excerpt có cue gần đó. Giờ dùng
    cùng ranh giới `\\w` với nhánh full-date."""
    excerpt = "Mã hồ sơ A2001B được lập trong năm nay."
    assert g._year_value_entailed_by_excerpt("2001", excerpt) is False


def test_extract_date_range_ddmmyyyy_rejects_slash_or_hyphen_adjacent_identifier():
    """Regression TRỰC TIẾP cho Codex review round 3 (task #262), MEDIUM
    (repro của reviewer -- round 2's ranh giới `\\w` vẫn CHƯA đóng đủ): '/'
    và '-' KHÔNG nằm trong `\\w`, nên ngày vẫn bị xác nhận nhầm khi liền kề 1
    mã định danh dùng CHÍNH 2 dấu này làm phân cách (thực tế: số hiệu quyết
    định pháp lý Việt Nam thường viết "<số>/<năm>/QĐ-<toà>")."""
    excerpt1 = "Mã hồ sơ A-24/8/2011-B đã lưu."
    ef1 = {"date_range_start": "2011-08-24", "date_range_end": "2011-08-24", "date_range_excerpt": excerpt1}
    assert g._extract_date_range(ef1, excerpt1) is None

    excerpt2 = "Mã hồ sơ X/2011-08-24/Y đã lưu."
    ef2 = {"date_range_start": "2011-08-24", "date_range_end": "2011-08-24", "date_range_excerpt": excerpt2}
    assert g._extract_date_range(ef2, excerpt2) is None


def test_extract_date_range_year_rejects_decision_number_pattern():
    """Regression TRỰC TIẾP cho Codex review round 3 (task #262), MEDIUM
    (2 repro còn lại của reviewer): "năm 2001/QĐ-TA" -- cue "năm" đứng NGAY
    TRƯỚC "2001" (đúng cú pháp cue-anchor), nhưng "2001" là 1 phần số hiệu
    quyết định (năm/QĐ-toà), không phải năm hành vi độc lập. _cue_anchored_
    years() giờ kiểm tra ký tự NGAY SAU năm: '/' hoặc chữ/số dính liền -> loại
    trừ; '-' chỉ được giữ nếu mở đầu 1 năm 4-chữ-số KHÁC sạch (cú pháp
    khoảng thời gian thật)."""
    excerpt1 = "Bản án năm 2001/QĐ-TA đã ban hành."
    ef1 = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": excerpt1}
    assert g._extract_date_range(ef1, excerpt1) is None

    excerpt2 = "Mã hồ sơ năm 2001-A đã lập."
    ef2 = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": excerpt2}
    assert g._extract_date_range(ef2, excerpt2) is None


def test_extract_date_range_year_range_via_cue_still_works_after_boundary_tightening():
    """Đối chứng: siết ranh giới cue-anchor không được làm hỏng cú pháp
    khoảng thời gian THẬT ("khoảng 2001-2004") -- '-2004' là 1 năm 4-chữ-số
    sạch theo ngay sau '2001', phải vẫn được giữ làm ngoại lệ hợp lệ."""
    excerpt = "xảy ra trong khoảng 2001-2004 tại TP.HCM."
    ef_start = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": excerpt}
    assert g._extract_date_range(ef_start, excerpt) == ("2001", "2001")
    ef_end = {"date_range_start": "2004", "date_range_end": "2004", "date_range_excerpt": excerpt}
    assert g._extract_date_range(ef_end, excerpt) == ("2004", "2004")


def test_extract_date_range_rejects_unicode_dash_adjacent_identifier():
    """Regression TRỰC TIẾP cho Codex review round 4 (task #262), MEDIUM
    (repro của reviewer -- round 3's ranh giới ASCII '-' vẫn CHƯA đóng đủ):
    text copy từ Word/PDF thường chứa dash Unicode trông giống hệt ASCII '-'
    nhưng KHÔNG khớp `[\\w/-]` -- vd en dash '–' (U+2013), non-breaking
    hyphen '‑' (U+2011). '_DATE_RANGE_IDENTIFIER_BOUNDARY_CLASS' giờ liệt
    kê tường minh các dash Unicode thường gặp, KHÔNG hưởng ngoại lệ range
    (chỉ ASCII '-' mới có ngoại lệ đó)."""
    excerpt1 = "Mã hồ sơ năm 2001–A đã lập."  # en dash U+2013
    ef1 = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": excerpt1}
    assert g._extract_date_range(ef1, excerpt1) is None

    excerpt2 = "Mã hồ sơ năm 2001‑A đã lập."  # non-breaking hyphen U+2011
    ef2 = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": excerpt2}
    assert g._extract_date_range(ef2, excerpt2) is None

    excerpt3 = "Mã hồ sơ A–24/8/2011–B đã lưu."  # en dash quanh full date
    ef3 = {"date_range_start": "2011-08-24", "date_range_end": "2011-08-24", "date_range_excerpt": excerpt3}
    assert g._extract_date_range(ef3, excerpt3) is None


def test_extract_date_range_ddmmyyyy_zero_padding_matrix():
    """Ma trận zero-padding: '3/4', '03/4', '3/04', '03/04' đều phải nhận
    đúng cho value '2011-04-03' (theo yêu cầu coverage của Codex round 1)."""
    for day_str, month_str in (("3", "4"), ("03", "4"), ("3", "04"), ("03", "04")):
        excerpt = f"Đêm {day_str}/{month_str}/2011, hành vi xảy ra."
        ef = {"date_range_start": "2011-04-03", "date_range_end": "2011-04-03", "date_range_excerpt": excerpt}
        assert g._extract_date_range(ef, excerpt) == ("2011-04-03", "2011-04-03"), repr(excerpt)


def test_extract_date_range_ddmmyyyy_accepts_both_separators():
    for sep in ("/", "-"):
        excerpt = f"Đêm 24{sep}8{sep}2011, hành vi xảy ra."
        ef = {"date_range_start": "2011-08-24", "date_range_end": "2011-08-24", "date_range_excerpt": excerpt}
        assert g._extract_date_range(ef, excerpt) == ("2011-08-24", "2011-08-24"), repr(excerpt)


def test_extract_date_range_ddmmyyyy_day_month_ambiguity_not_confused():
    """'03/04/2011' viết theo thứ tự D/M (chuẩn tiếng Việt) chỉ được khớp
    ĐÚNG value có day=3/month=4 ('2011-04-03'), KHÔNG khớp value đảo ngược
    ('2011-03-04', day=3/month=... nhầm) -- xác nhận không có ambiguity."""
    excerpt = "Đêm 03/04/2011, hành vi xảy ra."
    ef_correct = {"date_range_start": "2011-04-03", "date_range_end": "2011-04-03", "date_range_excerpt": excerpt}
    assert g._extract_date_range(ef_correct, excerpt) == ("2011-04-03", "2011-04-03")
    ef_wrong = {"date_range_start": "2011-03-04", "date_range_end": "2011-03-04", "date_range_excerpt": excerpt}
    assert g._extract_date_range(ef_wrong, excerpt) is None


def test_extract_date_range_ddmmyyyy_different_start_end_vietnamese_format():
    """2 mốc KHÁC nhau, cả hai đều viết dạng DD/MM/YYYY tiếng Việt (không
    chỉ trường hợp start==end đã test ở trên)."""
    excerpt = "Hành vi bắt đầu ngày 24/8/2011 và kết thúc ngày 31/8/2011."
    ef = {"date_range_start": "2011-08-24", "date_range_end": "2011-08-31", "date_range_excerpt": excerpt}
    assert g._extract_date_range(ef, excerpt) == ("2011-08-24", "2011-08-31")


def test_extract_date_range_missing_fields_returns_none():
    case_text = "Không có thời điểm cụ thể nào trong văn bản này."
    assert g._extract_date_range({}, case_text) is None
    assert g._extract_date_range({"date_range_start": "", "date_range_end": "", "date_range_excerpt": ""}, case_text) is None


def test_extract_date_range_ungrounded_excerpt_fails_closed():
    case_text = "Vụ án xảy ra năm 2001."
    ef = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": "CÂU BỊA KHÔNG CÓ TRONG NGUỒN"}
    assert g._extract_date_range(ef, case_text) is None


def test_extract_date_range_malformed_value_fails_closed():
    case_text = "Vụ án xảy ra đầu những năm 2000."
    ef = {"date_range_start": "đầu những năm 2000", "date_range_end": "đầu những năm 2000", "date_range_excerpt": "đầu những năm 2000"}
    assert g._extract_date_range(ef, case_text) is None


def test_extract_date_range_swapped_order_normalizes():
    case_text = "Vụ án được phát hiện năm 2004, hành vi phạm tội bắt đầu từ năm 2001."
    ef = {"date_range_start": "2004", "date_range_end": "2001", "date_range_excerpt": "phát hiện năm 2004, hành vi phạm tội bắt đầu từ năm 2001"}
    assert g._extract_date_range(ef, case_text) == ("2001", "2004")


def test_extract_date_range_fabricated_values_not_entailed_by_excerpt_fails_closed():
    """Regression TRỰC TIẾP cho Codex review round 1, HIGH #1 (repro chính
    xác của reviewer): excerpt LÀ substring thật của case_text (không bịa),
    nhưng start/end KHÔNG khớp năm nào trong chính excerpt đó -- bản trước
    (chỉ check _excerpt_grounded) trả thẳng ("2020","2021") dù case_text chỉ
    nói năm 2001. Việc này nguy hiểm hơn null vì date_range non-None tự nâng
    dedupe_confidence lên "high", né luôn fail-closed escalation."""
    case_text = "Vụ án xảy ra năm 2001."
    ef = {"date_range_start": "2020", "date_range_end": "2021", "date_range_excerpt": "Vụ án xảy ra năm 2001."}
    assert g._extract_date_range(ef, case_text) is None


def test_extract_date_range_invalid_calendar_values_fail_closed():
    """FIX (Codex review round 1, MEDIUM #3): _DATE_RANGE_VALUE_RE hình
    dạng suông trước đây chấp nhận '0000', '9999-99-99', '2021-02-29' (2021
    không phải năm nhuận) -- _valid_date_range_value() giờ validate lịch
    thật qua datetime.strptime()."""
    assert g._extract_date_range({"date_range_start": "0000", "date_range_end": "0000", "date_range_excerpt": "năm 0000"}, "Sự kiện năm 0000.") is None
    assert g._extract_date_range({"date_range_start": "2021-02-29", "date_range_end": "2021-02-29", "date_range_excerpt": "ngày 2021-02-29"}, "Xảy ra ngày 2021-02-29 (không có thật, 2021 không nhuận).") is None
    assert g._extract_date_range({"date_range_start": "2020-13-40", "date_range_end": "2020-13-40", "date_range_excerpt": "ngày 2020-13-40"}, "Xảy ra ngày 2020-13-40.") is None


def test_extract_date_range_fabricated_full_date_wrong_year_fails_closed():
    """Round 2 addition: bịa NGÀY ĐẦY ĐỦ nhưng excerpt chỉ chứng minh NĂM --
    check full-date branch của _extract_date_range() đòi TOÀN BỘ giá trị
    'YYYY-MM-DD' (không chỉ năm) xuất hiện nguyên văn trong excerpt."""
    case_text = "Vụ án xảy ra năm 2001, không rõ ngày cụ thể."
    ef = {"date_range_start": "2001-12-31", "date_range_end": "2001-12-31", "date_range_excerpt": "Vụ án xảy ra năm 2001, không rõ ngày cụ thể."}
    assert g._extract_date_range(ef, case_text) is None


def test_extract_date_range_year_lookalike_in_unrelated_number_fails_closed():
    """Regression TRỰC TIẾP cho Codex review round 2, HIGH #1 (repro của
    reviewer): '2001' xuất hiện trong excerpt nhưng LÀ số hiệu bản án, không
    phải năm -- _year_value_entailed_by_excerpt() đòi từ khoá thời gian
    ("năm"/"tháng"/"ngày"/...) nằm SÁT năm đó, không chỉ "có mặt đâu đó
    trong câu". "không rõ năm" ở cuối câu KHÔNG được tính vì cách xa 4 chữ số
    '2001' hơn cửa sổ 12 ký tự."""
    case_text = "Bản án số 2001, hành vi xảy ra không rõ năm."
    ef = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": "Bản án số 2001, hành vi xảy ra không rõ năm."}
    assert g._extract_date_range(ef, case_text) is None


def test_extract_date_range_cue_borrowed_by_nearby_unrelated_number_fails_closed():
    """Regression TRỰC TIẾP cho Codex review round 3, HIGH #1 (repro của
    reviewer -- round 2's fix vẫn CHƯA đóng đủ): '2001' là số hiệu bản án,
    cue "vào năm" thật ra thuộc về '2005' (năm THẬT của hành vi) đứng SAU nó
    -- nhưng vì cả 2 số đều nằm trong cửa sổ ±12 ký tự quanh '2001', bản
    round 2 (chỉ đòi "có cue trong cửa sổ", không xác định cue đó thuộc về
    SỐ NÀO) xác nhận NHẦM '2001'. _year_value_entailed_by_excerpt() giờ neo
    ở CUỐI cụm cue rồi tìm token 4-chữ-số GẦN cụm cue đó NHẤT trong toàn bộ
    excerpt -- '2005' mới là năm thật sự được "vào năm" mô tả, không phải
    '2001'."""
    case_text = "Bản án số 2001, vào năm 2005."
    ef = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": "Bản án số 2001, vào năm 2005."}
    assert g._extract_date_range(ef, case_text) is None
    # xác nhận '2005' (năm THẬT được "vào năm" mô tả) vẫn được nhận đúng
    ef2 = {"date_range_start": "2005", "date_range_end": "2005", "date_range_excerpt": "Bản án số 2001, vào năm 2005."}
    assert g._extract_date_range(ef2, case_text) == ("2005", "2005")


def test_extract_date_range_anaphoric_trailing_cue_does_not_borrow_preceding_number():
    """Regression TRỰC TIẾP cho Codex review round 4, HIGH #1 (repro của
    reviewer -- round 3's "nearest cue token" fix vẫn CHƯA đóng đủ): cụm cue
    hồi chỉ "năm đó" (không có số nào theo sau nó) đứng SAU '2001' (số bản
    án) trong văn bản -- round 3's nearest-token-2-chiều tìm NGƯỢC về '2001'
    và xác nhận NHẦM, dù "năm đó" ngữ nghĩa hồi chỉ '2005' (năm đã nêu trước
    đó trong câu), không mô tả '2001'. _year_value_entailed_by_excerpt() giờ
    CHỈ chấp nhận cue đứng NGAY TRƯỚC năm (`_cue_anchored_years()`, hướng
    cue->năm duy nhất) -- cue đứng SAU (hồi chỉ) không bao giờ tự xác nhận
    được năm nào."""
    case_text = "Năm 2005, Tòa ra bản án số 2001, năm đó bị cáo bỏ trốn."
    ef = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": case_text}
    assert g._extract_date_range(ef, case_text) is None
    # '2005' được cue "Năm" đứng NGAY TRƯỚC xác nhận trực tiếp -- vẫn đúng
    ef2 = {"date_range_start": "2005", "date_range_end": "2005", "date_range_excerpt": case_text}
    assert g._extract_date_range(ef2, case_text) == ("2005", "2005")


def test_extract_date_range_cue_across_newline_or_tab_does_not_anchor_next_number():
    """Regression TRỰC TIẾP cho Codex review round 5, HIGH #1 phần (a) (repro
    của reviewer -- round 4's fix dùng `\\s+` làm dấu phân cách, khớp CẢ
    newline/tab, khiến cue ở CUỐI DÒNG "neo" nhầm số ở ĐẦU DÒNG/sau tab kế
    tiếp không liên quan). `_DATE_RANGE_CUE_THEN_YEAR_RE` giờ CHỈ chấp nhận
    dấu cách thường (` +`) làm phân cách -- newline/tab KHÔNG được tính."""
    case_newline = "Hành vi xảy ra không rõ năm\n2001 là số bản án."
    ef = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": case_newline}
    assert g._extract_date_range(ef, case_newline) is None

    case_tab = "Hành vi xảy ra không rõ năm\t2001 là số bản án."
    ef2 = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": case_tab}
    assert g._extract_date_range(ef2, case_tab) is None


def test_extract_date_range_cue_chain_no_longer_needed_still_matches_via_immediate_word():
    """Chuỗi cue nhiều từ ('vào năm') không còn được match như 1 cụm (đã bỏ
    nhóm lặp lồng nhau vì rủi ro hiệu năng -- xem test riêng dưới), nhưng
    VẪN nhận đúng nhờ từ NGAY TRƯỚC năm ('năm') tự nó đã là 1 cue hợp lệ."""
    case_text = "Bản án số 2001, vào năm 2005."
    ef = {"date_range_start": "2005", "date_range_end": "2005", "date_range_excerpt": case_text}
    assert g._extract_date_range(ef, case_text) == ("2005", "2005")


def test_extract_date_range_cue_regex_linear_time_no_quadratic_blowup():
    """Regression TRỰC TIẾP cho Codex review round 5, HIGH #1 phần (b) (repro
    của reviewer -- round 4's regex nối chuỗi cue lồng nhau có rủi ro
    backtracking O(n^2) trên input nhiều cue liên tiếp KHÔNG kết thúc bằng
    năm). Bỏ hẳn nhóm lặp lồng nhau -- xác nhận input 100k cue liên tiếp xử
    lý xong trong thời gian hợp lý (không treo/chậm bất thường)."""
    import time

    case_text = ("năm " * 100_000) + "không có số nào ở đây."
    ef = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": case_text}
    t0 = time.monotonic()
    result = g._extract_date_range(ef, case_text)
    elapsed = time.monotonic() - t0
    assert result is None
    assert elapsed < 5.0, f"quá chậm ({elapsed:.2f}s) -- nghi backtracking O(n^2) quay lại"


def test_extract_date_range_adjacency_requires_real_hyphen_not_just_whitespace():
    """Regression TRỰC TIẾP cho Codex review round 5, HIGH #1 phần cuối
    (repro của reviewer): nhánh "liền kề" ('khoảng 2001-2004') trước đây
    chấp nhận khoảng trắng ĐƠN THUẦN làm liền kề -- '2005 2001' (cách nhau 1
    dấu cách, KHÔNG có dấu '-') từng bị xác nhận nhầm '2001' chỉ vì đứng
    ngay sau '2005' đã cue-anchored. Giờ đòi phần đệm phải chứa dấu '-' THẬT
    (sau khi bỏ khoảng trắng 2 đầu, phải còn lại >=1 ký tự VÀ toàn bộ là
    '-')."""
    case_text = "Năm 2005 2001/QĐ-TA không liên quan."
    ef = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": case_text}
    assert g._extract_date_range(ef, case_text) is None
    # đối chứng: có dấu '-' thật vẫn được chấp nhận (không over-correct)
    case_hyphen = "khoảng 2001-2004 tại TP.HCM."
    ef2 = {"date_range_start": "2004", "date_range_end": "2004", "date_range_excerpt": case_hyphen}
    assert g._extract_date_range(ef2, case_hyphen) == ("2004", "2004")


def test_extract_date_range_adjacency_hyphen_check_excludes_newline_and_tab():
    """Regression TRỰC TIẾP cho Codex review round 6, HIGH #1 (repro của
    reviewer -- round 5's fix `gap.strip() ... set(stripped) <= {"-"}` vẫn
    CHƯA đóng đủ): `.strip()` xoá CẢ newline/tab (không chỉ dấu cách), nên
    "Năm 2005\\n- 2001/QĐ..." (dấu gạch đầu dòng bullet-list liệt kê, KHÔNG
    phải cú pháp khoảng thời gian "2001-2004") vẫn bị coi là liền kề qua
    dấu '-' vì gap="\\n- " strip() còn lại "-" . Nhánh liền kề giờ dùng
    `re.fullmatch(r" *-+ *", gap)` -- CHỈ chấp nhận dấu cách thường 2 bên
    dấu '-', không newline/tab."""
    for case_text in (
        "Năm 2005\n- 2001/QĐ là số quyết định.",
        "Năm 2005\t-\t2001/QĐ là số quyết định.",
        "Năm 2005\n\n-\n\n2001/QĐ là số quyết định.",
    ):
        ef = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": case_text}
        assert g._extract_date_range(ef, case_text) is None, repr(case_text)


def test_extract_date_range_year_token_boundary_rejects_substring_of_longer_number():
    """'2001' không được tính là "có mặt" nếu nó chỉ là 4 số ĐẦU của 1 số dài
    hơn (vd mã hồ sơ '20015-A') -- _year_value_entailed_by_excerpt() đòi
    ranh giới token (ký tự trước/sau không phải chữ số)."""
    case_text = "Mã hồ sơ 20015-A được lập, không nêu năm phạm tội."
    ef = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": "Mã hồ sơ 20015-A được lập, không nêu năm phạm tội."}
    assert g._extract_date_range(ef, case_text) is None


def test_extract_date_range_mixed_precision_rejected():
    """FIX (Codex review round 2, MEDIUM #5): start='YYYY-MM-DD' + end='YYYY'
    (hoặc ngược lại) có ngữ nghĩa mơ hồ sau khi mở bound (_date_range_bound())
    -- giá trị năm nào đại diện ngày nào? Fail-closed về None thay vì cố
    swap/suy luận, đúng đề xuất của reviewer."""
    case_text = "Hành vi bắt đầu ngày 2001-12-31 và kết thúc năm 2004."
    ef = {"date_range_start": "2001-12-31", "date_range_end": "2004", "date_range_excerpt": "Hành vi bắt đầu ngày 2001-12-31 và kết thúc năm 2004."}
    assert g._extract_date_range(ef, case_text) is None


def test_extract_date_range_known_limitation_investigation_date_not_mechanically_caught():
    """Giới hạn ĐÃ BIẾT, ghi lại có chủ đích (không giấu): excerpt nói RÕ đây
    là ngày XÉT XỬ (không phải hành vi), nhưng _year_value_entailed_by_excerpt()
    là 1 kiểm tra CƠ HỌC (ranh giới token + từ khoá thời gian sát cạnh),
    KHÔNG hiểu ngữ nghĩa "xét xử" khác "hành vi" -- vẫn PASS (date_range vẫn
    được set). Giảm nhẹ bởi: (1) _EXTRACT_CASE_FACTS_PROMPT đã yêu cầu LLM
    CHỈ trích ngày hành vi -- rủi ro còn lại là LLM không tuân thủ prompt,
    (2) date_range chỉ là 1/3 tín hiệu blocking trong stage1_blocking(),
    không tự nó quyết định trùng/không trùng case. Test này xác nhận hành vi
    HIỆN TẠI (không phải hành vi MONG MUỐN) để không ai nhầm đây là bug chưa
    phát hiện."""
    case_text = "Vụ án được xét xử năm 2001."
    ef = {"date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": "Vụ án được xét xử năm 2001."}
    assert g._extract_date_range(ef, case_text) == ("2001", "2001")


def test_extract_date_range_single_endpoint_missing_fails_closed():
    case_text = "Vụ án xảy ra năm 2001, không rõ ngày kết thúc."
    ef = {"date_range_start": "2001", "date_range_end": "", "date_range_excerpt": "xảy ra năm 2001"}
    assert g._extract_date_range(ef, case_text) is None


def test_extract_date_range_wrong_type_fails_closed():
    case_text = "Vụ án xảy ra năm 2001."
    ef = {"date_range_start": 2001, "date_range_end": 2001, "date_range_excerpt": "xảy ra năm 2001"}
    assert g._extract_date_range(ef, case_text) is None


# =============================================================================
# _date_range_bound() / stage1_blocking() mixed-precision overlap -- FIX
# (Codex review round 1, HIGH #4): so sánh string thô "2001" < "2001-06-15"
# khiến 1 case chỉ có năm và 1 case có ngày CÙNG năm bị tính SAI là không
# overlap (Python coi tiền tố ngắn hơn "nhỏ hơn"). _date_range_bound() mở
# rộng 'YYYY' thành mốc đầu/cuối năm trước khi so sánh.
# =============================================================================

def _candidate_with_date_range(case_id, name, date_range, locations=None):
    ef = g.EventFingerprint(normalized_core_act="x", date_range=date_range, locations=locations or [], organizations=[], all_named_individuals=[name], decision_identifiers=[])
    person = g.NamedIndividual(canonical_name=name, identity_confidence="high", role="victim")
    return g.CandidateCase(case_id=case_id, case_key=case_id, working_title=f"Case {case_id}", named_individuals=[person], event_fingerprint=ef)


def _ledger_entry_with_date_range(case_id, name, date_range, locations=None):
    ef = g.EventFingerprint(normalized_core_act="x", date_range=date_range, locations=locations or [], organizations=[], all_named_individuals=[name], decision_identifiers=[])
    return g.CaseLedgerEntry(
        case_id=case_id, canonical_names=[name], title_keywords=[case_id], fingerprint=ef, status=g.CaseLedgerStatus.LOW_CLEARED,
        policy_trigger=None, rejection_scope=None, recheck_policy=None, evidence_as_of=None,
        next_eligible_review_at=None, pending_alias_write=False, merged_into_case_id=None,
        first_seen_at="t0", last_updated_at="t0", history=[],
    )


def test_stage1_blocking_year_and_date_in_same_year_overlap():
    """Trước fix: '2001' < '2001-06-15' (string) -> bị tính SAI là không
    overlap. Sau fix: năm 2001 (cả năm) VÀ ngày 15/06/2001 (trong năm đó)
    phải overlap. Location trùng cho tín hiệu #2 -> overlap_count=2 -> collision."""
    candidate = _candidate_with_date_range("new1", "Người A", ("2001", "2001"), locations=["TP.HCM"])
    ledger = g.CaseLedger({"old1": _ledger_entry_with_date_range("old1", "Người B", ("2001-06-15", "2001-06-15"), locations=["TP.HCM"])})
    collisions = g.stage1_blocking(candidate, ledger)
    assert len(collisions) == 1
    assert collisions[0].case_id == "old1"


def test_stage1_blocking_year_and_date_in_different_year_no_overlap():
    candidate = _candidate_with_date_range("new1", "Người A", ("2001", "2001"), locations=["TP.HCM"])
    ledger = g.CaseLedger({"old1": _ledger_entry_with_date_range("old1", "Người B", ("2005-01-01", "2005-01-01"), locations=["TP.HCM"])})
    collisions = g.stage1_blocking(candidate, ledger)
    assert collisions == []  # chỉ 1/2 tín hiệu (location) trùng -- date không overlap thật -> không đủ blocking


def test_ledger_date_range_malformed_fails_closed_not_crash():
    """FIX (Codex review round 1, LOW #7): _entry_from_dict() trước đây tin
    thẳng bất kỳ giá trị truthy nào của fingerprint.date_range -- ledger đọc
    từ đĩa có thể chứa dữ liệu hỏng/sai định dạng (sửa tay, ghi lỗi...).
    _ledger_date_range() giờ validate lại, fail-closed về None thay vì để
    stage1_blocking() crash khi index [0]/[1] trên dữ liệu thiếu phần tử,
    hoặc tính overlap sai trên giá trị không phải ngày hợp lệ."""
    assert g._ledger_date_range(["2001"]) is None  # thiếu 1 phần tử
    assert g._ledger_date_range(["2001", "2002", "2003"]) is None  # thừa phần tử
    assert g._ledger_date_range(["0000", "0000"]) is None  # năm không hợp lệ
    assert g._ledger_date_range([2001, 2002]) is None  # sai kiểu (int, không phải str)
    assert g._ledger_date_range(None) is None
    assert g._ledger_date_range(["2001-12-31", "2004"]) is None  # mixed precision -- fail-closed, không suy luận
    assert g._ledger_date_range(["2001", "2004"]) == ("2001", "2004")  # hợp lệ -- vẫn đọc được bình thường


def test_case_ledger_load_malformed_date_range_from_disk_fails_closed_not_crash(tmp_path, monkeypatch):
    """Round 2 addition (Codex explicitly flagged round 1's test chỉ gọi
    helper trực tiếp, không đi qua CaseLedger.load()/_entry_from_dict() thật
    -- test này đóng khoảng đó): ghi 1 ledger.json THẬT trên đĩa với
    fingerprint.date_range hỏng (thiếu phần tử), load qua đúng đường sản
    xuất dùng (CaseLedger.load()), xác nhận không crash và date_range fail-
    closed về None thay vì giữ dữ liệu hỏng."""
    monkeypatch.setattr(g, "CASE_LEDGER_PATH", tmp_path / "ledger.json")
    raw = {
        "case1": {
            "case_id": "case1", "canonical_names": ["A"], "title_keywords": ["x"],
            "fingerprint": {"normalized_core_act": "x", "date_range": ["2001"], "locations": [], "organizations": [], "all_named_individuals": ["A"], "decision_identifiers": []},
            "status": "low_cleared", "policy_trigger": None, "rejection_scope": None, "recheck_policy": None,
            "evidence_as_of": None, "next_eligible_review_at": None, "pending_alias_write": False, "merged_into_case_id": None,
            "first_seen_at": "t0", "last_updated_at": "t0", "history": [],
        }
    }
    (tmp_path / "ledger.json").write_text(json.dumps(raw), encoding="utf-8")
    ledger = g.CaseLedger.load()  # KHÔNG được raise/crash
    entry = ledger.get("case1")
    assert entry is not None
    assert entry.fingerprint.date_range is None  # dữ liệu hỏng (thiếu 1 phần tử) -- fail-closed, không giữ nguyên


def test_verify_sources_populates_date_range_when_grounded(monkeypatch):
    tiers = g.load_source_tiers()
    case_text = "## 1. Vụ án Test\n\nVụ án xảy ra năm 2001 tại Hà Nội.\n"
    stub = {"case_id": "c_date1", "case_key": "vu_an_date1", "working_title": "Vụ án Date 1", "discovery_source_file": "X.md", "case_text": case_text, "reference_urls": []}
    fake_response = {
        "named_individuals": [], "core_facts": [],
        "event_fingerprint": {
            "normalized_core_act": "x", "locations": ["Hà Nội"], "organizations": [], "decision_identifiers": [],
            "date_range_start": "2001", "date_range_end": "2001", "date_range_excerpt": "xảy ra năm 2001 tại Hà Nội",
        },
    }
    monkeypatch.setattr(g, "_run_agy", lambda prompt: _fake_json(fake_response))
    candidate = g.verify_sources(stub, tiers)
    assert candidate.event_fingerprint.date_range == ("2001", "2001")


def test_verify_sources_date_range_none_when_source_silent_on_dates(monkeypatch):
    """Regression đúng ý nghĩa: KHÔNG được suy đoán/bịa ngày tháng khi
    nguồn không nêu -- date_range PHẢI vẫn là None (không phải fabricate 1
    giá trị nào đó để "cải thiện" dedupe_confidence)."""
    tiers = g.load_source_tiers()
    case_text = "## 1. Vụ án Test\n\nMột vụ án xảy ra, không rõ thời điểm.\n"
    stub = {"case_id": "c_date2", "case_key": "vu_an_date2", "working_title": "Vụ án Date 2", "discovery_source_file": "X.md", "case_text": case_text, "reference_urls": []}
    fake_response = {
        "named_individuals": [], "core_facts": [],
        "event_fingerprint": {
            "normalized_core_act": "x", "locations": [], "organizations": [], "decision_identifiers": [],
            "date_range_start": "", "date_range_end": "", "date_range_excerpt": "",
        },
    }
    monkeypatch.setattr(g, "_run_agy", lambda prompt: _fake_json(fake_response))
    candidate = g.verify_sources(stub, tiers)
    assert candidate.event_fingerprint.date_range is None
