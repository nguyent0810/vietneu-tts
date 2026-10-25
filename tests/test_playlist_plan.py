import json
from pathlib import Path

import pytest

if not (Path(__file__).resolve().parents[1] / "output/cl_staging/scoreboard/playlist_apply.py").exists():   # gitignore: CI không có
    pytest.skip("playlist_apply chỉ có trên máy dựng", allow_module_level=True)


from output.cl_staging.scoreboard import playlist_apply
from output.cl_staging.scoreboard.playlist_apply import playlist_for_row


def test_lane_and_series_mapping():
    assert playlist_for_row("fs", {"lane": "lich"})["key"] == "daily_hoang_dao"
    assert playlist_for_row("fs", {"lane": "tuoi"})["key"] == "birth_year_element"
    assert playlist_for_row("fs", {"lane": "long", "series": "fs"})["key"] == "fs_long_character"
    assert playlist_for_row("bud", {"lane": "long", "series": "bud"})["key"] == "bud_long_character"
    assert playlist_for_row("bud", {"lane": "unknown"}) is None


def test_plan_shape_and_default_opt_out():
    plan = json.loads((Path(__file__).resolve().parents[1] / "output/cl_staging/scoreboard/playlist_plan.json").read_text())
    assert plan["automation"]["default_enabled"] is False
    assert set(plan["channels"]) == {"fs", "bud"}
    assert all("id" in v and "title" in v for c in plan["channels"].values() for p in c["playlists"] for v in p["videos"])


def test_apply_dry_run_uses_mocked_read_api_and_never_posts(monkeypatch, capsys):
    monkeypatch.setattr(playlist_apply, "get_valid_access_token", lambda _: "test-token")
    monkeypatch.setattr(playlist_apply, "inventory", lambda _: [])
    def forbidden(*args, **kwargs):
        raise AssertionError("dry-run must not send API requests")
    monkeypatch.setattr(playlist_apply.urllib.request, "urlopen", forbidden)
    playlist_apply.apply("fs", batch_size=2, confirm=False)
    output = capsys.readouterr().out
    assert "quota ghi ước tính" in output
    assert "TẠO" in output
