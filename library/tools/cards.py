#!/usr/bin/env python3
"""Sinh/cập nhật thẻ thư viện; chỉ dùng thư viện chuẩn."""
import json, re, sys
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
INV=ROOT/'library/inventory'; CARDS=ROOT/'library/cards'
KINDS={'style':'canh','canh':'canh','template':'template','device':'thiet_bi','thiet_bi':'thiet_bi','kich_ban':'kich_ban','luat':'luat','cong_qa':'cong_qa','quy_trinh':'quy_trinh','cong_cu':'cong_cu','du_lieu_nguon':'du_lieu_nguon','do_luong':'do_luong','bai_hoc':'bai_hoc','tham_khao':'tham_khao','khac':'tham_khao'}
MACHINE={'so_muc','so_nguon','nguon','bang_chung_dung','vi_du','da_dung','cap_nhat','so_lieu','nguon_su_that','mo_ta_nguon','dang_dung_o'}
BODY='\n\n## Mô tả\n\n<!-- Codex/Lead soạn ở P2 -->\n\n## Khi nào dùng\n\n<!-- Codex/Lead soạn ở P2 -->\n\n## Cách dựng trong HyperFrames\n\n<!-- Codex/Lead soạn ở P2 -->\n\n## Rủi ro\n\n<!-- Codex/Lead soạn ở P2 -->\n'
def read_card(p):
 s=p.read_text(encoding='utf8'); m=re.match(r'\A---\s*\n(.*?)\n---\s*\n?(.*)\Z',s,re.S)
 if not m: return {},s
 try: data=json.loads(m.group(1))
 except json.JSONDecodeError: data={}
 return data,m.group(2)
def _human_body(item, kind):
 """Tạo nội dung khởi đầu từ đúng đoạn nguồn; người duyệt có thể biên tập tiếp."""
 source=item['nguon_su_that'][0]
 excerpt=(item.get('mo_ta_nguon') or '').strip()
 if not excerpt: excerpt=f"{item['ten']} được định nghĩa trực tiếp trong nguồn."
 excerpt=re.sub(r'\s+',' ',excerpt).strip()
 excerpt=excerpt[:480].rstrip(' .')+'.'
 about={
  'luat':f"{item['ten']} giới hạn hành động theo điều kiện nêu trong nguồn: {excerpt}",
  'quy_trinh':f"{item['ten']} ghi lại thao tác và thứ tự cần đối chiếu: {excerpt}",
  'cong_qa':f"{item['ten']} là điểm chặn cho lỗi kiểm tra được: {excerpt}",
  'khuon':f"{item['ten']} cho biết khung nội dung cần giữ khi thay dữ liệu: {excerpt}",
  'kich_ban':f"{item['ten']} tổ chức lời kể theo nhịp và mục đích: {excerpt}",
  'du_lieu_nguon':f"{item['ten']} là đầu mối dữ liệu; phạm vi được ghi trong nguồn: {excerpt}",
  'cong_cu':f"{item['ten']} hỗ trợ một tác vụ trong pipeline: {excerpt}",
  'do_luong':f"{item['ten']} gắn với phép đo cần giữ đúng đơn vị và mẫu số: {excerpt}",
  'bai_hoc':f"{item['ten']} đại diện cho {item.get('so_lieu',{}).get('so_lan',0)} lỗi ghi nhận ở khâu này: {excerpt}",
  'tham_khao':f"{item['ten']} cung cấp chất liệu để tra cứu: {excerpt}",
  'thiet_bi':f"{item['ten']} là thành phần Studio để trình bày dữ liệu: {excerpt}",
 }
 mode={
  'luat':'đọc phạm vi kênh và điều kiện chặn trước khi biến yêu cầu thành việc phải làm',
  'quy_trinh':'lặp lại thao tác được mô tả và kiểm tra đầu ra ở từng chặng.',
  'cong_qa':'chạy tại điểm kiểm tương ứng trước khi render hoặc giao và lưu đầu ra có thể đối chiếu',
  'khuon':'thay dữ liệu trong cấu trúc mẫu sau khi xác nhận brief phù hợp',
  'kich_ban':'brief gọi đúng dạng kể chuyện và mỗi nhịp có mục đích rõ',
  'du_lieu_nguon':'cần tra cứu dữ liệu gốc và giữ lại định danh để kiểm tra kết quả',
  'cong_cu':'tác vụ khớp chức năng script và đầu ra có thể được kiểm lại',
  'do_luong':'so sánh các nhóm trên cùng cửa sổ thời gian và một định nghĩa chỉ số',
  'bai_hoc':'đang rà một lần vấp ở cùng khâu và cần kiểm tra cách sửa đã ngăn tái diễn chưa',
  'tham_khao':'cần tìm ví dụ rồi đối chiếu với brief cùng luật hiện hành',
  'thiet_bi':'cần hiển thị loại dữ liệu mà device này nhận trong Studio',
 }
 risk={
  'luat':'Một luật riêng kênh không tự động áp sang kênh khác; nhãn phạm vi trong thẻ cần được Lead xác nhận.',
  'quy_trinh':'Nếu công cụ hoặc cấu trúc thư mục đổi, bước trong tài liệu có thể lỗi thời.',
  'cong_qa':'Cổng không thể chứng minh những điều nằm ngoài các điều kiện mà nó đo.',
  'khuon':'Dùng nguyên khung cho mọi chủ đề sẽ làm sản phẩm thành công thức.',
  'kich_ban':'Nhịp kể là gợi ý cấu trúc, không thay việc kiểm chứng sự kiện và nguồn.',
  'du_lieu_nguon':'Bản ghi hoặc kết quả tra cứu có thể thiếu trường; xác minh từng mục trước khi xuất bản.',
  'cong_cu':'Mô tả từ docstring không thay thế việc xác nhận tác dụng phụ và tham số.',
  'do_luong':'Số liệu nhỏ hoặc khác mẫu số dễ tạo kết luận sai.',
  'bai_hoc':'Các lỗi cùng khâu có thể khác nguyên nhân; không coi số lần là tỷ lệ nếu chưa biết mẫu số.',
  'tham_khao':'Nguồn tham khảo không đồng nghĩa với quyền sử dụng hoặc tính đúng của nội dung.',
  'thiet_bi':'API và giao diện có thể thay đổi; xem mã nguồn trước khi gắn vào composition.',
 }
 return (f"\n## Mô tả\n\n{about.get(kind,excerpt)}\n\n## Khi nào dùng\n\n{item['ten']} phù hợp khi cần {mode.get(kind,'áp dụng hướng dẫn của nguồn sau khi kiểm tra phạm vi.')}\n\n## Cách dùng\n\nNguồn sự thật: `{source}`. {excerpt}\n\n## Rủi ro\n\nVới {item['ten']}, lưu ý rằng {risk.get(kind,'ngữ cảnh có thể thay đổi theo dự án.')}\n")

