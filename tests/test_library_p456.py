import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

cards = module('library_cards_p456', ROOT / 'library/tools/cards.py')
lib = module('library_lib_p456', ROOT / 'library/tools/lib.py')

def test_render_prefix_rules_are_explicit_and_channel_specific():
    assert cards.render_channel('_r_tn2_hop.html') == 'fs'
    assert cards.render_channel('_r_r27_hop2004.html') == 'fs'
    assert cards.render_channel('_r_fs_yd_02.html') == 'fs'
    assert cards.render_channel('_r_tn3_tam.html') == 'bud'
    assert cards.render_channel('_r_tn4_p5.html') == 'bud'
    assert cards.render_channel('_r_r27_ngu.html') == 'bud'
    assert cards.render_channel('_r_bud_a2_01.html') == 'bud'
    assert cards.render_channel('_r_unknown.html') is None

def test_plan_usage_counts_articles_by_series_and_engine(tmp_path, monkeypatch):
    inv = tmp_path / 'inventory'; inv.mkdir()
    monkeypatch.setattr(cards, 'INV', inv)
    monkeypatch.setattr(cards, 'CARDS', tmp_path / 'cards')
    (inv / 'engine_map.json').write_text(json.dumps({'bridge_style:casemap': ['map_animated']}))
    (tmp_path / 'fs').mkdir(); (tmp_path / 'bud').mkdir()
    (tmp_path / 'fs/plan_fs.json').write_text(json.dumps([
        {'id': 'a1', 'series': 'fs', 'style': 'casemap'},
        {'id': 'a2', 'series': 'fs', 'style': 'casemap'}]))
    (tmp_path / 'bud/plan_bud.json').write_text(json.dumps(
        {'id': 'b1', 'series': 'bud', 'style': 'casemap'}))
    usage = cards._usage_evidence(tmp_path)
    assert usage['map_animated']['fs']['so_bai'] == 2
    assert usage['map_animated']['bud']['so_bai'] == 1

def _card(path, d):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('---\n' + json.dumps(d, ensure_ascii=False) + '\n---\n\n<!-- Codex/Lead soạn ở P2 -->\n')

def test_rank_formula_filters_zero_fit_and_channel_bans(tmp_path, monkeypatch):
    monkeypatch.setattr(lib, 'CARDS', tmp_path / 'cards')
    base = {'loai':'canh','da_dung':'chua_co','so_nguon':4,'do_hop':{'fs':3},'cong':'cao','cam_ngach':[]}
    _card(tmp_path/'cards/canh/a.md', dict(base, id='a', ten='A'))
    _card(tmp_path/'cards/canh/b.md', dict(base, id='b', ten='B', cong='thap', so_nguon=2))
    _card(tmp_path/'cards/canh/zero.md', dict(base, id='zero', ten='Zero', do_hop={'fs':0}))
    _card(tmp_path/'cards/canh/banned.md', dict(base, id='banned', ten='Banned', cam_ngach=['fs']))
    got = lib.ranked('fs', 10)
    assert [x['id'] for x in got] == ['b', 'a']
    assert got[0]['diem'] == 6

def test_pick_excludes_winning_templates_and_includes_experiments(tmp_path, monkeypatch):
    monkeypatch.setattr(lib, 'CARDS', tmp_path/'cards')
    monkeypatch.setattr(lib, 'CHANNELS', tmp_path/'channels')
    briefdir=tmp_path/'output/cl_staging/briefs'; briefdir.mkdir(parents=True)
    rules=tmp_path/'output/cl_staging/grok'; rules.mkdir(parents=True)
    (rules/'rules.md').write_text('1. chung\n5. FS: luật thử nghiệm; BUD: đối chiếu nguồn.\n')
    for ch, conclusion in [('fs','giữ'),('bud','DỪNG')]:
        (briefdir/f'{ch}.md').write_text('## Short — luật dừng khuôn\nSàn, cửa sổ và điều kiện mẫu.\n| khuôn | n | trung vị | cao nhất | kết luận |\n|---|---|---|---|---|\n| `win` | 8 | 9 | 10 | giữ |\n| `test` | 2 | 3 | 4 | chưa đủ bài |\n| `stop` | 7 | 2 | 4 | DỪNG (đổi khuôn, giữ chủ đề) |\n')
    exp=tmp_path/'output/cl_staging/experiments'; exp.mkdir(parents=True)
    (exp/'trial.json').write_text(json.dumps({'id':'trial-x','channel':'fs','format':'short'}))
    result=lib.picks('fs',tmp_path)
    names=[x['ten'] for x in result['noi_duoc_ap']]
    states={x['ten']:x['trang_thai'] for x in lib.sync_channels(tmp_path)['fs']['khuon']}
    assert states == {'win':'thang','test':'ngang','stop':'thua'}
    assert 'win' not in names
    assert 'test' in names and 'stop' in names and 'trial-x' in names
    assert all(len(x['goi_y']) <= 3 for x in result['noi_duoc_ap'])
