from __future__ import annotations
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEMPLATES = json.loads((ROOT / 'templates.json').read_text(encoding='utf-8'))['mechanisms']

def _facts(doc):
    return [f for f in doc.get('fact_table', []) if f.get('certainty') == 'verified']

def _pairs(doc):
    return [(f, r) for f in _facts(doc) for r in f.get('relations', []) if len(r) >= 3]

def _get_slots(doc):
    """Expose only typed values supported by one verified relation/fact."""
    slots, provenance = {}, {}
    for fact, rel in _pairs(doc):
        subject, predicate, obj = map(str, rel[:3])
        pred = predicate.lower()
        if 'được lệnh' in pred or 'được giao' in pred:
            # The relation's subject is the recipient of an order, not necessarily its performer.
            continue
        for key, value in [('actor', subject), ('action', predicate), ('object', obj)]:
            slots.setdefault(key, value)
            provenance.setdefault(key, fact.get('fact_id'))
    # Durations are not assigned an actor without an explicit same-fact subject relation.
    for f in _facts(doc):
        stmt = str(f.get('statement', ''))
        m = re.search(r'((?:\d[\d,.]*)(?:\s*(?:năm|ngày|tháng|giờ)))', stmt, re.I)
        if m:
            # Only provide duration when a relation on this fact explicitly names its actor.
            rel = next((r for r in f.get('relations', []) if len(r) >= 3), None)
            if rel and any(w in str(rel[1]).lower() for w in ('giả', 'thử', 'giữ', 'im')):
                slots['actor'], slots['action'], slots['duration'] = str(rel[0]), str(rel[1]), m.group(1)
                for k in ('actor','action','duration'): provenance[k] = f.get('fact_id')
    return slots, provenance

def _grams(s):
    w=re.findall(r'[\wÀ-ỹ]+',s.lower()); return {tuple(w[i:i+3]) for i in range(max(0,len(w)-2))}
def _sim(a,b):
    x,y=_grams(a),_grams(b); return len(x&y)/len(x|y) if x|y else 0

def _candidate(doc, fact, title, hook, template_id, mechanism, slots, slot_prov, limit, history):
    if len(title) > limit or len(hook) > 110 or _sim(title, hook) >= .5: return None
    fid=fact.get('fact_id')
    prov={'triples': [{'subject':str(r[0]),'predicate':str(r[1]),'object':str(r[2]),'fact_id':fid}
                      for r in fact.get('relations',[]) if len(r)>=3],
          'slots':{k:{'value':v,'fact_id':slot_prov.get(k)} for k,v in slots.items()},
          'title_fact_ids':[fid], 'hook_0_3s_fact_ids':[fid], 'hook_3_10s_fact_ids':[fid],
          'title_template_id':template_id,'hook_template_id':template_id}
    return {'title':title,'hook_0_3s':hook,'hook_3_10s':fact.get('statement',''),
            'thumbnail':' '.join(title.replace(':','').replace('?','').split()[:5]),
            'template_id':template_id,'hook_template_id':template_id,'mechanism':mechanism,
            'score':round(3*int(bool(re.search(r'\d',title)))-2*history.count(template_id),4),
            'provenance':prov}

def generate_topic(doc, history=None):
    history=history or []; slots,prov=_get_slots(doc); fmt=doc.get('format','short'); limit=50 if fmt=='short' else 70
    candidates=[]
    # A relation template asserts only its own subject-predicate-object triple.
    for fact, rel in _pairs(doc):
        subj,pred,obj=map(str,rel[:3]); p=pred.lower()
        if any(x in p for x in ('được lệnh','được giao')): continue
        title=f'{subj}: {pred} {obj}'
        hook=f'{subj} {pred} {obj}.'
        c=_candidate(doc,fact,title,hook,'typed_relation','verified_relation',slots,prov,limit,history)
        if c: candidates.append(c)
    # Duration claims require an explicit relation naming the same actor on the same fact.
    for fact in _facts(doc):
        if slots.get('duration') and prov.get('duration')==fact.get('fact_id') and prov.get('actor')==fact.get('fact_id'):
            actor,action,duration=slots['actor'],slots['action'],slots['duration']
            title=f'{actor} {action} suốt {duration}'
            hook=f'{actor} {action} suốt {duration}.'
            c=_candidate(doc,fact,title,hook,'duration_actor_action','impossible_outcome',slots,prov,limit,history)
            if c: candidates.append(c)
    # Numeric comparisons are deliberately omitted until schema carries quantity, unit and subject.
    unique=[]; seen=set()
    for c in candidates:
        key=c['title']
        if key not in seen: seen.add(key); unique.append(c)
    unique.sort(key=lambda c:(-c['score'],c['template_id'],c['title']))
    selected=unique[:5]
    if selected:
        best=selected[0]
        title,thumb,h0,h3=best['title'],best['thumbnail'],best['hook_0_3s'],best['hook_3_10s']
    else:
        # No factual claim is manufactured when no typed relation can bind safely.
        title=doc.get('slug','Chủ đề'); thumb=(title+' Câu chuyện'); h0='Chưa có quan hệ đã xác minh để viết câu mở.'; h3=''
        best={'title':title,'thumbnail':thumb,'hook_0_3s':h0,'hook_3_10s':h3,'template_id':'no_safe_relation','hook_template_id':'no_safe_relation','mechanism':'none','score':0,
              'provenance':{'triples':[],'slots':{},'title_fact_ids':[],'hook_0_3s_fact_ids':[],'hook_3_10s_fact_ids':[]}}
    for c in selected: c['hook_title_jaccard_3gram']=round(_sim(c['title'],c['hook_0_3s']),4)
    return {'slug':doc.get('slug'),'channel':doc.get('channel'),'format':fmt,'title':title,'thumbnail':thumb,'hook_0_3s':h0,'hook_3_10s':h3,'chosen':best,'candidates':selected,
            'selection_rules':['verified single-relation triples only','duration requires same-fact actor and action','numeric pairs omitted without matching subject, quantity and unit schema','length over limit rejected','Jaccard 3-gram >= 0.5 excluded','specificity means presence of a digit']}

def generate_directory(directory, history=None):
    history=history if history is not None else {}; outputs=[]
    for path in sorted(Path(directory).glob('*.json')):
        doc=json.loads(path.read_text(encoding='utf-8')); channel=doc.get('channel','default'); recent=history.setdefault(channel,[])
        result=generate_topic(doc,recent); outputs.append(result); recent.append(result['chosen']['template_id'])
    return outputs
