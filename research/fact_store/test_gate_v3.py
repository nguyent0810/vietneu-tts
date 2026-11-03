import json
from pathlib import Path
from .gate import gate_claims

ROOT=Path(__file__).parent
STORE=json.loads((ROOT/'pilot/stores_fixed/ck_bybit_2025.json').read_text())
VER=json.loads((ROOT/'pilot/stores_fixed/ck_bybit_2025.verification.json').read_text())

def claim(subject='Bybit', predicate='lost_asset', value=1500000000, marker='khoảng', attribution='FBI', **kw):
    return {'claim_id':'c1','field':'title','span':'claim replay','type':'explicit','subject_text':subject,'subject_entity_id':'bybit','predicate':predicate,'object_text':'tài sản ảo','quantity':{'value':value,'unit':'USD','measure':'amount_lost','approx_marker':marker},'time':None,'polarity':True,'modality_marker':'none','attributed_to_text':attribution,'attributed_to_entity_id':'fbi' if attribution=='FBI' else None,'condition_text':None,'scope_text':None,**kw}

def run(c,complete=True,context=None):
    return gate_claims({'package_id':'test','complete':complete,'uncovered_spans':[],'claims':[c] if c else []},STORE,VER,context)

def test_bybit_claim_cases():
    assert run(claim())['verdict']=='PASS'
    assert run(claim(attribution=None))['verdict']=='REVIEW'
    wrong=run(claim(value=2000000000,marker='gần'))
    assert wrong['verdict']=='REJECT'
    assert wrong['claims'][0]['reason_code']=='value_contradiction'
    hack=claim(predicate='compromised',value=None,attribution=None,quantity=None,object_text=None)
    assert run(hack)['verdict']=='REJECT'

def test_incomplete_and_empty_are_review():
    assert run(claim(),complete=False)['verdict']=='REVIEW'
    assert gate_claims({'complete':True,'claims':[]},STORE,VER)['verdict']=='REVIEW'

def test_unknown_is_review():
    s=json.loads((ROOT/'pilot/stores_fixed/tt05_temiya.json').read_text())
    v=json.loads((ROOT/'pilot/stores_fixed/tt05_temiya.verification.json').read_text())
    c=claim(subject='Temiya',predicate='performed',value=None,quantity=None,object_text='giả câm',attribution=None)
    c['quantity']={'value':16,'unit':'year','measure':'duration','approx_marker':'none'}
    assert gate_claims({'complete':True,'claims':[c]},s,v)['verdict']=='REVIEW'

def test_time_and_value_contradiction_and_entity_id():
    c=claim(time='21/02/2025',subject_entity_id='bybit',object_entity_id='virtual_assets')
    assert run(c)['verdict']=='PASS'
    c['quantity']['value']=1400000000
    # Attribution identifies a different verified variant, so this is attribution, not value.
    assert run(c)['verdict']=='REJECT'

def test_scope_mismatch_is_review_and_polarity_normalized():
    c=claim(scope_text='global')
    c['polarity']=False
    assert run(c)['verdict']=='REVIEW'

def test_series_context_string_frame():
    s=json.loads((ROOT/'pilot/stores_fixed/tt05_temiya.json').read_text())
    v=json.loads((ROOT/'pilot/stores_fixed/tt05_temiya.verification.json').read_text())
    fact=next(f for f in s['facts'] if f.get('qualifiers',{}).get('modality')=='legendary')
    c={'claim_id':'m','field':'title','span':'x','type':'explicit','subject_text':next(e['name'] for e in s['entities'] if e['entity_id']==fact['subject']),'subject_entity_id':fact['subject'],'predicate':fact['predicate'],'object_text':None,'object_entity_id':None,'quantity':None,'time':None,'polarity':True,'modality_marker':'none','attributed_to_text':None,'attributed_to_entity_id':None,'condition_text':None,'scope_text':None}
    assert gate_claims({'complete':True,'claims':[c]},s,v,'truyền thuyết')['verdict'] in ('PASS','REVIEW')
