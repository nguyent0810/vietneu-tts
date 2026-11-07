import json
from pathlib import Path

root = Path('data/stier/specs')
law = 'https://xaydungchinhsach.chinhphu.vn/quy-dinh-dieu-kien-va-muc-huong-tro-cap-that-nghiep-119250807095034717.htm'
health = 'https://baohiemxahoi.gov.vn/tintuc/pages/linh-vuc-bao-hiem-y-te.aspx?CateID=169&ItemID=27248&OtItem=date'
items = [
 dict(slug='ck-f1-60-phan-tram-luong-dong', title='Trợ cấp thất nghiệp: 60% bình quân lương đóng', sub='TRỢ CẤP THẤT NGHIỆP', image='lib198/ai_21.png', url=law, target='ck-f1-tro-cap-that-nghiep', date='2026-11-20T10:30:00Z', num=60, suffix='%', label='BÌNH QUÂN LƯƠNG ĐÓNG', cards=[('LƯƠNG ĐÓNG','6 THÁNG'),('TRỢ CẤP','60%')], ending='CÓ TRẦN VÙNG', lines=[
 'Trợ cấp không tính theo lương thực nhận.',
 'Theo Luật Việc làm, trợ cấp mỗi tháng bằng sáu mươi phần trăm bình quân lương đóng bảo hiểm thất nghiệp. Mức bình quân tính theo sáu tháng gần nhất trước khi nghỉ.',
 'Đó là tiền lương làm căn cứ đóng, không mặc định là số tiền chuyển vào tài khoản của bạn.',
 'Khoản trợ cấp còn có mức trần theo lương tối thiểu vùng tại tháng đóng cuối cùng.',
 'Bạn cũng phải đáp ứng đủ điều kiện và nộp hồ sơ đúng hạn.',
 'Vì vậy, nhìn bảng lương đóng trước khi ước tính khoản đệm sau nghỉ việc.' ]),
 dict(slug='ck-f1-bac-thang-tro-cap', title='Đóng thất nghiệp 36 tháng: hưởng trợ cấp bao lâu', sub='THỜI GIAN HƯỞNG', image='lib198/ai_37.png', url=law, target='ck-f1-tro-cap-that-nghiep', date='2026-11-20T12:00:00Z', num=3, suffix=' THÁNG', label='HƯỞNG KHI ĐỦ ĐIỀU KIỆN', cards=[('ĐÓNG ĐỦ','12–36 THÁNG'),('HƯỞNG','3 THÁNG')], ending='CÓ GIỚI HẠN', lines=[
 'Ba năm đóng không đổi thành ba năm hưởng.',
 'Khi đủ điều kiện hưởng trợ cấp thất nghiệp, thời gian nhận được tính theo bậc tháng đã đóng.',
 'Đóng từ đủ mười hai đến đủ ba mươi sáu tháng thì hưởng ba tháng trợ cấp.',
 'Sau đó, cứ đóng đủ thêm mười hai tháng thì được thêm một tháng hưởng.',
 'Tổng thời gian hưởng tối đa là mười hai tháng, không kéo dài theo toàn bộ số năm đi làm.',
 'Số tháng đã đóng và điều kiện hồ sơ cùng quyết định khoản đệm của bạn.' ]),
 dict(slug='ck-f2-bhyt-nam-nam-lien-tuc', title='BHYT 5 năm: khi nào được hưởng 100%', sub='BẢO HIỂM Y TẾ', image='lib198/ai_40.png', url=health, target='ck-f2-vien-phi-bhyt', date='2026-11-20T15:00:00Z', num=5, suffix=' NĂM', label='THAM GIA LIÊN TỤC', cards=[('ĐIỀU KIỆN','5 NĂM'),('CÙNG CHI TRẢ','TRÊN 15,18 TRIỆU')], ending='TRONG PHẠM VI HƯỞNG', lines=[
 'Năm năm chưa tự động miễn viện phí.',
 'Tham gia bảo hiểm y tế liên tục từ năm năm là một điều kiện. Khi đủ điều kiện, quỹ thanh toán một trăm phần trăm chi phí trong phạm vi quyền lợi.',
 'Bạn còn cần có số tiền cùng chi trả trong năm vượt sáu lần mức tham chiếu và khám chữa bệnh đúng quy định.',
 'Theo Bảo hiểm xã hội Việt Nam, từ tháng bảy năm nay, ngưỡng đó là trên khoảng mười lăm triệu đồng.',
 'Phần ngoài phạm vi quyền lợi không vì thế tự động được chi trả.',
 'Một trăm phần trăm luôn phải đi cùng điều kiện và phạm vi hưởng.' ])
]
for x in items:
    p=root/(x['slug']+'.json')
    scenes=[
      dict(type='photo',at=0,img='opening',credit=False,label=dict(text=x['sub'],at=0),mode='full'),
      dict(type='counter',at=1,**{'from':x['num'],'to':x['num']},label=x['label'],suffix=x['suffix'],prefix=''),
      dict(type='cards3d',at=2,title=x['sub'],cards=[dict(k=k,v=v,at=2) for k,v in x['cards']]),
      dict(type='timeline',at=3,items=[dict(year='ĐIỀU KIỆN',text='ÁP DỤNG THEO QUY ĐỊNH',at=3)]),
      dict(type='cards3d',at=4,title='ĐIỀU KIỆN ÁP DỤNG',cards=[dict(k='QUYỀN LỢI',v='THEO QUY ĐỊNH',at=4)]),
      dict(type='slam',at=5,text=x['ending'],sub='QUYỀN LỢI CÓ ĐIỀU KIỆN')]
    spec=dict(theme='ck',kicker='1 CON SỐ',sub=x['sub'],title=x['title'],description=x['title']+'\n\nNguồn:\n'+x['url']+'\n\nNội dung giáo dục, không phải tư vấn đầu tư.',tags=['tài chính cá nhân','biểu đồ biết nói'],acc=[],lines=x['lines'],scenes=scenes,sources=[x['url']],mix=True,rules=2,music_gain=.18,music_duck=3,sfx_gain=.36,tts={'pauses':{str(i):.22 for i in range(5)}},say={},imgs={'opening':'local:../output/asset_library/'+x['image']},short_type='L',publish_at=x['date'],long_target='long-'+x['target'])
    with p.open('w',encoding='utf-8') as f: json.dump(spec,f,ensure_ascii=False,indent=1); f.write('\n')

with Path('docs/pm/tickets/GH-228-ck-shorts2-lines.md').open('w',encoding='utf-8') as f:
    f.write('# GH-228 — lời đọc và nguồn (đang làm)\n\n')
    for x in items:
        f.write('## '+x['slug']+'\n\n'+'\n\n'.join(x['lines'])+'\n\nNguồn: '+x['url']+'\n\n')
