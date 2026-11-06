"""GH-176: lặp có chủ đích được qua, đoạn bị ghép lặp vẫn bị chặn."""
from factory import integrity

LONG = "Đây là một câu dài có nhiều hơn tám từ để thử luật."
LONG2 = "Một câu dài thứ hai cũng có hơn tám từ trong đó."


def repeats(text):
    return [f for f in integrity.blocking(text) if f.code == "INT_REPEATED_SENTENCE"]


def filler(n):
    return " ".join(f"Câu xen số {i}." for i in range(n))


def test_issue_examples_pass():
    # long-mim-ai-voice: callback ngắn
    assert not repeats("Người nhân viên này không hề cả tin. Anh ta nghi ngờ. Mọi thứ diễn ra. Anh ta nghi ngờ.")
    # long-ck-c6: cấu trúc song song theo từng ngày T, T+1 (câu ngắn, có câu xen)
    s = "Ô cổ phiếu có thể bán vẫn là không."
    assert not repeats(f"Ngày T. {s} Ngày T+1. {s}")
    # long-ck-c6: callback câu dài cách xa (~5.000 ký tự)
    s = "Phiên đó có một trăm bốn mươi bảy mã giảm sàn."
    assert not repeats(f"{s} {filler(25)} {s}")


def test_adjacent_duplicate_blocked_any_length():
    assert repeats("Một câu. Một câu.")
    assert repeats(f"{LONG} {LONG}")


def test_single_long_sentence_with_gap_passes():
    assert not repeats(f"{LONG} Một câu xen. {LONG}")
    assert not repeats(f"{LONG} {filler(20)} {LONG}")


def test_duplicated_block_blocked_even_far_apart():
    block = f"Anh ta đi. {LONG2}"
    assert repeats(f"{block} {filler(40)} {block}")
    short_block = "Anh ta đi. Trời tối."
    assert repeats(f"{short_block} {filler(40)} {short_block}")


def test_short_refrain_far_apart_passes():
    assert not repeats(f"Hãy nhớ cái tên này. {filler(3)} Hãy nhớ cái tên này.")


def test_normalisation_still_applies():
    assert repeats(f"{LONG} {LONG.upper().replace('.', '!')}")


def test_one_word_count_block_passes():
    # Long yakuza (đã đăng): đếm điểm khi lật bài.
    assert not repeats("Chín. Ba. Lật thêm một lá. Chín. Ba.")
