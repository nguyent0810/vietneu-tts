import json
import re
from pathlib import Path

import numpy as np
import pytest

import hf_batch_render as hbr
import hf_asr_check
import hf_voice
import long_script_lint as lint
from tools import prose_to_script as prose, tts_sample
from tools.long_plan_build import parse
from tools.prose_split import PDSplitter, split_sentences


@pytest.mark.parametrize('text, expected', [
    ('Có 1.800 người. Anh ở TP.HCM hôm qua.',
     ['Có 1.800 người.', 'Anh ở TP.HCM hôm qua.']),
    ('Ông M. ở TP. Hồ Chí Minh. Bác sĩ đến.',
     ['Ông M. ở TP. Hồ Chí Minh.', 'Bác sĩ đến.']),
    ('Có hoa, lá, v.v. trên bàn. Anh đi.', ['Có hoa, lá, v.v. trên bàn.', 'Anh đi.']),
    ('Có hoa, lá, v.v. Anh đi.', ['Có hoa, lá, v.v.', 'Anh đi.']),
    ('Anh ngập ngừng... rồi nói… rất khẽ. Đèn tắt… Anh đi.',
     ['Anh ngập ngừng... rồi nói… rất khẽ.', 'Đèn tắt…', 'Anh đi.']),
    ('Anh nói: “Tôi về.” “Vì sao?” Cô hỏi!',
     ['Anh nói: “Tôi về.”', '“Vì sao?”', 'Cô hỏi!']),
    ('Một vế, vế khác; rồi: vẫn vậy — chưa hết.',
     ['Một vế, vế khác; rồi: vẫn vậy — chưa hết.']),
])
def test_vietnamese_sentence_boundaries(text, expected):
    assert split_sentences(text) == expected
    assert ''.join(''.join(expected).split()) == ''.join(text.split())


def test_pd_state_across_paragraphs():
    splitter = PDSplitter()
    assert splitter.feed('Thật. [PD]Một câu. Câu khác!') == [
        ('Thật.', False), ('Một câu.', True), ('Câu khác!', True)]
    assert splitter.feed('“Hết rồi.”[/PD] Trở về.') == [('“Hết rồi.”', True), ('Trở về.', False)]
    splitter.finish()


@pytest.mark.parametrize('text', ['[/PD]', '[PD][PD]', 'Giữa [PD]câu.', '[PD]Chưa xong[/PD]', '[PD]Câu.'])
def test_bad_pd(text):
    with pytest.raises(ValueError):
        splitter = PDSplitter()
        splitter.feed(text)
        splitter.finish()


def test_adapter_preserves_tokens_and_builder_input(tmp_path, capsys):
    source = Path(__file__).parent / 'fixtures' / 'prose_two_chapters.md'
    md = source.read_text(encoding='utf-8')
    result = prose.convert(md)
    assert re.sub(r'\s+', '', result.replace('**', '')) == re.sub(r'\s+', '', md.replace('## ', ''))
    script = tmp_path / 'script.txt'
    assert prose.main([str(source), str(script)]) == 0
    output = capsys.readouterr().out
    assert 'CH00: 4 câu' in output and 'CH01: 3 câu' in output
    assert 'tiếng đọc' in output
    assert 'CẢNH BÁO' in output
    assert parse(script)[0] == result.splitlines()


def test_adapter_reports_lint_error_without_rewriting(tmp_path, capsys):
    md = tmp_path / 'prose.md'
    md.write_text('## Mở\n' + 'lời ' * 71 + '.', encoding='utf-8')
    script = tmp_path / 'out.txt'
    assert prose.main([str(md), str(script)]) == 1
    assert 'cau_dai' in capsys.readouterr().out
    assert script.read_text(encoding='utf-8') == prose.convert(md.read_text(encoding='utf-8'))


@pytest.mark.parametrize('count, level', [(35, None), (45, None), (46, lint.WARN),
                                         (70, lint.WARN), (71, lint.ERROR)])
def test_long_sentence_thresholds(count, level):
    row = {'id': 'sample', 'script': [' '.join(['lời'] * count) + '.']}
    found = [lv for lv, code, _ in lint.lint(row)['issues'] if code == 'cau_dai']
    assert found == ([] if level is None else [level])
    retention = hbr.retention_issues(row)
    assert any('> 45 tiếng' in text for text in retention) == (count > 45)
    assert not any('tách đôi' in text for text in retention)


def test_no_short_sentence_quota():
    row = {'id': 'x', 'script': ['Người kể chuyện đứng bên cánh cửa và nhìn ra sân.'] * 10}
    assert not any(code == 'it_cau_ngan' for _, code, _ in lint.lint(row)['issues'])
    assert not any('câu ngắn <= 6' in text for text in hbr.retention_issues(row))


