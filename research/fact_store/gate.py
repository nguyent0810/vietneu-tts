"""Conservative deterministic Fact Gate for the research store."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import json, re, unicodedata
from pathlib import Path
from . import ROOT

@dataclass
class ParsedClaim:
    subject: str | None
    predicate: str | None
    object: str | None = None
    quantity: dict | None = None
    time: str | None = None
    polarity: bool = False
    modality: str | None = None
    attributed_to: str | None = None
    condition: str | None = None
    span: str = ""

@dataclass
class Unparsed:
    span: str
    reason: str

class ClaimParser:
    def parse(self, text: str, store: dict) -> list[ParsedClaim | Unparsed]:
        return parse_claims(text, store)

def _norm(s):
    s=unicodedata.normalize('NFD',s.casefold())
    return ''.join(c for c in s if unicodedata.category(c)!='Mn')

def _predicates(): return json.loads((ROOT/'predicates.json').read_text(encoding='utf8'))['predicates']

def parse_claims(text, store):
    """Split on sentence boundaries and conjunctions; ambiguous/incomplete -> Unparsed."""
    chunks=[x.strip(' \t,;:') for x in re.split(r'(?<=[.!?])\s+|\s+(?:và|nhưng|rồi)\s+',text.strip()) if x.strip(' \t,;:')]
    entities=[]
    for e in store.get('entities',[]):
        for a in [e.get('name',''),*e.get('aliases',[])]:
            if a: entities.append((_norm(a),e['entity_id']))
    entities.sort(key=lambda x:len(x[0]),reverse=True)
    preds=[]
    for p,d in _predicates().items():
        for v in d.get('gate_verbs',[]):
            if v: preds.append((_norm(v),p))
    preds.sort(key=lambda x:len(x[0]),reverse=True)
    out=[]
    for chunk in chunks:
        n=_norm(chunk)
        p_matches=[(m.start(),p,v) for v,p in preds if v!='theo truyen thong' and v!='theo quan niem' and (m:=re.search(r'(?<![\w])'+re.escape(v)+r'(?![\w])',n))]
        first_pred=min((x[0] for x in p_matches),default=len(n))
        ss={eid for a,eid in entities if (m:=re.search(r'(?<![\w])'+re.escape(a)+r'(?![\w])',n)) and m.start()<first_pred}
        ps={p for _,p,_ in p_matches}
        # A conventional modality frame is not itself the asserted relationship.
        if not ps and ('theo quan niem' in n or 'theo truyen thong' in n): ps={'rule_traditional'}
        if len(ss)!=1 or len(ps)!=1:
            out.append(Unparsed(chunk,'thiếu hoặc đa nghĩa subject/predicate')); continue
        subj=next(iter(ss)); pred=next(iter(ps))
        quantity=None
        m=re.search(r'([\d.,]+|mot|hai|ba|bon|nam|sau|bay|tam|chin|muoi|muoi sau|muoi lam|muoi bon|muoi ba|muoi hai|muoi mot)\s*(met|m|km|cm|nam|ngay|ty\s*usd|trieu\s*usd|usd|eth)',n)
        if m:
            words={'mot':1,'hai':2,'ba':3,'bon':4,'nam':5,'sau':6,'bay':7,'tam':8,'chin':9,'muoi':10,'muoi mot':11,'muoi hai':12,'muoi ba':13,'muoi bon':14,'muoi lam':15,'muoi sau':16}
            raw=m.group(1); val=words.get(raw)
            if val is None:
                raw=raw.replace('.','').replace(',','.');
                try: val=float(raw)
                except ValueError: val=None
            u=m.group(2); unit='m' if u in ('m','met') else 'year' if u=='nam' else 'day' if u=='ngay' else 'km' if u=='km' else 'cm' if u=='cm' else 'USD' if 'usd' in u else 'ETH'
            if val is not None: quantity={'value':val,'unit':unit}
            if quantity and 'ty' in u: quantity['value']*=1_000_000_000
            elif quantity and 'trieu' in u: quantity['value']*=1_000_000
        tm=re.search(r'\b(\d{4})(?:-(\d{2})-(\d{2}))?\b',n)
        mod=('legendary' if any(x in n for x in ('tuong truyen','trong truyen','theo kinh')) else 'traditional' if 'theo quan niem' in n or 'theo truyen thong' in n else 'reported' if any(x in n for x in ('duoc cho la','theo ')) else None)
        attribution=None
        if 'theo ' in n:
            for a,eid in entities:
                if re.search(r'theo\s+'+re.escape(a),n): attribution=eid
        neg=bool(re.search(r'\b(khong|chua|chang)\b',n))
        out.append(ParsedClaim(subj,pred,quantity=quantity,time=tm.group(0) if tm else None,polarity=neg,modality=mod,attributed_to=attribution,condition=None,span=chunk))
    return out

def _entity_name(store,eid):
    e=next((x for x in store.get('entities',[]) if x['entity_id']==eid),None)
    return (e or {}).get('name',eid)

def gate(text_fields, store, verification):
    if isinstance(text_fields,str): text_fields={'text':text_fields}
    states={x['fact_id']:x for x in verification.get('results',[])}
    allclaims=[]
    for field,text in text_fields.items():
        if not isinstance(text,str) or not text.strip(): continue
        for parsed in parse_claims(text,store):
            span=parsed.span if isinstance(parsed,ParsedClaim) else parsed.span
            row={'span':span,'field':field,'parsed':asdict(parsed) if isinstance(parsed,ParsedClaim) else None,'fact_id':None,'verdict':'REVIEW','reason':parsed.reason if isinstance(parsed,Unparsed) else 'chưa có fact khớp đầy đủ'}
            if isinstance(parsed,ParsedClaim):
                hits=[]
                for f in store.get('facts',[]):
                    if f.get('subject')==parsed.subject and f.get('predicate')==parsed.predicate:
                        hits.append(f)
                matched=[]
                for f in hits:
                    if not parsed.quantity and (f.get('quantity') or {}).get('value') is not None: continue
                    if parsed.quantity:
                        q=f.get('quantity') or {}
                        if q.get('unit')!=parsed.quantity['unit'] or q.get('value') is None or abs(q['value']-parsed.quantity['value'])>max(.05,abs(q['value'])*.001): continue
                    if parsed.time and (f.get('time') or {}).get('start','')[:4]!=parsed.time[:4]: continue
                    if f.get('qualifiers',{}).get('negated',False)!=parsed.polarity: continue
                    matched.append(f)
                verified=[f for f in matched if states.get(f['fact_id'],{}).get('status')=='verified' and states.get(f['fact_id'],{}).get('certainty') in ('established','uncertain')]
                if verified:
                    f=verified[0]; q=f.get('qualifiers',{}); modality=q.get('modality')
                    needs={'legendary':('legendary','traditional'),'traditional':('traditional',),'reported':('reported',),'estimated':('estimated','reported'),'hypothesized':('hypothesized','reported')}
                    if modality in needs and parsed.modality not in needs[modality]: row['reason']='claim bỏ/giảm khung modality'; row['verdict']='REVIEW'
                    elif q.get('attributed_to') and parsed.attributed_to!=q['attributed_to']: row['reason']='thiếu/sai attribution'; row['verdict']='REVIEW'
                    elif q.get('condition') and parsed.predicate=='rule_traditional' and _norm(q['condition'].get('text','')) not in _norm(parsed.span): row['reason']='bỏ/đổi điều kiện'; row['verdict']='REVIEW'
                    else: row.update(fact_id=f['fact_id'],verdict='PASS',reason='khớp fact verified')
                elif hits and (matched or (parsed.quantity is not None and field in ('title','thumbnail_text') and any(states.get(f['fact_id'],{}).get('certainty')=='contested' for f in hits))):
                    row['verdict']='REJECT'; row['reason']='trái fact hoặc chọn một phương án contested'
                elif hits: row['reason']='fact khớp chưa verified'
            allclaims.append(row)
    verdict=max((x['verdict'] for x in allclaims),key=lambda v:{'PASS':0,'REVIEW':1,'REJECT':2}[v],default='REVIEW')
    return {'verdict':verdict,'claims':allclaims}
