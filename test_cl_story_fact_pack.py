"""Regression coverage cho cl_story_fact_pack.py -- khóa lại các defect
THẬT phát hiện qua C4 Repair Round 4/5 (xem handoff/C4_REPAIR_ROUND4_REPORT.md
+ handoff/C4_ROUND5_BLIND_VALIDATION_REPORT.md) trước khi tích hợp production
(Round 6). Mirror phong cách monkeypatch _run_codex đã dùng ở
test_criminal_law_storytelling_phase_a.py (module import làm S/F)."""
import json

import cl_story_fact_pack as F


def _fake_json(obj):
    return json.dumps(obj, ensure_ascii=False)


def test_span_must_exist_verbatim_in_excerpt(monkeypatch):
    """Fact có source_span KHÔNG tồn tại nguyên văn trong excerpt bị LOẠI
    khỏi pack -- fail-closed bằng cách EXCLUDE, không phải flag/warn."""
    monkeypatch.setattr(F, "_run_codex", lambda prompt: _fake_json({"facts": [
        {"proposition": "A xảy ra năm 1990.", "risk_class": "timeline", "material": True, "source_spans": ["A xảy ra năm 1990"]},
        {"proposition": "B bịa đặt hoàn toàn.", "risk_class": "ordinary", "material": True, "source_spans": ["B không có trong nguồn"]},
    ]}))
    pack = F.build_story_fact_pack("T1", "T1.md", "Đoạn văn: A xảy ra năm 1990. Sự kiện khác cũng xảy ra.")
    assert len(pack.facts) == 1
    assert pack.facts[0].proposition == "A xảy ra năm 1990."


def test_fact_with_unknown_risk_class_excluded(monkeypatch):
    monkeypatch.setattr(F, "_run_codex", lambda prompt: _fake_json({"facts": [
        {"proposition": "X thật.", "risk_class": "not_a_real_class", "material": True, "source_spans": ["X thật"]},
    ]}))
    pack = F.build_story_fact_pack("T2", "T2.md", "X thật.")
    assert len(pack.facts) == 0


def test_fact_missing_source_spans_excluded(monkeypatch):
    monkeypatch.setattr(F, "_run_codex", lambda prompt: _fake_json({"facts": [
        {"proposition": "Y thật.", "risk_class": "ordinary", "material": True, "source_spans": []},
    ]}))
    pack = F.build_story_fact_pack("T3", "T3.md", "Y thật.")
    assert len(pack.facts) == 0


def test_malformed_llm_response_raises(monkeypatch):
    monkeypatch.setattr(F, "_run_codex", lambda prompt: "not json {{{")
    import pytest
    with pytest.raises(Exception):
        F.build_story_fact_pack("T4", "T4.md", "excerpt bất kỳ")


def test_response_missing_facts_key_raises(monkeypatch):
    monkeypatch.setattr(F, "_run_codex", lambda prompt: _fake_json({"wrong_key": []}))
    import pytest
    with pytest.raises(ValueError):
        F.build_story_fact_pack("T5", "T5.md", "excerpt bất kỳ")


def test_self_contained_proposition_instruction_present_in_prompt():
    """C4 Round 4 defect #1 THẬT (Maxi Trial S2, 'đứng đầu nỗ lực NÀY' --
    xem C4_REPAIR_ROUND4_REPORT.md Phần 11 mục 2): fact tự nó chứa đại từ/
    từ chỉ định dangling khiến downstream (drift detector) không thể xác
    nhận được ngay cả khi văn xuôi trung thành 100%. Vá bằng PROMPT
    (không phải code cơ học -- không có cách nào cơ học chặn dangling
    reference sau khi LLM đã trích), nên regression test ở ĐÂY chỉ khóa
    lại việc HƯỚNG DẪN đó còn tồn tại trong prompt -- ngăn ai đó vô tình
    xoá mất hướng dẫn này khi sửa prompt sau này."""
    assert "tự đủ nghĩa" in F._FACT_EXTRACTION_PROMPT
    assert "đại từ" in F._FACT_EXTRACTION_PROMPT


def test_excerpt_hash_deterministic():
    h1 = F.excerpt_hash("Cùng 1 đoạn văn.")
    h2 = F.excerpt_hash("Cùng 1 đoạn văn.")
    h3 = F.excerpt_hash("Đoạn văn khác.")
    assert h1 == h2
    assert h1 != h3


