"""Regression coverage cho cl_story_plan_and_generation.py -- khóa lại các
defect THẬT phát hiện qua C4 Repair Round 4 (7 lỗ hổng vá + xác nhận lại)
và Round 5 (blind validation, bao gồm bẫy pháp lý Kenneth Lay THẬT) trước
khi tích hợp production (Round 6). Xem handoff/C4_REPAIR_ROUND4_REPORT.md
Phần 11 + handoff/C4_ROUND5_BLIND_VALIDATION_REPORT.md Phần 4/8."""
import json

import pytest

import cl_story_plan_and_generation as spg
from cl_story_fact_pack import StoryFact, StoryFactPack


def _pack(topic_id="T1", facts=None):
    return StoryFactPack(topic_id=topic_id, source_file=f"{topic_id}.md", excerpt_hash="h", ledger_version_at_build="v1", facts=facts or [])


def _fake_json(obj):
    return json.dumps(obj, ensure_ascii=False)


# ---------------------------------------------------------------- Story Plan

def test_plan_fails_closed_on_fake_fact_id(monkeypatch):
    pack = _pack(facts=[StoryFact(fact_id="F001", proposition="A.", source_spans=["A"])])
    monkeypatch.setattr(spg, "_run_codex", lambda prompt: _fake_json({"segments": [
        {"segment_id": "S1", "role": "HOOK", "fact_ids": ["F999"]},  # fact_id KHÔNG có trong pack
    ]}))
    with pytest.raises(ValueError, match="fact_id không có trong pack"):
        spg.build_story_plan(pack)


def test_plan_rejects_empty_segments(monkeypatch):
    pack = _pack(facts=[StoryFact(fact_id="F001", proposition="A.", source_spans=["A"])])
    monkeypatch.setattr(spg, "_run_codex", lambda prompt: _fake_json({"segments": []}))
    with pytest.raises(ValueError, match="rỗng"):
        spg.build_story_plan(pack)


def test_plan_prompt_instructs_payoff_must_add_new_info():
    """C4 Round 5 finding (payoff lặp lại hook, xem
    C4_ROUND5_BLIND_VALIDATION_REPORT.md Phần 11/32): quy tắc chất lượng
    nhẹ, cấp plan -- khóa lại hướng dẫn còn tồn tại trong prompt."""
    assert "PAYOFF" in spg._PLAN_PROMPT
    assert "lặp lại" in spg._PLAN_PROMPT


# --------------------------------------------------------- generate_bound_script

def test_generate_bound_script_fails_closed_on_plan_pack_hash_mismatch(monkeypatch):
    """Cross-topic plan attack: plan.fact_pack_hash không khớp pack hiện
    tại (bị copy từ topic khác, hoặc pack đã rebuild) -- KHÔNG được sinh
    script (fail-closed TRƯỚC khi tốn bất kỳ lượt LLM nào)."""
    pack = _pack(facts=[StoryFact(fact_id="F001", proposition="A.", source_spans=["A"])])
    stale_plan = spg.StoryPlan(topic_id="T1", fact_pack_hash="stale_hash_from_other_pack", segments=[spg.PlanSegment("S1", "HOOK", ["F001"])])
    with pytest.raises(ValueError, match="không khớp pack hiện tại"):
        spg.generate_bound_script(stale_plan, pack)


def test_generate_bound_script_binds_pack_hash_at_generation(monkeypatch):
    pack = _pack(facts=[StoryFact(fact_id="F001", proposition="A xảy ra.", source_spans=["A xảy ra"])])
    plan = spg.StoryPlan(topic_id="T1", fact_pack_hash=pack.pack_hash(), segments=[spg.PlanSegment("S1", "HOOK", ["F001"])])
    monkeypatch.setattr(spg, "_run_agy", lambda prompt: _fake_json({"prose": "A đã xảy ra thật."}))
    script_text, bindings = spg.generate_bound_script(plan, pack)
    assert bindings[0]["pack_hash_at_generation"] == pack.pack_hash()


# ----------------------------------------------------- validate_binding_integrity

def test_integrity_rejects_unknown_fact_id():
    pack = _pack(facts=[StoryFact(fact_id="F001", proposition="A.", source_spans=["A"])])
    bindings = [{"segment_id": "S1", "fact_ids": ["F999"], "prose": "text", "pack_hash_at_generation": pack.pack_hash()}]
    violations = spg.validate_binding_integrity(bindings, pack)
    assert violations
    assert "F999" in violations[0]


