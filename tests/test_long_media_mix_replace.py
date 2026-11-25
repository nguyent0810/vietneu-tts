"""151b: offline replacement, unique savings, and protected editorial media."""
import copy
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
import hf_batch_render as HBR
import hyperframes_bridge as HB
from tools.long_media_mix import enrich_stock, prompt_query, prompt_descriptions, flow_first_frames
from tools import pexels_long as PX, visual_mix as VM
from tools import long_media_mix as MIX


@pytest.fixture(autouse=True)
def no_real_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Cấm mạng/credential trong test 151b')
    monkeypatch.setattr(PX.stock_image, 'load_keys', forbidden)
    monkeypatch.setattr(PX.stock_image, '_get_json', forbidden)
    monkeypatch.setattr(PX.urllib.request, 'urlopen', forbidden)


def sample():
    return {'id': 'stock-replace', 'lane': 'long', 'series': 'fs', 'style': 'laban_long',
            'script': ['Một nhận xét tham khảo theo truyền thống và điều kiện thực tế.'] * 120,
            'media': {}, 'visuals': {}, 'media_mix': {'max_query_repeat': 999}}


@pytest.mark.parametrize('scene', [
    'Blank paper on the desk. Bao waits in the background.',
    'Blank paper on the desk. A woman is visible at the doorway.',
    'Close view of hands beside the notebook.',
    'Empty desk in a room with a family behind it.',
    'Close view of the notebook. One child stands behind it.',
    'A crowded market with workers.',
    'A blank reference paper beside Bảo.',
])
def test_entire_unique_scene_blocks_background_people_and_names(scene):
    assert prompt_query(scene, 'fs', ['Bao']) is None


def test_scene_query_channel_sanitizer(monkeypatch):
    sanitizer = Mock(side_effect=lambda q, channel: q)
    monkeypatch.setattr(HB, 'sanitize_query', sanitizer)
    assert 'vietnam' in prompt_query('Empty house with a warm lamp.', 'fs')
    assert 'vietnam' in prompt_query('Quiet street market after Tet.', 'fs')
    assert prompt_query('Blank paper beside a pen.', 'bud') is None
    assert prompt_query('A Hindu altar with incense.', 'bud') is None
    assert prompt_query('Empty incense altar.', 'bud').endswith('no people')
    assert all(c.args[1] in {'FS', 'BUD'} for c in sanitizer.call_args_list)


def test_prompt_formats_job_resolution_and_map_fallback(tmp_path):
    job = tmp_path / 'output/cl_staging/grokbot/fs_d25_1977'
    job.mkdir(parents=True)
    job.joinpath('prompt.md').write_text('''## ai_01.png — câu 1

- Prompt (EN): Empty wooden workbench. The same Vietnamese watch repairer Bao, approximately 63 years old. Natural hands.
- Khung: 16:9

## ai_02.png

Câu 2

The same Vietnamese woman Huong, approximately 50 years old. Use the identical faces. Natural hands. Lower fifth quiet for subtitles. Overhead still life of blank paper beside an open folder. No people. Photorealistic restrained cinema.

## ai_03.png

The same Vietnamese woman Huong, approximately 50 years old. Lower fifth quiet for subtitles. Blank paper on the table. Huong hand is visible. Photorealistic restrained cinema.
''')
    research = tmp_path / 'output/cl_staging/long/research/d25/1977'
    research.mkdir(parents=True)
    research.joinpath('150_media_map.json').write_text(json.dumps({'mapped_media': [
        {'path': 'ai_04.png', 'description': 'Empty steel desk in daylight.'},
        {'path': 'ai_05.png'},
    ]}))
    descriptions = prompt_descriptions({'id': 'L_fs_d25_1977'}, tmp_path)
    assert set(descriptions) == {'ai_01.png', 'ai_02.png', 'ai_03.png', 'ai_04.png'}
    assert '- Khung' not in descriptions['ai_01.png']
    assert prompt_query(descriptions['ai_01.png'], 'fs')
    assert prompt_query(descriptions['ai_02.png'], 'fs')
    assert prompt_query(descriptions['ai_03.png'], 'fs') is None
    assert prompt_query('The same Vietnamese woman Huong. Unknown template with a desk.', 'fs') is None


