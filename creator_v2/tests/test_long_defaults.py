import copy
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from motion.long import build_long as b


@pytest.fixture(autouse=True)
def _new_topic(monkeypatch):
    """'gh274-new-test' giả làm Long mới (không có thư mục thật); mọi topic khác là cũ."""
    monkeypatch.setattr(b, "is_legacy_topic", lambda topic: topic != "gh274-new-test")


def test_is_legacy_topic_needs_list_and_real_spec(tmp_path, monkeypatch):

    monkeypatch.undo()
    monkeypatch.setattr(b, "ROOT", tmp_path)
    assert b.is_legacy_topic("moi") is True                       # chưa có danh sách -> cũ
    (tmp_path / "data" / "long").mkdir(parents=True)
    (tmp_path / "data" / "long" / "_legacy_topics.json").write_text('["cu"]', encoding="utf-8")
    assert b.is_legacy_topic("moi") is True                       # chưa có spec thật -> cũ
    for t in ("cu", "moi"):
        (tmp_path / "data" / "long" / t).mkdir()
        (tmp_path / "data" / "long" / t / "spec.json").write_text("{}", encoding="utf-8")
    assert b.is_legacy_topic("cu") is True
    assert b.is_legacy_topic("moi") is False


def test_long_defaults_new_and_legacy():
    legacy = {'channel': 'CL'}
    assert b.apply_long_defaults('mata-hari', copy.deepcopy(legacy)) == legacy
    new = b.apply_long_defaults('gh274-new-test', {'channel': 'CL'}, [('ch01', {'lines': ['Trời mưa.']})])
    assert all(new[k] for k in ('opening_gate', 'cine_auto', 'idcards', 'voice2', 'ambience'))
    assert new['ambience'][0]['kind'] == 'rain'
    for channel in ('CK', 'MIM'):
        spec = b.apply_long_defaults('gh274-new-test', {'channel': channel})
        assert spec['ambience'] == [] and spec['voice2']['voice']


def test_long_defaults_explicit_and_opening_gate():
    spec = b.apply_long_defaults('gh274-new-test', {'channel': 'CL', 'opening_gate': False, 'cine_auto': False, 'voice2': None, 'ambience': []})
    assert spec['opening_gate'] is False and spec['cine_auto'] is False and spec['voice2'] is None
    with pytest.raises(SystemExit, match='allow-opening'):
        b._refuse_opening('gh274-new-test', spec, False)
    b._refuse_opening('gh274-new-test', spec, True)
    b._refuse_opening('mata-hari', {'opening_gate': False}, False)


def test_mix_levels_channels_legacy_and_custom():
    for channel in ('CL', 'MIM', 'CK'):
        assert b.mix_levels('gh274-new-test', channel) == {'gain': .17, 'threshold': .05, 'ratio': 4., 'ambience_db': 15.}
        assert b.mix_levels('mata-hari', channel)['threshold'] == .03
    assert b.mix_levels('gh274-new-test', 'CL', {'mix_levels': {'CL': {'gain': .2}}})['gain'] == .2


def test_mix_level_gate():
    assert b.check_mix_level({'music_minus_voice_db': -18, 'blocks': 3}) is None
    assert b.check_mix_level({'music_minus_voice_db': -18.01, 'blocks': 3})
    assert b.check_mix_level({'music_minus_voice_db': float('nan'), 'blocks': 3})
    assert b.check_mix_level({})


def test_legacy_html_does_not_add_cine_fields():
    scene = {'type': 'photo', 'img': 'a', 't0': 0.0, 't1': 5.0}
    chapter = {'scenes': [copy.deepcopy(scene)], 'lines': []}
    spec = {'title': 'test', 'channel': 'CL', 'chapters': ['ch01'], 'imgs': {'a': 'source'}}
    writes = {}

    def record(path, text, **kwargs):
        writes[str(path)] = text
        return len(text)

    with patch.object(b, 'load', return_value=(spec, [('ch01', chapter)], Path('tmp_dry/legacy_case'))), \
         patch.object(b, '_refuse_html_lint'), patch.object(b, '_refuse_craft'), patch.object(b, '_refuse_opening'), \
         patch.object(b.variety, 'resolve_bgm'), patch.object(b.variety, 'look', return_value={}), \
         patch.object(b.variety, 'fonts_url', return_value=''), patch.object(b, 'fetch_img', return_value={'w': 1920, 'h': 1080}), \
         patch.object(b, 'word_lines', return_value=[]), patch.object(b, 'plan', side_effect=lambda *args: [copy.deepcopy(scene)]), \
         patch.object(b.sfx_long, 'build'), patch.object(b, 'mix_chapter'), patch.object(b, 'late_first', return_value=[]), \
         patch.object(Path, 'read_text', return_value='{"duration": 5}'), patch.object(Path, 'write_text', record), \
         patch.object(Path, 'mkdir'), patch.object(Path, 'exists', return_value=False):
        b.do_html('mata-hari')
    data = next(value for path, value in writes.items() if path.endswith('data.js'))
    case = json.loads(data.split('=', 1)[1].strip().rstrip(';'))
    assert case['scenes'] == [scene]
    assert chapter['scenes'] == [scene]
