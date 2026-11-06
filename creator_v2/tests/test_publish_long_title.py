import json

import pytest

from motion.long.publish_long import chosen_title, long_bundle


def test_chosen_title_prefers_youtube_and_warns(capsys):
    spec = {"title": "Tiêu đề cũ", "youtube": {"titles": ["Tiêu đề đã chọn", "Khác"]}}
    assert chosen_title(spec) == "Tiêu đề đã chọn"
    assert "Tiêu đề đã chọn" in capsys.readouterr().out


@pytest.mark.parametrize("youtube", [{}, {"titles": []}, {"titles": [""]}])
def test_chosen_title_falls_back(youtube):
    assert chosen_title({"title": "Tiêu đề cũ", "youtube": youtube}) == "Tiêu đề cũ"


def test_chosen_title_without_youtube():
    assert chosen_title({"title": "Tiêu đề cũ"}) == "Tiêu đề cũ"


def test_bundle_uses_chosen_title_but_keeps_thumbnail_text(tmp_path):
    sd = tmp_path / "data"
    od = tmp_path / "output"
    sd.mkdir()
    od.mkdir()
    spec = {"title": "Tiêu đề hồ sơ", "youtube": {"titles": ["Tiêu đề đã chọn"], "tags": []}, "chapters": []}
    (sd / "spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    (od / "description.txt").write_text("Mô tả", encoding="utf-8")
    bundle = long_bundle("topic", "MIM", "2026-11-06T00:00:00Z", sd, od)
    assert bundle.title == "Tiêu đề đã chọn"
    assert bundle.thumbnail_text == "Tiêu đề hồ sơ"
