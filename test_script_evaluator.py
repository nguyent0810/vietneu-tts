"""Script evaluator shadow (ticket 17): đúng một lần gọi, 4 phần tách riêng có
evidence, không điểm tổng; shadow không bao giờ đổi Gate status; invariant LLM
không ghi đè trường code/story_plan; Source không đủ; không có finding CR-1."""
import json
import sys

import pytest

import content_invariant as ci
import content_quality_gate as cqg
import script_evaluator as se
import script_quality_gate as sqg
import short_judge_panel_engine as engine
import zodiac_short_generator as zsg

def _gate_records(domain):
    """Record tầng Content/Script (bỏ record catalog advisory ghi sau S7)."""
    return [r for r in cqg.read_records(domain) if r["layer"] != "catalog"]


SCRIPT = "Hôm nay tuổi Tý gặp quý nhân.\nNgày Canh Tý được xem là thuận hoà.\nChúc bạn an yên."
INV = ci.build(claim_source_kind="generator_facts", claim_source_data={"day_can_chi": "Canh Tý"})

GOOD = {
    "invariant": {"content_hook": {"value": "tuổi Tý gặp quý nhân", "evidence": ["tuổi Tý gặp quý nhân"]},
                  "idea_order": {"value": ["hook", "lý do", "chúc"], "evidence": ["Hôm nay", "Ngày Canh Tý"]},
                  "payoff": {"value": "chúc an yên", "evidence": ["Chúc bạn an yên."]}},
    "fidelity": {"findings": [
        {"type": "new_claim", "script_span": "gặp quý nhân", "source_span": None, "certainty": "medium"},
        {"type": "cr1_certainty", "script_span": "chắc chắn", "source_span": None, "certainty": "high"},
    ]},
    "hook_span": "tuổi Tý gặp quý nhân",
    "opening_pattern": {"description": "khẳng định thẳng con giáp may mắn", "evidence": "Hôm nay tuổi Tý gặp quý nhân."},
}


@pytest.fixture
def evaluator_on(monkeypatch):
    monkeypatch.setenv(se.ENV, "1")
    calls = []

    def run(prompt, payload=GOOD):
        calls.append(prompt)
        return json.dumps(payload, ensure_ascii=False)
    monkeypatch.setattr(se, "_run_codex", run)
    return calls


def _gate(script=SCRIPT, inv=INV):
    return sqg.evaluate(script, domain="FS", identity={"content_id": "X_01"}, invariant=inv,
                        content_quality_record_id="c1")


def test_exactly_one_call_with_four_separate_parts_and_evidence(evaluator_on):
    gate = _gate()
    assert len(evaluator_on) == 1
    ev = _gate_records("FS")[-1]["evaluator"]
    assert ev["model"] == se.EVALUATOR_MODEL and ev["shadow"] is True and ev["status"] == "ok"
    assert set(ev["invariant_derived"]) == {"content_hook", "idea_order", "payoff"}
    assert ev["invariant_derived"]["content_hook"]["evidence"] == ["tuổi Tý gặp quý nhân"]
    assert ev["fidelity"]["status"] == "checked"
    assert ev["opening_pattern"]["description"] and ev["opening_pattern"]["evidence"]
    assert ev["hook"] == {"span": "tuổi Tý gặp quý nhân", "words_before_hook": 2,
                          "seconds_before_hook": {"170wpm": 0.71, "200wpm": 0.6}}
    assert "score" not in json.dumps(ev)
    assert gate.publishable


def test_fidelity_findings_are_shadow_and_never_change_gate_status(evaluator_on):
    gate = _gate()
    rec = _gate_records("FS")[-1]
    findings = rec["evaluator"]["fidelity"]["findings"]
    assert [f["type"] for f in findings] == ["new_claim"] and all(f["shadow"] for f in findings)
    assert rec["gate_status"] == cqg.PASS and rec["reason_codes"] == [] and gate.publishable


def test_cr1_or_unknown_finding_types_are_dropped_not_counted(evaluator_on):
    _gate()
    ev = _gate_records("FS")[-1]["evaluator"]
    assert all(f["type"] != "cr1_certainty" for f in ev["fidelity"]["findings"])
    assert ev["dropped_findings"][0]["type"] == "cr1_certainty"


