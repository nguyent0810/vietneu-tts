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
def main():
 ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True); sub.add_parser('check'); f=sub.add_parser('find'); f.add_argument('--loai',action='append'); f.add_argument('--dinh-dang'); f.add_argument('--pham-vi'); f.add_argument('--ngach'); f.add_argument('--da-dung',choices=['dung_that','co_san','chua_co']); a=ap.parse_args()
 if a.cmd=='check':sys.exit(check())
 find(a)
if __name__=='__main__':main()
