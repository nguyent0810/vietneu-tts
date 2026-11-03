"""Span keyed semantic review and verified fact retrieval."""
from __future__ import annotations
import json, re, subprocess
from pathlib import Path
from .check import spans_for, norm, _names, _number_tokens

HERE=Path(__file__).resolve().parent

def relevant_facts(package,store,verification,spans=None):
    states={x.get("fact_id"):x for x in verification.get("results",[])}
    facts=[f for f in store.get("facts",[]) if states.get(f.get("fact_id"),{}).get("status")=="verified"]
    entities=store.get("entities",[]); result={}; missing=[]
    for sp in spans if spans is not None else spans_for(package):
        sentence=sp["sentence"]; entity_ids={e.get("entity_id") for e in _names(sentence,store)}
        tokens=set(re.findall(r"[a-z0-9]+",norm(sentence))); chosen=[]
        for f in facts:
            entmatch=bool(entity_ids & {f.get("subject"),f.get("object")})
            predicate_tokens=set(re.findall(r"[a-z0-9]+",norm(f.get("predicate",""))))
            predmatch=bool(predicate_tokens and predicate_tokens & tokens)
            fact_text=norm(f.get("statement_vi","")); fact_tokens=set(re.findall(r"[a-z0-9]+",fact_text))
            tokenmatch=len(tokens & fact_tokens)>=2
            claimmatch=any(f.get("fact_id") in c.get("fact_ids",[]) and c.get("field")==sp["field"] for c in package.get("claims",[]))
            if entmatch or predmatch or tokenmatch or claimmatch: chosen.append(f)
        result[sp["span_id"]]=chosen
        factual=bool(entity_ids or list(_number_tokens(sentence)))
        if factual and not chosen: missing.append(sp["span_id"])
    return result,missing

def _usage(event):
    if event.get("type")=="event_msg" and (event.get("payload") or {}).get("type")=="token_count":
        info=(event["payload"].get("info") or {}).get("total_token_usage") or {}
        return info.get("total_tokens")
    usage=event.get("usage") or event.get("token_usage")
    if isinstance(usage,dict):
        return usage.get("total_tokens",(usage.get("input_tokens",0)+usage.get("output_tokens",0)) if "input_tokens" in usage and "output_tokens" in usage else None)
    return None

def semantic_review(package,facts_by_span,spans,cli="codex",replay=None):
    if replay:
        data=json.loads(Path(replay).read_text(encoding="utf-8")); data.setdefault("model","replay"); data.setdefault("tokens",None); return data
    prompt=(HERE/"review_prompt_v1.md").read_text(encoding="utf-8")
    facts={f.get("fact_id"):f for rows in facts_by_span.values() for f in rows}
    payload={"spans_to_review":[{"span_id":s["span_id"],"field":s["field"],"sentence":s["sentence"]} for s in spans],"facts":list(facts.values())}
    request=prompt+"\n\nINPUT JSON:\n"+json.dumps(payload,ensure_ascii=False)
    proc=subprocess.run([cli,"exec","--json","--skip-git-repo-check","-s","read-only","-"],input=request,text=True,capture_output=True,check=False,timeout=900)
    if proc.returncode: raise RuntimeError(f"review CLI failed ({proc.returncode}): {proc.stderr[-2000:]}")
    model=None; tokens=None; answer=None
    for line in proc.stdout.splitlines():
        try: event=json.loads(line)
        except ValueError: continue
        if event.get("type")=="turn.completed": model=event.get("model") or model
        if event.get("type")=="item.completed" and event.get("item",{}).get("type")=="agent_message": answer=event["item"].get("text")
        if event.get("type")=="event_msg" and (event.get("payload") or {}).get("type")=="turn_context": model=(event["payload"].get("model") or model)
        total=_usage(event)
        if total is not None: tokens=total
    if answer is None: answer=proc.stdout.strip()
    try: data=json.loads(answer)
    except (TypeError,ValueError) as exc: raise ValueError("reviewer did not return JSON") from exc
    if isinstance(data,list): data={"sentences":data}
    if not isinstance(data,dict): raise ValueError("reviewer response must be an object")
    data["model"]=model or "unknown"; data["tokens"]=tokens
    return data
