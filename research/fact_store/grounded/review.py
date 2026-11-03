"""One-call independent semantic review, with deterministic replay support."""
from __future__ import annotations
import json, os, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent

def relevant_facts(package, store, verification):
    states={x.get("fact_id"):x for x in verification.get("results",[])}
    byid={x.get("fact_id"):x for x in store.get("facts",[])}
    selected=set()
    for c in package.get("claims",[]): selected.update(c.get("fact_ids",[]))
    entities=set()
    for fid in selected:
        if fid in byid:
            f=byid[fid]; entities.update(x for x in (f.get("subject"),f.get("object")) if x)
    for f in store.get("facts",[]):
        if f.get("subject") in entities or f.get("object") in entities: selected.add(f.get("fact_id"))
    return [{**byid[fid],"verification":states.get(fid,{"status":"unverified"})} for fid in sorted(selected) if fid in byid]

def semantic_review(package, facts_subset, cli="codex", replay=None):
    if replay:
        data=json.loads(Path(replay).read_text(encoding="utf-8"))
        data.setdefault("model", "replay"); data.setdefault("tokens", None)
        return data
    prompt=(HERE/"review_prompt_v1.md").read_text(encoding="utf-8")
    payload={"packaging":package,"facts":facts_subset,"sentences_to_review":[{"field":f,"text":package.get(f)} for f in ("title","thumbnail_text","first_frame_0_1s","voice_0_3s","escalation_3_10s","payoff") if package.get(f)]}
    request=prompt+"\n\nINPUT JSON:\n"+json.dumps(payload,ensure_ascii=False)
    proc=subprocess.run([cli,"exec","--json","--skip-git-repo-check","-s","read-only","-"],input=request,text=True,capture_output=True,check=False,timeout=900)
    if proc.returncode:
        raise RuntimeError(f"review CLI failed ({proc.returncode}): {proc.stderr[-2000:]}")
    raw=proc.stdout; model=None; tokens=None; answer=None
    for line in raw.splitlines():
        try: event=json.loads(line)
        except ValueError: continue
        # Trust CLI event metadata only, never model-authored metadata.
        if event.get("type") in ("turn.completed","result"):
            model=event.get("model") or model
            answer=event.get("text") or event.get("output") or answer
        for key in ("usage","token_usage"):
            usage=event.get(key)
            if isinstance(usage,dict):
                total=usage.get("total_tokens")
                if total is None and usage.get("input_tokens") is not None and usage.get("output_tokens") is not None:
                    total=usage["input_tokens"]+usage["output_tokens"]
                tokens=total if total is not None else tokens
        if event.get("type") in ("token_count","tokens"):
            tokens=event.get("total_tokens",event.get("token_count",tokens))
        if isinstance(event.get("total_tokens"),(int,float)): tokens=event["total_tokens"]
        if event.get("type")=="item.completed" and event.get("item",{}).get("type")=="agent_message": answer=event["item"].get("text")
    if answer is None: answer=raw.strip()
    try: result=json.loads(answer)
    except (TypeError,ValueError) as exc: raise ValueError("reviewer did not return JSON") from exc
    result["model"]=model or "unknown"; result["tokens"]=tokens
    return result