def test_first_120s_long_sentence_gate_is_unchanged():
    row = {'id': 'sample', 'script': [' '.join(['lời'] * 40) + '.'],
           'media': {'1': {'kind': 'local', 'path': 'fixture.jpg'}}}
    segments = [{'start': 0, 'end': 13}]
    assert any('tĩnh dài 13.0s' in msg and '> 4.0s' in msg
               for msg in hbr.pace_gate_issues(row, segments))
    row['media']['1']['pan'] = {'dir': 'ltr', 'stops': [{'line': 1, 'x': 0.0}]}
    assert hbr._pan_stop_lines(row['media']) == set()
    assert any('có chuyển động dài 13.0s' in msg and '> 8.0s' in msg
               for msg in hbr.pace_gate_issues(row, segments))


def test_tts_sample_with_fake_engine(tmp_path, monkeypatch):
    calls, commands, tempos = [], [], []
    previous_asr = hf_asr_check.CACHE

    def asr(*args, **kwargs):
        assert hf_asr_check.CACHE.is_relative_to(tmp_path / 'samples')
        return {'model': 'fake', 'n_checked': 0, 'n_cached': 0, 'asr_seconds': 0,
                'audio_seconds': 0, 'xrt': 0, 'flagged': []}

    class FakeEngine:
        retries = 0

        def say(self, text, voice, style, engine, **kwargs):
            calls.append((text, voice, style, engine, kwargs))
            return np.full(12000, 0.1, dtype=np.float32), None

    def run(cmd, **kwargs):
        commands.append(cmd)
        Path(cmd[-1]).write_bytes(b'fake mp3')
        assert kwargs == {'check': True}

    monkeypatch.setattr(hf_voice, 'Voices', FakeEngine)
    monkeypatch.setattr(hf_asr_check, 'check', asr)
    monkeypatch.setattr(hf_voice, 'tempo', lambda a, sr, k: tempos.append(k) or a)
    production_cache = tmp_path / 'production-cache'
    monkeypatch.setattr(hf_voice, 'CACHE', production_cache)
    row = {'id': 'sample', 'script': ['Mở đầu.', '**Trang mới**', 'Lời tiếp.'],
           'tts': {'voice': 'Binh', 'tempo': 0.91, 'pause_ctx': True, 'pause': 0.4,
                   'seed': 42, 'text_mode': 'production', 'asr_check': True,
                   'alt': {'voice': 'Tuyen', 'lines': [3]},
                   'pauses': {'2': 1.2}, 'tempos': {'3': 0.87}}}
    original = json.dumps(row, ensure_ascii=False)
    outputs = tts_sample.sample(row, [0, 1], dest=tmp_path / 'samples', run=run)
    assert [p.name for p in outputs] == ['CH00.mp3', 'CH01.mp3']
    assert [x[:2] for x in calls] == [('Mở đầu.', 'Binh'), ('Trang mới', 'Binh'), ('Lời tiếp.', 'Tuyen')]
    assert [x[-1]['seed'] for x in calls] == [52, 62, 72]
    assert tempos == [0.91, 0.91, 0.87]
    manifest = json.loads((outputs[1].parent / '_work' / 'CH01' / 'voice.json').read_text(encoding='utf-8'))
    assert manifest['tts']['pause_ctx'] is True
    assert manifest['segments'][1]['start'] - manifest['segments'][0]['end'] == pytest.approx(1.2, abs=0.001)
    assert all('loudnorm=I=-16:TP=-1.5:LRA=11' in cmd for cmd in commands)
    assert hf_voice.CACHE == production_cache and not production_cache.exists()
    assert hf_asr_check.CACHE == previous_asr
    assert json.dumps(row, ensure_ascii=False) == original


def test_sample_cli_selects_plan_row(tmp_path, monkeypatch):
    plan = tmp_path / 'plan.json'
    rows = [{'id': 'other', 'script': ['Không chọn.']},
            {'id': 'chosen', 'script': ['Câu.'], 'tts': {'voice': 'Binh'}}]
    plan.write_text(json.dumps(rows, ensure_ascii=False), encoding='utf-8')
    calls = []
    monkeypatch.setattr(tts_sample, 'sample', lambda row, chapters: calls.append((row, chapters)))
    assert tts_sample.main([str(plan), '--only', 'chosen', '--chapters', '0', '1']) == 0
    assert calls == [(rows[1], [0, 1])]


def test_tts_rebase_roles_and_restore_cache_on_failure(tmp_path):
    tts = {'voices': ['ke', 'ke', 'ta'], 'voice': 'Binh', 'voice_ta': 'Tuyen',
           'tempo_ta': 0.88, 'pause_ctx': True}
    assert tts_sample.chapter_tts(tts, 1, 3)['voices'] == ['ke', 'ta']
    assert tts_sample.chapter_tts(tts, 1, 3)['tempo_ta'] == 0.88

    class FailedVoice:
        CACHE = tmp_path / 'production'

        def synth(self, *args):
            raise RuntimeError('engine failed')

    voice = FailedVoice()
    with pytest.raises(RuntimeError):
        tts_sample.sample({'id': 'x', 'script': ['Câu.'], 'tts': tts}, [0],
                          voice=voice, dest=tmp_path)
    assert voice.CACHE == tmp_path / 'production'
    with pytest.raises(ValueError, match='Chương không tồn tại'):
        tts_sample.sample({'id': 'x', 'script': ['Câu.'], 'tts': tts}, [1],
                          voice=voice, dest=tmp_path)
