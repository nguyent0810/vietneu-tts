"""S7 cho mọi đường vào (ticket 16): mỗi đường có record `layer: script` ngay
sau S1, runner không đưa Short tới TTS khi chưa có quyết định S7 hoặc S7 không
PASS, và S7 không bao giờ ghi đè Needs review của S1. Cần fcntl (runner)."""
import json
import sys

import pytest

import cl_risk_gate_lifecycle as L
import content_quality_gate as cqg
import short_batch_runner as sbr
import short_judge_panel_engine as engine
import twelve_gods_short_generator as gods
from gate_test_support import stamp_content_gate_pass

def _gate_records(domain):
    """Record tầng Content/Script (bỏ record catalog advisory ghi sau S7)."""
    return [r for r in cqg.read_records(domain) if r["layer"] != "catalog"]


FS, BUD, CL = "Phong Thủy", sbr.DEFAULT_TOPIC, "Hình Sự"
REPEAT = "Câu mở.\nHãy giữ tâm thế bình tĩnh.\nHãy giữ tâm thế bình tĩnh."


class _TTS(Exception):
    pass


@pytest.fixture
def runner(tmp_path, monkeypatch):
    reg = tmp_path / "registry.json"
    reg.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(sbr, "_registry_path", lambda t: reg)
    monkeypatch.setattr(sbr, "PROJECT_ROOT", tmp_path)
    import short_segment_discovery as sd
    monkeypatch.setattr(sd, "PROJECT_ROOT", tmp_path)
    calls = []

    def tts(script, *a, **k):
        calls.append(script)
        raise _TTS()
    monkeypatch.setattr(sbr, "run_tts", tts)

    def run(seg, topic, registry=None):
        try:
            return sbr.process_one_segment(seg, tmp_path / "out", "c.json", [], registry or {}, None, 8, True, topic)
        except _TTS:
            return json.loads(reg.read_text(encoding="utf-8"))[seg["key"]]
    return run, calls, tmp_path


def _layers(domain):
    """(layer, gate_status) của record Content/Script (bỏ record catalog advisory)."""
    return [(r["layer"], r["gate_status"]) for r in cqg.read_records(domain) if r["layer"] != "catalog"]


def _seed_fs_record(key, script):
    history = [{"round": 1, "candidates": [{"strategy": "A", "script": script}],
                "verdict": {"fact_check": {"A": "PASS"}, "candidate_id": "A", "hook_score": 9}}]
    cqg.evaluate(cqg.SourceOutcome(source=cqg.SOURCE_JUDGE_PANEL_ENGINE, domain="FS", content_id=key,
                                   raw={"script": script, "passed": True, "hook_score": 9, "history": history,
                                        "needs_human_review": False}))


def test_fs_staged_path_runs_s7_after_s1_and_reaches_tts(runner):
    run, calls, _ = runner
    seg = {"key": "THAN20260928_12ViThan_01", "episode": "THAN20260928_12ViThan", "segment_index": 1,
           "text": "Hôm nay Thần Thanh Long được xem là tốt.\nChúc bạn an yên."}
    _seed_fs_record(seg["key"], seg["text"])
    entry = run(seg, FS)
    assert calls == [seg["text"]]
    content_rec, script_rec = _gate_records("FS")[-2:]
    assert (content_rec["layer"], script_rec["layer"]) == ("content", "script")
    assert script_rec["content_quality_record_id"] == content_rec["quality_record_id"] == entry["quality_record_id"]
    assert entry["script_gate_status"] == cqg.PASS and entry["script_quality_record_id"] == script_rec["quality_record_id"]


def test_fs_staged_script_failing_s8_never_reaches_tts(runner):
    run, calls, _ = runner
    seg = {"key": "X_01", "episode": "X", "segment_index": 1, "text": REPEAT}
    _seed_fs_record(seg["key"], seg["text"])
    entry = run(seg, FS)
    assert calls == [] and entry["status"] == "needs_review"
    assert cqg.SCR_REPEATED_SENTENCE in entry["script_gate_reason_codes"]
    assert "Script Quality Gate" in entry["needs_human_review_script_gate"]