def test_integrity_rejects_copied_binding_across_packs():
    """Mutation #12 THẬT (C4 Round 4 mutation test đầu tiên): binding bị
    copy từ 1 pack/topic KHÁC, dù fact_id trùng namespace (F001, F002...),
    phải bị chặn CƠ HỌC -- KHÔNG phụ thuộc 2 pack có tình cờ trùng nội
    dung/số liệu hay không (điểm khác biệt so với lần chặn đầu tiên ở
    round 4, vốn chỉ chặn được nhờ may rủi số liệu không trùng)."""
    pack_a = _pack(topic_id="TOPIC_A", facts=[StoryFact(fact_id="F001", proposition="A thuộc topic A.", source_spans=["A thuộc topic A"])])
    pack_b = _pack(topic_id="TOPIC_B", facts=[StoryFact(fact_id="F001", proposition="B thuộc topic B, KHÔNG liên quan A.", source_spans=["B thuộc topic B"])])
    binding_from_pack_a = [{"segment_id": "S1", "fact_ids": ["F001"], "prose": "A thuộc topic A.", "pack_hash_at_generation": pack_a.pack_hash()}]
    violations = spg.validate_binding_integrity(binding_from_pack_a, pack_b)
    assert violations
    assert "pack_hash_at_generation" in violations[0]


def test_integrity_passes_for_legit_binding():
    pack = _pack(facts=[StoryFact(fact_id="F001", proposition="A.", source_spans=["A"])])
    bindings = [{"segment_id": "S1", "fact_ids": ["F001"], "prose": "A.", "pack_hash_at_generation": pack.pack_hash()}]
    assert spg.validate_binding_integrity(bindings, pack) == []


def test_integrity_backward_compatible_when_pack_hash_at_generation_missing():
    """Binding cũ (sinh trước khi trường pack_hash_at_generation tồn tại)
    không có field này -- KHÔNG tự động fail (None nghĩa là 'chưa gắn',
    không phải 'giả mạo'); vẫn kiểm tra fact_id tồn tại như trước."""
    pack = _pack(facts=[StoryFact(fact_id="F001", proposition="A.", source_spans=["A"])])
    bindings = [{"segment_id": "S1", "fact_ids": ["F001"], "prose": "A."}]
    assert spg.validate_binding_integrity(bindings, pack) == []


# --------------------------------------------------------- run_deterministic_guards

def test_numeric_guard_blocks_changed_number():
    pack = _pack(facts=[StoryFact(fact_id="F001", proposition="475 người bị bắt.", source_spans=["475 người bị bắt"])])
    bindings = [{"segment_id": "S1", "fact_ids": ["F001"], "prose": "290 người bị bắt.", "pack_hash_at_generation": pack.pack_hash()}]
    violations = spg.run_deterministic_guards(bindings, pack)
    assert violations
    assert "290" in violations[0]


def test_numeric_guard_accepts_digit_form_when_proposition_uses_words(monkeypatch):
    """C4 Round 4 defect THẬT (Maxi Trial F011, xem C4_REPAIR_ROUND4_REPORT.md
    Phần 11 mục 3): proposition ghi số bằng CHỮ ("Mười chín") trong khi
    prose/source_span dùng CHỮ SỐ ("19") -- guard PHẢI đọc cả source_spans
    (nguyên văn, đã validate tồn tại thật), không chỉ proposition, để
    tránh false positive do khác biệt định dạng của CÙNG 1 nguồn thật."""
    fact = StoryFact(fact_id="F001", proposition="Mười chín án chung thân được tuyên.", source_spans=["19 án chung thân"])
    pack = _pack(facts=[fact])
    bindings = [{"segment_id": "S1", "fact_ids": ["F001"], "prose": "19 án chung thân đã được tuyên.", "pack_hash_at_generation": pack.pack_hash()}]
    assert spg.run_deterministic_guards(bindings, pack) == []


def test_guards_defer_to_integrity_violations_first():
    pack = _pack(facts=[StoryFact(fact_id="F001", proposition="A.", source_spans=["A"])])
    bindings = [{"segment_id": "S1", "fact_ids": ["F999"], "prose": "999 số bịa.", "pack_hash_at_generation": pack.pack_hash()}]
    violations = spg.run_deterministic_guards(bindings, pack)
    assert "F999" in violations[0]  # integrity violation, không phải KeyError crash


# --------------------------------------------------------------- run_drift_detector

