"""Test cho cl_claim_ledger.py -- vá lỗi kiến trúc "excerpt-as-ground-truth"
(PART L của yêu cầu vá lỗi, xem docstring cl_claim_ledger.py). Monkeypatch
module attribute (classify_high_risk_claims/load_claim_ledger/load_source_
tiers), đúng quy ước đã dùng ở test_criminal_law_storytelling_phase_a.py."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import cl_claim_ledger as L  # noqa: E402
import cl_risk_gate as g  # noqa: E402
from cl_risk_gate_lifecycle import LifecycleError  # noqa: E402


def _claims(*items):
    """items: list[(text, risk_class)] -> đúng format classify_high_risk_claims() trả về."""
    return [{"text": t, "risk_class": r} for t, r in items]


# =============================================================================
# Helper cho kiến trúc 2-LƯỢT-TRÍCH-ĐỘC-LẬP (round 2 review đối kháng Codex
# CLI, BLOCKER): classify_high_risk_claims() giờ gọi CẢ _run_codex VÀ
# _run_agy, mỗi model có thể được gọi để (a) trích claim thô ("lượt trích")
# HOẶC (b) xác minh subject/materiality độc lập cho claim của model KIA
# ("lượt xác minh"). Dispatch theo nội dung prompt (3 marker duy nhất,
# khớp đúng 3 prompt trong cl_claim_ledger.py).
# =============================================================================
_EXTRACTION_MARKER = "Trích MỌI khẳng định thực tế"
_SUBJECT_MARKER = "NGƯỜI THẬT, CỤ THỂ, có thể nhận diện được không"
_MATERIAL_MARKER = "TRỌNG TÂM của câu chuyện không"


def _dispatch_by_marker(routes):
    """routes: list[(marker_substring, handler)], handler(prompt) -> str thô
    (hoặc raise). Trả 1 function(prompt) khớp marker ĐẦU TIÊN xuất hiện
    trong prompt; raise AssertionError nếu prompt không khớp route nào đã
    khai -- buộc mỗi test khai RÕ mọi tình huống model có thể bị gọi tới,
    không để sót 1 nhánh nào âm thầm rơi vào hành vi mặc định sai."""
    def _fn(prompt):
        for marker, handler in routes:
            if marker in prompt:
                return handler(prompt)
        raise AssertionError(f"Prompt không khớp route nào đã khai trong test: {prompt[:150]!r}")
    return _fn


def _extraction_route(claims):
    import json
    return (_EXTRACTION_MARKER, lambda p: json.dumps({"claims": claims}))


def _subject_route(verdict=None, exc=None, raw=None):
    import json
    def _handler(p):
        if exc is not None:
            raise exc
        if raw is not None:
            return raw
        return json.dumps({"subject_is_named_real_person": verdict})
    return (_SUBJECT_MARKER, _handler)


def _material_route(verdict=None, exc=None, raw=None):
    import json
    def _handler(p):
        if exc is not None:
            raise exc
        if raw is not None:
            return raw
        return json.dumps({"material": verdict})
    return (_MATERIAL_MARKER, _handler)


# =============================================================================
# PART L.1 -- input/excerpt-only claim KHÔNG thể thành VERIFIED
# =============================================================================

def test_high_risk_claim_with_no_ledger_entry_is_blocked(monkeypatch):
    """Claim rủi ro cao không khớp entry ledger nào -> BLOCKED_FACT, dù
    "nghe hợp lý" tới đâu -- đúng bất biến GATE 0A: INPUT IS NOT EVIDENCE."""
    monkeypatch.setattr(L, "classify_high_risk_claims", lambda text: _claims(("Nghi phạm hành động vì thù hằn cá nhân.", "motive")))
    monkeypatch.setattr(L, "load_claim_ledger", lambda: {})  # topic chưa từng được populate
    passed, evidence = L.verify_high_risk_claims("TOPIC_KHONG_TON_TAI", "văn bản bất kỳ")
    assert passed is False
    assert "BLOCKED_FACT" in evidence
    assert "KHÔNG có entry ledger khớp" in evidence


def test_ordinary_claim_only_passes_without_ledger_lookup(monkeypatch):
    """Claim risk_class=ordinary bị lọc NGAY tại classify_high_risk_claims
    (không lọt vào danh sách cần verify) -- văn bản không có claim rủi ro
    cao nào thì PASS free, không cần ledger/nguồn ngoài gì."""
    monkeypatch.setattr(L, "classify_high_risk_claims", lambda text: [])
    passed, evidence = L.verify_high_risk_claims("BAT_KY_TOPIC", "văn bản mô tả chung chung")
    assert passed is True
    assert "Không có claim thuộc nhóm rủi ro cao" in evidence


# =============================================================================
# PART L.2 -- P2-only (aggregator) KHÔNG đủ cho claim rủi ro cao
# =============================================================================

def test_p2_aggregator_only_source_cannot_verify_high_risk_claim(monkeypatch):
    monkeypatch.setattr(L, "classify_high_risk_claims", lambda text: _claims(("X dùng cảm biến để né bị phát hiện.", "security_system")))
    monkeypatch.setattr(L, "load_claim_ledger", lambda: {
        "TOPIC_A": [{
            "claim_id": "C1", "normalized_claim": "x dùng cảm biến để né bị phát hiện",
            "status": "VERIFIED", "risk_class": "security_system",
            "provenance": [{"source_url": "https://en.wikipedia.org/wiki/X"}],  # aggregator == P2
        }],
    })
    passed, evidence = L.verify_high_risk_claims("TOPIC_A", "văn bản")
    assert passed is False
    assert "tier=aggregator" in evidence


# =============================================================================
# PART L.3 -- P0-backed claim CÓ THỂ thành VERIFIED
# =============================================================================

def test_p0_backed_verified_claim_passes(monkeypatch):
    monkeypatch.setattr(L, "classify_high_risk_claims", lambda text: _claims(("Y bị bắt ngày X.", "legal_status")))
    monkeypatch.setattr(L, "load_claim_ledger", lambda: {
        "TOPIC_B": [{
            "claim_id": "C2", "normalized_claim": "y bị bắt ngày x",
            "status": "VERIFIED", "risk_class": "legal_status",
            "provenance": [{"source_url": "https://www.fbi.gov/some-case"}],  # public_record == P0
        }],
    })
    passed, evidence = L.verify_high_risk_claims("TOPIC_B", "văn bản")
    assert passed is True
    assert "P0/P1" in evidence


# =============================================================================
# PART L.4 -- nguồn xác thực bác bỏ THẮNG nhiều nguồn yếu lặp lại
# =============================================================================

def test_authoritative_contradiction_beats_claim_even_with_input_repetition(monkeypatch):
    """Claim CONTRADICTED trong ledger vẫn bị chặn dù script "khẳng định
    chắc nịch" -- input lặp lại bao nhiêu lần cũng không đổi được verdict
    của 1 nguồn P0 đã bác bỏ (SOURCE CONFLICT RULE: authoritative > input)."""
    monkeypatch.setattr(L, "classify_high_risk_claims", lambda text: _claims(
        ("Z chắc chắn đã dùng mật khẩu bị rò rỉ để xâm nhập.", "forensic"),
    ))
    monkeypatch.setattr(L, "load_claim_ledger", lambda: {
        "TOPIC_C": [{
            "claim_id": "C3", "normalized_claim": "z dùng mật khẩu bị rò rỉ để xâm nhập",
            "status": "CONTRADICTED", "risk_class": "forensic",
            "provenance": [{"source_url": "https://www.fbi.gov/some-case"}],
            "evidence_summary": "Hồ sơ chính thức xác nhận Z KHÔNG có quyền truy cập bằng mật khẩu nào.",
        }],
    })
    passed, evidence = L.verify_high_risk_claims("TOPIC_C", "văn bản")
    assert passed is False
    assert "BÁC BỎ" in evidence


# =============================================================================
# PART L.6-8 -- Gardner regression: dùng ĐÚNG ledger/tiers THẬT trên đĩa
# (creator_specs/CL_VERIFIED_CLAIM_LEDGER_v1.json + CL_SOURCE_TIERS_v1.json)
# =============================================================================

def test_gardner_sensor_evasion_claim_is_contradicted(monkeypatch):
    """L.6: claim SAI kế thừa từ excerpt gốc ('dùng cảm biến để né bị phát
    hiện') phải bị CONTRADICTED bởi ledger thật, KHÔNG được publish."""
    monkeypatch.setattr(L, "classify_high_risk_claims", lambda text: _claims(
        ("Hai kẻ trộm dùng chính cảm biến chuyển động của bảo tàng để tránh bị phát hiện.", "security_system"),
    ))
    passed, evidence = L.verify_high_risk_claims("RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3", "văn bản kịch bản thật")
    assert passed is False
    assert "GARDNER_SENSOR_EVASION" in evidence
    assert "BÁC BỎ" in evidence


def test_gardner_motion_recorded_claim_is_verified(monkeypatch):
    """L.7: claim ĐÚNG đã verify ('cảm biến ghi lại đường đi') phải PASS
    với provenance P0 (gardnermuseum.org, đã thêm vào CL_SOURCE_TIERS_v1.json
    Part K -- P0 trực tiếp, không phải Wikipedia)."""
    monkeypatch.setattr(L, "classify_high_risk_claims", lambda text: _claims(
        ("Cảm biến chuyển động của bảo tàng ghi lại đường di chuyển của hai kẻ trộm qua các phòng trưng bày.", "security_system"),
    ))
    passed, evidence = L.verify_high_risk_claims("RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3", "văn bản kịch bản thật")
    assert passed is True


def test_gardner_blue_room_anomaly_claim_is_verified(monkeypatch):
    monkeypatch.setattr(L, "classify_high_risk_claims", lambda text: _claims(
        ("Không có chuyển động nào được ghi nhận ở Blue Room dù tranh Chez Tortoni bị lấy đi từ đó.", "security_system"),
    ))
    passed, evidence = L.verify_high_risk_claims("RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3", "văn bản kịch bản thật")
    assert passed is True


def test_gardner_81_minutes_claim_is_verified(monkeypatch):
    """L.8: mốc thời gian trọng yếu (81 phút) phải VERIFIED qua FBI.gov (P0)."""
    monkeypatch.setattr(L, "classify_high_risk_claims", lambda text: _claims(
        ("Tổng thời gian bên trong bảo tàng là 81 phút.", "timeline"),
    ))
    passed, evidence = L.verify_high_risk_claims("RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3", "văn bản kịch bản thật")
    assert passed is True


def test_gardner_claim_ledger_source_tiers_resolve_correctly():
    """Kiểm tra trực tiếp (không mock) rằng domain thật trong ledger THẬT
    được classify_publisher_tier() nhận đúng P0/P1, không rơi về UNKNOWN
    (regression cho chính bước bổ sung CL_SOURCE_TIERS_v1.json)."""
    tiers = L.load_source_tiers()
    assert g.classify_publisher_tier("https://www.gardnermuseum.org/about/theft", tiers) == g.PublisherTier.PUBLIC_RECORD
    assert g.classify_publisher_tier("https://www.fbi.gov/history/famous-cases/isabella-stewart-gardner-museum-heist", tiers) == g.PublisherTier.PUBLIC_RECORD
    assert g.classify_publisher_tier("https://www.wbur.org/lastseen/2018/09/16/eighty-one-minutes", tiers) == g.PublisherTier.REPUTABLE_PRESS


def test_gardner_ledger_entries_actually_exist_on_disk():
    """Sanity check tối thiểu: 5 claim_id kỳ vọng thật sự có trong
    CL_VERIFIED_CLAIM_LEDGER_v1.json trên đĩa (không chỉ trong test mock)."""
    ledger = L.load_claim_ledger()
    entries = ledger.get("RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3", [])
    ids = {e["claim_id"] for e in entries}
    assert {"GARDNER_SENSOR_EVASION", "GARDNER_SENSOR_RECORDED", "GARDNER_BLUE_ROOM_ANOMALY", "GARDNER_DURATION_81MIN"} <= ids
    sensor_evasion = next(e for e in entries if e["claim_id"] == "GARDNER_SENSOR_EVASION")
    assert sensor_evasion["status"] == "CONTRADICTED"


# =============================================================================
# Adversarial self-review fix: match phải cùng risk_class, không chỉ text
# =============================================================================

def test_match_does_not_cross_risk_class_boundary(monkeypatch):
    """Claim risk_class='legal_status' KHÔNG được khớp 1 entry ledger có
    text gần giống nhưng risk_class='security_system' -- dù ratio text cao,
    lệch nhóm rủi ro nghĩa là 2 claim khác nhau, phải BLOCKED_FACT thay vì
    mượn trạng thái VERIFIED của entry sai nhóm."""
    monkeypatch.setattr(L, "classify_high_risk_claims", lambda text: _claims(("Nghi phạm bị bắt tại hiện trường.", "legal_status")))
    monkeypatch.setattr(L, "load_claim_ledger", lambda: {
        "TOPIC_D": [{
            "claim_id": "C4", "normalized_claim": "nghi phạm bị bắt tại hiện trường",
            "status": "VERIFIED", "risk_class": "security_system",  # KHÁC risk_class với claim đang kiểm tra
            "provenance": [{"source_url": "https://www.fbi.gov/some-case"}],
        }],
    })
    passed, evidence = L.verify_high_risk_claims("TOPIC_D", "văn bản")
    assert passed is False
    assert "KHÔNG có entry ledger khớp" in evidence


# =============================================================================
# fail-closed error handling
# =============================================================================

def test_classify_high_risk_claims_fails_closed_on_malformed_response(monkeypatch):
    monkeypatch.setattr(L, "_run_codex", lambda prompt: "not json {{{")
    with pytest.raises(LifecycleError):
        L.classify_high_risk_claims("văn bản bất kỳ")


def test_classify_high_risk_claims_fails_closed_on_missing_claims_key(monkeypatch):
    import json
    monkeypatch.setattr(L, "_run_codex", lambda prompt: json.dumps({"wrong_key": []}))
    with pytest.raises(LifecycleError):
        L.classify_high_risk_claims("văn bản bất kỳ")


def test_load_claim_ledger_returns_empty_dict_when_file_missing(monkeypatch):
    monkeypatch.setattr(L, "CLAIM_LEDGER_PATH", Path("/khong/ton/tai/nao.json"))
    assert L.load_claim_ledger() == {}


def test_load_claim_ledger_fails_closed_on_corrupt_json(tmp_path, monkeypatch):
    bad = tmp_path / "corrupt.json"
    bad.write_text("{ not valid json", encoding="utf-8")
    monkeypatch.setattr(L, "CLAIM_LEDGER_PATH", bad)
    with pytest.raises(LifecycleError):
        L.load_claim_ledger()


def test_conditional_risk_class_skipped_when_not_material(monkeypatch):
    """numerical/timeline material=False (VÀ lượt xác minh độc lập đồng ý
    material=false) bị miễn -- claim material=True (subject mặc định fail-
    closed=True, không cần xác minh subject vì đã bắt buộc qua nhánh khác)
    vẫn giữ lại."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([
            {"text": "Có khoảng 100 người tham dự.", "risk_class": "numerical", "material": False, "subject_is_named_real_person": False},
            {"text": "Giá trị vụ trộm ước tính 500 triệu đô.", "risk_class": "numerical", "material": True, "subject_is_named_real_person": True},
        ]),
        _material_route(verdict=False),  # xác minh cho claim material=False do pass B (agy) trích -- không xảy ra ở đây nhưng khai đủ phòng khi
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([
        _extraction_route([]),
        _material_route(verdict=False),  # đồng ý claim "100 người tham dự" KHÔNG trọng yếu
    ]))
    claims = L.classify_high_risk_claims("văn bản")
    assert len(claims) == 1
    assert "500 triệu" in claims[0]["text"]


# =============================================================================
# subject_is_named_real_person -- phát hiện thật qua pilot 20-episode (task
# #309): gate cũ chặn claim thể chế/lịch sử thuần tuý (không đụng tình
# trạng pháp lý của 1 CÁ NHÂN thật cụ thể) y hệt claim buộc tội người thật,
# khiến yield PASS chỉ ~18%. Test khoá lại: (a) claim thể chế được miễn
# trừ đúng thiết kế, (b) claim về người thật vẫn fail-closed như cũ, (c)
# field thiếu/sai kiểu vẫn fail-closed (không bị lợi dụng để né ledger).
# =============================================================================

def test_institutional_legal_status_claim_exempt_when_both_passes_agree(monkeypatch):
    """legal_status nhưng chủ thể là 1 TOÀ ÁN/CÔNG TY (thể chế), không phải
    1 cá nhân thật cụ thể -- lượt trích (codex) VÀ lượt xác minh độc lập
    (agy) đều đồng ý false -- được miễn ledger. Lượt trích B (agy) không
    tìm thấy gì thêm (extraction=[])."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Tối cao Pháp viện Hoa Kỳ kết luận Standard Oil vi phạm Đạo luật Sherman.", "risk_class": "legal_status", "subject_is_named_real_person": False}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([
        _extraction_route([]),
        _subject_route(verdict=False),
    ]))
    claims = L.classify_high_risk_claims("văn bản")
    assert claims == []


