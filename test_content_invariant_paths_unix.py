"""Content invariant cho BUD runner và CL (ticket 15). Cần fcntl."""
import json
import sys
from types import SimpleNamespace as NS

import pytest

import cl_case_batch as batch
import cl_risk_gate as g
import cl_risk_gate_orchestrator as orch
import cl_story_fact_pack as fp
import cl_story_plan_and_generation as spg
import content_invariant as ci
import criminal_law_short_generator as clgen
import short_batch_runner as sbr
import short_judge_panel_engine as engine


def test_bud_runner_writes_source_excerpt_before_review(tmp_path, monkeypatch):
    reg = tmp_path / "registry.json"
    reg.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(sbr, "_registry_path", lambda t: reg)
    seg = {"key": "EP9_Short_03", "episode": "EP9_Short", "segment_index": 3, "text": "Đoạn trích gốc của tập Long."}
    seen = {}

    def review(text, **k):
        seen["invariant"] = ci.read_json(ci.segment_sidecar_path(tmp_path / "out" / seg["episode"], 3))
        return {"final_script": None, "passed": False, "hook_score": None, "rounds_used": 0, "round_history": [],
                "needs_human_review": True}
    monkeypatch.setattr(sbr, "review_and_optimize_short", review)
    sbr.process_one_segment(seg, tmp_path / "out", "c.json", [], {}, None, 8, True, sbr.DEFAULT_TOPIC)
    inv = seen["invariant"]
    assert inv is not None, "invariant phải có TRƯỚC khi review viết lại"
    assert inv["source_excerpt"] == seg["text"] and inv["claim_source"] is None
    assert inv["versions"]["long_source"] == seg["episode"]
    assert ci.sufficiency(inv)[1] == ["thiếu content_hook", "thiếu idea_order", "thiếu payoff"]


def _pack_plan_bindings():
    pack = fp.StoryFactPack(topic_id="T1", source_file="s.md", excerpt_hash="h", ledger_version_at_build="v",
                            facts=[fp.StoryFact(fact_id="F001", proposition="P1"), fp.StoryFact(fact_id="F002", proposition="P2")])
    plan = spg.StoryPlan(topic_id="T1", fact_pack_hash=pack.pack_hash(), segments=[
        spg.PlanSegment("S1", "HOOK", ["F001"]), spg.PlanSegment("S2", "BEAT", ["F002"]), spg.PlanSegment("S3", "PAYOFF", ["F001"])])
    bindings = [{"segment_id": s, "fact_ids": [], "prose": f"Văn {s}.", "pack_hash_at_generation": pack.pack_hash()}
                for s in ("S1", "S2", "S3")]
    return pack, plan, bindings


def test_story_plan_invariant_is_deterministic_story_plan():
    pack, plan, bindings = _pack_plan_bindings()
    inv = ci.from_story_plan(plan, bindings, pack)
    assert inv["content_hook"]["derived_by"] == "story_plan" and inv["content_hook"]["evidence"] == ["Văn S1."]
    assert [s["role"] for s in inv["idea_order"]["value"]] == ["HOOK", "BEAT", "PAYOFF"]
    assert inv["payoff"]["evidence"] == ["Văn S3."]
    assert inv["claim_source"]["data"] == [{"fact_id": "F001", "proposition": "P1"}, {"fact_id": "F002", "proposition": "P2"}]
    assert ci.sufficiency(inv) == (True, [])


def test_story_plan_without_hook_records_reason():
    pack, plan, bindings = _pack_plan_bindings()
    plan.segments = [s for s in plan.segments if s.role != "HOOK"]
    inv = ci.from_story_plan(plan, bindings, pack)
    assert {"field": "content_hook", "reason": "StoryPlan không có segment HOOK"} in inv["missing"]


