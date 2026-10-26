#!/usr/bin/env python3
"""Kiểm tra, tìm và xếp hạng thẻ thư viện; chỉ dùng thư viện chuẩn."""
import argparse,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; CARDS=ROOT/'library/cards'; SCHEMA=ROOT/'library/schema/card.schema.json'

def parse(p):
 s=p.read_text(encoding='utf8'); m=re.match(r'\A---\s*\n(.*?)\n---\s*\n?',s,re.S)
 if not m: raise ValueError('thiếu front matter YAML')
 try:return json.loads(m.group(1)) # JSON là tập con YAML, do cards.py sinh
 except json.JSONDecodeError as e: raise ValueError('front matter phải là YAML dạng JSON hợp lệ trong P1: '+str(e))
def validate(d,schema,usage_root=None):
 errs=[]
 for k in schema['required']:
  if k not in d: errs.append('thiếu '+k)
 for k,v in d.items():
  rule=schema.get('properties',{}).get(k,{})
  expected=rule.get('type')
  if expected=='string' and not isinstance(v,str): errs.append(k+' phải là chuỗi')
  if expected=='array' and not isinstance(v,list): errs.append(k+' phải là danh sách')
  if expected=='object' and not isinstance(v,dict): errs.append(k+' phải là đối tượng')
  if isinstance(expected,list) and not any((typ=='string' and isinstance(v,str)) or (typ=='array' and isinstance(v,list)) for typ in expected): errs.append(k+' phải là chuỗi hoặc danh sách')
  if 'enum' in rule and v not in rule['enum']: errs.append(f'{k} không hợp lệ: {v}')
  if rule.get('type')=='array' and not isinstance(v,list): errs.append(k+' phải là danh sách')
  if rule.get('type')=='integer' and (not isinstance(v,int) or isinstance(v,bool) or v<0): errs.append(k+' phải là số nguyên không âm')
  if k in ('so_muc','so_nguon') and (not isinstance(v,int) or v<0): errs.append(k+' phải là số nguyên không âm')
 if len(d.get('bang_chung_dung',[]))>5: errs.append('bang_chung_dung tối đa 5')
 if len(d.get('vi_du',[]))>3: errs.append('vi_du tối đa 3')
 for channel,usage in d.get('dang_dung_o',{}).items() if isinstance(d.get('dang_dung_o',{}),dict) else []:
  if channel not in ('fs','bud','cl') or not isinstance(usage,dict) or not isinstance(usage.get('so_bai'),int) or isinstance(usage.get('so_bai'),bool) or usage['so_bai']<0 or not isinstance(usage.get('bai'),list): errs.append('dang_dung_o không đúng cấu trúc: '+str(channel))
 aliases=d.get('alias',[])
 if not isinstance(d.get('id'),str) or not re.fullmatch(r'[a-z0-9_]+',d.get('id','')): errs.append('id không đúng mẫu')
 if isinstance(aliases,list):
  safe=[x for x in aliases if isinstance(x,str)]
  if len(safe)!=len(set(safe)): errs.append('alias bị trùng')
  if len(safe)!=len(aliases): errs.append('alias phải là chuỗi')
 for x in d.get('vi_du',[]):
  if not isinstance(x,str) or not re.match(r'^(https?|file)://',x): errs.append('vi_du phải là link: '+str(x))
 for x in d.get('nguon_su_that',[]):
  source=str(x).rsplit(':',1)[0] if isinstance(x,str) and re.search(r':\d+$',x) else x
  if isinstance(source,str) and source.startswith('output/') and not usage_root:
   continue   # output/ bị gitignore: chỉ kiểm khi có --usage-root (checkout chính); CI chạy không có thư mục này
  if not isinstance(source,str) or not ((ROOT/source).is_file() or (usage_root and (Path(usage_root)/source).is_file())): errs.append('nguon_su_that không tồn tại: '+str(x))
 return errs
def cards(): return sorted(CARDS.rglob('*.md')) if CARDS.exists() else []
def check(usage_root=None):
 schema=json.loads(SCHEMA.read_text()); seen={}; errors=[]
 for p in cards():
  try:d=parse(p)
  except ValueError as e: errors.append(f'{p.relative_to(ROOT)}: {e}'); continue
  for e in validate(d,schema,usage_root): errors.append(f'{p.relative_to(ROOT)}: {e}')
  tid=d.get('id')
  if tid in seen: errors.append(f'id trùng {tid}: {seen[tid]} và {p.relative_to(ROOT)}')
  seen[tid]=p.relative_to(ROOT)
 ids=set(seen)
 for tid,p in seen.items():
  try:d=parse(ROOT/p)
  except ValueError: continue
  for alias in d.get('alias',[]):
   if alias in ids: errors.append(f'{p}: alias {alias} trùng id')
 for e in errors: print('ERROR:',e)
 if not errors: print(f'OK: {len(seen)} thẻ hợp lệ')
 return 1 if errors else 0
