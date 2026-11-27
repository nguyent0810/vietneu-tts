import os
import random
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import viet_loi_v3 as V  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _topic(tmp_path, slug="mim-test-a"):
    d = tmp_path / "data" / "long" / slug / "viet_loi_in"
    d.mkdir(parents=True)
    (d / "1_ho_so.md").write_text("# Hồ sơ truyện — Vụ thử\n\nKênh MIM.\n", encoding="utf-8")
    (d / "2_du_kien.md").write_text(
        "Nguồn chính: https://example.com/a.pdf (ĐÃ MỞ) và [báo](https://x.org/y) xem 2_du_kien.md, #548.\n"
        "Số liệu: 110 km.\n", encoding="utf-8")
    (d / "4_dan_chuong.md").write_text("CH00 · Mở (1 phút): cảnh mở\nCH01 · Hai: nhóm\n", encoding="utf-8")
    return d


def test_fill_template_leaves_no_placeholders(tmp_path):
    d = _topic(tmp_path)
    for loai in ("dai", "vua"):
        prompt, cont, used = V.build_prompt("MIM", "mim-test-a", loai, "NGHICH_LY", inputs=d, root=tmp_path / "data" / "long")
        assert not re.search(r"\{[A-Z_]+\}", prompt)
        assert "110 km" in prompt and "Vụ thử" in prompt
        assert "LƯỢT HAI" not in prompt and used[0] == "NGHICH_LY"
    assert "Viết tiếp" in cont


def test_fill_template_missing_value_raises():
    try:
        V.fill_template("a {X_Y} b", {})
    except ValueError as e:
        assert "X_Y" in str(e)
    else:
        raise AssertionError


def test_all_channels_have_rules_and_cach():
    for ch in ("CL", "MIM", "CK", "FS", "BUD"):
        luat, giong = V.channel_rules(ch)
        assert luat.startswith("Các điều bắt buộc") and giong
        desc = V.cach_descriptions()
        for c in V.CACH_KENH[ch]:
            assert c in desc, (ch, c)


def test_rotation_avoids_previous():
    for ch, pool in V.CACH_KENH.items():
        for last in pool:
            for seed in range(20):
                assert V.pick_cach(ch, {ch: {"last": last}}, rng=random.Random(seed)) != last
    assert V.pick_cach("MIM", {"MIM": {"last": "VONG_MO"}}, override="hoi_dap") == "HOI_DAP"


def test_tranh_lap_extraction(tmp_path):
    root = tmp_path / "long"
    now = time.time()
    for i, slug in enumerate(["mim-a", "mim-b", "mim-self", "ck-x", "mim-c"]):
        f = root / slug / "script.md"
        f.parent.mkdir(parents=True)
        f.write_text(f"## CH00 · Mở\n\nMở {slug} một. {{pd}}\nCâu hai của {slug}. ‖\nCâu ba của {slug}.\n\n## CH01 · B\n\nKhác.\n", encoding="utf-8")
        os.utime(f, (now - i * 100, now - i * 100))   # mim-a mới nhất
    out = V.tranh_lap("MIM", "mim-self", root)
    assert "Mở mim-a một. Câu hai của mim-a." in out
    assert "mim-self" not in out and "ck-x" not in out and "Câu ba" not in out and "{pd}" not in out
    assert out.index("mim-a") < out.index("mim-b") < out.index("mim-c")
    assert V.tranh_lap("CL", "cl-z", root).startswith("(chưa có")


def test_du_kien_strips_urls_and_files():
    t = V.strip_data("Nguồn: https://a.b/c.pdf (ĐÃ MỞ) xem notes.md và [báo](https://x.org/y) ticket #548.\nCó 5 triệu.")
    assert "http" not in t and ".md" not in t and "#548" not in t
    assert "báo" in t and "5 triệu" in t


def test_same_text():
    orig = "Đoạn một.\n\nĐoạn hai  có   khoảng trắng.\nĐoạn ba."
    ok = "## CH00 · Mở\n\nĐoạn một.\n\n## CH01 · Hai\n\nĐoạn hai có khoảng trắng. Đoạn ba.\n"
    assert V.same_text(orig, ok)
    assert not V.same_text(orig, ok.replace("Đoạn ba", "Đoạn bốn"))
    assert not V.same_text(orig, ok.replace("Đoạn một.", ""))
    assert V.same_text(orig, orig)


def test_heuristic_splitter():
    paras = [" ".join(["chữ"] * 120) + f" câu {i}." for i in range(40)]
    text = "\n\n".join(paras)
    for loai in ("dai", "vua"):
        out = V.heuristic_mark(text, loai)
        heads = [l for l in out.splitlines() if l.startswith("## ")]
        assert V.valid_headings(out) and V.same_text(text, out)
        assert heads[0] == "## CH00 · Phần 1"
        assert len(heads) == (6 if loai == "dai" else 5)
    short = V.heuristic_mark("Một đoạn.\n\nHai đoạn.", "dai")
    assert V.valid_headings(short) and V.same_text("Một đoạn.\n\nHai đoạn.", short)


def test_valid_headings():
    assert V.valid_headings("## CH00 · A\n\nx\n\n## CH01 · B\n\ny")
    assert not V.valid_headings("x\n\n## CH00 · A")
    assert not V.valid_headings("## CH00 · A\n\n## CH02 · B")
    assert not V.valid_headings("## Phần một\n\nx")


def test_stop_rules():
    hook = " ".join(["chữ"] * 200) + ". Nhưng điều gì đã xảy ra ở phía sau?"
    closed = " ".join(["chữ"] * 200) + ". Và cái cửa sổ ấy khép lại."
    assert V.stop_reason([hook]) == ""
    assert V.stop_reason([hook, hook]) == ""
    assert V.stop_reason([hook, "ngắn " * 50 + "Lát nữa ta sẽ biết?"])
    assert V.stop_reason([hook, closed])


def test_template_parts_cut_at_second_turn():
    body, cont = V.template_parts("dai")
    assert body.startswith("VAI TRÒ") and "LƯỢT HAI" not in body and not body.endswith("---")
    assert "{DU_KIEN}" in body and cont.startswith("Viết tiếp")


def test_save_json_drops_root_backref(tmp_path):
    root = {"v2": {"x": 1}}
    st = {"chat": "", "parts": []}
    st["_root"] = root
    root["v3"] = st
    f = tmp_path / "state.json"
    V.save_json(f, root)
    import json as _j
    assert _j.loads(f.read_text(encoding="utf-8")) == {"v2": {"x": 1}, "v3": {"chat": "", "parts": []}}
