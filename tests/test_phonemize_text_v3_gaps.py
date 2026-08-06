"""Regression tests cho `normalize_to_chunks_v3_with_gaps` (pathway v3turbo/
demo, dùng bởi `apps/gradio_main.py` và `src/vieneu/v3turbo.py`).

Codex review (Phase 2 remediation) chỉ ra: patch ban đầu chỉ sửa
`render_engine.normalize_preserving_paragraphs` + `core_utils.
split_text_into_chunks_with_gaps`, NHƯNG `normalize_to_chunks_v3_with_gaps`
có bước normalize RIÊNG (không dùng `normalize_preserving_paragraphs`) mà
VẪN rejoin bằng đúng 1 "\\n" như code cũ -- nếu không sửa, hàm này sẽ tự
GÂY RA regression mới: paragraph thật ("\\n\\n") bị hiểu nhầm thành ranh
giới câu ("sentence") sau khi splitter dùng chung đã patch, thay vì giữ
đúng "para" như hành vi cũ (dù cũ cũng sai theo hướng ngược lại cho input
"mỗi câu 1 dòng", nhưng ĐÚNG cho input có đoạn văn thật).

Đã sửa: `normalize_to_chunks_v3_with_gaps` giờ dùng CÙNG logic bảo toàn ranh
giới với `render_engine.normalize_preserving_paragraphs`. Test dưới đây khoá
lại hành vi ĐÚNG cho cả 2 loại input.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vieneu_utils.phonemize_text import normalize_to_chunks_v3_with_gaps


def test_v3_double_newline_stays_paragraph_boundary():
    """Regression cụ thể Codex đã chỉ ra: input có "\\n\\n" thật (đoạn văn)
    PHẢI vẫn ra "para", không được lặng lẽ đổi thành "sentence"."""
    text = "Đoạn một câu một. Đoạn một câu hai.\n\nĐoạn hai câu một."
    chunks, gaps = normalize_to_chunks_v3_with_gaps(text)
    assert gaps == ["para"]


def test_v3_single_newline_now_correctly_sentence_boundary():
    """Cùng bug gốc cũng ảnh hưởng pathway này -- nay đã sửa nhất quán."""
    text = "Câu một đây.\nCâu hai đây.\nCâu ba đây."
    chunks, gaps = normalize_to_chunks_v3_with_gaps(text)
    assert gaps == ["sentence", "sentence"]


def test_v3_mixed_boundaries():
    text = "Câu 1.\nCâu 2.\n\nĐoạn mới câu 1.\nĐoạn mới câu 2."
    chunks, gaps = normalize_to_chunks_v3_with_gaps(text)
    assert gaps == ["sentence", "para", "sentence"]


def test_v3_no_content_loss():
    text = "Câu một đây.\nCâu hai đây.\nCâu ba kết thúc."
    chunks, gaps = normalize_to_chunks_v3_with_gaps(text)
    assert len(chunks) == 3


def test_v3_emotion_cue_path_unaffected_by_newline_fix():
    """Đường có emotion cue ([cười]/<|emotion_k|>) -- xác nhận nhánh này
    KHÔNG bị đụng bởi patch theo hướng crash (không crash, vẫn hoạt động
    bình thường)."""
    text = "Câu vui [cười] thật đấy."
    chunks, gaps = normalize_to_chunks_v3_with_gaps(text)
    assert len(chunks) >= 1  # không crash, ra được ít nhất 1 chunk


# --- SỬA theo Codex review vòng 2: bản trước CHỈ bảo toàn ranh giới ở
# nhánh KHÔNG có emotion cue -- nhánh CÓ emotion cue (else) vẫn ghép mọi
# mảnh bằng dấu cách, làm mất hết "\n"/"\n\n" -- tái phát đúng bug gốc cho
# bất kỳ script nào có emotion marker xen giữa các đoạn. 2 test dưới đây
# khoá lại đúng case Codex chỉ ra.

def test_v3_paragraph_boundary_survives_with_emotion_cue_after():
    text = "Câu một.\n\nCâu hai [cười]."
    chunks, gaps = normalize_to_chunks_v3_with_gaps(text)
    assert "para" in gaps


def test_v3_sentence_boundary_survives_with_emotion_cue_before():
    text = "Câu một [cười].\nCâu hai."
    chunks, gaps = normalize_to_chunks_v3_with_gaps(text)
    assert "para" not in gaps


# --- SỬA theo Codex review vòng 3: 2 test trên đặt newline BÊN TRONG 1 mảnh
# text (không sát mép tag) nên không bắt được case newline nằm NGAY SÁT 1
# emotion tag -- Codex chỉ ra bản vòng-2 fix vẫn mất boundary trong 3 case
# dưới đây (root cause: tách theo tag TRƯỚC rồi mới xử lý newline, nên
# newline sát mép mảnh bị .strip() xoá mất). Đã sửa cấu trúc: tách theo
# NEWLINE TRƯỚC (độc lập hoàn toàn với vị trí tag), rồi mới xử lý emotion cue
# bên trong từng đoạn đã đảm bảo không còn newline nào.

@pytest.mark.parametrize("text", [
    "Câu một.\n\n[cười] Câu hai.",
    "Câu một [cười]\n\nCâu hai.",
    "Câu một.\n\n[cười][thở dài] Câu hai.",
])
def test_v3_paragraph_boundary_adjacent_to_emotion_tag(text):
    chunks, gaps = normalize_to_chunks_v3_with_gaps(text)
    assert "para" in gaps


# --- SỬA theo caveat Codex review vòng 4: `assert "para" in gaps` chỉ xác
# nhận CÓ para đâu đó, không xác nhận ĐÚNG SỐ LƯỢNG/VỊ TRÍ boundary cho case
# nhiều đoạn + nhiều tag xen kẽ. 3 test dưới đây khoá chính xác `gaps ==
# [...]` cho các case nhiều boundary Codex đề xuất.

def test_v3_exact_gaps_multiple_paragraphs_with_tag_between():
    text = "A.\n\n[cười]\n\nB."
    chunks, gaps = normalize_to_chunks_v3_with_gaps(text)
    assert gaps == ["para", "para"]


def test_v3_exact_gaps_multiple_paragraphs_with_two_tags_between():
    text = "A.\n\n[cười]\n\n[thở dài]\n\nB."
    chunks, gaps = normalize_to_chunks_v3_with_gaps(text)
    assert gaps == ["para", "para", "para"]


def test_v3_exact_gaps_tag_at_start_and_middle():
    text = "[cười]\n\nA.\n\n[thở dài]"
    chunks, gaps = normalize_to_chunks_v3_with_gaps(text)
    assert gaps == ["para", "para"]
