"""Runner đọc Gate decision của Content Quality Gate (S1) thay vì tự diễn giải
outcome theo topic (ticket 04). Registry trỏ vào thư mục tạm, TTS bị chặn:
Short chỉ tới TTS khi Gate PASS; registry chỉ giữ reference quality_record_id."""
import json

import pytest

import content_quality_gate as cqg
import short_batch_runner as sbr

BUD = sbr.DEFAULT_TOPIC
FS = "Phong Thủy"


class _ReachedTTS(Exception):
    pass


def _seg(episode="EP001_Short", idx=1, text="Câu một.\nCâu hai."):
    return {"key": f"{episode}_{idx:02d}", "episode": episode, "segment_index": idx, "text": text}


@pytest.fixture
def runner(tmp_path, monkeypatch):
    reg = tmp_path / "registry.json"
    reg.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(sbr, "_registry_path", lambda topic: reg)
    calls = []

    def fake_tts(script, *a, **k):
        calls.append(script)
        raise _ReachedTTS()
    monkeypatch.setattr(sbr, "run_tts", fake_tts)

    def run(seg, topic):
        try:
            return sbr.process_one_segment(seg, tmp_path / "out", "creds.json", [], {}, None, 8, True, topic), calls
        except _ReachedTTS:
            return json.loads(reg.read_text(encoding="utf-8"))[seg["key"]], calls
    return run


def _review(passed, script, history, needs_review=None, hook_score=9):
    return {"final_script": script, "passed": passed, "hook_score": hook_score, "rounds_used": len(history),
            "round_history": history, "needs_human_review": (not passed) if needs_review is None else needs_review}


CANDS = [{"strategy": s, "script": f"Bản {s}."} for s in "ABC"]


def test_bud_pass_goes_to_tts_with_extracted_from_long_record(runner, monkeypatch):
    history = [{"round": 1, "candidates": CANDS, "verdict": {"fact_check": {"A": "PASS", "B": "PASS", "C": "PASS"},
                                                           "winner": "A", "winner_script": "Bản A.", "hook_score": 9}}]
    monkeypatch.setattr(sbr, "review_and_optimize_short", lambda text, **k: _review(True, "Bản A.", history))
    seg = _seg()
    entry, calls = runner(seg, BUD)
    assert calls == ["Bản A."]
    assert entry["status"] == "scripted" and entry["content_gate_status"] == cqg.PASS
    rec = cqg.read_records("BUD")[-1]
    assert entry["quality_record_id"] == rec["quality_record_id"]
    assert rec["identity"]["short_kind"] == "extracted_from_long"
    assert rec["identity"]["long_source"] == seg["episode"]
    assert rec["source_excerpt"] == seg["text"]
    assert [c["candidate_id"] for c in rec["candidates"]] == ["A", "B", "C"]


def test_bud_below_threshold_is_needs_review_and_never_reaches_tts(runner, monkeypatch):
    history = [{"round": 1, "candidates": CANDS, "verdict": {"fact_check": {"A": "PASS", "B": "PASS", "C": "PASS"},
                                                           "winner": "A", "winner_script": "Bản A.", "hook_score": 6}}]
    monkeypatch.setattr(sbr, "review_and_optimize_short", lambda text, **k: _review(False, "Bản A.", history, hook_score=6))
    entry, calls = runner(_seg(), BUD)
    assert calls == []
    assert entry["status"] == "needs_review"
    assert entry["content_gate_status"] == cqg.NEEDS_REVIEW
    assert entry["content_gate_reason_codes"] == [cqg.JUDGE_BELOW_HOOK_THRESHOLD]


def test_bud_weak_source_is_source_insufficient_not_fail(runner, monkeypatch):
    none = {"fact_check": {s: "FAIL: phải thêm thắt" for s in "ABC"}, "winner": "NONE", "winner_script": "",
            "hook_score": 0, "source_insufficient": True}
    history = [{"round": r, "candidates": CANDS, "verdict": dict(none)} for r in (1, 2, 3)]
    monkeypatch.setattr(sbr, "review_and_optimize_short", lambda text, **k: _review(False, None, history))
    entry, calls = runner(_seg(), BUD)
    assert calls == []
    assert entry["status"] == "needs_review"
    assert entry["content_gate_status"] == cqg.INSUFFICIENT_SOURCE
    rec = cqg.read_records("BUD")[-1]
    assert rec["gate_status"] == cqg.INSUFFICIENT_SOURCE
    assert rec["reason_codes"] == [cqg.SRC_INSUFFICIENT_SOURCE_MATERIAL]


def test_bud_no_factcheck_pass_without_source_flag_is_fail(runner, monkeypatch):
    none = {"fact_check": {s: "FAIL: đổi ý" for s in "ABC"}, "winner": "NONE", "winner_script": "", "hook_score": 0,
            "source_insufficient": False}
    history = [{"round": 1, "candidates": CANDS, "verdict": none}]
    monkeypatch.setattr(sbr, "review_and_optimize_short", lambda text, **k: _review(False, None, history))
    entry, calls = runner(_seg(), BUD)
    assert calls == [] and entry["content_gate_status"] == cqg.FAIL


