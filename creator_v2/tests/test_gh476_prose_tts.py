import warnings

import numpy as np
import pytest

from scripts import prose_to_script as prose, tts_sample as sample
from motion.long import craft


def test_conversion_and_preservation():
    source = ('# Đầu\n\n## CH00 · Mở\n'
              'Ông M. ở TP. Hồ Chí Minh. Có 1.800 người! “Thật sao?” '
              '[PD]Gió nổi lên… Đèn tắt.[/PD]\n\n'
              '» Lời nói thật. [TRÍCH DỊCH]\n---\n## Ghi chú\n| A | B |\n')
    result = prose.convert(source)
    assert 'Ông M. ở TP. Hồ Chí Minh.\nCó 1.800 người!\n“Thật sao?”\n' in result
    assert 'Gió nổi lên… {pd}\nĐèn tắt. {pd}' in result
    assert '» Lời nói thật. [TRÍCH DỊCH]\n' in result
    assert result.endswith('## Ghi chú\n| A | B |\n')
    original = source.split('## CH00 · Mở\n')[1].split('---')[0]
    converted = result.split('## CH00 · Mở\n')[1].split('---')[0]
    for marker in ('[PD]', '[/PD]'):
        original = original.replace(marker, '')
    assert ''.join(original.split()) == ''.join(converted.replace(' {pd}', '').split())
    assert [m['raw'] for m in prose.script_lines.parse(result)[0]['marks']] == ['pd', 'pd']


def test_sample_with_fake_engine():
    class Engine:
        def __init__(self):
            self.calls = []
        def infer(self, text, voice=None):
            self.calls.append((text, voice))
            return np.ones(3, dtype=np.float32)
    eng = Engine()
    lines = ['Một.', 'Hai?', 'Ba!', {'t': 'Bốn…', 'p': 1.0}, '“Năm?”']
    audio = sample.synthesize_chapter({'lines': lines}, eng, 'Giọng thử')
    assert eng.calls == [(x if isinstance(x, str) else x['t'], 'Giọng thử') for x in lines]
    assert [sample.pause_seconds(x) for x in lines] == pytest.approx([.55, .6, .5, 1.3, .6])
    assert len(audio) == 15 + round(3.55 * sample.speak.SAMPLE_RATE)


@pytest.mark.parametrize('n,blocked,warned', [(45, False, False), (46, False, True), (70, False, True), (71, True, False)])
def test_length_thresholds(n, blocked, warned):
    ch = [{'name': 'ch00', 'lines': [{'t': 'bạn ' * (n-1) + '?', 'p': 1.0}]}]
    with warnings.catch_warnings(record=True) as found:
        warnings.simplefilter('always')
        errors = craft.audio_problems(ch)
    assert any('vượt 70' in x for x in errors) == blocked
    assert any('vượt 45' in str(x.message) for x in found) == warned
