from __future__ import annotations
from dataclasses import dataclass, asdict
import re
from typing import Any
from .config import FORBIDDEN_PHRASES

@dataclass
class Claim:
    text: str
    kind: str
    span: tuple[int, int]
    field: str = ""

@dataclass
class Provenance:
    fact_id: str | None
    match_kind: str
    span: tuple[int, int] | None
    source_url: str | None
    certainty: str | None

_UNIT = r"(?<!\w)(?:%|km|cm|mm|mét|met|m|đồng|usd|eth|ngày|năm|triệu|tỷ)(?!\w)"
_NUM = re.compile(rf"(?<![\w])(?:\d{{1,3}}(?:\.\d{{3}})+(?:,\d+)?|\d+(?:,\d+)?)(?:\s*(?:{_UNIT}))?", re.I)
_DATE = re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}[/-]\d{4}|\d{4})\b")
_WORDNUM = re.compile(r"(?<!\w)(?:(?:một|hai|ba|bốn|tư|năm|sáu|bảy|tám|chín|mười|mươi|trăm|nghìn|ngàn|triệu|tỷ|linh|lẻ|lăm|mốt|phẩy|không)(?:\s+|$))+(?:"+_UNIT+r")?", re.I)
_REL_WORDS = {
 "compromised": ("bị hack", "bị xâm nhập", "xâm nhập", "hack", "compromised"),
 "lost_asset": ("mất", "thất thoát", "bị đánh cắp", "đánh cắp", "rút", "lost"),
 "harmed": ("gây thiệt hại", "bị ảnh hưởng", "harmed"),
 "attributed_to": ("quy cho", "chịu trách nhiệm", "do", "attributed to"),
 "root_cause": ("nguyên nhân", "do mã độc", "do javascript", "root cause"),
 "grew/changed": ("cao thêm", "tăng", "giảm", "mất", "mọc", "nâng lên", "grew", "increased", "decreased"),
 "discovered": ("phát hiện", "discovered"), "wrote": ("viết", "wrote"),
}
_ASSERT = re.compile(r"\b(?:chắc\s+chắn|đảm\s+bảo|cam\s+kết|nhất\s+định|sẽ\s+(?:tăng|giảm|thành công|khỏi|giàu)|đe\s+dọa|doạ)\b", re.I)
_PROPER = re.compile(r"(?<![\w])(?:[A-ZÀ-ỸĐ][\wÀ-ỹĐđ]*(?:\s+[A-ZÀ-ỸĐ][\wÀ-ỹĐđ]*){0,4})")

_SMALL={"không":0,"một":1,"hai":2,"ba":3,"bốn":4,"tư":4,"năm":5,"sáu":6,"bảy":7,"tám":8,"chín":9}
def _spoken_number(s: str) -> float | None:
    s=re.sub(rf"\s*(?:{_UNIT})\s*$","",s.strip(),flags=re.I).casefold()
    if not re.search(r"\b(?:một|hai|ba|bốn|tư|năm|sáu|bảy|tám|chín|mười|mươi|trăm|nghìn|ngàn|triệu|tỷ|linh|lẻ|lăm|mốt|phẩy|không)\b",s): return None
    if "phẩy" in s:
        a,b=s.split("phẩy",1); left=_spoken_number(a) or 0
        digits="".join(str(_SMALL.get(w,0)) for w in b.split())
        return left+float("0."+digits) if digits else left
    words=s.split(); total=0; cur=0; i=0
    while i<len(words):
        w=words[i]
        if w in ("linh","lẻ"): i+=1; continue
        if w in _SMALL:
            n=_SMALL[w]
            if i+1<len(words) and words[i+1]=="trăm": cur+=n*100; i+=2; continue
            if i+1<len(words) and words[i+1] in ("mười","mươi"): cur+=n*10; i+=2; continue
            cur+=n; i+=1; continue
        if w in ("mười","mươi"): cur+=10; i+=1; continue
        if w=="trăm": cur+=100; i+=1; continue
        if w in ("nghìn","ngàn","triệu","tỷ"):
            total+=(cur or 1)*{"nghìn":1000,"ngàn":1000,"triệu":1000000,"tỷ":1000000000}[w]; cur=0; i+=1; continue
        if w in ("lăm","mốt"): cur+=5 if w=="lăm" else 1
        i+=1
    return float(total+cur)

def _norm_number(s: str) -> float | None:
    spoken=_spoken_number(s)
    if spoken is not None: return spoken
    s=re.sub(rf"\s*(?:{_UNIT})\s*$","",s,flags=re.I).strip()
    if not re.search(r"\d",s): return None
    if "." in s and "," in s: s=s.replace(".","").replace(",",".")
    elif "," in s:
        parts=s.split(","); s="".join(parts) if len(parts[-1])==3 and len(parts)>1 else ".".join(parts)
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+",s): s=s.replace(".","")
    try:return float(s)
    except ValueError:return None