def test_exemption_blocked_when_pass2_disagrees(monkeypatch):
    """Review đối kháng Codex CLI (BLOCKER): lượt trích (codex) nói
    subject=false nhưng lượt XÁC MINH độc lập (agy) nói true (bất đồng) --
    KHÔNG được miễn, fail-closed giữ claim lại. Đây chính là phòng tuyến vá
    lỗ hổng 'boolean false đúng kiểu nhưng sai ngữ nghĩa' đã bị review chỉ
    ra."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Nguyễn Văn A bị khởi tố về hành vi lừa đảo.", "risk_class": "legal_status", "subject_is_named_real_person": False}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([
        _extraction_route([]),
        _subject_route(verdict=True),  # lượt xác minh KHÔNG đồng ý miễn trừ
    ]))
    claims = L.classify_high_risk_claims("văn bản")
    assert len(claims) == 1


def test_exemption_blocked_when_pass2_errors(monkeypatch):
    """Lượt xác minh (agy) lỗi (network/parse/timeout...) -- fail-closed:
    KHÔNG miễn trừ, vẫn giữ claim lại."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Quan chức X bị điều tra vì nhận hối lộ.", "risk_class": "legal_status", "subject_is_named_real_person": False}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([
        _extraction_route([]),
        _subject_route(exc=RuntimeError("agy lỗi mạng")),
    ]))
    claims = L.classify_high_risk_claims("văn bản")
    assert len(claims) == 1


