"""Regression fixtures cho G3 (Audio Generation remediation, finding D2):
karaoke word-highlight timing phải dùng ĐÚNG 1 canonical normalized token
stream cho cả synthesis lẫn việc gắn is_important, không phải 2 nguồn tách
biệt dễ lệch nhau.

Bug gốc (CONFIRMED bởi Codex CLI review, chạy normalizer thật): trước
fix, ``_short_tts_render.py::strip_importance_markers()`` tính
important_indices bằng ``text.split()`` trên text CHƯA normalize, trong
khi ``render_short.py::known_transcript_from_segments()`` tính lại
global_word_offset trên segments CỦA MANIFEST đã normalize (số/ngày
tháng/viết tắt có thể bị mở rộng thành nhiều từ hơn, vd "123" -> "một
trăm hai mươi ba" 1->5 từ). 2 chỉ số lệch nhau ngay khi có normalize thay
đổi số lượng từ TRƯỚC hoặc TRONG phrase đánh dấu -- karaoke highlight trỏ
sai từ.

Fix: strip_importance_markers() giờ tự normalize (dùng lại
render_engine._normalize_paragraphs/_rejoin_paragraphs -- CHÍNH XÁC 2 hàm
mà normalize_preserving_paragraphs() dùng nội bộ) rồi định vị lại phrase
đánh dấu SAU normalize qua kỹ thuật sentinel-word, đảm bảo text trả về
BYTE-IDENTICAL với text sẽ đưa cho session.render_text(...,
already_normalized=True) -- một token stream canonical duy nhất.

AN TOÀN NỘI DUNG: phát hiện thêm trong lúc sửa (không có trong audit gốc)
-- 1 số rule normalize NHẠY NGỮ CẢNH (vd "ngày" đứng liền TRƯỚC ngày-tháng)
cho kết quả KHÁC khi sentinel chen vào giữa. Nếu không validate, sẽ có
nguy cơ TTS đọc THÊM TỪ không có trong kịch bản gốc -- lỗi nghiêm trọng
hơn cả bug D2 ban đầu. strip_importance_markers() validate: sentinel-based
text PHẢI khớp y hệt naive-normalized text, không khớp thì bỏ highlight,
KHÔNG bao giờ đổi nội dung thật sự đưa vào TTS."""
import re

from _short_tts_render import _IMPORTANT_MARKER_RE, strip_importance_markers
from render_engine import normalize_preserving_paragraphs


def _naive_normalized(text: str) -> str:
    """Text sẽ ĐƯỢC ĐỌC nếu bóc ** đơn giản rồi normalize thẳng -- nguồn sự
    thật độc lập để kiểm tra strip_importance_markers() không bao giờ đổi
    nội dung thật sự đưa vào TTS."""
    return normalize_preserving_paragraphs(_IMPORTANT_MARKER_RE.sub(lambda m: m.group(1), text))


def _assert_content_safe(raw_text: str):
    """Bất biến BẮT BUỘC cho MỌI input: text trả về từ
    strip_importance_markers() phải giống hệt normalize không sentinel --
    important-marker computation KHÔNG BAO GIỜ được phép đổi nội dung sẽ
    đọc."""
    clean_text, _ = strip_importance_markers(raw_text)
    assert clean_text == _naive_normalized(raw_text), (
        "strip_importance_markers() đã LÀM THAY ĐỔI nội dung sẽ đọc so với "
        "normalize không đánh dấu -- vi phạm an toàn nội dung."
    )


# ─── Fixture: số (Codex example, 5->9 từ) ─────────────────────────────

def test_number_expansion_marks_all_expanded_words():
    raw = "Tôi có **123** con mèo."
    clean, idx = strip_importance_markers(raw)
    _assert_content_safe(raw)
    words = clean.split()
    assert words == "tôi có một trăm hai mươi ba con mèo.".split()
    assert [words[i] for i in idx] == ["một", "trăm", "hai", "mươi", "ba"]


# ─── Fixture: ngày tháng (Codex example, 3->15 từ) -- rơi vào nhánh AN
# TOÀN NỘI DUNG (rule "ngày" nhạy ngữ cảnh) -- content vẫn ĐÚNG, chỉ mất
# highlight ─────────────────────────────────────────────────────────────

