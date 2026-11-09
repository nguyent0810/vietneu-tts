import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "motion" / "long"))
import opening_gate as og  # noqa: E402

TITLE = "TỂ TƯỚNG LƯU GÙ Ngoài Đời Thật: Hòa Thân — Kẻ Tham Nhất"


def line(text, start, step=0.3):
    words = text.split()
    return {"text": text, "start": start, "end": start + step * len(words),
            "words": [{"w": w, "t": start + i * step, "d": step} for i, w in enumerate(words)]}


GOOD_LINES = [line("Tể tướng Lưu Gù và Hòa Thân là ai?", 1.0)]
GOOD_SCENES = [{"type": "photo", "img": "a.jpg", "t0": 0, "t1": 60}]


def run(title=TITLE, scenes=GOOD_SCENES, lines=GOOD_LINES):
    return og.check(title, scenes, lines)


def has(errs, frag):
    return any(frag in e for e in errs)


def test_all_pass():
    assert run() == []


def test_rule1_title_keyword_pass_and_fail():
    assert not has(run(), "Từ khóa")
    late = [line("Một câu mở đầu rất dài " * 3 + "?", 1.0), line("Lưu Gù Hòa Thân", 40.0)]
    assert has(run(lines=late), "Từ khóa")


def test_rule1_person_only_with_colon_and_dash():
    assert og.title_phrases("TỂ TƯỚNG LƯU GÙ Ngoài Đời Thật")[0] == ["TỂ TƯỚNG"]
    assert og.title_phrases("X Y Ngoài Đời Thật: Tên Người")[0] == ["X Y"]
    assert og.title_phrases(TITLE)[0] == ["TỂ TƯỚNG", "Hòa Thân"]


def test_rule1_mata_hari_accent_insensitive():
    title = "MATA HARI Ngoài Đời Thật: Margaretha — Điệp viên"
    lines = [line("Mata Hari, tên thật Margaretha, một vũ nữ, bị xử bắn lúc bình minh, vì sao?", 5.0)]
    assert run(title=title, lines=lines) == []
    assert has(run(title=title, lines=[line("Bà vũ nữ ấy là ai?", 1.0)]), "MATA HARI")


def test_rule1_non_ip_title():
    title = "Vụ trộm 2 tỷ USD và Ngân Hàng Nhà Nước"
    ok = [line("Vụ trộm 2 tỷ USD ở Ngân Hàng Nhà Nước, vì sao?", 1.0)]
    assert run(title=title, lines=ok) == []
    assert has(run(title=title, lines=[line("Chuyện gì đã xảy ra?", 1.0), line("2 tỷ Ngân Hàng Nhà Nước", 30.0)]), "Từ khóa")


def test_rule2_question_block():
    spread = GOOD_LINES + [line("Ai? ", 40.0), line("Vì sao?", 70.0), line("Khi nào?", 85.0)]
    assert not has(run(lines=spread), "3 câu hỏi")
    block = GOOD_LINES + [line("Ai?", 40.0), line("Vì sao?", 50.0), line("Khi nào?", 58.0)]
    assert has(run(lines=block), "3 câu hỏi")


def test_rule3_early_visual():
    assert not has(run(), "5s đầu")
    late = [{"type": "kinetic", "t0": 0, "t1": 8}, {"type": "photo", "img": "a.jpg", "t0": 8, "t1": 60}]
    assert has(run(scenes=late), "5s đầu")


def test_rule4_bare_text():
    ok = GOOD_SCENES + [{"type": "kinetic", "t0": 5, "t1": 9}]
    assert not has(run(scenes=ok), "Cảnh chữ trống")
    bad = [{"type": "photo", "img": "a.jpg", "t0": 0, "t1": 3}, {"type": "kinetic", "t0": 3, "t1": 20}]
    assert has(run(scenes=bad), "Cảnh chữ trống")
    with_bg = [{"type": "photo", "img": "a.jpg", "t0": 0, "t1": 3}, {"type": "kinetic", "bg": "x.jpg", "t0": 3, "t1": 20}]
    assert not has(run(scenes=with_bg), "Cảnh chữ trống")


def test_rule5_big_question():
    assert not has(run(), "câu hỏi trong 45s")
    no_q = [line("Tể tướng Lưu Gù và Hòa Thân.", 1.0), line("Sao?", 60.0)]
    assert has(run(lines=no_q), "câu hỏi trong 45s")


def test_title_number_matches_spoken_number_words():
    for title, said in (("Vụ Án 100 Triệu Đô", "một trăm triệu"),
                        ("Sụp Đổ Năm 2019", "hai nghìn không trăm mười chín"),
                        ("Con Số 1,2 Tỷ", "một phẩy hai tỷ")):
        errs = og.check(title, GOOD_SCENES, [line("Câu mở " + said + " là ai?", 1.0)])
        assert not has(errs, "Từ khóa"), (title, errs)


def test_title_number_still_fails_when_not_spoken_and_accepts_digits():
    assert has(og.check("Vụ Án 100 Triệu Đô", GOOD_SCENES, [line("Câu mở đầu là ai?", 1.0)]), "Từ khóa")
    assert not has(og.check("Vụ Án 100 Triệu Đô", GOOD_SCENES, [line("Có 100 triệu đô là ai?", 1.0)]), "Từ khóa")
