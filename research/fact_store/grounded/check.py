"""Deterministic, token-free checks for fact-grounded creative packaging."""
from __future__ import annotations
import re
import unicodedata

RISK_WORDS = re.compile(r"\b(vì|khiến|nên|do|hoá ra|hóa ra|bí mật|sự thật là|thực ra|chứng minh|dẫn đến)\b", re.I)
FIELDS = ("title", "thumbnail_text", "first_frame_0_1s", "voice_0_3s", "escalation_3_10s", "payoff")
KINDS = {"interpretive", "implied", "causal", "metaphor", "promise"}

def norm(value):
    s = unicodedata.normalize("NFC", str(value or "")).casefold()
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

def _verification(verification):
    return {r.get("fact_id"): r for r in verification.get("results", [])}

def _text(package):
    return " ".join(str(package.get(k) or "") for k in FIELDS)

def _numbers(text):
    """Yield numeric tokens while preserving Vietnamese word diacritics."""
    n=unicodedata.normalize("NFC",str(text or "")).casefold()
    words=r"một|hai|ba|bốn|tư|năm|sáu|bảy|tám|chín|mười(?:\s+(?:một|hai|lăm|bốn))?"
    units=r"%|usd|vnd|đồng|eth|km|m|mét|năm|ngày|tháng|người|lần|giờ"
    mags=r"tỷ|triệu|nghìn|ngàn"
    # Words are quantities only when explicitly connected to a unit/magnitude.
    pat=re.compile(rf"(?<!\w)(?P<num>\d{{1,3}}(?:\.\d{{3}})+(?:,\d+)?|\d+(?:[.,]\d+)?|{words})(?P<tail>\s*(?:{mags})?(?:\s*(?:{units}))?)?(?!\w)",re.I)
    vals={"một":1,"hai":2,"ba":3,"bốn":4,"tư":4,"năm":5,"sáu":6,"bảy":7,"tám":8,"chín":9,"mười":10,"mười một":11,"mười hai":12,"mười lăm":15,"mười bốn":14}
    for m in pat.finditer(n):
        raw=m.group("num"); tail=m.group("tail") or ""
        if not raw[0].isdigit() and not tail.strip(): continue
        try: value=float(raw.replace(".","").replace(",","."))
        except ValueError: value=vals.get(raw)
        if value is None: continue
        mag=next((x for x in ("tỷ","triệu","nghìn","ngàn") if x in tail),"")
        mult={"tỷ":1e9,"triệu":1e6,"nghìn":1e3,"ngàn":1e3}.get(mag,1)
        unit=next((x for x in ("%","usd","vnd","đồng","eth","km","mét","m","năm","ngày","tháng","người","lần","giờ") if re.search(rf"\b{re.escape(x)}\b",tail)),"")
        yield value*mult,unit,m.group(0).strip()

def _date_tokens(text):
    n = norm(text)
    out=[]
    for m in re.finditer(r"\b(?:nam\s*)?(1[0-9]{3}|20[0-9]{2}|21[0-9]{2})(?:[-/](\d{1,2})(?:[-/](\d{1,2}))?)?\b", n):
        out.append(m.group(0))
    return out

def _verified(facts, states):
    return [f for f in facts if states.get(f.get("fact_id"), {}).get("status") == "verified"]

def _number_supported(value, unit, facts, states):
    matched=[]
    for f in _verified(facts, states):
        q=f.get("quantity") or {}
        if q.get("value") is None: continue
        fact_unit=norm(q.get("unit", ""))
        if unit and unit not in fact_unit and not (unit in ("dong","vnd") and fact_unit in ("vnd","dong")): continue
        x=float(q["value"]); y=value
        if abs(x-y) <= max(abs(x)*.05, 1): matched.append(f)
    return matched

def _date_supported(token, facts, states):
    year=re.search(r"(\d{4})", token)
    if not year: return []
    target=year.group(1)
    found=[]
    for f in _verified(facts, states):
        txt=" ".join([*[str((f.get("time") or {}).get(k) or "") for k in ("start","end")], str(f.get("statement_vi") or ""), *[str(e.get("span") or e.get("text") or "") for e in f.get("evidence",[])]])
        if target in txt: found.append(f)
    return found

