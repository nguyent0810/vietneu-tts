"""Regression test cho `_short_tts_render._parse_and_validate_silence_map` --
SỬA theo Codex review vòng 6 (caveat không chặn nhưng đáng sửa): CLI
`--silence-map-json` trước đây chỉ `json.loads` thẳng, không validate schema
-- key thiếu/thừa, giá trị không phải số, bool, âm, NaN/Infinity đều lọt
qua rồi mới gây lỗi khó hiểu (hoặc âm thầm sai) ở tận `gaps_to_silence()`.
Nay validate NGHIÊM ngay tại input boundary, raise `ValueError` rõ ràng.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _short_tts_render import _parse_and_validate_silence_map


def test_none_input_returns_none():
    assert _parse_and_validate_silence_map(None) is None


def test_valid_map_parses_correctly():
    result = _parse_and_validate_silence_map('{"para": 0.35, "sentence": 0.35, "minor": 0.04}')
    assert result == {"para": 0.35, "sentence": 0.35, "minor": 0.04}


def test_invalid_json_syntax_raises():
    with pytest.raises(ValueError, match="không phải JSON hợp lệ"):
        _parse_and_validate_silence_map("not json")


def test_non_object_json_raises():
    with pytest.raises(ValueError, match="phải là JSON object"):
        _parse_and_validate_silence_map("[1, 2, 3]")


def test_missing_key_raises():
    with pytest.raises(ValueError, match="ĐÚNG 3 key"):
        _parse_and_validate_silence_map('{"para": 0.35, "sentence": 0.35}')


def test_extra_key_raises():
    with pytest.raises(ValueError, match="ĐÚNG 3 key"):
        _parse_and_validate_silence_map('{"para": 0.35, "sentence": 0.35, "minor": 0.04, "extra": 1}')


def test_boolean_value_raises():
    """bool là subclass của int trong Python -- phải kiểm tra riêng, không
    được để True/False lọt qua như 1/0."""
    with pytest.raises(ValueError, match="phải là số"):
        _parse_and_validate_silence_map('{"para": true, "sentence": 0.35, "minor": 0.04}')


def test_negative_value_raises():
    with pytest.raises(ValueError, match="không được âm"):
        _parse_and_validate_silence_map('{"para": -0.1, "sentence": 0.35, "minor": 0.04}')


def test_nan_value_raises():
    with pytest.raises(ValueError, match="số hữu hạn"):
        _parse_and_validate_silence_map('{"para": NaN, "sentence": 0.35, "minor": 0.04}')


def test_infinity_value_raises():
    with pytest.raises(ValueError, match="số hữu hạn"):
        _parse_and_validate_silence_map('{"para": Infinity, "sentence": 0.35, "minor": 0.04}')


def test_string_value_raises():
    with pytest.raises(ValueError, match="phải là số"):
        _parse_and_validate_silence_map('{"para": "0.35", "sentence": 0.35, "minor": 0.04}')


def test_zero_value_is_allowed():
    """0.0 hợp lệ (không âm) -- edge case biên không bị từ chối nhầm."""
    result = _parse_and_validate_silence_map('{"para": 0.35, "sentence": 0.0, "minor": 0.04}')
    assert result["sentence"] == 0.0


def test_duplicate_key_raises():
    """SỬA theo Codex review vòng 7: json.loads mặc định ÂM THẦM giữ giá trị
    key trùng CUỐI CÙNG -- với override production tường minh, đây là lỗi
    nhập liệu cần raise, không âm thầm chọn 1 giá trị."""
    with pytest.raises(ValueError, match="trùng lặp"):
        _parse_and_validate_silence_map('{"para": 0.35, "sentence": 0.18, "sentence": 0.35, "minor": 0.04}')


def test_value_above_reasonable_upper_bound_raises():
    """SỬA theo Codex review vòng 7: giá trị hữu hạn nhưng phi thực tế (vd
    gõ nhầm ms thành s) nên bị từ chối trước khi lọt vào production."""
    with pytest.raises(ValueError, match="vượt giới hạn hợp lý"):
        _parse_and_validate_silence_map('{"para": 350, "sentence": 0.35, "minor": 0.04}')


def test_value_at_upper_bound_is_allowed():
    """5.0s đúng bằng giới hạn -- không bị từ chối nhầm (biên bao gồm)."""
    result = _parse_and_validate_silence_map('{"para": 5.0, "sentence": 0.35, "minor": 0.04}')
    assert result["para"] == 5.0
