"""Deterministic, token-free checks for fact-grounded creative packaging."""
from __future__ import annotations
import hashlib, re, unicodedata

FIELDS = ("title", "thumbnail_text", "first_frame_0_1s", "voice_0_3s", "escalation_3_10s", "payoff")
KINDS = {"interpretive", "implied", "causal", "metaphor", "promise"}
RISK_WORDS = re.compile(r"\b(vì|khiến|nên|do|hoá ra|hóa ra|bí mật|sự thật là|thực ra|chứng minh|dẫn đến)\b", re.I)

def norm(value):
    s=unicodedata.normalize("NFD",unicodedata.normalize("NFC",str(value or "")).casefold())
    return "".join(c for c in s if unicodedata.category(c)!="Mn")

def spans_for(package):
    out=[]
    for field in FIELDS:
        value=str(package.get(field) or "")
        if not value.strip(): continue
        sentences=[x.strip() for x in re.split(r"(?<=[.!?])\s+",value) if x.strip()]
        if not sentences: sentences=[value.strip()]
        for index,sentence in enumerate(sentences):
            sid=f"{field}:{index}:{hashlib.sha1(sentence.encode('utf-8')).hexdigest()[:8]}"
            out.append({"span_id":sid,"field":field,"sentence":sentence})
    return out

def _verification(v): return {x.get("fact_id"):x for x in v.get("results",[])}
def _verified(facts,states): return [f for f in facts if states.get(f.get("fact_id"),{}).get("status")=="verified"]

def _number_tokens(text):
    pat=re.compile(r"(?<!\w)(\d+(?:[.,]\d+)?)(?:\s*(tỷ|triệu|nghìn|ngàn))?(?:\s*(km|mét|m|usd|vnd|đồng|đô|\$|%|năm|ngày|tháng|người|lần|giờ))?(?!\w)",re.I)
    for m in pat.finditer(text):
        raw=m.group(0); unit=(m.group(3) or "").casefold(); mag=(m.group(2) or "").casefold()
        try: value=float(m.group(1).replace(",","."))
        except ValueError: continue
        value*=({"tỷ":1e9,"triệu":1e6,"nghìn":1e3,"ngàn":1e3}.get(mag,1))
        yield value,unit,raw,m.start(),m.end()

def _unit_identity(unit):
    u=norm(unit)
    if u=="km": return ("length",1000)
    if u in ("m","met"): return ("length",1)
    if u in ("usd","$","do"): return ("currency_usd",1)
    if u in ("vnd","dong"): return ("currency_vnd",1)
    if u=="%": return ("percent",1)
    return (u,1) if u else ("",1)

def _quantity_matches(value,unit,facts):
    target,scale=_unit_identity(unit); out=[]
    for f in facts:
        q=f.get("quantity") or {}
        if q.get("value") is None: continue
        source,sscale=_unit_identity(q.get("unit",""))
        if target!=source: continue
        if abs(float(q["value"])*sscale-value*scale)<=max(abs(value*scale)*.05,1): out.append(f)
    return out

def _names(text,store):
    n=norm(text); return [e for e in store.get("entities",[]) if any(a and re.search(r"(?<!\w)"+re.escape(norm(a))+r"(?!\w)",n) for a in [e.get("name","")]+e.get("aliases",[]))]

def _dates(text):
    return [m.group(0) for m in re.finditer(r"\b(?:năm\s*)?(?:19|20|21)\d{2}(?:[-/]\d{1,2}(?:[-/]\d{1,2})?)?\b",text,re.I)]

def _date_matches(token,facts):
    year=re.search(r"\d{4}",token)
    if not year: return []
    y=year.group(0); found=[]
    for f in facts:
        content=" ".join([str((f.get("time") or {}).get(k) or "") for k in ("start","end")]+[str(f.get("statement_vi") or "")]+[str(e.get("span") or e.get("text") or "") for e in f.get("evidence",[])])
        if re.search(r"(?<!\d)"+re.escape(y)+r"(?!\d)",content): found.append(f)
    return found

