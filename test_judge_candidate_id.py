"""Judge chỉ chọn bằng `candidate_id` (ticket 07, D48): văn bản thắng luôn là
nguyên văn ứng viên; verdict thiếu/sai/lạ id hoặc sai cấu trúc bị từ chối và
ghi vào lịch sử vòng; không còn word overlap 0.4."""
import json

import pytest

import short_judge_panel_engine as engine
from content_seo import ContentSeoError

CANDS = [{"strategy": s, "script": f"Nguyên văn ứng viên {s}. Câu hai."} for s in "ABC"]


def _verdict(**kw):
    v = {"fact_check": {"A": "PASS", "B": "PASS", "C": "FAIL: bịa"}, "candidate_id": "A", "hook_score": 9,
         "feedback": "ok"}
    v.update(kw)
    return v


# --- Hàm kiểm tra verdict (thuần) -----------------------------------------

def test_valid_verdict_selects_the_candidate_verbatim():
    v = engine._validate_verdict(_verdict(), CANDS)
    assert engine.selected_script(v, CANDS) == CANDS[0]["script"]


def test_verdict_with_its_own_script_does_not_change_selected_text():
    v = engine._validate_verdict(_verdict(winner_script="Judge tự viết một kịch bản khác hẳn.",
                                          script="Cũng tự viết."), CANDS)
    assert engine.selected_script(v, CANDS) == CANDS[0]["script"]


def test_none_selects_nothing():
    v = engine._validate_verdict(_verdict(candidate_id="NONE"), CANDS)
    assert engine.selected_script(v, CANDS) is None


@pytest.mark.parametrize("bad", [
    {"candidate_id": None},
    {"candidate_id": "Z"},
    {"candidate_id": 1},
    {"candidate_id": "D"},  # không có trong bộ A/B/C
])
def test_missing_or_unknown_candidate_id_is_rejected(bad):
    v = _verdict(**bad)
    with pytest.raises(ContentSeoError):
        engine._validate_verdict(v, CANDS)


def test_legacy_winner_field_without_candidate_id_is_rejected():
    v = _verdict()
    del v["candidate_id"]
    v["winner"] = "A"
    with pytest.raises(ContentSeoError):
        engine._validate_verdict(v, CANDS)


@pytest.mark.parametrize("bad", [
    {"fact_check": None},
    {"fact_check": {"A": "FAIL: x"}},
    {"hook_score": "cao"},
    {"hook_score": 99},
])
def test_structurally_invalid_verdict_is_rejected(bad):
    with pytest.raises(ContentSeoError):
        engine._validate_verdict(_verdict(**bad), CANDS)


def test_non_object_verdict_is_rejected():
    with pytest.raises(ContentSeoError):
        engine._validate_verdict(["A"], CANDS)


def test_fact_check_of_winner_must_still_pass():
    with pytest.raises(ContentSeoError):
        engine._validate_verdict(_verdict(candidate_id="C"), CANDS)


# --- Qua engine với agy/Codex giả lập --------------------------------------

@pytest.fixture
def fake_agy(monkeypatch):
    monkeypatch.delenv("VIETNEU_SKIP_JUDGE_PANEL", raising=False)
    monkeypatch.setattr(engine, "_run_agy", lambda p: json.dumps({"candidates": CANDS}, ensure_ascii=False))


def test_engine_returns_candidate_text_even_if_judge_attaches_rewritten_script(fake_agy, monkeypatch):
    monkeypatch.setattr(engine, "_run_codex", lambda p: json.dumps(
        _verdict(candidate_id="B", winner_script="Bản judge viết lại."), ensure_ascii=False))
    result = engine.generate_verified_script({"k": "v"}, "{facts_json}{revision_note}Trả về CHỈ 1 JSON object",
                                             "{facts_json}{candidates_text}Trả về CHỈ 1 JSON object")
    assert result["passed"] is True
    assert result["script"] == CANDS[1]["script"]


def test_engine_records_rejected_verdicts_in_round_history(fake_agy, monkeypatch):
    responses = iter([json.dumps({"candidate_id": "Q"}), json.dumps(_verdict(candidate_id=None)),
                      json.dumps(_verdict(candidate_id="A"))])
    monkeypatch.setattr(engine, "_run_codex", lambda p: next(responses))
    result = engine.generate_verified_script({}, "{facts_json}{revision_note}", "{facts_json}{candidates_text}")
    stages = [h.get("stage") for h in result["history"]]
    assert stages[:2] == ["judge_rejected", "judge_rejected"]
    assert result["passed"] and result["script"] == CANDS[0]["script"]


def test_every_judge_prompt_asks_for_candidate_id_not_script():
    """Đọc thẳng source (không import: vài generator cần fcntl)."""
    from pathlib import Path
    root = Path(engine.__file__).parent
    names = ["cl_case_generation", "criminal_law_short_generator", "educational_short_generator",
             "element_color_short_generator", "element_luck_short_generator", "iching_short_generator",
             "lich_hoang_dao_generator", "short_content_review", "storytelling_short_generator",
             "trending_short_generator", "twelve_gods_short_generator", "western_zodiac_short_generator",
             "zodiac_month_short_generator", "zodiac_short_generator"]
    for name in names:
        src = (root / f"{name}.py").read_text(encoding="utf-8")
        assert '"candidate_id": "A" hoặc' in src, name
        assert '"winner_script":' not in src, name
