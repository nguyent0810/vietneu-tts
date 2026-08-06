"""Regression test cho quyết định "kênh nào dùng silence override nào" --
Phase 2 PASS WITH CAVEAT (xem PHASE2_FINAL_PATCH_SUMMARY.md).

Quyết định NẰM Ở call site (`short_batch_runner._silence_map_for_topic`),
KHÔNG suy luận tên kênh trong `core_utils.py`/`render_engine.py`. Test dưới
đây khoá:
1. CL ("Hình Sự") giữ default hệ thống (None -> gaps_to_silence dùng
   V3_GAP_SILENCE, "sentence" = 0.18s) -- KHÔNG bị đụng vào.
2. FS ("Phong Thủy")/BUD ("Phật giáo") dùng override tường minh 0.35s.
3. Giá trị override cục bộ trong short_batch_runner.py PHẢI khớp hệt
   `vieneu_utils.core_utils.FS_BUD_SENTENCE_SAFE_DEFAULT` -- 2 module này
   không import lẫn nhau (short_batch_runner.py chạy dưới python3 hệ thống,
   không có vieneu_utils) nên phải khoá đồng bộ bằng test, tránh drift.
4. Ranh giới "para" GIỮ NGUYÊN 0.35s bất kể override nào (chỉ "sentence" bị
   ảnh hưởng).
5. Override CHỈ đổi độ dài silence -- không đổi nội dung/thứ tự chunk hay
   hành vi marker (emotion/importance).
"""
import sys
from pathlib import Path

import short_batch_runner as sbr

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from vieneu_utils.core_utils import (  # noqa: E402
    FS_BUD_SENTENCE_SAFE_DEFAULT,
    V3_GAP_SILENCE,
    gaps_to_silence,
    split_text_into_chunks_with_gaps,
)


def test_cl_topic_uses_system_default_none_override():
    assert sbr._silence_map_for_topic("Hình Sự") is None


def test_fs_and_bud_topics_use_explicit_override():
    assert sbr._silence_map_for_topic("Phong Thủy") == sbr._FS_BUD_SENTENCE_SAFE_DEFAULT
    assert sbr._silence_map_for_topic("Phật giáo") == sbr._FS_BUD_SENTENCE_SAFE_DEFAULT


def test_unknown_topic_raises_instead_of_silently_defaulting():
    """SỬA theo Codex review vòng 6: exact-match "im lặng" (topic lạ -> rơi
    về None -> CL default 0.18s) không fail-safe -- 1 lỗi chính tả nhỏ ở tên
    FS/BUD sẽ ÂM THẦM đổi pause 0.35s -> 0.18s mà không ai biết. Topic lạ
    PHẢI raise lỗi rõ ràng, không âm thầm coi là CL."""
    import pytest
    with pytest.raises(ValueError, match="Topic không hợp lệ"):
        sbr._silence_map_for_topic("Kênh Chưa Biết")


def test_typo_or_extra_whitespace_in_fs_bud_topic_raises_not_silently_falls_to_cl_default():
    """Case cụ thể Codex chỉ ra: "Phật giáo " (thừa khoảng trắng) trước đây sẽ
    âm thầm rơi về None (0.18s) -- nay PHẢI raise, không được âm thầm đổi."""
    import pytest
    with pytest.raises(ValueError):
        sbr._silence_map_for_topic("Phật giáo ")
    with pytest.raises(ValueError):
        sbr._silence_map_for_topic("phật giáo")  # sai case cũng phải raise, không tự case-fold


def test_local_override_constant_matches_core_utils_source_of_truth():
    """short_batch_runner.py không import được vieneu_utils (chạy dưới
    python3 hệ thống) nên định nghĩa lại giá trị -- test này chạy trong venv
    CÓ vieneu_utils, khoá đồng bộ 2 nơi để tránh drift."""
    assert sbr._FS_BUD_SENTENCE_SAFE_DEFAULT == FS_BUD_SENTENCE_SAFE_DEFAULT


def test_cl_sentence_pause_stays_0_18s_via_default_pipeline():
    """Mô phỏng đúng pipeline thật cho topic CL: silence_map=None ->
    gaps_to_silence dùng V3_GAP_SILENCE hệ thống."""
    text = "Câu một.\nCâu hai.\nCâu ba."
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    silence_map = sbr._silence_map_for_topic("Hình Sự")
    assert gaps_to_silence(gaps, silence_map=silence_map) == [
        V3_GAP_SILENCE["sentence"], V3_GAP_SILENCE["sentence"]
    ]
    assert V3_GAP_SILENCE["sentence"] == 0.18


def test_fs_bud_sentence_pause_becomes_0_35s_via_override():
    text = "Câu một.\nCâu hai.\nCâu ba."
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    for topic in ("Phong Thủy", "Phật giáo"):
        silence_map = sbr._silence_map_for_topic(topic)
        assert gaps_to_silence(gaps, silence_map=silence_map) == [0.35, 0.35]


def test_paragraph_pause_unchanged_regardless_of_topic_override():
    """Ranh giới "para" GIỮ NGUYÊN 0.35s cho cả CL lẫn FS/BUD -- override chỉ
    đụng "sentence", đúng yêu cầu "preserve paragraph pause behavior"."""
    text = "Đoạn một.\n\nĐoạn hai."
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    assert gaps == ["para"]
    for topic in ("Hình Sự", "Phong Thủy", "Phật giáo"):
        silence_map = sbr._silence_map_for_topic(topic)
        assert gaps_to_silence(gaps, silence_map=silence_map) == [0.35]


def test_override_does_not_change_chunk_content_or_order():
    """silence_map chỉ đổi độ dài im lặng lúc GHÉP audio -- không đụng vào
    bước tách chunk (nội dung/thứ tự text hoàn toàn giống nhau bất kể topic
    nào áp dụng override nào)."""
    text = "Câu một.\nCâu hai.\n\nĐoạn mới câu một.\nĐoạn mới câu hai."
    chunks_a, gaps_a = split_text_into_chunks_with_gaps(text)
    chunks_b, gaps_b = split_text_into_chunks_with_gaps(text)
    assert chunks_a == chunks_b
    assert gaps_a == gaps_b
    # gaps_to_silence với 2 map khác nhau không mutate lại `gaps` gốc.
    _ = gaps_to_silence(gaps_a, silence_map=sbr._FS_BUD_SENTENCE_SAFE_DEFAULT)
    assert gaps_a == gaps_b == ["sentence", "para", "sentence"]


def test_override_does_not_change_emotion_or_importance_marker_behavior():
    """Override silence hoàn toàn tách biệt khỏi strip_unsupported_emotion_
    markers/strip_importance_markers -- 2 cơ chế đó xử lý TEXT trước khi ra
    gaps, không liên quan tới silence_map."""
    from _short_tts_render import strip_unsupported_emotion_markers, strip_importance_markers
    raw = "Bạn thấy vui **quá đi** [cười] đúng không?"
    stripped = strip_unsupported_emotion_markers(raw)
    clean, important = strip_importance_markers(stripped)
    assert "cười" not in clean
    assert important  # marker ** vẫn được ghi nhận is_important bình thường
    # Hành vi này giống hệt bất kể topic/silence_map nào sẽ áp dụng sau đó
    # (2 bước strip chạy TRƯỚC khi biết silence_map, độc lập hoàn toàn).
