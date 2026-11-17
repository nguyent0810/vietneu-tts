import copy

import pytest

from motion.stier import build as B


def spec(lines, **kw):
    return {"lines": lines, **kw}


def test_comma_all_and_date_boundary():
    row = spec(["Một câu, {pd}", "Câu sau."], publish_at="2026-11-29T05:00:00Z")
    assert any("tách giữa chừng" in x for x in B.ear_issues(row)[0])
    row["publish_at"] = "2026-11-28T23:59:00Z"
    errors, warnings = B.ear_issues(row)   # #471: Short cũ trước 29/11 chỉ cảnh báo câu tách
    assert not errors and any("tách giữa chừng" in x for x in warnings)
    del row["publish_at"]
    assert B.ear_issues(row)[0]


@pytest.mark.parametrize("field", [{"theme": "case"}, {"story": True}, {"short_type": "S"}, {"test_cell": "A"}])
def test_story_source_density_counts_sentences(field):
    row = spec(["Theo hồ sơ, tài liệu ghi lại việc này.", "Wikipedia kể việc khác."], **field)
    errors, warnings = B.ear_issues(row)
    assert len(errors) == 1 and "2 câu rào nguồn" in errors[0]
    assert not warnings
    assert not B.ear_issues(spec([row["lines"][0]], **field))[0]


def test_other_formats_warn():
    errors, warnings = B.ear_issues(spec(["Theo hồ sơ, việc xảy ra.", "Wikipedia ghi l?i."], theme="mim"))
    assert not errors and len(warnings) == 1


def test_pd_clean_and_scene_intersections(monkeypatch):
    row = spec(["Một câu đầu.", "Câu tái dựng. {pd}", "Câu cuối."], theme="case",
               scenes=[{"type": "kinetic", "at": 0, "items": []},
                       {"type": "kinetic", "at": [1, None, 0, 0.2], "items": []}])
    original = copy.deepcopy(row)
    prepared = B.prepare_pd(row)
    assert row == original and prepared["lines"][1] == "Câu tái dựng."
    lines, dur = B.estimated_word_lines(prepared["lines"])
    monkeypatch.setattr(B.themes, "theme", lambda _: {"pools": {}})
    monkeypatch.setattr(B, "assign_beats", lambda *a, **kw: None)
    scenes = B.plan(prepared, lines, dur)
    assert scenes[0]["pd_ranges"] == [[lines[1]["start"], scenes[0]["t1"]]]
    assert scenes[1]["pd_ranges"] == [[scenes[1]["t0"], lines[1]["end"]]]
    engine = (B.HF / "assets/engine/casefile.js").read_text(encoding="utf-8")
    assert 's.pd_ranges || []' in engine and '"PHỎNG DỰNG"' in engine


def test_old_spec_unchanged():
    row = spec(["Câu. {pd}"], publish_at="2026-11-28")
    assert B.prepare_pd(row) is row


def test_preflight_guard_used_in_build_and_preflight(monkeypatch, tmp_path):
    import json
    row = spec(["Câu bị tách,"] * 60, theme="case", scenes=[])
    (tmp_path / "x.json").write_text(json.dumps(row, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(B, "SPECS", tmp_path)
    monkeypatch.setattr(B, "OUT", tmp_path)
    monkeypatch.setattr(B, "engine_registry", lambda: (set(), {}))
    monkeypatch.setattr(B, "retention_hook_lint", lambda *args: ([], []))
    monkeypatch.setattr(B, "dark_image_errors", lambda *args: [])
    errors, _ = B.preflight("x", allow_hook=True)
    assert any("tách giữa chừng" in e for e in errors)
    with pytest.raises(SystemExit, match="tách giữa chừng"):
        B.build("x", render=False)


def test_build_strips_pd_before_tts(monkeypatch, tmp_path):
    import json
    row = spec(["Câu tái dựng. {pd}"] * 3, theme="case", scenes=[])
    (tmp_path / "x.json").write_text(json.dumps(row, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(B, "SPECS", tmp_path)
    monkeypatch.setattr(B, "OUT", tmp_path)
    monkeypatch.setattr(B, "retention_hook_lint", lambda *a: ([], []))
    monkeypatch.setattr(B, "spec_preflight_errors", lambda *a: [])
    seen = {}

    def fake_speak(lines, *a, **kw):
        seen["lines"] = lines
        raise SystemExit("stop")
    monkeypatch.setattr(B, "speak", fake_speak)
    with pytest.raises(SystemExit, match="stop"):
        B.build("x", render=False)
    assert seen["lines"] == ["Câu tái dựng."] * 3