def test_ai_only_sample_hits_targets_rollback_and_unique_savings():
    row = sample()
    row['media'] = {str(i): {'kind': 'local', 'path': f'ai_{i:03d}.png'} for i in range(1, 121)}
    descriptions = {s['path']: 'Blank paper sheets on a wooden table.' for s in row['media'].values()}
    original = copy.deepcopy(row['media'])
    spans = [(i * 5., (i + 1) * 5.) for i in range(120)]
    enrich_stock(row, 'fs', spans, descriptions)
    report = row['media_mix_report']
    assert report['estimated_shares'] == pytest.approx({'video': .15, 'image': .15})
    assert report['ai_images_saved'] == 36
    assert len(report['ai_removed']) == len(set(report['ai_removed'])) == 36
    assert all(row['media'][str(i)] == original[str(i)] for i in range(1, 9))
    for key, spec in row['media'].items():
        if spec.get('replaced_ai'):
            assert 'paper' in spec['query']  # narration contains no literal subject
            assert spec['replaced_media'] == original[key]
    enriched_media = copy.deepcopy(row['media'])
    enrich_stock(row, 'fs', spans, descriptions)
    assert row['media'] == enriched_media
    assert row['media_mix_report']['ai_images_saved'] == 36


def test_protects_flow_sources_locks_all_clips_and_missing_descriptions(tmp_path):
    job = tmp_path / 'output/cl_staging/grokbot/fs_d25_1965'
    job.mkdir(parents=True)
    job.joinpath('clips.md').write_text('- Khung đầu: `ai_31.png` trong thư mục ảnh.')
    research = tmp_path / 'output/cl_staging/long/research/d25/1965'
    research.mkdir(parents=True)
    research.joinpath('110_clips_manifest.json').write_text('[{"first_frame":"ai_30.png"}]')
    row = sample()
    row['id'] = 'L_fs_d25_1965'
    row['media'] = {
        '1': {'kind': 'local', 'path': 'ai_01.png'},
        **{str(i): {'kind': 'local', 'path': f'ai_{i}.png'} for i in range(30, 39)},
        '40': {'kind': 'local', 'path': 'clip_40.mp4'},
        '41': {'kind': 'local', 'path': 'clip_41.MOV'},
        '42': {'kind': 'local', 'path': 'manual.png'},
    }
    row['media']['32']['lock'] = True
    row['media']['33']['flow_first_frame'] = True
    row['media']['34']['first_frame'] = True
    row['media_locks'] = {'35': True}
    original = copy.deepcopy(row['media'])
    descriptions = {Path(s['path']).name: 'Empty wooden workbench.' for s in row['media'].values()}
    descriptions['ai_36.png'] = 'Empty wooden workbench. A man is visible behind it.'
    descriptions.pop('ai_37.png')
    spans = [(i * 2., (i + 1) * 2.) for i in range(120)]
    assert flow_first_frames(row, tmp_path) == {'ai_30.png', 'ai_31.png', 'ai_33.png', 'ai_34.png'}
    enrich_stock(row, 'fs', spans, descriptions, project_root=tmp_path)
    for key in original.keys() - {'38'}:
        assert row['media'][key] == original[key]
    assert row['media']['38']['replaced_ai'] == 'ai_38.png'
    assert row['media_mix_report']['ai_removed'] == ['ai_38.png']


def test_cuts_preserved_and_remaining_uses_excluded_from_savings():
    row = sample()
    row['media'] = {
        '1': {'kind': 'local', 'path': 'ai_30.png'},
        '30': {'kind': 'local', 'path': 'ai_30.png', 'cuts': [
            {'at': 'theo truyền thống', 'kind': 'local', 'path': 'ai_31.png', 'lock': True}]},
        '31': {'kind': 'local', 'path': 'ai_31.png'},
        '32': {'kind': 'local', 'path': 'ai_32.png', 'cuts': [
            {'at': 'theo truyền thống', 'kind': 'local', 'path': 'ai_33.png'}]},
        '40': {'kind': 'local', 'path': 'ai_34.png', 'lock': True},
        '45': {'kind': 'local', 'path': 'ai_34.png'},
    }
    descriptions = {f'ai_{i}.png': 'Blank reference paper beside an open folder.' for i in range(30, 35)}
    original = copy.deepcopy(row['media'])
    spans = [(i * 2., (i + 1) * 2.) for i in range(120)]
    enrich_stock(row, 'fs', spans, descriptions)
    assert row['media']['1'] == original['1']
    assert row['media']['30']['cuts'] == original['30']['cuts']
    assert row['media']['30']['replaced_ai'] == 'ai_30.png'
    assert row['media']['31']['replaced_ai'] == 'ai_31.png'
    assert row['media']['32']['cuts'][0]['at'] == 'theo truyền thống'
    assert row['media']['32']['cuts'][0]['replaced_ai'] == 'ai_33.png'
    assert set(row['media_mix_report']['ai_removed']) == {'ai_32.png', 'ai_33.png'}
    actual = VM.measure(HBR.visual_mix_scenes(row, [{'start': a, 'end': b} for a, b in spans]))
    assert row['media_mix_report']['estimated_shares']['video'] == actual['stock_video_share']
    assert row['media_mix_report']['estimated_shares']['image'] == actual['stock_image_share']