def test_exemption_blocked_when_pass2_returns_malformed_response(monkeypatch):
    """Lượt xác minh trả về JSON hợp lệ nhưng không phải dict (vd 1
    list/string) -- fail-closed, không miễn trừ."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Quan chức Y bị cáo buộc tham nhũng nhưng chưa bị khởi tố chính thức.", "risk_class": "legal_status", "subject_is_named_real_person": False}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([
        _extraction_route([]),
        _subject_route(raw="khong phai json object"),
    ]))
    claims = L.classify_high_risk_claims("văn bản")
    assert len(claims) == 1


def test_legal_status_claim_about_named_person_still_required(monkeypatch):
    """CÙNG risk_class=legal_status nhưng lượt trích đã nói subject_is_
    named_real_person=True -- KHÔNG cần gọi lượt xác minh (không đủ điều
    kiện miễn trừ ngay từ đầu), hành vi cũ giữ nguyên: không khớp ledger
    nào -> BLOCKED_FACT."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Kevin Mitnick bị kết án 5 năm tù.", "risk_class": "legal_status", "subject_is_named_real_person": True}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([_extraction_route([])]))  # không cần lượt xác minh subject/material
    monkeypatch.setattr(L, "load_claim_ledger", lambda: {})
    passed, evidence, verified_ids, blocked_ids = L.verify_high_risk_claims_with_refs("TOPIC_MITNICK", "văn bản kịch bản thật")
    assert passed is False
    assert "BLOCKED_FACT" in evidence


