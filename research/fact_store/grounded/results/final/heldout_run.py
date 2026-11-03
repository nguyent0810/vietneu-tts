import json,sys,concurrent.futures as cf
from pathlib import Path
R=Path(sys.argv[1]); B=Path(sys.argv[2]); OUT=Path(sys.argv[3]); sys.path.insert(0,str(R))
from research.fact_store.grounded.pipeline import run_package
P=R/'research/fact_store/pilot/stores_fixed'; jobs=[]
for t in ['tt05_temiya','vsd_fansipan','ck_bybit_2025','f19_hue_phong_thuy','fs_short_ngay_tot_cuoi']:
    st=json.loads((P/f'{t}.json').read_text()); ver=json.loads((P/f'{t}.verification.json').read_text())
    for pk in json.loads((B/'items'/f'{t}.json').read_text()): pk.setdefault('topic_id',t); jobs.append((pk,st,ver))
def one(j):
    try: r=run_package(*j,cli='codex')
    except Exception as e: r={'decision':{'verdict':'REVIEW','reasons':[f'pipeline_error: {type(e).__name__}: {e}']}}
    r['package_id']=j[0]['package_id']; return r
with cf.ThreadPoolExecutor(4) as ex: res=list(ex.map(one,jobs))
OUT.write_text(json.dumps(res,ensure_ascii=False,indent=1),encoding='utf8'); print(len(res))
