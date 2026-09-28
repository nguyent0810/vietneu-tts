"""Mọi generator Phong Thủy còn lại đi qua Content Quality Gate (S1): mỗi
generator có ít nhất một outcome PASS và một FAIL, cả hai đều có Quality
record với category/generator đúng. agy/Codex giả lập ở cấp hàm gọi CLI của
engine judge panel."""
import importlib
import json
import sys

import pytest

import content_categories
import content_quality_gate as cqg
import short_judge_panel_engine as engine

TOPIC = {"title": "Cửa chính hướng Nam", "excerpt": "Trích đoạn nguồn về cửa chính.", "source_file": "src.md",
         "is_hypothetical": False}

# (module, category, argv thêm, bộ strategy)
GENERATORS = [
    ("lich_hoang_dao_generator", content_categories.GROUNDED_DATA, ["--date", "2026-09-28"], "ABC"),
    ("twelve_gods_short_generator", content_categories.GROUNDED_DATA, ["--date", "2026-09-28"], "ABC"),
    ("zodiac_month_short_generator", content_categories.GROUNDED_DATA, ["--date", "2026-09-28"], "ABC"),
    ("element_color_short_generator", content_categories.GROUNDED_DATA, [], "ABC"),
    ("element_luck_short_generator", content_categories.GROUNDED_DATA, ["--date", "2026-09-28"], "ABC"),
    ("iching_short_generator", content_categories.INTERPRETATION, [], "ABC"),
    ("western_zodiac_short_generator", content_categories.CREATIVE_ASTROLOGY, [], "ABCD"),
    ("educational_short_generator", content_categories.EDUCATIONAL, [], "ABC"),
    ("storytelling_short_generator", content_categories.STORYTELLING, [], "ABC"),
]


def _candidates(strategies):
    return {"candidates": [{"strategy": s, "script": f"Kịch bản phương án {s}. Câu hai."} for s in strategies]}


def _verdict(strategies, winner, score):
    fact_check = {s: ("PASS" if winner != "NONE" else "FAIL: bịa") for s in strategies}
    script = f"Kịch bản phương án {winner}. Câu hai." if winner != "NONE" else ""
    return {"fact_check": fact_check, "candidate_id": winner, "winner_script": script, "hook_score": score, "feedback": "x"}


def _load(name, tmp_path, monkeypatch, extra_argv):
    mod = importlib.import_module(name)
    monkeypatch.setattr(mod, "OUTPUT_DIR", tmp_path / "staged")
    if hasattr(mod, "ROTATION_STATE_PATH"):
        monkeypatch.setattr(mod, "ROTATION_STATE_PATH", tmp_path / "rotation.json")
    if hasattr(mod, "next_unused_topic"):
        monkeypatch.setattr(mod, "next_unused_topic", lambda: dict(TOPIC))
        monkeypatch.setattr(mod, "mark_topic_used", lambda title: None)
    monkeypatch.setattr(sys, "argv", [f"{name}.py", *extra_argv])
    return mod


@pytest.fixture
def store(tmp_path, monkeypatch):
    monkeypatch.setenv(cqg.STORE_DIR_ENV, str(tmp_path / "qr"))
    monkeypatch.delenv("VIETNEU_SKIP_JUDGE_PANEL", raising=False)
    return tmp_path


@pytest.mark.parametrize("name,category,argv,strategies", GENERATORS)
def test_pass_outcome_writes_script_and_pass_record(store, monkeypatch, name, category, argv, strategies):
    mod = _load(name, store, monkeypatch, argv)
    monkeypatch.setattr(engine, "_run_agy", lambda prompt: json.dumps(_candidates(strategies), ensure_ascii=False))
    monkeypatch.setattr(engine, "_run_codex", lambda prompt: json.dumps(_verdict(strategies, "A", 9), ensure_ascii=False))
    assert mod.main() == 0
    staged = list((store / "staged").glob("*_Short.txt"))
    assert len(staged) == 1
    rec = cqg.read_records("FS")[-1]
    assert (rec["gate_status"], rec["identity"]["generator"], rec["identity"]["category"]) == (cqg.PASS, name, category)
    assert rec["identity"]["content_id"] == staged[0].name[: -len("_Short.txt")] + "_01"
    assert rec["versions"]["prompt_version"] and rec["versions"]["generator_version"]


@pytest.mark.parametrize("name,category,argv,strategies", GENERATORS)
def test_fail_outcome_still_records_without_script_file(store, monkeypatch, name, category, argv, strategies):
    mod = _load(name, store, monkeypatch, argv)
    monkeypatch.setattr(engine, "_run_agy", lambda prompt: json.dumps(_candidates(strategies), ensure_ascii=False))
    monkeypatch.setattr(engine, "_run_codex", lambda prompt: json.dumps(_verdict(strategies, "NONE", 0), ensure_ascii=False))
    assert mod.main() == 1
    assert not list((store / "staged").glob("*_Short.txt")) if (store / "staged").exists() else True
    rec = cqg.read_records("FS")[-1]
    assert rec["gate_status"] == cqg.FAIL
    assert rec["reason_codes"] == [cqg.ACC_NO_CANDIDATE_PASSED_FACTCHECK]
    assert (rec["identity"]["generator"], rec["identity"]["category"]) == (name, category)
    assert rec["facts"]


@pytest.mark.parametrize("name", ["educational_short_generator", "storytelling_short_generator"])
def test_topic_bank_generators_record_source_excerpt(store, monkeypatch, name):
    mod = _load(name, store, monkeypatch, [])
    monkeypatch.setattr(engine, "_run_agy", lambda prompt: json.dumps(_candidates("ABC"), ensure_ascii=False))
    monkeypatch.setattr(engine, "_run_codex", lambda prompt: json.dumps(_verdict("ABC", "A", 9), ensure_ascii=False))
    assert mod.main() == 0
    assert cqg.read_records("FS")[-1]["source_excerpt"] == TOPIC["excerpt"]
