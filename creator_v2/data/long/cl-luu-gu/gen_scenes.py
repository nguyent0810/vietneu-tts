"""GH-307: cảnh biên tập CH00–CH06; giữ lời đọc đã duyệt."""
import importlib.util
import json
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[2]
sys.path.insert(0, str(ROOT / 'motion/long'))
from scenekit import sc, kin, write

RES = json.loads((ROOT / 'output/long/cl-luu-gu/research.json').read_text(encoding='utf-8'))['images']
def im(i, must):
    f = RES[i]['file']
    if must not in f:
        raise ValueError(f'Ảnh {i} không khớp: {f}')
    return f

IMGS = {
 'liu': im(0, 'Liu Yong.png'), 'liu2': im(130, '劉墉人像圖1'), 'liu3': im(131, '劉墉人像圖.jpg'),
 'heshen': im(29, 'Hesen.jpg'), 'qianlong': im(4, 'Qianlong11'), 'jia': im(1, '嘉庆'),
 'council': im(162, '萬國來朝'), 'exam': im(47, 'Examination hall'), 'exam2': im(36, 'Beamtenprüfungen'),
 'exam3': im(51, 'Pass List'), 'paper': im(63, 'Qing Paper'), 'book': im(30, 'Complete Library'),
 'book2': im(31, 'Siku'), 'hall': im(55, 'lecture hall'), 'city': im(25, 'Forbidden City'),
 'court': im(10, 'Entering Suzhou'), 'gate': im(49, 'Hall of Classics'), 'cells': im(35, 'Exam cells'),
 'robe': im(158, 'court robe'), 'ink': im(96, 'Brushwasher'), 'official': im(135, 'young official'),
 'writing': im(109, '刘墉各家手札'), 'writing2': im(108, '刘墉行书'),
 'writing3': im(110, '刘墉行书'), 'writing4': im(112, '刘墉行书'), 'writing5': im(113, '刘墉行书'),
 'writing6': im(114, '刘墉行书'), 'writing7': im(125, '刘墉行书'), 'writing8': im(128, '刘墉行草'),
 'horse': im(3, 'Qianlong Emperor'), 'court2': im(162, '萬國來朝'), 'land': im(155, 'New City'),
 'hall2': im(42, 'Guozijian'), 'exam4': im(43, 'Examination hall'), 'page': im(68, '状元卷'),
 'arch': im(54, 'Imperial Colledge'), 'gates': im(153, 'Along the River'), 'rooms': im(52, 'Xu Xianqing'),
}
IMGS.update({
 'call111': im(111, '刘镛行书杂书'), 'call119': im(119, '刘墉 行书苏轼'),
 'call120': im(120, '刘墉 行书轴'), 'call126': im(126, '刘墉行书诗卷'),
 'call127': im(127, '刘墉行书录文'), 'call106': im(106, 'MET 1980'),
 'edict': im(166, 'Shengyu Guangxun'), 'painting53': im(53, 'Xu Xianqing'),
 'painting71': im(71, '应元书院'), 'painting154': im(154, 'QingMingShangHeTu'),
 'qian150': im(150, 'Qianlong Emperor in Court Dress'), 'qian151': im(151, '乾隆.jpg'),
 'plate160': im(160, 'Plate with court scene'), 'exam41': im(41, 'Exam cells model'),
 'archive66': im(66, '遷都詔'),
})
GEO = {'china': {'countries':['China'], 'context':['Mongolia','Vietnam','Laos','Myanmar','India'],
 'labels':{'China':'TRUNG QUỐC'}, 'bbox':[95,22,125,45], 'box':[260,110,1660,880],
 'pins':[{'name':'Bắc Kinh','lon':116.4,'lat':39.9,'label':'BẮC KINH'},
         {'name':'Hồ Nam','lon':112.98,'lat':28.2,'label':'HỒ NAM'},
         {'name':'Sơn Đông','lon':117,'lat':36.67,'label':'SƠN ĐÔNG'},
         {'name':'An Huy','lon':117.28,'lat':31.86,'label':'AN HUY'},
         {'name':'Sơn Tây','lon':112.55,'lat':37.87,'label':'SƠN TÂY'},
         {'name':'Thiểm Tây','lon':108.94,'lat':34.34,'label':'THIỂM TÂY'}]}}

def p(n, img, label, move='in'):
    return sc('photo', n, img=img, tone='color', move=move, illus=label, focus=[0.5,0.18])
def k(n, text, word):
    return sc('kinetic', n, items=kin((text,[n,word],'acc')))
def _split2(text):
    words, best = text.split(' '), None
    for i in range(1, len(words)):
        a, b = ' '.join(words[:i]), ' '.join(words[i:])
        cost = max(len(a), len(b))
        if best is None or cost < best[0]:
            best = (cost, [a, b])
    return best[1] if best else [text]
def _wrap(name, limit=12):
    """Lint html 13/11: lòng thẻ file 872px ≈ 12 ký tự chữ hoa. Tách tại '·' trước (bỏ dấu), dòng nào còn dài thì chia đôi
    ở khoảng trắng cân nhất."""
    if len(name) <= limit or '\n' in name:
        return name
    parts = [x.strip() for x in name.split('·')] if '·' in name else [name]
    out = []
    while parts:
        part = parts.pop(0)
        if len(part) > limit and ' ' in part:
            parts[:0] = _split2(part)      # chia tiếp tới khi mỗi dòng ≤ limit (tiêu đề 6–7 chữ thành 3 dòng)
        else:
            out.append(part)
    return '\n'.join(out)
def f(n, label, name, desc=''):
    return sc('file', n, k=label, name=_wrap(name), desc=desc)
def dt(n, label, date):
    return sc('date', n, day=label, date=date)
def ledger(n, title, rows):
    return sc('ledger', n, title=title, rows=[{'k':a,'v':b,'at':[n,w]} for a,b,w in rows])
def mp(n, name):
    return sc('map', n, geo='china', pins=[{'name':name}])

