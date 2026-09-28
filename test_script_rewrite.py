"""Script rewrite contract + deterministic invariant guard (ticket 18): một lần
viết lại cho finding S8, guard token claim, vi phạm = đổi Content, qua guard
thì chạy lại S1 + S7, không retry loop."""
import json
import sys

import pytest

import content_invariant as ci
import content_quality_gate as cqg
import script_quality_gate as sqg
import script_rewrite as sr
import short_judge_panel_engine as engine
import zodiac_short_generator as zsg

INV = ci.build(claim_source_kind="generator_facts",
               claim_source_data={"day_can_chi": "Canh Tý", "hop": ["Thân", "Tý", "Thìn"], "ngay": "25/07"},
               content_hook=ci.derived("3 con giáp", "llm"), idea_order=ci.derived([1, 2], "llm"),
               payoff=ci.derived("chúc", "llm"))
ORIGINAL = ("Ngày 25/07 là ngày Canh Tý.\nTuổi Thân, Tý, Thìn được xem là thuận hoà.\n"
            "Tuổi Thân, Tý, Thìn được xem là thuận hoà.\nChúc bạn an yên.")
FIXED = "Ngày 25/07 là ngày Canh Tý.\nTuổi Thân, Tý, Thìn được xem là thuận hoà.\nChúc bạn một ngày an yên."


# --- Guard (hàm thuần) -----------------------------------------------------

def test_guard_passes_when_claim_tokens_are_kept():
    assert sr.guard(ORIGINAL, FIXED, INV)["passed"]


@pytest.mark.parametrize("rewritten,key,value", [
    (FIXED.replace("25/07", "26/07"), "new_numbers", ["26/07"]),
    (FIXED.replace("Canh Tý", "Tân Sửu"), "missing_terms", ["canh"]),
    (FIXED.replace("Thìn", "Tuất"), "missing_terms", ["thìn"]),
    (FIXED + "\nCó 3 điều cần nhớ.", "new_numbers", ["3"]),
    (FIXED.replace("Ngày 25/07 là ngày Canh Tý.\n", ""), "missing_numbers", ["25/07"]),
])
def test_guard_catches_changed_numbers_names_and_terms(rewritten, key, value):
    g = sr.guard(ORIGINAL, rewritten, INV)
    assert not g["passed"]
    assert set(value) <= set(g[key]), g


def test_contract_names_only_the_flagged_sentences_and_the_invariant():
    gate = sqg.evaluate(ORIGINAL, domain="FS", identity={"content_id": "X_01"}, invariant=INV, content_quality_record_id="c")
    contract = sr.build_contract(ORIGINAL, gate.integrity, INV)
    assert contract["sentences_to_fix"] == [2]
    assert contract["findings"][0]["reason_code"] == cqg.SCR_REPEATED_SENTENCE
    assert contract["invariant"]["claim_source"]["data"]["day_can_chi"] == "Canh Tý"
    prompt = sr.build_prompt(contract)
    assert "CHỈ sửa các câu đó" in prompt and "câu 3" in prompt


# --- Luồng attempt ----------------------------------------------------------

def _s7(script=ORIGINAL, inv=INV):
    return sqg.evaluate(script, domain="FS", identity={"content_id": "X_01"}, invariant=inv, content_quality_record_id="c")


def _recheck_pass(new_script):
    raw = {"script": new_script, "passed": True, "hook_score": 9, "needs_human_review": False,
           "history": [{"round": 1, "candidates": [{"strategy": "A", "script": new_script}],
                        "verdict": {"fact_check": {"A": "PASS"}, "candidate_id": "A", "hook_score": 9}}]}
    return cqg.evaluate(cqg.SourceOutcome(source=cqg.SOURCE_JUDGE_PANEL_ENGINE, domain="FS", raw=raw, content_id="X_01"))


