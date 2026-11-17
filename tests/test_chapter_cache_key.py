"""Chapter cache keys ignore the chapter's absolute position in the video."""

import hf_batch_render as R


def _row():
    return {
        "script": ["**Chương 1**", "Câu một.", "**Chương 2**", "Câu hai.", "Câu ba."],
        "style": "inkwash_long",
        "media": {"4": {"kind": "image", "query": "cảnh núi"}},
        "visuals": {},
    }


def _key(row, segments):
    return R.chapter_key(row, 2, 5, segments[2]["start"], segments[4]["end"], "looks",
                         segments=segments, chapter_base=1)


def test_prior_chapter_duration_does_not_invalidate_later_chapters():
    row = _row()
    row["style"] = "vhs"  # exercise position-independent cache keys
    original = [
        {"start": 0, "end": 1}, {"start": 1, "end": 129},
        {"start": 130, "end": 131}, {"start": 131, "end": 133}, {"start": 133, "end": 135},
    ]
    # Chapter 1 gets longer; chapter 2 shifts by five seconds but its local
    # duration and each sentence's local boundaries stay unchanged.
    shifted = [
        {"start": 0, "end": 1}, {"start": 1, "end": 134},
        {"start": 135, "end": 136}, {"start": 136, "end": 138}, {"start": 138, "end": 140},
    ]
    assert _key(row, original) == _key(row, shifted)


def test_chapter_text_or_media_change_invalidates_key():
    segments = [
        {"start": 0, "end": 1}, {"start": 1, "end": 4},
        {"start": 5, "end": 6}, {"start": 6, "end": 8}, {"start": 8, "end": 10},
    ]
    row = _row()
    base = _key(row, segments)
    changed_text = _row()
    changed_text["script"][3] = "Câu hai đã sửa."
    assert _key(changed_text, segments) != base
    changed_media = _row()
    changed_media["media"]["4"]["query"] = "cảnh biển"
    assert _key(changed_media, segments) != base


def test_chapter_sentence_duration_change_invalidates_key():
    row = _row()
    segments = [
        {"start": 0, "end": 1}, {"start": 1, "end": 4},
        {"start": 5, "end": 6}, {"start": 6, "end": 8}, {"start": 8, "end": 10},
    ]
    changed = [dict(s) for s in segments]
    changed[3]["end"] = 9.0
    changed[4]["start"] = 9.0
    changed[4]["end"] = 11.0
    assert _key(row, changed) != _key(row, segments)


def _position_key(row, t0, total=400):
    segments = [{"start": 0, "end": 1}, {"start": t0, "end": t0 + 1},
                {"start": t0 + 1, "end": t0 + 3}, {"start": t0 + 3, "end": t0 + 5}]
    return R.chapter_key(row, 1, 4, t0, t0 + 5, "looks", segments=segments,
                         chapter_base=1, seg_total=total)


def test_later_chapter_keeps_key_when_prior_chapter_grows():
    row = _row()
    row["style"] = "vhs"
    assert _position_key(row, 130, 400) == _position_key(row, 150, 420)


def test_early_chapter_position_invalidates_key():
    row = _row()
    row["style"] = "vhs"
    assert _position_key(row, 20) != _position_key(row, 30)


def test_all_long_styles_keep_later_chapter_key_when_prior_chapter_grows():
    for style in ("studio_long", "moon_long", "lacquer_long", "dongho_long",
                  "inkwash_long", "ember_long", "laban_long"):
        row = _row()
        row["style"] = style
        assert _position_key(row, 130, 400) == _position_key(row, 150, 420), style


def test_chapter_bridge_opts_keep_whole_video_timing():
    opts = R.chapter_render_opts(137.25, 902.5, video_only=True)
    assert opts == {"video_only": True, "seg_off": 137.25, "seg_total": 902.5}