def test_drift_detector_cumulative_context_across_segments(monkeypatch):
    """C4 Round 4 defect THẬT (Maxi Trial S2 smoke test đầu tiên): segment
    sau có thể quy chiếu ngược thực thể đã giới thiệu ở segment trước --
    scope phải CỘNG DỒN theo thứ tự plan, không chỉ fact riêng segment đó."""
    seen_core_facts = []

    def fake_c4(prose, candidate):
        seen_core_facts.append([f.fact_id for f in candidate.core_facts])
        import cl_risk_gate as g
        return g.CriterionResult(criterion_id="C4", passed=True, evidence="ok", checked_by="test")

    monkeypatch.setattr(spg, "_score_c4_adversarial_text", fake_c4)
    pack = _pack(facts=[
        StoryFact(fact_id="F001", proposition="Phiên tòa khai mạc.", source_spans=["Phiên tòa khai mạc"]),
        StoryFact(fact_id="F002", proposition="Thẩm phán X đứng đầu.", source_spans=["Thẩm phán X đứng đầu"]),
    ])
    bindings = [
        {"segment_id": "S1", "fact_ids": ["F001"], "prose": "Phiên tòa khai mạc.", "pack_hash_at_generation": pack.pack_hash()},
        {"segment_id": "S2", "fact_ids": ["F002"], "prose": "Thẩm phán X đứng đầu.", "pack_hash_at_generation": pack.pack_hash()},
    ]
    spg.run_drift_detector(bindings, pack)
    assert seen_core_facts[0] == ["F001"]
    assert seen_core_facts[1] == ["F001", "F002"]  # cộng dồn, không phải chỉ ["F002"]


def test_drift_detector_fails_closed_on_integrity_violation_without_calling_c4(monkeypatch):
    calls = []
    monkeypatch.setattr(spg, "_score_c4_adversarial_text", lambda *a: calls.append(1))
    pack = _pack(facts=[StoryFact(fact_id="F001", proposition="A.", source_spans=["A"])])
    bindings = [{"segment_id": "S1", "fact_ids": ["F999"], "prose": "bịa.", "pack_hash_at_generation": pack.pack_hash()}]
    results = spg.run_drift_detector(bindings, pack)
    assert not results[0].passed
    assert not calls  # KHÔNG gọi C4 trên dữ liệu không xác định được nguồn gốc


# ------------------------------------------------- Kenneth Lay legal-status trap

def test_kenneth_lay_vacated_conviction_regression(monkeypatch):
    """C4 Round 5 blind THẬT (Enron/Kenneth Lay, xem
    C4_ROUND5_BLIND_VALIDATION_REPORT.md Phần 4): bẫy pháp lý tinh vi nhất
    trong bộ 5 topic blind -- Kenneth Lay bị bồi thẩm đoàn tuyên có tội,
    nhưng bản án sau đó bị HỦY BỎ hoàn toàn do ông qua đời trước khi tuyên
    án (học thuyết đình chỉ tố tụng do tử vong). Fact pack THẬT tách 2
    giai đoạn pháp lý thành 2 fact ĐỘC LẬP (F013 kết tội, F015 hủy bỏ) --
    regression test này khóa lại: nếu script CHỈ nói 'Kenneth Lay bị kết
    tội' mà KHÔNG có ngữ cảnh hủy bỏ đi kèm dù fact hủy bỏ đã được chọn
    cho 1 segment KHÁC, drift detector (cộng dồn scope) KHÔNG được coi đó
    là drift -- 2 fact cùng tồn tại trong ground truth cộng dồn."""
    facts = [
        StoryFact(fact_id="F013", proposition="Ngày 25 tháng 5 năm 2006, Kenneth Lay bị kết tội 10 tội danh gian lận, âm mưu và khai gian với ngân hàng.",
                  source_spans=["Kenneth Lay bị kết tội 10 tội danh gian lận, âm mưu, và khai gian với ngân hàng ngày 25/5/2006"], risk_class="legal_status"),
        StoryFact(fact_id="F014", proposition="Kenneth Lay qua đời vì bệnh tim ngày 5 tháng 7 năm 2006, trước khi bị tuyên án.",
                  source_spans=["qua đời vì bệnh tim ngày 5/7/2006, trước khi bị tuyên án"], risk_class="legal_status"),
        StoryFact(fact_id="F015", proposition="Theo học thuyết đình chỉ tố tụng do tử vong, một thẩm phán liên bang tại Houston đã ra lệnh hủy bỏ toàn bộ kết luận có tội của Kenneth Lay.",
                  source_spans=["một thẩm phán liên bang tại Houston sau đó đã ra lệnh hủy bỏ toàn bộ kết luận có tội của Lay"], risk_class="legal_status"),
    ]
    pack = _pack(topic_id="ENRON", facts=facts)
    bindings = [
        {"segment_id": "S1", "fact_ids": ["F013", "F014"], "prose": "Ngày 25 tháng 5 năm 2006, Kenneth Lay bị kết tội 10 tội danh gian lận, âm mưu và khai gian với ngân hàng, nhưng đã qua đời vì bệnh tim vào ngày 5 tháng 7 năm 2006 trước khi bị tuyên án.", "pack_hash_at_generation": pack.pack_hash()},
        {"segment_id": "S2", "fact_ids": ["F015"], "prose": "Sau khi Kenneth Lay qua đời, một thẩm phán liên bang tại Houston đã ra lệnh hủy bỏ toàn bộ kết luận có tội của ông theo học thuyết đình chỉ tố tụng do tử vong.", "pack_hash_at_generation": pack.pack_hash()},
    ]

    def fake_c4(prose, candidate):
        import cl_risk_gate as g
        core_texts = " ".join(f.statement for f in candidate.core_facts)
        # Mô phỏng C4 THẬT: câu chỉ PASS nếu nội dung của nó được core_facts hỗ trợ.
        passed = "hủy bỏ" not in prose or "hủy bỏ" in core_texts
        return g.CriterionResult(criterion_id="C4", passed=passed, evidence="mô phỏng", checked_by="test")

    monkeypatch.setattr(spg, "_score_c4_adversarial_text", fake_c4)
    results = spg.run_drift_detector(bindings, pack)
    assert all(r.passed for r in results), f"Kịch bản THẬT (đúng bẫy Kenneth Lay) không được bị chặn nhầm: {results}"

    # Mutation đối kháng: nếu ai đó XOÁ fact F015 khỏi binding S2 (giả lập
    # 'quên' đưa fact hủy bỏ vào ground truth) -- câu nói 'hủy bỏ' PHẢI bị
    # chặn vì không còn fact nào hỗ trợ, đúng ý nghĩa câu này KHÔNG ĐƯỢC
    # xuất hiện tự do nếu fact tương ứng chưa được chọn.
    tampered = [dict(bindings[0]), {"segment_id": "S2", "fact_ids": [], "prose": bindings[1]["prose"], "pack_hash_at_generation": pack.pack_hash()}]
    tampered_results = spg.run_drift_detector(tampered, pack)
    assert not tampered_results[-1].passed