def find(args):
 rows=[]
 for p in cards():
  try:d=parse(p)
  except ValueError:continue
  if args.loai and d.get('loai') not in args.loai:continue
  if args.dinh_dang and args.dinh_dang not in d.get('dinh_dang',[]):continue
  if args.pham_vi and args.pham_vi not in d.get('pham_vi',[]):continue
  if args.ngach and args.ngach not in d.get('hop_ngach',[]):continue
  if args.da_dung and d.get('da_dung')!=args.da_dung:continue
  rows.append(d)
 print('| id | tên | loại | định dạng | phạm vi | ngách | đã dùng |\n|---|---|---|---|---|---|---|')
 for d in rows: print('| '+' | '.join(str(d.get(k,'' )).replace('|','\\|') for k in ('id','ten','loai','dinh_dang','pham_vi','hop_ngach','da_dung'))+' |')

CHANNELS=ROOT/'library/channels'
def _brief_templates(path, source_root=None):
 """Đọc bảng luật dừng khuôn; trả khuôn, trạng thái, và dòng nguồn."""
 lines=path.read_text(encoding='utf8').splitlines(); in_table=False; seen_table=False; rows=[]; section='short'
 for no,line in enumerate(lines,1):
  if line.startswith('## '):
   section='long' if 'long' in line.lower() else ('short' if 'short' in line.lower() else section)
   if 'luật dừng khuôn' in line.lower(): in_table=True; seen_table=False; continue
  if 'luật dừng khuôn' in line.lower(): in_table=True; seen_table=False; continue
  if in_table and line.startswith('|'):
   seen_table=True
   cells=[x.strip().strip('`') for x in line.strip().strip('|').split('|')]
   if len(cells)<5 or cells[0].lower()=='khuôn' or set(''.join(cells))<=set('-: '): continue
   name, conclusion=cells[0],cells[-1]
   if not name: continue
   state='thua' if 'dừng' in conclusion.lower() else ('thang' if 'giữ' in conclusion.lower() else 'ngang')
   source=path.relative_to(source_root).as_posix() if source_root else path.as_posix()
   rows.append({'ten':name,'dinh_dang':section,'trang_thai':state,'nguon':f'{source}:{no}'})
  elif in_table and seen_table and line.strip() and not line.startswith('|'):
   in_table=False
 return rows

def sync_channels(usage_root):
 """Sinh hồ sơ JSON hợp lệ YAML từ rules + brief, lưu dòng nguồn nguyên dạng."""
 usage=Path(usage_root); rules=usage/'output/cl_staging/grok/rules.md'
 out=usage/'output/cl_staging/briefs'; CHANNELS.mkdir(parents=True,exist_ok=True)
 for ch,ngach,giong,formats,cta in (
  ('fs',['phong_thuy','tu_vi','lich_am'],'giọng giải thích gần gũi, khung tham khảo; tên con giáp theo tên chi',['short','long'],'chưa nêu trong brief/rules'),
  ('bud',['phat_phap','loi_phat_day','jataka'],'giọng trang nghiêm, lời Phật phải đối chiếu nguồn',['short','long'],'chưa nêu trong brief/rules')):
  brief=out/f'{ch}.md'; templates=_brief_templates(brief,usage) if brief.is_file() else []
  brief_rel=brief.relative_to(usage).as_posix(); rules_rel=rules.relative_to(usage).as_posix()
  try: rule_text=rules.read_text(encoding='utf8').splitlines()
  except OSError: rule_text=[]
  rule_line=next((i for i,x in enumerate(rule_text,1) if x.startswith('5. ')),None)
  rules_ch=rule_text[rule_line-1] if rule_line else 'Chưa tìm thấy luật kênh trong grok/rules.md'
  if rule_line and ch=='fs' and ' BUD:' in rules_ch: rules_ch=rules_ch.split(' BUD:',1)[0]
  elif rule_line and ch=='bud' and ' BUD:' in rules_ch: rules_ch='BUD:'+rules_ch.split(' BUD:',1)[1]
  doc={'kenh':ch,'ngach':ngach,'giong':giong,'luat_cam':[{'noi_dung':rules_ch,'nguon':f'{rules_rel}:{rule_line}' if rule_line else rules_rel}],
       'dinh_dang_dung':formats,'cta_hien_tai':{'gia_tri':cta,'nguon':f'{brief_rel} (CTA không được nêu)'},
       'khuon':templates,'nguon_brief':brief_rel}
  dst=CHANNELS/f'{ch}.yaml'
  if dst.is_file():   # giữ trường người điền (vd bao_ve, cta thật) — chỉ ghi lại trường máy
   try: old=json.loads(dst.read_text(encoding='utf8'))
   except ValueError: old={}
   for k,v in old.items():
    if k not in doc: doc[k]=v
  (CHANNELS/f'{ch}.yaml').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return {c:json.loads((CHANNELS/f'{c}.yaml').read_text()) for c in ('fs','bud')}

