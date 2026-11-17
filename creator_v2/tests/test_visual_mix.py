"""Visual budget adapters: fake chapters/timings only, no assets or rendering."""
import json

import pytest

from motion.long import floor

VM = floor.visual_mix


def test_visual_mix_creator_seconds_text_overlay_data_and_repeat_aliases():
    source = [{"type": "chapter"}, {"type": "slam", "at": 1},
              {"type": "date", "at": 2}, {"type": "counter", "at": 3, "img": "a"},
              {"type": "kinetic", "at": 4, "vid": "movie.mp4", "overlay": True},
              {"type": "ledger", "at": 5}, {"type": "photo", "at": 6, "img": "b"}]
    chapters = [("ch00", {"scenes": source})]
    timing = {"segments": [{"start": n, "end": n+1} for n in range(7)], "duration": 10}
    metrics = VM.measure(floor.visual_mix_scenes(chapters, timings={"ch00": timing},
                                               spec={"imgs": {"a": "file.jpg", "b": "file.jpg"}}))
    assert metrics["text_seconds"] == 2
    assert metrics["seconds"] == 10
    assert metrics["max_repeat"] == 2
    assert metrics["unique_images"] == 1


def test_visual_mix_creator_styles_and_split_panels():
    chapters = [("ch00", {"scenes": [
        {"type": "split", "t0": 0, "t1": 1, "a": {"img": "a"}, "b": {"img": "b"}},
        {"type": "woodcut", "at": 1.0, "img": "a"},
        {"type": "photo", "at": 2.0, "img": "a", "cam": "other", "crop": [0, 0]}]})]
    metrics = VM.measure(floor.visual_mix_scenes(chapters, timings={"ch00": {"duration": 3}},
                                               spec={"imgs": {"a": "same.jpg", "b": "other.jpg"}}))
    assert metrics["max_repeat"] == 2
    assert metrics["unique_images"] == 2
    assert metrics["seconds"] == 3


def test_visual_mix_creator_word_float_and_offset_anchors():
    segments = [{"start": 0, "end": 5, "text": "Một hai ba", "words": [
        {"w": "Một", "t": 0}, {"w": "hai", "t": 1}, {"w": "ba", "t": 3}]}]
    assert floor._mix_anchor([0, "HAI", 0, .25], segments) == 1.25
    assert floor._mix_anchor([0, None, 0, .4], segments) == .4
    assert floor._mix_anchor(2.5, segments) == 2.5
    with pytest.raises(ValueError, match="không có"):
        floor._mix_anchor([0, "bốn"], segments)


def _project(tmp_path, *, legacy=False, reason=None):
    data = tmp_path / "data/long/topic"
    data.mkdir(parents=True)
    (data.parent / "_legacy_topics.json").write_text(json.dumps(["topic"] if legacy else []), encoding="utf-8")
    (data / "spec.json").write_text(json.dumps({"text_budget_reason": reason}), encoding="utf-8")
    return data


def test_visual_mix_creator_legacy_matches_build_long(tmp_path):
    _project(tmp_path, legacy=True)
    assert not floor.visual_mix_is_new("topic", tmp_path)
    assert not floor.visual_mix_is_new("missing", tmp_path)
    (tmp_path / "data/long/_legacy_topics.json").write_text("[]", encoding="utf-8")
    assert floor.visual_mix_is_new("topic", tmp_path)


def test_visual_mix_creator_floor_new_reason_and_legacy(monkeypatch, tmp_path):
    data = _project(tmp_path)
    monkeypatch.setattr(floor, "ROOT", tmp_path)
    monkeypatch.setattr(floor, "_coverage_report", lambda _: {"text_only_percent": 100, "longest_text_only_run_s": 1})
    chapters = [("ch00", {"lines": ["Câu thứ nhất."], "scenes": [{"type": "kinetic"}]})]
    assert any("visual_mix: chữ" in msg for msg in floor.problems(chapters, "MIM", "topic"))
    assert "WARN" in floor.visual_mix_report(chapters, "topic")  # density always warning
    (data / "spec.json").write_text('{"text_budget_reason": "trích đọc"}', encoding="utf-8")
    assert floor.problems(chapters, "MIM", "topic") == []
    assert "visual_mix WARN: chữ" in floor.visual_mix_report(chapters, "topic")
    (data.parent / "_legacy_topics.json").write_text('["topic"]', encoding="utf-8")
    assert not floor.visual_mix_findings(chapters, "topic")


def test_visual_mix_creator_new_repeated_images_still_block_with_reason(monkeypatch, tmp_path):
    _project(tmp_path, reason="đọc nguyên văn")
    monkeypatch.setattr(floor, "ROOT", tmp_path)
    monkeypatch.setattr(floor, "_coverage_report", lambda _: {"text_only_percent": 0, "longest_text_only_run_s": 0})
    chapters = [("ch00", {"lines": ["Một câu."] * 7, "scenes": [
        {"type": "photo", "at": i, "img": "same.jpg", "cam": str(i)} for i in range(7)]})]
    assert any("visual_mix: ảnh tĩnh lặp tối đa 7" in msg for msg in floor.problems(chapters, "MIM", "topic"))


def test_visual_mix_creator_timing_duration_and_estimate_label(tmp_path):
    _project(tmp_path)
    chapters = [("ch00", {"lines": ["Một câu."], "scenes": [{"type": "slam"}]}),
                ("ch01", {"lines": ["Hai câu."], "scenes": [{"type": "map"}]})]
    before = floor.visual_mix_metrics(chapters, "topic", root=tmp_path)
    assert len(before["estimated"]) == 2
    folder = tmp_path / "output/long/topic/ch00"
    folder.mkdir(parents=True)
    (folder / "timing.json").write_text(json.dumps({"duration": 10, "segments": [{"start": 0, "end": 9, "text": "Một câu."}]}), encoding="utf-8")
    after = floor.visual_mix_metrics(chapters, "topic", root=tmp_path)
    assert after["text_seconds"] == 10
    assert len(after["estimated"]) == 1
