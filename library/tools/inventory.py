#!/usr/bin/env python3
"""Deterministic inventory of video editing techniques; stdlib only."""
from __future__ import annotations
import argparse, csv, hashlib, html, json, re, ssl, unicodedata, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
from functools import lru_cache
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
INV = ROOT / 'library' / 'inventory'
CACHE = ROOT / 'chunks_cache' / 'library_src'
REPORT = ROOT / 'output/cl_staging/grok/reports/37_inventory.md'
V2_REPORT = ROOT / 'output/cl_staging/grok/reports/37_inventory_v2.md'
V3_REPORT = ROOT / 'output/cl_staging/grok/reports/37_inventory_v3.md'
USAGE_ROOT = ROOT
SOURCES = {
 'athemeroy': ['https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/data/cases.csv','https://raw.githubusercontent.com/athemeroy/awesome-opus-5-5-videos/main/data/domain-style.csv'],
 'yihui-dev': ['https://raw.githubusercontent.com/yihui-dev/awesome-opus5-5-videos/main/data/videos.json','https://api.github.com/repos/yihui-dev/awesome-opus5-5-videos/contents/prompts'],
 'LeaddeOpenLab': ['https://api.github.com/repos/LeaddeOpenLab/awesome-opus-5-5-video-prompts/contents/prompts','https://api.github.com/repos/LeaddeOpenLab/awesome-opus-5-5-video-prompts/contents'],
}

def norm(s):
    s=unicodedata.normalize('NFC', str(s or '')).lower()
    return re.sub(r'\s+', ' ', re.sub(r'[^\w]+', ' ', s, flags=re.UNICODE)).strip()
def canon_url(url):
    if not url: return ''
    p=urlsplit(str(url).strip())
    host=p.netloc.lower().removeprefix('www.')
    path=re.sub(r'/+$','',p.path)
    if host in ('x.com','twitter.com','mobile.twitter.com'):
        m=re.search(r'/status/(\d+)',path)
        if m: return 'https://x.com/i/status/'+m.group(1)
    return urlunsplit(('https',host,path,'',''))
def post_id(url, obj=None):
    for k in ('post_id','tweet_id','status_id','id'):
        v=(obj or {}).get(k)
        if v and re.fullmatch(r'\d{8,}',str(v)): return str(v)
    m=re.search(r'/status/(\d+)',str(url or ''))
    return m.group(1) if m else ''
def record(source, source_id, title='', text='', url='', labels=None, tools=None, fmt='unknown', built=False, post_id_value=''):
    srcid=str(source_id or title or hashlib.sha1((title+text).encode()).hexdigest()[:12])
    pid=str(post_id_value or post_id(url) or (srcid if re.fullmatch(r'\d{15,}',srcid) else ''))
    return {'uid':source+':'+srcid,'source':source,'source_id':srcid,'url':url or '', 'post_id':pid, 'title':str(title or '').strip(), 'text':str(text or '').strip(), 'labels':labels or [], 'tools':sorted(set(tools or [])), 'format':fmt if fmt in ('short','long','unknown') else 'unknown','engine_asset':bool(built)}

def fetch_one(name, url, offline):
    d=CACHE/name; d.mkdir(parents=True,exist_ok=True)
    stem=re.sub(r'[^a-zA-Z0-9._-]','_',urlsplit(url).path.rsplit('/',1)[-1] or 'index')
    if url.rstrip('/').endswith('/prompts'): stem='prompts_index.json'
    dest=d/stem; meta=d/(stem+'.meta.json')
    if offline: return dest if dest.exists() else None
    req=urllib.request.Request(url,headers={'User-Agent':'library-inventory/1.0','Accept':'application/vnd.github+json'})
    old=json.loads(meta.read_text()) if meta.exists() else {}
    if old.get('etag'): req.add_header('If-None-Match',old['etag'])
    try:
        with urllib.request.urlopen(req,timeout=18,context=ssl_context()) as r:
            data=r.read(); dest.write_bytes(data)
            meta.write_text(json.dumps({'url':url,'downloaded_at':datetime.now(timezone.utc).isoformat(),'etag':r.headers.get('ETag'),'last_modified':r.headers.get('Last-Modified')},ensure_ascii=False,indent=2))
        return dest
    except urllib.error.HTTPError as e:
        if e.code==304 and dest.exists(): return dest
        raise