def test_subject_is_named_real_person_missing_fails_closed(monkeypatch):
    """Field subject_is_named_real_person THIẾU hoàn toàn trong response
    model (không phải False tường minh) -- fail-closed ngay, không cần
    lượt xác minh."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Nghi phạm hành động vì thù hằn cá nhân.", "risk_class": "motive"}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([_extraction_route([])]))
    claims = L.classify_high_risk_claims("văn bản")
    assert len(claims) == 1


def test_subject_is_named_real_person_malformed_type_fails_closed(monkeypatch):
    """Field trả về sai kiểu (string thay vì bool) -- vẫn KHÔNG phải False
    tường minh nên fail-closed, không cần lượt xác minh."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Vì áp lực công luận, quan chức đã từ chức.", "risk_class": "causal", "subject_is_named_real_person": "khong_chac"}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([_extraction_route([])]))
    claims = L.classify_high_risk_claims("văn bản")
    assert len(claims) == 1


def test_allegation_always_required_regardless_of_subject(monkeypatch):
    """allegation thuộc ALWAYS_HIGH_RISK_CLASSES -- KHÔNG được miễn dù
    subject_is_named_real_person=False, không đi qua nhánh subject-gated
    nên không cần lượt xác minh."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Công ty X bị cáo buộc gian lận kế toán.", "risk_class": "allegation", "subject_is_named_real_person": False}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([_extraction_route([])]))
    claims = L.classify_high_risk_claims("văn bản")
    assert len(claims) == 1


def test_forensic_and_security_system_always_required_regardless_of_subject(monkeypatch):
    """forensic/security_system thuộc ALWAYS_HIGH_RISK_CLASSES -- không có
    trục 'chủ thể' nào miễn trừ được."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([
            {"text": "Dấu vân tay được tìm thấy tại hiện trường.", "risk_class": "forensic", "subject_is_named_real_person": False},
            {"text": "Hệ thống camera không ghi nhận chuyển động.", "risk_class": "security_system", "subject_is_named_real_person": False},
        ]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([_extraction_route([])]))
    claims = L.classify_high_risk_claims("văn bản")
    assert len(claims) == 2


def test_material_numerical_institutional_claim_is_exempt(monkeypatch):
    """numerical material=True nhưng chủ thể là 1 công ty/thể chế -- cả
    lượt trích và lượt xác minh subject đều đồng ý false -- miễn ledger."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Standard Oil bị giải thể thành khoảng 34 công ty con.", "risk_class": "numerical", "material": True, "subject_is_named_real_person": False}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([
        _extraction_route([]),
        _subject_route(verdict=False),
    ]))
    claims = L.classify_high_risk_claims("văn bản")
    assert claims == []


def test_material_missing_fails_closed_as_material(monkeypatch):
    """field 'material' THIẾU cho claim numerical/timeline -- fail-closed:
    coi là True (trọng yếu), vẫn xét tiếp (và với subject thiếu -> True
    mặc định thì vẫn bắt buộc ledger, không cần lượt xác minh nào)."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Giá trị vụ trộm ước tính 500 triệu đô.", "risk_class": "numerical"}]),  # thiếu cả material lẫn subject_is_named_real_person
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([_extraction_route([])]))
    claims = L.classify_high_risk_claims("văn bản")
    assert len(claims) == 1


def test_material_false_blocked_when_independent_check_disagrees(monkeypatch):
    """Review đối kháng round 2 (Codex CLI, HIGH): material=False tự khai
    cũng phải qua xác minh độc lập trước khi miễn trừ, CÙNG kỷ luật với
    subject -- lượt xác minh KHÔNG đồng ý (material=true thật) -> vẫn giữ
    claim lại."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Số nạn nhân được ghi nhận là 12 người.", "risk_class": "numerical", "material": False, "subject_is_named_real_person": False}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([
        _extraction_route([]),
        _material_route(verdict=True),  # lượt xác minh nói ĐÂY THẬT SỰ trọng yếu
    ]))
    claims = L.classify_high_risk_claims("văn bản")
    assert len(claims) == 1


def test_unknown_risk_class_fails_closed(monkeypatch):
    """risk_class không thuộc 9 nhãn đã biết (model trả nhãn lạ/gõ sai) --
    trước đây bị âm thầm coi như 'ordinary' và bỏ qua; nay raise fail-closed
    thay vì im lặng bỏ qua 1 claim có thể thật sự rủi ro."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Claim gì đó.", "risk_class": "khong_ro_nhan"}]),
    ]))
    with pytest.raises(LifecycleError):
        L.classify_high_risk_claims("văn bản")


