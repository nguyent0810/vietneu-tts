import copy
import json
from pathlib import Path
from unittest.mock import patch

from motion.long import cine_auto
import motion.long.build_long as b


def test_sparse_images_and_text_windows():
    scenes = []
    for i in range(14):
        scene = {"type": "photo", "img": "a"} if i in (0, 4, 8, 12) else {"type": "kinetic", "bg": "a", "items": []}
        scene.update(t0=i * 240 / 14, t1=(i + 1) * 240 / 14)
        scenes.append(scene)
    cine_auto.Director("sparse").apply(scenes, {})
    assert cine_auto.window_stats(scenes)["under_3"] == 0
    cams = [s["cam"] for s in scenes if s.get("cam")]
    assert all(a != b for a, b in zip(cams, cams[1:]))
    assert all(s["cam"] in {"push_in", "pan"} for s in scenes if s["type"] == "kinetic")


def test_manual_and_motion_count():
    manual = {"type": "photo", "img": "a", "cam": "pan", "fx": "dust", "frame": True, "transition_in": "whip", "t0": 0, "t1": 120}
    original = copy.deepcopy(manual)
    cine_auto.Director("manual").apply([manual], {})
    assert manual == original
    assert cine_auto.window_stats([manual])["under_3"] == 1
    assert cine_auto.motion_kind({"type": "pano", "cam": "push_in"}) == "pano"
    assert cine_auto.motion_kind({"type": "broll", "cam": "push_in"}) == "video"


def test_html_selected_chapter_matches_all():
    names = ["ch01", "ch02", "ch03"]
    chapters = [(name, {"lines": [], "scenes": [{"type": "photo", "img": "a", "t0": 0, "t1": 5}]}) for name in names]
    spec = {"title": "test", "channel": "CL", "chapters": names, "imgs": {"a": "source"}, "cine_auto": True}
    writes = {}
    def record(path, text, **kwargs):
        writes[str(path)] = text
        return len(text)
    def read(path, **kwargs):
        return '{"duration": 5}'
    def planned(ch, *args):
        return copy.deepcopy(ch["scenes"])
    with patch.object(b, "load", return_value=(spec, chapters, Path("tmp_dry/cine_case"))), \
         patch.object(b, "_refuse_html_lint"), patch.object(b, "_refuse_craft"), patch.object(b, "_refuse_opening"), \
         patch.object(b.variety, "resolve_bgm"), patch.object(b.variety, "look", return_value={}), \
         patch.object(b.variety, "fonts_url", return_value=""), patch.object(b, "fetch_img", return_value={"w": 1920, "h": 1080}), \
         patch.object(b, "word_lines", return_value=[]), patch.object(b, "plan", side_effect=planned), \
         patch.object(b.sfx_long, "build"), patch.object(b, "mix_chapter"), patch.object(b, "late_first", return_value=[]), \
         patch.object(Path, "read_text", read), patch.object(Path, "write_text", record), \
         patch.object(Path, "mkdir"), patch.object(Path, "exists", return_value=True), \
         patch.object(b, "is_legacy_topic", return_value=True):
        b.do_html("sample")
        all_data = next(v for k, v in writes.items() if "ch02" in k and k.endswith("data.js"))
        writes.clear()
        b.do_html("sample", only={"ch02"})
        one_data = next(v for k, v in writes.items() if "ch02" in k and k.endswith("data.js"))
    def fields(data):
        scenes = json.loads(data.split("=", 1)[1].strip().rstrip(";"))["scenes"]
        return [{k: s.get(k) for k in ("cam", "fx", "transition_in")} for s in scenes]
    assert fields(all_data) == fields(one_data)
    assert not any("ch01" in k or "ch03" in k for k in writes)