CH = {}
# Lead 13/11/2026: thẻ file/ledger 40s đầu có bg ảnh minh họa (cổng mở đầu O2/O2b: chữ trên nền trống ≤15%, liên tục ≤3s).
CH['ch00'] = dict(hud={'k':'MỞ ĐẦU','t':'MỘT DANH SÁCH'}, bgm={'mood':'tense','at':0,'gain':0.12}, scenes=[
 dt(None,'GIA KHÁNH NĂM THỨ TƯ','12.02.1799'),
 k(1,'MÙNG TÁM THÁNG GIÊNG','Giêng'), p(2,'qianlong','TRANH CÀN LONG'),
 dict(sc('ledger', 3, title='BỊ ĐƯA VÀO NGỤC', rows=[{'k':'NỘI DUNG','v':'HÒA THÂN','at':3},{'k':'CHI TIẾT','v':'Theo Thanh sử cảo','at':3}]), bg='ai03'),
 p([4,'ghi'],'book','SÁCH CỔ · MINH HỌA'), dict(k(5,'GIAM ĐỂ XÉT HỎI','giam'), at=[5,'ông']),
 dict(f(6,'NGUỒN THỨ CẤP','BẢN GHI KHUYẾT DANH','Ghi chép đời Thanh'), bg='ai01'),
 p(7,'writing','THƯ PHÁP LƯU DUNG · MINH HỌA'),
 dict(ledger(8,'BẢN KÊ',[('VIỆC LÀM','KÊ TỪNG KHOẢN','kê'),('SAU ĐÓ','TÂU DANH SÁCH','tâu')]), bg='ai07'),
 k(9,'MỘT NHÓM NGƯỜI','nhóm'), p(10,'liu','TRANH LƯU DUNG'),
 dict(p(11, 'r82', 'THƯ PHÁP · MINH HỌA'), bg='ai18'),
 mp(12,'Sơn Đông'), k(13,'MỘT KHO BẠC CẦN TRA XÉT','kho'),
])
CH['ch01'] = dict(hud={'k':'CHƯƠNG 01','t':'PHIM KỂ, HỒ SƠ GHI'}, bgm={'mood':'mystery','at':0,'gain':0.12}, scenes=[
 k(0,'MỘT CÁI TÊN QUEN THUỘC','tên'), f(1,'PHIM','TỂ TƯỚNG LƯU GÙ','Nhân vật: Lưu Dung'),
 dt(2,'PHIM · LÊN SÓNG','1996'), ledger(3,'PHIM · VAI DIỄN',[('LÝ BẢO ĐIỀN','LƯU DUNG','Lý'),('VƯƠNG CƯƠNG','HÒA THÂN','Vương')]),
 sc('ledger', 4, title='PHIM · VAI DIỄN', rows=[{'k':'NỘI DUNG','v':'TRƯƠNG QUỐC LẬP','at':4},{'k':'CHI TIẾT','v':'Vai Càn Long','at':4}]),
 k(5,'MỘT BỘ PHIM ĐƯỢC NHỚ','phim'), k(6,'PHIM · NHÂN VẬT LƯNG CÒNG','lưng'),
 p(7, 'r89', 'THƯ PHÁP · MINH HỌA'), k(8,'PHIM · HAI NGƯỜI ĐỐI DIỆN','đối'),
 k(9,'PHIM · NGƯỜI NGAY THẲNG','thẳng'), f(11,'HỒ SƠ','THANH SỬ CẢO','Một đoạn truyện'),
 p(12,'book2','SÁCH CỔ · MINH HỌA'), k(13,'CHỨC VỤ · NĂM THÁNG · SỰ VIỆC','chức'),
 p(14, 'archive66', 'VĂN BẢN CỔ · MINH HỌA'), k(15,'KHÔNG THỂ KẾT LUẬN','không'),
 k(17,'PHIM · HAI ĐỒNG LIÊU','phim'), dt(18,'LƯU DUNG SINH','1720'),
 dt(19,'HÒA THÂN SINH','1750'), sc('counter',20,**{'from':0,'to':30},suffix=' TUỔI',label='LƯU DUNG LỚN HƠN',countAt=[20,'ba']),
 p(22,'liu2','TRANH LƯU DUNG'), k(23,'THEO THỨ TỰ NĂM THÁNG','thứ'),
 f(24,'NGƯỜI CHA','LƯU THỐNG HUÂN','Đại thần triều Thanh'),
 ledger(25,'ĐƯỜNG QUAN',[('BẮT ĐẦU','KỲ THI TIẾN SĨ','thi'),('ĐỨT ĐOẠN','NHÀ NGỤC · ĐI ĐÀY','ngục')]),
 dt(26,'VỤ ÁN VĂN TỰ','1778'), dt(27,'KHO BẠC SƠN ĐÔNG','1782'),
 k(28,'MỘT NGƯỜI TỐ CÁO','tố'), dt(29,'BỊ GIÁNG CHỨC','1789'),
 dt(30,'DANH SÁCH','1799'), k(31,'NHÓM ĐƯỢC GIAO KÊ BIÊN','biên'),
 sc('question',32,text='BIỆT DANH TỪ ĐÂU RA?'), k(33,'SỬ KHÔNG GHI BIỆT DANH','sử'),
 ledger(34,'BA LỚP CÂU CHUYỆN',[('HỒ SƠ','SỬ','sử'),('TRUYỀN MIỆNG','GIAI THOẠI','truyền'),('TÁC PHẨM','PHIM','phim')]),
 k(35,'TRƯỚC HẾT: NGƯỜI CHA','cha'),
])
CH['ch02'] = dict(hud={'k':'CHƯƠNG 02','t':'NGƯỜI CHA'}, bgm={'mood':'quiet','at':0,'gain':0.12}, scenes=[
 f(0,'NGƯỜI CHA','LƯU THỐNG HUÂN','Đại thần triều Càn Long'), k(2,'ĐẠI THẦN TRIỀU CÀN LONG','đại'),
 p(3,'council','TRANH TRIỀU ĐÌNH · MINH HỌA'), k(4,'VIỆC CƠ MẬT CỦA TRIỀU ĐÌNH','mật'),
 k(5,'TIẾP TỤC THĂNG CHỨC','thăng'), p(6, 'plate160', 'TRANH TRIỀU ĐÌNH · MINH HỌA'),
 ledger(7,'HAI BỘ',[('KIÊM COI','BỘ LỄ','Lễ'),('KIÊM COI','BỘ BINH','Binh')]),
 p(8,'court','TRANH TRIỀU THANH · MINH HỌA'), k(9,'LẦN VÀO CHẦU CUỐI','chầu'),
 dt(11,'MÙA ĐÔNG','1773'), p(13,'city','TRANH CUNG ĐÌNH · MINH HỌA'),
 f(14,'THEO THANH SỬ CẢO','NGOÀI CỬA ĐÔNG HOA','Chiếc kiệu hơi nghiêng'),
 k(15,'NGƯỜI TA VÉN MÀN','màn'), k(16,'ÔNG ĐÃ NHẮM MẮT','mắt'),
 sc('counter',17,**{'from':0,'to':73},suffix=' TUỔI',label='LƯU THỐNG HUÂN',countAt=[17,'bảy']),
 k(18,'MẤT TRÊN ĐƯỜNG ĐI CHẦU','mất'), p(19,'gates','TRANH ĐÔ THỊ · MINH HỌA'),
 k(20,'CHIẾC KIỆU NGHIÊNG','kiệu'), k(21,'KHÔNG TỚI BUỔI CHẦU','chầu'),
 p(22,'horse','TRANH CÀN LONG'), k(23,'NHÀ VUA ĐẾN VIẾNG','giản'),
 k(24,'NẾP NHÀ GIẢN DỊ','giản'), f(25,'THANH SỬ CẢO','CỬA CÀN THANH','Nhà vua rơi nước mắt'),
 sc('quote',27,text='Trẫm mất một cánh tay.',by='THANH SỬ CẢO',lbl='TRÍCH DỊCH',qline=27,typeAt=[27,'Trẫm']),
 sc('quote',29,text='Như Thống Huân, mới thật không hổ là bậc tể tướng.',by='THANH SỬ CẢO',lbl='TRÍCH DỊCH',qline=29,typeAt=[29,'Thống']),
 k(30,'LỜI CỦA HOÀNG ĐẾ','hoàng'), p(31, 'court2', 'TRANH TRIỀU ĐÌNH · MINH HỌA'),
 p(32, 'plate160', 'TRANH TRIỀU ĐÌNH · MINH HỌA'), k(33,'CHỮ “THẬT”','thật'),
 k(35,'NGƯỜI CON ĐÃ HƠN NĂM MƯƠI','con'), f(36,'THEO MỘT BÀI VIẾT HIỆN ĐẠI','VỀ CHỊU TANG CHA','Lưu Dung'),
 k(37,'LỜI KHEN DÀNH CHO NGƯỜI CHA','cha'), p(38,'liu3','TRANH LƯU DUNG'),
 ledger(39,'HAI CHA CON',[('NGƯỜI CHA','MỘT BIẾN CỐ','cha'),('NGƯỜI CON','BỊ CUỐN THEO','con')]),
 k(41,'TỪ CHỨC QUAN ĐẾN NHÀ NGỤC','ngục'), p(42, 'qian150', 'TRANH CÀN LONG'),
 k(43,'PHIM · TÊN GẮN VỚI NGƯỜI CON','phim'), sc('question',44,text='CHẶNG ĐƯỜNG NÀO NỐI HAI CÁCH GỌI?'),
])
CH['ch03'] = dict(hud={'k':'CHƯƠNG 03','t':'ĐỖ ĐẠT VÀ TAI HỌA'}, bgm={'mood':'mystery','at':0,'gain':0.12}, scenes=[
 f(0,'TỰ','SÙNG NHƯ','Lưu Dung'), dt(1,'ĐỖ TIẾN SĨ','1751'),
 sc('counter',2,**{'from':0,'to':31},suffix=' TUỔI',label='LƯU DUNG KHI ĐỖ',countAt=[2,'ba']),
 p(3,'exam','TRANH TRƯỜNG THI · MINH HỌA'), p(4,'exam2','TRANH THI CỬ · MINH HỌA'),
 p(5,'exam3','TRANH XEM BẢNG THI · MINH HỌA'), f(6,'HÀN LÂM VIỆN','BIÊN TU','Chức đầu tiên được sử ghi'),
 p(7, 'exam4', 'TRƯỜNG THI · MINH HỌA'),
 ledger(8,'HAI CHA CON',[('CHA','QUÂN CƠ XỨ','cha'),('CON','BIÊN TU → THỊ GIẢNG','con')]),
 k(9,'CÙNG PHỤC VỤ TRIỀU ĐÌNH','phục'),
 p(10, 'gates', 'TRANH ĐÔ THỊ · MINH HỌA'), k(11,'BIẾN CỐ CỦA NGƯỜI CHA','cha'),
 dt(13,'LƯU THỐNG HUÂN BỊ TRỊ TỘI','1755'), k(14,'MIỀN TÂY BẮC · CHUẨN CÁT NHĨ','Chuẩn'),
 k(15,'VĨNH THƯỜNG RÚT QUÂN','rút'), f(16,'NHÀ VUA TRÁCH','LƯU THỐNG HUÂN','Phụ họa Vĩnh Thường'),
 k(17,'TRÁCH NHIỆM VỀ TRIỀU ĐÌNH','trách'), k(18,'SỬ KHÔNG NÊU CỤ THỂ','không'),
 p(19,'liu','TRANH LƯU DUNG'), k(20,'LƯU DUNG BỊ TƯỚC CHỨC','tước'),
 p(21, 'r85', 'THƯ PHÁP · MINH HỌA'), k(22,'NHÀ HỌ LƯU BỊ TỊCH BIÊN','biên'),
 sc('counter',23,**{'from':0,'to':35},suffix=' TUỔI',label='LƯU DUNG NĂM 1755',countAt=[23,'ba']),
 ledger(24,'HỆ QUẢ',[('NGƯỜI CON','MẤT CHỨC · BỊ GIAM','chức'),('GIA SẢN','BỊ TỊCH BIÊN','sản')]),
 p(25,'cells','Ô THI CỬ · MINH HỌA KIẾN TRÚC'), k(26,'TỪ BIÊN TU ĐẾN NHÀ NGỤC','ngục'),
 k(27,'VIỆC ĐƯỢC GIẢI','giải'), f(28,'TRỞ LẠI','BIÊN TU','Sau khi việc được giải'),
 mp(29,'An Huy'), k(30,'ĐỐC HỌC CHÍNH AN HUY','Huy'),
 p(31,'paper','BÀI THI TRIỀU THANH · MINH HỌA'), k(32,'TỪ KỲ THI ĐẾN BIẾN CỐ','thi'),
 k(33,'CHUYỆN KÊ BIÊN SẼ TRỞ LẠI','biên'), dt(34,'NHÀ HỌ LƯU BỊ TỊCH BIÊN','1755'),
])
CH['ch04'] = dict(hud={'k':'CHƯƠNG 04','t':'TRI PHỦ THÁI NGUYÊN'}, bgm={'mood':'tense','at':0,'gain':0.05}, scenes=[
 mp(0,'An Huy'), f(1,'CHỨC VỤ','TRI PHỦ','Quan đứng đầu một phủ'),
 k(2,'GIỮA DÂN VÀ TRIỀU ĐÌNH','dân'), p(3, 'court', 'TRANH TRIỀU ĐÌNH · MINH HỌA'),
 k(4,'CÔNG QUỸ CỦA PHỦ','quỹ'), p(5,'liu2','TRANH LƯU DUNG'),
 mp(6,'Sơn Tây'), dt(7,'THÁI NGUYÊN · THEO NGUỒN HIỆN ĐẠI','1762'),
 sc('counter',8,**{'from':0,'to':42},suffix=' TUỔI',label='LƯU DUNG',countAt=[8,'bốn']),
 k(9,'HƠN MƯỜI NĂM LÀM QUAN','năm'), dt(10,'ĐỖ TIẾN SĨ','1751'),
 k(11,'ĐÃ CÓ MỘT LẦN VÀO NGỤC','ngục'), p(12,'writing2','THƯ PHÁP LƯU DUNG · MINH HỌA'),
 k(13,'THUỘC HẠ BIỂN THỦ CÔNG QUỸ','biển'), k(14,'ÔNG KHÔNG PHÁT HIỆN','phát'),
 ledger(15,'LỖI ĐƯỢC GHI',[('TRI PHỦ','KHÔNG PHÁT HIỆN','phát'),('NGƯỜI DƯỚI QUYỀN','BIỂN THỦ','biển')]),
 k(16,'KHÔNG GHI TÊN HAY SỐ TIỀN','không'), k(17,'HÌNH PHẠT KHÔNG CHỈ DÀNH CHO NGƯỜI LẤY','riêng'),
 f(18,'HỆ QUẢ','NGƯỜI ĐỨNG ĐẦU RỜI CHỨC','Phải đi chịu phạt'), sc('ledger', 19, title='HÌNH PHẠT', rows=[{'k':'NỘI DUNG','v':'PHÁT ĐI QUÂN ĐÀI','at':19},{'k':'CHI TIẾT','v':'Làm việc chuộc lỗi','at':19}]),
 k(20,'LÀM VIỆC CHUỘC LỖI','chuộc'), p(21, 'r89', 'THƯ PHÁP · MINH HỌA'),
 k(22,'ĐƯỜNG QUAN BỊ NGẮT','ngắt'), p(23,'land','TRANH PHONG CẢNH · MINH HỌA'),
 k(24,'KHÔNG CÓ NHẬT KÝ TRONG ĐOẠN SỬ','nhật'), ledger(25,'HAI ĐIỀU CÒN LẠI',[('HÌNH PHẠT','BỊ ĐÀY','hai')]),
 k(26,'CHỊU PHẠT VÌ KHÔNG PHÁT HIỆN','đày'), k(27,'RỒI ĐƯỢC TRỞ VỀ','về'),
 ledger(28,'HAI LẦN ĐỨT ĐOẠN',[('LẦN TRƯỚC','BIẾN CỐ CỦA CHA','cha')]),
 ledger(29,'LẦN SAU',[('THUỘC HẠ','BIỂN THỦ','biển'),('LƯU DUNG','KHÔNG PHÁT HIỆN','phát')]),
 k(30,'HAI SỰ VIỆC KHÁC NHAU','khác'), k(31,'TRỞ VỀ QUAN TRƯỜNG','về'),
 mp(33,'Thiểm Tây'), f(34,'CHỨC VỤ','ÁN SÁT SỨ','Coi việc hình án của tỉnh'),
 k(35,'TỪ NGƯỜI BỊ ĐÀY ĐẾN QUAN XÉT ÁN','án'), p(36, 'archive66', 'VĂN BẢN CỔ · MINH HỌA'),
 k(37,'HAI CHỮ KHO BẠC','bạc'), k(38,'SẼ TRỞ LẠI','lại'),
])
CH['ch05'] = dict(hud={'k':'CHƯƠNG 05','t':'BÀI THƠ NĂM 1778'}, bgm={'mood':'tense','at':0,'gain':0.12}, scenes=[
 dt(0,'CÀN LONG NĂM THỨ 43','1778'), k(1,'MỘT VỤ ÁN VĂN TỰ','án'),
 f(2,'NGUỒN QUA BẢN TRÍCH','ĐÔNG HOA LỤC','Bản sử được trích lại'),
 sc('ledger', 3, title='ĐOẠN TRUYỆN LƯU DUNG', rows=[{'k':'NỘI DUNG','v':'THANH SỬ CẢO','at':3},{'k':'CHI TIẾT','v':'Không kể vụ án này','at':3}]),
 p(4,'official','TRANH QUAN VĂN · MINH HỌA'), sc('ledger', 5, title='NGƯỜI LÀM THƠ', rows=[{'k':'NỘI DUNG','v':'TỪ THUẬT QUỲ','at':5},{'k':'CHI TIẾT','v':'Theo bản trích Đông Hoa lục','at':5}]),
 p(6,'writing3','THƯ PHÁP LƯU DUNG · MINH HỌA'), k(7,'TRIỀU ĐÌNH COI LÀ PHẢN NGHỊCH','nghịch'),
 p(8, 'r104', 'THƯ PHÁP · MINH HỌA'), k(9,'MỘT KẾT CỤC NGHIỆT NGÃ','cục'),
 f(10,'THEO ĐÔNG HOA LỤC','LƯU DUNG','Người tâu việc ấy'), p(11,'writing4','THƯ PHÁP LƯU DUNG · MINH HỌA'),
 k(12,'LỜI GHI NHẬN VIỆC TÂU','tâu'),
 sc('quote',13,text='Bài từ phản nghịch do Từ Thuật Quỳ làm, nếu không nhờ Lưu Dung...',by='ĐÔNG HOA LỤC · BẢN TRÍCH',lbl='TRÍCH DỊCH',qline=13,typeAt=[13,'Bài']),
 sc('quote',[13,'theo'],text='...theo đúng sự thật mà tâu lên, thì suýt đã lọt lưới.',by='ĐÔNG HOA LỤC · BẢN TRÍCH',lbl='TRÍCH DỊCH',qline=13,typeAt=[13,'theo']),
 k(14,'MỘ BỊ QUẬT · THI THỂ BỊ CHÉM','quật'), k(15,'NGƯỜI CHÁU CŨNG BỊ XỬ CHÉM','cháu'),
 f(16,'HỒ SƠ','VỤ ÁN VĂN TỰ','Theo bản trích Đông Hoa lục'),
 k(17,'TỘI NẰM TRONG CHỮ','chữ'), p(18,'writing5','THƯ PHÁP LƯU DUNG · MINH HỌA'),
 k(19,'KẾT CỤC KHÔNG DỪNG Ở NGƯỜI VIẾT','dừng'), k(20,'CẢ NGƯỜI THÂN','thân'),
 p(21, 'r105', 'THƯ PHÁP · MINH HỌA'), k(22,'BẢN SỬ · MỘT VỤ QUẬT MỘ','quật'),
 ledger(23,'HAI LỚP',[('NHÂN VẬT','PHIM XÂY DỰNG','phim'),('SỰ VIỆC','BẢN SỬ GHI','sử')]),
 k(24,'LỜI TÂU VÀ KẾT CỤC','tâu'), k(25,'KHÔNG ĐOÁN ĐỘNG CƠ','động'),
 p(26,'writing6','THƯ PHÁP LƯU DUNG · MINH HỌA'),
 k(27,'QUẬT MỘ · XỬ CHÉM NGƯỜI CHÁU','cháu'), f(28,'ĐÔNG HOA LỤC · BẢN TRÍCH','TÊN LƯU DUNG','Gắn với việc phát hiện bài thơ'),
 k(29,'MỘT PHẦN CỦA HỒ SƠ','phần'), sc('ledger', 30, title='KẾT CỤC', rows=[{'k':'NỘI DUNG','v':'NGƯỜI CHÁU MẤT MẠNG','at':30},{'k':'CHI TIẾT','v':'Theo bản trích','at':30}]),
 k(31,'ĐƯỜNG QUAN TIẾP TỤC','tiếp'),
])
CH['ch06'] = dict(hud={'k':'CHƯƠNG 06','t':'TỪ HỒ NAM ĐẾN ĐÔ SÁT VIỆN'}, bgm={'mood':'mystery','at':0,'gain':0.12}, scenes=[
 sc('ledger', 0, title='KHOẢNG 1776–1780', rows=[{'k':'NỘI DUNG','v':'NỘI CÁC HỌC SĨ','at':0},{'k':'CHI TIẾT','v':'Chức vụ trong kinh','at':0}]),
 sc('ledger', [0,'rồi'], title='CHỨC VỤ TRONG KINH', rows=[{'k':'NỘI DUNG','v':'THỊ LANG','at':[0,'rồi']},{'k':'CHI TIẾT','v':'Bộ Hộ và Bộ Lại','at':[0,'rồi']}]),
 k(1,'CÙNG GIAI ĐOẠN VỤ ÁN BÀI THƠ','thơ'), k(2,'MỘT PHẦN DỰA VÀO NGUỒN HIỆN ĐẠI','nguồn'),
 f(3,'CHỨC VỤ','NỘI CÁC HỌC SĨ','Soạn và chuyển văn bản'),
 p(4, 'court', 'TRANH TRIỀU ĐÌNH · MINH HỌA'),
 ledger(5,'HAI BỘ',[('BỘ HỘ','THUẾ','thuế'),('BỘ LẠI','BỔ NHIỆM QUAN LẠI','nhiệm')]),
 p(6,'robe','TRIỀU PHỤC · MINH HỌA'), dt(7,'LƯU DUNG SÁU MƯƠI TUỔI','1780'),
 mp(8,'Hồ Nam'), f(9,'CHỨC VỤ','TUẦN PHỦ','Quan đứng đầu một tỉnh'),
 k(10,'HỒ NAM · PHÍA NAM HỒ ĐỘNG ĐÌNH','nam'), k(11,'TỪ KINH THÀNH ĐẾN MỘT TỈNH','tỉnh'),
 p(12, 'land', 'TRANH PHONG CẢNH · MINH HỌA'), k(13,'TỪ CAI QUẢN ĐẾN GIÁM SÁT','sát'),
 f(14,'CHỨC VỤ','TẢ ĐÔ NGỰ SỬ','Đứng đầu ngành giám sát'),
 p(15, 'city', 'TRANH CUNG ĐÌNH · MINH HỌA'),
 k(16,'HAI NHIỆM VỤ CÙNG XUẤT HIỆN','hai'), p(17,'writing7','THƯ PHÁP LƯU DUNG · MINH HỌA'),
 dt(18,'TẢ ĐÔ NGỰ SỬ · THEO NGUỒN HIỆN ĐẠI','1781'),
 f(19,'CƠ QUAN','ĐÔ SÁT VIỆN','Giám sát quan lại'), k(20,'NGỰ SỬ CÓ QUYỀN TÂU HẶC','hặc'),
 k(21,'TẢ ĐÔ NGỰ SỬ ĐỨNG ĐẦU','đầu'), p(22,'rooms','TRANH QUAN VĂN · MINH HỌA'),
 ledger(23,'CÁC VỊ TRÍ',[('Ở XA','TUẦN PHỦ','xa'),('Ở GẦN','NAM THƯ PHÒNG','gần'),('GIÁM SÁT','TẢ ĐÔ NGỰ SỬ','giám')]),
 k(24,'SỬ KHÔNG KỂ CHI TIẾT','không'), k(25,'TỪ NHÀ NGỤC ĐẾN VỊ TRÍ GIÁM SÁT','ngục'),
 p(26,'heshen','TRANH HÒA THÂN'), k(27,'MỘT NGỰ SỬ KHÁC KHỞI ĐẦU','ngự'),
 p(28,'writing8','THƯ PHÁP LƯU DUNG · MINH HỌA'), k(29,'MỘT CÁI TÊN SẮP XUẤT HIỆN','tên'),
 k(30,'MỘT NGỰ SỬ','sử'), sc('ledger', 31, title='NGỰ SỬ', rows=[{'k':'NỘI DUNG','v':'TIỀN PHONG','at':31},{'k':'CHI TIẾT','v':'Người khởi đầu cuộc tra xét','at':31}]),
])