def test_accusation_keyword_forces_ledger_even_when_mislabeled_ordinary(monkeypatch):
    """Review đối kháng Codex CLI (BLOCKER #3): allegation/legal_status
    chồng lấn ranh giới, model có thể gán nhầm 1 câu cáo buộc thành nhãn
    khác (kể cả 'ordinary') RỒI đồng thời gắn subject=false -- lớp phòng
    thủ từ khoá phải bắt được case này bất kể risk_class model chọn, không
    cần lượt xác minh."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "John Doe bị cáo buộc rửa tiền.", "risk_class": "ordinary", "subject_is_named_real_person": False}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([_extraction_route([])]))
    claims = L.classify_high_risk_claims("văn bản")
    assert len(claims) == 1


def test_accusation_keyword_forces_ledger_even_when_mislabeled_legal_status(monkeypatch):
    """Biến thể: model gán 'legal_status' (thay vì 'allegation' đúng ra
    phải chọn) VÀ subject=false -- từ khoá 'bị cáo buộc' vẫn chặn cứng."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Công tố viên nói A tổ chức đường dây rửa tiền, A hiện bị cáo buộc.", "risk_class": "legal_status", "subject_is_named_real_person": False}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([_extraction_route([])]))
    claims = L.classify_high_risk_claims("văn bản")
    assert len(claims) == 1


def test_ordinary_mislabel_caught_by_independent_extraction_no_keyword(monkeypatch):
    """Review đối kháng round 2 (Codex CLI, BLOCKER #1) -- ví dụ CHÍNH XÁC
    được review nêu ra: 'FBI cho rằng John Doe điều hành đường dây' KHÔNG
    khớp bất kỳ từ khoá nào trong _ACCUSATION_KEYWORDS (không có 'cáo
    buộc'/'nghi phạm'/...) VÀ lượt trích A (codex) gán nhầm 'ordinary' +
    subject=false -- CHỈ được cứu bởi lượt trích B (agy) trích ĐỘC LẬP
    TOÀN VĂN và tự tìm ra + gắn đúng risk_class=allegation cho CHÍNH câu
    đó. Union 2 lượt -> vẫn bắt buộc ledger."""
    text = "FBI cho rằng John Doe điều hành đường dây buôn lậu."
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "FBI cho rằng John Doe điều hành đường dây buôn lậu.", "risk_class": "ordinary", "subject_is_named_real_person": False}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([
        _extraction_route([{"text": "FBI cho rằng John Doe điều hành đường dây buôn lậu.", "risk_class": "allegation", "subject_is_named_real_person": True}]),
    ]))
    claims = L.classify_high_risk_claims(text)
    assert len(claims) == 1  # union: pass B's correctly-labeled claim vẫn lọt vào, dù pass A bỏ sót/gán sai