def test_llm_invariant_fills_missing_fields_but_never_overwrites_code_or_story_plan(evaluator_on):
    inv = ci.build(claim_source_kind="k", claim_source_data={"f": 1},
                   content_hook=ci.derived("hook từ story plan", "story_plan", ["S1"]))
    gate = _gate(inv=inv)
    merged = gate.extra["invariant"]
    assert merged["content_hook"]["derived_by"] == "story_plan" and merged["content_hook"]["value"] == "hook từ story plan"
    assert merged["idea_order"]["derived_by"] == "llm" and merged["payoff"]["derived_by"] == "llm"
    assert merged["missing"] == []
    assert ci.sufficiency(merged) == (True, [])


def test_no_claim_source_means_fidelity_source_insufficient(evaluator_on):
    _gate(inv=ci.build(claim_source_kind="k", claim_source_data=None))
    assert _gate_records("FS")[-1]["evaluator"]["fidelity"] == {"status": se.SOURCE_INSUFFICIENT}


def test_invalid_hook_span_is_recorded_not_guessed(evaluator_on, monkeypatch):
    payload = dict(GOOD, hook_span="cụm không có trong kịch bản")
    monkeypatch.setattr(se, "_run_codex", lambda p: json.dumps(payload, ensure_ascii=False))
    _gate()
    hook = _gate_records("FS")[-1]["evaluator"]["hook"]
    assert "error" in hook and "words_before_hook" not in hook


@pytest.mark.parametrize("bad", ["không phải json", json.dumps({"fidelity": {"findings": []}}), json.dumps([1])])
def test_evaluator_error_or_bad_structure_is_recorded_and_does_not_block(evaluator_on, monkeypatch, bad):
    monkeypatch.setattr(se, "_run_codex", lambda p: bad)
    gate = _gate()
    ev = _gate_records("FS")[-1]["evaluator"]
    assert ev["status"] == "error" and ev["error"]
    assert gate.publishable and gate.decision.gate_status == cqg.PASS


def test_evaluator_llm_invariant_can_make_s8_fail_rewrite_eligible(evaluator_on):
    """Invariant chỉ có nguồn claim (code) + hook/thứ tự ý/Payoff do LLM trích ->
    đủ để Script rewrite (D83) khi S8 chặn."""
    repeat = "Hãy giữ tâm thế bình tĩnh.\nHãy giữ tâm thế bình tĩnh.\nChúc bạn an yên."
    gate = _gate(script=repeat)
    assert gate.decision.gate_status == cqg.FAIL and gate.decision.rewrite_eligible


def test_disabled_evaluator_makes_no_call(monkeypatch):
    monkeypatch.setenv(se.ENV, "0")
    monkeypatch.setattr(se, "_run_codex", lambda p: pytest.fail("evaluator tắt thì không được gọi"))
    _gate()
    assert "evaluator" not in _gate_records("FS")[-1]


def test_prompt_contains_claim_source_and_excludes_cr1(evaluator_on):
    _gate()
    prompt = evaluator_on[0]
    assert "Canh Tý" in prompt and SCRIPT.split("\n")[0] in prompt
    assert "KHÔNG báo lỗi về từ ngữ chắc chắn" in prompt


def test_zodiac_writes_evaluator_enriched_invariant(evaluator_on, tmp_path, monkeypatch):
    monkeypatch.setattr(zsg, "OUTPUT_DIR", tmp_path)
    monkeypatch.delenv("VIETNEU_SKIP_JUDGE_PANEL", raising=False)
    monkeypatch.setattr(engine, "_run_agy", lambda p: json.dumps(
        {"candidates": [{"strategy": s, "script": SCRIPT} for s in "ABC"]}, ensure_ascii=False))
    monkeypatch.setattr(engine, "_run_codex", lambda p: json.dumps(
        {"fact_check": {s: "PASS" for s in "ABC"}, "candidate_id": "A", "hook_score": 9, "feedback": "x"}))
    monkeypatch.setattr(sys, "argv", ["z.py", "--date", "2026-09-28"])
    assert zsg.main() == 0
    inv = ci.read_sidecar(next(tmp_path.glob("*_Short.txt")))
    assert inv["content_hook"]["derived_by"] == "llm" and inv["claim_source"]["kind"] == "generator_facts"
    script_rec = [r for r in _gate_records("FS") if r["layer"] == "script"][-1]
    assert script_rec["evaluator"]["status"] == "ok" and script_rec["opening_pattern"]["description"]