TD = '\u0054\u00c1I D\u1ef0NG MINH H\u1eccA'
V = {f'v{i}': f'90000{i}' for i in range(1, 9)}
IMGS.update({f'ai{i:02}': f'EXT:ai:ai_{i:02}' for i in range(1, 19)})
IMGS.update({
 'r37': im(37, 'Pr\u00fcfungszellen'), 'r45': im(45, 'imperial exam winner'),
 'r48': im(48, '国子监'), 'r73': im(73, 'Mid-Autumn'),
 'r74': im(74, 'Boyuan'), 'r82': im(82, 'Kaishu'),
 'r85': im(85, 'LantingXu'), 'r88': im(88, 'Chinesecalligraphy'),  # KHÔNG DÙNG: ảnh hiện đại (người viết thư pháp nước trên vỉa hè), sai bối cảnh nhà Thanh (Lead 13/11)
 'r89': im(89, 'Huang Ting Jing'), 'r90': im(90, 'Shang Yu Tie'),
 'r91': im(91, 'Mi Fei'), 'r92': im(92, 'Wang Xianzhi'),
 'r93': im(93, 'Mi Fu-On Calligraphy'), 'r95': im(95, 'Sunny after Snow'),
 'r100': im(100, 'Wen Zhengming'), 'r103': im(103, 'Hongyinshanfang'),
 'r104': im(104, 'chengzisizhen'), 'r105': im(105, 'Running script'),
 'r115': im(115, '珊瑚帖'), 'r116': im(116, '珊瑚帖'),
 'r117': im(117, '劉石菴'), 'r118': im(118, '劉石菴'),
})
NEN = {
 'ho_so': ['ai01','ai07','ai18','r73','r74','r82','r85','r89','r90','r91','r92','r93','r95','r100','r103','r104','r105','r115','r116','r117','r118'],
 'trieu': ['ai14','ai02','r48','ai05','ai01','ai07','r73','r74','r82','r85','r89','r90','r91','r92','r93','r95','r100'],
 'phim': ['ai17','ai01','ai08','r73','r74','r82','r85','r89','r90','r91','r92','r93','r95','r100','r103','r104','r105'],
 'nguc': ['ai03','ai06','ai02','ai01','r73','r74','r82','r85','r89','r90','r91','r92'],
 'thi': ['ai04','r37','r45','r48','ai01','r73','r74','r82','r85','r89','r90','r91'],
 'cua_cai': ['ai11','ai07','ai02','ai01','r73','r74','r82','r85','r89','r90'],
 'duong': ['ai12','ai06','ai05','ai10','ai01','r73','r74','r82','r85','r89','r90','r91'],
 'tho': ['ai08','ai18','ai01','r73','r74','r82','r85','r89','r90','r91','r92','r93','r95','r100','r103','r104','r105','r115','r116','r117','r118'],
 'tang': ['ai15','ai09','ai02','ai01','r73','r74','r82','r85','r89','r90','r91'],
 'thu_phong': ['ai13','ai01','ai18','ai07','r73','r74','r82','r85','r89','r90','r91','r92','r93'],
}
BANG_NEN = {
 'ch00': {'trieu':[1], 'cua_cai':[13]},
 'ch01': {'phim':[0,2,5,6,8,9,15], 'ho_so':[12,14,16,17,18,20,23,24,25,26,27,28,29,30,32]},
 'ch02': {'trieu':[1,3,4,8], 'tang':[9,12,13,14,15,17,18,20,21,23,24,25,28,29,31], 'nguc':[34], 'phim':[36,37]},
 'ch03': {'thi':[1,2,31], 'trieu':[9,11,12,17,19,26,29], 'duong':[13,14,16], 'cua_cai':[21,32,33], 'nguc':[25]},
 'ch04': {'trieu':[2,7,8,9,10,14,16,17,22,30,31], 'nguc':[11,20,26,27], 'cua_cai':[4,13,34,36,37], 'ho_so':[24]},
 'ch05': {'tho':[0,1,7,12,13,14,18,23,25,30,32], 'tang':[9,15,16,20,21,28], 'ho_so':[26]},
 'ch06': {'ho_so':[2,3,25], 'trieu':[8,12,14,17,19,21,22,28,30,31], 'duong':[11,26]},
 'ch07': {'trieu':[4,5,19,21,24,27,36,38,40,43], 'cua_cai':[10,12,13,16,17,26], 'ho_so':[29]},
 'ch08': {'trieu':[0,9,12,15,16,19,21,25,28,29,32,37], 'thu_phong':[4,6,8,11,36], 'nguc':[33]},
 'ch09': {'trieu':[3,4,8,9,13,14,15,16,19,29,30,31], 'ho_so':[7,23,25]},
 'ch10': {'tang':[0,8,24,26,28,29], 'trieu':[2,6,20,21,22,31], 'cua_cai':[10,13,14], 'ho_so':[18,34,35,37,39]},
 'ch11': {'ho_so':[1,3,5,8,11,22,24], 'phim':[13,15,17,19,20]},
 'ch12': {'tho':[0,2,8,11,32], 'ho_so':[16,17,22,23,25,27], 'tang':[20]},
 'ch13': {'tho':[0,10,25,27,29,30,32,38], 'tang':[2,13], 'phim':[4,5,9,14,15,17,20,21,31,40], 'cua_cai':[35,36]},
}
BANG_CLIP = {
 'ch00': {0:'v3',5:'v8',9:'v7'},
 'ch01': {0:'v1',12:'v7',30:'v4'},
 'ch02': {8:'v3',18:'v1',34:'v8'},
 'ch03': {9:'v7',21:'v5',25:'v8'},
 'ch04': {2:'v1',11:'v8',24:'v2'},
 'ch05': {1:'v4',12:'v7',23:'v2'},
 'ch06': {11:'v6',14:'v1',26:'v8'},
 'ch07': {5:'v1',16:'v7',29:'v2'},
 'ch08': {4:'v7',8:'v2'},
 'ch09': {13:'v1',25:'v4',29:'v3'},
 'ch10': {0:'v2',10:'v5',20:'v7',29:'v8'},
 'ch11': {3:'v4',11:'v2',24:'v7'},
 'ch12': {11:'v4',20:'v3',32:'v2'},
 'ch13': {2:'v3',27:'v4',35:'v5'},
}