def test_date_expansion_is_content_safe_even_when_highlight_is_dropped():
    raw = "Hẹn ngày **21/02/2025** nhé."
    clean, idx = strip_importance_markers(raw)
    _assert_content_safe(raw)
    # Nội dung ĐÚNG (không thừa "ngày") dù highlight có thể rỗng.
    assert clean == "hẹn ngày hai mươi mốt tháng hai năm hai nghìn không trăm hai mươi lăm nhé."
    assert "ngày ngày" not in clean, "TUYỆT ĐỐI không được thừa từ so với bản không đánh dấu"


# ─── Fixture: viết tắt (Codex example, 4->8 từ) ────────────────────────

def test_abbreviation_expansion_marks_all_expanded_words():
    raw = "**TP.HCM** có 2 người."
    clean, idx = strip_importance_markers(raw)
    _assert_content_safe(raw)
    words = clean.split()
    assert words == "thành phố hồ chí minh có hai người.".split()
    assert [words[i] for i in idx] == ["thành", "phố", "hồ", "chí", "minh"]


# ─── Fixture: dấu câu dính sát marker (không khoảng trắng đệm) ────────

def test_marker_adjacent_to_terminal_punctuation():
    raw = "Kết thúc bằng **từ cuối**."
    clean, idx = strip_importance_markers(raw)
    _assert_content_safe(raw)
    words = clean.split()
    assert words[-1] == "cuối."  # dấu chấm PHẢI dính đúng từ cuối phrase, không mồ côi
    assert [words[i] for i in idx] == ["từ", "cuối."]


def test_marker_adjacent_to_comma_and_exclaim():
    raw = "Rất **quan trọng**, nhớ nhé!"
    clean, idx = strip_importance_markers(raw)
    _assert_content_safe(raw)
    words = clean.split()
    assert [words[i] for i in idx] == ["quan", "trọng,"]


# ─── Fixture: token count không đổi (baseline, không có số/ngày/viết tắt) ─

def test_plain_phrase_no_token_count_change():
    raw = "Đây là **quan trọng** và bình thường."
    clean, idx = strip_importance_markers(raw)
    _assert_content_safe(raw)
    words = clean.split()
    assert [words[i] for i in idx] == ["quan", "trọng"]


# ─── Fixture: không có marker nào ─────────────────────────────────────

def test_no_markers_returns_empty_indices():
    raw = "Không có gì đánh dấu ở đây cả."
    clean, idx = strip_importance_markers(raw)
    _assert_content_safe(raw)
    assert idx == []
    assert "*" not in clean


# ─── Fixture: nhiều đoạn (giữ đúng ranh giới \n/\n\n, xem G1/Phase 2) ──

def test_multi_paragraph_boundary_preserved_with_marker_at_edge():
    raw = "Đoạn một có chữ.\n\n**Đoạn hai** bắt đầu bằng từ quan trọng."
    clean, idx = strip_importance_markers(raw)
    _assert_content_safe(raw)
    assert "\n\n" in clean, "ranh giới ĐOẠN VĂN (>=2 dấu xuống dòng) phải được giữ nguyên"
    words = clean.split()
    assert [words[i] for i in idx] == ["đoạn", "hai"]


def test_marker_spanning_sentence_boundary_within_paragraph():
    raw = "Câu một.\nCâu **hai quan trọng**.\nCâu ba."
    clean, idx = strip_importance_markers(raw)
    _assert_content_safe(raw)
    assert clean.count("\n") == 2 and "\n\n" not in clean, "ranh giới CÂU (1 dấu xuống dòng) phải được giữ nguyên"
    words = clean.split()
    assert [words[i] for i in idx] == ["hai", "quan", "trọng."]


# ─── Fixture: nhiều marker trong cùng 1 script (chỉ số cộng dồn đúng) ──

def test_multiple_markers_accumulate_indices_correctly():
    raw = "Có **123** con mèo và **456** con chó."
    clean, idx = strip_importance_markers(raw)
    _assert_content_safe(raw)
    words = clean.split()
    marked = [words[i] for i in idx]
    assert marked == ["một", "trăm", "hai", "mươi", "ba", "bốn", "trăm", "năm", "mươi", "sáu"]


