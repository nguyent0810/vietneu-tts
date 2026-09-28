"""VIETNEU_SKIP_JUDGE_PANEL=1 ở mọi đường vào không cần fcntl (FS: 12 vị Thần,
educational, storytelling; TRENDING draft): Gate status Needs review, reason
code BYPASS_JUDGE, bypass flag; không ghi script (ticket 06, D49).
BUD runner và CL nằm ở test_skip_judge_panel_bypass_unix.py."""
import json
import sys

import pytest

import content_quality_gate as cqg
import educational_short_generator as edu
import short_judge_panel_engine as engine
import storytelling_short_generator as story
import trending_short_generator as tsg
import twelve_gods_short_generator as gods

def _gate_records(domain):
    """Record tầng Content/Script (bỏ record catalog advisory ghi sau S7)."""
    return [r for r in cqg.read_records(domain) if r["layer"] != "catalog"]


CANDS = {"candidates": [{"strategy": s, "script": f"Bản {s}. Câu hai."} for s in "ABC"]}
TOPIC = {"title": "Chủ đề", "excerpt": "Trích đoạn.", "source_file": "src.md", "is_hypothetical": False}


@pytest.fixture
def bypass(monkeypatch):
    monkeypatch.setenv("VIETNEU_SKIP_JUDGE_PANEL", "1")
    monkeypatch.setattr(engine, "_run_agy", lambda p: json.dumps(CANDS, ensure_ascii=False))
    monkeypatch.setattr(engine, "_run_codex", lambda p: pytest.fail("bypass không gọi judge"))


def _assert_bypass_record(domain):
    rec = cqg.read_records(domain)[-1]
    assert (rec["gate_status"], rec["reason_codes"], rec["bypass"]) == (cqg.NEEDS_REVIEW, [cqg.BYPASS_JUDGE], True)
    return rec


@pytest.mark.parametrize("mod,argv", [(gods, ["--date", "2026-09-28"]), (edu, []), (story, [])])
def test_fs_generators_bypass_is_needs_review_and_writes_nothing(bypass, tmp_path, monkeypatch, mod, argv):
    monkeypatch.setattr(mod, "OUTPUT_DIR", tmp_path / "staged")
    if hasattr(mod, "next_unused_topic"):
        monkeypatch.setattr(mod, "next_unused_topic", lambda: dict(TOPIC))
        monkeypatch.setattr(mod, "mark_topic_used", lambda t: pytest.fail("không đánh dấu chủ đề đã dùng khi bypass"))
    monkeypatch.setattr(sys, "argv", ["gen.py", *argv])
    assert mod.main() == 1
    assert not (tmp_path / "staged").exists() or not list((tmp_path / "staged").glob("*"))
    _assert_bypass_record("FS")


def test_trending_draft_bypass_is_needs_review_with_bypass_flag(bypass, tmp_path, monkeypatch):
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    monkeypatch.setattr(tsg, "_run_agy", lambda p: json.dumps(
        {"excerpt": "cơ quan chức năng xác nhận sự việc", "summary": "S", "mentions_real_person": False,
         "still_developing": False}, ensure_ascii=False))
    src = "Theo tin, cơ quan chức năng xác nhận sự việc xảy ra hôm qua tại địa phương, gây chú ý dư luận."
    monkeypatch.setattr(sys, "argv", ["t.py", "draft", "--domain", "FS", "--source-text", src, "--source-url",
                                      "https://x.vn/a", "--source-date", "2026-09-28", "--output-json",
                                      str(tmp_path / "d.json")])
    tsg.main()
    _assert_bypass_record("FS")
    assert not list(tmp_path.rglob("*_Short.txt"))


def test_env_off_keeps_normal_behaviour(tmp_path, monkeypatch):
    monkeypatch.delenv("VIETNEU_SKIP_JUDGE_PANEL", raising=False)
    monkeypatch.setattr(engine, "_run_agy", lambda p: json.dumps(CANDS, ensure_ascii=False))
    monkeypatch.setattr(engine, "_run_codex", lambda p: json.dumps(
        {"fact_check": {s: "PASS" for s in "ABC"}, "candidate_id": "A", "winner_script": "Bản A. Câu hai.",
         "hook_score": 9, "feedback": "x"}, ensure_ascii=False))
    monkeypatch.setattr(gods, "OUTPUT_DIR", tmp_path / "staged")
    monkeypatch.setattr(sys, "argv", ["gods.py", "--date", "2026-09-28"])
    assert gods.main() == 0
    rec = _gate_records("FS")[-1]
    assert (rec["gate_status"], rec["bypass"]) == (cqg.PASS, False)
