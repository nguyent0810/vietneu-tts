"""Decision policy and CLI for the research-only grounded packaging gate."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from .check import det_check
from .review import relevant_facts,semantic_review

SEMANTIC_RESOLVABLE={"dropped_qualifier","unattributed_disputed"}
VALID={"supported","needs_review","unsupported","contradicted"}

def decide(det,review=None):
    issues=det.get("issues",[]); rows=(review or {}).get("sentences",[])
    if any(i.get("code")=="contradiction" for i in issues): return {"verdict":"REJECT","reasons":["deterministic contradiction"]}
    needs=det.get("needs_semantic",[]); required={x.get("span_id") for x in needs if x.get("span_id")}
    # All known spans define the reviewer contract, including non-semantic spans.
    omitted=set(det.get("evidence_missing",[]))
    spans=det.get("spans",[]); expected={s.get("span_id") for s in spans if s.get("span_id") and s.get("span_id") not in omitted}
    ids=[]; bad=False
    for row in rows:
        sid=row.get("span_id") if isinstance(row,dict) else None
        if not sid or sid not in expected or sid in ids or row.get("verdict") not in VALID or not row.get("reason") or not isinstance(row.get("fact_ids"),list): bad=True
        if sid: ids.append(sid)
        if row.get("verdict")=="contradicted": return {"verdict":"REJECT","reasons":["semantic contradiction for span_id %s"%sid]}
    byid={r.get("span_id"):r for r in rows if isinstance(r,dict) and r.get("span_id")}
    if review is not None and (bad or set(ids)!=expected): return {"verdict":"REVIEW","reasons":["review rows have unknown, duplicate, missing, or malformed span_id"]}
    for i in issues:
        if i.get("severity")=="reject": return {"verdict":"REJECT","reasons":[i.get("code","deterministic reject")]}
        if i.get("severity")!="review": continue
        sid=i.get("span_id")
        if not sid or sid not in expected: return {"verdict":"REVIEW","reasons":["deterministic issue has no valid span_id",i.get("code","issue")]}
        if i.get("code") in SEMANTIC_RESOLVABLE and byid.get(sid,{}).get("verdict")=="supported": continue
        return {"verdict":"REVIEW","reasons":[i.get("code","deterministic review issue")]}
    if required and review is None: return {"verdict":"REVIEW","reasons":["semantic review required"]}
    unsupported=[sid for sid in required if byid.get(sid,{}).get("verdict")!="supported"]
    if unsupported: return {"verdict":"REVIEW","reasons":["needs_semantic spans not supported: "+", ".join(sorted(unsupported))]}
    return {"verdict":"APPROVED","reasons":[]}

def _load(path): return json.loads(Path(path).read_text(encoding="utf-8"))

def run_package(package,store,verification,cli="codex",replay=None,explain=False):
    det=det_check(package,store,verification,explain=explain); review=None; facts_by_span,missing=relevant_facts(package,store,verification,det["spans"])
    det["evidence_missing"]=missing
    for sid in missing:
        sp=next(x for x in det["spans"] if x["span_id"]==sid)
        det["needs_semantic"].append({**sp,"reason":"evidence_missing"})
    review_spans=[s for s in det["spans"] if s["span_id"] not in missing]
    if review_spans and (det["needs_semantic"] or det["issues"]):
        review=semantic_review(package,{s["span_id"]:facts_by_span[s["span_id"]] for s in review_spans},review_spans,cli=cli,replay=replay)
    return {"deterministic":det,"review":review,"retrieved_fact_count":len({f.get("fact_id") for rows in facts_by_span.values() for f in rows}),"decision":decide(det,review)}

def main(argv=None):
    p=argparse.ArgumentParser(prog="python -m research.fact_store.grounded"); sub=p.add_subparsers(dest="command",required=True)
    run=sub.add_parser("run"); run.add_argument("package"); run.add_argument("--store",required=True); run.add_argument("--verification",required=True); run.add_argument("--cli",default="codex"); run.add_argument("--replay"); run.add_argument("--out",required=True); run.add_argument("--explain",action="store_true")
    adv=sub.add_parser("eval-adversarial"); adv.add_argument("items_dir"); adv.add_argument("--stores",required=True); adv.add_argument("--out",required=True); adv.add_argument("--cli",default="codex"); adv.add_argument("--replay-dir"); adv.add_argument("--workers",type=int,default=1); adv.add_argument("--explain",action="store_true")
    a=p.parse_args(argv)
    if a.command=="run":
        pkg=_load(a.package); store=_load(a.store); ver=_load(a.verification); result={"package":run_package(pkg,store,ver,a.cli,a.replay,a.explain)}
        for alt in pkg.get("alternates",[]): result.setdefault("alternates",[]).append(run_package(alt,store,ver,a.cli,a.replay,a.explain))
    else:
        items=Path(a.items_dir); stores=Path(a.stores); result={"items":[]}
        for path in sorted(items.glob("*.json")):
            loaded=_load(path); entries=loaded if isinstance(loaded,list) else [loaded]
            for index,entry in enumerate(entries):
                topic=entry.get("topic_id") or path.stem; label=path.name if not isinstance(loaded,list) else f"{path.name}[{index}]"
                sp=stores/(topic+".json"); vp=stores/(topic+".verification.json")
                if not vp.exists(): vp=sp.with_name(sp.stem+".verification.json")
                if not sp.exists() or not vp.exists(): result["items"].append({"item":label,"topic_id":topic,"decision":{"verdict":"REVIEW","reasons":["matching store or verification missing"]}}); continue
                replay=Path(a.replay_dir)/(path.stem+".json") if a.replay_dir else None
                result["items"].append({"item":label,"topic_id":topic,**run_package(entry,_load(sp),_load(vp),a.cli,str(replay) if replay and replay.exists() else None,a.explain)})
        result["false_acceptance_count"]=sum(x.get("decision",{}).get("verdict")=="APPROVED" for x in result["items"])
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__": main()