# ─── End-to-end: mô phỏng render_short.py::known_transcript_from_segments()
# (KHÔNG import render_short.py trực tiếp được -- nó cần video_tool_clone
# venv riêng với PySide6..., không có trong .venv repo này; xem docstring
# _short_tts_render.py). Copy tối giản đúng thuật toán word-offset thuần
# Python từ render_short.py để xác nhận alignment ĐẦU-CUỐI thật sự đúng,
# không chỉ đúng ở strip_importance_markers() một mình. Nếu sửa thuật
# toán gốc trong render_short.py, nhớ đồng bộ lại đây.

def _segment_to_word_timestamps(text, start, end, global_word_offset, important_indices):
    words = text.strip().split()
    if not words:
        return []
    duration = max(end - start, 0.001)
    total_chars = sum(len(w) for w in words) or 1
    out = []
    cursor = start
    for i, w in enumerate(words):
        share = len(w) / total_chars
        w_dur = duration * share
        out.append({"word": w, "start": cursor, "end": cursor + w_dur,
                     "is_important": (global_word_offset + i) in important_indices})
        cursor += w_dur
    return out


def _simulate_manifest_segments(clean_text: str, n_segments: int) -> list[str]:
    """Chia text thành N segment giả lập cách render_engine.py chunk text
    thật (chia theo từ, KHÔNG cắt giữa từ) -- mô phỏng manifest["segments"]
    thật sẽ có nhiều chunk cho script dài."""
    words = clean_text.split()
    n_segments = max(1, min(n_segments, len(words)))
    per = max(1, len(words) // n_segments)
    segments = []
    for i in range(0, len(words), per):
        segments.append(" ".join(words[i:i + per]))
    return segments


def test_end_to_end_alignment_across_multiple_manifest_segments():
    """Mô phỏng ĐẦY ĐỦ luồng thật: _short_tts_render.py tính important_indices
    trên canonical text -> giả lập text đó bị CHIA THÀNH NHIỀU SEGMENT
    (giống manifest thật khi script dài hơn MAX_CHARS) -> render_short.py
    cộng dồn global_word_offset qua từng segment -- xác nhận is_important
    vẫn gắn ĐÚNG từ dù xuyên qua nhiều segment, với đúng các ví dụ Codex
    đã dùng để confirm bug D2."""
    raw = "Hôm nay tôi có **123** con mèo rất dễ thương và ngoan."
    clean, important_indices = strip_importance_markers(raw)
    _assert_content_safe(raw)

    segments_text = _simulate_manifest_segments(clean, n_segments=3)
    assert len(segments_text) >= 2, "test cần >=2 segment để xác nhận cộng dồn offset xuyên segment"

    global_word_offset = 0
    all_words = []
    for i, seg_text in enumerate(segments_text):
        words = _segment_to_word_timestamps(
            seg_text, start=float(i), end=float(i) + 1.0,
            global_word_offset=global_word_offset, important_indices=set(important_indices),
        )
        all_words.extend(words)
        global_word_offset += len(seg_text.split())

    marked_words = [w["word"] for w in all_words if w["is_important"]]
    assert marked_words == ["một", "trăm", "hai", "mươi", "ba"], (
        f"karaoke highlight lệch từ khi xuyên qua nhiều segment: {marked_words}"
    )
    # Toàn bộ text ghép lại từ các segment phải khớp đúng canonical text.
    assert " ".join(w["word"] for w in all_words) == clean


def test_end_to_end_alignment_with_content_safe_fallback_no_false_highlight():
    """Khi rơi vào nhánh an toàn nội dung (important_indices rỗng do rule
    ngữ cảnh), luồng đầu-cuối KHÔNG được tự tạo ra highlight giả -- toàn
    bộ is_important phải False."""
    raw = "Hẹn ngày **21/02/2025** nhé."
    clean, important_indices = strip_importance_markers(raw)
    assert important_indices == []

    words = _segment_to_word_timestamps(
        clean, start=0.0, end=3.0, global_word_offset=0, important_indices=set(important_indices),
    )
    assert all(not w["is_important"] for w in words)
