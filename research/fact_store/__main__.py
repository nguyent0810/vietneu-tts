from __future__ import annotations
import subprocess, argparse, json, sys, hashlib
from collections import Counter
from pathlib import Path
from . import validate_store, compute_verification, _schema_errors, ROOT

def main():
    p=argparse.ArgumentParser(prog="python -m research.fact_store")
    sub=p.add_subparsers(dest="cmd", required=True)
    v=sub.add_parser("validate"); v.add_argument("store")
    q=sub.add_parser("verify"); q.add_argument("store"); q.add_argument("--sources",required=True); q.add_argument("--checks"); q.add_argument("--out",required=True)
    g=sub.add_parser("gate"); g.add_argument("topic"); g.add_argument("--stores",default=str(ROOT/"pilot/stores_fixed")); g.add_argument("--bench",required=True); g.add_argument("--assume-verified",action="store_true")
    ec=sub.add_parser("extract-claims"); ec.add_argument("items"); ec.add_argument("--store",required=True); ec.add_argument("--cli",choices=["codex","claude"],default="codex"); ec.add_argument("--out",required=True); ec.add_argument("--replay")
    ru=sub.add_parser("reuse"); ru.add_argument("--store",required=True); ru.add_argument("--sources",required=True); ru.add_argument("--out",required=True)
    a=p.parse_args()
    try:
        if a.cmd=="extract-claims":
            from .claims import extract_package
            items=json.loads(Path(a.items).read_text(encoding="utf8")); store=json.loads(Path(a.store).read_text(encoding="utf8"))
            items=items if isinstance(items,list) else items.get("items",[items])
            result={}
            for item in items:
                pid=item.get("item_id",item.get("package_id"))
                try: result[pid]=extract_package(item,store,a.cli,a.replay)
                except (ValueError,subprocess.SubprocessError) as e:
                    # Một gói trích hỏng không được làm sập cả lượt: gói đó thành "trích chưa đủ" → gate REVIEW.
                    result[pid]={"package_id":pid,"extractor":{"cli":a.cli},"complete":False,"uncovered_spans":[f"extraction_error: {e}"],"claims":[]}
            Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8"); return 0
        if a.cmd=="reuse":
            from .claims import reuse
            s=json.loads(Path(a.store).read_text(encoding="utf8")); result=reuse(s,a.sources)
            Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8"); return 0
        if a.cmd=="gate":
            store=None; errs=[]
        else:
            store=json.loads(Path(a.store).read_text(encoding="utf-8"))
            errs=validate_store(store)
        if a.cmd=="validate":
            print(f"facts={len(store.get('facts',[]))} errors={len(errs)}")
            for e in errs: print("ERROR:",e)
            return 1 if errs else 0
        if a.cmd=="gate":
            from .gate import gate
            from .nollm import generate
            store_path=Path(a.stores)/f"{a.topic}.json"
            ver_path=Path(a.stores)/f"{a.topic}.verification.json"
            store=json.loads(store_path.read_text(encoding="utf8")); verification=json.loads(ver_path.read_text(encoding="utf8"))
            if a.assume_verified:
                print("\n*** CẢNH BÁO: --assume-verified CHỈ DÙNG THỬ NGHIỆM; đây không phải xác minh thực tế. ***\n")
                for r in verification.get("results",[]):
                    if any(c.get("method")=="span_match" and c.get("result")=="supports" for c in r.get("checks",[])):
                        r["status"]="verified"; r["certainty"]="uncertain" if r.get("certainty")=="unknown" else r["certainty"]
            bench=json.loads((Path(a.bench)/f"{a.topic}.json").read_text(encoding="utf8"))
            print("level             verdict   PASS REVIEW REJECT")
            for level in ("safe","max_defensible","invalid"):
                data=bench.get("levels",{}).get(level,{})
                fields={k:data[k] for k in ("title","thumbnail_text","voice_0_3s") if isinstance(data.get(k),str)}
                result=gate(fields,store,verification); counts={v:sum(c["verdict"]==v for c in result["claims"]) for v in ("PASS","REVIEW","REJECT")}
                print(f"{level:18} {result['verdict']:8} {counts['PASS']:4} {counts['REVIEW']:6} {counts['REJECT']:6}")
            gen=generate(store,verification,[])
            print(f"NO_LLM candidates={len(gen['candidates'])} abstain={len(gen['abstain'])}")
            return 0
        if errs:
            for e in errs: print("ERROR:",e)
            return 1
        checks=json.loads(Path(a.checks).read_text(encoding="utf-8")) if a.checks else []
        result=compute_verification(store,checks,a.sources)
        result["store_sha256"]=hashlib.sha256(Path(a.store).read_bytes()).hexdigest()
        verrs=_schema_errors(result,ROOT/"verification.schema.json")
        if verrs:
            for e in verrs: print("ERROR:",e)
            return 1
        Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        statuses=Counter(x["status"] for x in result["results"]); certainty=Counter(x["certainty"] for x in result["results"])
        print(f"facts={len(result['results'])} status={dict(statuses)} certainty={dict(certainty)} errors=0")
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as e:
        print(f"ERROR: {e}",file=sys.stderr); return 1
if __name__=="__main__": raise SystemExit(main())