def _cards_data():
 out=[]
 for p in cards():
  try: out.append(parse(p))
  except ValueError: pass
 return out

def ranked(channel,top=10):
 rows=[]
 for d in _cards_data():
  if d.get('loai')!='canh' or d.get('da_dung') not in ('chua_co','co_san'): continue
  fit=d.get('do_hop',{})
  try: score_fit=float(fit.get(channel,0))
  except (AttributeError,TypeError,ValueError): score_fit=0
  if score_fit<=0: continue
  barred=[str(x).lower() for x in d.get('cam_ngach',[])]
  if any(channel in x for x in barred): continue
  cost={'thap':1,'vua':2,'cao':3}.get(str(d.get('cong','vua')).lower(),2)
  n=max(0,int(d.get('so_nguon',0) or 0)); score=score_fit*n/cost
  if score<=0: continue
  reason=f"độ hợp {score_fit:g} × {n} nguồn / công {cost} ({d.get('cong','vua')}); trạng thái {d['da_dung']}"
  rows.append({'id':d['id'],'ten':d.get('ten',d['id']),'diem':score,'do_hop':score_fit,'so_nguon':n,'cong':cost,'ly_do':reason})
 return sorted(rows,key=lambda r:(-r['diem'],r['id']))[:max(0,top)]

def _experiments(root,channel):
 found=[]; base=Path(root)/'output/cl_staging/experiments'
 if not base.exists(): return found
 for p in sorted(base.glob('*.json')):
  try: d=json.loads(p.read_text(encoding='utf8'))
  except (OSError,ValueError): continue
  if not isinstance(d,dict): continue
  ch=d.get('channel') or d.get('kenh')
  if ch and ch!=channel: continue
  found.append({'ten':d.get('id') or d.get('name') or p.stem,'dinh_dang':d.get('format') or d.get('dinh_dang') or 'thử nghiệm','trang_thai':'thu_nghiem','nguon':p.relative_to(Path(root)).as_posix()})
 return found

def picks(channel,usage_root):
 profiles=sync_channels(usage_root); profile=profiles[channel]
 bao_ve=profile.get('bao_ve',[])   # chuỗi/bài thắng nằm trong khuôn thua-ngang: không được áp thư viện (Lead 26/10)
 places=[dict(x) for x in profile.get('khuon',[]) if x.get('trang_thai')!='thang']
 for x in places:
  hit=[b for b in bao_ve if b.get('khuon') in (x.get('id'),x.get('ten'))]
  if hit: x['loai_tru']=[f"{b['ten']}: {b['ly_do']}" for b in hit]
 places.extend(_experiments(usage_root,channel))
 top=ranked(channel,3)
 for place in places: place['goi_y']=top
 return {'kenh':channel,'noi_duoc_ap':places,'ly_do_chung':'ADR 0018 mục 7: chỉ áp vào khuôn ngang/thua và ô thử nghiệm; loại toàn bộ khuôn thang.'}

def print_rank(rows):
 print('| # | kỹ thuật | điểm | lý do |\n|---:|---|---:|---|')
 for i,x in enumerate(rows,1): print(f"| {i} | {x['ten']} (`{x['id']}`) | {x['diem']:.3f} | {x['ly_do']} |")

