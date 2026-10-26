#!/usr/bin/env python3
"""Kiểm tra và tìm thẻ thư viện; chuẩn thư viện Python."""
import argparse,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; CARDS=ROOT/'library/cards'; SCHEMA=ROOT/'library/schema/card.schema.json'

def parse(p):
 s=p.read_text(encoding='utf8'); m=re.match(r'\A---\s*\n(.*?)\n---\s*\n?',s,re.S)
 if not m: raise ValueError('thiếu front matter YAML')
 try:return json.loads(m.group(1)) # JSON là tập con YAML, do cards.py sinh
 except json.JSONDecodeError as e: raise ValueError('front matter phải là YAML dạng JSON hợp lệ trong P1: '+str(e))
def validate(d,schema):
 errs=[]
 for k in schema['required']:
  if k not in d: errs.append('thiếu '+k)
 for k,v in d.items():
  rule=schema.get('properties',{}).get(k,{})
  expected=rule.get('type')
  if expected=='string' and not isinstance(v,str): errs.append(k+' phải là chuỗi')
  if expected=='array' and not isinstance(v,list): errs.append(k+' phải là danh sách')
  if isinstance(expected,list) and not any((typ=='string' and isinstance(v,str)) or (typ=='array' and isinstance(v,list)) for typ in expected): errs.append(k+' phải là chuỗi hoặc danh sách')
  if 'enum' in rule and v not in rule['enum']: errs.append(f'{k} không hợp lệ: {v}')
  if rule.get('type')=='array' and not isinstance(v,list): errs.append(k+' phải là danh sách')
  if rule.get('type')=='integer' and (not isinstance(v,int) or isinstance(v,bool) or v<0): errs.append(k+' phải là số nguyên không âm')
  if k in ('so_muc','so_nguon') and (not isinstance(v,int) or v<0): errs.append(k+' phải là số nguyên không âm')
 if len(d.get('bang_chung_dung',[]))>5: errs.append('bang_chung_dung tối đa 5')
 if len(d.get('vi_du',[]))>3: errs.append('vi_du tối đa 3')
 aliases=d.get('alias',[])
 if not isinstance(d.get('id'),str) or not re.fullmatch(r'[a-z0-9_]+',d.get('id','')): errs.append('id không đúng mẫu')
 if isinstance(aliases,list):
  safe=[x for x in aliases if isinstance(x,str)]
  if len(safe)!=len(set(safe)): errs.append('alias bị trùng')
  if len(safe)!=len(aliases): errs.append('alias phải là chuỗi')
 for x in d.get('vi_du',[]):
  if not isinstance(x,str) or not re.match(r'^(https?|file)://',x): errs.append('vi_du phải là link: '+str(x))
 for x in d.get('nguon_su_that',[]):
  if not (ROOT/x).is_file(): errs.append('nguon_su_that không tồn tại: '+x)
 return errs
def cards(): return sorted(CARDS.rglob('*.md')) if CARDS.exists() else []
def check():
 schema=json.loads(SCHEMA.read_text()); seen={}; errors=[]
 for p in cards():
  try:d=parse(p)
  except ValueError as e: errors.append(f'{p.relative_to(ROOT)}: {e}'); continue
  for e in validate(d,schema): errors.append(f'{p.relative_to(ROOT)}: {e}')
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
# ---- Cổng nội dung (Lead 26/10): thẻ đã viết không được là văn khuôn, "Cách dựng" phải trỏ code có thật
PLACEHOLDER='<!-- Codex/Lead soạn ở P2 -->'
REF=re.compile(r'`([\w./-]+\.(?:py|js|html|json|css|md)):(\d+)`')
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
        dup=[x for x in _sentences(b) if count.get(x,0)>max_repeat]
        if dup: issues.append(f'{rel}: {len(dup)} câu khuôn lặp ở >{max_repeat} thẻ, vd "{dup[0][:70]}"')
        sec=b.split('## Cách dựng trong HyperFrames',1)
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
 ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True); c=sub.add_parser('check'); c.add_argument('--content',action='store_true',help='thêm cổng nội dung: câu khuôn lặp, dẫn code path:line'); c.add_argument('--usage-root'); f=sub.add_parser('find'); f.add_argument('--loai',action='append'); f.add_argument('--dinh-dang'); f.add_argument('--pham-vi'); f.add_argument('--ngach'); f.add_argument('--da-dung',choices=['dung_that','co_san','chua_co']); a=ap.parse_args()
 if a.cmd=='check':
  rc=check()
  if a.content:
   iss=content_issues(usage_root=a.usage_root)
   for x in iss: print('NỘI DUNG:',x)
   print(f'Cổng nội dung: {len(iss)} lỗi'); rc=rc or (1 if iss else 0)
  sys.exit(rc)
 find(a)
if __name__=='__main__':main()
