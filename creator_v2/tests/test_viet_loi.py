import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import viet_loi as V  # noqa: E402

BODY = " ".join(["chữ"] * 50) + "."


def test_outline_chapters_from_ch_lines_or_line_count():
    assert V.outline_chapters("CH00 (~1 phút): mở\nCH01 · A\n\nCH08 · Kết\n") == ["CH00", "CH01", "CH08"]
    assert V.outline_chapters("Mở đầu\nChương một\nChương hai\n") == ["CH00", "CH01", "CH02"]


def test_missing_chapters_counts_empty_placeholder():
    got = f"## CH00 · A\n\n{BODY}\n\n## CH01 · B\n\n(Chưa có nội dung)\n"
    assert V.missing_chapters(got, ["CH00", "CH01", "CH02"]) == ["CH01", "CH02"]


def test_chapters_split_and_merge_order():
    a = f"## CH01 · B\n\n{BODY}\n"
    b = f"Đây là phần tiếp.\n\n## CH02 · C\n\n{BODY}\n\n## CH03 · D\n\n{BODY}\n"
    ch = {**V.chapters(b), **V.chapters(a)}
    assert sorted(ch) == ["CH01", "CH02", "CH03"]
    assert "Đây là phần tiếp" not in "".join(ch.values())


def test_headings_without_hashes_are_normalized():
    got = f"CH00 · Bản án\n\n{BODY}\n\n**CH01** · Arras\n\n{BODY}\n\n### CH2 - Giấy giả\n\n{BODY}\n"
    assert sorted(V.chapters(got)) == ["CH00", "CH01", "CH02"]
    assert V.chapters(got)["CH01"].startswith("## CH01 · Arras")
    assert V.missing_chapters(got, ["CH00", "CH01", "CH02"]) == []


def test_every_channel_has_profile():
    for c in ("CL", "MIM", "CK", "FS", "BUD"):
        text = V.instructions(c)
        assert f"Hồ sơ kênh {c}:" in text and "Giới hạn cứng" in text
    p = V.first_prompt("CL", ["h", "d", "g", "CH00 · a\nCH01 · b"])
    assert p.count("=====") == 10 and "tờ nhịp" in p  # #531 H2: lượt đầu là tờ nhịp


def test_wrong_part_flags_foreign_or_empty_chapters():
    from viet_loi import wrong_part
    outline = ["CH00", "CH01", "CH02", "CH03"]
    ok = "## CH02 · A\n\n" + "chữ " * 50 + "\n## CH03 · B\n\n" + "chữ " * 50
    assert wrong_part(ok, ["CH02", "CH03"], outline) == ""
    assert "không có chương" in wrong_part("Figuring out\nGemini said", ["CH02"], outline)
    # nhiễm chéo: chat của Long khác trả CH07 (24/11 Air Canada lẫn vào Dreyfus)
    assert "ngoài dàn chương" in wrong_part(ok + "\n## CH07 · C\n\nx", ["CH02", "CH03"], outline)


def test_first_prompt_asks_beat_sheet_with_channel_sample():
    texts = ["hồ sơ", "dữ kiện", "MẪU CŨ", "CH00 · Mở\nCH01 · Tiếp"]
    p = V.first_prompt("MIM", texts)
    assert "tờ nhịp" in p and "CÁI GIÁ" in p
    assert "Oppenheimer" in p and "MẪU CŨ" not in p
    assert "(#531" not in p
    assert "CH00 và CH01" in V.open_prompt()


def test_channel_without_sample_keeps_input_sample():
    assert V.channel_sample("XX", "MẪU CŨ") == "MẪU CŨ"


def test_fs_and_bud_have_channel_samples():
    for ch in ("FS", "BUD"):
        sample = V.channel_sample(ch, "MẪU CŨ")
        assert sample != "MẪU CŨ" and "Ví dụ 1" in sample
