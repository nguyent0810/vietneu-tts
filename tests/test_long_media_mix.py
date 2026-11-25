"""Ticket 151: offline selection, mocked Pexels, whole-Long rotation."""
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from unittest.mock import Mock

import pytest
import hf_batch_render as HBR
import hyperframes_bridge as HB
from library.tools.plan_enrich import enrich_long_plan, line_spans
from tools.long_media_mix import enrich_stock, query_for, prompt_query, prompt_descriptions
from tools.long_text_rotation import inventory, issues, prepare
from tools import pexels_long as PX, visual_mix as VM


@pytest.fixture(autouse=True)
def no_real_stock_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Test phải mock mạng và credential; cấm gọi API thật')
    monkeypatch.setattr(PX.stock_image, 'load_keys', forbidden)
    monkeypatch.setattr(PX.stock_image, '_get_json', forbidden)
    monkeypatch.setattr(PX.urllib.request, 'urlopen', forbidden)


def sample():
    subjects = ('dòng sông', 'ngọn núi', 'hoa sen', 'cây xanh', 'ngọn đèn', 'đồng hồ')
    return {'id': 'stock-test', 'lane': 'long', 'series': 'fs', 'style': 'laban_long',
            'script': [f'Bên cạnh {subjects[i%len(subjects)]}, cảnh vật vẫn bình dị trong ánh sáng ban mai.' for i in range(120)],
            'media': {}, 'visuals': {}, 'kinetic': True,
            'media_mix': {'max_query_repeat': 999}}  # mẫu tổng hợp chỉ 6 chủ đề: tắt trần lặp để đo tỉ lệ


def test_lane_duration_targets_editorial_and_deterministic():
    row = sample()
    row['media'] = {'1': {'kind': 'local', 'path': 'opener.mp4'}, '25': {'kind': 'local', 'path': 'manual.jpg'}}
    row['visuals'] = {'30': {'type': 'ledger', 'until': 35}}
    before = copy.deepcopy(row)
    spans = line_spans(row)[0]
    enrich_stock(row, 'fs', spans)
    assert row['media']['1'] == before['media']['1']
    assert row['media']['25'] == before['media']['25']
    assert row['visuals'] == before['visuals']
    for k, spec in row['media'].items():
        if spec.get('mix_auto'):
            assert spans[int(k)-1][0] >= 40
            assert int(k) not in range(30,36)
            assert spec['provider'] == 'pexels'
    # Repeated with exactly the same inputs, no stock network calls.
    other = copy.deepcopy(before); enrich_stock(other, 'fs', spans)
    assert other == row
    measured = VM.measure(HBR.visual_mix_scenes(row))
    assert abs(measured['stock_video_share'] - .15) <= .05
    assert abs(measured['stock_image_share'] - .15) <= .05


def test_replaces_only_character_free_ai_stills_and_tracks_savings():
    row = sample()
    row['media_mix'] = {'stock_video_share': .15, 'stock_image_share': .15}
    # 120 equal-length lines; line 1 is protected by the 40s guard.
    row['media'] = {
        '1': {'kind': 'local', 'path': 'ai_01.png'},
        '30': {'kind': 'local', 'path': 'ai_30.png'},
        '31': {'kind': 'local', 'path': 'ai_31.png'},
        '32': {'kind': 'local', 'path': 'clip_01.mp4'},
        '33': {'kind': 'local', 'path': 'ai_33.png', 'lock': True},
        '34': {'kind': 'local', 'path': 'ai_34.png', 'cuts': [{'at':'cảnh','kind':'local','path':'frame.png'}]},
    }
    descriptions = {
        'ai_01.png': 'Empty old wooden workbench beneath a warm desk lamp.',
        'ai_30.png': 'Empty old wooden workbench beneath a warm desk lamp.',
        'ai_31.png': 'Bao studies the workbench while the apprentice waits.',
        'clip_01.mp4': 'Empty old wooden workbench beneath a warm desk lamp.',
        'ai_33.png': 'Empty old wooden workbench beneath a warm desk lamp.',
        'ai_34.png': 'Bao stands at the old wooden workbench beneath a warm desk lamp.',
    }
    spans = [(i * 2.0, (i + 1) * 2.0) for i in range(120)]
    enrich_stock(row, 'fs', spans, descriptions)
    assert row['media']['30']['provider'] == 'pexels'
    assert row['media']['30']['replaced_ai'] == 'ai_30.png'
    assert row['media']['30']['query'] == 'sanitized' or 'workbench' in row['media']['30']['query']
    for key in ('1', '31', '32', '33', '34'):
        assert row['media'][key]['kind'] == 'local'
    assert row['media_mix_report']['ai_removed'] == ['ai_30.png']


def test_prompt_scene_parser_blocks_personalized_scene_and_reads_first_sentence(monkeypatch):
    monkeypatch.setattr(HB, 'sanitize_query', lambda q, channel: q)
    assert prompt_query('Close view of Bao holding a watch. Same repairer, same shop.', 'fs') is None
    assert prompt_query('Empty old wooden workbench beneath a warm desk lamp. No people.', 'fs') == 'old wooden workbench lamp'


