import json

from research.hitl.history.history import (
    build_history,
    extract_features,
    first_frame_type,
    has_number,
    load_packages,
    main,
    opener_shape,
    summarize,
    title_shape,
)


def pkg(title="Một tiêu đề đơn giản", voice="Một câu bình thường.", frame="Ảnh AI: một căn phòng.",
        mech="moral_dilemma", pid="p", **extra):
    d = {"package_id": pid, "topic_id": "t", "title": title, "voice_0_3s": voice,
         "first_frame_0_1s": frame, "angle": {"mechanism": mech}}
    d.update(extra)
    return d


# --- classification -------------------------------------------------------

def test_opener_shapes_vietnamese():
    assert opener_shape("Ngày 21 tháng 2 năm 2025, Bybit phát hiện hoạt động lạ.") == "date"
    assert opener_shape("Năm 1909, người Pháp đo Fansipan bằng khí áp.") == "date"
    assert opener_shape("Có bao giờ bạn cảm thấy cuộc đời mình sao lắm chông gai?") == "question"
    assert opener_shape("'Tôi không còn đường lui', ông nói.") == "quote"
    assert opener_shape("Ở vùng Chí Linh, có một ngôi đền nằm giữa thung lũng.") == "scene"
    assert opener_shape("Mười sáu năm, mười sáu phép thử lớn.") == "statement"


def test_first_frame_types_vietnamese():
    assert first_frame_type("Bản đồ Hoàng Liên Sơn, Lào Cai sáng lên; chữ động '1909'.") == "map"
    assert first_frame_type("Sơ đồ chữ động: ô 'Bybit' nguyên vẹn, mũi tên đỏ.") == "text_card"
    assert first_frame_type("Chữ động trên nền đen đỏ: '3 · 7 · 13'.") == "text_card"
    # scene-led frame with overlaid text stays a scene
    assert first_frame_type("Ảnh AI: chiếc lọng trắng trong cung tối; chữ động '16 NĂM'.") == "scene"
    assert first_frame_type("Ảnh AI: núi Ngự Bình tĩnh lặng trong sương.") == "scene"
    assert first_frame_type("Ảnh chân dung nhà sư bạc đầu, nhìn thẳng vào camera.") == "portrait"
    assert first_frame_type("Một chiếc đồng xu vàng xoay trên mặt bàn gỗ.") == "object"
    assert first_frame_type("Cận cảnh khuôn mặt người đàn ông trong sương.") == "portrait"
    assert first_frame_type("") == "unknown"
    assert first_frame_type("Hình ảnh không rõ.") == "unknown"


def test_first_frame_english_keywords():
    assert first_frame_type("Map of the Mekong delta, route highlighted.") == "map"
    assert first_frame_type("Text card: 'THE TRUTH' on black") == "text_card"


def test_title_shapes_and_number():
    assert title_shape("Bybit nói không bị xâm nhập, vẫn mất hơn 1 tỷ USD") == "two_clause"
    assert title_shape("Hoàng tử giả câm điếc | Tiền Thân Temiya") == "two_clause"
    assert title_shape("Vì sao kinh thành Huế không quay mặt đúng hướng nam?") == "question"
    assert title_shape("14 Money Mistakes to AVOID in Your 20's") == "number_led"
    assert title_shape("Xem số phận tuổi Bính Ngọ") == "plain"
    assert has_number("Tam Nương: 3 mỹ nhân") is True
    assert has_number("Không có số") is False


def test_mechanism_from_angle_tags_and_unknown():
    assert extract_features(pkg(mech="broken expectations (2)"))["mechanism"] == "broken_expectations"
    assert extract_features(pkg(mech="power reversal"))["mechanism"] == "power_reversal"
    tagged = pkg(mech="power_reversal", tags_for_history=["mechanism:moral_dilemma", "x"])
    assert extract_features(tagged)["mechanism"] == "moral_dilemma"
    assert extract_features(pkg(tags_for_history={"mechanism": "hidden_vulnerability"}))["mechanism"] == "hidden_vulnerability"
    bare = {"title": "T"}
    assert extract_features(bare)["mechanism"] == "unknown"
    assert extract_features(bare)["opener_shape"] == "statement"
    assert extract_features(bare)["first_frame_type"] == "unknown"


