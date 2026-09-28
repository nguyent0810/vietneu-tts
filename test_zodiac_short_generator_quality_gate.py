"""Generator 12 con giáp đi qua Content Quality Gate (S1) cho MỌI outcome,
kể cả khi FAIL (không có file script). agy/Codex được giả lập ở cấp hàm gọi
CLI của engine judge panel (`_run_agy` / `_run_codex`)."""
import json
import sys

import pytest

import content_quality_gate as cqg
import short_judge_panel_engine as engine
import zodiac_short_generator as zsg

CANDIDATES = {"candidates": [
    {"strategy": "A", "script": "3 con giáp **Tuổi Thân**, **Tuổi Tý**, **Tuổi Thìn** được xem là thuận hoà hôm nay."},
    {"strategy": "B", "script": "**Tuổi Ngọ** nên thận trọng hôm nay."},
    {"strategy": "C", "script": "Hôm nay con giáp nào may mắn nhất?"},
]}


def _verdict(winner="A", score=9, fact_check=None):
    script = next((c["script"] for c in CANDIDATES["candidates"] if c["strategy"] == winner), "")
    return {"fact_check": fact_check or {"A": "PASS", "B": "PASS", "C": "PASS"}, "candidate_id": winner,
            "winner_script": script, "hook_score": score, "feedback": "ok"}


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.setenv(cqg.STORE_DIR_ENV, str(tmp_path / "qr"))
    monkeypatch.setattr(zsg, "OUTPUT_DIR", tmp_path / "staged")
    monkeypatch.delenv("VIETNEU_SKIP_JUDGE_PANEL", raising=False)
    monkeypatch.setattr(engine, "_run_agy", lambda prompt: json.dumps(CANDIDATES, ensure_ascii=False))
    monkeypatch.setattr(sys, "argv", ["zodiac_short_generator.py", "--date", "2026-09-28"])
    return tmp_path


def _set_judge(monkeypatch, responses):
    it = iter(responses)
    monkeypatch.setattr(engine, "_run_codex", lambda prompt: next(it))


def _records():
    return cqg.read_records("FS")


def test_pass_writes_script_and_a_pass_record(env, monkeypatch):
    _set_judge(monkeypatch, [json.dumps(_verdict("A", 9), ensure_ascii=False)])
    assert zsg.main() == 0
    staged = list((env / "staged").glob("*_Short.txt"))
    assert len(staged) == 1
    rec = _records()[-1]
    assert rec["gate_status"] == cqg.PASS
    assert rec["identity"]["content_id"] == "CONGIAP20260928_ConGiap_01"
    assert staged[0].name == "CONGIAP20260928_ConGiap_Short.txt"
    assert rec["identity"]["generator"] == "zodiac_short_generator"
    assert rec["facts"]["day_can_chi"]
    assert rec["versions"]["generator_version"] and rec["versions"]["prompt_version"]
    assert rec["versions"]["judge_model"] == cqg.JUDGE_MODEL_JUDGE_PANEL
    assert rec["script"] in staged[0].read_text(encoding="utf-8")


def test_no_factcheck_pass_still_records_fail_without_script_file(env, monkeypatch):
    none = json.dumps(_verdict("NONE", 0, {"A": "FAIL: x", "B": "FAIL: y", "C": "FAIL: z"}), ensure_ascii=False)
    _set_judge(monkeypatch, [none, none, none])
    assert zsg.main() == 1
    assert not (env / "staged").exists() or not list((env / "staged").glob("*"))
    rec = _records()[-1]
    assert rec["gate_status"] == cqg.FAIL
    assert rec["reason_codes"] == [cqg.ACC_NO_CANDIDATE_PASSED_FACTCHECK]
    assert len(rec["candidates"]) == 9


def test_below_threshold_records_needs_review_and_writes_nothing(env, monkeypatch):
    low = json.dumps(_verdict("A", 6), ensure_ascii=False)
    _set_judge(monkeypatch, [low, low, low])
    assert zsg.main() == 1
    assert not list((env / "staged").glob("*")) if (env / "staged").exists() else True
    assert _records()[-1]["reason_codes"][0] == cqg.JUDGE_BELOW_HOOK_THRESHOLD


def test_judge_errors_and_rejected_verdicts_are_recorded(env, monkeypatch):
    rejected = json.dumps({"candidate_id": "Z"})  # JSON hợp lệ nhưng verdict sai → bị từ chối
    calls = iter(["không phải json", rejected, rejected])
    monkeypatch.setattr(engine, "_run_codex", lambda prompt: next(calls))
    assert zsg.main() == 1
    rec = _records()[-1]
    assert rec["gate_status"] == cqg.FAIL
    assert set(rec["reason_codes"]) == {cqg.JUDGE_CALL_ERROR, cqg.JUDGE_VERDICT_REJECTED}


def test_generate_error_every_round_is_recorded(env, monkeypatch):
    monkeypatch.setattr(engine, "_run_agy", lambda prompt: "{}")
    _set_judge(monkeypatch, [])
    assert zsg.main() == 1
    assert _records()[-1]["reason_codes"] == [cqg.JUDGE_GENERATE_ERROR]


def test_record_write_failure_blocks_script_file(env, monkeypatch, tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    monkeypatch.setenv(cqg.STORE_DIR_ENV, str(blocker / "qr"))
    _set_judge(monkeypatch, [json.dumps(_verdict("A", 9), ensure_ascii=False)])
    assert zsg.main() == 1
    assert not (env / "staged").exists() or not list((env / "staged").glob("*"))


def test_bypass_is_recorded_as_needs_review_and_writes_nothing(env, monkeypatch):
    monkeypatch.setenv("VIETNEU_SKIP_JUDGE_PANEL", "1")
    _set_judge(monkeypatch, [])
    assert zsg.main() == 1
    rec = _records()[-1]
    assert (rec["gate_status"], rec["reason_codes"], rec["bypass"]) == (cqg.NEEDS_REVIEW, [cqg.BYPASS_JUDGE], True)
