"""Phase D: tiếng động bám mốc cảnh (hf_sfx) -- cùng luật tính giờ với longform.js."""
import hf_sfx


def _lines():
    return [
        {"sentence_id": 1, "start": 0.0, "end": 3.0, "words": [{"w": "Một", "t": .1}], "visual": {"type": "word"}},
        {"sentence_id": 2, "start": 3.2, "end": 7.0, "words": [{"w": "năm", "t": 3.4}, {"w": "**hai**", "t": 4.0}],
         "visual": {"type": "list", "items": [{"at": 2, "word": "hai"}]}},
        {"sentence_id": 3, "start": 7.2, "end": 9.0, "words": [{"w": "gì?", "t": 8.5}], "visual": {"type": "ask"}},
    ]


def test_when_bam_chu_duoc_doc_nhu_longform():
    L = _lines()
    assert hf_sfx.when(L, {"at": 2, "word": "hai"}, 0) == 4.0          # bỏ ** khi so chữ
    assert hf_sfx.when(L, {"at": 2}, 0) == 3.2 + 0.3                    # không có word -> đầu câu + 0.3


def test_cau_hoi_lang_khong_co_tieng_nao():
    ev = hf_sfx.events(_lines(), "bud", silence={3})
    assert not [e for e in ev if 7.0 <= e[0] <= 9.0]
    assert any(name == "woodblock" and abs(t - 4.0) < 1e-6 for t, name, _ in ev)  # mục danh sách = mõ


def test_bang_am_theo_kenh():
    bud = {n for _, n, _ in hf_sfx.events(_lines(), "bud", set())}
    fs = {n for _, n, _ in hf_sfx.events(_lines(), "fs", set())}
    assert "bell" in bud and "gong" not in bud                           # Phật giáo: chuông
    assert "gong" in fs                                                  # Phong Thuỷ: cồng