def fetch(offline=False):
    errors=[]
    for name,urls in SOURCES.items():
        for url in urls:
            try:
                p=fetch_one(name,url,offline)
                if p is None: errors.append(f'{name}: cache miss {url}')
            except Exception as e: errors.append(f'{name}: {url}: {type(e).__name__}: {e}')
    if not offline:
        # Materialize prompt markdowns during fetch; build never needs network.
        tasks=[]
        for name in ('yihui-dev','LeaddeOpenLab'):
            for idx in sorted((CACHE/name).glob('*index.json')):
                data=load_json(idx)
                if not isinstance(data,list): continue
                for item in data:
                    if not isinstance(item,dict) or item.get('type')!='file' or not item.get('download_url','').endswith('.md'): continue
                    dest=idx.parent/re.sub(r'[^\w.-]','_',item.get('name','prompt.md'))
                    meta=dest.parent/(dest.name+'.meta.json')
                    refresh=True
                    if dest.exists() and meta.exists():
                        try:
                            downloaded=datetime.fromisoformat(json.loads(meta.read_text())['downloaded_at'])
                            refresh=(datetime.now(timezone.utc)-downloaded).total_seconds()>=86400
                        except Exception: refresh=True
                    if refresh: tasks.append((name,item,dest))
        def download_prompt(task):
            name,item,dest=task; u=item['download_url']
            meta=dest.parent/(dest.name+'.meta.json')
            old=json.loads(meta.read_text()) if meta.exists() else {}
            headers={'User-Agent':'library-inventory/1.0'}
            if old.get('etag'): headers['If-None-Match']=old['etag']
            req=urllib.request.Request(u,headers=headers)
            try:
                with urllib.request.urlopen(req,timeout=25,context=ssl_context()) as r:
                    dest.write_bytes(r.read())
                    meta.write_text(json.dumps({'url':u,'downloaded_at':datetime.now(timezone.utc).isoformat(),'etag':r.headers.get('ETag')},ensure_ascii=False,indent=2))
            except urllib.error.HTTPError as e:
                if e.code!=304 or not dest.exists(): raise
            return None
        with ThreadPoolExecutor(max_workers=12) as pool:
            futures={pool.submit(download_prompt,t):t for t in tasks}
            for f in as_completed(futures):
                try: f.result()
                except Exception as e:
                    name,item,_=futures[f]; errors.append(f'{name}: prompt {item.get("name")}: {type(e).__name__}: {e}')
    # Also cache prompt-motion catalog, a local source, for an auditable snapshot.
    return errors

def ssl_context():
    """Use the platform CA bundle when this Python build lacks a configured bundle."""
    paths=ssl.get_default_verify_paths()
    if paths.cafile and Path(paths.cafile).is_file(): return ssl.create_default_context()
    for ca in ('/etc/ssl/cert.pem','/etc/ssl/certs/ca-certificates.crt','/opt/homebrew/etc/openssl@3/cert.pem'):
        if Path(ca).is_file(): return ssl.create_default_context(cafile=ca)
    return ssl.create_default_context()

