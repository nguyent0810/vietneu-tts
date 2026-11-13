import sys
from pathlib import Path

import pytest

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
    pytest.importorskip("vieneu_utils.phonemize_text")
    for title, said in (("Vụ Án 100 Triệu Đô", "một trăm triệu"),
                        ("Sụp Đổ Năm 2019", "hai nghìn không trăm mười chín"),
                        ("Con Số 1,2 Tỷ", "một phẩy hai tỷ")):
        errs = og.check(title, GOOD_SCENES, [line("Câu mở " + said + " là ai?", 1.0)])
        assert not has(errs, "Từ khóa"), (title, errs)


def test_title_number_still_fails_when_not_spoken_and_accepts_digits():
    assert has(og.check("Vụ Án 100 Triệu Đô", GOOD_SCENES, [line("Câu mở đầu là ai?", 1.0)]), "Từ khóa")
    assert not has(og.check("Vụ Án 100 Triệu Đô", GOOD_SCENES, [line("Có 100 triệu đô là ai?", 1.0)]), "Từ khóa")


def test_decimal_matches_colloquial_speech():
    pytest.importorskip("vieneu_utils.phonemize_text")
    cases = (("sổ 1,2 tỷ", "một tỷ hai"),
             ("sổ 1,5 triệu", "một triệu rưỡi"),
             ("sổ 1,5 triệu", "một triệu năm"))
    for title, said in cases:
        errs = og.check(title, GOOD_SCENES, [line("Câu mở nói " + said + ", vì sao?", 1.0)])
        assert not has(errs, "Từ khóa"), (title, said, errs)


def test_decimal_colloquial_does_not_match_a_longer_number():
    errs = og.check("sổ 1,2 tỷ", GOOD_SCENES, [line("Câu mở nói một tỷ hai mươi, vì sao?", 1.0)])
    assert has(errs, "1,2")


def test_ck_e4_title_matches_spoken_mot_ty_hai():
    pytest.importorskip("vieneu_utils.phonemize_text")
    title = "Gửi 1,2 Tỷ, Ngân Hàng Phá Sản: Chỉ Được Trả 350 Triệu?"
    said = ("Gửi một tỷ hai ở một ngân hàng, ngân hàng ấy phá sản: "
            "khoản chắc chắn được trả là ba trăm năm mươi triệu. Phần còn lại thì sao?")
    errs = og.check(title, GOOD_SCENES, [line(said, 0.0)])
    assert not has(errs, "1,2"), errs
    assert not has(errs, "350"), errs


def test_o2b_continuous_bare_text_over_three_seconds():
    base = [{"type": "photo", "img": "a.jpg", "t0": 0, "t1": 40}]
    exact = base + [{"type": "kinetic", "t0": 10, "t1": 13.0}]
    assert not has(og.check(TITLE, exact, GOOD_LINES), "O2b")
    over = base + [{"type": "kinetic", "t0": 10, "t1": 13.1}]
    assert has(og.check(TITLE, over, GOOD_LINES), "O2b")
    gap = base + [{"type": "kinetic", "t0": 10, "t1": 12.5}, {"type": "slam", "t0": 13, "t1": 15.5}]
    assert not has(og.check(TITLE, gap, GOOD_LINES), "O2b")
    joined = base + [{"type": "kinetic", "t0": 10, "t1": 12}, {"type": "question", "t0": 12, "t1": 14.5}]
    assert has(og.check(TITLE, joined, GOOD_LINES), "O2b")
    covered = [{"type": "kinetic", "bg": "x.jpg", "t0": 0, "t1": 10}, {"type": "photo", "img": "a.jpg", "t0": 0, "t1": 40}]
    assert not has(og.check(TITLE, covered, GOOD_LINES), "O2b")


def test_o6_meta_speech_in_first_40_seconds():
    for phrase in ("trong video này", "video hôm nay", "chương một", "hãy cùng", "đăng ký kênh"):
        lines = GOOD_LINES + [line("Xin " + phrase + " nhé.", 10.0)]
        assert has(og.check(TITLE, GOOD_SCENES, lines), phrase), phrase
    late = GOOD_LINES + [line("Xin trong video này nhé.", 41.0)]
    assert not has(og.check(TITLE, GOOD_SCENES, late), "O6")



def test_new_opening_warnings_do_not_block():
    with pytest.warns(UserWarning):
        errs = og.check("Tiền của bạn", GOOD_SCENES, [line("Bạn mất tiền khi ngân hàng phá sản.", 0)], legacy=False)
    assert not has(errs, "câu hỏi trong 45s")


def test_new_o6_boundaries_and_legacy_unchanged():
    for text in ("Xin chào các bạn", "Hôm nay chúng ta sẽ tìm hiểu ba phần"):
        with pytest.warns(UserWarning):
            assert has(og.check(TITLE, GOOD_SCENES, GOOD_LINES + [line(text, 10)], legacy=False), "O6")
        with pytest.warns(UserWarning):
            assert not has(og.check(TITLE, GOOD_SCENES, GOOD_LINES + [line(text, 30)], legacy=False), "O6")
    assert not has(og.check(TITLE, GOOD_SCENES, GOOD_LINES + [line("Xin chào các bạn", 10)]), "O6")


def test_retention_findings_and_legacy_registry(tmp_path):
    assert any("5s" in x for x in og.retention_findings("Khoản tiền", [line("Một buổi sáng yên bình", 0)]))
    assert not any("5s" in x for x in og.retention_findings("Tiền của bạn", [line("Bạn mất tiền khi mua hàng", 0)]))
    p = tmp_path / "data" / "long" / "_legacy_topics.json"
    p.parent.mkdir(parents=True)
    p.write_text('["old"]', encoding="utf-8")
    assert og.is_legacy("old", tmp_path)
    assert not og.is_legacy("new", tmp_path)


def test_new_title_keyword_is_warning_legacy_still_blocks():
    lines = [line("Bạn mất tiền khi gặp rủi ro.", 0)]
    with pytest.warns(UserWarning) as seen:
        errors = og.check(TITLE, GOOD_SCENES, lines, legacy=False)
    assert not has(errors, "Từ khóa tiêu đề")
    assert any("Từ khóa tiêu đề" in str(w.message) for w in seen)
    assert has(og.check(TITLE, GOOD_SCENES, lines), "Từ khóa tiêu đề")
