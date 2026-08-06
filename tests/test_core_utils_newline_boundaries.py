"""Regression tests cho patch "ranh giới câu/đoạn" (Phase 2 Audio Script audit).

Bug đã sửa: `split_text_into_chunks_with_gaps` từng gán CỨNG "para" cho MỌI
ranh giới `[\\r\\n]+`, bất kể 1 hay nhiều dấu xuống dòng liên tiếp -- khiến
script quy ước "mỗi câu 1 dòng" (FS/BUD) bị PHÂN LOẠI nhầm là ranh giới đoạn
văn thay vì đúng loại "sentence" (ranh giới câu).

Các test dưới đây khoá lại hành vi PHÂN LOẠI đúng: đúng 1 "\\n" -> "sentence";
>=2 "\\n" liên tiếp -> "para"; áp dụng cho cả \\n Unix lẫn \\r\\n Windows;
không mất/lặp/đảo thứ tự nội dung so với input gốc.

LƯU Ý (Phase 2 PASS WITH CAVEAT): phân loại "sentence" vs "para" ĐÃ ĐÚNG và
GIỮ NGUYÊN vĩnh viễn. ĐỘ DÀI SILENCE mặc định TOÀN CỤC (`V3_GAP_SILENCE`)
GIỮ NGUYÊN KHÔNG ĐỔI ("sentence": 0.18s) -- đây LÀ hành vi hiện tại, đang
sống của kênh Hình Sự (CL) và mọi nội dung có "sentence" đến từ ngắt trong
đoạn (không phải newline), hoàn toàn không liên quan bug đã sửa. Riêng
FS/BUD ("mỗi câu 1 dòng") cần override TƯỜNG MINH qua
`FS_BUD_SENTENCE_SAFE_DEFAULT` (0.35s, giữ đúng trải nghiệm nghe hiện tại
của họ) -- override này PHẢI được truyền rõ ràng ở call site
(`short_batch_runner.py`), KHÔNG suy luận tên kênh trong module này. Test
dưới đây khoá CẢ 2 hằng số, không phải hệ quả tình cờ của việc sửa logic
phân loại.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vieneu_utils.core_utils import (
    split_text_into_chunks_with_gaps,
    gaps_to_silence,
    _classify_newline_run,
    _collapse_blank_lines,
    V3_GAP_SILENCE,
    FS_BUD_SENTENCE_SAFE_DEFAULT,
)


# --- 1. Ranh giới câu (1 "\n") -> PHÂN LOẠI "sentence" ---------------------

def test_single_newline_is_sentence_boundary():
    text = "Câu một đây.\nCâu hai đây.\nCâu ba đây."
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    assert chunks == ["Câu một đây.", "Câu hai đây.", "Câu ba đây."]
    assert gaps == ["sentence", "sentence"]
    # Default TOÀN CỤC giữ nguyên 0.18s (hành vi CL hiện tại, không đổi).
    assert gaps_to_silence(gaps) == [0.18, 0.18]
    # FS/BUD override tường minh -> 0.35s (giữ trải nghiệm nghe hiện tại của
    # FS/BUD, xem PHASE2_FINAL_PATCH_SUMMARY.md).
    assert gaps_to_silence(gaps, silence_map=FS_BUD_SENTENCE_SAFE_DEFAULT) == [0.35, 0.35]


# --- 2. Ranh giới đoạn văn (>=2 "\n") -> pause 0.35s ("para") --------------

def test_double_newline_is_paragraph_boundary():
    text = "Đoạn một.\n\nĐoạn hai."
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    assert chunks == ["Đoạn một.", "Đoạn hai."]
    assert gaps == ["para"]
    assert gaps_to_silence(gaps) == [0.35]


def test_triple_newline_still_classified_as_paragraph():
    # >=2 dấu xuống dòng đều là "para", không chỉ đúng 2.
    text = "Đoạn một.\n\n\nĐoạn hai."
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    assert gaps == ["para"]


# --- 3. Trộn lẫn 1 và 2 "\n" trong cùng script -----------------------------

def test_mixed_single_and_double_newlines():
    text = "Câu 1.\nCâu 2.\n\nĐoạn mới câu 1.\nĐoạn mới câu 2."
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    assert chunks == ["Câu 1.", "Câu 2.", "Đoạn mới câu 1.", "Đoạn mới câu 2."]
    assert gaps == ["sentence", "para", "sentence"]


# --- 4. Windows (\r\n) vs Unix (\n) line endings ---------------------------

def test_windows_single_crlf_is_sentence_boundary():
    text = "Câu 1.\r\nCâu 2."
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    assert gaps == ["sentence"]


def test_windows_double_crlf_is_paragraph_boundary():
    text = "Đoạn 1.\r\n\r\nĐoạn 2."
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    assert gaps == ["para"]


def test_mixed_crlf_and_lf_in_same_text():
    text = "Câu 1.\r\nCâu 2.\n\nĐoạn mới.\nCâu khác."
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    assert gaps == ["sentence", "para", "sentence"]


# --- 5. CL — kịch bản dạng đoạn văn liền, không \n giữa câu ----------------

def test_cl_style_continuous_paragraph_no_newlines():
    text = (
        "Yakuza, tổ chức tội phạm Nhật Bản, có gốc từ hai nhóm bên lề xã hội. "
        "Khác với hầu hết tổ chức tội phạm khác, yakuza không hoạt động hoàn toàn ngầm. "
        "Đây không phải câu chuyện về một tổ chức bí ẩn vẫn hùng mạnh."
    )
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    # Không có "\n" nào trong input -> không có gap "para" nào (chỉ sentence/minor
    # tuỳ MAX_CHARS có buộc cắt hay không).
    assert "para" not in gaps


# --- 6. Không mất / lặp / đảo thứ tự nội dung ------------------------------

def test_no_content_loss_duplication_or_reordering_single_newline():
    sentences = ["Câu một đây.", "Câu hai đây có số 5.", "Câu ba kết thúc."]
    text = "\n".join(sentences)
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    assert chunks == sentences  # thứ tự + nội dung giữ nguyên tuyệt đối
    assert len(chunks) == len(sentences)  # không lặp, không mất


def test_no_content_loss_duplication_or_reordering_mixed_paragraphs():
    text = "Mở đầu câu A.\nMở đầu câu B.\n\nThân bài câu A.\nThân bài câu B.\n\nKết câu A."
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    expected = [
        "Mở đầu câu A.", "Mở đầu câu B.",
        "Thân bài câu A.", "Thân bài câu B.",
        "Kết câu A.",
    ]
    assert chunks == expected
    assert gaps == ["sentence", "para", "sentence", "para"]


def test_blank_line_with_only_whitespace_collapses_correctly():
    # 1 dòng "trống" chỉ chứa space giữa 2 lần xuống dòng phải được coi là
    # phần của cùng 1 ranh giới đoạn văn ("para"), không tạo ra 1 "đoạn" rỗng
    # xen giữa làm lệch phân loại.
    text = "Đoạn một.\n   \nĐoạn hai."
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    assert chunks == ["Đoạn một.", "Đoạn hai."]
    assert gaps == ["para"]


# --- Helper functions dùng riêng ------------------------------------------

def test_classify_newline_run_boundary_values():
    assert _classify_newline_run("\n") == "sentence"
    assert _classify_newline_run("\r\n") == "sentence"
    assert _classify_newline_run("\n\n") == "para"
    assert _classify_newline_run("\r\n\r\n") == "para"
    assert _classify_newline_run("\n\n\n") == "para"


def test_collapse_blank_lines_removes_whitespace_only_lines():
    assert _collapse_blank_lines("a\n   \nb") == "a\n\nb"
    assert _collapse_blank_lines("a\nb") == "a\nb"  # không đổi khi không có dòng trống


def test_v3_gap_silence_table_unchanged():
    # Khoá lại default TOÀN CỤC -- KHÔNG đổi bởi Phase 2, giữ đúng hành vi
    # CL hiện tại. Đổi bảng này phải cố ý, không phải vô tình khi sửa logic
    # phân loại.
    assert V3_GAP_SILENCE == {"para": 0.35, "sentence": 0.18, "minor": 0.04}


def test_fs_bud_sentence_safe_default_table_unchanged():
    # Khoá lại override RIÊNG cho FS/BUD (Phase 2 PASS WITH CAVEAT) -- cố ý
    # đặt "sentence" == "para" == 0.35s để giữ trải nghiệm nghe hiện tại của
    # FS/BUD, KHÔNG áp dụng cho CL (xem V3_GAP_SILENCE ở trên, giữ 0.18s).
    assert FS_BUD_SENTENCE_SAFE_DEFAULT == {"para": 0.35, "sentence": 0.35, "minor": 0.04}


def test_empty_and_whitespace_only_input():
    assert split_text_into_chunks_with_gaps("") == ([], [])
    assert split_text_into_chunks_with_gaps("   \n\n   ") == ([], [])
