"""TRENDING đi qua Content Quality Gate (S1) ở cả bước draft và bước publish
(fact-check lại). Chính sách "luôn cần người duyệt" là Gate status Needs
review trong bảng ánh xạ của S1."""
import json
import sys

import pytest

import content_categories
import content_quality_gate as cqg
import trending_short_generator as tsg

SOURCE = "Theo tin, cơ quan chức năng xác nhận sự việc xảy ra hôm qua tại địa phương, gây chú ý trong dư luận rộng rãi."
FACTS = {"excerpt": "cơ quan chức năng xác nhận sự việc xảy ra hôm qua", "summary": "Su viec dia phuong",
         "mentions_real_person": False, "still_developing": False}
CANDS = {"candidates": [{"strategy": s, "script": f"Phương án {s}. Câu hai."} for s in "ABC"]}


def _verdict(winner, score):
    return {"fact_check": {s: ("PASS" if winner != "NONE" else "FAIL: x") for s in "ABC"}, "winner": winner,
            "winner_script": f"Phương án {winner}. Câu hai." if winner != "NONE" else "", "hook_score": score,
            "feedback": "x"}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    monkeypatch.delenv("VIETNEU_SKIP_JUDGE_PANEL", raising=False)
    return tmp_path


def _draft(repo, monkeypatch, verdict):
    monkeypatch.setattr(tsg, "_run_agy", lambda prompt: json.dumps(FACTS, ensure_ascii=False))
    monkeypatch.setattr("short_judge_panel_engine._run_agy", lambda prompt: json.dumps(CANDS, ensure_ascii=False))
    monkeypatch.setattr("short_judge_panel_engine._run_codex", lambda prompt: json.dumps(verdict, ensure_ascii=False))
    out = repo / "draft.json"
    monkeypatch.setattr(sys, "argv", ["trending_short_generator.py", "draft", "--domain", "FS", "--source-text", SOURCE,
                                      "--source-url", "https://example.com/a", "--source-date", "2026-09-28",
                                      "--output-json", str(out)])
    return tsg.main(), out


def test_draft_that_passes_engine_is_needs_review_not_pass(repo, monkeypatch):
    rc, out = _draft(repo, monkeypatch, _verdict("A", 9))
    assert rc == 0 and out.exists()
    rec = cqg.read_records("FS")[-1]
    assert rec["gate_status"] == cqg.NEEDS_REVIEW
    assert rec["reason_codes"] == [cqg.SAF_TRENDING_REQUIRES_HUMAN_REVIEW]
    assert rec["source_outcome"]["source"] == cqg.SOURCE_TRENDING_DRAFT
    assert rec["source_outcome"]["raw"]["passed"] is True, "source outcome gốc giữ nguyên"
    assert (rec["identity"]["generator"], rec["identity"]["category"]) == ("trending_short_generator", content_categories.TRENDING)
    assert rec["source_excerpt"] == FACTS["excerpt"]
    assert not list(repo.rglob("*_Short.txt"))


def test_draft_fail_is_recorded(repo, monkeypatch):
    rc, _ = _draft(repo, monkeypatch, _verdict("NONE", 0))
    assert rc == 1
    rec = cqg.read_records("FS")[-1]
    assert (rec["gate_status"], rec["reason_codes"]) == (cqg.FAIL, [cqg.ACC_NO_CANDIDATE_PASSED_FACTCHECK])


def _publish(repo, monkeypatch, draft, reverify):
    path = repo / "d.json"
    path.write_text(json.dumps(draft, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(tsg, "_run_codex", reverify)
    monkeypatch.setattr(sys, "argv", ["trending_short_generator.py", "publish", "--draft-json", str(path),
                                      "--confirm-reviewed"])
    return tsg.main()


def _good_draft():
    return {"facts": {**FACTS, "domain": "FS", "source_text": SOURCE}, "script": "Phương án A. Câu hai.", "passed": True}


def test_publish_reverify_pass_writes_short_and_pass_record(repo, monkeypatch):
    rc = _publish(repo, monkeypatch, _good_draft(), lambda p: json.dumps({"verdict": "PASS", "reason": "khớp"}))
    assert rc == 0
    rec = cqg.read_records("FS")[-1]
    assert rec["gate_status"] == cqg.PASS
    assert rec["source_outcome"]["source"] == cqg.SOURCE_TRENDING_PUBLISH
    assert len(list(repo.rglob("*_Short.txt"))) == 1
    assert rec["identity"]["content_id"] == list(repo.rglob("*_Short.txt"))[0].name[: -len("_Short.txt")] + "_01"


def test_publish_reverify_fail_has_its_own_reason_code(repo, monkeypatch):
    rc = _publish(repo, monkeypatch, _good_draft(), lambda p: json.dumps({"verdict": "FAIL", "reason": "bịa"}))
    assert rc == 1
    rec = cqg.read_records("FS")[-1]
    assert (rec["gate_status"], rec["reason_codes"]) == (cqg.FAIL, [cqg.ACC_PUBLISH_REVERIFY_FAILED])
    assert not list(repo.rglob("*_Short.txt"))


def test_publish_reverify_call_error_is_recorded_and_fails_closed(repo, monkeypatch):
    rc = _publish(repo, monkeypatch, _good_draft(), lambda p: "không phải json")
    assert rc == 1
    rec = cqg.read_records("FS")[-1]
    assert (rec["gate_status"], rec["reason_codes"]) == (cqg.FAIL, [cqg.JUDGE_CALL_ERROR])


def test_publish_precheck_failure_is_recorded(repo, monkeypatch):
    draft = _good_draft()
    draft["facts"]["excerpt"] = "không có trong nguồn"
    rc = _publish(repo, monkeypatch, draft, lambda p: pytest.fail("không được gọi fact-check lại"))
    assert rc == 1
    rec = cqg.read_records("FS")[-1]
    assert (rec["gate_status"], rec["reason_codes"]) == (cqg.FAIL, [cqg.ACC_DRAFT_INVALID])
    assert rec["evidence"][0]["stage"] == "precheck"


def test_publish_record_write_failure_blocks_short(repo, monkeypatch, tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    monkeypatch.setenv(cqg.STORE_DIR_ENV, str(blocker / "qr"))
    rc = _publish(repo, monkeypatch, _good_draft(), lambda p: json.dumps({"verdict": "PASS", "reason": "khớp"}))
    assert rc == 1
    assert not list(repo.rglob("*_Short.txt"))
