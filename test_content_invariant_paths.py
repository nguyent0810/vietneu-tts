"""Content invariant cho các đường vào không cần fcntl (ticket 15): generator
FS (facts, có/không đoạn trích) và TRENDING publish. Đường BUD runner + CL ở
test_content_invariant_paths_unix.py."""
import json
import sys

import pytest

import content_invariant as ci
import educational_short_generator as edu
import short_judge_panel_engine as engine
import trending_short_generator as tsg
import twelve_gods_short_generator as gods

CANDS = {"candidates": [{"strategy": s, "script": f"Bản {s}. Câu hai."} for s in "ABC"]}
TOPIC = {"title": "Cửa chính", "excerpt": "Trích đoạn nguồn về cửa.", "source_file": "src.md"}


@pytest.fixture
def judge_pass(monkeypatch):
    monkeypatch.delenv("VIETNEU_SKIP_JUDGE_PANEL", raising=False)
    monkeypatch.setattr(engine, "_run_agy", lambda p: json.dumps(CANDS, ensure_ascii=False))
    monkeypatch.setattr(engine, "_run_codex", lambda p: json.dumps(
        {"fact_check": {s: "PASS" for s in "ABC"}, "candidate_id": "A", "hook_score": 9, "feedback": "x"},
        ensure_ascii=False))


def test_fs_generator_invariant_has_facts_as_claim_source(judge_pass, tmp_path, monkeypatch):
    monkeypatch.setattr(gods, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(sys, "argv", ["g.py", "--date", "2026-09-28"])
    assert gods.main() == 0
    inv = ci.read_sidecar(next(tmp_path.glob("*_Short.txt")))
    assert inv["claim_source"]["kind"] == "generator_facts"
    assert inv["claim_source"]["data"] == gods.compute_god_facts(__import__("datetime").date(2026, 9, 28))
    assert inv["source_excerpt"] is None and inv["versions"]["quality_record_id"]


def test_topic_generator_invariant_keeps_source_excerpt(judge_pass, tmp_path, monkeypatch):
    monkeypatch.setattr(edu, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(edu, "next_unused_topic", lambda: dict(TOPIC))
    monkeypatch.setattr(edu, "mark_topic_used", lambda t: None)
    monkeypatch.setattr(sys, "argv", ["e.py"])
    assert edu.main() == 0
    inv = ci.read_sidecar(next(tmp_path.glob("*_Short.txt")))
    assert inv["source_excerpt"] == TOPIC["excerpt"] and inv["claim_source"]["data"]["excerpt"] == TOPIC["excerpt"]


def test_trending_publish_invariant(tmp_path, monkeypatch):
    monkeypatch.setattr(tsg, "__file__", str(tmp_path / "trending_short_generator.py"))
    source = "Theo tin, cơ quan chức năng xác nhận sự việc xảy ra hôm qua tại địa phương."
    facts = {"excerpt": "cơ quan chức năng xác nhận sự việc", "summary": "Su viec", "domain": "FS",
             "source_text": source, "mentions_real_person": False, "still_developing": False}
    draft = tmp_path / "d.json"
    draft.write_text(json.dumps({"facts": facts, "script": "Kịch bản.", "passed": True}, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(tsg, "_run_codex", lambda p: json.dumps({"verdict": "PASS", "reason": "khớp"}))
    monkeypatch.setattr(sys, "argv", ["t.py", "publish", "--draft-json", str(draft), "--confirm-reviewed"])
    assert tsg.main() == 0
    inv = ci.read_sidecar(next(tmp_path.rglob("*_Short.txt")))
    assert inv["claim_source"] == {"kind": "trending_extract_facts", "data": facts}
    assert inv["source_excerpt"] == facts["excerpt"]
