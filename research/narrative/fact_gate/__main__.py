import argparse, json
from pathlib import Path
from collections import defaultdict
from .core import gate

def main():
    p=argparse.ArgumentParser(prog="python -m research.narrative.fact_gate")
    sub=p.add_subparsers(dest="command",required=True)
    e=sub.add_parser("eval"); e.add_argument("topics",type=Path); e.add_argument("--key",type=Path); e.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.key:
        # Supported for compatibility; benchmark levels are already explicitly named.
        json.loads(a.key.read_text(encoding="utf-8"))
    details={}; counts=defaultdict(lambda:defaultdict(int))
    for path in sorted(a.topics.glob("*.json")):
        topic=json.loads(path.read_text(encoding="utf-8")); slug=topic.get("slug",path.stem); details[slug]={}
        for name,level in topic.get("levels",{}).items():
            result=gate({**level,"name":name},topic); details[slug][name]=result; counts[name][result["verdict"]]+=1
    print("level             PASS  REVIEW  REJECT")
    for name in ("safe","max_defensible","invalid"):
        c=counts[name]; print(f"{name:17} {c['PASS']:>4}  {c['REVIEW']:>6}  {c['REJECT']:>6}")
    output=json.dumps(details,ensure_ascii=False,indent=2)
    if a.out: a.out.write_text(output+"\n",encoding="utf-8")
    else: print(output)

if __name__=="__main__": main()