for _nen in NEN.values():
    _nen.extend(x for x in ['r103','r104','r105','r115','r116','r117','r118','paper','book','book2','page','writing','writing2','writing3','writing4','writing5','writing6','writing7','writing8','call111','call119','call120','call126','call127'] if x not in _nen)

def gan_tu_lieu():
    from collections import Counter
    used = Counter()
    clip_ch = {}
    for chapter, group in BANG_NEN.items():
        scenes = CH[chapter]['scenes']
        mapping = {}
        for kind, indexes in group.items():
            for index in indexes:
                if index in mapping: raise ValueError(f'duplicate {chapter} {index}')
                mapping[index] = kind
        for index in BANG_CLIP.get(chapter, {}):
            mapping.setdefault(index, 'ho_so')
        for index, kind in sorted(mapping.items()):
            scene = scenes[index]
            if scene['type'] not in ('kinetic','slam','date','counter','question','quote') or any(scene.get(k) for k in ('bg','img','vid')):
                raise ValueError(f'bad scene {chapter} {index} {scene}')
            v = BANG_CLIP.get(chapter, {}).get(index)
            if v and (v not in clip_ch or int(chapter[2:]) - clip_ch[v] >= 2):
                clip_ch[v] = int(chapter[2:])
                used[v] += 1
                if used[v] > 8: raise ValueError(f'clip limit {v}')
                scene.update(vid=V[v], illus=TD)   # minh_hoa_chung: ghi ở json clip (ai_generated), engine không đọc tags
                continue
            choices = NEN[kind]
            available = [x for x in choices if used[x] < (6 if x.startswith('ai') else 4)]
            if not available: raise ValueError(f'no background {chapter} {index} {kind}')
            img = min(available, key=lambda x: (used[x], choices.index(x)))
            used[img] += 1
            scene['bg'] = img
            if img.startswith('ai'):
                scene.update(credit=False, illus=TD)
            else:
                scene['illus'] = 'T\u01af LI\u1ec6U \u00b7 MINH H\u1eccA'
    return used