def _usage_evidence(root):
 """Đếm bài dùng thật từ plan và render; mọi suy luận kênh/engine được khai báo ở đây."""
 root=Path(root); counts={}; examples={}
 engine_map=json.loads((INV/'engine_map.json').read_text(encoding='utf8'))
 def channel(series,path):
  s=str(series or '').lower(); p=path.as_posix().lower()
  if s in ('fs','bud','cl'): return s
  # Plan không có series hợp lệ thì chỉ dùng thư mục fs/ hoặc bud/.
  for c in ('fs','bud','cl'):
   if f'/{c}/' in f'/{p}/': return c
  return None
 def add(ch, ident, engines):
  if ch not in ('fs','bud','cl'): return
  ids=set()
  for e in engines:
   key=str(e)
   ids.update(engine_map.get(key, []))
   # Plan style/layout aliases are explicit keys in engine_map.
   ids.update(engine_map.get('bridge_style:'+key, []))
   ids.update(engine_map.get('longform_layout:'+key, []))
  for tid in ids:
   counts.setdefault(tid,{}).setdefault(ch,set()).add(str(ident))
   examples.setdefault(tid,{}).setdefault(ch,[])
   if str(ident) not in examples[tid][ch] and len(examples[tid][ch])<5: examples[tid][ch].append(str(ident))
 # Each plan row represents one article. Use its style/layout engine declarations.
 for p in sorted(set(root.rglob('plan_*.json')) | set(root.rglob('plan_long_*.json'))):
  try: data=json.loads(p.read_text(encoding='utf8'))
  except (OSError,ValueError): continue
  rows=data if isinstance(data,list) else [data]
  for i,row in enumerate(rows):
   if not isinstance(row,dict): continue
   ch=channel(row.get('series'),p.relative_to(root))
   eng=[row[k] for k in ('style','layout','engine','composition') if isinstance(row.get(k),str)]
   if eng: add(ch,row.get('id') or f'{p.relative_to(root).as_posix()}#{i+1}',eng)
 # Render filenames encode channel: tn2_/r27_hop/fs_ => fs;
 # tn3_/tn4_/r27_ngu.../bud_ => bud. Count matching technique IDs/names in HTML.
 for p in sorted(root.rglob('_r_*.html')):
  ch=render_channel(p.name)
  if not ch: continue
  try: body=p.read_text(encoding='utf8',errors='ignore').lower()
  except OSError: continue
  ident=p.stem
  for card in CARDS.rglob('*.md'):
   try: d,_=read_card(card)
   except (OSError,ValueError): continue
   tid=d.get('id','')
   if d.get('loai')!='canh' or not tid: continue
   # Explicit technique id/name references in rendered artifact are evidence.
   if tid.lower() in body or str(d.get('ten','')).lower() in body:
    counts.setdefault(tid,{}).setdefault(ch,set()).add(ident)
    examples.setdefault(tid,{}).setdefault(ch,[])
    if ident not in examples[tid][ch] and len(examples[tid][ch])<5: examples[tid][ch].append(ident)
 return {tid:{ch:{'so_bai':len(ids),'bai':sorted(examples.get(tid,{}).get(ch,[]))} for ch,ids in sorted(by.items())} for tid,by in sorted(counts.items())}