def _normalized_number_forms(value):
    x=float(value); forms={str(int(x)) if x.is_integer() else str(x)}
    forms.add(f"{x:,.1f}".replace(",","X").replace(".",",").replace("X","."))
    return forms

def _text_fact_matches(value, unit, f):
    q=f.get("quantity") or {}
    if q.get("value") is not None:
        try:
            if abs(float(q["value"])-value)<=max(abs(value)*.005,1e-8) and (not unit or norm(unit) in norm(q.get("unit",""))): return True
        except (TypeError,ValueError): pass
    text=" ".join([str(f.get("statement_vi") or ""),*[str(e.get("span") or e.get("text") or "") for e in f.get("evidence",[])]])
    flat=norm(text)
    return any(norm(form) in flat for form in _normalized_number_forms(value))

def _names(text, store):
    n=norm(text); found=[]
    for ent in store.get("entities",[]):
        names=[ent.get("name", ""), *ent.get("aliases", [])]
        if any(a and re.search(r"(?<!\w)"+re.escape(norm(a))+r"(?!\w)", n) for a in names):
            found.append(ent)
    return found

def det_check(package, store, verification, explain=False):
    facts=store.get("facts", []); fact_by={f.get("fact_id"):f for f in facts}
    sources={s.get("source_id") for s in store.get("sources", [])}; states=_verification(verification)
    issues=[]; needs=[]; text=_text(package); claims=package.get("claims") or []
    for i,c in enumerate(claims):
        for fid in c.get("fact_ids", []):
            if fid not in fact_by: issues.append({"code":"missing_fact_id","claim":i,"fact_id":fid,"severity":"review"}); continue
            status=states.get(fid,{}).get("status")
            if status == "unverified" or status is None:
                issues.append({"code":"unverified_ref","claim":i,"fact_id":fid,"severity":"review"})
            elif status == "disputed":
                fact=fact_by[fid]; attribution=(fact.get("qualifiers") or {}).get("attributed_to")
                srcs={s.get("source_id"):s for s in store.get("sources", [])}
                publisher=next((srcs[e.get("source_id" )].get("publisher") for e in fact.get("evidence",[]) if e.get("source_id") in srcs),None)
                span=norm(c.get("span", ""))
                attributed=attribution and any(norm(e.get("entity_id")) in span or norm(e.get("name")) in span for e in store.get("entities",[]) if e.get("entity_id")==attribution)
                attributed=attributed or (publisher and norm(publisher) in span)
                if not attributed: issues.append({"code":"unattributed_disputed","claim":i,"fact_id":fid,"severity":"review"})
        for sid in c.get("source_ids", []):
            if sid not in sources: issues.append({"code":"missing_source_id","claim":i,"source_id":sid,"severity":"review"})
        if c.get("kind") in KINDS: needs.append({"field":c.get("field"),"span":c.get("span",""),"reason":"claim_kind"})
    claims_by_field={f:[] for f in FIELDS}
    for c in claims: claims_by_field.setdefault(c.get("field"),[]).append(c)
    for field in FIELDS:
        for sentence in re.split(r"(?<=[.!?])\s+", str(package.get(field) or "")):
            sentence=sentence.strip()
            if not sentence: continue
            relevant=[c for c in claims_by_field.get(field,[]) if norm(c.get("span")) in norm(sentence)]
            if RISK_WORDS.search(sentence): needs.append({"field":field,"span":sentence,"reason":"causal_or_implicature_language"})
            elif not relevant: needs.append({"field":field,"span":sentence,"reason":"unclaimed_sentence"})
    if claims == []:
        needs.extend({"field":f,"span":str(package.get(f) or ""),"reason":"missing_claims"} for f in FIELDS if package.get(f))
    for value,unit,raw in _numbers(text):
        matched=_number_supported(value,unit,facts,states)
        textual=[f for f in _verified(facts,states) if _text_fact_matches(value,unit,f)]
        matched=list({f.get("fact_id"):f for f in matched+textual}.values())
        if not matched: issues.append({"code":"ungrounded_number","token":raw,"severity":"review","compared_facts":[]})
        elif explain: issues.append({"code":"grounded_number","token":raw,"fact_ids":[f.get("fact_id") for f in matched],"severity":"info"})
    for token in _date_tokens(text):
        matched=_date_supported(token,facts,states)
        if not matched: issues.append({"code":"ungrounded_date","token":token,"severity":"review","compared_facts":[]})
        elif explain: issues.append({"code":"grounded_date","token":token,"fact_ids":[f.get("fact_id") for f in matched],"severity":"info"})
    entities=_names(text,store)
    for ent in entities:
        refs=[f for f in _verified(facts,states) if f.get("subject")==ent.get("entity_id") or f.get("object")==ent.get("entity_id")]
        if not refs: issues.append({"code":"ungrounded_name","entity_id":ent.get("entity_id"),"name":ent.get("name"),"severity":"review"})
    # Check verified facts with same entity and measure for numeric contradiction.
    for value,unit,raw in _numbers(text):
        if _number_supported(value,unit,facts,states) or any(_text_fact_matches(value,unit,f) for f in _verified(facts,states)): continue
        # Contradiction needs an entity in the same sentence and matching
        # measure/unit; unrelated verified quantities cannot reject copy.
        sentence=next((s for s in re.split(r"(?<=[.!?])\s+",text) if raw.strip() and raw.casefold() in unicodedata.normalize("NFC",s).casefold()),"")
        mentioned={e.get("entity_id") for e in _names(sentence,store)}
        if not mentioned: continue
        for f in _verified(facts,states):
            q=f.get("quantity") or {}
            same_entity=f.get("subject") in mentioned or f.get("object") in mentioned
            same_unit=not unit or norm(q.get("unit",""))==unit or unit in ("dong","vnd") and norm(q.get("unit","")) in ("vnd","dong")
            measure=norm(f.get("predicate","")); same_measure=bool(measure and measure in norm(sentence))
            time_role=bool((f.get("time") or {}).get("start") and (f.get("time") or {}).get("start") in sentence)
            if same_entity and same_unit and same_measure and time_role and q.get("value") is not None and abs(float(q["value"])-value)>max(abs(float(q["value"]))*0.05,1):
                issues.append({"code":"contradiction","token":raw,"entity":next(iter(mentioned)),"measure":f.get("predicate"),"fact_id":f.get("fact_id"),"fact_value":q,"severity":"reject"}); break
    for c in claims:
        for fid in c.get("fact_ids",[]):
            f=fact_by.get(fid,{}); q=f.get("qualifiers",{}); mod=q.get("modality")
            cues={"legendary":("tuong truyen","truyen thuyet","theo truyen"),"traditional":("theo quan niem","theo truyen thong"),"hypothesized":("gia thuyet","duoc gia thuyet")}
            span=norm(c.get("span","")); context=norm(package.get("series_context",""))
            if q.get("condition") and not any(norm(x) in span for x in (str(q["condition"]),)):
                issues.append({"code":"dropped_qualifier","qualifier":"condition","claim":c.get("span"),"severity":"review"}); needs.append({"field":c.get("field"),"span":c.get("span"),"reason":"dropped_condition"})
            if q.get("attributed_to") and not any(norm(e.get("name")) in span or norm(e.get("name")) in norm(text) for e in store.get("entities",[]) if e.get("entity_id")==q["attributed_to"]):
                issues.append({"code":"dropped_qualifier","qualifier":"attribution","claim":c.get("span"),"severity":"review"}); needs.append({"field":c.get("field"),"span":c.get("span"),"reason":"dropped_attribution"})
            if mod in cues and not any(x in span for x in cues[mod]) and not (mod in ("legendary","traditional") and any(x in context for x in cues[mod])):
                issues.append({"code":"dropped_qualifier","qualifier":"modality","claim":c.get("span"),"severity":"review"}); needs.append({"field":c.get("field"),"span":c.get("span"),"reason":"dropped_modality"})
    dedup=[]; seen=set()
    for item in needs:
        key=(item.get("field"),item.get("span"),item.get("reason"))
        if key not in seen: seen.add(key); dedup.append(item)
    verdict="REJECT" if any(i["code"]=="contradiction" for i in issues) else "REVIEW" if issues or dedup else "APPROVED"
    return {"issues":issues,"needs_semantic":dedup,"verdict_hint":verdict}