# Spec tạo ở phần A chỉ có ch00–ch06; danh sách chương và tên chương luôn lấy theo CH (14 chương).
CHAPTER_TITLES = ['MỘT DANH SÁCH','PHIM KỂ, HỒ SƠ GHI','NGƯỜI CHA','ĐỖ ĐẠT VÀ TAI HỌA','TRI PHỦ THÁI NGUYÊN',
                  'BÀI THƠ NĂM 1778','TỪ HỒ NAM ĐẾN ĐÔ SÁT VIỆN','SƠN ĐÔNG, NĂM 1782','BỊ GIÁNG, NĂM 1789',
                  'THƯỢNG THƯ, ĐẠI HỌC SĨ','THÁNG HAI NĂM 1799','BIỆT DANH: SỬ, GIAI THOẠI, PHIM',
                  'THƯ PHÁP VÀ CUỐI ĐỜI','CHỮ TỂ TƯỚNG']


if __name__ == '__main__':
    sys.modules['gen_scenes'] = sys.modules[__name__]
    other = D / 'gen_scenes2.py'
    if other.exists():
        module_spec = importlib.util.spec_from_file_location('gen_scenes2', other)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        CH.update(module.CH)
    gan_tu_lieu()
    # GH-307: keep original indices through media assignment; then merge and retime.
    adjustments = {'ch00': {'move': {}, 'remove': []},
 'ch01': {'move': {'21': [24, 'tiên'],
                   '20': [23, 'đi'],
                   '12': [13, 'chức'],
                   '11': [12, 'cho'],
                   '2': [2, 'truyền']},
          'remove': []},
 'ch02': {'move': {'30': [36, 'Theo'],
                   '20': [23, 'nếp'],
                   '17': [20, 'kiệu'],
                   '16': [19, 'vào'],
                   '15': [18, 'đường']},
          'remove': [13]},
 'ch03': {'move': {'29': [30, 'trở'],
                   '28': [29, 'ở'],
                   '27': [28, 'biên'],
                   '23': [24, 'cha'],
                   '22': [23, 'ấy'],
                   '16': [17, 'loạn'],
                   '15': [16, 'Huân'],
                   '7': [7, 'lên'],
                   '6': [6, 'vào'],
                   '3': [3, 'qua'],
                   '1': [1, 'Năm']},
          'remove': [19]},
 'ch04': {'move': {'28': [28, 'biến'],
                   '24': [24, 'Không'],
                   '22': [22, 'lần'],
                   '21': [21, 'Sau'],
                   '20': [20, 'phát'],
                   '15': [15, 'cho'],
                   '14': [14, 'không'],
                   '12': [12, 'việc'],
                   '11': [11, 'ông'],
                   '10': [10, 'tới'],
                   '9': [9, 'mười'],
                   '6': [6, 'Theo'],
                   '3': [3, 'máy'],
                   '2': [2, 'phủ']},
          'remove': [26, 36]},
 'ch05': {'move': {'22': [21, 'Lưu'],
                   '21': [20, 'người'],
                   '18': [17, 'có'],
                   '14': [13, 'đúng'],
                   '13': [13, 'nghịch'],
                   '12': [12, 'công'],
                   '11': [11, 'lục'],
                   '6': [6, 'thơ']},
          'remove': [7]},
 'ch06': {'move': {'23': [22, 'thư'],
                   '12': [11, 'một'],
                   '11': [10, 'phía'],
                   '10': [9, 'phủ'],
                   '6': [5, 'Ông']},
          'remove': [31]},
 'ch07': {'move': {'42': [43, 'ông'],
                   '41': [42, 'đi'],
                   '40': [41, 'đến'],
                   '39': [40, 'biện'],
                   '38': [39, 'quyền'],
                   '37': [38, 'tổng'],
                   '36': [37, 'được'],
                   '31': [31, 'kia'],
                   '30': [31, 'kể'],
                   '28': [28, 'Có'],
                   '27': [27, 'là'],
                   '26': [26, 'kho'],
                   '24': [24, 'lệnh'],
                   '22': [22, 'của'],
                   '17': [15, 'ra'],
                   '14': [12, 'quán'],
                   '13': [11, 'thiếu'],
                   '8': [6, 'sử'],
                   '4': [2, 'thả'],
                   '3': [1, 'Giản']},
          'remove': [1, 5, 10, 15]},
 'ch08': {'move': {'28': [28, 'hình'],
                   '26': [26, 'Hiệp'],
                   '25': [25, 'không'],
                   '24': [24, 'hoàng'],
                   '23': [23, 'bạc'],
                   '19': [19, 'thứ'],
                   '18': [18, 'bị'],
                   '11': [11, 'lâu'],
                   '6': [6, 'thế'],
                   '5': [5, 'đứng']},
          'remove': [12, 16, 37]},
 'ch09': {'move': {'31': [30, 'ra'],
                   '26': [26, 'tiến'],
                   '18': [18, 'cảo'],
                   '17': [17, 'đế'],
                   '16': [16, 'triều'],
                   '12': [12, 'Hai'],
                   '11': [11, 'học']},
          'remove': [30]},
 'ch10': {'move': {'36': [36, 'khuyết'],
                   '35': [35, 'một'],
                   '34': [34, 'tờ'],
                   '33': [33, 'được'],
                   '30': [30, 'do'],
                   '29': [29, 'cho'],
                   '28': [28, 'không'],
                   '27': [27, 'do'],
                   '26': [26, 'cách'],
                   '23': [23, 'Cũng'],
                   '16': [16, 'bằng'],
                   '12': [12, 'có'],
                   '11': [11, 'giao'],
                   '4': [4, 'tên'],
                   '2': [2, 'đế']},
          'remove': [21, 31]},
 'ch11': {'move': {'24': [23, 'không'],
                   '23': [22, 'là'],
                   '19': [18, 'hiện'],
                   '18': [17, 'ấy'],
                   '16': [15, 'tiết'],
                   '14': [13, 'phim'],
                   '13': [12, 'lấy']},
          'remove': []},
 'ch12': {'move': {'27': [27, 'Văn'],
                   '26': [26, 'cho'],
                   '25': [25, 'Cho'],
                   '22': [22, 'Chạp'],
                   '13': [13, 'câu'],
                   '12': [12, 'được']},
          'remove': []},
 'ch13': {'move': {'40': [39, 'phim'],
                   '36': [35, 'thành'],
                   '34': [34, 'tháng'],
                   '33': [33, 'không'],
                   '32': [32, 'gì'],
                   '31': [31, 'lấp'],
                   '28': [28, 'còn'],
                   '26': [26, 'này'],
                   '25': [25, 'thấy'],
                   '23': [23, 'dễ'],
                   '22': [22, 'trí'],
                   '21': [21, 'lưng'],
                   '20': [20, 'đưa'],
                   '14': [14, 'Phim'],
                   '8': [8, 'là'],
                   '5': [5, 'phát'],
                   '4': [4, 'Tể'],
                   '3': [3, 'tên'],
                   '2': [2, 'bên'],
                   '1': [1, 'tướng']},
          'remove': []}}
    for chapter, edit in adjustments.items():
        scenes = CH[chapter]["scenes"]
        for index, at in edit["move"].items():
            scenes[int(index)]["at"] = at
        CH[chapter]["scenes"] = [scene for index, scene in enumerate(scenes) if index not in edit["remove"]]
    used = set()
    def collect(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ('img','bg') and isinstance(value, str): used.add(value)
                collect(value)
        elif isinstance(obj, list):
            for value in obj: collect(value)
    collect(CH)
    spec_path = D / 'spec.json'
    if not spec_path.exists():
        base = {'title':'TỂ TƯỚNG LƯU GÙ Ngoài Đời Thật: Lưu Dung', 'channel':'CL',
                'accent':'#7f9e91', 'look':'jade', 'theme':'noir', 'autoTr':True,
                'master':True, 'craft':True, 'endcard':9, 'endcardSub':'HỒ SƠ TIẾP THEO',
                'acc':['lưu dung','lưu thống huân','hòa thân'], 'say':{},
                'chapters':list(CH),
                'youtube':{'titles':['TỂ TƯỚNG LƯU GÙ Ngoài Đời Thật: Lưu Dung'],
                 'summary':'Hồ sơ Lưu Dung qua sử liệu và hình tượng trên màn ảnh.',
                 'more':[], 'sources':['https://zh.wikisource.org/wiki/清史稿/卷302',
                    'https://zh.wikisource.org/wiki/清史稿/卷319',
                    'https://zh.wikisource.org/wiki/清史稿/卷16',
                    'https://zh.wikipedia.org/wiki/劉墉_(清朝)',
                    'https://zh.wikipedia.org/wiki/和珅',
                    'https://zh.wikisource.org/zh-hant/殛珅誌略',
                    'https://zh.wikipedia.org/wiki/宰相刘罗锅',
                    'https://zh.wikipedia.org/wiki/刘统勋',
                    'https://zh.wikisource.org/wiki/清史稿/卷301'],
                 'tags':['lưu dung','lưu gù','nhà thanh'], 'hashtags':['LuuDung','HoSo'],
                 'category':'24', 'thumb':'t1.jpg',
                 'chapter_titles':['MỘT DANH SÁCH','PHIM KỂ, HỒ SƠ GHI','NGƯỜI CHA',
                    'ĐỖ ĐẠT VÀ TAI HỌA','TRI PHỦ THÁI NGUYÊN','BÀI THƠ NĂM 1778',
                    'TỪ HỒ NAM ĐẾN ĐÔ SÁT VIỆN'], 'video_credits':[]}}
        spec_path.write_text(json.dumps(base, ensure_ascii=False, indent=1)+'\n', encoding='utf-8')
    # Lead 13/11 (cổng nhịp cảnh build_long.late_first): phần tử con thứ hai phải hiện <= 1s sau đầu cảnh,
    # nên mọi phần tử con neo theo mốc của chính cảnh; counter đếm ngay (bỏ countAt).
    KIDS = {'ledger': 'rows', 'timeline': 'items', 'file': 'rows', 'map': 'pins', 'org': 'nodes'}
    for chapter in CH.values():
        for scene in chapter['scenes']:
            field = KIDS.get(scene.get('type'))
            if field:
                for kid in scene.get(field) or []:
                    if isinstance(kid, dict) and 'at' in kid:
                        kid['at'] = scene['at']
            if scene.get('type') == 'split':
                for side in ('a', 'b'):
                    if isinstance(scene.get(side), dict) and 'at' in scene[side]:
                        scene[side]['at'] = scene['at']
            if scene.get('type') == 'counter':
                scene.pop('countAt', None)
    write(__file__, CH, {key:value for key,value in IMGS.items() if key in used}, GEO, endcardBg='liu')
    path = D / 'spec.json'
    spec = json.loads(path.read_text(encoding='utf-8'))
    # Lead 13/11: cổng mức nhạc (final) — nhạc dưới giọng 21–27 dB > 18 dB; nâng chung + giảm nén, ch04/ch07 (tense) hạ riêng.
    spec['mix_levels'] = {'CL': {'gain': 0.45, 'threshold': 0.08, 'ratio': 3.0}}
    # Lead 13/11: thông tin đăng. Chủ kênh 12/11: "schedule upload thi xong cu up, ko doi" -> slot CL kế tiếp (Thứ Ba 21:00 VN).
    spec['approved'] = '12/11/2026 — schedule upload thi xong cu up, ko doi'
    spec.setdefault('youtube', {}).update({'publish_at': '2026-11-17T14:00:00Z', 'playlist': 'Ngoài Đời Thật', 'thumb': 't2.jpg',
        'video_credits': ["状元卷.JPG — 三猎 — CC BY-SA 4.0 — https://commons.wikimedia.org/wiki/File:%E7%8A%B6%E5%85%83%E5%8D%B7.JPG", "Prüfungszellen-Nanking.jpg — Wikimedia Commons — CC BY-SA 3.0 — https://commons.wikimedia.org/wiki/File:Pr%C3%BCfungszellen-Nanking.jpg", "Quanzhou Museum - imperial exam winner boards - DSCF8225.JPG — User:Vmenkov — CC BY-SA 3.0 — https://commons.wikimedia.org/wiki/File:Quanzhou_Museum_-_imperial_exam_winner_boards_-_DSCF8225.JPG", "北京国子监.JPG — WU Yuchen — CC BY-SA 3.0 — https://commons.wikimedia.org/wiki/File:%E5%8C%97%E4%BA%AC%E5%9B%BD%E5%AD%90%E7%9B%91.JPG", "Liu Yong Hongyinshanfang board.JPG — Gisling — CC BY-SA 4.0 — https://commons.wikimedia.org/wiki/File:Liu_Yong_Hongyinshanfang_board.JPG", "Liu Yong chengzisizhen board.JPG — Gisling — CC BY-SA 4.0 — https://commons.wikimedia.org/wiki/File:Liu_Yong_chengzisizhen_board.JPG", "Running script of Liu Yong.jpg — AlexHe34 — CC BY-SA 3.0 — https://commons.wikimedia.org/wiki/File:Running_script_of_Liu_Yong.jpg", "刘墉临 米芾《珊瑚帖》之一.jpg — 陳寅恪 — CC BY-SA 4.0 — https://commons.wikimedia.org/wiki/File:%E5%88%98%E5%A2%89%E4%B8%B4_%E7%B1%B3%E8%8A%BE%E3%80%8A%E7%8F%8A%E7%91%9A%E5%B8%96%E3%80%8B%E4%B9%8B%E4%B8%80.jpg", "刘墉临 米芾《珊瑚帖》之二.jpg — 陳寅恪 — CC BY-SA 4.0 — https://commons.wikimedia.org/wiki/File:%E5%88%98%E5%A2%89%E4%B8%B4_%E7%B1%B3%E8%8A%BE%E3%80%8A%E7%8F%8A%E7%91%9A%E5%B8%96%E3%80%8B%E4%B9%8B%E4%BA%8C.jpg", "劉石菴1.png — 陳寅恪 — CC BY-SA 4.0 — https://commons.wikimedia.org/wiki/File:%E5%8A%89%E7%9F%B3%E8%8F%B41.png", "劉石菴2.png — 陳寅恪 — CC BY-SA 4.0 — https://commons.wikimedia.org/wiki/File:%E5%8A%89%E7%9F%B3%E8%8F%B42.png", "Ảnh và clip minh họa không người, không chữ: tạo bằng AI, ghi chú \"TÁI DỰNG MINH HỌA\" trên hình."]})
    spec.update({'title':'TỂ TƯỚNG LƯU GÙ Ngoài Đời Thật: Lưu Dung','channel':'CL','theme':'noir','look':'jade',
                 'acc':['lưu dung','lưu thống huân','hòa thân'], 'say':{}, 'chapters':list(CH)})
    spec.setdefault('youtube', {})['chapter_titles'] = CHAPTER_TITLES
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=1)+'\n', encoding='utf-8')