def test_valid_rewrite_reruns_s1_and_s7_and_is_publishable():
    calls = []
    result = sr.attempt(_s7(), script=ORIGINAL, invariant=INV, recheck_content=_recheck_pass,
                        writer=lambda p: calls.append(p) or json.dumps({"script": FIXED}, ensure_ascii=False))
    assert len(calls) == 1, "đúng một lần viết lại"
    assert result.outcome == sr.OUTCOME_REWRITTEN and result.publishable and result.script == FIXED
    rec = result.record
    assert rec["rewrite"]["before"] == ORIGINAL and rec["rewrite"]["after"] == FIXED
    assert rec["rewrite"]["guard"]["passed"] and rec["gate_status"] == cqg.PASS
    assert rec["rewrite"]["recheck"]["content_gate_status"] == cqg.PASS
    assert rec["rewrite"]["recheck"]["script_gate_status"] == cqg.PASS
    assert rec["rewrite"]["invariant_compare"]["shadow"] is True


def test_guard_violation_is_content_change_back_to_content_gate():
    result = sr.attempt(_s7(), script=ORIGINAL, invariant=INV, recheck_content=lambda s: pytest.fail("không recheck"),
                        writer=lambda p: json.dumps({"script": FIXED.replace("25/07", "26/07")}, ensure_ascii=False))
    assert result.outcome == sr.OUTCOME_CONTENT_CHANGED and not result.publishable
    assert result.record["reason_codes"] == [cqg.SCR_REWRITE_CHANGED_CONTENT]
    assert result.record["gate_status"] == cqg.NEEDS_REVIEW


def test_writer_failure_is_needs_review_without_retry():
    calls = []

    def writer(p):
        calls.append(p)
        return "không phải json"
    result = sr.attempt(_s7(), script=ORIGINAL, invariant=INV, recheck_content=lambda s: pytest.fail("x"), writer=writer)
    assert len(calls) == 1 and result.outcome == sr.OUTCOME_WRITER_ERROR
    assert result.record["reason_codes"] == [cqg.SCR_REWRITE_FAILED] and not result.publishable


def test_rewrite_that_still_fails_s8_is_not_retried():
    still_bad = "Ngày 25/07 là ngày Canh Tý.\nTuổi Thân, Tý, Thìn thuận hoà.\nTuổi Thân, Tý, Thìn thuận hoà."
    calls = []
    result = sr.attempt(_s7(), script=ORIGINAL, invariant=INV, recheck_content=_recheck_pass,
                        writer=lambda p: calls.append(p) or json.dumps({"script": still_bad}, ensure_ascii=False))
    assert len(calls) == 1 and result.outcome == sr.OUTCOME_RECHECK_FAILED and not result.publishable


def test_incomplete_invariant_means_no_rewrite():
    partial = ci.build(claim_source_kind="k", claim_source_data={"x": 1})
    gate = _s7(inv=partial)
    result = sr.attempt(gate, script=ORIGINAL, invariant=partial, recheck_content=lambda s: pytest.fail("x"),
                        writer=lambda p: pytest.fail("không được viết lại"))
    assert result.outcome == sr.OUTCOME_NOT_ELIGIBLE and gate.decision.gate_status == cqg.NEEDS_REVIEW


# --- Qua generator zodiac ----------------------------------------------------

