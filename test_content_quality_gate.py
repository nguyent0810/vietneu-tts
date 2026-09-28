"""Test qua seam Content Quality Gate (S1): bảng ánh xạ source outcome → Gate
decision, kho Quality record append-only theo Domain, fail closed khi ghi
record lỗi. Chạy được trên Windows (không import code cần fcntl)."""
import json

import pytest

import content_quality_gate as cqg

CANDS = [{"strategy": "A", "script": "Câu A."}, {"strategy": "B", "script": "Câu B."}, {"strategy": "C", "script": "Câu C."}]


def _verdict(winner="A", score=9, fact_check=None):
    return {
        "fact_check": fact_check or {"A": "PASS", "B": "FAIL: bịa", "C": "PASS"},
        "candidate_id": winner, "winner_script": "Câu A." if winner != "NONE" else "",
        "hook_score": score, "feedback": "ok",
    }


def _engine(passed, script, history, hook_score=None, needs_human_review=None):
    return {"script": script, "passed": passed, "hook_score": hook_score, "iterations_used": len(history),
            "history": history, "needs_human_review": (not passed) if needs_human_review is None else needs_human_review}


def _outcome(raw, source=cqg.SOURCE_JUDGE_PANEL_ENGINE, domain="FS"):
    return cqg.SourceOutcome(source=source, domain=domain, raw=raw, content_id="X_01", category="GROUNDED_DATA",
                             generator="zodiac_short_generator", facts={"k": "v"},
                             versions={"generator_version": "g1", "prompt_version": "p1", "judge_model": "m"})


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setenv(cqg.STORE_DIR_ENV, str(tmp_path / "qr"))
    return tmp_path / "qr"


def test_pass_outcome_maps_to_pass_without_reason_codes():
    raw = _engine(True, "Câu A.", [{"round": 1, "candidates": CANDS, "verdict": _verdict()}], hook_score=9)
    d = cqg.decide(_outcome(raw))
    assert (d.gate_status, d.reason_codes, d.bypass, d.script) == (cqg.PASS, [], False, "Câu A.")


def test_no_candidate_passed_factcheck_is_fail_with_accuracy_code():
    history = [{"round": i, "candidates": CANDS, "verdict": _verdict("NONE", 0, {"A": "FAIL", "B": "FAIL", "C": "FAIL"})} for i in (1, 2, 3)]
    d = cqg.decide(_outcome(_engine(False, None, history)))
    assert d.gate_status == cqg.FAIL
    assert d.reason_codes == [cqg.ACC_NO_CANDIDATE_PASSED_FACTCHECK]
    assert len(d.evidence) == 3


def test_below_hook_threshold_is_needs_review_not_pass():
    history = [{"round": 1, "candidates": CANDS, "verdict": _verdict("A", 6)}]
    d = cqg.decide(_outcome(_engine(False, "Câu A.", history, hook_score=6)))
    assert d.gate_status == cqg.NEEDS_REVIEW
    assert d.reason_codes == [cqg.JUDGE_BELOW_HOOK_THRESHOLD]
    assert d.script == "Câu A."


def test_round_errors_and_rejected_verdicts_are_all_reported():
    history = [
        {"round": 1, "stage": "generate", "error": "agy timeout"},
        {"round": 2, "stage": "judge", "error": "codex exit 1"},
        {"round": 3, "stage": "judge_rejected", "error": "winner không hợp lệ"},
    ]
    d = cqg.decide(_outcome(_engine(False, None, history)))
    assert d.gate_status == cqg.FAIL
    assert d.reason_codes == [cqg.JUDGE_GENERATE_ERROR, cqg.JUDGE_CALL_ERROR, cqg.JUDGE_VERDICT_REJECTED]


def test_mixed_failures_keep_every_reason_code():
    history = [
        {"round": 1, "stage": "judge_rejected", "error": "x"},
        {"round": 2, "candidates": CANDS, "verdict": _verdict("NONE", 0)},
        {"round": 3, "stage": "generate", "error": "y"},
    ]
    d = cqg.decide(_outcome(_engine(False, None, history)))
    assert d.gate_status == cqg.FAIL
    assert set(d.reason_codes) == {cqg.JUDGE_VERDICT_REJECTED, cqg.ACC_NO_CANDIDATE_PASSED_FACTCHECK, cqg.JUDGE_GENERATE_ERROR}