def test_provenance_generator_writes_story_plan_invariant(tmp_path, monkeypatch):
    import criminal_law_provenance_generator as prov
    import criminal_law_storytelling_phase_a as S
    pack, plan, bindings = _pack_plan_bindings()
    txt = tmp_path / "ANDAXU_X_Short.txt"
    result = S.StorytellingPhaseAResult(True, None, "PASS", reviewed_script_hash="h", reviewed_editorial_hash="e")
    monkeypatch.setattr(prov, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(prov.cl_claim_ledger, "topic_id_from_source_file", lambda s: "T1")
    monkeypatch.setattr(prov, "compute_phase_a_result_provenance", lambda *a: (result, "Văn S1. Văn S2. Văn S3.", plan, bindings))
    monkeypatch.setattr(prov, "write_provenance_sidecars", lambda *a: (txt, tmp_path / "p.json", tmp_path / "b.json"))
    monkeypatch.setattr(prov, "write_topic_meta_sidecar", lambda *a: None)
    monkeypatch.setattr(prov, "write_storytelling_sidecar", lambda *a: tmp_path / "m.json")
    monkeypatch.setattr(prov.cl_story_fact_pack, "load_fact_pack", lambda topic_id: pack)
    status, _ = prov.run_one({"title": "X", "excerpt": "e", "source_file": "s.md"})
    assert status == "PASS"
    inv = ci.read_sidecar(txt)
    assert inv["content_hook"]["derived_by"] == "story_plan" and inv["versions"]["quality_record_id"]


def test_cl_legacy_generator_invariant(tmp_path, monkeypatch):
    monkeypatch.delenv("VIETNEU_SKIP_JUDGE_PANEL", raising=False)
    topic = {"title": "Vụ án", "excerpt": "Trích đoạn vụ án.", "source_file": "s.md"}
    monkeypatch.setattr(clgen, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(clgen, "next_unused_topic", lambda: dict(topic))
    monkeypatch.setattr(clgen, "mark_topic_used", lambda t: None)
    monkeypatch.setattr(clgen, "cl_topic_meta_sidecar_path", lambda ep, t: tmp_path / f"{ep}_Short.topic_meta.json")
    monkeypatch.setattr(sys, "argv", ["c.py"])
    monkeypatch.setattr(engine, "_run_agy", lambda p: json.dumps(
        {"candidates": [{"strategy": s, "script": f"Bản {s}."} for s in "ABC"]}, ensure_ascii=False))
    monkeypatch.setattr(engine, "_run_codex", lambda p: json.dumps(
        {"fact_check": {s: "PASS" for s in "ABC"}, "candidate_id": "A", "hook_score": 9, "feedback": "x"}))
    assert clgen.main() == 0
    inv = ci.read_sidecar(next(tmp_path.glob("ANDAXU_*_Short.txt")))
    assert inv["claim_source"]["kind"] == "topic_excerpt" and inv["source_excerpt"] == topic["excerpt"]


def test_cl_case_batch_invariant_has_core_facts(tmp_path, monkeypatch):
    cand = g.CandidateCase(case_id="c1", case_key="k", working_title="Vụ",
                           core_facts=[g.CoreFact(fact_id="F001", statement="S1", fact_type="event")])
    result = orch.CLGateResult()
    gen = NS(passed=True, final_script="Kịch bản cuối.", final_editorial={"title": "t"}, reason=None, seo_result={},
             script_result={"history": []})
    result.auto_selected.append((cand, gen, NS(evidence="PASS", reviewed_editorial_hash="h")))
    monkeypatch.setattr(batch.g, "load_source_tiers", lambda: {})
    monkeypatch.setattr(batch, "prepare_candidates", lambda limit, tiers: [])
    monkeypatch.setattr(batch.g.CaseLedger, "load", classmethod(lambda cls: None))
    monkeypatch.setattr(batch, "run_cl_case_gate", lambda c, l, d: result)
    monkeypatch.setattr(batch, "cl_metadata_sidecar_path", lambda ep, t: tmp_path / f"{ep}_Short.cl_meta.json")
    monkeypatch.setattr(sys, "argv", ["b.py", "--deficit", "1", "--out-dir", str(tmp_path)])
    assert batch.main() == 0
    inv = ci.read_sidecar(tmp_path / "CLGATE_c1_Short.txt")
    assert inv["claim_source"] == {"kind": "cl_core_facts",
                                   "data": [{"fact_id": "F001", "statement": "S1", "fact_type": "event"}]}
    assert inv["versions"]["case_id"] == "c1"