def det_check(package,store,verification,explain=False):
    facts=store.get("facts",[]); fact_by={f.get("fact_id"):f for f in facts}; states=_verification(verification)
    spans=spans_for(package); issues=[]; needs=[]; claims=package.get("claims") or []
    def sentence_for(field,claimspan=""):
        candidates=[s for s in spans if s["field"]==field]
        return next((s for s in candidates if claimspan and norm(claimspan) in norm(s["sentence"])),candidates[0] if len(candidates)==1 else None)
    for i,c in enumerate(claims):
        sp=sentence_for(c.get("field"),c.get("span","")); sid=sp and sp["span_id"]
        for fid in c.get("fact_ids",[]):
            f=fact_by.get(fid)
            if not f: issues.append({"code":"missing_fact_id","claim":i,"fact_id":fid,"span_id":sid,"severity":"review"}); continue
            status=states.get(fid,{}).get("status")
            if status in (None,"unverified"): issues.append({"code":"unverified_ref","claim":i,"fact_id":fid,"span_id":sid,"severity":"review"})
            elif status=="disputed":
                attribution=(f.get("qualifiers") or {}).get("attributed_to"); sent=norm(sp["sentence"] if sp else c.get("span",""))
                if not attribution or not any(norm(e.get("name")) in sent for e in store.get("entities",[]) if e.get("entity_id")==attribution):
                    issues.append({"code":"unattributed_disputed","claim":i,"fact_id":fid,"field":c.get("field"),"span_id":sid,"severity":"review"})
    for sp in spans:
        related=[c for c in claims if c.get("field")==sp["field"] and norm(c.get("span")) in norm(sp["sentence"])]
        if RISK_WORDS.search(sp["sentence"]): needs.append({**sp,"reason":"causal_or_implicature_language"})
        if any(c.get("kind") in KINDS for c in related): needs.append({**sp,"reason":"claim_kind"})
        elif not related: needs.append({**sp,"reason":"unclaimed_sentence"})
        for value,unit,raw,start,end in _number_tokens(sp["sentence"]):
            if any(raw.strip() in token for token in _dates(sp["sentence"])): continue
            matched=_quantity_matches(value,unit,_verified(facts,states))
            if not matched:
                issues.append({"code":"ungrounded_number","token":raw,"subspan":sp["sentence"][start:end],"span_id":sp["span_id"],"severity":"review","compared_facts":[]})
        for token in _dates(sp["sentence"]):
            if not _date_matches(token,_verified(facts,states)):
                issues.append({"code":"ungrounded_date","token":token,"subspan":token,"span_id":sp["span_id"],"severity":"review","compared_facts":[]})
        for ent in _names(sp["sentence"],store):
            refs=[f for f in _verified(facts,states) if f.get("subject")==ent.get("entity_id") or f.get("object")==ent.get("entity_id")]
            if not refs: issues.append({"code":"ungrounded_name","entity_id":ent.get("entity_id"),"name":ent.get("name"),"subspan":ent.get("name"),"span_id":sp["span_id"],"severity":"review"})
    # A possible contradiction requires a verified fact for the named entity and exact unit.
    for sp in spans:
        ents=_names(sp["sentence"],store)
        for value,unit,raw,start,end in _number_tokens(sp["sentence"]):
            if _quantity_matches(value,unit,_verified(facts,states)): continue
            for ent in ents:
                for f in _verified(facts,states):
                    q=f.get("quantity") or {}
                    if f.get("subject")!=ent.get("entity_id") or q.get("value") is None: continue
                    if _unit_identity(q.get("unit",""))[0]!=_unit_identity(unit)[0]: continue
                    predicate=norm(f.get("predicate",""))
                    if predicate and re.search(r"(?<!\w)"+re.escape(predicate)+r"(?!\w)",norm(sp["sentence"])) and abs(float(q["value"])-value)>max(abs(float(q["value"]))*.05,1):
                        issues.append({"code":"contradiction","token":raw,"subspan":sp["sentence"][start:end],"span_id":sp["span_id"],"entity":ent["entity_id"],"fact_id":f.get("fact_id"),"severity":"reject"}); break
    for c in claims:
        sp=sentence_for(c.get("field"),c.get("span","")); sid=sp and sp["span_id"]
        for fid in c.get("fact_ids",[]):
            f=fact_by.get(fid,{})
            if states.get(fid,{}).get("status")!="verified": continue
            q=f.get("qualifiers") or {}; span=norm(c.get("span",""))
            if q.get("condition") and norm(q["condition"]) not in span:
                issues.append({"code":"dropped_qualifier","qualifier":"condition","field":c.get("field"),"span_id":sid,"subspan":c.get("span"),"severity":"review"})
                if sid: needs.append({**sp,"reason":"dropped_condition"})
            if q.get("attributed_to") and not any(norm(e.get("name")) in span for e in store.get("entities",[]) if e.get("entity_id")==q["attributed_to"]):
                issues.append({"code":"dropped_qualifier","qualifier":"attribution","field":c.get("field"),"span_id":sid,"subspan":c.get("span"),"severity":"review"})
                if sid: needs.append({**sp,"reason":"dropped_attribution"})
            modality=q.get("modality")
            cue_map={"legendary":("tuong truyen","truyen thuyet","theo truyen"),"traditional":("theo quan niem","theo truyen thong"),"hypothesized":("gia thuyet","duoc gia thuyet")}
            if modality in cue_map and not any(cue in span for cue in cue_map[modality]):
                issues.append({"code":"dropped_qualifier","qualifier":"modality","field":c.get("field"),"span_id":sid,"subspan":c.get("span"),"severity":"review"})
                if sid: needs.append({**sp,"reason":"dropped_modality"})
    # Every needs_semantic row points at its packaging sentence.
    unique=[]; seen=set()
    for row in needs:
        key=(row.get("span_id"),row.get("reason"))
        if key not in seen: seen.add(key); unique.append(row)
    hint="REJECT" if any(i.get("code")=="contradiction" for i in issues) else "REVIEW" if issues or unique else "APPROVED"
    return {"spans":spans,"issues":issues,"needs_semantic":unique,"verdict_hint":hint}
