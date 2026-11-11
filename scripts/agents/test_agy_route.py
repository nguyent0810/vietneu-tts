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
    # media: Flash bị chặn (5h 10% < 15) -> Argon medium
    assert R.pick("type: media/render\n", p) == ("gemini-4-argon-medium", "medium")
    # content: Opus cần Claude tuần >= 40 (đang 35) -> Argon
    assert R.pick("type: content\n", p) == ("gemini-4-argon-high", "high")
    assert R.pick("type: research\n", p) == ("gemini-4-argon-high", "high")


def test_pin_and_full_quota():
    full = R.parse_quota(SAMPLE.replace("10%", "100%").replace("35%", "100%"))
    assert R.pick("type: code_shared\n", full) == ("gemini-4-argon-high", "high")
    assert R.pick("type: content\n", full) == ("claude-opus-5-5-medium", "medium")
    assert R.pick("type: media\n> Model: gemini-4-argon-low\n", full) == ("gemini-4-argon-low", "medium")
    assert R.pick("không có type\n", full)[0] == "gemini-3.8-flash-high"


def test_all_exhausted():
    empty = {k: {"week": 0.0, "5h": 0.0} for k in ("gemini", "claude_gpt", "argon")}
    assert R.pick("type: media\n", empty) is None


def test_host_c_dung_ssh_va_cache_rieng():
    assert R.quota_cmd("local") == ["agy", "-p", "/quota"]
    cmd = R.quota_cmd("c")
    assert cmd[0] == "ssh" and "C-ts" in cmd
    assert R.cache_for("c") != R.cache_for("local")
    assert R._host(["pick", "x.md", "--host", "c"]) == "c"
    assert R._host(["pick", "x.md"]) == "local"


QUOTA_C = ("Gemini Models\tWeekly Limit Remaining\t99%\t2026-11-18T01:03:02Z\n"
           "Gemini Models\tFive Hour Limit Remaining\t98%\t2026-11-11T06:03:02Z\n"
           "Gemini 4 Argon\tGemini 4 Argon Weekly Limit\t97%\t2026-11-18T00:47:41Z\n")


def test_main_host_c_quota_va_pick(tmp_path, monkeypatch, capsys):
    calls = []

    class Out:
        stdout = QUOTA_C

    def fake_run(cmd, **kw):
        calls.append(cmd)
        return Out()

    monkeypatch.setattr(R, "CACHE", tmp_path / "agy_quota.json")
    monkeypatch.setattr(R.subprocess, "run", fake_run)
    assert R.main(["quota", "--host", "c", "--fresh"]) == 0
    assert calls[-1][0] == "ssh"
    assert (tmp_path / "agy_quota_c.json").exists() and not (tmp_path / "agy_quota.json").exists()
    t = tmp_path / "T.md"
    t.write_text("type: review\n", encoding="utf-8")
    capsys.readouterr()
    assert R.main(["pick", "--host", "c", str(t)]) == 0      # cờ đặt trước tham số vị trí
    assert capsys.readouterr().out.split()[0] == "gemini-4-argon-high"


def test_host_loi_ro_rang():
    import pytest
    with pytest.raises(SystemExit):
        R._host(["quota", "--host"])
    with pytest.raises(SystemExit):
        R._host(["quota", "--host", "b"])