def _unit(s: str) -> str | None:
    m=re.search(rf"({_UNIT})\s*$",s.strip(),re.I)
    if not m:return None
    u=m.group(1).casefold()
    return {"mét":"m","met":"m","km":"m","cm":"m","mm":"m","usd":"usd","đồng":"vnd","tỷ":"vnd_scale","triệu":"vnd_scale"}.get(u,u)
def _quantity(s: str):
    m=_NUM.search(s) or _WORDNUM.search(s)
    if not m:return None,None
    value=_norm_number(m.group()); unit=_unit(m.group())
    raw_unit=re.search(rf"({_UNIT})\s*$",m.group().strip(),re.I)
    if value is not None and raw_unit:
        u=raw_unit.group(1).casefold()
        value *= {"km":1000,"cm":.01,"mm":.001,"triệu":1_000_000,"tỷ":1_000_000_000}.get(u,1)
    return value,unit
def _nums(text: str):
    return [(m.group(),m.span(),_norm_number(m.group())) for p in (_NUM,_WORDNUM) for m in p.finditer(text)]

def _sentence(text: str, pos: int) -> str:
    bounds=[]
    for i,ch in enumerate(text):
        if ch in "!?\n" or (ch=="." and not (i>0 and i+1<len(text) and text[i-1].isdigit() and text[i+1].isdigit())): bounds.append(i)
    left=max((i+1 for i in bounds if i<pos),default=0)
    right=min((i for i in bounds if i>=pos),default=len(text))
    return text[left:right].strip()

def extract_claims(text: str) -> list[Claim]:
    hits=[]
    for pat,kind in ((_DATE,"date"),(_NUM,"number"),(_WORDNUM,"number"),(_PROPER,"entity"),(_ASSERT,"assertion")):
        for m in pat.finditer(text): hits.append((m.start(),m.end(),kind,m.group()))
    hits.sort(key=lambda h:(h[0],-(h[1]-h[0])))
    out=[]; occupied=[]
    for s,e,k,t in hits:
        if any(s<z and a<e for a,z in occupied):continue
        occupied.append((s,e)); out.append(Claim(_sentence(text,s),k,(s,e)))
    return out

def _fact_text(f): return " ".join(str(f.get(k,"")) for k in ("statement","value","edition"))
def _main_entity(topic):
    roles=topic.get("entity_roles",{})
    for k in ("harmed_org","compromised_system","stolen_asset"):
        if roles.get(k): return str(roles[k]).split(":",1)[0]
    return topic.get("slug","").replace("_"," ")
def _subject(claim,topic):
    txt=claim.text.casefold()
    candidates=[_main_entity(topic)]
    candidates += [str(v).split(":",1)[0] for v in topic.get("entity_roles",{}).values()]
    for ent in candidates:
        if ent and ent.casefold() in txt:return ent.casefold()
    for m in _PROPER.finditer(claim.text):
        if m.start()==0: continue
        return m.group().casefold()
    return ""
def _canonical(p):
    p=str(p).casefold()
    if p in {"grew/changed","grew","changed","increased","decreased"}:return "grew/changed"
    return p
def _claim_triple(claim,topic):
    text=claim.text.casefold(); sub=_subject(claim,topic)
    for rel,verbs in _REL_WORDS.items():
        if any(v in text for v in verbs):
            obj=""
            if rel=="lost_asset": obj="asset"
            elif rel=="compromised": obj="system"
            elif rel=="grew/changed": obj="change"
            else: obj=""
            return sub,_canonical(rel),obj
    return None
def _fact_triples(f):
    triples=[]
    for rel in f.get("relations",[]) or []:
        if len(rel)>=3:triples.append((str(rel[0]).casefold(),_canonical(rel[1]),str(rel[2]).casefold()))
    return triples
def _relation_match(claim,topic,facts):
    tri=_claim_triple(claim,topic)
    if not tri:return None
    subj,pred,obj=tri; possible=[]
    for f in facts:
        for fs,fp,fo in _fact_triples(f):
            if fp!=pred:continue
            subject_ok=bool(subj and (subj in fs or fs in subj or fs in claim.text.casefold()))
            if subject_ok:possible.append((f,fo))
    if possible:
        # For common lexical aliases, the explicit entity_roles guard supplies the contradiction.
        f,_=possible[0]
        return f,"relation"
    return None

