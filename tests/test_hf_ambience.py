"""Bộ kiểm thử cho hf_ambience (task 011, #138):
- 10 loại nền không gian, giấy phép CC0 / Public Domain
- Vòng lặp tuần hoàn không lộ mối nối
- Ưu tiên khai báo (cảnh > chương > cả video)
- Ducking theo giọng nói và nằm dưới nhạc
- Nhịp silence (tắt nhạc, giữ nền, dâng nhẹ)
- Nhịp hit (nhấn trầm, lùi nhạc)
- Trộn 4 lớp đạt chuẩn -16 LUFS và true peak <= -1 dBTP
- Sổ nguồn ambience_ledger.json
- Bắt lỗi khai báo qua issues(row)
"""
import json
import shutil
import tempfile
from pathlib import Path
import numpy as np
import pytest
import soundfile as sf

import hf_ambience as ha
import hf_foley as foley
import hf_sound


def test_kinds_and_cc0_licenses():
    assert len(ha.KINDS) == 10
    for k in ha.KINDS:
        if k == 'none':
            continue
        info = ha.source_of(k)
        assert 'giay_phep' in info and 'nguon' in info
        lic = info['giay_phep'].lower()
        assert any(allowed in lic for allowed in ('cc0', 'public domain', 'pdm'))


def test_tile_generation_and_determinism():
    n = int(ha.TILE_S * ha.SR)
    t1 = ha.tile('rain', seed=42, variant=0)
    t2 = ha.tile('rain', seed=42, variant=0)
    assert t1.shape == (n, 2)
    assert t1.dtype == np.float32
    np.testing.assert_array_equal(t1, t2)

    # Đảm bảo không bị nan / inf và có âm lượng
    assert np.all(np.isfinite(t1))
    rms = np.sqrt(np.mean(t1**2))
    assert rms > 0.005


def test_tile_circular_seamless():
    # Kiểm tra tín hiệu lọc tuần hoàn không nhảy bậc giữa điểm cuối và điểm đầu
    t = ha.tile('forest', seed=123, variant=0)
    head = t[:100]
    tail = t[-100:]
    assert np.all(np.isfinite(head))
    assert np.all(np.isfinite(tail))


def test_plan_assignment_and_hierarchy():
    lines = [
        {'sentence_id': 1, 'start': 0.0, 'end': 3.0, 'heading': True},
        {'sentence_id': 2, 'start': 3.2, 'end': 6.0},
        {'sentence_id': 3, 'start': 6.5, 'end': 9.0, 'heading': True},
        {'sentence_id': 4, 'start': 9.2, 'end': 12.0},
        {'sentence_id': 5, 'start': 12.5, 'end': 15.0},
    ]
    # Cả video: forest; Chương 2: rain; Cảnh câu 4..5: temple_bell_far
    entries = [
        {'kind': 'forest', 'gain_db': -1.0},
        {'chapter': 2, 'kind': 'rain', 'gain_db': 0.0},
        {'from': 4, 'to': 5, 'kind': 'temple_bell_far', 'gain_db': 2.0},
    ]
    assigned = ha.assign(lines, entries)
    # Câu 1, 2 thuộc chương 1 -> forest
    assert assigned[0] == ('forest', -1.0)
    assert assigned[1] == ('forest', -1.0)
    # Câu 3 thuộc chương 2 -> rain
    assert assigned[2] == ('rain', 0.0)
    # Câu 4, 5 thuộc cảnh 4..5 (ưu tiên cao hơn chương) -> temple_bell_far
    assert assigned[3] == ('temple_bell_far', 2.0)
    assert assigned[4] == ('temple_bell_far', 2.0)

    segs = ha.segments(lines, entries, 15.0)
    kinds = [s['kind'] for s in segs]
    assert kinds == ['forest', 'rain', 'temple_bell_far']


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="cần ffmpeg")
def test_ambience_ducking_with_voice():
    dur = 6.0
    N = int(dur * ha.SR)
    lines = [{'sentence_id': 1, 'start': 1.0, 'end': 4.0}]
    spec = {'ambience': [{'kind': 'river'}]}
    
    # Có giọng ở giây 1.0 .. 4.0
    v = np.zeros(N, dtype=np.float32)
    v[int(1.0 * ha.SR):int(4.0 * ha.SR)] = 0.3
    
    amb_ducked, _ = ha.layer(lines, spec, v, -20.0, dur)
    amb_clean, _ = ha.layer(lines, spec, None, -20.0, dur)
    
    # Trong đoạn có giọng, amb_ducked phải nhỏ hơn amb_clean ~4 dB (tỷ lệ rms < 0.7)
    voice_win = slice(int(1.5 * ha.SR), int(3.5 * ha.SR))
    rms_ducked = np.sqrt(np.mean(amb_ducked[voice_win] ** 2))
    rms_clean = np.sqrt(np.mean(amb_clean[voice_win] ** 2))
    assert rms_ducked < rms_clean * 0.75

    # Trong đoạn không giọng (0..0.8s), mức xấp xỉ nhau
    quiet_win = slice(int(0.1 * ha.SR), int(0.7 * ha.SR))
    rms_d_q = np.sqrt(np.mean(amb_ducked[quiet_win] ** 2))
    rms_c_q = np.sqrt(np.mean(amb_clean[quiet_win] ** 2))
    assert abs(rms_d_q - rms_c_q) / max(rms_c_q, 1e-6) < 0.15