def test_pass1_returns_empty_but_pass2_independent_extraction_finds_claim(monkeypatch):
    """Biến thể cực đoan của BLOCKER #1: lượt trích A (codex) trả về
    claims=[] HOÀN TOÀN (bỏ sót mọi claim) -- lượt trích B (agy) ĐỘC LẬP
    vẫn tự tìm ra claim rủi ro cao. Trước round-2-fix, claims=[] của lượt
    1 từng được coi là kết quả hợp lệ cuối cùng (không có gì để lo)."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([_extraction_route([])]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([
        _extraction_route([{"text": "Vị thẩm phán chủ toạ đã nhận hối lộ để tuyên trắng án.", "risk_class": "legal_status", "subject_is_named_real_person": True}]),
    ]))
    claims = L.classify_high_risk_claims("văn bản")
    assert len(claims) == 1


def test_institutional_topic_passes_end_to_end_with_empty_ledger(monkeypatch):
    """Kịch bản THẬT quan sát được qua pilot: 1 topic thuần thể chế/lịch sử
    (không đụng tình trạng pháp lý của 1 cá nhân thật, không chứa từ khoá
    buộc tội) phải PASS dù ledger HOÀN TOÀN rỗng cho topic đó, VỚI ĐIỀU
    KIỆN CẢ 2 lượt trích độc lập đều không tìm thấy gì thêm VÀ lượt xác
    minh subject đồng ý -- đây chính là hành vi cần sửa (trước khi vá, mọi
    claim legal_status/timeline/causal đều bị BLOCKED_FACT dù không có rủi
    ro phỉ báng thật nào)."""
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([
            {"text": "Đạo luật Bắt cóc Liên bang được Quốc hội thông qua năm 1932.", "risk_class": "timeline", "material": True, "subject_is_named_real_person": False},
            {"text": "Bản sửa đổi năm 1934 nhằm giảm gánh nặng chứng minh cho công tố liên bang.", "risk_class": "causal", "subject_is_named_real_person": False},
        ]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([
        _extraction_route([]),
        _subject_route(verdict=False),
    ]))
    monkeypatch.setattr(L, "load_claim_ledger", lambda: {})
    passed, evidence, verified_ids, blocked_ids = L.verify_high_risk_claims_with_refs("RESEARCH_DRAFT_TO_CHUC_THUC_THI_PHAP_LUAT", "văn bản kịch bản thật")
    assert passed is True
    assert verified_ids == []
    assert blocked_ids == []


# =============================================================================
# Canary pilot finding (task #304, BLOCKER): SequenceMatcher.ratio() +
# bag-of-words overlap ĐỀU không đủ nhạy khi 1 claim chỉ đổi đúng 1 con số
# so với ledger entry ("...81 phút" -> "...45 phút") -- phần còn lại của câu
# giống hệt nên vẫn vượt ngưỡng dễ dàng, khiến số liệu bị đổi được khớp
# VERIFIED nhầm. Xác nhận THẬT qua producer path (verify_high_risk_claims)
# lẫn consumer path (validate_fact_verification_binding) trước khi vá
# _numeric_tokens_mismatch(); test này lock lại hành vi ĐÃ vá.
# =============================================================================

def test_altered_number_does_not_match_ledger_entry_with_different_number(monkeypatch):
    """L.9 (canary pilot BLOCKER): claim đổi 81->45 phút KHÔNG được khớp
    GARDNER_DURATION_81MIN dù phần còn lại của câu giống hệt."""
    monkeypatch.setattr(L, "classify_high_risk_claims", lambda text: _claims(
        ("Tổng thời gian bên trong bảo tàng là 45 phút.", "timeline"),
    ))
    passed, evidence = L.verify_high_risk_claims("RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3", "văn bản kịch bản thật")
    assert passed is False
    assert "BLOCKED_FACT" in evidence


def test_altered_number_fails_consumer_binding_check_even_with_real_claim_id():
    """L.10 (canary pilot BLOCKER, consumer layer): sidecar khai đúng
    claim_id=GARDNER_DURATION_81MIN thật (không giả mạo claim_id) nhưng
    script đang publish nói 45 phút (không phải 81) -- validate_fact_
    verification_binding() phải BLOCK, không được chỉ dựa bag-of-words
    overlap của phần còn lại của câu."""
    fv = {
        "state": "VERIFIED_CLAIM_LEDGER",
        "topic_id": "RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3",
        "ledger_version": L.ledger_version(),
        "verified_claim_ids": ["GARDNER_DURATION_81MIN"],
        "blocked_claim_ids": [],
        "checked_at": "2026-08-24T00:00:00Z",
    }
    script = "Tổng thời gian hai kẻ trộm ở trong bảo tàng là 45 phút."
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False
    assert "GARDNER_DURATION_81MIN" in reason


# =============================================================================
# Review đối kháng round 2 (Codex CLI, BLOCKER #2) -- "vacuous success":
# verified_claim_ids=[] trước đây khiến vòng lặp trong validate_fact_
# verification_binding() không làm gì và hàm trả True VÔ ĐIỀU KIỆN, bất kể
# final_script THẬT SỰ có chứa claim rủi ro cao chưa từng qua ledger hay
# không (sidecar giả mạo/hỏng với state=VERIFIED_CLAIM_LEDGER + list rỗng
# vẫn qua được publish boundary). Vá bằng cách gọi LẠI verify_high_risk_
# claims_with_refs(topic_id, final_script) TƯƠI trên CHÍNH final_script
# đang publish, không tin field tự khai nào của `fact_verification`.
# =============================================================================

def test_forged_sidecar_with_empty_ids_blocked_when_script_has_real_high_risk_claim(monkeypatch):
    """Sidecar 'hợp lệ về hình thức' (state đúng, ledger_version khớp,
    verified_claim_ids=[]) nhưng final_script THẬT SỰ chứa 1 claim rủi ro
    cao (chưa từng qua ledger) -- trước round-2-fix, hàm trả True vì vòng
    lặp rỗng không phát hiện gì. Nay tái phân loại TƯƠI trên final_script
    phải bắt được và BLOCK."""
    fv = {
        "state": "VERIFIED_CLAIM_LEDGER",
        "topic_id": "TOPIC_FORGED",
        "ledger_version": L.ledger_version(),
        "verified_claim_ids": [],
        "blocked_claim_ids": [],
        "checked_at": "2026-08-26T00:00:00Z",
    }
    script = "Nguyễn Văn A bị khởi tố về hành vi lừa đảo chiếm đoạt tài sản."
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": "Nguyễn Văn A bị khởi tố về hành vi lừa đảo chiếm đoạt tài sản.", "risk_class": "legal_status", "subject_is_named_real_person": True}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([_extraction_route([])]))
    monkeypatch.setattr(L, "load_claim_ledger", lambda: {})  # TOPIC_FORGED chưa từng được populate
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False
    assert "Tái phân loại" in reason


def test_genuinely_empty_claims_sidecar_still_passes(monkeypatch):
    """Hồi quy an toàn: verified_claim_ids=[] hợp lệ khi final_script THẬT
    SỰ không có claim rủi ro cao nào (nội dung thuần thể chế/lịch sử) --
    tái phân loại tươi cũng phải trả rỗng, không được biến mọi sidecar rỗng
    thành BLOCKED oan."""
    fv = {
        "state": "VERIFIED_CLAIM_LEDGER",
        "topic_id": "TOPIC_ORDINARY",
        "ledger_version": L.ledger_version(),
        "verified_claim_ids": [],
        "blocked_claim_ids": [],
        "checked_at": "2026-08-26T00:00:00Z",
    }
    script = "Ranh giới giữa giảm thuế hợp pháp và trốn thuế nằm ở bản chất giao dịch, không phải số tiền."
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([_extraction_route([])]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([_extraction_route([])]))
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is True


# =============================================================================
# Review đối kháng round 3 (Codex CLI, 2 HIGH còn lại sau khi BLOCKER an
# toàn nội dung đã đóng): (a) lỗi hạ tầng ở Step 2 (LifecycleError từ lượt
# trích) không được làm crash batch worker -- phải fail-closed CÓ KIỂM
# SOÁT; (b) claim tái phân loại tìm được PHẢI là tập con của verified_
# claim_ids sidecar tự khai -- sidecar THIẾU record cho 1 claim thật (dù
# nội dung claim đó vẫn an toàn) không được coi là "hợp lệ".
# =============================================================================

def test_step2_llm_failure_fails_closed_without_crashing(monkeypatch):
    """Lượt trích ở Step 2 raise LifecycleError (lỗi hạ tầng/JSON hỏng) --
    validate_fact_verification_binding() PHẢI bắt lại và trả (False, lý
    do), KHÔNG được để exception lan ra ngoài làm crash batch worker."""
    fv = {
        "state": "VERIFIED_CLAIM_LEDGER",
        "topic_id": "TOPIC_INFRA_LOI",
        "ledger_version": L.ledger_version(),
        "verified_claim_ids": [],
        "blocked_claim_ids": [],
        "checked_at": "2026-08-26T00:00:00Z",
    }
    script = "Văn bản bất kỳ."
    monkeypatch.setattr(L, "_run_codex", lambda prompt: "not json {{{")  # Step 2 sẽ raise LifecycleError khi trích
    ok, reason = L.validate_fact_verification_binding(fv, script)  # KHÔNG được raise ra ngoài
    assert ok is False
    assert "lỗi" in reason.lower()


def test_step1_ledger_load_failure_fails_closed_without_crashing(monkeypatch):
    """Review đối kháng round 4 (Codex CLI, HIGH): lỗi ở Step 1 (vd
    load_claim_ledger() raise LifecycleError vì file ledger hỏng), KHÔNG
    chỉ Step 2, cũng PHẢI fail-closed có kiểm soát -- vỏ bọc ngoài cùng
    validate_fact_verification_binding() bắt MỌI exception, không riêng
    lỗi từ tái phân loại."""
    fv = {
        "state": "VERIFIED_CLAIM_LEDGER",
        "topic_id": "TOPIC_X",
        "ledger_version": L.ledger_version(),
        "verified_claim_ids": ["C1"],
        "blocked_claim_ids": [],
        "checked_at": "2026-08-26T00:00:00Z",
    }
    def _raise_corrupt(*a, **k):
        raise L.LifecycleError("ledger JSON hỏng")
    monkeypatch.setattr(L, "load_claim_ledger", _raise_corrupt)
    ok, reason = L.validate_fact_verification_binding(fv, "văn bản bất kỳ")  # KHÔNG được raise ra ngoài
    assert ok is False
    assert "lỗi" in reason.lower()


def test_verified_claim_ids_with_non_hashable_element_fails_closed_without_crashing(monkeypatch):
    """verified_claim_ids chứa phần tử KHÔNG hashable (vd dict) -- trước
    round-4-fix, topic_entries.get(claim_id) sẽ raise TypeError ra ngoài;
    nay vỏ bọc ngoài cùng bắt lại, fail-closed thay vì crash."""
    fv = {
        "state": "VERIFIED_CLAIM_LEDGER",
        "topic_id": "TOPIC_Y",
        "ledger_version": L.ledger_version(),
        "verified_claim_ids": [{"khong": "hashable"}],
        "blocked_claim_ids": [],
        "checked_at": "2026-08-26T00:00:00Z",
    }
    ok, reason = L.validate_fact_verification_binding(fv, "văn bản bất kỳ")  # KHÔNG được raise TypeError ra ngoài
    assert ok is False
    assert "lỗi" in reason.lower()


def test_sidecar_missing_provenance_record_for_freshly_found_claim_blocked(monkeypatch):
    """verified_claim_ids=[] trong sidecar, nhưng final_script THẬT SỰ có 1
    claim rủi ro cao ĐÃ khớp ledger VERIFIED P0/P1 khi tái phân loại tươi --
    claim_id đó KHÔNG nằm trong verified_claim_ids sidecar tự khai (sidecar
    THIẾU provenance record) -- phải BLOCK dù nội dung claim tự nó an
    toàn, vì sidecar không phản ánh đúng thực tế đã kiểm tra gì."""
    fv = {
        "state": "VERIFIED_CLAIM_LEDGER",
        "topic_id": "RESEARCH_DRAFT_VU_AN_CHUA_LOI_GIAI_BATCH3",
        "ledger_version": L.ledger_version(),
        "verified_claim_ids": [],  # THIẾU record cho GARDNER_SENSOR_RECORDED dù script thật chứa claim đó
        "blocked_claim_ids": [],
        "checked_at": "2026-08-26T00:00:00Z",
    }
    script = "Cảm biến chuyển động của bảo tàng ghi lại đường di chuyển của hai kẻ trộm qua các phòng trưng bày."
    monkeypatch.setattr(L, "_run_codex", _dispatch_by_marker([
        _extraction_route([{"text": script, "risk_class": "security_system"}]),
    ]))
    monkeypatch.setattr(L, "_run_agy", _dispatch_by_marker([_extraction_route([])]))
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False
    assert "thiếu provenance record" in reason.lower()


# =============================================================================
# VERIFIED_CLAUDE_REVIEW -- theo yêu cầu tường minh của user (không phải
# quyết định tự ý): bỏ phụ thuộc codex/agy tại publish boundary sau khi cả
# 2 dịch vụ lặp lại hết quota/lỗi hạ tầng khiến pilot nghẽn. Đây LÀ 1 nới
# lỏng THẬT của nguyên tắc "không tin state tự khai" -- test khoá lại 4
# lớp fail-closed KHÔNG cần LLM vẫn còn (tinh chỉnh sau 1 vòng review đối
# kháng Codex CLI): review_outcome tường minh + nhất quán với reviewed_
# claims, reviewer phải đúng "claude", reviewed_script_hash phải khớp FULL
# hash final_script THẬT, reviewed_at phải parse được ISO-8601 thật.
# =============================================================================

def _claude_review_hash(script: str) -> str:
    import hashlib
    return hashlib.sha256(script.encode("utf-8")).hexdigest()


def _valid_claude_fv(script, **overrides):
    fv = {
        "state": "VERIFIED_CLAUDE_REVIEW",
        "review_outcome": "CLAIMS_REVIEWED",
        "reviewer": "claude",
        "reviewed_script_hash": _claude_review_hash(script),
        "reviewed_claims": [
            {"claim": "Đạo luật X được ban hành năm 1900.", "risk_class": "timeline", "verdict": "institutional, không đụng tình trạng pháp lý của người thật cụ thể"},
        ],
        "reviewed_at": "2026-09-03T00:00:00Z",
    }
    fv.update(overrides)
    return fv


def test_claude_review_state_passes_with_valid_structure():
    script = "Văn bản đã được Claude tự duyệt."
    fv = _valid_claude_fv(script)
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is True
    assert "VERIFIED_CLAUDE_REVIEW" in reason


def test_claude_review_no_high_risk_claims_found_passes_with_empty_list():
    """review_outcome=NO_HIGH_RISK_CLAIMS_FOUND + reviewed_claims=[] là
    tổ hợp NHẤT QUÁN hợp lệ (khác với thiếu review_outcome hoàn toàn)."""
    script = "Văn bản thuần mô tả, không có claim rủi ro cao nào."
    fv = _valid_claude_fv(script, review_outcome="NO_HIGH_RISK_CLAIMS_FOUND", reviewed_claims=[])
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is True


def test_claude_review_rejects_missing_review_outcome():
    """Finding thật từ review đối kháng: trước đây reviewed_claims=[] pass
    ÂM THẦM dù không rõ 'đã xét không có gì' hay 'chưa xét gì' -- nay bắt
    buộc review_outcome tường minh."""
    script = "Văn bản bất kỳ."
    fv = _valid_claude_fv(script, reviewed_claims=[])
    fv.pop("review_outcome")
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False


def test_claude_review_rejects_claims_reviewed_with_empty_list():
    """review_outcome=CLAIMS_REVIEWED nhưng reviewed_claims rỗng -- không
    nhất quán (nói có claim đã xét nhưng không liệt kê gì)."""
    script = "Văn bản bất kỳ."
    fv = _valid_claude_fv(script, review_outcome="CLAIMS_REVIEWED", reviewed_claims=[])
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False


def test_claude_review_rejects_no_high_risk_claims_with_nonempty_list():
    """review_outcome=NO_HIGH_RISK_CLAIMS_FOUND nhưng reviewed_claims KHÔNG
    rỗng -- không nhất quán."""
    script = "Văn bản bất kỳ."
    fv = _valid_claude_fv(script, review_outcome="NO_HIGH_RISK_CLAIMS_FOUND")
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False


def test_claude_review_rejects_unknown_review_outcome():
    script = "Văn bản bất kỳ."
    fv = _valid_claude_fv(script, review_outcome="DA_XONG_ROI")
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False


def test_claude_review_rejects_wrong_reviewer_name():
    script = "Văn bản bất kỳ."
    fv = _valid_claude_fv(script, reviewer="codex")  # KHÔNG phải "claude"
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False


def test_claude_review_rejects_missing_reviewer():
    script = "Văn bản bất kỳ."
    fv = _valid_claude_fv(script)
    fv.pop("reviewer")
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False


def test_claude_review_blocks_when_script_hash_mismatched():
    """Kịch bản THẬT quan trọng nhất: Claude duyệt 1 bản script, sau đó
    script bị đổi trước khi publish (dù chỉ đổi 1 chi tiết) -- phải BLOCK,
    không được để reviewed_script_hash cũ 'kế thừa' cho script mới."""
    reviewed_script = "Bản gốc Claude đã đọc và duyệt."
    tampered_script = "Bản ĐÃ BỊ SỬA sau khi Claude duyệt."
    fv = _valid_claude_fv(reviewed_script)
    ok, reason = L.validate_fact_verification_binding(fv, tampered_script)
    assert ok is False
    assert "KHÔNG khớp" in reason


def test_claude_review_uses_full_hash_not_truncated():
    """Review đối kháng Codex CLI (finding thật): prefix 64-bit làm bài
    toán collision có chủ đích rẻ hơn nhiều so với full sha256 -- khoá lại
    hash dùng ĐÚNG full hexdigest (64 ký tự), không cắt ngắn."""
    script = "Văn bản bất kỳ."
    fv = _valid_claude_fv(script)
    assert len(fv["reviewed_script_hash"]) == 64  # full sha256 hex, không cắt còn 16


def test_claude_review_rejects_missing_script_hash():
    script = "Văn bản bất kỳ."
    fv = _valid_claude_fv(script)
    fv.pop("reviewed_script_hash")
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False


def test_claude_review_rejects_non_list_reviewed_claims():
    script = "Văn bản bất kỳ."
    fv = _valid_claude_fv(script, reviewed_claims="tôi đã duyệt hết rồi")  # KHÔNG phải list
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False


def test_claude_review_rejects_malformed_claim_entry():
    script = "Văn bản bất kỳ."
    fv = _valid_claude_fv(script, reviewed_claims=[{"claim": "Claim gì đó."}])  # thiếu risk_class/verdict
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False


def test_claude_review_rejects_missing_reviewed_at():
    script = "Văn bản bất kỳ."
    fv = _valid_claude_fv(script)
    fv.pop("reviewed_at")
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False


def test_claude_review_rejects_unparseable_reviewed_at():
    """Finding thật từ review đối kháng: trước đây chỉ cần string không
    rỗng, kể cả 'x' cũng qua -- nay phải parse được ISO-8601 thật."""
    script = "Văn bản bất kỳ."
    fv = _valid_claude_fv(script, reviewed_at="x")
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is False


def test_claude_review_accepts_iso8601_with_z_suffix():
    script = "Văn bản bất kỳ."
    fv = _valid_claude_fv(script, reviewed_at="2026-09-03T12:34:56Z")
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is True


def test_claude_review_does_not_call_any_llm(monkeypatch):
    """Xác nhận THẬT mục tiêu của nhánh này: KHÔNG gọi _run_codex/_run_agy
    dưới bất kỳ hình thức nào."""
    script = "Văn bản đã được Claude tự duyệt, không qua LLM nào khác."
    def _should_not_be_called(prompt):
        raise AssertionError("VERIFIED_CLAUDE_REVIEW không được gọi bất kỳ LLM nào")
    monkeypatch.setattr(L, "_run_codex", _should_not_be_called)
    monkeypatch.setattr(L, "_run_agy", _should_not_be_called)
    fv = _valid_claude_fv(script)
    ok, reason = L.validate_fact_verification_binding(fv, script)
    assert ok is True


def test_numeric_tokens_mismatch_ignores_claims_without_numbers():
    """_numeric_tokens_mismatch() chỉ áp dụng khi text_a (nguồn sự thật)
    CÓ số -- claim/entry không chứa số nào thì không bị chặn bởi check này
    (không phải mọi claim đều có số cụ thể)."""
    assert L._numeric_tokens_mismatch("kẻ trộm mặc đồng phục cảnh sát", "kẻ trộm giả danh cảnh sát để vào bảo tàng") is False


def test_numeric_tokens_mismatch_true_when_number_differs():
    assert L._numeric_tokens_mismatch("tổng thời gian là 81 phút", "tổng thời gian là 45 phút") is True


def test_numeric_tokens_mismatch_false_when_number_matches():
    assert L._numeric_tokens_mismatch("tổng thời gian là 81 phút", "kịch bản nói tổng thời gian bên trong là khoảng 81 phút") is False


# =============================================================================
# C4 repair task -- mở rộng coverage số liệu bị đổi theo đúng yêu cầu §12
# ("Add/retain permanent tests covering at least: 81->45, $22M->$28M,
# 1984->1985"). 81->45 đã có ở trên (test_altered_number_*) -- 2 test dưới
# đây thêm 2 case còn lại, cùng cơ chế _numeric_tokens_mismatch().
# =============================================================================

def test_numeric_tokens_mismatch_true_when_dollar_amount_differs():
    assert L._numeric_tokens_mismatch("hối lộ khoảng 22 triệu USD", "hối lộ khoảng 28 triệu USD") is True


def test_numeric_tokens_mismatch_true_when_year_differs():
    assert L._numeric_tokens_mismatch("phát hiện vào năm 1984", "phát hiện vào năm 1985") is True
