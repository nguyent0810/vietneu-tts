"""Câu không có **cụm** thì key_parts không 'hot' -> ảnh tràn khung không bật thẻ cụt (Lead 12/11)."""
import hyperframes_bridge as HB
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_marked_phrase_is_hot():
    assert HB._key_parts("Chị sinh năm **Quý Hợi**.") == [{"t": "QUÝ HỢI", "hot": True}]


def test_unmarked_line_has_no_fallback():
    parts = HB._key_parts("Hai chữ Tý và Ngọ, mực son đỏ.")
    assert parts == []


def test_avoid_still_picks_other_mark():
    parts = HB._key_parts("**Tý** và **Ngọ đối đầu**", avoid="NGỌ ĐỐI ĐẦU")
    assert parts == [{"t": "TÝ", "hot": True}]


def test_media_tag_is_opt_in_and_trimmed():
    assert HB._media_tag({"kind": "image"}) is None
    assert HB._media_tag({"tag": "  Tê-mi-ya · 16 tuổi  "}) == "Tê-mi-ya · 16 tuổi"
    assert HB._media_tag({"tag": "   "}) is None


def test_unmarked_split_falls_back_to_full_with_camera():
    got = HB.assign_layouts_v2(
        {"1": {"kind": "image", "layout": "split"}}, "seed",
        script=["Câu không có cụm đánh dấu."], series="fs",
    )
    assert got[1]["layout"] == "full"
    assert got[1]["cine"]["cam"] in HB.CINE_CAMS


def test_handwritten_full_gets_distinct_adjacent_cameras():
    got = HB.assign_layouts_v2(
        {
            "1": {"kind": "image", "layout": "full", "w": 1600, "h": 900},
            "2": {"kind": "image", "layout": "full", "w": 1600, "h": 900},
        }, "stable-seed", script=["Một.", "Hai."], series="fs",
    )
    assert all(got[sid]["cine"] for sid in (1, 2))
    assert got[1]["cine"]["cam"] != got[2]["cine"]["cam"]


def test_full_wide_image_gets_pan():
    got = HB.assign_layouts_v2(
        {"1": {"kind": "image", "layout": "full", "w": 2200, "h": 1000}},
        "wide", script=["Toàn cảnh."], series="fs",
    )
    assert got[1]["pan"]["stops"][0]["line"] == 1
    assert got[1]["cine"] is None


def test_full_media_has_no_automatic_key_overlay_and_tag_is_opt_in():
    js = (ROOT / "hyperframes_short/compositions/longform.js").read_text(encoding="utf-8")
    engine = (ROOT / "hyperframes_short/compositions/engine.js").read_text(encoding="utf-8")
    full = js.split("    full: {", 1)[1].split("    split_r:", 1)[0]
    tag = engine.split("  function mediaTag(inner, m) {", 1)[1].split("\n  }", 1)[0]
    assert "lf-callout" not in full
    assert "m.tag" in tag
    assert "m.label" not in tag and "m.credit" not in tag


def test_local_video_clip_is_not_auto_cine_image():
    """Lead 17/11: render thử 072 dính cine tự gán lên clip local .mp4 (Temiya câu 9)."""
    from hyperframes_bridge import _layout_is_clip
    assert _layout_is_clip({"kind": "local", "path": "a/b/clip_1080p.mp4", "layout": "full"})
    assert not _layout_is_clip({"kind": "local", "path": "a/b/anh.jpg", "layout": "full"})