@pytest.mark.parametrize('as_list', [True, False])
def test_cli_only_writes_sibling_trial_and_prints_unique_savings(tmp_path, monkeypatch, capsys, as_list):
    row = sample()
    row['id'] = 'L_fs_d25_1977'
    row['media'] = {str(i): {'kind': 'local', 'path': f'ai_{i:03d}.png'} for i in range(1, 121)}
    folder = tmp_path / 'output/cl_staging/long'
    folder.mkdir(parents=True)
    plan = folder / 'plan_L_fs_d25_1977.json'
    data = [row] if as_list else row
    original = json.dumps(data).encode()
    plan.write_bytes(original)
    descriptions = {s['path']: 'Blank paper on a wooden desk.' for s in row['media'].values()}
    monkeypatch.setattr(MIX, 'prompt_descriptions', lambda *a, **k: descriptions)
    monkeypatch.setattr('sys.argv', ['long_media_mix', '--data-root', str(tmp_path), '--years', '1977'])
    assert MIX.main() == 0
    assert plan.read_bytes() == original
    trial = json.loads(plan.with_suffix('.mix.json').read_text())
    assert isinstance(trial, list) == as_list
    changed = trial[0] if as_list else trial
    assert changed['media_mix_report']['ai_images_saved'] > 0
    assert '1977 AI không còn dùng:' in capsys.readouterr().out


def test_character_scene_kept_for_conceptual_narration_when_concept_broll_off():
    row = sample()
    row['media_mix'] = {'concept_broll': False}
    row['script'] = ['Theo truyền thống, nạp âm và sao hạn có ý nghĩa để tham khảo.'] * 120
    row['media'] = {str(i): {'kind': 'local', 'path': f'ai_{i:03d}.png'} for i in range(1, 121)}
    descriptions = {s['path']: 'A Vietnamese man sitting at the desk with his family.' for s in row['media'].values()}
    before = copy.deepcopy(row['media'])
    spans = [(i * 5., (i + 1) * 5.) for i in range(120)]
    enrich_stock(row, 'fs', spans, descriptions)
    assert row['media'] == before
    assert row['media_mix_report']['ai_images_saved'] == 0


def test_concept_broll_replaces_filler_character_shots_on_concept_lines():
    # PO 25/11: ~15% + 15% Pexels; câu giải thích khái niệm không nhắc nhân vật -> B-roll hợp nghĩa.
    row = sample()
    row['script'] = ['Theo truyền thống, nạp âm và sao hạn có ý nghĩa để tham khảo.'] * 120
    row['media'] = {str(i): {'kind': 'local', 'path': f'ai_{i:03d}.png'} for i in range(1, 121)}
    descriptions = {s['path']: 'A Vietnamese man sitting at the desk with his family.' for s in row['media'].values()}
    spans = [(i * 5., (i + 1) * 5.) for i in range(120)]
    enrich_stock(row, 'fs', spans, descriptions)
    assert row['media_mix_report']['ai_images_saved'] > 0
    assert all(spec['kind'] == 'local' for k, spec in row['media'].items() if spans[int(k) - 1][0] < 40)


def test_concept_broll_query_is_opt_in_and_maps_concepts():
    from tools import long_media_mix as M
    assert M.DEFAULTS["concept_broll"] is True
    assert M.concept_query("Năm 2027 thuộc nạp âm Thiên Hà Thủy", "fs")
    assert M.concept_query("Sao La Hầu chiếu năm nay", "fs")
    assert M.concept_query("Một câu không có khái niệm nào", "fs") is None


def test_diversify_queries_caps_repeats_and_rotates_alternates():
    from tools.long_media_mix import diversify_queries
    cands = [(i, None, "blank paper sheets desk", None) for i in range(10)]
    out = diversify_queries(cands, cap=3)
    from collections import Counter
    c = Counter(q for _, _, q, _ in out)
    assert max(c.values()) <= 3 and len(c) >= 3


def test_review537_stock_spec_does_not_hold_and_people_lines_kept():
    from tools.long_media_mix import _stock_spec, OPENING_GUARD_S
    assert _stock_spec({'kind': 'local', 'path': 'ai_001.png'}, 'image', 'q')['hold'] is False
    assert OPENING_GUARD_S > 40
    row = sample()
    row['script'] = ['Gia đình nào cũng xem nạp âm và sao hạn theo truyền thống.'] * 120
    row['media'] = {str(i): {'kind': 'local', 'path': f'ai_{i:03d}.png'} for i in range(1, 121)}
    descriptions = {s['path']: 'A Vietnamese man at the desk.' for s in row['media'].values()}
    enrich_stock(row, 'fs', [(i * 5., (i + 1) * 5.) for i in range(120)], descriptions)
    assert row['media_mix_report']['ai_images_saved'] == 0