def print_pick(result):
 print('| nơi áp dụng | trạng thái | nguồn | 3 gợi ý kỹ thuật | lý do |\n|---|---|---|---|---|')
 for x in result['noi_duoc_ap']:
  names=', '.join(f"{r['ten']} ({r['diem']:.2f})" for r in x['goi_y']) or 'chưa có kỹ thuật phù hợp'
  why=result['ly_do_chung']+(' KHÔNG áp cho: '+'; '.join(x['loai_tru']) if x.get('loai_tru') else '')
  print(f"| {x['dinh_dang']} · {x['ten']} | {x['trang_thai']} | {x['nguon']} | {names} | {why} |")
# ---- Cổng nội dung (Lead 26/10): thẻ đã viết không được là văn khuôn, "Cách dựng" phải trỏ code có thật
PLACEHOLDER='<!-- Codex/Lead soạn ở P2 -->'
REF=re.compile(r'`([\w./-]+\.(?:py|js|html|json|jsonl|css|md)):(\d+)`')
def _body(text):
    return text.split('\n---\n',1)[1] if '\n---\n' in text else text
def _sentences(body):
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+|\n',body) if len(x.strip())>25 and not x.strip().startswith('#')]
def content_issues(root=None, usage_root=None, max_repeat=4):
    """Trả danh sách lỗi nội dung cho các thẻ ĐÃ viết (bỏ qua thẻ còn chú thích chờ soạn)."""
    root=Path(root or ROOT); usage=Path(usage_root) if usage_root else root
    cards={f:_body(f.read_text(encoding='utf8')) for f in sorted((root/'library/cards').glob('*/*.md'))}
    written={f:b for f,b in cards.items() if PLACEHOLDER not in b}
    count={}
    for b in written.values():
        for x in set(_sentences(b)): count[x]=count.get(x,0)+1
    issues=[]
    for f,b in written.items():
        rel=f.relative_to(root).as_posix()
        empty=[h for h,c in re.findall(r'\n## ([^\n]+)\n(.*?)(?=\n## |\Z)','\n'+b,re.S) if not c.strip()]
        if empty: issues.append(f'{rel}: mục rỗng: {", ".join(empty)}')
        dup=[x for x in _sentences(b) if count.get(x,0)>max_repeat]
        if dup: issues.append(f'{rel}: {len(dup)} câu khuôn lặp ở >{max_repeat} thẻ, vd "{dup[0][:70]}"')
        heading='## Cách dựng trong HyperFrames' if '## Cách dựng trong HyperFrames' in b else '## Cách dùng'
        sec=b.split(heading,1)
        part=sec[1].split('\n## ',1)[0] if len(sec)>1 else ''
        refs=REF.findall(part)
        if not refs and 'chưa có trong engine' not in part:
            issues.append(f'{rel}: "Cách dựng" thiếu dẫn `đường_dẫn:dòng`')
        for path,line in refs:
            q=root/path if (root/path).exists() else usage/path
            if not q.exists(): issues.append(f'{rel}: dẫn tới file không có {path}'); continue
            lines=q.read_text(encoding='utf8',errors='ignore').splitlines()
            if not (1<=int(line)<=len(lines)): issues.append(f'{rel}: {path}:{line} vượt số dòng ({len(lines)})')
    return issues

def main():
 ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True); c=sub.add_parser('check'); c.add_argument('--content',action='store_true',help='thêm cổng nội dung: câu khuôn lặp, dẫn code path:line'); c.add_argument('--usage-root'); f=sub.add_parser('find'); f.add_argument('--loai',action='append'); f.add_argument('--dinh-dang'); f.add_argument('--pham-vi'); f.add_argument('--ngach'); f.add_argument('--da-dung',choices=['dung_that','co_san','chua_co']);
 for cmd in ('rank','pick'):
  q=sub.add_parser(cmd); q.add_argument('--channel',choices=['fs','bud'],required=True); q.add_argument('--usage-root',default=str(ROOT))
  if cmd=='rank': q.add_argument('--top',type=int,default=10)
  else: q.add_argument('--json',action='store_true')
 a=ap.parse_args()
 if a.cmd=='check':
  rc=check(a.usage_root)
  if a.content:
   iss=content_issues(usage_root=a.usage_root)
   for x in iss: print('NỘI DUNG:',x)
   print(f'Cổng nội dung: {len(iss)} lỗi'); rc=rc or (1 if iss else 0)
  sys.exit(rc)
 elif a.cmd=='rank': print_rank(ranked(a.channel,a.top))
 elif a.cmd=='pick':
  result=picks(a.channel,a.usage_root)
  if a.json: print(json.dumps(result,ensure_ascii=False,indent=2))
  else: print_pick(result)
 else: find(a)
if __name__=='__main__':main()
