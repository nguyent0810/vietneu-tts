"""Template-only, verified-fact candidate generation."""
from __future__ import annotations
import json
from pathlib import Path
from . import ROOT
from .gate import gate

TEMPLATES=json.loads((ROOT/'templates_vi.json').read_text(encoding='utf8'))['templates']

def _entity(store,eid):
    e=next((e for e in store.get('entities',[]) if e['entity_id']==eid),{})
    return e.get('name',eid)

def _quantity(q):
    if not q: return None
    v=q.get('value'); unit=q.get('unit','')
    if v is None:return None
    if unit=='m' and float(v).is_integer(): n=f'{int(v):,}'.replace(',','.')+' m'
    elif unit=='m': n=f'{v:,.1f}'.replace(',','X').replace('.',',').replace('X','.')+' m'
    elif unit=='USD': n=(f'{v/1e9:g}'.replace('.',',')+' tỷ USD') if v>=1e9 else f'{v:g} USD'
    elif unit=='year': n=f'{int(v)} năm'
    elif unit=='day': n=f'{int(v)} ngày'
    elif unit in ('ETH','person','day') and float(v).is_integer(): n=f'{int(v):,}'.replace(',','.')+f' {unit}'
    else:n=f'{v:g} {unit}'
    return n

def generate(store, verification, history=None):
    history=history or []
    used={x.get('template_id') for x in history if isinstance(x,dict)}
    used_kinds={x.get('kind_sentence') for x in history if isinstance(x,dict)}
    states={r['fact_id']:r for r in verification.get('results',[])}
    candidates=[]; abstain=[]
    for f in store.get('facts',[]):
        st=states.get(f['fact_id'],{})
        if st.get('status')!='verified' or st.get('certainty') not in ('established','uncertain'):continue
        ts=[t for t in TEMPLATES if t['predicate']==f.get('predicate') and t['kind']==f.get('kind') and t['modality']==f.get('qualifiers',{}).get('modality') and t['id'] not in used]
        ts.sort(key=lambda t:(t['kind_sentence'] in used_kinds,t['id']))
        if not ts: continue
        q=_quantity(f.get('quantity')); subject=_entity(store,f['subject']); obj=_entity(store,f.get('object')) if f.get('object_is_entity') else f.get('object')
        chosen=None
        for t in ts:
            vals={'subject':subject,'object':obj or '', 'value':q or '', 'time':(f.get('time') or {}).get('start',''), 'attributed_to':_entity(store,f.get('qualifiers',{}).get('attributed_to','')) if f.get('qualifiers',{}).get('attributed_to') else '', 'condition':f.get('qualifiers',{}).get('condition',{}).get('text',''), 'outcome':f.get('qualifiers',{}).get('condition',{}).get('outcome','')}
            if all('{'+slot+'}' not in t['text'] or vals.get(slot) for slot in t['slots']):
                try: text=t['text'].format(**vals)
                except (KeyError,ValueError):continue
                chosen=(t,text);break
        if not chosen:
            abstain.append({'fact_id':f['fact_id'],'reason':'thiếu slot bắt buộc'});continue
        t,text=chosen; checked=gate({'title':text},store,verification)
        if checked['verdict']=='PASS': candidates.append({'text':text,'template_id':t['id'],'kind_sentence':t['kind_sentence'],'fact_ids':[f['fact_id']],'slots':{slot:{'value':_entity(store,f['subject']) if slot=='subject' else (obj if slot=='object' else q if slot=='value' else (f.get('time') or {}).get('start') if slot=='time' else f.get('qualifiers',{}).get('attributed_to') if slot=='attributed_to' else f.get('qualifiers',{}).get('condition')),'fact_id':f['fact_id']} for slot in t['slots']},'gate':checked})
    if not candidates:
        abstain.append({'reason':'không có fact verified phù hợp'})
    return {'candidates':candidates,'abstain':abstain}
