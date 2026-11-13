from collections import Counter
from pathlib import Path
import warnings

from motion.long import script_lines as sl
from motion.long import build_long as build


ROOT = Path(__file__).resolve().parents[1]


def chapters(topic):
    return sl.parse((ROOT / 'data' / 'long' / topic / 'script.md').read_text(encoding='utf-8'))


def test_mata_hari_real_chapter():
    findings = [w for w in sl.flow_warnings(chapters('mata-hari')) if w[1] == 'ch03']
    assert ('RAO_NGUON', 'ch03', 9, 'câu 9–15') in findings
    assert ('NHIP_DEU', 'ch03', 3, 'câu 3–7') in findings
    assert any(w[0] == 'NHAY_MOC' and w[2] == 32 and '1919' in w[3] for w in findings)
    assert {w[2] for w in findings if w[0] == 'META_NGUOI_KE'} == {10, 14, 24}


def test_negative_varied_story_and_year_boundaries():
    chs = [
        {'name': 'ch00', 'title': 'Mở', 'lines': ['Năm 1900, câu chuyện mở ra ở một nơi xa.', 'Năm 2020.', 'Ba.', 'Bốn.', 'Năm.']},
        {'name': 'ch01', 'title': 'Hành trình 1900', 'lines': [
            'Anh ta giữ một con đường quan trọng trong vùng đất ấy.',
            'Bà đi tiếp.', 'Đến năm 1910, người đi đường quay trở lại ngôi làng nhỏ.',
            'Mười năm sau.', 'Một cánh cửa mở ra giữa đêm mùa đông dài.',
            'Năm 1911.', 'Hai.', 'Ba.']},
        {'name': 'ch02', 'title': 'Kết', 'lines': ['Năm 1900, câu chuyện mở ra ở một nơi xa.', 'Năm 2020.', 'Ba.', 'Bốn.', 'Năm.']},
    ]
    assert sl.flow_warnings(chs) == []


def test_golden_warning_rate():
    chs = chapters('golden')
    counts = Counter(w[0] for w in sl.flow_warnings(chs))
    assert sum(counts.values()) <= len(chs)


def test_gate_emits_only_warnings():
    chs = [{'name': 'ch00', 'title': 'Mở', 'lines': [
        'Một câu ngắn.', 'Hai câu ngắn.', 'Ba câu ngắn.', 'Bốn câu ngắn.', 'Năm câu ngắn.']}]
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter('always')
        result = sl.gate(chs)
    assert result == []
    assert any('NHIP_DEU' in str(item.message) for item in seen)


def test_tts_warns_for_all_missing_chapters_without_blocking(tmp_path, monkeypatch):
    chs = [('ch01', {'lines': ['một câu']}), ('ch02', {'lines': ['hai câu']})]
    monkeypatch.setattr(build, 'ROOT', tmp_path)
    monkeypatch.setattr(build, 'load', lambda topic: ({}, chs, tmp_path))
    monkeypatch.setattr(build, 'is_legacy_topic', lambda topic: False)
    monkeypatch.setattr(build, 'speak', lambda *args: {'duration': 60})
    (tmp_path / 'ch01').mkdir()
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter('always')
        build.do_tts('new', only=['ch01'])
    assert 'ch01, ch02' in str(seen[0].message)
    assert (tmp_path / 'ch01' / 'timing.json').exists()
    monkeypatch.setattr(build, 'is_legacy_topic', lambda topic: True)
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter('always')
        build.do_tts('old', only=['ch01'])
    assert not seen



def test_beat_windows_cross_chapters():
    chs = [dict(name='ch00', lines=['lời ' * 252], marks=[]),
           dict(name='ch01', lines=['tiếp ' * 126, 'mới ' * 126], marks=[{'i': 0, 'raw': 'beat: hệ quả'}])]
    notes = sl.beat_warnings(chs)
    assert not any('60–90' in n for n in notes)
    assert any('90–' in n for n in notes)
    assert sl.beat_warnings([dict(name='ch00', lines=['ngắn'])]) == []


def test_beat_mark_is_not_spoken():
    chs = sl.parse('## CH00 · Mở\nMột câu. {beat: diễn biến}\n')
    assert chs[0]['lines'] == ['Một câu.']
    assert chs[0]['marks'][0]['raw'] == 'beat: diễn biến'