def test_get_or_build_fact_pack_reuses_when_excerpt_unchanged(tmp_path, monkeypatch):
    monkeypatch.setattr(F, "STORY_FACT_PACK_DIR", tmp_path)
    calls = []

    def fake_build(topic_id, source_file, excerpt):
        calls.append(excerpt)
        return F.StoryFactPack(topic_id=topic_id, source_file=source_file, excerpt_hash=F.excerpt_hash(excerpt), ledger_version_at_build="v1", facts=[])

    monkeypatch.setattr(F, "build_story_fact_pack", fake_build)
    pack1 = F.get_or_build_fact_pack("T6", "T6.md", "excerpt A")
    pack2 = F.get_or_build_fact_pack("T6", "T6.md", "excerpt A")
    assert len(calls) == 1  # lần 2 tái dùng pack đã lưu, KHÔNG build lại
    assert pack1.pack_hash() == pack2.pack_hash()


def test_get_or_build_fact_pack_rebuilds_when_excerpt_changes(tmp_path, monkeypatch):
    """Bất biến tích hợp §7 THẬT: source excerpt đổi -> Fact Pack cũ trở
    nên stale -- KHÔNG được âm thầm dùng lại pack ứng với excerpt cũ."""
    monkeypatch.setattr(F, "STORY_FACT_PACK_DIR", tmp_path)
    calls = []

    def fake_build(topic_id, source_file, excerpt):
        calls.append(excerpt)
        return F.StoryFactPack(topic_id=topic_id, source_file=source_file, excerpt_hash=F.excerpt_hash(excerpt), ledger_version_at_build="v1", facts=[])

    monkeypatch.setattr(F, "build_story_fact_pack", fake_build)
    F.get_or_build_fact_pack("T7", "T7.md", "excerpt A")
    F.get_or_build_fact_pack("T7", "T7.md", "excerpt B (đã sửa research draft)")
    assert calls == ["excerpt A", "excerpt B (đã sửa research draft)"]


def test_high_risk_fact_verified_when_ledger_matches(monkeypatch):
    """external_status tính đúng qua tái dùng cl_claim_ledger._find_ledger_
    match/_claim_tier -- fact rủi ro cao khớp entry VERIFIED P0/P1 trong
    ledger được gắn external_status=VERIFIED (tín hiệu sớm cho plan, KHÔNG
    phải quyết định publish cuối -- xem docstring module)."""
    monkeypatch.setattr(F, "_run_codex", lambda prompt: _fake_json({"facts": [
        {"proposition": "Ông X bị kết án 5 năm tù.", "risk_class": "legal_status", "material": True, "source_spans": ["Ông X bị kết án 5 năm tù"]},
    ]}))
    import cl_risk_gate as g
    fake_ledger = {"T8": [{"claim_id": "C1", "claim": "Ông X bị kết án 5 năm tù.", "normalized_claim": "ông x bị kết án 5 năm tù", "status": "VERIFIED", "risk_class": "legal_status", "provenance": [{"source_url": "https://apnews.com/x"}]}]}
    monkeypatch.setattr(F.L, "load_claim_ledger", lambda: fake_ledger)
    monkeypatch.setattr(F.L, "load_source_tiers", lambda: {})
    monkeypatch.setattr(F.L, "ledger_version", lambda: "v_test")
    monkeypatch.setattr(F.L, "_claim_tier", lambda entry, tiers: g.PublisherTier.REPUTABLE_PRESS)
    pack = F.build_story_fact_pack("T8", "T8.md", "Ông X bị kết án 5 năm tù.")
    assert len(pack.facts) == 1
    assert pack.facts[0].external_status == "VERIFIED"
    assert pack.facts[0].external_claim_id == "C1"


def test_high_risk_fact_unverified_when_no_ledger_match(monkeypatch):
    monkeypatch.setattr(F, "_run_codex", lambda prompt: _fake_json({"facts": [
        {"proposition": "Ông Y bị bắt vì tội gian lận.", "risk_class": "allegation", "material": True, "source_spans": ["Ông Y bị bắt vì tội gian lận"]},
    ]}))
    monkeypatch.setattr(F.L, "load_claim_ledger", lambda: {})
    monkeypatch.setattr(F.L, "load_source_tiers", lambda: {})
    monkeypatch.setattr(F.L, "ledger_version", lambda: "v_test")
    pack = F.build_story_fact_pack("T9", "T9.md", "Ông Y bị bắt vì tội gian lận.")
    assert pack.facts[0].external_status == "UNVERIFIED"
    assert pack.facts[0].external_claim_id is None