def load_json(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return None
def labels_from(obj):
    out=[]
    for k in ('style','style2','domain','tags','tag','tech_tags','topic','category','type','format','primary_path','label','group','ky_thuat','tool'):
        v=obj.get(k)
        if isinstance(v,list): out += [str(x) for x in v]
        elif v: out.append(str(v))
    return sorted(set(out))
def tools_from(text):
    terms=('remotion','manim','threejs','three.js','p5.js','canvas','gsap','webgl','svg','css','lottie','ffmpeg','blender')
    low=text.lower(); return [t.replace('.js','').replace('three.js','threejs') for t in terms if re.search(r'(?<!\w)'+re.escape(t)+r'(?!\w)',low)]
def format_from(text, obj=None):
    s=(text+' '+str((obj or {}).get('format',''))).lower()
    if re.search(r'\b(short|shorts|reel|tiktok|9:16)\b',s): return 'short'
    if re.search(r'\b(long|longform|documentary|16:9)\b',s): return 'long'
    return 'unknown'
def walk_objects(obj):
    if isinstance(obj,list):
        for x in obj: yield from walk_objects(x)
    elif isinstance(obj,dict):
        if any(k in obj for k in ('title','prompt','description','url','post_id','tweet_id')): yield obj
        for k,v in obj.items():
            if isinstance(v,(dict,list)): yield from walk_objects(v)
def adapt_opus(name, path):
    out=[]
    if path.suffix.lower()=='.csv':
        try:
            with path.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
        except Exception: return out
        for i,o in enumerate(rows):
            title=next((o[k] for k in o if k.lower() in ('title','name','case','video','project')), '')
            if name == 'athemeroy':
                text=' '.join(str(o.get(k,'')) for k in (('topic_en',) if 'topic_en' in o else ('creator_disclosure','hypit_observation','review_note','label')) if o.get(k))
            else: text=' '.join(str(v) for k,v in o.items() if v and k.lower() not in ('url','link'))
            url=next((v for k,v in o.items() if v and ('url' in k.lower() or 'link' in k.lower())), '')
            out.append(record(name, o.get('id') or o.get('slug') or post_id(url,o) or i, title,text,url,labels_from(o),tools_from(text),format_from(text,o),post_id_value=post_id(url,o)))
    elif path.suffix.lower()=='.json':
        data=load_json(path)
        if data is not None:
            for i,o in enumerate(walk_objects(data)):
                title=o.get('title') or o.get('name') or ''
                text=' '.join(str(o.get(k,'')) for k in ('prompt','description','text','content','style','domain','tech_tags'))
                url=o.get('url') or o.get('link') or o.get('post_url') or o.get('tweet_url') or o.get('source_url') or ''
                out.append(record(name,o.get('id') or o.get('slug') or o.get('post_id') or post_id(url,o) or i,title,text,url,labels_from(o),tools_from(text),format_from(text,o),post_id_value=post_id(url,o)))
    elif path.suffix.lower()=='.md':
        t=path.read_text(encoding='utf-8',errors='replace')
        title=next((x.lstrip('# ').strip() for x in t.splitlines() if x.strip()),path.stem)
        native=[]
        fm=re.match(r'\A---\s*\n(.*?)\n---\s*\n',t,re.S)
        if fm:
            for line in fm.group(1).splitlines():
                m=re.match(r'\s*(category|group|tags?|tool|ky_thuat)\s*:\s*(.+)',line,re.I)
                if m: native.extend(re.findall(r'[\wÀ-ỹ-]+',m.group(2)))
        cat=re.search(r'^\s*-\s*\*\*Category:\*\*\s*([^\n]+)',t,re.I|re.M)
        if cat: native.append(cat.group(1).strip())
        remake=re.search(r'^\s*-\s*\*\*Remake built with:\*\*\s*([^\n]+)',t,re.I|re.M)
        if remake: native.extend(x.strip(' `*') for x in re.split(r'[,;·]',remake.group(1)) if x.strip(' `*'))
        fragment=re.search(r'\*\*([^*]{2,50})\*\*\s*[·|—-]',t)
        if fragment: native.append(fragment.group(1).strip())
        for label in re.findall(r'^\s*[-*]\s*\*\*(?:Tools?|Công cụ|Kỹ thuật)\*\*\s*:\s*([^\n]+)',t,re.I|re.M):
            native.extend(x.strip(' `*') for x in re.split(r'[,;]',label) if x.strip(' `*'))
        url_match=re.search(r'https?://(?:www\.)?(?:x\.com|twitter\.com)/[^\s)>]*?/status/\d+',t)
        url=url_match.group(0).rstrip('.,;)') if url_match else ''
        out.append(record(name,path.stem,title,t,url,sorted(set(native)),tools_from(t),format_from(t),post_id_value=post_id(url) or (path.stem if re.fullmatch(r'\d{15,}',path.stem) else '')))
    return out

def extract_a():
    out=[]; a='engine'
    comp=ROOT/'hyperframes_short/compositions'
    for p in sorted(comp.glob('*.html')):
        if p.name.startswith('_'): continue
        out.append(record(a,'composition:'+p.stem,p.stem,p.read_text(errors='ignore'),p.as_uri(),['composition','style'],tools_from(p.read_text(errors='ignore')),'unknown',True))
    for p in sorted((comp/'components').glob('*.html')):
        out.append(record(a,'component:'+p.stem,p.stem,p.read_text(errors='ignore'),p.as_uri(),['component','template'],tools_from(p.read_text(errors='ignore')),'unknown',True))
    for p in sorted((ROOT/'hyperframes_short/studio/devices').glob('*.js')):
        out.append(record(a,'device:'+p.stem,p.stem,p.read_text(errors='ignore'),p.as_uri(),['device','studio'],tools_from(p.read_text(errors='ignore')),'unknown',True))
    for p in sorted((ROOT/'hyperframes_short/studio/themes').glob('*.json')):
        out.append(record(a,'theme:'+p.stem,p.stem,p.read_text(errors='ignore'),p.as_uri(),['theme','style'],[],'unknown',True))
    bridge=(ROOT/'hyperframes_bridge.py').read_text(errors='ignore'); m=re.search(r'STYLES\s*=\s*\{(.*?)\n\}',bridge,re.S)
    if m:
        for style,file in re.findall(r'"([\w-]+)"\s*:\s*\{"file":\s*"([^"]+)"',m.group(1)):
            out.append(record(a,'style:'+style,style,file,'', ['style'],[],'unknown',True))
    for rel in ('.claude/skills/motion-library/SKILL.md','hyperframes_short/compositions/longform.js'):
        p=ROOT/rel; txt=p.read_text(errors='ignore')
        # Extract names of declared scene types, variants and layouts; preserve source text for matching.
        names=set(re.findall(r'`(?:type\s*=\s*)?([a-z][a-z0-9_-]{2,})`',txt))
        names.update(re.findall(r'\b(?:VISUAL_TYPES|MEDIA_LAYOUTS|LAYOUT_POOL)\s*=\s*\(([^)]*)\)',txt,re.S) for _ in [])
        out.append(record(a,'skill:'+rel,p.stem,txt,p.as_uri(),['scene','layout'],tools_from(txt),'unknown',True))
        if rel.endswith('longform.js'):
            lm=re.search(r'const layouts\s*=\s*\{(.*?)\n\s*\};',txt,re.S)
            if lm:
                for name in sorted(set(re.findall(r'^\s{4}([a-z][\w-]*):\s*\{',lm.group(1),re.M))):
                    out.append(record(a,'layout:'+name,name,'layout '+name,p.as_uri(),['layout','built'],[], 'unknown',True))
            vm=re.search(r'const visuals\s*=\s*\{(.*?)(?=\n\s*\};)',txt,re.S)
            names=set(re.findall(r'^\s{4}([a-z][\w-]*):\s*\{',vm.group(1),re.M)) if vm else set()
            names.update(re.findall(r'visuals\.([a-z][\w-]*)\s*=\s*\{',txt))
            for name in sorted(names):
                out.append(record(a,'scene:'+name,name,'visual scene '+name,p.as_uri(),['scene','built'],[], 'unknown',True))
        else:
            # `type` rows are the supported visual scene catalog in the skill.
            for name in sorted(set(re.findall(r'^\|\s*`([a-z][\w-]*)`\s*\|',txt,re.M))):
                out.append(record(a,'scene-doc:'+name,name,'visual scene '+name,p.as_uri(),['scene','built'],[], 'unknown',True))
    # Skill files and references contribute technique names only; ignored long-script writing/research references.
    base=ROOT/'.claude/skills'
    for p in sorted(base.glob('*/SKILL.md'))+sorted(base.glob('*/references/*')):
        if not p.is_file() or p.suffix not in ('.md','.txt'): continue
        txt=p.read_text(errors='ignore')
        names=set(re.findall(r'`([^`\n]{2,100})`',txt))
        names.update(x.strip('# ').strip() for x in re.findall(r'^#{1,4}\s+(.+)$',txt,re.M))
        names.update(re.findall(r'^\|\s*`?([a-z][\w -]{1,60})`?\s*\|',txt,re.M))
        name_text='; '.join(sorted(names,key=lambda x:(x.casefold(),x)))
        out.append(record(a,'skill:'+p.relative_to(ROOT).as_posix(),p.stem,name_text,p.as_uri(),['skill','technique'],tools_from(name_text),'unknown',True))
    catalog=ROOT/'.claude/skills/motion-library/references/prompt_motion/catalog.json'
    data=load_json(catalog)
    if data is not None:
        for i,o in enumerate(walk_objects(data)):
            title=o.get('title') or o.get('name') or o.get('id') or f'prompt motion {i}'
            text=' '.join(str(o.get(k,'')) for k in ('description','prompt','tags','category'))
            out.append(record('prompt-motion','catalog:'+str(o.get('id',i)),title,text,o.get('url',''),labels_from(o),tools_from(text),'unknown',False))
    ref=ROOT/'.ref_opus55_styles.md'
    if ref.exists():
        txt=ref.read_text(encoding='utf-8',errors='ignore')
        matches=list(re.finditer(r'^#{1,4}\s+(.+)$',txt,re.M))
        if matches:
            for i,m in enumerate(matches):
                title=m.group(1).strip(); chunk=txt[m.end():matches[i+1].start() if i+1<len(matches) else len(txt)]
                out.append(record('lead-reference',f'heading:{i}:{norm(title)[:70]}',title,chunk,'',[],tools_from(title+' '+chunk),'unknown',False))
        else: out.append(record('lead-reference','styles',ref.stem,txt,'',[],tools_from(txt),'unknown',False))
    return out

def adapt_b_c():
    out=[]
    for name in SOURCES:
        for p in sorted((CACHE/name).glob('*')):
            if p.name.endswith('.meta.json') or not p.is_file(): continue
            if p.name.endswith('index.json') or p.name=='contents.json': continue
            if p.suffix in ('.csv','.json','.md'): out.extend(adapt_opus(name,p))
    return out

def load_taxonomy(): return json.loads((INV/'taxonomy.json').read_text(encoding='utf-8'))
def load_map(name):
    p=INV/name
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
def native_label_report(records):
    counts=defaultdict(Counter)
    for r in records:
        for label in r.get('labels',[]): counts[r['source']][str(label).strip()] += 1
    data={s:[{'label':k,'count':n} for k,n in sorted(c.items(),key=lambda x:(-x[1],x[0].casefold()))] for s,c in sorted(counts.items())}
    (INV/'native_labels.json').write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return data
def tag_records(records,tax):
    label_map=load_map('label_map.json')
    for r in records:
        blob=norm(' '.join([r['title'],r['text'],*r['labels']]))
        tags=[]
        for t in tax:
            for k in t['keywords']:
                nk=norm(k)
                if not nk: continue
                if t['id']=='canvas_drawing' and nk in ('canvas','html canvas'): continue
                if nk in blob:
                    if t['id']=='canvas_drawing' and nk in ('canvas drawing','canvas animation') and not re.search(r'\b(draw|drawing|brush|stroke|paint|painting|sketch|vẽ|nét)\b',blob): continue
                    tags.append(t['id']); break
        srcmap=label_map.get(r['source'],{})
        for label in r.get('labels',[]):
            value=srcmap.get(str(label).strip())
            if isinstance(value,str) and value!='bo_qua': tags.append(value)
            elif isinstance(value,list): tags.extend(x for x in value if x!='bo_qua')
        content=re.sub(r'https?://\S+',' ',r['text']).strip()
        if len(norm(content))<12:
            r['techniques']=['thieu_du_lieu']
        else: r['techniques']=sorted(set(tags)) or ['chua_phan_loai']
    return records
def exact_dedup(records):
    seen={}; kept=[]
    for r in sorted(records,key=lambda x:(x['source'],x['source_id'],x['uid'])):
        key= 'post:'+r['post_id'] if r['post_id'] else ('url:'+canon_url(r['url']) if canon_url(r['url']) else 'text:'+hashlib.sha256(norm(r['title']+' '+r['text']).encode()).hexdigest())
        if key not in seen: seen[key]=r; kept.append(r)
        else:
            old=seen[key]
            # Merge provenance and retain a stable, content-rich representative.
            old['sources']=sorted(set(old.get('sources',[old['source']])+[r['source']]))
            old['engine_asset']=old['engine_asset'] or r['engine_asset']
            old['techniques']=sorted(set(old.get('techniques',[])+r.get('techniques',[])))
            old['example_urls']=sorted(set(old.get('example_urls',[old['url']] if old['url'] else [])+([r['url']] if r['url'] else [])))
    return kept
def shingles(s):
    s=norm(s); return {s[i:i+5] for i in range(max(1,len(s)-4))} if s else set()
def near_dedup(records,threshold=.8):
    rs=sorted(records,key=lambda x:x['uid']); n=len(rs); parent=list(range(n))
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b: parent[max(a,b)]=min(a,b)
    # Deterministic MinHash (32 permutations, 8 bands) proposes candidates;
    # exact Jaccard decides every merge, so the threshold has no estimator noise.
    sh=[shingles(x['title']+' '+x['text']) for x in rs]
    prime=4294967311
    coeff=[(i*2654435761+104729, i*2246822519+3266489917) for i in range(32)]
    buckets=defaultdict(list)
    for i,ss in enumerate(sh):
        if not ss: continue
        vals=sorted(int.from_bytes(hashlib.sha1(s.encode()).digest()[:4],'big') for s in ss)
        sig=[]
        for aa,bb in coeff: sig.append(min((aa*v+bb)%prime for v in vals))
        for band in range(8): buckets[(band,tuple(sig[band*4:(band+1)*4]))].append(i)
    candidates=set()
    for members in buckets.values():
        if len(members)>1:
            for pos,i in enumerate(members):
                for j in members[pos+1:]: candidates.add((min(i,j),max(i,j)))
    for i,j in sorted(candidates):
        score=len(sh[i]&sh[j])/len(sh[i]|sh[j])
        if score>=threshold: union(i,j)
    groups=defaultdict(list)
    for i,r in enumerate(rs): groups[find(i)].append(r)
    out=[]
    for _,g in sorted(groups.items()):
        g.sort(key=lambda x:(-len(x['text']),x['uid'])); chosen=g[0]
        if len(g)>1:
            chosen['sources']=sorted(set(sum([x.get('sources',[x['source']]) for x in g],[])))
            chosen['engine_asset']=any(x['engine_asset'] for x in g)
            chosen['example_urls']=sorted(set(sum([x.get('example_urls',[x['url']] if x['url'] else []) for x in g],[])))
            chosen['near_members']=[x['uid'] for x in sorted(g,key=lambda x:x['uid'])]
            chosen['techniques']=sorted(set(sum((x.get('techniques',[]) for x in g),[])))
        out.append(chosen)
    return out
def clusters(records,tax):
    byid={t['id']:t for t in tax}; groups=defaultdict(list)
    for r in records:
        for tid in r['techniques']:
            if tid not in ('chua_phan_loai','thieu_du_lieu'): groups[tid].append(r)
    rows=[]
    # kỹ thuật chỉ có trong engine (không có mục tham khảo ngoài) vẫn phải lên bảng, vd zodiac_wheel, statue_cards
    for techs in load_map('engine_map.json').values():
        for tid in techs:
            if tid in byid: groups.setdefault(tid,[])
    for tid,rs in sorted(groups.items()):
        srcs=sorted(set(s for r in rs for s in r.get('sources',[r['source']])))
        links=[]
        for r in sorted(rs,key=lambda x:x['uid']):
            for u in r.get('example_urls',[r.get('url','')]):
                if u and u not in links: links.append(u)
                if len(links)>=2: break
            if len(links)>=2: break
        built=engine_status(tid)
        rows.append({'id':tid,'name_vi':byid[tid]['name_vi'],'group':byid[tid]['group'],'count':len(rs),'sources':srcs,'source_count':len(srcs),'built':built['status'],'built_evidence':built['evidence'],'examples':links,'uids':[r['uid'] for r in sorted(rs,key=lambda x:x['uid'])]})
    return rows
@lru_cache(maxsize=None)
def engine_status(tid):
    emap=load_map('engine_map.json'); assets=[]; used=[]
    for path,techs in sorted(emap.items()):
        if tid not in techs: continue
        bridge_style=path.startswith('bridge_style:')
        style=path.split(':',1)[1] if bridge_style else ''
        p=ROOT/'hyperframes_bridge.py' if bridge_style else ROOT/path
        if bridge_style:
            if not p.exists() or not re.search(r'["\']'+re.escape(style)+r'["\']\s*:',p.read_text(errors='ignore')): continue
        elif not p.exists(): continue
        assets.append(path)
        candidates=[]
        comp=USAGE_ROOT/'hyperframes_short/compositions'
        if comp.exists(): candidates.extend(sorted(comp.glob('_*.html')))
        stage=USAGE_ROOT/'output/cl_staging'
        if stage.exists():
            candidates.extend(q for q in sorted(stage.rglob('*.py')) if q.is_file())
            candidates.extend(q for q in sorted(stage.rglob('plan_*.json')) if q.is_file())
            candidates.extend(q for q in sorted(stage.rglob('*.html')) if q.is_file())
        for q in candidates:
            try: content=q.read_text(errors='ignore')
            except OSError: continue
            if bridge_style:
                refs=len(re.findall(r'["\']style["\']\s*:\s*["\']'+re.escape(style)+r'["\']',content)) if q.name.startswith('plan_') else content.count(style)
            else:
                refs=max(content.count(path),content.count(p.name),content.count(p.stem))
            if refs: used.append({'path':q.relative_to(USAGE_ROOT).as_posix(),'uses':refs,'engine_item':path})
    return {'status':'dung_that' if used else ('co_san' if assets else 'chua_co'),'evidence':used if used else assets}
def cluster_sets(records,tax):
    """Group inventory records by their complete sorted primary-technique set."""
    byid={t['id']:t for t in tax}; groups=defaultdict(list)
    for r in records: groups[tuple(t for t in r['techniques'] if t not in ('chua_phan_loai','thieu_du_lieu'))].append(r)
    rows=[]
    for techs,rs in sorted(groups.items(),key=lambda item:item[0]):
        sources=sorted(set(s for r in rs for s in r.get('sources',[r['source']])))
        rows.append({'cluster_id':'techniques:'+('+'.join(techs) if techs else 'chua_phan_loai'),'techniques':list(techs),'technique_names':[byid[t]['name_vi'] for t in techs], 'count':len(rs),'sources':sources,'source_count':len(sources),'built':{t:engine_status(t)['status'] for t in techs},'uids':[r['uid'] for r in sorted(rs,key=lambda x:x['uid'])]})
    return rows
def build(threshold=.8):
    tax=load_taxonomy(); records=tag_records(extract_a()+adapt_b_c(),tax)
    raw=records[:]; a=exact_dedup(records); b=near_dedup(a,threshold); cls=clusters(b,tax); sets=cluster_sets(b,tax)
    INV.mkdir(parents=True,exist_ok=True)
    for file,rows in [('records.jsonl',b),('clusters.jsonl',sets)]:
        (INV/file).write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in rows),encoding='utf-8')
    native_label_report(raw)
    write_samples(b, tax, cls)
    stats={'raw':dict(sorted(Counter(r['source'] for r in raw).items())),'after_exact':len(a),'after_near':len(b),'raw_count':len(raw),'technique_count':len(cls),'unclassified':sum('chua_phan_loai' in r['techniques'] for r in b),'insufficient':sum('thieu_du_lieu' in r['techniques'] for r in b),'threshold':threshold}
    stats['technique_set_clusters']=len(sets)
    (INV/'techniques.json').write_text(json.dumps({'stats':stats,'techniques':cls,'technique_set_clusters':sets},ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return stats,cls,b
def write_samples(records,tax,cls):
    top=sorted(cls,key=lambda c:(-c['count'],c['id']))[:15]
    lines=['# Mẫu kiểm tra thủ công','', 'Seed cố định: sắp xếp theo UID rồi lấy 5 mục đầu mỗi kỹ thuật. Văn bản cắt ở 150 ký tự.','']
    for c in top:
        lines += [f"## {c['name_vi']} (`{c['id']}`)",'']
        rows=[r for r in sorted(records,key=lambda x:x['uid']) if c['id'] in r['techniques']][:5]
        for r in rows:
            lines.append(f"- **{r['title'][:120]}** — {r['text'][:150].replace(chr(10),' ')} — nhãn gốc: {', '.join(r.get('labels',[])) or '—'}")
        lines.append('')
    (INV/'samples.md').write_text('\n'.join(lines),encoding='utf-8')
def make_report(stats,cls,errors):
    lines=['# Kiểm kê kỹ thuật dựng video','',f"- Mục thô: **{stats['raw_count']}** ({'; '.join(f'{k}: {v}' for k,v in stats['raw'].items()) or 'không có nguồn'})",f"- Sau khử trùng chính xác (a): **{stats['after_exact']}**",f"- Sau khử trùng gần (b, Jaccard ≥ {stats['threshold']:.2f}): **{stats['after_near']}**",f"- Kỹ thuật có match: **{stats['technique_count']}**; chưa phân loại: **{stats['unclassified']}**",'','| Kỹ thuật | Tên | Mục | Nguồn | Đã dựng (A)? | Ví dụ |','|---|---|---:|---:|---|---|']
    for c in cls:
        ex='; '.join(f'[{i+1}]({u})' for i,u in enumerate(c['examples'])) or '—'
        lines.append(f"| `{c['id']}` | {c['name_vi']} | {c['count']} | {c['source_count']} | {c['built']} | {ex} |")
    gaps=sorted((c for c in cls if c['built']!='dung_that'),key=lambda c:(-c['source_count'],-c['count'],c['id']))
    lines += ['', '## Khoảng trống tham khảo chưa dựng','']
    lines += [f"- {c['name_vi']} (`{c['id']}`): {c['source_count']} nguồn, {c['count']} mục" for c in gaps] or ['- Chưa thấy.']
    lines += ['', '## Nguồn chưa có / lỗi fetch','', '- Kho 52 mẫu Hình Sự: **chưa có** trên máy; có thể thêm adapter `adapt_<nguồn>()` trả record chung.']
    lines += [f'- {e}' for e in errors] or ['- Không có lỗi fetch.']
    lines += ['', '## Giới hạn','', '- Tagging dựa từ khoá trong taxonomy, không hiểu ngữ cảnh; Jaccard 5-gram là gần trùng văn bản, có thể bỏ sót prompt diễn đạt lại. Cluster kỹ thuật đếm một mục cho mỗi nhãn match; `chua_phan_loai` được giữ riêng.']
    body='\n'.join(lines)+'\n'
    (INV/'report.md').write_text(body,encoding='utf-8')
    source_counts='; '.join(f'{k}: {v}' for k,v in stats['raw'].items()) or 'không có dữ liệu'
    gaps=sorted((c for c in cls if c['built']!='dung_that'),key=lambda c:(-c['source_count'],-c['count'],c['id']))[:5]
    short=[
        '# Epic #37 — kiểm kê kho kiểu dựng video','',
        f"- Thô: **{stats['raw_count']}** ({source_counts}).",
        f"- Sau dedup chính xác (post ID/URL hoặc hash văn bản): **{stats['after_exact']}**.",
        f"- Sau dedup gần (MinHash 5-gram, xác minh Jaccard ≥ {stats['threshold']:.2f}): **{stats['after_near']}**; technique-set clusters: **{stats.get('technique_set_clusters',0)}**.",
        f"- Kỹ thuật match: **{stats['technique_count']}**; chưa phân loại: **{stats['unclassified']}**.",
        '- Fetch: không lỗi.' if not errors else '- Fetch lỗi: '+'; '.join(errors),
        '- Hình Sự: kho 52 mẫu **chưa có** trên máy; adapter nguồn mới chưa được feed dữ liệu.',
        f"- Giới hạn: taxonomy có {len(load_taxonomy())-1} kỹ thuật gắn bằng từ khóa tất định; không hiểu ngữ cảnh nên có thể false positive/âm tính. Jaccard 5-gram không phát hiện tốt diễn đạt lại sâu.",
        '- Lead cần quyết: duyệt mapping taxonomy vào 13 nhóm epic, ngưỡng 0.80 và các kỹ thuật cần ưu tiên; cung cấp kho Hình Sự khi sẵn sàng.',
        '- Kho bảng đầy đủ, ví dụ và khoảng trống: `library/inventory/report.md`.'
    ]
    REPORT.parent.mkdir(parents=True,exist_ok=True); REPORT.write_text('\n'.join(short)+'\n',encoding='utf-8')
    statuses=Counter(engine_status(t['id'])['status'] for t in load_taxonomy() if t['id']!='chua_phan_loai')
    unclassified=[]
    for raw_line in (INV/'records.jsonl').read_text(encoding='utf-8').splitlines():
        if not raw_line: continue
        try: row=json.loads(raw_line)
        except json.JSONDecodeError: continue
        if 'chua_phan_loai' in row.get('techniques',[]): unclassified.append(row)
    stop=set(load_map('stopwords.json').get('words',[])) | {'the','and','not','https','http','com','www','x','status','source','opus','video','to','a','by','text','author','s','original','model','from','with','this','that','for','is','in','of','on','as','at','it','be','an','or','are','was','were','has','have','will','can'}
    freq=Counter(w for r in unclassified for w in re.findall(r'[^\W\d_]{3,}',norm(re.sub(r'https?://\S+',' ',r['title']+' '+r['text'])) ,re.UNICODE) if w not in stop)
    labels=Counter(str(label) for r in unclassified for label in r.get('labels',[]))
    top=', '.join(f'{w} ({n})' for w,n in labels.most_common(20)) or 'không có'
    total=stats['after_near']; pct=100*stats['unclassified']/max(1,total)
    v2=['# Epic #37 — kiểm kê v2','',f"- Trước: 2.787 mục, 1.685 chưa phân loại (60,5%); sau: {total} mục, {stats['unclassified']} chưa phân loại ({pct:.1f}%), {stats.get('insufficient',0)} thiếu dữ liệu.",f"- Built: dung_that {statuses['dung_that']}, co_san {statuses['co_san']}, chua_co {statuses['chua_co']} kỹ thuật.",f"- Dedup 3 tầng giữ nguyên: chính xác {stats['after_exact']}, gần {stats['after_near']}.",f"- Lead cần quyết: duyệt nhãn bị bỏ qua và mapping engine còn chưa chắc; top từ còn sót: {top}."]
    V2_REPORT.parent.mkdir(parents=True,exist_ok=True); V2_REPORT.write_text('\n'.join(v2)+'\n',encoding='utf-8')
    status_counts=Counter(engine_status(t['id'])['status'] for t in load_taxonomy() if t['id'] not in ('chua_phan_loai','thieu_du_lieu'))
    pct_text=f"{pct:.1f}% ({stats['unclassified']}/{total})"
    examples=[]
    for t in sorted(load_taxonomy(),key=lambda x:x['id']):
        if engine_status(t['id'])['status']=='dung_that' and engine_status(t['id'])['evidence']:
            e=engine_status(t['id'])['evidence'][0]
            examples.append(f"{t['id']}: {e['path']} ({e['uses']})")
        if len(examples)==5: break
    v3=['# Epic #37 — kiểm kê v3','',f"- Chưa phân loại: **{pct_text}**.",f"- Kỹ thuật: **{status_counts['dung_that']} dung_that**, **{status_counts['co_san']} co_san**, **{status_counts['chua_co']} chua_co**.",'- 5 bằng chứng dung_that: '+'; '.join(examples)+'.',f"- Nhãn gốc còn sót: {top}.",'- Lead quyết: duyệt ánh xạ nhãn còn sót và taxonomy kỹ thuật mới; kiểm tra các bằng chứng sử dụng thật trước khi chốt.']
    V3_REPORT.parent.mkdir(parents=True,exist_ok=True); V3_REPORT.write_text('\n'.join(v3)+'\n',encoding='utf-8')
    return lines
def main():
    global USAGE_ROOT
    ap=argparse.ArgumentParser(); ap.add_argument('command',choices=['fetch','build','report']); ap.add_argument('--offline',action='store_true'); ap.add_argument('--threshold',type=float,default=.8); ap.add_argument('--usage-root',type=Path,default=ROOT); args=ap.parse_args()
    USAGE_ROOT=args.usage_root.expanduser().resolve(); engine_status.cache_clear()
    if not 0<=args.threshold<=1: ap.error('--threshold phải nằm trong [0,1]')
    errs=[]
    if args.command=='fetch': errs=fetch(args.offline)
    elif args.command=='build':
        s,_,_=build(args.threshold); print(json.dumps(s,ensure_ascii=False,sort_keys=True)); return
    else:
        errs=fetch(args.offline)
        # report recomputes from frozen cache/current repo for reproducibility
        s,cs,_=build(args.threshold); make_report(s,cs,errs); print(REPORT)
    for e in errs: print('WARN:',e)
if __name__=='__main__': main()
