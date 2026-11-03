"""Conservative deterministic Fact Gate for the research store."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import json, re, unicodedata
from pathlib import Path
from . import ROOT

REVIEW_CODES = {'unverified_fact','no_fact','entity_ambiguous','extractor_incomplete','missing_modality','unattributed_variant','promise_unsupported','other','dropped_condition','scope_mismatch'}

def _time_parts(value):
    """Return (ISO start, granularity) for supported Vietnamese/ISO date forms."""
    if not value: return None
    s=str(value).strip().casefold()
    m=re.search(r'(?:năm\s*)?(\d{4})',s)
    if not m: return None
    y=int(m.group(1)); month=None; day=None
    md=re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})',s)
    if md: day,month,y=map(int,md.groups())
    else:
        mm=re.search(r'tháng\s*(\d{1,2})\s*/\s*(\d{4})',s)
        iso=re.search(r'\d{4}-(\d{2})(?:-(\d{2}))?',s)
        if mm: month,y=map(int,mm.groups())
        elif iso: month=int(iso.group(1)); day=int(iso.group(2)) if iso.group(2) else None
    if day: return (f'{y:04d}-{month:02d}-{day:02d}','day')
    if month: return (f'{y:04d}-{month:02d}','month')
    return (f'{y:04d}','year')

def _same_time(claim, fact):
    ct=_time_parts(claim); ft=_time_parts((fact.get('time') or {}).get('start'))
    if ct and ft:
        gran={'year':1,'month':2,'day':3}[min((ct[1],ft[1]),key=lambda x:{'year':1,'month':2,'day':3}[x])]
        return ct[0][:4] == ft[0][:4] and (gran<2 or ct[0][:7]==ft[0][:7]) and (gran<3 or ct[0][:10]==ft[0][:10])
    return True

def _frame(series_context):
    if isinstance(series_context,dict):
        if series_context.get('frame'): return str(series_context['frame']).casefold()
        raw=' '.join(str(v) for v in series_context.values())
    else: raw=str(series_context or '')
    cfg=ROOT/'series_frames.json'
    try: rules=json.loads(cfg.read_text(encoding='utf8')).get('rules',[])
    except (OSError,ValueError): rules=[]
    n=_norm(raw)
    for rule in rules:
        if any(_norm(k) in n for k in rule.get('keywords',[])): return rule.get('frame')
        if rule.get('regex') and re.search(rule['regex'],n): return rule.get('frame')
    return ''

def _resolve_entity(text, store):
    if not text: return None, False
    n = _norm(text)
    found=set()
    for e in store.get('entities',[]):
        for name in [e.get('name',''), *e.get('aliases',[])]:
            if name and _norm(name) in n: found.add(e['entity_id'])
    return (next(iter(found)),False) if len(found)==1 else (None,len(found)>1)

def _norm(s):
    s=unicodedata.normalize('NFC',str(s)).casefold()
    s=unicodedata.normalize('NFD',s)
    return ''.join(c for c in s if unicodedata.category(c)!='Mn')

def gate_claims(extraction, store, verification, series_context=None, rounding=None):
    """Deterministic fact matching over LLM-extracted claims. Never infers claims from prose."""
    frame=_frame(series_context)
    results={r['fact_id']:r for r in verification.get('results',[])}
    facts=store.get('facts',[]); entities={e['entity_id']:e for e in store.get('entities',[])}
    verified=lambda f: results.get(f.get('fact_id'),{}).get('status') in ('verified','disputed')
    allowed_certainty=('established','uncertain','contested')
    rows=[]
    for c in extraction.get('claims',[]):
        row={'claim_id':c.get('claim_id'),'span':c.get('span',''),'field':c.get('field'),'fact_id':None,'verdict':'REVIEW','reason_code':'no_fact'}
        def resolve(role, textkey):
            eid=c.get(role+'_entity_id')
            if eid is not None: return (eid,False) if eid in entities else (None,True)
            return _resolve_entity(c.get(textkey),store)
        s,sa=resolve('subject','subject_text')
        # Chỉ tra thực thể ở đối tượng khi quan hệ yêu cầu đối tượng là thực thể (không tra trong literal/quantity).
        obj_types=str((_predicates().get(c.get('predicate')) or {}).get('object','literal'))
        o,oa=resolve('object','object_text') if obj_types not in ('literal','') and not c.get('quantity') else (None,False)
        if sa or oa or not s:
            row['reason_code']='entity_ambiguous'; rows.append(row); continue
        subject_predicate_facts=[f for f in facts if f.get('subject')==s and f.get('predicate')==c.get('predicate')]
        candidates=subject_predicate_facts
        if c.get('predicate')=='compromised' and not candidates:
            # Organization-as-victim is contradicted only by a verified negative compromised fact on its part_of system.
            systems={f.get('subject') for f in facts if f.get('predicate')=='part_of' and f.get('object')==s}
            negatives=[f for f in facts if f.get('subject') in systems and f.get('predicate')=='compromised' and f.get('qualifiers',{}).get('negated') and verified(f)]
            if negatives: row.update(verdict='REJECT',reason_code='negated_system',fact_id=negatives[0]['fact_id'])
            else: row['reason_code']='no_fact'
            rows.append(row); continue
        if o:
            candidates=[f for f in candidates if f.get('object')==o]
        q=c.get('quantity') or {}; marker=q.get('approx_marker','none')
        def qtymatch(f):
            fq=f.get('quantity') or {}
            if not q.get('value'): return not fq.get('value')
            if fq.get('unit')!=q.get('unit') or fq.get('value') is None:return False
            x=float(fq['value']); y=float(q['value']); tol=(rounding or {}).get('default',0.005)
            if marker=='khoảng': return abs(x-y)<=abs(x)*.05
            if marker=='hơn': return x>y and x-y<=abs(x)*.10
            if marker=='gần': return y>=x and y-x<=abs(x)*.05
            return abs(x-y)<=max(abs(x)*tol,10**(-max(0,len(str(y).split('.')[-1])))/2)
        claim_negated=(c.get('polarity') is False) or bool(re.search(r'\b(không|chưa|chẳng|not|never)\b',_norm(c.get('span',''))))
        candidates=[f for f in candidates if (not o or f.get('object')==o)]
        modality_markers=_norm(c.get('modality_marker','none'))
        verified_candidates=[f for f in candidates if verified(f) and results.get(f.get('fact_id'),{}).get('certainty') in allowed_certainty]
        matched=[f for f in candidates if qtymatch(f) and (f.get('qualifiers',{}).get('negated',False)==claim_negated) and _same_time(c.get('time'),f)]
        verified_matches=[f for f in matched if verified(f) and results.get(f['fact_id'],{}).get('certainty') in allowed_certainty]
        if c.get('type')=='promise' and not verified_matches:
            row['reason_code']='promise_unsupported'
        elif verified_matches:
            f=verified_matches[0]; qf=f.get('qualifiers',{}); mod=qf.get('modality')
            need={'legendary':('tương truyền','legend'),'traditional':('theo quan niệm','tradition'),'hypothesized':('giả thuyết',)}
            context_ok=(mod=='legendary' and frame in ('legend','story')) or (mod=='traditional' and frame=='tradition')
            marker_text=modality_markers
            required=need.get(mod,())
            if c.get('scope_text') and _norm(c['scope_text'])!=_norm(str(qf.get('scope',''))): row['reason_code']='scope_mismatch'
            elif required and not context_ok and not any(_norm(x) in marker_text for x in required): row['reason_code']='missing_modality'
            elif qf.get('condition') and not c.get('condition_text'): row['reason_code']='dropped_condition'
            elif qf.get('attributed_to'):
                aid=c.get('attributed_to_entity_id')
                if aid is not None and aid not in entities:
                    row['reason_code']='entity_ambiguous'; rows.append(row); continue
                if aid is None: aid=_resolve_entity(c.get('attributed_to_text'),store)[0]
                if aid!=qf['attributed_to']:
                    row.update(verdict='REJECT' if c.get('attributed_to_text') or aid else 'REVIEW',reason_code='attribution_contradiction' if c.get('attributed_to_text') or aid else 'unattributed_variant',fact_id=f['fact_id'])
                else: row.update(verdict='PASS',reason_code=None,fact_id=f['fact_id'])
            elif qf.get('scope') is not None and c.get('scope_text') and _norm(str(qf['scope']))!=_norm(str(c['scope_text'])):
                row['reason_code']='scope_mismatch'
            elif f.get('variant_group') and not c.get('attributed_to_text'): row['reason_code']='unattributed_variant'
            else: row.update(verdict='PASS',reason_code=None,fact_id=f['fact_id'])
        elif verified_candidates:
            # Contradiction is proven only after all dimensions except value or role/attribution match.
            structural=[]
            for f in verified_candidates:
                fq=f.get('quantity') or {}; cq=q or {}
                if fq.get('measure')!=cq.get('measure') or fq.get('unit')!=cq.get('unit'): continue
                if f.get('qualifiers',{}).get('negated',False)!=claim_negated: continue
                if not _same_time(c.get('time'),f): continue
                if c.get('scope_text') and _norm(c['scope_text'])!=_norm(str(f.get('qualifiers',{}).get('scope',''))): continue
                fqf=f.get('qualifiers',{})
                if fqf.get('attributed_to'):
                    aid=c.get('attributed_to_entity_id')
                    if aid is None: aid=_resolve_entity(c.get('attributed_to_text'),store)[0]
                    if aid!=fqf['attributed_to']: continue
                if fqf.get('condition') and (not c.get('condition_text') or _norm(c['condition_text'])!=_norm(str(fqf['condition']))): continue
                modality=fqf.get('modality')
                frame_ok=(modality=='legendary' and frame in ('legend','story')) or (modality=='traditional' and frame=='tradition')
                markers=_norm(c.get('modality_marker','none'))
                marker_ok=(modality in ('legendary','traditional') and frame_ok) or any(x in markers for x in ('truyen thuyet','tuong truyen','theo quan niem','theo truyen thong','gia thuyet'))
                if modality in ('legendary','traditional','hypothesized') and not marker_ok: continue
                structural.append(f)
            if structural and q.get('value') is not None:
                f=structural[0]; row.update(verdict='REJECT',reason_code='value_contradiction',fact_id=f['fact_id'])
            elif verified_candidates and c.get('scope_text'): row['reason_code']='scope_mismatch'
            elif not candidates and o:
                role_matches=[]
                for f in subject_predicate_facts:
                    if not verified(f): continue
                    fq=f.get('quantity') or {}
                    if fq.get('measure')!=(q or {}).get('measure') or fq.get('unit')!=(q or {}).get('unit'): continue
                    if (q or {}).get('value') is not None and not qtymatch(f): continue
                    if f.get('qualifiers',{}).get('negated',False)!=claim_negated or not _same_time(c.get('time'),f): continue
                    if c.get('scope_text') and _norm(c['scope_text'])!=_norm(str(f.get('qualifiers',{}).get('scope',''))): continue
                    role_matches.append(f)
                if role_matches: row.update(verdict='REJECT',reason_code='role_contradiction',fact_id=role_matches[0]['fact_id'])
            elif candidates and not matched: row['reason_code']='no_fact'
            else: row['reason_code']='no_fact'
        elif candidates and any(results.get(f.get('fact_id'),{}).get('status') not in ('verified','disputed') for f in candidates):
            row['reason_code']='unverified_fact'
        elif not candidates: row['reason_code']='no_fact'
        rows.append(row)
    if not extraction.get('complete',False):
        rows.append({'claim_id':None,'span':'','field':None,'fact_id':None,'verdict':'REVIEW','reason_code':'extractor_incomplete'})
    if not extraction.get('claims') and extraction.get('complete',False):
        rows.append({'claim_id':None,'span':'','field':None,'fact_id':None,'verdict':'REVIEW','reason_code':'no_fact','reason':'no checkable claim'})
    verdict=max((r['verdict'] for r in rows),key=lambda v:{'PASS':0,'REVIEW':1,'REJECT':2}[v],default='REVIEW')
    return {'verdict':verdict,'claims':rows}

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
    # Trường rỗng từ extractor (None) không được làm sập gate.
    s=unicodedata.normalize('NFD',str(s or '').casefold())
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
