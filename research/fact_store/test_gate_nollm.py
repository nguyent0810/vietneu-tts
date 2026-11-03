import json
from pathlib import Path
from .gate import parse_claims, gate, Unparsed
from .nollm import generate

ROOT=Path(__file__).parent

def load(topic):
    s=json.loads((ROOT/'pilot/stores_fixed'/f'{topic}.json').read_text())
    v=json.loads((ROOT/'pilot/stores_fixed'/f'{topic}.verification.json').read_text())
    return s,v

def verified(v, *ids):
    for r in v['results']:
        r['status']='unverified';r['certainty']='unknown'
    for r in v['results']:
        if r['fact_id'] in ids:r['status']='verified';r['certainty']='established'

def test_temiya_slot_is_subject_bound():
    s,v=load('tt05_temiya'); verified(v,'tt05_temiya_f01')
    out=generate(s,v)
    assert all('Sunanda' not in x['text'] for x in out['candidates'])

def test_bybit_loss_does_not_generate_compromise():
    s,v=load('ck_bybit_2025'); verified(v,'ck_bybit_2025_f06')
    out=generate(s,v)
    assert all('Bybit bị hack' not in x['text'] for x in out['candidates'])

def test_fansipan_does_not_infer_growth():
    s,v=load('vsd_fansipan'); verified(v,'vsd_fansipan_f01')
    out=generate(s,v)
    assert all('cao thêm' not in x['text'] for x in out['candidates'])

def test_tradition_template_preserves_frame():
    s,v=load('fs_short_ngay_tot_cuoi'); verified(v,'fs_short_ngay_tot_cuoi_f01')
    out=generate(s,v)
    assert out['candidates']
    from .gate import _norm
    assert all(('theo quan niem' in _norm(x['text']) or 'theo truyen thong' in _norm(x['text']) or 'trong quan niem dan gian' in _norm(x['text'])) for x in out['candidates'])

def test_unverified_is_never_promoted_and_abstains():
    s,v=load('tt05_temiya')
    for r in v['results']:r['status']='unverified';r['certainty']='unknown'
    assert not generate(s,v)['candidates']
    assert generate(s,v)['abstain']

def test_incomplete_is_review_and_deterministic():
    s,v=load('vsd_fansipan')
    for r in v['results']:r['status']='unverified';r['certainty']='unknown'
    a=gate({'title':'Fansipan cao'},s,v)
    assert a['verdict']=='REVIEW'
    assert a==gate({'title':'Fansipan cao'},s,v)

def test_modality_omission_review_when_verified():
    s,v=load('tt05_temiya'); verified(v,'tt05_temiya_f01')
    assert gate({'title':'Temiya giả tật nguyền suốt 16 năm'},s,v)['verdict']=='REVIEW'

def test_contested_title_assertion_rejected():
    s,v=load('ck_bybit_2025')
    for r in v['results']:
        if r['fact_id'] in ('ck_bybit_2025_f07','ck_bybit_2025_f08'): r['certainty']='contested'
    r=gate({'title':'Bybit mất 1,5 tỷ USD'},s,v)
    assert r['verdict']=='REJECT'
