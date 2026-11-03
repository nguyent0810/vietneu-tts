import json
from pathlib import Path
from .generator import generate_topic, generate_directory, _get_slots

ROOT=Path(__file__).resolve().parents[1]

def load(slug): return json.loads((ROOT/'bench114'/f'{slug}.json').read_text(encoding='utf-8'))

def test_slots_are_filled():
    d=load('vsd_fansipan'); o=generate_topic(d)
    assert '{' not in o['title'] and '{' not in o['hook_0_3s']

def test_contested_not_used_in_title():
    d=load('f18_ta_ao'); o=generate_topic(d)
    contested=[f for f in d['fact_table'] if f.get('certainty')!='verified']
    assert not any(f.get('value') and f['value'] in o['title'] for f in contested)
    assert all(s['fact_id'] not in {f['fact_id'] for f in contested} for s in o['chosen']['provenance']['slots'].values() if s.get('fact_id'))

def test_bybit_roles_are_correct():
    d=load('ck_bybit_2025'); o=generate_topic(d)
    assert all(c['provenance']['triples'] for c in o['candidates'])
    assert all(c['provenance']['title_fact_ids']==c['provenance']['hook_0_3s_fact_ids'] for c in o['candidates'])

def test_history_penalizes_recent_template():
    d=load('tt05_temiya'); a=generate_topic(d)
    if not a['candidates']:
        return
    b=generate_topic(d,[a['chosen']['template_id']])
    assert b['chosen']['score'] <= a['chosen']['score']

def test_deterministic():
    d=load('ck_bybit_2025')
    assert generate_topic(d)==generate_topic(d)

def test_directory_history_sequential_and_bounded_options():
    data=generate_directory(ROOT/'bench114',{})
    assert len(data)==18
    assert all(len(x['candidates'])<=5 for x in data)


def test_packaging_length_limits():
    for item in generate_directory(ROOT/'bench114',{}):
        limit=50 if item['format']=='short' else 70
        assert len(item['title']) <= limit
        assert 2 <= len(item['thumbnail'].split()) <= 5

def test_temiya_duration_never_binds_sunanda():
    d=load('tt05_temiya'); o=generate_topic(d)
    assert all('Sunanda' not in c['title'] or '16 năm' not in c['title'] for c in o['candidates'])
    assert not any(c['template_id']=='duration_actor_action' for c in o['candidates'])

def test_piprahwa_does_not_pair_unlike_numbers():
    d=load('b19_xa_loi'); o=generate_topic(d)
    assert all('hay' not in c['title'] and 'hay' not in c['hook_0_3s'] for c in o['candidates'])

def test_length_and_similarity_are_exclusions():
    for item in generate_directory(ROOT/'bench114',{}):
        for c in item['candidates']:
            assert len(c['title']) <= (50 if item['format']=='short' else 70)
            assert c['hook_title_jaccard_3gram'] < .5