def test_prompt_inventory_supports_plan_id_and_1977_longest_paragraph(tmp_path):
    p = tmp_path/'output/cl_staging/grokbot/fs_d25_1977/prompt.md'
    p.parent.mkdir(parents=True)
    p.write_text('## ai_08.png\n\nCâu 8\n\nEmpty old wooden workbench beneath a warm desk lamp, with no person in frame. ' + 'Detail. '*20, encoding='utf-8')
    got = prompt_descriptions({'id':'L_fs_d25_1977'}, tmp_path)
    assert 'ai_08.png' in got and 'workbench' in got['ai_08.png']


def test_mocked_ai_replacement_reaches_both_soft_targets():
    row = sample(); row['media_mix'] = {'stock_video_share': .15, 'stock_image_share': .15, 'max_query_repeat': 999}
    row['media'] = {str(i): {'kind':'local','path':f'ai_{i:02}.png'} for i in range(1,121)}
    descriptions = {f'ai_{i:02}.png':'Empty old wooden workbench beneath a warm desk lamp.' for i in range(1,121)}
    spans = [(i * 2.0, (i + 1) * 2.0) for i in range(120)]
    enrich_stock(row, 'fs', spans, descriptions)
    measured = VM.measure(HBR.visual_mix_scenes(row))
    assert abs(measured['stock_video_share'] - .15) <= .02
    assert abs(measured['stock_image_share'] - .15) <= .02
    assert len(row['media_mix_report']['ai_removed']) == sum(row['media_mix_report']['added'].values())


def test_character_and_channel_rules_and_sanitizer(monkeypatch):
    assert query_for('Ông Bảo nhìn dòng sông.', 'fs') is None
    assert query_for('Đức Phật đứng dưới ngọn núi.', 'bud') is None
    assert query_for('Người thợ sửa đồng hồ.', 'fs') is None
    assert query_for('Cảnh nhà thờ phía sau dòng sông.', 'fs') is None
    assert query_for('Bàn thờ tĩnh lặng.', 'bud').endswith('no people')
    assert query_for('Cây xanh bên gia đình.', 'bud') is None
    assert query_for('Những người đi qua khu chợ.', 'fs').startswith('vietnam asian')
    assert query_for('Đồng hồ trên bàn.', 'bud') is None
    sanitizer = Mock(return_value='sanitized')
    monkeypatch.setattr(HB, 'sanitize_query', sanitizer)
    assert query_for('Dòng sông chảy.', 'fs') == 'sanitized'
    sanitizer.assert_called_once_with('vietnam river landscape', 'FS')


def test_config_off_shortage_and_named_character(capsys):
    row = sample(); row['media_mix'] = False
    enrich_stock(row, 'fs', line_spans(row)[0]); assert not row['media']
    row['media_mix'] = {'stock_video_share': .2, 'stock_image_share': .2, 'character_names': ['Bảo']}
    row['script'] = ['Bảo nhìn dòng sông.'] * 100
    enrich_stock(row, 'fs', line_spans(row)[0]); assert not row['media']
    assert 'thiếu câu phù hợp' in capsys.readouterr().out
    row['media_mix'] = {'stock_image_share': float('nan')}
    with pytest.raises(ValueError): enrich_stock(row, 'fs', line_spans(row)[0])


@pytest.mark.parametrize('kinetic', [True,False])
@pytest.mark.parametrize('n',[4,5,6,7,12,29,120])
def test_rotation_caps_adjacency_reproducibility(kinetic,n):
    row = {'id': 'rotate', 'series':'fs','style':'laban_long','lane':'long','kinetic':kinetic,
           'script':['Đây là **KHÔNG PHẢI X · Y** trong câu.']*n}
    got = prepare(row)
    counts, sequence = inventory(got)
    assert all(a[1] != b[1] for a,b in zip(sequence,sequence[1:]))
    assert max(counts.values()) <= n*.25
    assert issues(got) == []
    assert prepare(row) == got
    assert prepare(got) == got
    assert 'text_effects' not in row


def test_word_semantics_preserve_manual_preset_and_warn(capsys):
    row = {'id':'words','lane':'long','series':'fs','script':['Một câu **BUÔNG**.']*8,
           'visuals':{str(i):{'type':'word','text':'BUÔNG'} for i in range(1,9)}}
    got = prepare(row)
    assert got['visuals'] == row['visuals']
    counts, seq = inventory(got)
    assert counts['word:dissolve'] == 2
    assert not issues(got)
    row['visuals'] = {str(i): {'type':'word','preset':'keyword_spotlight'} for i in range(1,9)}
    got = prepare(row)
    assert got['visuals'] == row['visuals']
    assert any('25%' in msg for msg in issues(got))
    HBR.visual_mix_check(got)
    assert '!! chữ lặp hiệu ứng' in capsys.readouterr().out


