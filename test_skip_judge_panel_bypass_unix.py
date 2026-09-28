"""VIETNEU_SKIP_JUDGE_PANEL=1 ở BUD (runner) và CL (generator criminal law,
case pipeline): Gate status Needs review + BYPASS_JUDGE + bypass flag, không
bao giờ "scripted", không tới TTS/upload (ticket 06, D49). Cần fcntl."""
import json
import sys
from types import SimpleNamespace as NS

import pytest

import cl_case_generation as clcg
import cl_risk_gate as g
import cl_risk_gate_orchestrator as orch
import content_quality_gate as cqg
import criminal_law_short_generator as clgen
import short_batch_runner as sbr
import short_judge_panel_engine as engine

CANDS = {"candidates": [{"strategy": s, "script": f"Bản {s}. Câu hai."} for s in "ABC"]}


@pytest.fixture
def bypass(monkeypatch):
    monkeypatch.setenv("VIETNEU_SKIP_JUDGE_PANEL", "1")
    monkeypatch.setattr(engine, "_run_agy", lambda p: json.dumps(CANDS, ensure_ascii=False))
    monkeypatch.setattr(engine, "_run_codex", lambda p: pytest.fail("bypass không gọi judge"))


def _assert_bypass_record(domain):
    rec = cqg.read_records(domain)[-1]
    assert (rec["gate_status"], rec["reason_codes"], rec["bypass"]) == (cqg.NEEDS_REVIEW, [cqg.BYPASS_JUDGE], True)
    return rec


def test_bud_runner_bypass_never_scripted_never_tts(bypass, tmp_path, monkeypatch):
    reg = tmp_path / "registry.json"
    reg.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(sbr, "_registry_path", lambda t: reg)
    monkeypatch.setattr(sbr, "run_tts", lambda *a, **k: pytest.fail("bypass không được tới TTS"))
    monkeypatch.setattr(sbr, "upload_short", lambda *a, **k: pytest.fail("bypass không được upload"))
    seg = {"key": "EP001_Short_01", "episode": "EP001_Short", "segment_index": 1, "text": "Câu gốc. Câu hai."}
    entry = sbr.process_one_segment(seg, tmp_path / "out", "c.json", [], {}, None, 8, False, sbr.DEFAULT_TOPIC)
    assert entry["status"] == "needs_review"
    assert entry["content_gate_reason_codes"] == [cqg.BYPASS_JUDGE]
    _assert_bypass_record("BUD")


def test_cl_legacy_generator_bypass(bypass, tmp_path, monkeypatch):
    monkeypatch.setattr(clgen, "OUTPUT_DIR", tmp_path / "staged")
    monkeypatch.setattr(clgen, "next_unused_topic", lambda: {"title": "Vụ", "excerpt": "e", "source_file": "s.md"})
    monkeypatch.setattr(clgen, "mark_topic_used", lambda t: pytest.fail("không đánh dấu đã dùng"))
    monkeypatch.setattr(sys, "argv", ["clgen.py"])
    assert clgen.main() == 1
    _assert_bypass_record("CL")
    assert not (tmp_path / "staged").exists() or not list((tmp_path / "staged").glob("*_Short.txt"))


def test_cl_case_pipeline_bypass_stops_before_seo_and_is_needs_review(bypass, monkeypatch):
    monkeypatch.setattr(clcg, "generate_cl_seo", lambda *a, **k: pytest.fail("bypass không được tới SEO"))
    cand = g.CandidateCase(case_id="c1", case_key="k1", working_title="Vụ 1",
                           core_facts=[g.CoreFact(fact_id="F001", statement="s", fact_type="event")])
    gen = clcg.generate_cl_final_content(cand)
    assert gen.passed is False and gen.reason == "JUDGE_BYPASSED"
    result = orch.CLGateResult()
    result.escalated_generation_failed.append((cand, gen))
    gates = orch.record_content_quality(result)
    assert not gates["c1"].publishable
    _assert_bypass_record("CL")


def test_orchestrator_auto_selected_with_bypassed_script_is_not_pass():
    """Phòng thủ theo chiều sâu: kể cả nếu một bản bypass lọt tới auto_selected,
    S1 vẫn không cho PASS."""
    cand = g.CandidateCase(case_id="c2", case_key="k2", working_title="Vụ 2")
    gen = NS(passed=True, final_script="x", final_editorial={}, reason=None, seo_result={},
             script_result={"history": [{"round": 1, "skipped_judge": True}]})
    result = orch.CLGateResult()
    result.auto_selected.append((cand, gen, NS(evidence="PASS", reviewed_editorial_hash="h")))
    gates = orch.record_content_quality(result)
    assert not gates["c2"].publishable
    _assert_bypass_record("CL")
