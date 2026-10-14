"""Mốc từ bám âm thanh thật (hf_align) cho video dài."""
import numpy as np

import hf_align as a


def test_so_doc_thanh_am_tiet():
    # một nghìn chín trăm bảy mươi chín / hai nghìn không trăm lẻ sáu / một trăm lẻ năm
    assert a.vi_number_syllables(1979) == 7
    assert a.vi_number_syllables(2027) == 7
    assert a.vi_number_syllables(2006) == 6
    assert a.vi_number_syllables(105) == 4
    assert a.vi_number_syllables(21) == 3 and a.vi_number_syllables(10) == 1


def test_trong_so_tu_theo_am_tiet_va_ngat():
    assert a.token_weight("Phật") == 1.0
    assert a.token_weight("1979") == 7.0
    assert a.token_weight("sau,") > a.token_weight("sau")


def test_ranh_gioi_roi_vao_khe_giua_am_tiet():
    # 4 âm tiết = 4 cụm năng lượng, khe lặng ở giữa; im lặng 0.3s ở đầu câu.
    hop = a.HOP_S
    env = np.zeros(int(2.5 / hop))
    bursts = [(0.30, 0.62), (0.70, 1.20), (1.28, 1.50), (1.58, 2.20)]  # âm tiết dài ngắn khác nhau
    for s, e in bursts:
        env[int(s / hop):int(e / hop)] = 1.0
    times = a.word_times(env, hop, 0.0, 2.5, [1, 1, 1, 1])
    starts = [t for t, _ in times]
    assert abs(starts[0] - 0.30) < 0.03, "phải bỏ khoảng lặng đầu câu"
    for (t, _), (s, _) in zip(times[1:], bursts[1:]):
        gap_lo = [b for b in bursts if b[0] == s][0][0] - 0.08
        assert gap_lo - 0.02 <= t <= s + 0.02, f"ranh giới {t} phải nằm trong khe trước {s}"
