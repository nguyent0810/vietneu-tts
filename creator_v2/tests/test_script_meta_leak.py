import warnings

import pytest

from motion.long.script_lines import gate, parse


def chapters(*lines):
    return parse("## CH01 · Thử\n" + "\n".join(lines) + "\n## Ghi chú\nWikipedia Wikipedia plan")


@pytest.mark.parametrize("line", [
    "Plan đã cấm đưa vào lời.",
    "Không có dải lụa trên hình.",
    "Mô-típ một dòng bản kê.",
    "Cảnh ấy ta không dựng.",
    "Vòng thứ nhất đóng ở chương chín.",
    "Sợi chỉ này sẽ quay lại ở chương tám.",
    "Đưa prompt vào render.",
])
def test_production_leak_blocks(line):
    assert any(item.startswith("META_LEAK") for item in gate(chapters(line)))


@pytest.mark.parametrize("line", [
    "Trên màn hình, Vương Cương đóng một gã hề.",
    "Việt Nam những năm gần đây cách rất xa kịch bản ấy.",   # CK: kịch bản = tình huống
    "Chừng nào chưa bán, khoản lỗ vẫn chỉ là con số trên màn hình.",
    "Cô ấy nghe ra kịch bản.",
    "Bộ phim kể về một người bạn.",
    "Một hành tinh xa đang lấp lánh.",
])
def test_legitimate_narration(line):
    assert not any(item.startswith("META_LEAK") for item in gate(chapters(line)))


def test_source_density_warns_per_chapter_without_blocking():
    chs = chapters("Wikipedia kể chuyện này.", "Bài tiếng Việt và cùng trang nói thêm.")
    with pytest.warns(UserWarning, match=r"SOURCE_DENSITY \[ch01\] 3 lần"):
        assert not gate(chs)
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        gate(chapters("Wikipedia kể chuyện này."))
    assert not seen