def match(claim: Claim | str, fact_table: list[dict], declared_claims: list[dict] | None = None, topic: dict | None = None) -> Provenance:
    if isinstance(claim,str):claim=Claim(claim,"text",(0,len(claim)))
    topic=topic or {}; text=claim.text; subj=_subject(claim,topic); val,unit=_quantity(text)
    # Relations require a fact relation with the same canonical predicate and subject.
    rel=_relation_match(claim,topic,fact_table)
    if rel:
        f,_=rel; return Provenance(f.get("fact_id"),"relation",claim.span,f.get("source_url"),f.get("certainty"))
    dates=set(_DATE.findall(text))
    if dates and subj:
        for f in fact_table:
            ft=_fact_text(f)
            if subj in ft.casefold() and dates & set(_DATE.findall(ft)):
                return Provenance(f.get("fact_id"),"date",claim.span,f.get("source_url"),f.get("certainty"))
    if claim.kind=="number" or val is not None:
        if val is None or unit is None or not subj:return Provenance(None,"none",claim.span,None,None)
        same_subject=[]
        for f in fact_table:
            ft=_fact_text(f); fsub=ft.casefold()
            if subj not in fsub and not any(subj in str(x).casefold() for triple in f.get("relations",[]) or [] for x in triple):continue
            fv,fu=_quantity(str(f.get("value","")))
            if fv is None: fv,fu=_quantity(str(f.get("statement","")))
            if fv is None or fu!=unit:continue
            same_subject.append((f,fv))
            if abs(val-fv)<1e-8:return Provenance(f.get("fact_id"),"exact_number",claim.span,f.get("source_url"),f.get("certainty"))
        if same_subject:
            f,_=same_subject[0]
            return Provenance("!contradiction:"+str(f.get("fact_id")),"contradiction",claim.span,f.get("source_url"),f.get("certainty"))
    # Date-only match requires same subject as well.
    if dates and subj:
        for f in fact_table:
            ft=_fact_text(f)
            if subj in ft.casefold() and dates & set(_DATE.findall(ft)):
                return Provenance(f.get("fact_id"),"date",claim.span,f.get("source_url"),f.get("certainty"))
    return Provenance(None,"none",claim.span,None,None)

def gate(level: dict, topic: dict) -> dict:
    fields=("title","thumbnail_text","voice_0_3s","escalation_3_10s"); results=[]
    facts=topic.get("fact_table",[])
    for field in fields:
        text=level.get(field) or ""
        for c in extract_claims(text):
            c.field=field; p=match(c,facts,level.get("claims",[]),topic)
            verdict="REVIEW"; reason="Không có fact khớp đủ để kiểm chứng claim định tính."
            if any(x in c.text.casefold() for x in FORBIDDEN_PHRASES) and field in ("title","voice_0_3s"):
                verdict="REJECT"; reason="Chứa cụm hứa tiền/tương lai chắc chắn/doạ bị kênh cấm."
            elif p.match_kind=="contradiction":
                verdict="REJECT"; reason="Giá trị khác fact verified cùng chủ thể và đơn vị."
            elif p.fact_id:
                fact=next((f for f in facts if f.get("fact_id")==p.fact_id),{})
                # Change claims need direct relation evidence; a coincident magnitude is insufficient.
                if _claim_triple(c,topic) and _claim_triple(c,topic)[1]=="grew/changed" and p.match_kind!="relation":
                    verdict="REVIEW"
                elif field in ("title","thumbnail_text") and fact.get("certainty") in ("contested","unknown"):
                    verdict="REJECT"; reason=f"Fact {p.fact_id} có certainty={fact.get('certainty')} trong title/thumbnail."
                elif p.certainty=="verified": verdict="PASS"; reason=f"Khớp fact verified {p.fact_id}."
                else: verdict="REVIEW"; reason=f"Fact {p.fact_id} không verified ({p.certainty})."
            results.append({"claim":asdict(c),"provenance":asdict(p),"verdict":verdict,"reason":reason})
    # Entity role contradiction: known harmful actor/system mismatch is proof of wrong attribution.
    roles=topic.get("entity_roles",{}); role_text=" ".join((level.get(f) or "") for f in fields).casefold()
    org=str(roles.get("harmed_org","")).split(":",1)[0].casefold(); system=str(roles.get("compromised_system","")).split(":",1)[0].casefold()
    if org and system and org in role_text and any(v in role_text for v in _REL_WORDS["compromised"]) and org not in system:
        for r in results:
            if org in r["claim"]["text"].casefold():
                r["verdict"]="REJECT"; r["reason"]="Vai trò thực thể trái entity_roles của topic."
    overall="REJECT" if any(x["verdict"]=="REJECT" for x in results) else "REVIEW" if any(x["verdict"]=="REVIEW" for x in results) else "PASS"
    return {"level":level.get("name"),"verdict":overall,"claims":results}
