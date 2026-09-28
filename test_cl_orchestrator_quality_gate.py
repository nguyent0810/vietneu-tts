"""CL orchestrator escalation + generator criminal law đi qua Content Quality
Gate (S1) (ticket 05b). Mỗi loại escalation có reason code riêng và có
record; không còn outcome CL nào chỉ in ra màn hình."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import cl_case_batch as batch  # noqa: E402
import cl_risk_gate as g  # noqa: E402
import cl_risk_gate_orchestrator as orch  # noqa: E402
import content_quality_gate as cqg  # noqa: E402
import criminal_law_short_generator as clgen  # noqa: E402
import short_judge_panel_engine as engine  # noqa: E402


def _cand(case_id):
    return g.CandidateCase(case_id=case_id, case_key=f"k-{case_id}", working_title=f"Vụ {case_id}",
                           core_facts=[g.CoreFact(fact_id="F001", statement=f"Dữ kiện {case_id}", fact_type="event")],
                           risk_review_draft=f"Bản nháp {case_id}")


def _gen(script="Kịch bản [F001].", passed=True):
    return NS(passed=passed, final_script=script, final_editorial={"title": "t"}, reason=None if passed else "3 vòng NONE",
              script_result={"passed": passed}, seo_result={})


def _full_result():
    r = orch.CLGateResult()
    r.escalated_high.append((_cand("high"), NS(rationale="C1 fail", tier="HIGH")))
    r.escalated_medium_exhausted.append((_cand("medium"), NS(rationale="C3 thiếu", tier="MEDIUM")))
    r.rejected_duplicate.append((_cand("dup"), NS(evidence="trùng case X", verdict="SAME_EVENT")))
    r.escalated_low_confidence_dedupe.append((_cand("lowdedupe"), NS(evidence="không chắc", verdict=None)))
    r.escalated_claim_exposure_failed.append((_cand("claim"), NS(evidence="claim lộ", reason_code="CLAIM_X")))
    r.deferred_deficit.append(_cand("deferred"))
    r.escalated_generation_failed.append((_cand("genfail"), _gen(script=None, passed=False)))
    r.escalated_phase_a_review_failed.append((_cand("phasea"), _gen("Kịch bản bị chặn."),
                                              NS(evidence="C4 chặn câu 1", reason_code="PHASE_A_C4_FAILED")))
    r.auto_selected.append((_cand("ok"), _gen("Kịch bản tốt [F001]."), NS(evidence="PASS", reviewed_editorial_hash="h1")))
    return r


EXPECTED = {
    "high": (cqg.NEEDS_REVIEW, cqg.SAF_CL_ESCALATED_HIGH_RISK),
    "medium": (cqg.NEEDS_REVIEW, cqg.SAF_CL_ESCALATED_MEDIUM_RISK),
    "dup": (cqg.FAIL, cqg.SRC_CL_DUPLICATE_CASE),
    "lowdedupe": (cqg.NEEDS_REVIEW, cqg.SRC_CL_LOW_CONFIDENCE_DEDUPE),
    "claim": (cqg.FAIL, cqg.SAF_CL_CLAIM_EXPOSURE_FAILED),
    "deferred": (cqg.NEEDS_REVIEW, cqg.SRC_CL_DEFERRED_DEFICIT),
    "genfail": (cqg.FAIL, cqg.JUDGE_CL_GENERATION_FAILED),
    "phasea": (cqg.FAIL, cqg.ACC_CL_PHASE_A_REVIEW_FAILED),
}


def test_every_bucket_gets_a_record_with_its_own_reason_code():
    gates = orch.record_content_quality(_full_result())
    records = {r["identity"]["case_id"]: r for r in cqg.read_records("CL")}
    assert set(records) == set(EXPECTED) | {"ok"}
    for case_id, (status, code) in EXPECTED.items():
        rec = records[case_id]
        assert (rec["gate_status"], rec["reason_codes"]) == (status, [code]), case_id
        assert rec["identity"]["content_id"] == f"CLGATE_{case_id}_01"
        assert not gates[case_id].publishable
    assert records["ok"]["gate_status"] == cqg.PASS and gates["ok"].publishable
    assert records["phasea"]["script"] == "Kịch bản bị chặn."
    assert records["phasea"]["evidence"][0]["source_reason_code"] == "PHASE_A_C4_FAILED"
    assert records["high"]["facts"] == [{"fact_id": "F001", "statement": "Dữ kiện high"}]
    assert records["high"]["source_excerpt"] == "Bản nháp high"
    assert len({c for c, _ in EXPECTED.items()}) == len({code for _, code in EXPECTED.values()}), "mỗi loại một code"


def _run_batch(tmp_path, monkeypatch, result):
    monkeypatch.setattr(batch.g, "load_source_tiers", lambda: {})
    monkeypatch.setattr(batch, "prepare_candidates", lambda limit, tiers: [])
    monkeypatch.setattr(batch.g.CaseLedger, "load", classmethod(lambda cls: None))
    monkeypatch.setattr(batch, "run_cl_case_gate", lambda candidates, ledger, deficit: result)
    written = []
    monkeypatch.setattr(batch, "write_bundle_and_sidecar", lambda c, gen, rev, out: written.append(c.case_id) or tmp_path / "b")
    monkeypatch.setattr(sys, "argv", ["cl_case_batch.py", "--deficit", "1", "--out-dir", str(tmp_path / "out")])
    assert batch.main() == 0
    return written


def test_case_batch_records_all_outcomes_and_writes_only_pass_bundle(tmp_path, monkeypatch):
    written = _run_batch(tmp_path, monkeypatch, _full_result())
    assert written == ["ok"]
    assert len(cqg.read_records("CL")) == len(EXPECTED) + 1


def test_case_batch_record_write_failure_blocks_bundle(tmp_path, monkeypatch):
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    monkeypatch.setenv(cqg.STORE_DIR_ENV, str(blocker / "qr"))
    assert _run_batch(tmp_path, monkeypatch, _full_result()) == []


# --------------------------------------------------------------------------
# Generator criminal law (legacy, judge panel)
# --------------------------------------------------------------------------

TOPIC = {"title": "Vụ án xưa", "excerpt": "Trích đoạn nguồn.", "source_file": "RESEARCH_DRAFT_X.md"}


@pytest.fixture
def clgen_env(tmp_path, monkeypatch):
    monkeypatch.setattr(clgen, "OUTPUT_DIR", tmp_path / "staged")
    monkeypatch.setattr(clgen, "next_unused_topic", lambda: dict(TOPIC))
    monkeypatch.setattr(clgen, "mark_topic_used", lambda title: None)
    monkeypatch.setattr(clgen, "cl_topic_meta_sidecar_path", lambda ep, topic: tmp_path / "staged" / f"{ep}_Short.topic_meta.json")
    monkeypatch.setattr(sys, "argv", ["criminal_law_short_generator.py"])
    monkeypatch.delenv("VIETNEU_SKIP_JUDGE_PANEL", raising=False)
    monkeypatch.setattr(engine, "_run_agy", lambda p: json.dumps(
        {"candidates": [{"strategy": s, "script": f"Bản {s}."} for s in "ABC"]}, ensure_ascii=False))
    return tmp_path


def _verdict(winner, score):
    return json.dumps({"fact_check": {s: ("PASS" if winner != "NONE" else "FAIL: x") for s in "ABC"}, "winner": winner,
                       "winner_script": f"Bản {winner}." if winner != "NONE" else "", "hook_score": score,
                       "feedback": "x"}, ensure_ascii=False)


def test_criminal_law_generator_pass_records_and_writes(clgen_env, monkeypatch):
    monkeypatch.setattr(engine, "_run_codex", lambda p: _verdict("A", 9))
    assert clgen.main() == 0
    rec = cqg.read_records("CL")[-1]
    assert rec["gate_status"] == cqg.PASS and rec["identity"]["generator"] == "criminal_law_short_generator"
    assert rec["source_excerpt"] == TOPIC["excerpt"]
    staged = list((clgen_env / "staged").glob("ANDAXU_*_Short.txt"))
    assert [p.name[: -len("_Short.txt")] + "_01" for p in staged] == [rec["identity"]["content_id"]]


def test_criminal_law_generator_fail_still_records(clgen_env, monkeypatch):
    monkeypatch.setattr(engine, "_run_codex", lambda p: _verdict("NONE", 0))
    assert clgen.main() == 1
    rec = cqg.read_records("CL")[-1]
    assert (rec["gate_status"], rec["reason_codes"]) == (cqg.FAIL, [cqg.ACC_NO_CANDIDATE_PASSED_FACTCHECK])
    assert not list((clgen_env / "staged").glob("ANDAXU_*_Short.txt")) if (clgen_env / "staged").exists() else True
