import json
import re
from pathlib import Path

root = Path('docs/pm/tickets/GH-180-shorts-lines.md').read_text(encoding='utf-8')
parts = re.split(r'^### (\d+)\. `([^`]+)` · ([LS])\s*$', root, flags=re.M)
common_tax = [
 'https://xaydungchinhsach.chinhphu.vn/quy-dinh-giam-tru-gia-canh-trong-thue-thu-nhap-ca-nhan-119260327071750084.htm',
 'https://tapchicongthuong.vn/nhung-diem-moi-cua-luat-thue-thu-nhap-ca-nhan-nam-2025-va-tac-dong-den-doi-song-kinh-te-xa-hoi-556804.htm',
 'https://luatvietnam.vn/bao-hiem/tu-2026-muc-dong-bhxh-bhyt-bhtn-cua-nld-va-nsdld-duoc-tinh-nhu-the-nao-563-106906-article.html']
cpi = 'https://www.nso.gov.vn/en/data-and-statistics/2026/10/consumer-price-index-gold-price-index-and-us-dollar-price-index-in-september-2026-q3-2026-and-the-nine-months-of-2026/'
visuals = [
 ['TRỪ 6,6 TRIỆU','LƯƠNG 25 TRIỆU · THƯỞNG 50 TRIỆU','PHIẾU LƯƠNG 75 TRIỆU','BẢO HIỂM TÍNH TRÊN LƯƠNG','THUẾ THÁNG THƯỞNG ≈ 6,635 TRIỆU','CẢ NĂM: ĐÃ TRỪ ≈ 7 TRIỆU · THUẾ ≈ 2,905 TRIỆU','CHÊNH LỆCH ≈ 4,1 TRIỆU','CHƯA PHẢI SỐ CUỐI'],
 ['LỆCH 3,7 TRIỆU','MỖI NGƯỜI PHỤ THUỘC · MỘT LẦN','CHỒNG 25 TRIỆU · VỢ 15 TRIỆU','ĐĂNG KÝ CHO CHỒNG · ≈ 33.750 ĐỒNG','ĐĂNG KÝ CHO VỢ · SAU BẢO HIỂM ≈ 13,4 TRIỆU','THUẾ CỦA CHỒNG ≈ 343.750 ĐỒNG','CHÊNH MỘT NĂM ≈ 3,72 TRIỆU','MỘT TỜ ĐĂNG KÝ'],
 ['BẬC MỘT 1.901','TỪ 1/11/2026 · 5 BẬC','BẬC THẤP NHẤT · 1.901 ĐỒNG/KWH','BẬC CAO NHẤT · 3.844 ĐỒNG/KWH','CHƯA GỒM VAT','BẬC CAO ≈ GẤP ĐÔI · KÊNH TỰ TÍNH','MỖI BẬC TÍNH PHẦN ĐIỆN RIÊNG','CHỈ PHẦN VƯỢT CHỊU GIÁ BẬC ĐÓ'],
 ['4,84 TRIỆU NGƯỜI','2016–2022 · ≈ 4,84 TRIỆU NGƯỜI','SỐ LIỆU BHXH VIỆT NAM','≈ 1,24 TRIỆU NGƯỜI QUAY LẠI','TỔNG TRONG 7 NĂM','≈ 1/4 · KÊNH TỰ TÍNH','KHOẢNG 4 NGƯỜI RÚT · 1 NGƯỜI QUAY LẠI'],
 ['540 NGHÌN MỘT THÁNG','TỪ THÁNG 10/2026 · 540 NGHÌN','TỪ THÁNG 7/2025 · 500 NGHÌN','TỪ ĐỦ 75 TUỔI · CÓ ĐIỀU KIỆN','HỘ NGHÈO, CẬN NGHÈO · TỪ ĐỦ 70','MỨC CHUNG · ĐỊA PHƯƠNG CÓ THỂ HỖ TRỢ THÊM','TRỢ CẤP XÃ HỘI · KHÔNG PHẢI LƯƠNG HƯU'],
 ['NGƯỠNG MỘT TỶ','DOANH THU NĂM ≤ 1 TỶ · KHÔNG NỘP TNCN, GTGT','≈ 2,556 TRIỆU HỘ VÀ CÁ NHÂN','TRÊN 1 TỶ · HÓA ĐƠN ĐIỆN TỬ','MỘT NGƯỠNG · HAI PHÍA'],
 ['CÒN MỘT NỬA','CPI 9 THÁNG · +4,52%','NẾU 4,52% LẶP LẠI · CHƯA TỚI 16 NĂM','70 ÷ 4,52 ≈ 15,5 NĂM','TÍNH ĐÚNG ≈ 15,68 NĂM','MINH HỌA · KHÔNG DỰ BÁO','4,52% ĐÃ XẢY RA · 16 NĂM NẾU LẶP LẠI'],
 ['THÁNG 9 LÀ 5,08%','THÁNG 9 · +5,08% SO VỚI CÙNG KỲ','BÌNH QUÂN 9 THÁNG · +4,52%','LẠM PHÁT LÕI · +4,26%','NGUỒN: CỤC THỐNG KÊ','MỘT THÁNG VÀ MỨC BÌNH QUÂN','THÁNG 9: 5,08% · 9 THÁNG: 4,52%'],
 ['TRẦN 26,55 TRIỆU','60% BÌNH QUÂN 6 THÁNG LƯƠNG ĐÓNG','6 THÁNG CÓ ĐÓNG BẢO HIỂM','TRẦN: 5 LẦN LƯƠNG TỐI THIỂU VÙNG','VÙNG I · 5,31 TRIỆU/THÁNG','5 × 5,31 = 26,55 TRIỆU · KÊNH TỰ TÍNH','60% LÀ CÔNG THỨC · TRẦN LÀ TỐI ĐA']]