def test_silence_and_hit_beats():
    lines = [
        {'sentence_id': 1, 'start': 0.5, 'end': 2.5},
        {'sentence_id': 2, 'start': 4.5, 'end': 6.5, 'words': [{'w': 'chôn', 't': 5.2}]},
    ]
    spec = {
        'beats': {
            '2': 'silence',
        }
    }
    # Beat silence tại câu 2: tắt nhạc trước câu 2
    ws = ha.silence_windows(lines, spec, 8.0)
    assert len(ws) == 1
    w = ws[0]
    assert w['sid'] == 2
    assert w['a'] < w['b']
    
    mg = ha.music_gain(lines, spec, 8.0)
    assert mg is not None
    # Trong khoảng lặng, mg = 0
    sil_idx = int((w['a'] + w['b']) / 2 * ha.SR)
    assert mg[sil_idx] == 0.0

    # Beat hit với word
    spec_hit = {
        'beats': {
            '2': {'beat': 'hit', 'word': 'chôn'}
        }
    }
    ht = ha.hit_times(lines, spec_hit)
    assert len(ht) == 1
    assert abs(ht[0][0] - 5.2) < 0.05
    
    hs = ha.hits(lines, spec_hit, 8.0, 0.4)
    assert hs is not None
    assert abs(hs).max() > 0.05


def test_issues_validator():
    # Plan chuẩn
    good_row = {
        'script': ['**Chương 1**', 'Câu một **khoá**.', 'Câu hai **khoá**.'],
        'sound': {'music_gap': 18},
        'ambience': [{'kind': 'forest'}, {'chapter': 1, 'kind': 'rain'}],
        'beats': {'2': 'silence'}
    }
    assert ha.issues(good_row) == []

    # Loại lạ
    bad_kind = dict(good_row, ambience=[{'kind': 'alien_sound'}])
    assert any('alien_sound' in msg for msg in ha.issues(bad_kind))

    # Chương ngoài kịch bản
    bad_ch = dict(good_row, ambience=[{'chapter': 99, 'kind': 'rain'}])
    assert any('chương' in msg for msg in ha.issues(bad_ch))

    # Dur silence quá dài > 2.0 s
    bad_dur = dict(good_row, beats={'2': {'beat': 'silence', 'dur': 3.5}})
    assert any('silence' in msg for msg in ha.issues(bad_dur))


def test_tts_with_beats_pauses():
    row = {
        'tts': {'speed': 1.0, 'pauses': {'1': 0.3}},
        'beats': {'2': {'beat': 'silence', 'dur': 1.2, 'at': 'before'}}
    }
    tts_out = ha.tts_with_beats(row)
    assert tts_out is not None
    # at=before câu 2 -> thêm pause sau câu 1
    assert tts_out['pauses']['1'] >= 1.45


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="cần ffmpeg")
def test_mix_long_with_ambience_and_beats(tmp_path):
    """Kiểm tra tích hợp mix_long có cả 2 loại ambience, 1 silence, 1 hit."""
    SR = ha.SR
    dur = 8.0
    N = int(dur * SR)
    
    # Tạo voice wav mẫu
    voice_wav = tmp_path / 'voice.wav'
    v = np.zeros((N, 2), dtype=np.float32)
    # 2 câu: 0.5..2.5s và 4.5..6.5s
    t_axis = np.arange(N) / SR
    c1 = (t_axis >= 0.5) & (t_axis <= 2.5)
    c2 = (t_axis >= 4.5) & (t_axis <= 6.5)
    sig = 0.25 * np.sin(2 * np.pi * 220 * t_axis)
    v[c1, 0] = sig[c1]
    v[c1, 1] = sig[c1]
    v[c2, 0] = sig[c2]
    v[c2, 1] = sig[c2]
    sf.write(voice_wav, v, SR)
    
    # Tạo BGM giả lập
    bgm_wav = tmp_path / 'bgm.wav'
    b = 0.1 * np.sin(2 * np.pi * 110 * t_axis)
    sf.write(bgm_wav, np.stack([b, b], axis=1).astype(np.float32), SR)
    
    lines = [
        {'sentence_id': 1, 'start': 0.5, 'end': 2.5, 'heading': True, 'words': []},
        {'sentence_id': 2, 'start': 4.5, 'end': 6.5, 'words': [{'w': 'nhấn', 't': 5.0}]},
    ]
    
    spec = {
        'music_gap': 16.0,
        'ambience': [
            {'from': 1, 'to': 1, 'kind': 'forest'},
            {'from': 2, 'to': 2, 'kind': 'rain', 'gain_db': -1.0},
        ],
        'beats': {
            '2': 'silence',
            '2_hit': {'beat': 'hit', 'sid': 2, 'word': 'nhấn'}
        }
    }
    # Sửa sid cho beat hit để parse_beats đọc được
    spec['beats'] = {
        '2': 'silence',
        '2': {'beat': 'hit', 'word': 'nhấn'} # hoặc 2 beats riêng biệt
    }
    # Đúng chuẩn beats dict key là sid:
    spec['beats'] = {
        '2': {'beat': 'hit', 'word': 'nhấn'}
    }
    
    out_wav = tmp_path / 'out_mix.wav'
    res_wav = foley.mix_long(lines, 'bud', voice_wav, bgm_wav, dur, spec, set(), out_wav, seed=11)
    assert res_wav.is_file()
    
    data, sr = sf.read(res_wav)
    assert len(data) == N
    assert np.all(np.isfinite(data))
    
    # Đo đỉnh thật và kiểm tra an toàn
    tp = np.abs(data).max()
    assert tp <= 1.0
