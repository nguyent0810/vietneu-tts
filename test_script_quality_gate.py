"""S7 Script Quality Gate (ticket 14): chạy ngay sau S1, ghi record
`layer: script` vào cùng kho Quality record, chỉ S8 có quyền chặn, chẩn đoán
không làm đổi Gate status, invariant không đủ -> Needs review khi cần rewrite."""
import json
import sys

import pytest

import content_invariant as ci
import content_quality_gate as cqg
import script_quality_gate as sqg
import short_judge_panel_engine as engine
import zodiac_short_generator as zsg

CLEAN = "Hôm nay **Tuổi Thìn** được xem là thuận hoà.\nNgười tuổi Tuất nên thận trọng.\nChúc bạn an yên."
REPEAT = "Câu mở.\nHãy giữ tâm thế bình tĩnh.\nHãy giữ tâm thế bình tĩnh.\nHãy giữ tâm thế bình tĩnh."
FULL_INV = ci.build(claim_source_kind="k", claim_source_data={"f": 1}, content_hook=ci.derived("h", "llm"),
                    idea_order=ci.derived([1], "llm"), payoff=ci.derived("p", "llm"))
PARTIAL_INV = ci.build(claim_source_kind="k", claim_source_data={"f": 1})
IDENTITY = {"content_id": "X_01", "category": "grounded_data", "generator": "g"}


def _eval(script, inv=PARTIAL_INV):
    return sqg.evaluate(script, domain="FS", identity=IDENTITY, invariant=inv, content_quality_record_id="c1")


def test_clean_script_is_pass_and_record_is_layer_script_in_the_same_store():
    gate = _eval(CLEAN)
    assert gate.publishable
    rec = cqg.read_records("FS")[-1]
    assert rec["layer"] == "script" and rec["rubric_version"] == "script-instrumentation-v0"
    assert rec["gate_status"] == cqg.PASS and rec["content_quality_record_id"] == "c1"
    assert rec["identity"]["content_id"] == "X_01"
    assert rec["diagnostics"]["sentence_count"] == 3 and rec["fingerprint"]
    assert rec["versions"]["diagnostics_version"]
    assert "score" not in json.dumps(rec["diagnostics"])


def test_diagnostics_and_invariant_never_change_pass_status():
    """Invariant thiếu hoặc câu đầu rất dài không làm đổi Gate status khi S8 sạch."""
    long_first = " ".join(["từ"] * 40) + ".\nCâu hai."
    assert _eval(long_first, inv=None).decision.gate_status == cqg.PASS


def test_s8_blocking_with_sufficient_invariant_is_fail_and_rewrite_eligible():
    gate = _eval(REPEAT, inv=FULL_INV)
    assert gate.decision.gate_status == cqg.FAIL and gate.decision.rewrite_eligible
    assert gate.decision.reason_codes == [cqg.SCR_REPEATED_SENTENCE]
    rec = cqg.read_records("FS")[-1]
    assert rec["evidence"][0]["span"] == "Hãy giữ tâm thế bình tĩnh." and rec["rewrite_eligible"] is True


def test_s8_blocking_with_incomplete_invariant_is_needs_review():
    gate = _eval(REPEAT, inv=PARTIAL_INV)
    assert gate.decision.gate_status == cqg.NEEDS_REVIEW and not gate.decision.rewrite_eligible
    assert gate.decision.reason_codes == [cqg.SCR_REPEATED_SENTENCE, cqg.SCR_INVARIANT_INCOMPLETE]


def test_non_blocking_truncation_does_not_fail():
    gate = _eval("Câu một đầy đủ.\nCâu cuối cụt và")
    assert gate.publishable
    assert cqg.read_records("FS")[-1]["evidence"][0]["reason_code"] == cqg.SCR_TRUNCATED


def test_unexpected_error_is_unmapped_needs_review(monkeypatch):
    monkeypatch.setattr(sqg.script_integrity, "check", lambda s: (_ for _ in ()).throw(RuntimeError("hỏng")))
    gate = _eval(CLEAN)
    assert (gate.decision.gate_status, gate.decision.reason_codes) == (cqg.NEEDS_REVIEW, [cqg.INTERNAL_UNMAPPED])


def test_record_write_failure_fails_closed(tmp_path, monkeypatch):
    blocker = tmp_path / "b"
    blocker.write_text("x", encoding="utf-8")
    monkeypatch.setenv(cqg.STORE_DIR_ENV, str(blocker / "qr"))
    gate = _eval(CLEAN)
    assert gate.decision.gate_status == cqg.PASS and gate.record_error and not gate.publishable


def test_module_does_not_depend_on_unix_only_locks():
    import subprocess
    from pathlib import Path
    code = ("import sys, script_quality_gate; bad=[m for m in ('fcntl','registry_lock','rotation_state','sea_g2p','vieneu_utils.phonemize_text') "
            "if m in sys.modules]; print(bad); sys.exit(1 if bad else 0)")
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, cwd=str(Path(sqg.__file__).parent))
    assert out.returncode == 0, out.stdout + out.stderr


# --- Qua generator zodiac ---------------------------------------------------

@pytest.fixture
def zodiac(tmp_path, monkeypatch):
    monkeypatch.setattr(zsg, "OUTPUT_DIR", tmp_path / "staged")
    monkeypatch.delenv("VIETNEU_SKIP_JUDGE_PANEL", raising=False)
    monkeypatch.setattr(sys, "argv", ["zodiac_short_generator.py", "--date", "2026-09-28"])
    return tmp_path


def _run(monkeypatch, script_a):
    cands = {"candidates": [{"strategy": "A", "script": script_a}] +
             [{"strategy": s, "script": f"Bản {s}."} for s in "BC"]}
    monkeypatch.setattr(engine, "_run_agy", lambda p: json.dumps(cands, ensure_ascii=False))
    monkeypatch.setattr(engine, "_run_codex", lambda p: json.dumps(
        {"fact_check": {s: "PASS" for s in "ABC"}, "candidate_id": "A", "hook_score": 9, "feedback": "x"},
        ensure_ascii=False))
    return zsg.main()


def test_zodiac_runs_s7_right_after_s1_and_links_records(zodiac, monkeypatch):
    assert _run(monkeypatch, CLEAN) == 0
    content_rec, script_rec = cqg.read_records("FS")[-2:]
    assert (content_rec["layer"], script_rec["layer"]) == ("content", "script")
    assert script_rec["content_quality_record_id"] == content_rec["quality_record_id"]
    assert script_rec["identity"]["content_id"] == content_rec["identity"]["content_id"]
    assert script_rec["invariant"]["sufficient"] is False  # hook/thứ tự ý/Payoff chưa trích (ticket 17)
    assert list((zodiac / "staged").glob("*_Short.txt"))


def test_zodiac_s8_fail_writes_no_bundle(zodiac, monkeypatch):
    assert _run(monkeypatch, REPEAT) == 1
    script_rec = cqg.read_records("FS")[-1]
    assert script_rec["layer"] == "script" and script_rec["gate_status"] == cqg.NEEDS_REVIEW
    assert cqg.SCR_REPEATED_SENTENCE in script_rec["reason_codes"]
    staged = zodiac / "staged"
    assert not staged.exists() or not list(staged.glob("*"))