def test_rotation_respects_image_holds_and_visual_until():
    row = {'script':['Một câu **CHỮ**.']*8,'kinetic':True,
           'media':{'1':{'kind':'local','path':'x.jpg'}},
           'visuals':{'5':{'type':'quote','until':8}}}
    counts, sequence = inventory(row)
    assert sequence == [('5','quote:auto')]


def test_quote_variants_rotate_without_changing_editor_text():
    row={'id':'quotes','script':['Một **lời nhắc**.']*8,
         'visuals':{str(i):{'type':'quote'} for i in range(1,9)}}
    got=prepare(row)
    assert got['visuals']==row['visuals']
    assert not issues(got)
    assert all(value['effect'].startswith('quote:') for value in got['text_effects'].values())


def test_stock_resolution_mocked_and_reused_across_queries(tmp_path,monkeypatch):
    monkeypatch.setattr(PX.stock_image,'CACHE_DIR',tmp_path)
    monkeypatch.setattr(PX.stock_image,'load_keys',lambda: ('mock-key',None))
    payload={'photos':[{'id':i,'width':1920,'height':1080,'src':{'original':f'https://mock/{i}'},'url':f'https://mock/page/{i}'} for i in [1,2,3]]}
    get=Mock(return_value=payload); monkeypatch.setattr(PX.stock_image,'_get_json',get)
    def download(req,**kwargs):
        response=Mock(); response.read.return_value=req.full_url.encode()*700
        response.__enter__=Mock(return_value=response); response.__exit__=Mock(return_value=False)
        return response
    monkeypatch.setattr(PX.urllib.request,'urlopen',download)
    row={'series':'fs','media':{'1':{'kind':'image','provider':'pexels','query':'river'},
                             '50':{'kind':'image','provider':'pexels','query':'water'}}}
    got=PX.prepare(row)
    paths=[PX.frozen_asset(s) for s in got['media'].values()]
    assert len({hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}) == 2
    assert {s['stock_source']['id'] for s in got['media'].values()} == {'1','2'}
    assert all('api.pexels.com/v1/search' in call.args[0] for call in get.call_args_list)
    get.reset_mock(); assert PX.prepare(got)==got; get.assert_not_called()
    path=paths[0]; path.write_bytes(b'changed')
    with pytest.raises(ValueError,match='thay đổi'): PX.frozen_asset(got['media']['1'])


def test_video_mock_and_safety_block_cache(tmp_path,monkeypatch):
    monkeypatch.setattr(PX.stock_image,'CACHE_DIR',tmp_path)
    monkeypatch.setattr(PX.stock_image,'load_keys',lambda: ('mock-key',None))
    get=Mock(return_value={'videos':[{'id':4,'video_files':[{'width':1280,'height':720,'file_type':'video/mp4','link':'https://mock/video'}]}]})
    monkeypatch.setattr(PX.stock_image,'_get_json',get)
    monkeypatch.setattr(PX,'_slow_video',lambda data,duration: b'processed_mp4'*400)
    class Response:
        def __enter__(self): return self
        def __exit__(self,*a): pass
        def read(self): return b'fake_mp4'*1000
    monkeypatch.setattr(PX.urllib.request,'urlopen',lambda *a,**k: Response())
    path,meta=PX.fetch('video','river',set())
    assert meta['provider']=='pexels' and path.suffix=='.mp4'
    assert '/videos/search?' in get.call_args.args[0]
    safety=Mock(side_effect=RuntimeError('unsafe'))
    monkeypatch.setattr(PX.asset_safety,'assert_asset_safe_for_assembly',safety)
    with pytest.raises(RuntimeError,match='unsafe'): PX.fetch('video','river',set())


def test_chapter_key_includes_global_rotation():
    row={'script':['Một câu **CHỮ**.']*4,'style':'laban_long','text_effects':{'3':{'effect':'keycard:lens','keycard':'lens'}}}
    first=HBR.chapter_key(row,2,4,0,10,'draft')
    row['text_effects']['3']={'effect':'keycard:stamp','keycard':'stamp'}
    assert HBR.chapter_key(row,2,4,0,10,'draft') != first


def test_stock_video_slow_filter_is_mute_and_center_excerpt(monkeypatch):
    from pathlib import Path as _P
    def fake_run(args, **kw):
        _P(args[-1]).write_bytes(b'x'*5000)  # ffmpeg ghi file đích (không pipe: mp4 moov cuối file)
        return Mock(returncode=0)
    proc = Mock(side_effect=fake_run)
    monkeypatch.setattr(PX.subprocess, 'run', proc)
    assert PX._slow_video(b'input', 20) == b'x'*5000
    args = proc.call_args.args[0]
    assert args[args.index('-ss')+1] == '7.000'
    assert args[args.index('-t')+1] == '6.000'
    assert 'setpts=1.25*PTS' in args and '-an' in args