subtitles=['THUẾ THU NHẬP CÁ NHÂN','GIẢM TRỪ NGƯỜI PHỤ THUỘC','GIÁ ĐIỆN SINH HOẠT','BẢO HIỂM XÃ HỘI MỘT LẦN','TRỢ CẤP HƯU TRÍ XÃ HỘI','THUẾ HỘ KINH DOANH','LẠM PHÁT VÀ SỨC MUA','CHỈ SỐ GIÁ TIÊU DÙNG','TRỢ CẤP THẤT NGHIỆP']
longs={1:('long-ck-e5-thue-tncn-2026','https://youtu.be/oOstT8fGnn0'),2:('long-ck-e5-thue-tncn-2026','https://youtu.be/oOstT8fGnn0'),4:('long-ck-e6-luong-huu-rut-mot-lan','https://youtu.be/0tbkF76yHTk'),5:('long-ck-e6-luong-huu-rut-mot-lan','https://youtu.be/0tbkF76yHTk'),7:('long-ck-a2-luong-va-lam-phat','https://youtu.be/3fmd-fVWW80'),8:('long-ck-a2-luong-va-lam-phat','https://youtu.be/3fmd-fVWW80')}
for pos in range(1,len(parts),4):
 n,slug,kind,body=parts[pos:pos+4]; n=int(n)
 title=re.search(r'Tiêu đề \(\d+\): (.+)',body).group(1).strip()
 section=body.split('Lời đọc:',1)[1].split('`hypo`:',1)[0]
 lines=re.findall(r'^\d+\. (.+)$',section,flags=re.M)
 assert len(lines)==len(visuals[n-1]) and len(title)<=60
 urls=re.findall(r'https://[^\s)]+',body.split('Nguồn đã mở:',1)[1].split('Ghi cho Codex:',1)[0])
 if n==2: urls=common_tax
 if n==8: urls=[cpi]
 assert urls
 scenes=[]
 for i,v in enumerate(visuals[n-1]):
  if i in (0,4,5):
   scene={'type':'kinetic','at':i,'items':[{'text':v,'at':i,'acc':True}],'clip':'pexels:7710775','win':'top','ms':1,'veil':0.58}
  elif i == 2:
   vals=[75,25,1901,1.24,500,2.556,15.68,4.52,6]
   scene={'type':'counter','at':i,'from':vals[n-1],'to':vals[n-1],'label':v}
  elif i % 2:
   scene={'type':'cards3d','at':i,'title':subtitles[n-1],'cards':[{'k':'THÔNG TIN','v':v,'at':i}]}
  else:
   scene={'type':'board','at':i,'title':subtitles[n-1],'nodes':[{'text':v,'x':0.5,'y':0.5,'at':i,'shape':'none','w':800}]}
  if n==4 and i==2:
   scene={'type':'board','at':i,'title':subtitles[n-1],'nodes':[{'text':v,'x':0.5,'y':0.5,'at':i,'shape':'none','w':800}]}
  if n==4 and i==3:
   scene={'type':'counter','at':i,'from':1.24,'to':1.24,'suffix':' TRIỆU','label':v}
  if n==3 and i==2: scene['year']=False
  if (n==1 and i<=6) or (n==2 and i in [0,2,3,4,5,6]) or (n==7 and i in [0,2,3,4,5,6]):
   scene['hypo']=True
   if n==7: scene['hypo_sub']='PHÉP TÍNH, KHÔNG PHẢI DỰ BÁO'
  scenes.append(scene)
 description=title+'.\n\nNguồn:\n'+'\n'.join(urls)
 if n in longs: description+='\n\nBản đầy đủ: '+longs[n][1]
 description+='\n\nNội dung giáo dục, không phải tư vấn đầu tư.'
 day=17+(n-1)%3; hour=['10:30','12:00','15:00'][(n-1)//3]
 spec={'theme':'ck','kicker':'1 CON SỐ','sub':subtitles[n-1],'title':title,'description':description,'tags':[subtitles[n-1].lower(),'tài chính cá nhân','biểu đồ biết nói'],'acc':[],'lines':lines,'scenes':scenes,'sources':urls,'mix':True,'rules':2,'music_gain':0.18,'music_duck':3,'sfx_gain':0.36,'tts':{'pauses':{str(i):(0.35 if i==0 else 0.22) for i in range(len(lines)-1)}},'say':{},'imgs':{},'short_type':kind,'publish_at':f'2026-11-{day}T{hour}:00Z'}
 if n in longs: spec['long_target']=longs[n][0]
 path=Path('data/stier/specs')/(slug+'.json')
 with open(path,'w',encoding='utf-8') as f: json.dump(spec,f,ensure_ascii=False,indent=2); f.write('\n')
 print(slug, spec['publish_at'])
