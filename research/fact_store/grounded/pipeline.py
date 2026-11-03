"""Decision policy and CLI for the research-only grounded packaging gate."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from .check import det_check
from .review import relevant_facts, semantic_review

def _n(t):
    import unicodedata,re
    return re.sub(r"\s+"," ",unicodedata.normalize("NFC",str(t or "")).casefold()).strip(" .,:;!?\"'")

# Lỗi tất định chỉ được gỡ bởi review ngữ nghĩa khi là lỗi về KHUNG (quy kết/modality), không phải số/ngày/tên.
SEMANTIC_RESOLVABLE={"dropped_qualifier","unattributed_disputed"}

def _verdict_for(field, span, rows):
    """Câu reviewer chấm có thể dài hơn đoạn cần xét: khớp theo cùng trường và chứa nhau (sau chuẩn hoá)."""
    span_n=_n(span); hits=[x.get("verdict") for x in rows if x.get("field")==field and (span_n in _n(x.get("span")) or _n(x.get("span")) in span_n)]
    if not hits: return None
    for v in ("contradicted","unsupported","needs_review"):
        if v in hits: return v
    return "supported"

def decide(det, review=None):
    if any(i.get("code")=="contradiction" for i in det.get("issues",[])):
        return {"verdict":"REJECT","reasons":["deterministic contradiction"]}
    rows=(review or {}).get("sentences",[])
    if any(x.get("verdict")=="contradicted" for x in rows): return {"verdict":"REJECT","reasons":["semantic reviewer found contradiction"]}
    if det.get("needs_semantic") and not review: return {"verdict":"REVIEW","reasons":["semantic review required"]}
    missing=[x for x in det.get("needs_semantic",[]) if _verdict_for(x.get("field"),x.get("span"),rows)!="supported"]
    open_issues=[]
    for i in det.get("issues",[]):
        if i.get("severity")!="review": continue
        if i.get("code") in SEMANTIC_RESOLVABLE and i.get("field") and _verdict_for(i.get("field"),i.get("span",""),rows)=="supported": continue
        if i.get("code") in SEMANTIC_RESOLVABLE and not i.get("field") and rows and all(x.get("verdict")=="supported" for x in rows): continue
        open_issues.append(i)
    if missing or open_issues:
        reasons=[]
        if missing: reasons.append("semantic review: %d câu chưa được xác nhận supported" % len(missing))
        reasons.extend(i.get("code","deterministic review issue") for i in open_issues)
        return {"verdict":"REVIEW","reasons":reasons}
    return {"verdict":"APPROVED","reasons":[]}

def _load(path): return json.loads(Path(path).read_text(encoding="utf-8"))

def run_package(package, store, verification, cli="codex", replay=None, explain=False):
    det=det_check(package,store,verification,explain=explain); review=None
    if det["needs_semantic"] or det["issues"]:
        subset=relevant_facts(package,store,verification)
        review=semantic_review(package,subset,cli=cli,replay=replay)
    return {"deterministic":det,"review":review,"decision":decide(det,review)}

def main(argv=None):
    p=argparse.ArgumentParser(prog="python -m research.fact_store.grounded")
    sub=p.add_subparsers(dest="command",required=True)
    run=sub.add_parser("run"); run.add_argument("package"); run.add_argument("--store",required=True); run.add_argument("--verification",required=True); run.add_argument("--cli",default="codex"); run.add_argument("--replay"); run.add_argument("--out",required=True); run.add_argument("--explain",action="store_true")
    adv=sub.add_parser("eval-adversarial"); adv.add_argument("items_dir"); adv.add_argument("--stores",required=True); adv.add_argument("--out",required=True); adv.add_argument("--cli",default="codex"); adv.add_argument("--replay-dir"); adv.add_argument("--workers",type=int,default=1); adv.add_argument("--explain",action="store_true")
    args=p.parse_args(argv)
    if args.command=="run":
        package=_load(args.package); store=_load(args.store); verification=_load(args.verification)
        result={"package":run_package(package,store,verification,args.cli,args.replay,args.explain)}
        for i,alt in enumerate(package.get("alternates",[])):
            result.setdefault("alternates",[]).append(run_package(alt,store,verification,args.cli,args.replay,args.explain))
    else:
        items=Path(args.items_dir); stores=Path(args.stores); result={"items":[]}
        for path in sorted(items.glob("*.json")):
            loaded=_load(path)
            entries=loaded if isinstance(loaded,list) else [loaded]
            for index,entry in enumerate(entries):
             package=entry; topic=package.get("topic_id",path.stem)
             label=path.name if not isinstance(loaded,list) else f"{path.name}[{index}]"
             sp=stores/(topic+".json"); vp=stores/(topic+".verification.json")
             if not vp.exists(): vp=sp.with_name(sp.stem+".verification.json")
             if not sp.exists() or not vp.exists(): result["items"].append({"item":label,"decision":{"verdict":"REVIEW","reasons":["matching store or verification missing"]}}); continue
             replay=Path(args.replay_dir)/(path.stem+".json") if args.replay_dir else None
             result["items"].append({"item":label,**run_package(package,_load(sp),_load(vp),args.cli,str(replay) if replay and replay.exists() else None,args.explain)})
        result["false_acceptance_count"]=sum(x.get("decision",{}).get("verdict")=="APPROVED" for x in result["items"])
    Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__": main()
