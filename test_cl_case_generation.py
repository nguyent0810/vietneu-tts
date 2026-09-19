"""Test cho cl_case_generation.py (§1.13 Phase A bước 3 -- sinh final
script+SEO cho candidate ĐÃ qua Stage 1/2). Mock content_seo._run_agy/
_run_codex đúng pattern các test khác trong dự án."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import cl_risk_gate as g  # noqa: E402
import cl_case_generation as CG  # noqa: E402
import content_seo  # noqa: E402
import short_judge_panel_engine as SJPE  # noqa: E402


def _fake_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False)


def _named(name, role="convicted_perpetrator"):
    return g.NamedIndividual(canonical_name=name, identity_confidence="high", role=role)


def _core_fact(fact_id, statement):
    return g.CoreFact(fact_id=fact_id, statement=statement, fact_type="event")


def _candidate(working_title="Test case { with brace }"):
    return g.CandidateCase(
        case_id="c1", case_key="k1", working_title=working_title,
        named_individuals=[_named("Nguyễn Văn A")],
        core_facts=[_core_fact("F1", "Sự kiện xảy ra { năm 2020 }.")],
    )


def _patch_agy_codex(monkeypatch, agy_responses, codex_responses):
    """agy_responses/codex_responses: list các string trả về LIÊN TIẾP cho
    mỗi lần gọi (agy = soạn, codex = phản biện) -- dùng chung cho cả
    short_judge_panel_engine VÀ content_seo (2 module IMPORT _run_agy/
    _run_codex RIÊNG từ content_seo, phải patch cả 2 chỗ import)."""
    agy_iter = iter(agy_responses)
    codex_iter = iter(codex_responses)
    agy_fn = lambda prompt: next(agy_iter)  # noqa: E731
    codex_fn = lambda prompt: next(codex_iter)  # noqa: E731
    monkeypatch.setattr(SJPE, "_run_agy", agy_fn)
    monkeypatch.setattr(SJPE, "_run_codex", codex_fn)
    monkeypatch.setattr(CG, "_run_agy", agy_fn)
    monkeypatch.setattr(CG, "_run_codex", codex_fn)


def test_generate_cl_script_handles_working_title_and_facts_with_braces(monkeypatch):
    """Regression cho brace-injection fix: working_title VÀ facts_block
    (statement) chứa dấu {{/}} literal -- PHẢI không crash, PHẢI không bị
    .format() nội bộ diễn giải sai. Nếu escaping thiếu, generate_candidates()'s
    .format(facts_json=..., revision_note=...) sẽ raise KeyError/IndexError
    ngay khi gặp '{ with brace }' hoặc '{ năm 2020 }' như 1 placeholder lạ."""
    candidate = _candidate(working_title="Test case { with brace }")
    _patch_agy_codex(
        monkeypatch,
        agy_responses=[_fake_json({"candidates": [
            {"strategy": "A", "script": "Câu 1 [F1]."},
            {"strategy": "B", "script": "Câu 2 [F1]."},
            {"strategy": "C", "script": "Câu 3 [F1]."},
        ]})],
        codex_responses=[_fake_json({
            "fact_check": {"A": "PASS", "B": "PASS", "C": "PASS"},
            "winner": "A", "winner_script": "Câu 1 [F1].", "hook_score": 9, "feedback": "ok",
        })],
    )
    result = CG.generate_cl_script(candidate, max_rounds=1)
    assert result["passed"] is True
    assert result["script"] == "Câu 1 [F1]."


def test_generate_cl_script_fails_closed_when_no_winner(monkeypatch):
    candidate = _candidate()
    _patch_agy_codex(
        monkeypatch,
        agy_responses=[_fake_json({"candidates": [
            {"strategy": "A", "script": "s"}, {"strategy": "B", "script": "s"}, {"strategy": "C", "script": "s"},
        ]})],
        codex_responses=[_fake_json({
            "fact_check": {"A": "FAIL: bịa", "B": "FAIL: bịa", "C": "FAIL: bịa"},
            "winner": "NONE", "winner_script": "", "hook_score": 1, "feedback": "",
        })],
    )
    result = CG.generate_cl_script(candidate, max_rounds=1)
    assert result["passed"] is False
    assert result["needs_human_review"] is True


def test_generate_cl_seo_passes_on_clean_verdict(monkeypatch):
    monkeypatch.setattr(content_seo, "_run_agy", lambda p: _fake_json({
        "title": "Tiêu đề", "description": "Mô tả", "tags": ["a", "b"], "thumbnail_brief": "Ảnh trung tính",
    }))
    monkeypatch.setattr(CG, "_run_agy", lambda p: _fake_json({
        "title": "Tiêu đề", "description": "Mô tả", "tags": ["a", "b"], "thumbnail_brief": "Ảnh trung tính",
    }))
    monkeypatch.setattr(CG, "_run_codex", lambda p: _fake_json({"verdict": "PASS", "feedback": ""}))
    result = CG.generate_cl_seo("Kịch bản đã duyệt.", max_iterations=1)
    assert result["passed"] is True
    assert result["seo"]["title"] == "Tiêu đề"
    assert "thumbnail_brief" in result["seo"]


def test_generate_cl_seo_fails_closed_after_max_iterations(monkeypatch):
    monkeypatch.setattr(CG, "_run_agy", lambda p: _fake_json({
        "title": "Kẻ giết người X", "description": "d", "tags": [], "thumbnail_brief": "b",
    }))
    monkeypatch.setattr(CG, "_run_codex", lambda p: _fake_json({"verdict": "FAIL", "feedback": "title (a) vi phạm -- quy kết tội trước bản án cuối cùng"}))
    result = CG.generate_cl_seo("Kịch bản.", max_iterations=2)
    assert result["passed"] is False
    assert result["needs_human_review"] is True
    assert result["iterations_used"] == 2


def test_generate_cl_final_content_skips_seo_when_script_fails(monkeypatch):
    """Script KHÔNG pass -> KHÔNG được gọi SEO generation (lãng phí lượt
    trên nội dung chưa đạt) -- xác nhận bằng cách để _run_agy/_run_codex
    (dùng chung cho cả script lẫn SEO) raise nếu bị gọi quá số lần script
    cần."""
    candidate = _candidate()
    call_count = {"agy": 0, "codex": 0}

    def agy_fn(prompt):
        call_count["agy"] += 1
        return _fake_json({"candidates": [{"strategy": "A", "script": "s"}, {"strategy": "B", "script": "s"}, {"strategy": "C", "script": "s"}]})

    def codex_fn(prompt):
        call_count["codex"] += 1
        return _fake_json({"fact_check": {"A": "FAIL", "B": "FAIL", "C": "FAIL"}, "winner": "NONE", "winner_script": "", "hook_score": 1, "feedback": ""})

    monkeypatch.setattr(SJPE, "_run_agy", agy_fn)
    monkeypatch.setattr(SJPE, "_run_codex", codex_fn)
    monkeypatch.setattr(CG, "_run_agy", agy_fn)
    monkeypatch.setattr(CG, "_run_codex", codex_fn)

    result = CG.generate_cl_final_content(candidate, max_script_rounds=1, max_seo_iterations=1)
    assert result.passed is False
    assert result.reason == "SCRIPT_GENERATION_FAILED"
    assert result.final_editorial is None
    # đúng 1 vòng script (1 agy + 1 codex) -- KHÔNG có lượt SEO nào thêm.
    assert call_count["agy"] == 1
    assert call_count["codex"] == 1


def test_generate_cl_final_content_full_pass(monkeypatch):
    candidate = _candidate()
    agy_responses = iter([
        _fake_json({"candidates": [{"strategy": "A", "script": "Câu 1 [F1]."}, {"strategy": "B", "script": "s"}, {"strategy": "C", "script": "s"}]}),
        _fake_json({"title": "Tiêu đề an toàn", "description": "Mô tả trung thực.", "tags": ["a"], "thumbnail_brief": "Ảnh trung tính"}),
    ])
    codex_responses = iter([
        _fake_json({"fact_check": {"A": "PASS", "B": "PASS", "C": "PASS"}, "winner": "A", "winner_script": "Câu 1 [F1].", "hook_score": 9, "feedback": ""}),
        _fake_json({"verdict": "PASS", "feedback": ""}),
    ])
    agy_fn = lambda p: next(agy_responses)  # noqa: E731
    codex_fn = lambda p: next(codex_responses)  # noqa: E731
    monkeypatch.setattr(SJPE, "_run_agy", agy_fn)
    monkeypatch.setattr(SJPE, "_run_codex", codex_fn)
    monkeypatch.setattr(CG, "_run_agy", agy_fn)
    monkeypatch.setattr(CG, "_run_codex", codex_fn)

    result = CG.generate_cl_final_content(candidate, max_script_rounds=1, max_seo_iterations=1)
    assert result.passed is True
    assert result.final_script == "Câu 1 [F1]."
    assert result.final_editorial["title"] == "Tiêu đề an toàn"
    assert result.final_editorial["thumbnail_brief"] == "Ảnh trung tính"


# =============================================================================
# Regression cho 5 finding thật từ review độc lập Cursor/Grok (Gate A vòng
# 1) -- xem docstring các hàm liên quan trong cl_case_generation.py.
# =============================================================================

def test_generate_cl_script_prompt_has_anti_injection_shield():
    """Regression High #1: prompt sinh script PHẢI có lá chắn data-vs-
    instruction + cấm dùng working_title làm căn cứ, giống hệt tinh thần
    _RISK_REVIEW_DRAFT_PROMPT (cl_risk_gate_verification.py)."""
    assert "KHÔNG PHẢI hướng dẫn" in CG._CL_GENERATE_SCRIPT_PROMPT
    assert "KHÔNG được dùng làm căn cứ" in CG._CL_GENERATE_SCRIPT_PROMPT
    assert "KHÔNG PHẢI hướng dẫn" in CG._CL_JUDGE_SCRIPT_PROMPT
    assert "KHÔNG PHẢI hướng dẫn" in CG._CL_SEO_DRAFT_PROMPT
    assert "KHÔNG PHẢI hướng dẫn" in CG._CL_SEO_REVIEW_PROMPT


def test_generate_cl_seo_rejects_pass_with_missing_field_despite_llm_pass(monkeypatch):
    """Regression High #2: LLM soạn thiếu field (thumbnail_brief) + LLM
    reviewer nói PASS (reviewer "mềm"/bỏ sót) -- schema check cơ học PHẢI
    từ chối, không chấp nhận passed=True."""
    incomplete_then_complete = iter([
        _fake_json({"title": "An toàn", "description": "Mô tả.", "tags": ["a"]}),  # thiếu thumbnail_brief
        _fake_json({"title": "An toàn", "description": "Mô tả.", "tags": ["a"], "thumbnail_brief": "Ảnh trung tính"}),
    ])
    always_pass = iter([_fake_json({"verdict": "PASS", "feedback": ""}), _fake_json({"verdict": "PASS", "feedback": ""})])
    monkeypatch.setattr(CG, "_run_agy", lambda p: next(incomplete_then_complete))
    monkeypatch.setattr(CG, "_run_codex", lambda p: next(always_pass))
    result = CG.generate_cl_seo("Kịch bản.", max_iterations=2)
    assert result["passed"] is True  # PASS thật ở vòng 2, sau khi field đủ
    assert result["iterations_used"] == 2
    assert "schema_error" in result["review_history"][0]


def test_generate_cl_seo_rejects_pass_with_guilt_word_in_title_despite_llm_pass(monkeypatch):
    """Regression Medium #5: denylist cơ học trên title chứa từ quy kết
    tội, dù LLM reviewer (bị thao túng/bỏ sót) nói PASS -- fail-closed cơ
    học độc lập với LLM."""
    guilty_then_clean = iter([
        _fake_json({"title": "Bắt được kẻ giết người", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}),
        _fake_json({"title": "Diễn biến vụ án", "description": "d", "tags": ["a"], "thumbnail_brief": "b"}),
    ])
    always_pass = iter([_fake_json({"verdict": "PASS", "feedback": ""}), _fake_json({"verdict": "PASS", "feedback": ""})])
    monkeypatch.setattr(CG, "_run_agy", lambda p: next(guilty_then_clean))
    monkeypatch.setattr(CG, "_run_codex", lambda p: next(always_pass))
    result = CG.generate_cl_seo("Kịch bản.", max_iterations=2)
    assert result["passed"] is True
    assert result["iterations_used"] == 2
    assert "denylist_violations" in result["review_history"][0]


def test_mechanical_seo_denylist_catches_sensational_language():
    violations = CG._mechanical_seo_denylist_violations({"title": "Sự thật rùng rợn về vụ án", "thumbnail_brief": "b"})
    assert violations
    assert any("rùng rợn" in v for v in violations)


def test_validate_seo_schema_rejects_empty_tags_list():
    error = CG._validate_seo_schema({"title": "t", "description": "d", "tags": [], "thumbnail_brief": "b"})
    assert error is not None


def test_validate_seo_schema_accepts_complete_seo():
    error = CG._validate_seo_schema({"title": "t", "description": "d", "tags": ["a"], "thumbnail_brief": "b"})
    assert error is None