def test_below_threshold_after_error_rounds_carries_round_codes():
    history = [{"round": 1, "stage": "generate", "error": "x"}, {"round": 2, "candidates": CANDS, "verdict": _verdict("A", 5)}]
    d = cqg.decide(_outcome(_engine(False, "Câu A.", history, hook_score=5)))
    assert d.gate_status == cqg.NEEDS_REVIEW
    assert d.reason_codes == [cqg.JUDGE_BELOW_HOOK_THRESHOLD, cqg.JUDGE_GENERATE_ERROR]


def test_bypass_outcome_is_needs_review_with_bypass_flag():
    raw = {"script": "Câu A.", "passed": True, "hook_score": None, "iterations_used": 1,
           "history": [{"round": 1, "candidates": CANDS, "skipped_judge": True}], "needs_human_review": False}
    d = cqg.decide(_outcome(raw))
    assert (d.gate_status, d.reason_codes, d.bypass) == (cqg.NEEDS_REVIEW, [cqg.BYPASS_JUDGE], True)
    assert not d.publishable


def test_unknown_source_is_unmapped_needs_review():
    d = cqg.decide(_outcome({"passed": True, "history": []}, source="nguồn_lạ"))
    assert (d.gate_status, d.reason_codes) == (cqg.NEEDS_REVIEW, [cqg.INTERNAL_UNMAPPED])


def test_unrecognised_engine_shape_is_unmapped_not_guessed():
    # passed=False, không có script, không có vòng lỗi nào: không map ngầm thành FAIL.
    d = cqg.decide(_outcome(_engine(False, None, [])))
    assert (d.gate_status, d.reason_codes) == (cqg.NEEDS_REVIEW, [cqg.INTERNAL_UNMAPPED])
    d2 = cqg.decide(_outcome({"foo": 1}))
    assert d2.reason_codes == [cqg.INTERNAL_UNMAPPED]


def test_passed_but_flagged_for_human_review_is_not_pass():
    raw = _engine(True, "Câu A.", [{"round": 1, "candidates": CANDS, "verdict": _verdict()}], needs_human_review=True)
    assert cqg.decide(_outcome(raw)).gate_status == cqg.NEEDS_REVIEW


def test_reason_codes_are_a_closed_set_with_group_prefixes():
    prefixes = ("ACC_", "SAF_", "STR_", "JUDGE_", "SRC_", "BYPASS_", "INTERNAL_", "SCR_")
    assert all(code.startswith(prefixes) for code in cqg.REASON_CODES)


def test_evaluate_appends_record_with_identity_versions_and_source_outcome(store):
    history = [{"round": 1, "candidates": CANDS, "verdict": _verdict("A", 6)}]
    raw = _engine(False, "Câu A.", history, hook_score=6)
    result = cqg.evaluate(_outcome(raw))
    assert result.record_error is None and not result.publishable
    records = cqg.read_records("FS")
    assert len(records) == 1
    rec = records[0]
    assert rec["schema_version"] == cqg.SCHEMA_VERSION
    assert rec["quality_record_id"] and rec["created_at"]
    assert rec["domain"] == "FS" and rec["layer"] == "content"
    assert rec["rubric_version"] == "legacy"
    assert rec["versions"] == {"generator_version": "g1", "prompt_version": "p1", "judge_model": "m"}
    assert rec["identity"]["content_id"] == "X_01" and rec["identity"]["category"] == "GROUNDED_DATA"
    assert rec["gate_status"] == cqg.NEEDS_REVIEW
    assert rec["reason_codes"] == [cqg.JUDGE_BELOW_HOOK_THRESHOLD]
    assert rec["source_outcome"] == {"source": cqg.SOURCE_JUDGE_PANEL_ENGINE, "raw": raw}
    assert rec["facts"] == {"k": "v"} and rec["script"] == "Câu A."
    # Mọi ứng viên, kèm fact-check và nhãn Hook formula, không chỉ ứng viên thắng.
    assert [(c["candidate_id"], c["hook_formula"], c["fact_check"], c["is_winner"]) for c in rec["candidates"]] == [
        ("A", "A", "PASS", True), ("B", "B", "FAIL: bịa", False), ("C", "C", "PASS", False)]
    assert rec["candidates"][0]["hook_score"] == 6


