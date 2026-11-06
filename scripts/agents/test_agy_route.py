import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("agy_route", Path(__file__).with_name("agy_route.py"))
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

SAMPLE = (
    "Gemini Models\tWeekly Limit Remaining\t80%\t2026-11-13T03:18:36Z\n"
    "Gemini Models\tFive Hour Limit Remaining\t10%\t2026-11-06T08:18:36Z\n"
    "Claude and GPT models\tWeekly Limit Remaining\t35%\t2026-11-13T03:18:36Z\n"
    "Claude and GPT models\tFive Hour Limit Remaining\t90%\t2026-11-06T08:18:36Z\n"
    "Gemini 4 Argon\tGemini 4 Argon Weekly Limit\t99%\t2026-11-13T03:17:37Z\n"
)


def test_parse_quota():
    p = R.parse_quota(SAMPLE)
    assert p["gemini"] == {"week": 80.0, "week_reset": "2026-11-13T03:18:36Z", "5h": 10.0, "5h_reset": "2026-11-06T08:18:36Z"}
    assert p["claude_gpt"]["week"] == 35.0 and p["claude_gpt"]["5h"] == 90.0
    assert p["argon"]["week"] == 99.0


def test_pick_by_type_and_fallback():
    p = R.parse_quota(SAMPLE)
    # media: Flash bị chặn (5h 10% < 15) -> Sonnet medium (Claude tuần 35% >= 20)
    assert R.pick("type: media/render\n", p) == ("claude-sonnet-5-5-medium", "medium")
    # code_shared: Opus cần Claude tuần >= 40 -> rơi xuống Sonnet
    assert R.pick("type: code_shared\n", p) == ("claude-sonnet-5-5-high", "high")
    assert R.pick("type: research\n", p) == ("gemini-4-argon-high", "high")


def test_pin_and_full_quota():
    full = R.parse_quota(SAMPLE.replace("10%", "100%").replace("35%", "100%"))
    assert R.pick("type: code_shared\n", full) == ("claude-opus-5-5-high", "high")
    assert R.pick("type: media\n> Model: gemini-4-argon-low\n", full) == ("gemini-4-argon-low", "medium")
    assert R.pick("không có type\n", full)[0] == "gemini-3.8-flash-high"


def test_all_exhausted():
    empty = {k: {"week": 0.0, "5h": 0.0} for k in ("gemini", "claude_gpt", "argon")}
    assert R.pick("type: media\n", empty) is None
