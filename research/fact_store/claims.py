"""LLM-backed packaging claim extraction and incremental fact reuse helpers."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
from . import ROOT

SCHEMA=ROOT/'claims_extraction.schema.json'
PROMPT=ROOT/'prompts/claim_extract_v2.md'

def validate(value):
    try:
        import jsonschema
        errs=list(jsonschema.Draft202012Validator(json.loads(SCHEMA.read_text())).iter_errors(value))
        if errs: raise ValueError('; '.join(e.message for e in errs))
    except ImportError:
        if not isinstance(value,dict) or not {'package_id','extractor','complete','uncovered_spans','claims'}<=value.keys(): raise ValueError('invalid extraction structure')
    return value

def extract(items, cli='codex', replay=None):
    if replay:
        raw=Path(replay).read_text(encoding='utf8')
    else:
        prompt=PROMPT.read_text(encoding='utf8')+'\n\nINPUT JSON:\n'+json.dumps(items,ensure_ascii=False)
        if cli=='codex': cmd=['codex','exec','-s','read-only','-']
        elif cli=='claude': cmd=['claude','-p']
        else: raise ValueError('cli must be codex or claude')
        proc=subprocess.run(cmd,input=prompt,text=True,capture_output=True,check=True)
        log=proc.stdout+'\n'+proc.stderr
        import re
        model=re.search(r'^model:\s*(\S+)',log,re.M)
        tokens=re.search(r'tokens used\s*\n\s*([\d,]+)',log)
        raw=log.split('\ncodex\n')[-1] if cli=='codex' else proc.stdout
    try: data=json.loads(raw)
    except json.JSONDecodeError:
        a,b=raw.find('{'),raw.rfind('}')
        if a<0 or b<a: raise ValueError('CLI output did not contain JSON')
        data=json.loads(raw[a:b+1])
    ext=data.setdefault('extractor',{})
    ext.update(cli=cli,prompt_sha256=hashlib.sha256(PROMPT.read_bytes()).hexdigest())
    if not replay:
        ext['model']=model.group(1) if model else 'unknown'
        ext['tokens_total']=int(tokens.group(1).replace(',','')) if tokens else None
    return validate(data)

def extract_package(item, store, cli='codex', replay=None):
    predicates=sorted(json.loads((ROOT/'predicates.json').read_text(encoding='utf8'))['predicates'])
    pkg={'package_id':item.get('item_id',item.get('package_id')),
         'fields':{k:item.get(k) for k in ('title','thumbnail_text','voice_0_3s','escalation_3_10s')},
         'series_context':item.get('series_context'),'predicates_vocabulary':predicates,
         'entities':[{'id':e['entity_id'],'name':e.get('name'),'aliases':e.get('aliases',[])} for e in store.get('entities',[])],
         'measures_vocabulary':sorted({(f.get('quantity') or {}).get('measure') for f in store.get('facts',[]) if (f.get('quantity') or {}).get('measure')})}
    result=extract(pkg,cli,replay)
    result['package_id']=pkg['package_id']
    return result

def reuse(store, sources):
    src=Path(sources)
    verpath=src.with_name(src.stem+'.verification.json')
    verification=json.loads(verpath.read_text(encoding='utf8')) if verpath.exists() else {'results':[]}
    statuses={x.get('fact_id'):x for x in verification.get('results',[])}
    facts=[f for f in store.get('facts',[]) if statuses.get(f.get('fact_id'),{}).get('status')=='verified']
    known={(f.get('subject'),f.get('predicate')) for f in facts}
    fresh=[]
    for p in sorted(Path(sources).glob('*')):
        if p.is_file(): fresh.append({'source':p.name,'covered':False})
    total=len(store.get('facts',[])); ratio=(len(facts)/total) if total else 0
    old_tokens=sum(int(f.get('extraction',{}).get('tokens_in',0)) for f in store.get('facts',[]))
    return {'reusable_facts':[f['fact_id'] for f in facts if f.get('fact_id')], 'new_sources':fresh,'reused_fact_count':len(facts),'uncovered_entity_predicates':sorted({(f.get('subject'),f.get('predicate')) for f in store.get('facts',[])}-known),'estimated_tokens_saved':round(old_tokens*ratio)}

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument('items'); p.add_argument('--cli',choices=['codex','claude'],default='codex'); p.add_argument('--out',required=True); p.add_argument('--replay'); a=p.parse_args(argv)
    items=json.loads(Path(a.items).read_text(encoding='utf8')); result=extract(items,a.cli,a.replay)
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return 0
if __name__=='__main__': raise SystemExit(main())
