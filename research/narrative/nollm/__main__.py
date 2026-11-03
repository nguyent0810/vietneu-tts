import argparse, json
from pathlib import Path
from .generator import generate_directory

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    g=sub.add_parser('gen'); g.add_argument('input'); g.add_argument('--out',required=True); g.add_argument('--history',nargs='?',const='__sequential__')
    a=p.parse_args()
    history={}
    if a.history and a.history!='__sequential__': history=json.loads(Path(a.history).read_text(encoding='utf-8'))
    data=generate_directory(a.input,history)
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    if a.history and a.history!='__sequential__': Path(a.history).write_text(json.dumps(history,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{len(data)} topics -> {out}')
if __name__=='__main__': main()