def render_channel(filename):
 """Prefix rules for _r_*.html: tn2/r27_hop/fs_→FS; tn3/tn4/r27_ngu/bud_→BUD."""
 stem=Path(filename).stem.lower()
 if re.match(r'_r_(?:tn2_|r27_hop|fs_)',stem): return 'fs'
 if re.match(r'_r_(?:tn3_|tn4_|r27_ngu|bud_)',stem): return 'bud'
 return None

def generate(usage_root=None):
 data=json.loads((INV/'techniques.json').read_text()); taxonomy=json.loads((INV/'taxonomy.json').read_text()); by={x['id']:x for x in taxonomy}
 rows={x['id']:x for x in data['techniques']}
 usage=_usage_evidence(usage_root) if usage_root is not None else {}
 for tid,t in sorted(by.items()):
  if tid in ('chua_phan_loai','thieu_du_lieu') or tid not in rows: continue
  row=rows[tid]
  found=sorted(CARDS.glob('*/'+tid+'.md')) if CARDS.exists() else []   # thẻ cũ có thể nằm ở thư mục loại khác
  old,body=read_card(found[0]) if found else ({},BODY)
  status=row.get('built','chua_co'); evidence=row.get('built_evidence',[])
  sources=row.get('sources',[]); examples=row.get('examples',[])[:3]
  truth=[]
  for item in evidence:
   v=item.get('engine_item') or item.get('path') if isinstance(item,dict) else item
   if isinstance(v,str) and v.startswith('bridge_style:'): v='hyperframes_bridge.py'
   if isinstance(v,str) and v.startswith('longform_layout:'): v='hyperframes_short/compositions/longform.js'
   if v and v not in truth: truth.append(v)
  machine={'so_muc':row.get('count',0),'so_nguon':row.get('source_count',len(sources)),'nguon':sources,'bang_chung_dung':[x.get('path') for x in evidence if isinstance(x,dict) and x.get('path')][:5],'vi_du':examples,'da_dung':status,'cap_nhat':date.today().isoformat(),'dang_dung_o':usage.get(tid,{})}
  card={'id':tid,'ten':old.get('ten') or t.get('name_vi',tid),'loai':old.get('loai') or KINDS.get(t.get('group'),'tham_khao'),'dinh_dang':(old.get('dinh_dang') if isinstance(old.get('dinh_dang'),list) else []),'pham_vi':old.get('pham_vi',[]),'hop_ngach':old.get('hop_ngach',[]),'cam_ngach':old.get('cam_ngach',[]),**machine,'nguon_su_that':old.get('nguon_su_that',truth[:5]),'alias':t.get('alias',[])}
  # Giữ nguyên mọi trường do người duyệt thêm và toàn bộ thân thẻ.
  for k,v in old.items():
   if k not in MACHINE and k not in card: card[k]=v
  path=CARDS/card['loai']/(tid+'.md'); path.parent.mkdir(parents=True,exist_ok=True)
  for f in found:
   if f!=path: f.unlink()   # thẻ đổi loại: chuyển sang thư mục mới, giữ nội dung
  body='\n'+(body or BODY).strip('\n')+'\n'   # chuẩn hoá để chạy lại ra đúng từng byte
  path.write_text('---\n'+json.dumps(card,ensure_ascii=False,indent=2)+'\n---\n'+body,encoding='utf8')
 generated=len(rows)
 # Knowledge cards coexist with the technical inventory and retain edited bodies.
 if usage_root is not None:
  if str(ROOT/'library/tools') not in sys.path: sys.path.insert(0,str(ROOT/'library/tools'))
  from knowledge import scan
  knowledge=scan(usage_root)['items']
  all_cards=sorted(CARDS.rglob('*.md'))
  used={}
  parsed_cards=[]
  for p in all_cards:
   try: d,_=read_card(p)
   except (OSError,ValueError): continue
   parsed_cards.append((p,d))
   if d.get('id'): used[d['id']]=p
  kept=set()
  for item in knowledge:
   kind=item['loai']; rels=item['nguon_su_that']; title=item['ten']
   found=[p for p,d in parsed_cards if p.exists() and d.get('de_xuat_boi')=='codex-p3' and d.get('loai')==kind and d.get('ten')==title and d.get('nguon_su_that',[None])[0]==rels[0]]
   found=sorted(found,key=lambda p:(next((d.get('id')!=item['id'] for q,d in parsed_cards if q==p),True),str(p)))
   if found:
    old,body=read_card(found[0]); ident=old.get('id',item['id'])
   else:
    old,body={},''; ident=item['id']
    if ident in used:
     ident=KINDS.get(kind,kind)+'_'+ident
     while ident in used: ident='k_'+ident
   item_id=ident; kind=item['loai']; rels=item['nguon_su_that']
   item_id=ident
   target=found[0] if found else CARDS/kind/(item_id+'.md')
   # machine fields refresh; editorial metadata and the full body remain user-owned
   human_fields={k:v for k,v in old.items() if k not in MACHINE}
   source_paths=[x.split(':',1)[0] for x in rels]
   scope='chung'
   title_upper=item['ten'].upper(); context=(title_upper+' '+item.get('mo_ta_nguon','').upper())
   if any(x.startswith('hf_sutta.py') for x in source_paths) or ('BUD' in context and 'FS' not in context): scope='bud'
   elif any('hinh_su' in x for x in source_paths): scope='cl'
   elif any(x.endswith(('/canchi.py','/amlich.py')) for x in source_paths): scope='fs'
   elif 'rules.md' in source_paths[0]:
    if 'HÌNH SỰ' in context or 'HINH_SU' in context: scope='cl'
    elif 'FS' in context and 'BUD' not in context: scope='fs'
   elif any(x.endswith('/build_r1026.py') for x in source_paths): scope='fs'
   dinh_dang=old.get('dinh_dang') or ['ca_hai']
   if any('/long-' in x or 'long-video' in x for x in source_paths): dinh_dang=['long']
   elif any('/short' in x for x in source_paths): dinh_dang=['short']
   card={'id':item_id,'ten':old.get('ten') or item['ten'],'loai':kind,
    'dinh_dang':dinh_dang,'pham_vi':old.get('pham_vi',[scope]),
    'hop_ngach':old.get('hop_ngach',[]),'cam_ngach':old.get('cam_ngach',[]),
    'so_muc':item.get('so_lieu',{}).get('so_lan',1),'so_nguon':len(rels),
    'nguon':[],'bang_chung_dung':[],'vi_du':[],'nguon_su_that':rels,'alias':[],
    'da_dung':'co_san','cap_nhat':date.today().isoformat(),'so_lieu':item.get('so_lieu',{}),'dang_dung_o':{},
    'mo_ta_nguon':item.get('mo_ta_nguon',''),**human_fields}
   if 'de_xuat_boi' not in card: card['de_xuat_boi']='codex-p3'
   if not any(x.get('id')==ident for x in rows.values()):
    related=next((x.get('id') for x in rows.values() if x.get('name_vi','').lower()==item['ten'].lower()),None)
    if related: card['lien_quan']=[related]
   target.parent.mkdir(parents=True,exist_ok=True)
   for f in found[1:]: f.unlink()
   body=body if body else _human_body(item,kind)
   target.write_text('---\n'+json.dumps(card,ensure_ascii=False,indent=2)+'\n---\n'+body.rstrip('\n')+'\n',encoding='utf8')
   kept.add(target); used[item_id]=target; generated+=1
  # Remove stale machine-created cards when a source candidate disappears.
  for p,d in parsed_cards:
   if d.get('de_xuat_boi')=='codex-p3' and p not in kept and p.exists(): p.unlink()
 return generated
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser(); ap.add_argument('--usage-root'); args=ap.parse_args()
 print(generate(args.usage_root))
