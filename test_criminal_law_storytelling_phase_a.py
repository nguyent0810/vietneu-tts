"""Test cho criminal_law_storytelling_phase_a.py (task #270). Mock
S._run_codex đúng pattern test_cl_risk_gate_lifecycle.py (monkeypatch module
attribute, không mock qua import cục bộ -- khớp lý do đã ghi trong
_storytelling_named_individual_scan()'s docstring)."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import criminal_law_storytelling_phase_a as S  # noqa: E402


def _fake_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False)


# =============================================================================
# _storytelling_named_individual_scan / _run_storytelling_person_check
# =============================================================================

def test_named_individual_scan_fails_closed_on_malformed_llm_response(monkeypatch):
    monkeypatch.setattr(S, "_run_codex", lambda prompt: "not json {{{")
    with pytest.raises(S.LifecycleError):
        S._storytelling_named_individual_scan("văn bản bất kỳ")


def test_named_individual_scan_fails_closed_on_missing_references_key(monkeypatch):
    monkeypatch.setattr(S, "_run_codex", lambda prompt: _fake_json({"wrong_key": []}))
    with pytest.raises(S.LifecycleError):
        S._storytelling_named_individual_scan("văn bản bất kỳ")


def test_person_check_passes_when_scan_returns_no_references(monkeypatch):
    """Trường hợp regression thật đã fix (task #270): script chỉ dùng danh
    từ vai trò chung chung ('người phạm tội', 'họ') -- prompt MỚI được
    thiết kế để KHÔNG liệt kê các cụm này (khác _llm_coreference_scan cũ
    của cl_risk_gate_lifecycle.py); ở mức unit test, mô phỏng đúng hành vi
    ĐÃ ĐƯỢC KỲ VỌNG của prompt mới: scan trả về [] cho input như vậy."""
    monkeypatch.setattr(S, "_run_codex", lambda prompt: _fake_json({"references": []}))
    passed, evidence = S._run_storytelling_person_check(
        "Người phạm tội không phải lúc nào cũng bị pháp luật trừng phạt. Họ có thể đã trốn thoát."
    )
    assert passed is True
    assert "Không phát hiện" in evidence


def test_person_check_fails_when_scan_finds_real_named_individual(monkeypatch):
    monkeypatch.setattr(S, "_run_codex", lambda prompt: _fake_json(
        {"references": [{"text": "Qin Baoqi", "inferred_name": "Qin Baoqi"}]}
    ))
    passed, evidence = S._run_storytelling_person_check("... Qin Baoqi được cho là người sáng lập ...")
    assert passed is False
    assert "Qin Baoqi" in evidence


def test_person_check_fails_closed_on_non_dict_reference_element(monkeypatch):
    monkeypatch.setattr(S, "_run_codex", lambda prompt: _fake_json({"references": ["not a dict"]}))
    with pytest.raises(S.LifecycleError):
        S._run_storytelling_person_check("văn bản bất kỳ")


def test_person_check_rejects_empty_text():
    with pytest.raises(S.LifecycleError):
        S._run_storytelling_person_check("   ")


# =============================================================================
# Miễn trừ nhân vật lịch sử (_independent_historical_figure_exempt) --
# thêm sau khi pilot legacy (task #310) phát hiện rule tuyệt đối cũ chặn
# oan Jonathan Wild/Macnaghten/Maconochie dù không có cá nhân còn sống nào
# bị ảnh hưởng. CHỈ miễn trừ khi CẢ 2 model (codex + agy) độc lập đồng ý.
# =============================================================================

def _scan_and_historical_dispatch(scan_payload: dict, codex_eligible_payload, agy_eligible_payload=None):
    """Trả (fake_codex, fake_agy) -- _run_codex trả `scan_payload` cho lượt
    scan (không có marker "NGƯỜI CẦN XÉT" trong prompt) và
    `codex_eligible_payload` cho lượt xác minh miễn trừ (CÓ marker đó).
    _run_agy CHỈ được gọi cho lượt xác minh miễn trừ (agy không tham gia
    scan ban đầu) -- trả `agy_eligible_payload` (mặc định = codex_eligible_
    payload nếu không truyền riêng)."""
    if agy_eligible_payload is None:
        agy_eligible_payload = codex_eligible_payload

    def fake_codex(prompt):
        if "NGƯỜI CẦN XÉT" in prompt:
            return codex_eligible_payload
        return _fake_json(scan_payload)

    def fake_agy(prompt):
        assert "NGƯỜI CẦN XÉT" in prompt, "agy chỉ nên được gọi cho lượt xác minh miễn trừ, không phải scan"
        return agy_eligible_payload

    return fake_codex, fake_agy


def test_person_check_exempts_when_both_models_confirm_historical_figure(monkeypatch):
    scan = {"references": [{"text": "Jonathan Wild", "inferred_name": "Jonathan Wild"}]}
    eligible = _fake_json({"eligible": True, "identified_name": "Jonathan Wild", "death_year_estimate": "1725", "reasoning": "Đã mất > 50 năm, hồ sơ đã đóng."})
    fake_codex, fake_agy = _scan_and_historical_dispatch(scan, eligible)
    monkeypatch.setattr(S, "_run_codex", fake_codex)
    monkeypatch.setattr(S, "_run_agy", fake_agy)

    passed, evidence = S._run_storytelling_person_check("... Jonathan Wild điều hành mạng lưới tội phạm ...")
    assert passed is True
    assert "Jonathan Wild" in evidence
    assert "miễn trừ" in evidence


def test_person_check_still_blocks_when_only_codex_confirms(monkeypatch):
    scan = {"references": [{"text": "Jonathan Wild", "inferred_name": "Jonathan Wild"}]}
    eligible_codex = _fake_json({"eligible": True})
    eligible_agy = _fake_json({"eligible": False, "reasoning": "Không chắc chắn năm mất."})
    fake_codex, fake_agy = _scan_and_historical_dispatch(scan, eligible_codex, eligible_agy)
    monkeypatch.setattr(S, "_run_codex", fake_codex)
    monkeypatch.setattr(S, "_run_agy", fake_agy)

    passed, evidence = S._run_storytelling_person_check("... Jonathan Wild ...")
    assert passed is False
    assert "Jonathan Wild" in evidence


def test_person_check_still_blocks_when_only_agy_confirms(monkeypatch):
    scan = {"references": [{"text": "Jonathan Wild", "inferred_name": "Jonathan Wild"}]}
    eligible_codex = _fake_json({"eligible": False})
    eligible_agy = _fake_json({"eligible": True})
    fake_codex, fake_agy = _scan_and_historical_dispatch(scan, eligible_codex, eligible_agy)
    monkeypatch.setattr(S, "_run_codex", fake_codex)
    monkeypatch.setattr(S, "_run_agy", fake_agy)

    passed, evidence = S._run_storytelling_person_check("... Jonathan Wild ...")
    assert passed is False


def test_person_check_blocks_when_historical_verification_response_malformed(monkeypatch):
    scan = {"references": [{"text": "Jonathan Wild", "inferred_name": "Jonathan Wild"}]}
    fake_codex, fake_agy = _scan_and_historical_dispatch(scan, "not json {{{")
    monkeypatch.setattr(S, "_run_codex", fake_codex)
    monkeypatch.setattr(S, "_run_agy", fake_agy)

    passed, evidence = S._run_storytelling_person_check("... Jonathan Wild ...")
    assert passed is False


def test_person_check_partial_exemption_still_blocks_overall(monkeypatch):
    """1 người được miễn trừ (lịch sử đã đóng), 1 người khác KHÔNG -- vẫn
    phải chặn toàn bộ (an toàn nhất còn thắng), evidence phải phân biệt rõ
    ai bị chặn vs ai đã miễn trừ."""
    scan = {"references": [
        {"text": "Jonathan Wild", "inferred_name": "Jonathan Wild"},
        {"text": "một nhân chứng ẩn danh còn sống", "inferred_name": None},
    ]}
    eligible_true = _fake_json({"eligible": True, "identified_name": "Jonathan Wild", "death_year_estimate": 1725})
    eligible_false = _fake_json({"eligible": False})

    def _for_ref(prompt):
        # Dispatch theo ĐÚNG cụm ref đang được xét -- ref_text/inferred_name
        # được JSON-encode trước khi nhúng (xem _verify_historical_figure_
        # pass), nên chuỗi JSON-quoted '"Jonathan Wild"' CHỈ xuất hiện trong
        # prompt của ĐÚNG ref đó (ref kia có inferred_name=null -> "null",
        # không chứa chuỗi này) -- không phụ thuộc câu chữ cố định của
        # template (dễ vỡ nếu prompt đổi wording).
        return eligible_true if '"Jonathan Wild"' in prompt else eligible_false

    def fake_codex(prompt):
        if "NGƯỜI CẦN XÉT" in prompt:
            return _for_ref(prompt)
        return _fake_json(scan)

    def fake_agy(prompt):
        return _for_ref(prompt)

    monkeypatch.setattr(S, "_run_codex", fake_codex)
    monkeypatch.setattr(S, "_run_agy", fake_agy)

    passed, evidence = S._run_storytelling_person_check("... Jonathan Wild ... nhân chứng ẩn danh còn sống ...")
    assert passed is False
    # "nhân chứng ẩn danh còn sống" PHẢI ở phần bị CHẶN (không đạt miễn trừ).
    blocked_part, _, exempted_part = evidence.partition("(Đã miễn trừ")
    assert "nhân chứng ẩn danh còn sống" in blocked_part
    assert "nhân chứng ẩn danh còn sống" not in exempted_part
    # "Jonathan Wild" PHẢI ở phần ĐÃ MIỄN TRỪ, không phải phần bị chặn.
    assert "Jonathan Wild" in exempted_part
    assert "Jonathan Wild" not in blocked_part


def test_independent_historical_figure_exempt_short_circuits_without_calling_agy_when_codex_rejects(monkeypatch):
    """Hiệu quả + đúng ngữ nghĩa AND: nếu lượt codex đã False, KHÔNG cần
    gọi agy nữa (kết quả AND đã chắc chắn False)."""
    agy_called = []
    monkeypatch.setattr(S, "_run_codex", lambda prompt: _fake_json({"eligible": False}))
    monkeypatch.setattr(S, "_run_agy", lambda prompt: agy_called.append(prompt) or _fake_json({"eligible": True}))

    result = S._independent_historical_figure_exempt("X", "X", "văn bản bất kỳ")
    assert result is False
    assert agy_called == []


# =============================================================================
# _independent_historical_figure_exempt -- cross-check identity/năm mất
# (vá lỗi BLOCKER round 1 Codex, task #310: trước đó chỉ check eligible=true
# riêng lẻ, không đối chiếu 2 lượt có đang nói tới CÙNG 1 người không).
# =============================================================================

def test_exempt_blocks_when_identified_names_disagree(monkeypatch):
    """2 model đều eligible=true nhưng identified_name KHÁC hẳn nhau (đang
    xác nhận 2 người khác nhau) -- PHẢI fail-closed."""
    codex_resp = _fake_json({"eligible": True, "identified_name": "Jonathan Wild", "death_year_estimate": 1725})
    agy_resp = _fake_json({"eligible": True, "identified_name": "Melville Macnaghten", "death_year_estimate": 1921})
    monkeypatch.setattr(S, "_run_codex", lambda prompt: codex_resp)
    monkeypatch.setattr(S, "_run_agy", lambda prompt: agy_resp)
    assert S._independent_historical_figure_exempt("X", "Jonathan Wild", "văn bản") is False


def test_exempt_blocks_when_death_years_disagree_too_much(monkeypatch):
    """Cùng tên (hoặc đủ giống) nhưng năm mất lệch quá xa (>
    _MAX_DEATH_YEAR_DISAGREEMENT) -- dấu hiệu KHÔNG đủ chắc chắn, dù cả 2
    đều đủ ngưỡng _MIN_DEATH_YEARS_AGO riêng lẻ."""
    codex_resp = _fake_json({"eligible": True, "identified_name": "Jonathan Wild", "death_year_estimate": 1725})
    agy_resp = _fake_json({"eligible": True, "identified_name": "Jonathan Wild", "death_year_estimate": 1900})
    monkeypatch.setattr(S, "_run_codex", lambda prompt: codex_resp)
    monkeypatch.setattr(S, "_run_agy", lambda prompt: agy_resp)
    assert S._independent_historical_figure_exempt("X", "Jonathan Wild", "văn bản") is False


def test_exempt_blocks_when_death_year_below_threshold(monkeypatch):
    """Cả 2 đồng ý tên + năm, nhưng chưa đủ _MIN_DEATH_YEARS_AGO (mất gần
    đây) -- PHẢI fail-closed dù mọi thứ khác nhất quán."""
    current_year = S.datetime.datetime.now(S.datetime.timezone.utc).year
    recent_year = current_year - 10
    resp = _fake_json({"eligible": True, "identified_name": "X", "death_year_estimate": recent_year})
    monkeypatch.setattr(S, "_run_codex", lambda prompt: resp)
    monkeypatch.setattr(S, "_run_agy", lambda prompt: resp)
    assert S._independent_historical_figure_exempt("X", "X", "văn bản") is False


def test_exempt_blocks_when_death_year_is_vague_string(monkeypatch):
    """death_year_estimate dạng mô tả mơ hồ ("khoảng 1725"/"thế kỷ 18") --
    KHÔNG parse được như số nguyên thuần -- PHẢI fail-closed (prompt yêu
    cầu số nguyên thuần, nhưng model có thể không tuân theo)."""
    resp = _fake_json({"eligible": True, "identified_name": "Jonathan Wild", "death_year_estimate": "khoảng 1725"})
    monkeypatch.setattr(S, "_run_codex", lambda prompt: resp)
    monkeypatch.setattr(S, "_run_agy", lambda prompt: resp)
    assert S._independent_historical_figure_exempt("X", "Jonathan Wild", "văn bản") is False


def test_exempt_passes_with_consistent_name_and_year(monkeypatch):
    """Trường hợp hợp lệ thật: cả 2 model đồng ý tên (gần giống, không cần
    y hệt tuyệt đối) + năm mất hợp lệ, đủ ngưỡng, không lệch nhau quá xa --
    VÀ khớp với inferred_name gốc từ lượt scan (subject-binding)."""
    codex_resp = _fake_json({"eligible": True, "identified_name": "Jonathan Wild", "death_year_estimate": 1725})
    agy_resp = _fake_json({"eligible": True, "identified_name": "Sir Jonathan Wild", "death_year_estimate": 1725})
    monkeypatch.setattr(S, "_run_codex", lambda prompt: codex_resp)
    monkeypatch.setattr(S, "_run_agy", lambda prompt: agy_resp)
    assert S._independent_historical_figure_exempt("X", "Jonathan Wild", "văn bản") is True


def test_exempt_blocks_when_inferred_name_is_none(monkeypatch):
    """Lượt scan gốc nhận diện được 1 người cụ thể nhưng KHÔNG suy ra được
    tên (inferred_name=None) -- KHÔNG có gì để ràng buộc chủ thể, PHẢI
    fail-closed TUYỆT ĐỐI, không gọi codex/agy (không có gì đáng kiểm tra)."""
    called = []
    monkeypatch.setattr(S, "_run_codex", lambda prompt: called.append(1) or _fake_json({"eligible": True}))
    monkeypatch.setattr(S, "_run_agy", lambda prompt: called.append(1) or _fake_json({"eligible": True}))
    assert S._independent_historical_figure_exempt("chức vụ + thời gian cụ thể", None, "văn bản") is False
    assert called == []


def test_exempt_blocks_when_both_models_agree_on_wrong_person(monkeypatch):
    """Vá lỗi BLOCKER round 2 Codex: 2 model ĐỒNG Ý VỚI NHAU (y hệt tên +
    năm) nhưng CẢ 2 cùng xác nhận SAI người -- khác hẳn inferred_name mà
    lượt scan gốc đã suy ra (mô phỏng injection/nhiễu hệ thống khiến cả 2
    model "trôi" sang xác nhận nhầm 1 nhân vật lịch sử an toàn khác, dù
    reference thật đang nói về người khác). PHẢI fail-closed dù r1 và r2
    khớp nhau hoàn hảo -- (b) cũ (chỉ so r1 với r2) sẽ SAI cho qua case
    này; subject-binding mới (so với inferred_name) phải bắt được."""
    resp = _fake_json({"eligible": True, "identified_name": "Jonathan Wild", "death_year_estimate": 1725})
    monkeypatch.setattr(S, "_run_codex", lambda prompt: resp)
    monkeypatch.setattr(S, "_run_agy", lambda prompt: resp)
    # inferred_name gốc (từ lượt scan ĐỘC LẬP) nói về 1 người HOÀN TOÀN khác.
    assert S._independent_historical_figure_exempt("người dẫn chương trình hiện tại", "Elon Musk", "văn bản") is False


# =============================================================================
# _names_match -- vá lỗi BLOCKER round 3 Codex: bản substring/2-token-chung
# cũ quá lỏng cho 1 cổng miễn trừ an toàn (tên 1 phần/mơ hồ khớp bậy được).
# =============================================================================

def test_names_match_rejects_single_ambiguous_token():
    """Tên 1 từ (vd chỉ tên riêng, không họ) KHÔNG BAO GIỜ đủ để xác định
    duy nhất 1 người -- PHẢI fail-closed dù nó là substring của tên kia."""
    assert S._names_match("John", "John Wayne Gacy") is False
    assert S._names_match("Alexander", "Alexander Maconochie") is False


def test_names_match_rejects_identical_single_token_name(monkeypatch=None):
    """Vá lỗi BLOCKER round 4 Codex: bản round-3 cho "John"=="john" (equality
    chạy TRƯỚC check độ dài) -- 2 tên GIỐNG HỆT NHAU nhưng chỉ 1 token vẫn
    PHẢI fail-closed (quá mơ hồ để xác định duy nhất 1 người, bất kể có
    khớp ký tự hay không)."""
    assert S._names_match("John", "John") is False
    assert S._names_match("John", "John (unknown)") is False


def test_names_match_rejects_partial_surname_collision():
    """2 tên đầy đủ trùng token đầu (họ/tên đệm) nhưng khác token còn lại
    -- 2 NGƯỜI KHÁC NHAU, không được coi là khớp chỉ vì 1 từ chung."""
    assert S._names_match("John Smith", "John Smithson") is False


def test_names_match_rejects_two_full_names_sharing_two_tokens_but_differing():
    """2 tên đủ 2 từ chung (đạt ngưỡng cũ) nhưng KHÁC token quyết định danh
    tính -- vẫn phải fail (bản cũ dùng "giao 2 token >=3 ký tự" sẽ SAI cho
    qua case này)."""
    assert S._names_match("John Smith Anderson", "John Smith Roberts") is False


def test_names_match_rejects_extra_disambiguating_token():
    """Vá lỗi BLOCKER round 4 Codex: full-token-containment round-3 cho
    "John Smith" khớp bậy "John Michael Smith"/"John Wayne Smith" -- token
    dư (tên đệm) CÓ THỂ phân biệt 2 người khác nhau, KHÔNG được coi là vô
    hại. Giờ yêu cầu tập token CỐT LÕI bằng nhau TUYỆT ĐỐI, không phải tập
    con -- token dư ở bên nào cũng làm mismatch."""
    assert S._names_match("John Smith", "John Michael Smith") is False
    assert S._names_match("John Smith", "John Wayne Smith") is False


def test_names_match_rejects_bracketed_disambiguating_suffix():
    """Vá lỗi BLOCKER round 4 Codex: bản round-3 xoá TOÀN BỘ nội dung
    trong ngoặc coi như luôn vô hại -- nhưng "Sr."/"Jr." (hoặc số hiệu La
    Mã/biệt danh riêng) trong ngoặc CÓ THỂ chính là thứ phân biệt 2 người
    khác nhau (cha/con cùng tên). Giờ chỉ lọc 1 allowlist HẸP honorific
    chung chung (Sir/Dr/Lord...), KHÔNG lọc hậu tố phân biệt danh tính."""
    assert S._names_match("John Smith (Sr.)", "John Smith (Jr.)") is False
    assert S._names_match("(John)", "(Smith)") is False


def test_names_match_accepts_exact_normalized_equal():
    assert S._names_match("Jonathan Wild", "jonathan   wild") is True


def test_names_match_accepts_generic_honorific_prefix():
    """1 bên thêm 1 DANH XƯNG CHUNG CHUNG (Sir/Dr/Lord... -- nằm trong
    allowlist hẹp _HONORIFIC_TOKENS, không bao giờ tự nó phân biệt được 2
    người) -- CÙNG 1 người, phải khớp."""
    assert S._names_match("Jonathan Wild", "Sir Jonathan Wild") is True


def test_names_match_accepts_token_order_difference():
    """So khớp KHÔNG phân biệt thứ tự token -- có chủ đích, chịu được khác
    biệt trật tự tên giữa các ngôn ngữ/quy ước."""
    assert S._names_match("Wild Jonathan", "Jonathan Wild") is True


def test_exempt_blocks_when_eligible_is_truthy_non_bool(monkeypatch):
    """eligible="true" (chuỗi) hay eligible=1 KHÔNG được coi là True tường
    minh -- chỉ đúng kiểu bool True mới hợp lệ (vá lỗi kiểu dữ liệu lỏng lẻo
    có thể bị lợi dụng)."""
    resp = _fake_json({"eligible": "true", "identified_name": "X", "death_year_estimate": 1000})
    monkeypatch.setattr(S, "_run_codex", lambda prompt: resp)
    monkeypatch.setattr(S, "_run_agy", lambda prompt: resp)
    assert S._independent_historical_figure_exempt("X", "X", "văn bản") is False


# =============================================================================
# _verify_ledger_combined -- lượt ledger THỨ 2 trên combined text (script+
# SEO), vá lỗi BLOCKER round 1 Codex: SEO sinh SAU lượt ledger đầu tiên nên
# có thể tự thêm claim rủi ro cao chưa từng qua ledger.
# =============================================================================

def test_combined_ledger_check_blocks_claim_introduced_only_by_seo(monkeypatch):
    """Script-only ledger PASS, nhưng SEO tự thêm 1 câu chứa claim rủi ro
    cao KHÔNG có trong script -- lượt ledger thứ 2 (combined) PHẢI bắt được
    và chặn, dù lượt đầu đã PASS."""
    monkeypatch.setattr(S, "_score_c4_adversarial_text", lambda text, candidate: _c4_result(True))

    def fake_ledger(topic_id, text):
        if "allegation-trong-SEO" in text:
            return False, "BLOCKED_FACT: claim chỉ xuất hiện trong SEO.", [], ["SEO_CLAIM"]
        return True, "ok", ["SCRIPT_CLAIM"], []

    monkeypatch.setattr(S.cl_claim_ledger, "verify_high_risk_claims_with_refs", fake_ledger)
    monkeypatch.setattr(S, "generate_cl_seo", lambda script: {
        "passed": True,
        "seo": {"title": "allegation-trong-SEO", "description": "d", "tags": ["a"], "thumbnail_brief": "b"},
        "iterations_used": 1,
    })
    result = S.compute_phase_a_result("EP1", "Tiêu đề", "Đoạn trích nguồn.", "Kịch bản.", claim_ledger_topic_id="SOME_TOPIC")
    assert result.passed is False
    assert result.reason_code == "STORYTELLING_BLOCKED_FACT"
    assert result.fact_verification["blocked_claim_ids"] == ["SEO_CLAIM"]


def test_combined_ledger_check_merges_verified_ids_from_both_passes(monkeypatch):
    """Khi CẢ 2 lượt (script-only + combined) đều PASS, verified_claim_ids
    trong sidecar cuối PHẢI gộp đủ ID từ CẢ 2 lượt (không chỉ giữ lượt cuối)."""
    monkeypatch.setattr(S, "_score_c4_adversarial_text", lambda text, candidate: _c4_result(True))
    _pass_person_check(monkeypatch)

    call_count = {"n": 0}

    def fake_ledger(topic_id, text):
        call_count["n"] += 1
        if call_count["n"] == 1:
            return True, "ok", ["SCRIPT_CLAIM"], []
        return True, "ok", ["SCRIPT_CLAIM", "SEO_CLAIM"], []

    monkeypatch.setattr(S.cl_claim_ledger, "verify_high_risk_claims_with_refs", fake_ledger)
    _pass_seo(monkeypatch)
    result = S.compute_phase_a_result("EP1", "Tiêu đề", "Đoạn trích nguồn.", "Kịch bản.", claim_ledger_topic_id="SOME_TOPIC")
    assert result.passed is True
    assert call_count["n"] == 2
    assert set(result.fact_verification["verified_claim_ids"]) == {"SCRIPT_CLAIM", "SEO_CLAIM"}


# =============================================================================
# compute_phase_a_result -- C4 retry-once + orchestration
# =============================================================================

def _pass_seo(monkeypatch):
    monkeypatch.setattr(S, "generate_cl_seo", lambda script: {
        "passed": True, "seo": {"title": "t", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}, "iterations_used": 1,
    })


def _pass_person_check(monkeypatch):
    monkeypatch.setattr(S, "_run_storytelling_person_check", lambda text: (True, "ok"))


def _c4_result(passed, evidence="e"):
    return type("R", (), {"passed": passed, "evidence": evidence})()


def test_c4_single_call_pass(monkeypatch):
    """C4 repair round 3: đã bỏ đa số 2/3 -- đo 2 lần độc lập (round 2 +
    round 3) trên golden corpus xác nhận đa số không giảm false-block so
    với 1 lượt duy nhất, chỉ tốn thêm lượt gọi. Giờ chỉ gọi C4 ĐÚNG 1 lần."""
    calls = {"n": 0}

    def fake_c4(text, candidate):
        calls["n"] += 1
        return _c4_result(True)

    monkeypatch.setattr(S, "_score_c4_adversarial_text", fake_c4)
    _pass_seo(monkeypatch)
    _pass_person_check(monkeypatch)

    result = S.compute_phase_a_result("EP1", "Tiêu đề", "Đoạn trích nguồn.", "Kịch bản.")
    assert result.passed is True
    assert calls["n"] == 1


def test_c4_single_call_fail_closed(monkeypatch):
    """1 lượt FAIL duy nhất -> fail-closed ngay, không có cơ chế 'thử lại
    để lật ngược' (gánh nặng chứng minh không đặt ở phía retry)."""
    calls = {"n": 0}

    def fake_c4(text, candidate):
        calls["n"] += 1
        return _c4_result(False, "câu bị chặn thiếu căn cứ")

    monkeypatch.setattr(S, "_score_c4_adversarial_text", fake_c4)
    result = S.compute_phase_a_result("EP1", "Tiêu đề", "Đoạn trích nguồn.", "Kịch bản.")
    assert result.passed is False
    assert result.reason_code == "STORYTELLING_C4_FAILED"
    assert calls["n"] == 1


def test_seo_failure_blocks_before_person_check(monkeypatch):
    monkeypatch.setattr(S, "_score_c4_adversarial_text", lambda text, candidate: _c4_result(True))
    monkeypatch.setattr(S, "generate_cl_seo", lambda script: {"passed": False, "iterations_used": 3})
    result = S.compute_phase_a_result("EP1", "Tiêu đề", "Đoạn trích nguồn.", "Kịch bản.")
    assert result.passed is False
    assert result.reason_code == "STORYTELLING_SEO_FAILED"


def test_person_reference_failure_blocks_final_pass(monkeypatch):
    monkeypatch.setattr(S, "_score_c4_adversarial_text", lambda text, candidate: _c4_result(True))
    _pass_seo(monkeypatch)
    monkeypatch.setattr(S, "_run_storytelling_person_check", lambda text: (False, "Qin Baoqi"))
    result = S.compute_phase_a_result("EP1", "Tiêu đề", "Đoạn trích nguồn.", "Kịch bản.")
    assert result.passed is False
    assert result.reason_code == "STORYTELLING_UNVETTED_PERSON_REFERENCE"


def test_full_pass_computes_hashes(monkeypatch):
    monkeypatch.setattr(S, "_score_c4_adversarial_text", lambda text, candidate: _c4_result(True))
    _pass_seo(monkeypatch)
    _pass_person_check(monkeypatch)
    result = S.compute_phase_a_result("EP1", "Tiêu đề", "Đoạn trích nguồn.", "Kịch bản.")
    assert result.passed is True
    assert result.reviewed_editorial_hash
    assert result.reviewed_script_hash


def test_unexpected_exception_fails_closed(monkeypatch):
    def boom(text, candidate):
        raise RuntimeError("lỗi bất ngờ")
    monkeypatch.setattr(S, "_score_c4_adversarial_text", boom)
    result = S.compute_phase_a_result("EP1", "Tiêu đề", "Đoạn trích nguồn.", "Kịch bản.")
    assert result.passed is False
    assert result.reason_code == "STORYTELLING_PHASE_A_UNEXPECTED_ERROR"


# =============================================================================
# write_storytelling_sidecar
# =============================================================================

def test_write_sidecar_rejects_failed_result():
    result = S.StorytellingPhaseAResult(False, "SOME_CODE", "evidence")
    with pytest.raises(ValueError):
        S.write_storytelling_sidecar("EP1", result)


def test_c4_pass_default_topic_id_none_skips_claim_ledger(monkeypatch):
    """PART M (tương thích ngược): claim_ledger_topic_id mặc định None --
    MỌI call site cũ (chưa biết khái niệm topic_id) phải chạy y hệt hành vi
    trước khi vá lỗi này, KHÔNG bị chặn bởi bước ledger mới dù không có
    entry ledger nào tồn tại cho nội dung đó."""
    monkeypatch.setattr(S, "_score_c4_adversarial_text", lambda text, candidate: _c4_result(True))
    _pass_seo(monkeypatch)
    _pass_person_check(monkeypatch)
    # Cố ý KHÔNG monkeypatch cl_claim_ledger -- nếu bước ledger lỡ chạy dù
    # topic_id=None, nó sẽ gọi codex thật/raise lỗi thật và test này FAIL,
    # chứng minh đúng tính "bỏ qua hoàn toàn" khi topic_id=None.
    result = S.compute_phase_a_result("EP1", "Tiêu đề", "Đoạn trích nguồn.", "Kịch bản.")
    assert result.passed is True


def test_claim_ledger_blocks_when_topic_id_given_and_claim_unverified(monkeypatch):
    monkeypatch.setattr(S, "_score_c4_adversarial_text", lambda text, candidate: _c4_result(True))
    monkeypatch.setattr(S.cl_claim_ledger, "verify_high_risk_claims_with_refs", lambda topic_id, text: (False, "BLOCKED_FACT: claim rủi ro cao chưa xác minh.", [], ["C1"]))
    result = S.compute_phase_a_result("EP1", "Tiêu đề", "Đoạn trích nguồn.", "Kịch bản.", claim_ledger_topic_id="SOME_TOPIC")
    assert result.passed is False
    assert result.reason_code == "STORYTELLING_BLOCKED_FACT"
    assert "BLOCKED_FACT" in result.evidence
    assert result.fact_verification["state"] == "BLOCKED_FACT"
    assert result.fact_verification["topic_id"] == "SOME_TOPIC"
    assert result.fact_verification["blocked_claim_ids"] == ["C1"]


def test_claim_ledger_passes_through_when_topic_id_given_and_claims_ok(monkeypatch):
    monkeypatch.setattr(S, "_score_c4_adversarial_text", lambda text, candidate: _c4_result(True))
    monkeypatch.setattr(S.cl_claim_ledger, "verify_high_risk_claims_with_refs", lambda topic_id, text: (True, "ok", ["GARDNER_SENSOR_RECORDED"], []))
    _pass_seo(monkeypatch)
    _pass_person_check(monkeypatch)
    result = S.compute_phase_a_result("EP1", "Tiêu đề", "Đoạn trích nguồn.", "Kịch bản.", claim_ledger_topic_id="RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3")
    assert result.passed is True
    assert result.fact_verification["state"] == "VERIFIED_CLAIM_LEDGER"
    assert result.fact_verification["topic_id"] == "RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3"
    assert result.fact_verification["verified_claim_ids"] == ["GARDNER_SENSOR_RECORDED"]
    assert result.fact_verification["ledger_version"]
    assert result.fact_verification["checked_at"]


def test_claim_ledger_error_fails_closed(monkeypatch):
    def boom(topic_id, text):
        raise S.LifecycleError("lỗi ledger giả lập")
    monkeypatch.setattr(S, "_score_c4_adversarial_text", lambda text, candidate: _c4_result(True))
    monkeypatch.setattr(S.cl_claim_ledger, "verify_high_risk_claims_with_refs", boom)
    result = S.compute_phase_a_result("EP1", "Tiêu đề", "Đoạn trích nguồn.", "Kịch bản.", claim_ledger_topic_id="SOME_TOPIC")
    assert result.passed is False
    assert result.reason_code == "STORYTELLING_CLAIM_LEDGER_ERROR"


def test_legacy_pass_marks_fact_verification_legacy_unverified(monkeypatch):
    """PART 10/11 (legacy regression + sidecar regression): claim_ledger_
    topic_id=None (mọi call site cũ) -- PASS vẫn xảy ra (tương thích ngược),
    nhưng fact_verification.state PHẢI là LEGACY_UNVERIFIED, KHÔNG BAO GIỜ
    im lặng thành VERIFIED_CLAIM_LEDGER chỉ vì thiếu field."""
    monkeypatch.setattr(S, "_score_c4_adversarial_text", lambda text, candidate: _c4_result(True))
    _pass_seo(monkeypatch)
    _pass_person_check(monkeypatch)
    result = S.compute_phase_a_result("EP1", "Tiêu đề", "Đoạn trích nguồn.", "Kịch bản.")
    assert result.passed is True
    assert result.fact_verification["state"] == "LEGACY_UNVERIFIED"
    assert result.fact_verification["topic_id"] is None


def test_sidecar_persists_fact_verification_for_verified_episode(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "cl_metadata_sidecar_path", lambda episode, topic: tmp_path / f"{episode}.cl_meta.json")
    result = S.StorytellingPhaseAResult(
        True, None, "ok", final_editorial={"title": "t", "description": "d", "tags": [], "thumbnail_brief": "b"},
        reviewed_editorial_hash="h1", reviewed_script_hash="h2",
        fact_verification={
            "state": "VERIFIED_CLAIM_LEDGER", "topic_id": "RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3",
            "ledger_version": "abc123", "verified_claim_ids": ["GARDNER_SENSOR_RECORDED"], "blocked_claim_ids": [],
            "checked_at": "2026-08-24T00:00:00+00:00",
        },
    )
    path = S.write_storytelling_sidecar("EP1", result)
    sidecar = json.loads(path.read_text(encoding="utf-8"))
    assert sidecar["fact_verification"]["state"] == "VERIFIED_CLAIM_LEDGER"
    assert sidecar["fact_verification"]["topic_id"] == "RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3"
    assert sidecar["fact_verification"]["verified_claim_ids"] == ["GARDNER_SENSOR_RECORDED"]


def test_sidecar_persists_fact_verification_for_legacy_episode(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "cl_metadata_sidecar_path", lambda episode, topic: tmp_path / f"{episode}.cl_meta.json")
    result = S.StorytellingPhaseAResult(
        True, None, "ok", final_editorial={"title": "t", "description": "d", "tags": [], "thumbnail_brief": "b"},
        reviewed_editorial_hash="h1", reviewed_script_hash="h2",
        fact_verification={
            "state": "LEGACY_UNVERIFIED", "topic_id": None, "ledger_version": None,
            "verified_claim_ids": [], "blocked_claim_ids": [], "checked_at": "2026-08-24T00:00:00+00:00",
        },
    )
    path = S.write_storytelling_sidecar("EP1", result)
    sidecar = json.loads(path.read_text(encoding="utf-8"))
    assert sidecar["fact_verification"]["state"] == "LEGACY_UNVERIFIED"


def test_write_sidecar_writes_expected_structure(tmp_path, monkeypatch):
    monkeypatch.setattr(S, "cl_metadata_sidecar_path", lambda episode, topic: tmp_path / f"{episode}.cl_meta.json")
    result = S.StorytellingPhaseAResult(
        True, None, "ok", final_editorial={"title": "t", "description": "d", "tags": [], "thumbnail_brief": "b"},
        reviewed_editorial_hash="h1", reviewed_script_hash="h2",
    )
    path = S.write_storytelling_sidecar("EP1", result)
    sidecar = json.loads(path.read_text(encoding="utf-8"))
    assert sidecar["named_individuals"] == []
    assert sidecar["phase_a_variant"] == "storytelling_v1"
    assert sidecar["reviewed_editorial_hash"] == "h1"
    assert sidecar["reviewed_script_hash"] == "h2"


# =============================================================================
# compute_phase_a_result_provenance (C4 Round 6 -- storytelling_provenance_v1)
# =============================================================================

def _fake_pack(topic_id="T1"):
    from cl_story_fact_pack import StoryFact, StoryFactPack
    return StoryFactPack(topic_id=topic_id, source_file=f"{topic_id}.md", excerpt_hash="h", ledger_version_at_build="v1",
                          facts=[StoryFact(fact_id="F001", proposition="A xảy ra.", source_spans=["A xảy ra"])])


def _fake_plan(pack):
    from cl_story_plan_and_generation import StoryPlan, PlanSegment
    return StoryPlan(topic_id=pack.topic_id, fact_pack_hash=pack.pack_hash(), segments=[PlanSegment("S1", "HOOK", ["F001"])])


def _wire_provenance_pass(monkeypatch, ledger_passed=True):
    pack = _fake_pack()
    plan = _fake_plan(pack)
    bindings = [{"segment_id": "S1", "fact_ids": ["F001"], "prose": "A đã xảy ra.", "pack_hash_at_generation": pack.pack_hash()}]
    monkeypatch.setattr(S.cl_story_fact_pack, "get_or_build_fact_pack", lambda *a: pack)
    monkeypatch.setattr(S.spg, "build_story_plan", lambda p: plan)
    monkeypatch.setattr(S.spg, "generate_bound_script", lambda p, pk: ("A đã xảy ra.", bindings))
    monkeypatch.setattr(S.spg, "run_deterministic_guards", lambda b, pk: [])
    from cl_story_plan_and_generation import DriftResult
    monkeypatch.setattr(S.spg, "run_drift_detector", lambda b, pk: [DriftResult("S1", True, "ok")])
    monkeypatch.setattr(S.cl_claim_ledger, "verify_high_risk_claims_with_refs", lambda topic_id, text: (ledger_passed, "ok" if ledger_passed else "blocked", [], []))
    monkeypatch.setattr(S.cl_claim_ledger, "ledger_version", lambda: "v_test")
    _pass_seo(monkeypatch)
    _pass_person_check(monkeypatch)
    return pack, plan, bindings


def test_provenance_full_pass_returns_tuple_with_artifacts(monkeypatch):
    pack, plan, bindings = _wire_provenance_pass(monkeypatch)
    result, script_text, ret_plan, ret_bindings = S.compute_phase_a_result_provenance("EP1", "T1", "T1.md", "excerpt")
    assert result.passed
    assert result.phase_a_variant == "storytelling_provenance_v1"
    assert result.provenance_state["provenance_pass"] is True
    assert result.fact_verification["state"] == "VERIFIED_CLAIM_LEDGER"
    assert script_text == "A đã xảy ra."
    assert ret_plan is plan
    assert ret_bindings is bindings


def test_provenance_drift_failure_blocks_before_ledger_check(monkeypatch):
    pack = _fake_pack()
    plan = _fake_plan(pack)
    bindings = [{"segment_id": "S1", "fact_ids": ["F001"], "prose": "A đã xảy ra, bịa thêm B.", "pack_hash_at_generation": pack.pack_hash()}]
    monkeypatch.setattr(S.cl_story_fact_pack, "get_or_build_fact_pack", lambda *a: pack)
    monkeypatch.setattr(S.spg, "build_story_plan", lambda p: plan)
    monkeypatch.setattr(S.spg, "generate_bound_script", lambda p, pk: ("A đã xảy ra, bịa thêm B.", bindings))
    monkeypatch.setattr(S.spg, "run_deterministic_guards", lambda b, pk: [])
    from cl_story_plan_and_generation import DriftResult
    monkeypatch.setattr(S.spg, "run_drift_detector", lambda b, pk: [DriftResult("S1", False, "UNSUPPORTED: bịa thêm B")])
    ledger_calls = []
    monkeypatch.setattr(S.cl_claim_ledger, "verify_high_risk_claims_with_refs", lambda *a: ledger_calls.append(1))
    result, script_text, ret_plan, ret_bindings = S.compute_phase_a_result_provenance("EP2", "T1", "T1.md", "excerpt")
    assert not result.passed
    assert result.reason_code == "STORYTELLING_PROVENANCE_FAILED"
    assert result.provenance_state["provenance_pass"] is False
    assert script_text is None and ret_plan is None and ret_bindings is None
    assert not ledger_calls  # claim-ledger KHÔNG được gọi khi provenance đã fail (tránh tốn LLM call vô ích)


def test_provenance_pass_but_ledger_blocked_fact(monkeypatch):
    """provenance_pass=True (văn xuôi trung thành với fact đã chọn) NHƯNG
    fact rủi ro cao chưa xác minh ngoài -- publish_ready THẬT (do consumer
    tính qua validate_fact_verification_binding) phải là False, KHÔNG
    được tự ý coi provenance_pass=True là đủ để publish."""
    pack, plan, bindings = _wire_provenance_pass(monkeypatch, ledger_passed=False)
    result, script_text, ret_plan, ret_bindings = S.compute_phase_a_result_provenance("EP3", "T1", "T1.md", "excerpt")
    assert not result.passed
    assert result.reason_code == "STORYTELLING_BLOCKED_FACT"
    assert result.provenance_state["provenance_pass"] is True  # provenance ĐÚNG, chỉ chưa verify ngoài
    assert result.fact_verification["state"] == "BLOCKED_FACT"


def test_provenance_stale_fact_pack_hash_bubbles_up_as_unexpected_error(monkeypatch):
    """generate_bound_script() raise ValueError khi plan.fact_pack_hash
    không khớp pack hiện tại (cross-topic plan attack / stale pack) --
    compute_phase_a_result_provenance() PHẢI bắt được, fail-closed, không
    để exception thoát ra ngoài làm crash cả batch."""
    pack = _fake_pack()

    def raise_stale(p, pk):
        raise ValueError("Story plan fact_pack_hash không khớp pack hiện tại")

    monkeypatch.setattr(S.cl_story_fact_pack, "get_or_build_fact_pack", lambda *a: pack)
    monkeypatch.setattr(S.spg, "build_story_plan", lambda p: _fake_plan(pack))
    monkeypatch.setattr(S.spg, "generate_bound_script", raise_stale)
    result, script_text, ret_plan, ret_bindings = S.compute_phase_a_result_provenance("EP4", "T1", "T1.md", "excerpt")
    assert not result.passed
    assert result.reason_code == "STORYTELLING_PHASE_A_UNEXPECTED_ERROR"
    assert script_text is None


def test_write_provenance_sidecars_writes_txt_plan_and_binding(tmp_path, monkeypatch):
    import short_segment_discovery as sd
    monkeypatch.setattr(sd, "_shorts_source_dir", lambda topic: tmp_path)
    monkeypatch.setattr(S, "cl_story_plan_sidecar_path", lambda ep, topic: tmp_path / f"{ep}.story_plan.json")
    monkeypatch.setattr(S, "cl_script_binding_sidecar_path", lambda ep, topic: tmp_path / f"{ep}.script_binding.json")
    pack, plan, bindings = _wire_provenance_pass(monkeypatch)
    result, script_text, ret_plan, ret_bindings = S.compute_phase_a_result_provenance("EP5", "T1", "T1.md", "excerpt")
    assert result.passed
    txt_path, plan_path, binding_path = S.write_provenance_sidecars("EP5", result, script_text, ret_plan, ret_bindings)
    assert txt_path.read_text(encoding="utf-8") == script_text
    plan_json = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan_json["fact_pack_hash"] == plan.fact_pack_hash
    binding_json = json.loads(binding_path.read_text(encoding="utf-8"))
    assert binding_json["bindings"] == bindings
