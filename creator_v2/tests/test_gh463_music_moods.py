import pytest
from pathlib import Path

from motion.stier import themes


@pytest.mark.parametrize("channel,excluded,allowed", [
    ("mim", "hyperfun.mp3", "chill_wave.mp3"),
    ("ck", "carefree.mp3", "thinking_music.mp3"),   # CK giữ jazz nhẹ, chỉ loại upbeat
])
def test_default_rotation_and_explicit_override(monkeypatch, channel, excluded, allowed):
    monkeypatch.setattr(Path, "exists", lambda path: path.name in (excluded, allowed))
    pools = []
    def pick(slug, pool, ledger):
        pools.append(pool)
        return pool[0]
    monkeypatch.setattr(themes, "pick_track", pick)
    theme = themes.THEMES[channel]
    assert themes.select_music({}, theme, "old") == allowed
    assert themes.select_music({}, theme, "next") == allowed
    assert pools == [[allowed], [allowed]]
    assert themes.select_music({"music": excluded}, theme, "explicit") == excluded
    assert len(pools) == 2


def test_complete_labels_and_empty_pool(monkeypatch):
    assert set(themes.MIM_MOODS) == set(themes.MIM_TRACKS)
    assert set(themes.CK_MOODS) == set(themes.CK_TRACKS)
    monkeypatch.setattr(Path, "exists", lambda path: path.name == "hyperfun.mp3")
    with pytest.raises(SystemExit, match="hợp mood"):
        themes.select_music({}, themes.THEMES["mim"], "empty")
    assert themes.select_music({"music": "hyperfun.mp3"}, themes.THEMES["mim"], "explicit") == "hyperfun.mp3"