def _seed_generator_record(key, script, status_raw="pass"):
    history = [{"round": 1, "candidates": CANDS, "verdict": {"fact_check": {"A": "PASS", "B": "PASS", "C": "PASS"},
                                                           "winner": "A", "winner_script": script, "hook_score": 9}}]
    raw = {"script": script, "passed": status_raw == "pass", "hook_score": 9 if status_raw == "pass" else 6,
           "iterations_used": 1, "history": history, "needs_human_review": status_raw != "pass"}
    return cqg.evaluate(cqg.SourceOutcome(source=cqg.SOURCE_JUDGE_PANEL_ENGINE, domain="FS", raw=raw, content_id=key,
                                          category="grounded_data", generator="zodiac_short_generator"))


def test_fs_staged_script_with_pass_record_goes_to_tts(runner):
    seg = _seg("CONGIAP20260928_ConGiap", 1, "Câu một.\nCâu hai.")
    gen = _seed_generator_record(seg["key"], seg["text"])
    entry, calls = runner(seg, FS)
    assert calls == [seg["text"]]
    assert entry["content_gate_status"] == cqg.PASS
    rec = cqg.read_records("FS")[-1]
    assert rec["source_outcome"]["source"] == cqg.SOURCE_RUNNER_STAGED
    assert rec["evidence"][0]["quality_record_id"] == gen.record["quality_record_id"]
    assert entry["quality_record_id"] == rec["quality_record_id"]


def test_fs_staged_script_without_record_does_not_bypass_s1(runner):
    entry, calls = runner(_seg("OLDFILE_X", 1), FS)
    assert calls == []
    assert (entry["status"], entry["content_gate_status"]) == ("needs_review", cqg.NEEDS_REVIEW)
    assert entry["content_gate_reason_codes"] == [cqg.SRC_NO_QUALITY_RECORD]


def test_fs_script_edited_after_gate_is_stopped(runner):
    seg = _seg("CONGIAP20260928_ConGiap", 1, "Câu đã bị sửa tay.")
    _seed_generator_record(seg["key"], "Câu gốc đã qua Gate.")
    entry, calls = runner(seg, FS)
    assert calls == []
    assert entry["content_gate_reason_codes"] == [cqg.SRC_SCRIPT_CHANGED_AFTER_GATE]


def test_fs_record_not_pass_is_stopped(runner):
    seg = _seg("CONGIAP20260928_ConGiap", 1)
    _seed_generator_record(seg["key"], seg["text"], status_raw="below")
    entry, calls = runner(seg, FS)
    assert calls == []
    assert entry["content_gate_reason_codes"] == [cqg.SRC_GATE_NOT_PASSED]


def test_record_write_failure_blocks_tts(runner, monkeypatch, tmp_path):
    seg = _seg("CONGIAP20260928_ConGiap", 1)
    _seed_generator_record(seg["key"], seg["text"])
    orig = cqg.append_record

    def fail_runner_records(record):
        if record["source_outcome"]["source"] == cqg.SOURCE_RUNNER_STAGED:
            raise cqg.QualityRecordWriteError("đĩa đầy")
        return orig(record)
    monkeypatch.setattr(cqg, "append_record", fail_runner_records)
    entry, calls = runner(seg, FS)
    assert calls == []
    assert entry["status"] == "needs_review" and entry["quality_record_id"] is None


@pytest.mark.parametrize("gate_status", [None, cqg.NEEDS_REVIEW, cqg.FAIL])
def test_resumed_scripted_entry_without_pass_gate_never_reaches_tts(runner, tmp_path, gate_status):
    """Resume / registry cũ / sửa tay: status "scripted" nhưng Gate không PASS
    (hoặc entry từ trước khi có S1) -> kiểm tra lại ngay trước TTS, dừng."""
    seg = _seg("RESUME_X", 1)
    entry = {"key": seg["key"], "episode": seg["episode"], "segment_index": 1, "status": "scripted",
             "final_script": seg["text"], "needs_human_review_hook": False}
    if gate_status is not None:
        entry["content_gate_status"] = gate_status
    reg = tmp_path / "registry.json"
    reg.write_text(json.dumps({seg["key"]: entry}, ensure_ascii=False), encoding="utf-8")
    result = sbr.process_one_segment(seg, tmp_path / "out", "creds.json", [], {seg["key"]: dict(entry)}, None, 8, True, FS)
    assert result["status"] == "needs_review"
    assert "Content Quality Gate" in result["needs_human_review_content_gate"]


def test_seo_ready_entry_without_pass_gate_is_blocked_before_upload(runner, tmp_path, monkeypatch):
    seg = _seg("RESUME_Y", 1)
    entry = {"key": seg["key"], "episode": seg["episode"], "segment_index": 1, "status": "seo_ready",
             "final_script": seg["text"], "content_gate_status": cqg.NEEDS_REVIEW,
             "needs_human_review_hook": False, "needs_human_review_seo": False, "seo": {"title": "t"}}
    reg = tmp_path / "registry.json"
    reg.write_text(json.dumps({seg["key"]: entry}, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(sbr, "upload_short", lambda *a, **k: pytest.fail("không được upload khi Gate chưa PASS"))
    result = sbr.process_one_segment(seg, tmp_path / "out", "creds.json", [], {seg["key"]: dict(entry)}, None, 8, False, FS)
    assert result["status"] == "needs_review"
    assert "upload" in result["needs_human_review_content_gate"]