def test_bud_path_has_script_record(runner, monkeypatch):
    run, calls, _ = runner
    history = [{"round": 1, "candidates": [{"strategy": "A", "script": "Bản viết lại."}],
                "verdict": {"fact_check": {"A": "PASS"}, "candidate_id": "A", "hook_score": 9}}]
    monkeypatch.setattr(sbr, "review_and_optimize_short", lambda text, **k: {
        "final_script": "Bản viết lại.", "passed": True, "hook_score": 9, "rounds_used": 1, "round_history": history,
        "needs_human_review": False})
    seg = {"key": "EP1_Short_01", "episode": "EP1_Short", "segment_index": 1, "text": "Đoạn trích gốc."}
    entry = run(seg, BUD)
    assert calls == ["Bản viết lại."]
    assert _layers("BUD")[-2:] == [("content", cqg.PASS), ("script", cqg.PASS)]
    script_rec = _gate_records("BUD")[-1]
    assert script_rec["invariant"]["missing"], "invariant BUD có đoạn trích nhưng chưa có hook/thứ tự ý/Payoff"


def test_cl_sidecar_path_has_script_record(runner):
    run, calls, root = runner
    seg = {"key": "CLGATE_c1_01", "episode": "CLGATE_c1", "segment_index": 1, "text": "Vụ án năm 1990.\nChưa có lời giải."}
    sidecar = {"case_id": "c1", "reviewed_editorial_hash": "e", "reviewed_script_hash": L._script_text_hash(seg["text"]),
               "final_editorial": {"title": "t"}, "named_individuals": []}
    p = root / "drive_input" / "content_repo_staged" / CL / "Short" / "CLGATE_c1_Short.cl_meta.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(sidecar), encoding="utf-8")
    entry = run(seg, CL)
    assert calls == [seg["text"]]
    assert _layers("CL")[-2:] == [("content", cqg.PASS), ("script", cqg.PASS)]
    assert entry["script_gate_status"] == cqg.PASS


def test_s1_needs_review_is_never_overwritten_by_s7(runner, monkeypatch):
    run, calls, _ = runner
    monkeypatch.setattr(sbr, "review_and_optimize_short", lambda text, **k: {
        "final_script": "Bản A.", "passed": True, "hook_score": None, "rounds_used": 1,
        "round_history": [{"round": 1, "skipped_judge": True, "candidates": []}], "needs_human_review": False})
    seg = {"key": "EP2_Short_01", "episode": "EP2_Short", "segment_index": 1, "text": "Đoạn gốc."}
    entry = run(seg, BUD)
    assert calls == [] and entry["content_gate_status"] == cqg.NEEDS_REVIEW
    assert "script_gate_status" not in entry
    assert [layer for layer, _ in _layers("BUD")] == ["content"], "S7 chỉ chạy khi S1 PASS"


def test_resumed_entry_without_s7_decision_is_blocked_before_tts(runner):
    run, calls, root = runner
    seg = {"key": "R_01", "episode": "R", "segment_index": 1, "text": "Câu một.\nCâu hai."}
    entry = stamp_content_gate_pass({"key": seg["key"], "episode": seg["episode"], "segment_index": 1,
                                     "status": "scripted", "final_script": seg["text"]}, "FS")
    del entry["script_gate_status"], entry["script_quality_record_id"]
    (root / "registry.json").write_text(json.dumps({seg["key"]: entry}, ensure_ascii=False), encoding="utf-8")
    result = run(seg, FS, registry={seg["key"]: dict(entry)})
    assert calls == [] and result["status"] == "needs_review"
    assert "Script Quality Gate chưa có quyết định" in result["needs_human_review_content_gate"]


def test_fs_generator_writes_script_record_right_after_content_record(tmp_path, monkeypatch):
    monkeypatch.delenv("VIETNEU_SKIP_JUDGE_PANEL", raising=False)
    monkeypatch.setattr(gods, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(engine, "_run_agy", lambda p: json.dumps(
        {"candidates": [{"strategy": s, "script": f"Bản {s}. Câu hai."} for s in "ABC"]}, ensure_ascii=False))
    monkeypatch.setattr(engine, "_run_codex", lambda p: json.dumps(
        {"fact_check": {s: "PASS" for s in "ABC"}, "candidate_id": "A", "hook_score": 9, "feedback": "x"}))
    monkeypatch.setattr(sys, "argv", ["g.py", "--date", "2026-09-28"])
    assert gods.main() == 0
    assert _layers("FS")[-2:] == [("content", cqg.PASS), ("script", cqg.PASS)]
