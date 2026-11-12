"""Câu không có **cụm** thì key_parts không 'hot' -> ảnh tràn khung không bật thẻ cụt (Lead 12/11)."""
import hyperframes_bridge as HB


def test_marked_phrase_is_hot():
    assert HB._key_parts("Chị sinh năm **Quý Hợi**.") == [{"t": "QUÝ HỢI", "hot": True}]


def test_unmarked_line_falls_back_but_not_hot():
    parts = HB._key_parts("Hai chữ Tý và Ngọ, mực son đỏ.")
    assert parts == [{"t": "HAI CHỮ TÝ VÀ", "hot": False}]


def test_avoid_still_picks_other_mark():
    parts = HB._key_parts("**Tý** và **Ngọ đối đầu**", avoid="NGỌ ĐỐI ĐẦU")
    assert parts == [{"t": "TÝ", "hot": True}]