def test_fail_record_keeps_candidates_facts_and_timestamp_for_blind_labeling(store):
    history = [{"round": 1, "candidates": CANDS, "verdict": _verdict("NONE", 0)}]
    cqg.evaluate(_outcome(_engine(False, None, history)))
    rec = cqg.read_records("FS")[0]
    assert rec["gate_status"] == cqg.FAIL
    assert rec["script"] is None
    assert [c["script"] for c in rec["candidates"]] == ["Câu A.", "Câu B.", "Câu C."]
    assert rec["facts"] == {"k": "v"} and rec["created_at"]


def test_store_is_append_only_and_split_per_domain(store):
    raw = _engine(True, "Câu A.", [{"round": 1, "candidates": CANDS, "verdict": _verdict()}], hook_score=9)
    first = cqg.evaluate(_outcome(raw))
    before = (store / "FS.jsonl").read_bytes()
    second = cqg.evaluate(_outcome(raw))
    cqg.evaluate(_outcome(raw, domain="BUD"))
    after = (store / "FS.jsonl").read_bytes()
    assert after.startswith(before), "dòng cũ không được sửa"
    assert len(cqg.read_records("FS")) == 2 and len(cqg.read_records("BUD")) == 1
    assert first.record["quality_record_id"] != second.record["quality_record_id"]
    assert all(json.loads(line) for line in after.decode("utf-8").splitlines())


def test_invalid_domain_is_rejected():
    with pytest.raises(ValueError):
        cqg.store_path("XX")


def test_record_write_failure_fails_closed_without_raising(tmp_path, monkeypatch):
    blocker = tmp_path / "not_a_dir"
    blocker.write_text("file chặn đường tạo thư mục", encoding="utf-8")
    monkeypatch.setenv(cqg.STORE_DIR_ENV, str(blocker / "qr"))
    raw = _engine(True, "Câu A.", [{"round": 1, "candidates": CANDS, "verdict": _verdict()}], hook_score=9)
    result = cqg.evaluate(_outcome(raw))
    assert result.decision.gate_status == cqg.PASS
    assert result.record_error
    assert not result.publishable, "PASS nhưng không ghi được record thì không được Publish"


def test_importing_s1_does_not_pull_unix_only_lock_modules():
    import subprocess
    import sys
    code = ("import sys, content_quality_gate; "
            "bad = [m for m in ('fcntl', 'registry_lock', 'rotation_state') if m in sys.modules]; "
            "print(bad); sys.exit(1 if bad else 0)")
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                            cwd=str(__import__('pathlib').Path(cqg.__file__).parent))
    assert result.returncode == 0, result.stdout + result.stderr


def test_reader_skips_a_torn_line_instead_of_failing_the_whole_store(store):
    raw = _engine(True, "Câu A.", [{"round": 1, "candidates": CANDS, "verdict": _verdict()}], hook_score=9)
    cqg.evaluate(_outcome(raw))
    with open(store / "FS.jsonl", "a", encoding="utf-8") as fh:
        fh.write('{"quality_record_id": "torn", "domain": "F')  # lần ghi bị ngắt giữa chừng
    cqg.evaluate(_outcome(raw))
    records = cqg.read_records("FS")
    assert len(records) == 2, "record sau dòng hỏng vẫn đọc được"
    assert all(r.get("quality_record_id") != "torn" for r in records)


def test_every_test_uses_an_isolated_quality_record_store():
    """conftest.py (autouse) trỏ kho Quality record của MỌI test vào thư mục tạm:
    không test nào ghi vào output/quality_records thật."""
    assert cqg.store_dir() != cqg.DEFAULT_STORE_DIR
    assert "_quality_records" in str(cqg.store_dir())
