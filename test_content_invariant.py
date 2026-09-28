"""Content invariant (S6, ticket 13): schema sidecar, lý do thiếu, đủ-để-rewrite,
nối qua generator zodiac (nguồn claim = đúng facts đã đưa cho writer)."""
import json
import sys

import pytest

import content_invariant as ci
import short_judge_panel_engine as engine
import zodiac_short_generator as zsg


def test_schema_has_every_field_and_missing_reasons():
    inv = ci.build(claim_source_kind="generator_facts", claim_source_data={"a": 1}, versions={"v": "1"})
    assert inv["schema_version"] == ci.SCHEMA_VERSION
    assert inv["claim_source"] == {"kind": "generator_facts", "data": {"a": 1}}
    assert inv["source_excerpt"] is None
    assert {m["field"] for m in inv["missing"]} == {"content_hook", "idea_order", "payoff"}
    assert all(m["reason"] for m in inv["missing"])
    assert "content_hook" not in inv, "trường thiếu không được bỏ trống lặng lẽ -- nằm trong missing"


def test_derived_fields_carry_derived_by_and_evidence():
    hook = ci.derived("3 con giáp hợp", "llm", ["3 con giáp **Tuổi Thân**"])
    inv = ci.build(claim_source_kind="k", claim_source_data={}, content_hook=hook,
                   idea_order=ci.derived(["HOOK", "PAYOFF"], "story_plan"), payoff=ci.derived("chúc", "code"))
    assert inv["content_hook"] == {"value": "3 con giáp hợp", "derived_by": "llm", "evidence": ["3 con giáp **Tuổi Thân**"]}
    assert inv["missing"] == []
    with pytest.raises(ValueError):
        ci.derived("x", "guess")


def test_sufficiency_for_rewrite():
    full = ci.build(claim_source_kind="k", claim_source_data={"f": 1}, content_hook=ci.derived("h", "llm"),
                    idea_order=ci.derived([1], "llm"), payoff=ci.derived("p", "llm"))
    assert ci.sufficiency(full) == (True, [])
    ok, reasons = ci.sufficiency(ci.build(claim_source_kind="k", claim_source_data={"f": 1}))
    assert not ok and set(reasons) == {"thiếu content_hook", "thiếu idea_order", "thiếu payoff"}
    ok, reasons = ci.sufficiency(ci.build(claim_source_kind="k", claim_source_data=None,
                                          content_hook=ci.derived("h", "llm"), idea_order=ci.derived([1], "llm"),
                                          payoff=ci.derived("p", "llm")))
    assert not ok and reasons == ["thiếu nguồn claim"]
    assert ci.sufficiency(None) == (False, ["không có Content invariant"])


def test_sidecar_roundtrip_next_to_bundle(tmp_path):
    bundle = tmp_path / "CONGIAP20260928_ConGiap_Short.txt"
    inv = ci.build(claim_source_kind="k", claim_source_data={"x": "ý"})
    path = ci.write_sidecar(bundle, inv)
    assert path.name == "CONGIAP20260928_ConGiap_Short.invariant.json"
    assert ci.read_sidecar(bundle) == inv
    assert ci.read_sidecar(tmp_path / "KHAC_Short.txt") is None
    with pytest.raises(ValueError):
        ci.sidecar_path(tmp_path / "abc.txt")


CANDS = {"candidates": [{"strategy": s, "script": f"Bản {s}. Câu hai."} for s in "ABC"]}


@pytest.fixture
def zodiac(tmp_path, monkeypatch):
    monkeypatch.setattr(zsg, "OUTPUT_DIR", tmp_path / "staged")
    monkeypatch.delenv("VIETNEU_SKIP_JUDGE_PANEL", raising=False)
    monkeypatch.setattr(engine, "_run_agy", lambda p: json.dumps(CANDS, ensure_ascii=False))
    monkeypatch.setattr(sys, "argv", ["zodiac_short_generator.py", "--date", "2026-09-28"])
    return tmp_path


def _judge(monkeypatch, winner):
    monkeypatch.setattr(engine, "_run_codex", lambda p: json.dumps(
        {"fact_check": {s: ("PASS" if winner != "NONE" else "FAIL: x") for s in "ABC"}, "candidate_id": winner,
         "hook_score": 9, "feedback": "x"}, ensure_ascii=False))


def test_zodiac_writes_invariant_with_the_exact_facts_given_to_writer(zodiac, monkeypatch):
    seen = {}
    real_generate = engine.generate_candidates

    def spy(facts, *a, **k):
        seen["facts"] = facts
        return real_generate(facts, *a, **k)
    monkeypatch.setattr(engine, "generate_candidates", spy)
    _judge(monkeypatch, "A")
    assert zsg.main() == 0
    bundle = next((zodiac / "staged").glob("*_Short.txt"))
    inv = ci.read_sidecar(bundle)
    assert inv["claim_source"] == {"kind": "generator_facts", "data": seen["facts"]}
    assert {m["field"] for m in inv["missing"]} == {"content_hook", "idea_order", "payoff"}
    assert inv["versions"]["quality_record_id"]


def test_zodiac_fail_writes_no_orphan_sidecar(zodiac, monkeypatch):
    _judge(monkeypatch, "NONE")
    assert zsg.main() == 1
    staged = zodiac / "staged"
    assert not staged.exists() or not list(staged.glob("*.invariant.json"))