def test_zodiac_rewrites_once_and_writes_the_rewritten_script(tmp_path, monkeypatch):
    import script_evaluator as se
    monkeypatch.setattr(zsg, "OUTPUT_DIR", tmp_path)
    monkeypatch.delenv("VIETNEU_SKIP_JUDGE_PANEL", raising=False)
    monkeypatch.setenv(se.ENV, "1")
    facts = zsg.compute_zodiac_facts(__import__("datetime").date(2026, 9, 28))
    hop = [h["animal"] for h in facts["hop_animals"]]
    bad = f"Hôm nay ngày {facts['day_can_chi']}.\nTuổi {hop[0]} thuận hoà.\nTuổi {hop[0]} thuận hoà.\nChúc bạn an yên."
    good = f"Hôm nay ngày {facts['day_can_chi']}.\nTuổi {hop[0]} thuận hoà.\nChúc bạn một ngày an yên."
    monkeypatch.setattr(engine, "_run_agy", lambda p: json.dumps(
        {"candidates": [{"strategy": s, "script": bad} for s in "ABC"]}, ensure_ascii=False))
    monkeypatch.setattr(engine, "_run_codex", lambda p: json.dumps(
        {"fact_check": {s: "PASS" for s in "ABC"}, "candidate_id": "A", "hook_score": 9, "feedback": "x"}))
    monkeypatch.setattr(se, "_run_codex", lambda p: json.dumps({
        "invariant": {"content_hook": {"value": "h", "evidence": []}, "idea_order": {"value": ["a"], "evidence": []},
                      "payoff": {"value": "p", "evidence": []}},
        "fidelity": {"findings": []}, "hook_span": None, "opening_pattern": None}))
    writes = []
    monkeypatch.setattr(sr, "_run_agy", lambda p: writes.append(p) or json.dumps({"script": good}, ensure_ascii=False))
    monkeypatch.setattr(sys, "argv", ["z.py", "--date", "2026-09-28"])
    assert zsg.main() == 0
    assert len(writes) == 1
    assert good in next(tmp_path.glob("*_Short.txt")).read_text(encoding="utf-8")
    rewrite_rec = [r for r in cqg.read_records("FS") if r.get("rewrite")][-1]
    assert rewrite_rec["rewrite"]["outcome"] == sr.OUTCOME_REWRITTEN


def test_guard_catches_a_changed_proper_name_taken_from_the_claim_source():
    """Review 18: tên riêng lấy từ nguồn claim (không thuộc DOMAIN_TERMS)."""
    inv = ci.build(claim_source_kind="k", claim_source_data={"nhan_vat": "Nguyễn Trãi"})
    original = "Nguyễn Trãi viết Bình Ngô đại cáo.\nNguyễn Trãi viết Bình Ngô đại cáo."
    rewritten = "Lê Lợi viết Bình Ngô đại cáo."
    g = sr.guard(original, rewritten, inv)
    assert not g["passed"] and {"nguyễn", "trãi"} <= set(g["missing_terms"])
    assert sr.guard(original, "Nguyễn Trãi viết Bình Ngô đại cáo.", inv)["passed"]


def test_llm_invariant_compare_uses_fresh_extractions_of_both_scripts(monkeypatch):
    """Review 18: so sánh phần evaluator trích MỚI trên bản gốc vs bản viết lại."""
    import script_evaluator as se
    monkeypatch.setenv(se.ENV, "1")
    hooks = iter(["móc bản gốc", "móc bản viết lại"])

    def fake(prompt):
        return json.dumps({"invariant": {"content_hook": {"value": next(hooks), "evidence": []},
                                         "idea_order": {"value": ["a"], "evidence": []},
                                         "payoff": {"value": "p", "evidence": []}},
                           "fidelity": {"findings": []}, "hook_span": None, "opening_pattern": None},
                          ensure_ascii=False)
    monkeypatch.setattr(se, "_run_codex", fake)
    result = sr.attempt(_s7(), script=ORIGINAL, invariant=INV, recheck_content=_recheck_pass,
                        writer=lambda p: json.dumps({"script": FIXED}, ensure_ascii=False))
    cmp = result.record["rewrite"]["invariant_compare"]
    assert cmp["status"] == "compared" and cmp["shadow"] is True
    assert cmp["fields"] == {"content_hook": "different", "idea_order": "same", "payoff": "same"}
    assert result.publishable, "so sánh shadow không đổi kết quả"


def test_rewrite_audit_record_write_failure_is_not_publishable(monkeypatch):
    orig = cqg.append_record

    def fail_rewrite_audit(record):
        if record.get("rewrite"):
            raise cqg.QualityRecordWriteError("đĩa đầy")
        return orig(record)
    monkeypatch.setattr(cqg, "append_record", fail_rewrite_audit)
    result = sr.attempt(_s7(), script=ORIGINAL, invariant=INV, recheck_content=_recheck_pass,
                        writer=lambda p: json.dumps({"script": FIXED}, ensure_ascii=False))
    assert result.outcome == sr.OUTCOME_REWRITTEN and not result.publishable