# --- summary --------------------------------------------------------------

def test_summary_counts_and_observations():
    packages = []
    for i in range(10):
        title = "Bybit nói không, vẫn mất tiền" if i < 6 else "Một tiêu đề một vế"
        frame = "Sơ đồ chữ động: ô 'X'." if i < 7 else "Ảnh AI: một căn phòng."
        packages.append(pkg(title=title, frame=frame, mech="hidden_vulnerability" if i < 3 else "power_reversal", pid=f"p{i}"))
    h = build_history(packages, "fs", n=10)
    s = h["summary"]
    assert s["n_items"] == 10
    assert s["counts"]["first_frame_type"]["text_card"] == 7
    assert s["counts"]["title_shape"]["two_clause"] == 6
    assert s["counts"]["has_number"] == {"no": 10}
    assert "7/10 mở bằng thẻ chữ" in s["observations"]
    assert "6/10 title hai vế" in s["observations"]
    assert all(not o.startswith(("không", "nên", "tránh", "cấm")) for o in s["observations"])


def test_observations_need_repetition_not_single_items():
    s = summarize([extract_features(pkg(frame="Bản đồ Việt Nam.", pid="a")),
                   extract_features(pkg(frame="Ảnh AI: núi cao.", pid="b"))])
    assert "1/2" not in " ".join(s["observations"])
    assert not any("bản đồ" in o for o in s["observations"])  # only 1 map out of 2


def test_window_keeps_last_n_in_order():
    packages = [pkg(pid=f"p{i}") for i in range(12)]
    h = build_history(packages, "bud", n=10)
    assert [it["package_id"] for it in h["items"]] == [f"p{i}" for i in range(2, 12)]
    assert h["channel"] == "bud" and h["n"] == 10


# --- input shapes ---------------------------------------------------------

def test_accepts_three_input_shapes(tmp_path):
    single = tmp_path / "single.json"
    single.write_text(json.dumps(pkg(pid="s")), encoding="utf-8")
    listed = tmp_path / "list.json"
    listed.write_text(json.dumps([pkg(pid="a"), pkg(pid="b")]), encoding="utf-8")
    with_alts = tmp_path / "alts.json"
    primary = pkg(pid="main")
    primary["alternates"] = [pkg(pid="alt1"), pkg(pid="alt2")]
    with_alts.write_text(json.dumps(primary), encoding="utf-8")

    assert [p["package_id"] for p in load_packages([str(single)])] == ["s"]
    assert [p["package_id"] for p in load_packages([str(listed)])] == ["a", "b"]
    loaded = load_packages([str(with_alts)])
    assert [p["package_id"] for p in loaded] == ["main"]
    assert "alternates" not in loaded[0]


def test_directory_input_skips_non_packages(tmp_path):
    (tmp_path / "b.json").write_text(json.dumps(pkg(pid="b")), encoding="utf-8")
    (tmp_path / "a.json").write_text(json.dumps(pkg(pid="a")), encoding="utf-8")
    (tmp_path / "junk.json").write_text(json.dumps({"hello": 1}), encoding="utf-8")
    (tmp_path / "notes.md").write_text("ignored", encoding="utf-8")
    assert [p["package_id"] for p in load_packages([str(tmp_path)])] == ["a", "b"]


def test_cli_writes_output(tmp_path):
    src = tmp_path / "p.json"
    src.write_text(json.dumps([pkg(pid="x"), pkg(pid="y")]), encoding="utf-8")
    out = tmp_path / "history.json"
    assert main([str(src), "--channel", "ck", "--out", str(out)]) == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["channel"] == "ck"
    assert [it["package_id"] for it in data["items"]] == ["x", "y"]
    assert set(data["summary"]) == {"n_items", "counts", "observations"}
