#!/usr/bin/env python3
"""Sinh/cập nhật nháp thẻ kỹ thuật; chỉ dùng thư viện chuẩn."""
import json, re
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
INV=ROOT/'library/inventory'; CARDS=ROOT/'library/cards'
KINDS={'style':'canh','canh':'canh','template':'template','device':'thiet_bi','thiet_bi':'thiet_bi','kich_ban':'kich_ban','luat':'luat','cong_qa':'cong_qa','quy_trinh':'quy_trinh','cong_cu':'cong_cu','du_lieu_nguon':'du_lieu_nguon','do_luong':'do_luong','bai_hoc':'bai_hoc','tham_khao':'tham_khao','khac':'tham_khao'}
MACHINE={'so_muc','so_nguon','nguon','bang_chung_dung','vi_du','da_dung','cap_nhat'}
BODY='\n\n## Mô tả\n\n<!-- Codex/Lead soạn ở P2 -->\n\n## Khi nào dùng\n\n<!-- Codex/Lead soạn ở P2 -->\n\n## Cách dựng trong HyperFrames\n\n<!-- Codex/Lead soạn ở P2 -->\n\n## Rủi ro\n\n<!-- Codex/Lead soạn ở P2 -->\n'
def read_card(p):
 s=p.read_text(encoding='utf8'); m=re.match(r'\A---\s*\n(.*?)\n---\s*\n?(.*)\Z',s,re.S)
 if not m: return {},s
 try: data=json.loads(m.group(1))
 except json.JSONDecodeError: data={}
 return data,m.group(2)
def generate():
 data=json.loads((INV/'techniques.json').read_text()); taxonomy=json.loads((INV/'taxonomy.json').read_text()); by={x['id']:x for x in taxonomy}
 rows={x['id']:x for x in data['techniques']}
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
  machine={'so_muc':row.get('count',0),'so_nguon':row.get('source_count',len(sources)),'nguon':sources,'bang_chung_dung':[x.get('path') for x in evidence if isinstance(x,dict) and x.get('path')][:5],'vi_du':examples,'da_dung':status,'cap_nhat':date.today().isoformat()}
  card={'id':tid,'ten':old.get('ten') or t.get('name_vi',tid),'loai':old.get('loai') or KINDS.get(t.get('group'),'tham_khao'),'dinh_dang':(old.get('dinh_dang') if isinstance(old.get('dinh_dang'),list) else []),'pham_vi':old.get('pham_vi',[]),'hop_ngach':old.get('hop_ngach',[]),'cam_ngach':old.get('cam_ngach',[]),**machine,'nguon_su_that':old.get('nguon_su_that',truth[:5]),'alias':t.get('alias',[])}
  # Giữ nguyên mọi trường do người duyệt thêm và toàn bộ thân thẻ.
  for k,v in old.items():
   if k not in MACHINE and k not in card: card[k]=v
  path=CARDS/card['loai']/(tid+'.md'); path.parent.mkdir(parents=True,exist_ok=True)
  for f in found:
   if f!=path: f.unlink()   # thẻ đổi loại: chuyển sang thư mục mới, giữ nội dung
  body='\n'+(body or BODY).strip('\n')+'\n'   # chuẩn hoá để chạy lại ra đúng từng byte
  path.write_text('---\n'+json.dumps(card,ensure_ascii=False,indent=2)+'\n---\n'+body,encoding='utf8')
 return len(rows)
if __name__=='__main__': print(generate())
