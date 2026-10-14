"""Regression tests cho `render_engine.normalize_preserving_paragraphs` sau
patch "ranh giới câu/đoạn" (Phase 2 Audio Script audit) — end-to-end qua
normalize + `split_text_into_chunks_with_gaps` thật, đúng đường đi thật của
`RenderSession.render_text`.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from render_engine import normalize_preserving_paragraphs
from vieneu_utils.core_utils import split_text_into_chunks_with_gaps


def _end_to_end(text: str):
    normalized = normalize_preserving_paragraphs(text)
    return split_text_into_chunks_with_gaps(normalized, max_chars=256)


# --- Bảo toàn ranh giới câu/đoạn xuyên suốt normalize -> chunk-split -------

def test_sentence_boundary_survives_normalize_end_to_end():
    text = "Câu một đây.\nCâu hai đây.\nCâu ba đây."
    chunks, gaps = _end_to_end(text)
    assert gaps == ["sentence", "sentence"]


def test_paragraph_boundary_survives_normalize_end_to_end():
    text = "Đoạn một câu một. Đoạn một câu hai.\n\nĐoạn hai câu một."
    chunks, gaps = _end_to_end(text)
    assert gaps == ["para"]


def test_mixed_boundaries_survive_normalize_end_to_end():
    text = "Câu 1.\nCâu 2.\n\nĐoạn mới câu 1.\nĐoạn mới câu 2."
    chunks, gaps = _end_to_end(text)
    assert gaps == ["sentence", "para", "sentence"]


def test_windows_line_endings_survive_normalize_end_to_end():
    text = "Câu 1.\r\nCâu 2.\r\n\r\nĐoạn mới."
    chunks, gaps = _end_to_end(text)
    assert gaps == ["sentence", "para"]


def test_cl_style_continuous_paragraph_end_to_end():
    text = (
        "Yakuza có gốc từ hai nhóm bên lề xã hội thời Mạc phủ Tokugawa. "
        "Từ đầu thập niên 1990, Nhật Bản chuyển hướng sang trấn áp có hệ thống."
    )
    chunks, gaps = _end_to_end(text)
    assert "para" not in gaps


# --- Emotion marker: ĐÃ SỬA thật (không chỉ khoá hành vi cũ) -------------
#
# Round trước của remediation này CHỈ khoá lại hành vi CŨ (marker bị bóc
# ngoặc nhưng từ bên trong vẫn được đọc thành lời) -- Codex review chỉ ra
# đúng: điều đó KHÔNG thoả yêu cầu "unsupported emotion markers never being
# spoken aloud". Đã sửa thật bằng `_short_tts_render.strip_unsupported_
# emotion_markers()` (gọi TRƯỚC khi text vào `normalize_preserving_
# paragraphs`) -- test dưới đây xác nhận hành vi ĐÃ SỬA, chạy end-to-end
# đúng thứ tự thật của `_short_tts_render.main()`.

def test_recognized_emotion_marker_genuinely_removed_end_to_end():
    from _short_tts_render import strip_unsupported_emotion_markers
    raw = "Bạn thấy vui quá đi [cười] đúng không?"
    stripped = strip_unsupported_emotion_markers(raw)
    final = normalize_preserving_paragraphs(stripped)
    assert "cười" not in final  # từ bên trong marker THẬT SỰ không còn, sẽ không được đọc thành lời
    assert "bạn thấy vui" in final and "đúng không" in final  # phần còn lại nguyên vẹn


def test_emotion_token_syntax_genuinely_removed_end_to_end():
    from _short_tts_render import strip_unsupported_emotion_markers
    raw = "Câu bình thường <|emotion_1|> câu tiếp theo."
    stripped = strip_unsupported_emotion_markers(raw)
    final = normalize_preserving_paragraphs(stripped)
    assert "emotion_1" not in final and "<|" not in final
    assert "câu bình thường" in final and "câu tiếp theo" in final


def test_unrecognized_bracket_text_left_untouched():
    from _short_tts_render import strip_unsupported_emotion_markers
    raw = "Xem [chú thích riêng] ở đây."
    stripped = strip_unsupported_emotion_markers(raw)
    assert "[chú thích riêng]" in stripped  # không phải emotion marker -- không đụng vào


def test_emotion_marker_removal_does_not_merge_adjacent_words():
    """SỬA theo Codex review vòng 2: marker sát chữ 2 bên không có khoảng
    trắng đệm (vd "A[cười]B") trước đây bị xoá bằng chuỗi rỗng -> nối liền
    thành "AB", làm sai nội dung. Nay thay bằng khoảng trắng trước khi dọn
    whitespace thừa -- 2 từ phải tách rời nhau."""
    from _short_tts_render import strip_unsupported_emotion_markers
    raw = "Vui[cười]quá."
    stripped = strip_unsupported_emotion_markers(raw)
    assert "vuiquá" not in stripped.lower()
    assert "vui quá" in stripped.lower()


@pytest.mark.parametrize("raw,forbidden,expected", [
    ("Vui[cười].", " .", "Vui."),
    ("Thật sao[cười]?", " ?", "Thật sao?"),
    ("Được[cười]!", " !", "Được!"),
])
def test_emotion_marker_removal_does_not_leave_space_before_punctuation(raw, forbidden, expected):
    """SỬA theo Codex review vòng 3: bản vòng-2 chỉ dọn khoảng trắng thừa
    trước dấu PHẨY (",") -- marker sát dấu câu khác (. ; : ! ?) để lại
    khoảng trắng thừa (vd "Vui[cười]." -> "Vui ." thay vì "Vui."). Đã mở
    rộng cleanup sang đủ các dấu câu thường gặp."""
    from _short_tts_render import strip_unsupported_emotion_markers
    stripped = strip_unsupported_emotion_markers(raw)
    assert forbidden not in stripped
    assert stripped == expected


# --- Không mất / lặp / đảo thứ tự nội dung qua normalize -------------------

def test_no_content_loss_through_normalize_end_to_end():
    sentences = ["Câu một đây.", "Câu hai đây có số 5.", "Câu ba kết thúc."]
    text = "\n".join(sentences)
    chunks, gaps = _end_to_end(text)
    assert len(chunks) == 3
    # Nội dung chữ (không tính khoảng trắng/hoa-thường do normalize) phải khớp
    # thứ tự — kiểm tra bằng cách tách số để xác nhận không đảo thứ tự.
    assert "một" in chunks[0] and "hai" in chunks[1] and "ba" in chunks[2]


def test_no_duplication_through_normalize_end_to_end():
    text = "Câu A.\nCâu B.\nCâu C."
    chunks, gaps = _end_to_end(text)
    assert len(chunks) == 3  # không nhân đôi bất kỳ câu nào
    assert len(set(chunks)) == 3  # cả 3 chunk khác nhau (không lặp nội dung)


def test_empty_input_returns_empty():
    assert normalize_preserving_paragraphs("") == ""
    assert normalize_preserving_paragraphs("   \n\n   ") == ""
