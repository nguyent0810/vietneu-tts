"""Regression test cho `gaps_to_silence(gaps, silence_map=...)` -- P1 mở rộng
(pause-calibration study) yêu cầu độ dài silence CẤU HÌNH ĐƯỢC độc lập với
logic phân loại boundary (para/sentence/minor). Tham số `silence_map` KHÔNG
đụng vào `_classify_newline_run`/`_classify_gap` -- chỉ đổi GIÁ TRỊ ứng với
mỗi loại gap đã phân loại sẵn.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vieneu_utils.core_utils import gaps_to_silence, V3_GAP_SILENCE


def test_default_behavior_unchanged_when_silence_map_omitted():
    gaps = ["sentence", "para", "minor"]
    assert gaps_to_silence(gaps) == [
        V3_GAP_SILENCE["sentence"],
        V3_GAP_SILENCE["para"],
        V3_GAP_SILENCE["minor"],
    ]


def test_custom_sentence_silence_does_not_affect_para():
    gaps = ["sentence", "para", "sentence"]
    custom = {"para": 0.35, "sentence": 0.24, "minor": 0.04}
    assert gaps_to_silence(gaps, silence_map=custom) == [0.24, 0.35, 0.24]


def test_custom_map_covers_all_four_calibration_values():
    gaps = ["sentence"]
    for val in (0.18, 0.24, 0.28, 0.35):
        custom = {"para": 0.35, "sentence": val, "minor": 0.04}
        assert gaps_to_silence(gaps, silence_map=custom) == [val]


def test_classification_logic_itself_is_untouched_by_silence_map():
    """silence_map chỉ đổi GIÁ TRỊ, không đổi nhãn phân loại -- gaps đầu vào
    (đến từ split_text_into_chunks_with_gaps, đã patch Phase 2) không bị ảnh
    hưởng bởi việc gọi gaps_to_silence với map khác nhau."""
    from vieneu_utils.core_utils import split_text_into_chunks_with_gaps
    text = "Câu một.\nCâu hai.\n\nĐoạn mới."
    chunks, gaps = split_text_into_chunks_with_gaps(text)
    assert gaps == ["sentence", "para"]
    silence_a = gaps_to_silence(gaps, silence_map={"para": 0.35, "sentence": 0.18, "minor": 0.04})
    silence_b = gaps_to_silence(gaps, silence_map={"para": 0.35, "sentence": 0.28, "minor": 0.04})
    assert silence_a == [0.18, 0.35]
    assert silence_b == [0.28, 0.35]
    # gaps (phân loại) giữ nguyên bất kể silence_map -- không bị mutate.
    assert gaps == ["sentence", "para"]