# --------------------------------------------------- Boy in the Box regression

def test_boy_in_the_box_no_injected_victim_name_regression(monkeypatch):
    """C4 Round 5 blind THẬT ("Boy in the Box", Philadelphia 1957, xem
    C4_ROUND5_BLIND_VALIDATION_REPORT.md Phần 4): DOMAIN_GUIDE.md §6 cấm
    tuyệt đối nêu tên nạn nhân vị thành niên, không có ngoại lệ. Fact pack
    THẬT chỉ dùng "bé trai"/"em" (excerpt nguồn không chứa tên) -- test
    này khóa lại: model KHÔNG ĐƯỢC tự thêm tên từ kiến thức nền (vụ án đã
    lên tin quốc tế 2022) dù fact_id không hề chứa tên đó. Mô phỏng: nếu
    prose 'lỡ' chèn 1 tên riêng không có trong core_facts, drift detector
    PHẢI coi đó là UNSUPPORTED."""
    fact = StoryFact(fact_id="F020", proposition="Ngày 8/12/2022, Sở Cảnh sát Philadelphia công bố danh tính bé trai đã được xác định qua hồ sơ khai sinh.",
                      source_spans=["Sở Cảnh sát Philadelphia chính thức công bố danh tính đứa trẻ"], risk_class="legal_status")
    pack = _pack(topic_id="BOY_IN_BOX", facts=[fact])
    clean_binding = [{"segment_id": "S1", "fact_ids": ["F020"], "prose": "Ngày 8/12/2022, cảnh sát Philadelphia công bố danh tính bé trai đã được xác định qua hồ sơ khai sinh.", "pack_hash_at_generation": pack.pack_hash()}]
    injected_name_binding = [{"segment_id": "S1", "fact_ids": ["F020"], "prose": "Ngày 8/12/2022, cảnh sát Philadelphia công bố bé trai tên là Joseph Augustus Zarelli.", "pack_hash_at_generation": pack.pack_hash()}]

    def fake_c4(prose, candidate):
        import cl_risk_gate as g
        core_texts = " ".join(f.statement for f in candidate.core_facts)
        # Mô phỏng: tên riêng xuất hiện trong prose mà KHÔNG có trong core_facts -> UNSUPPORTED.
        passed = "Zarelli" not in prose or "Zarelli" in core_texts
        return g.CriterionResult(criterion_id="C4", passed=passed, evidence="mô phỏng -- tên không có trong fact", checked_by="test")

    monkeypatch.setattr(spg, "_score_c4_adversarial_text", fake_c4)
    assert all(r.passed for r in spg.run_drift_detector(clean_binding, pack))
    assert not all(r.passed for r in spg.run_drift_detector(injected_name_binding, pack))
