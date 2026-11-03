import json,sys,subprocess,hashlib,re,time,concurrent.futures as cf
from pathlib import Path
R=Path(sys.argv[1]); O=Path(sys.argv[2]); BENCH=Path(sys.argv[3])
sys.path.insert(0,str(R)); from research.fact_store import claims as C
PROMPT=(R/'research/fact_store/prompts/claim_extract_v1.md').read_text(encoding='utf8')
PH=hashlib.sha256(PROMPT.encode()).hexdigest()
PRED=sorted(json.loads((R/'research/fact_store/predicates.json').read_text())['predicates'])
SCHEMA=(R/'research/fact_store/claims_extraction.schema.json').read_text(encoding='utf8')
def one(item):
    pkg={'package_id':item['item_id'],'fields':{k:item.get(k) for k in ('title','thumbnail_text','voice_0_3s','escalation_3_10s')},'series_context':item.get('series_context'),'predicates_vocabulary':PRED}
    prompt=PROMPT+'\n\nOUTPUT JSON SCHEMA:\n'+SCHEMA+'\n\nINPUT JSON:\n'+json.dumps(pkg,ensure_ascii=False)
    t0=time.time(); p=subprocess.run(['codex','exec','--skip-git-repo-check','-s','read-only','-'],input=prompt,text=True,capture_output=True,timeout=600)
    log=p.stdout+'\n'+p.stderr; (O/'raw'/(item['item_id']+'.log')).write_text(log,encoding='utf8')
    m=re.search(r'^model:\s*(\S+)',log,re.M); tk=re.search(r'tokens used\s*\n\s*([\d,]+)',log)
    body=log.split('\ncodex\n')[-1]; a,b=body.find('{'),body.rfind('}')
    try: d=json.loads(body[a:b+1])
    except Exception as e: return item['item_id'],{'package_id':item['item_id'],'error':str(e)},time.time()-t0
    d['package_id']=item['item_id']
    d['extractor']={'cli':'codex','model':m.group(1) if m else 'unknown','prompt_sha256':PH,'tokens_total':int(tk.group(1).replace(',','')) if tk else None}
    try: C.validate(d)
    except Exception as e: d['schema_error']=str(e)
    return item['item_id'],d,time.time()-t0
for t in ['tt05_temiya','vsd_fansipan','ck_bybit_2025','f19_hue_phong_thuy','fs_short_ngay_tot_cuoi']:
    items=json.loads((BENCH/'items'/f'{t}.json').read_text())
    items=items if isinstance(items,list) else items.get('items',items)
    with cf.ThreadPoolExecutor(4) as ex: res=list(ex.map(one,items))
    (O/f'{t}.claims.json').write_text(json.dumps({i:d for i,d,_ in res},ensure_ascii=False,indent=1),encoding='utf8')
    print(t,len(res),'items',round(sum(s for *_,s in res)),'s', 'tokens',sum((d.get('extractor',{}).get('tokens_total') or 0) for _,d,_ in res),'errors',sum(1 for _,d,_ in res if 'error' in d or 'schema_error' in d),flush=True)
