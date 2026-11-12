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
def f(n, label, name, desc=''):
    return sc('file', n, k=label, name=name, desc=desc)
def dt(n, label, date):
    return sc('date', n, day=label, date=date)
def ledger(n, title, rows):
    return sc('ledger', n, title=title, rows=[{'k':a,'v':b,'at':[n,w]} for a,b,w in rows])
def mp(n, name):
    return sc('map', n, geo='china', pins=[{'name':name}])

CH = {}
CH['ch00'] = dict(hud={'k':'MỞ ĐẦU','t':'MỘT DANH SÁCH'}, bgm={'mood':'tense','at':0,'gain':0.12}, scenes=[
 dt(None,'GIA KHÁNH NĂM THỨ TƯ','12.02.1799'),
 k(1,'MÙNG TÁM THÁNG GIÊNG','Giêng'), p(2,'qianlong','TRANH CÀN LONG'),
 f(3,'BỊ ĐƯA VÀO NGỤC','HÒA THÂN','Theo Thanh sử cảo'),
 p(4,'book','SÁCH CỔ · MINH HỌA'), k(5,'GIAM ĐỂ XÉT HỎI','giam'),
 f(6,'NGUỒN THỨ CẤP','BẢN GHI KHUYẾT DANH','Ghi chép đời Thanh'),
 p(7,'writing','THƯ PHÁP LƯU DUNG · MINH HỌA'),
 ledger(8,'BẢN KÊ',[('VIỆC LÀM','KÊ TỪNG KHOẢN','kê'),('SAU ĐÓ','TÂU DANH SÁCH','tâu')]),
 k(9,'MỘT NHÓM NGƯỜI','nhóm'), p(10,'liu','TRANH LƯU DUNG'),
 f(11,'TUỔI THEO CÁCH TÍNH XƯA','TÁM MƯƠI TUỔI','Lưu Dung'),
 mp(12,'Sơn Đông'), k(13,'MỘT KHO BẠC CẦN TRA XÉT','kho'),
])
CH['ch01'] = dict(hud={'k':'CHƯƠNG 01','t':'PHIM KỂ, HỒ SƠ GHI'}, bgm={'mood':'mystery','at':0,'gain':0.12}, scenes=[
 k(0,'MỘT CÁI TÊN QUEN THUỘC','tên'), f(1,'PHIM','TỂ TƯỚNG LƯU GÙ','Nhân vật: Lưu Dung'),
 dt(2,'PHIM · LÊN SÓNG','1996'), ledger(3,'PHIM · VAI DIỄN',[('LÝ BẢO ĐIỀN','LƯU DUNG','Lý'),('VƯƠNG CƯƠNG','HÒA THÂN','Vương')]),
 f(4,'PHIM · VAI DIỄN','TRƯƠNG QUỐC LẬP','Vai Càn Long'),
 k(5,'MỘT BỘ PHIM ĐƯỢC NHỚ','phim'), k(6,'PHIM · NHÂN VẬT LƯNG CÒNG','lưng'),
 f(7,'PHIM · NHÂN VẬT','LÃO QUAN LƯNG CÒNG','Lưu Dung trên màn ảnh'), k(8,'PHIM · HAI NGƯỜI ĐỐI DIỆN','đối'),
 k(9,'PHIM · NGƯỜI NGAY THẲNG','thẳng'), f(11,'HỒ SƠ','THANH SỬ CẢO','Một đoạn truyện'),
 p(12,'book2','SÁCH CỔ · MINH HỌA'), k(13,'CHỨC VỤ · NĂM THÁNG · SỰ VIỆC','chức'),
 f(14,'THANH SỬ CẢO','KHÔNG MÔ TẢ DÁNG NGƯỜI','Không có chi tiết về cái lưng'), k(15,'KHÔNG THỂ KẾT LUẬN','không'),
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
 k(5,'TIẾP TỤC THĂNG CHỨC','thăng'), f(6,'CHỨC VỤ','ĐÔNG CÁC ĐẠI HỌC SĨ','Càn Long năm thứ 26'),
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
 k(30,'LỜI CỦA HOÀNG ĐẾ','hoàng'), f(31,'CÁCH GỌI','TỂ TƯỚNG','Không phải chức chính thức của triều Thanh'),
 f(32,'CÁCH GỌI','ĐẠI THẦN ĐỨNG ĐẦU','Ý nghĩa chữ tể tướng'), k(33,'CHỮ “THẬT”','thật'),
 k(35,'NGƯỜI CON ĐÃ HƠN NĂM MƯƠI','con'), f(36,'THEO MỘT BÀI VIẾT HIỆN ĐẠI','VỀ CHỊU TANG CHA','Lưu Dung'),
 k(37,'LỜI KHEN DÀNH CHO NGƯỜI CHA','cha'), p(38,'liu3','TRANH LƯU DUNG'),
 ledger(39,'HAI CHA CON',[('NGƯỜI CHA','MỘT BIẾN CỐ','cha'),('NGƯỜI CON','BỊ CUỐN THEO','con')]),
 k(41,'TỪ CHỨC QUAN ĐẾN NHÀ NGỤC','ngục'), f(42,'LỜI KHEN','TỂ TƯỚNG THẬT','Dành cho người cha'),
 k(43,'PHIM · TÊN GẮN VỚI NGƯỜI CON','phim'), sc('question',44,text='CHẶNG ĐƯỜNG NÀO NỐI HAI CÁCH GỌI?'),
])
CH['ch03'] = dict(hud={'k':'CHƯƠNG 03','t':'ĐỖ ĐẠT VÀ TAI HỌA'}, bgm={'mood':'mystery','at':0,'gain':0.12}, scenes=[
 f(0,'TỰ','SÙNG NHƯ','Lưu Dung'), dt(1,'ĐỖ TIẾN SĨ','1751'),
 sc('counter',2,**{'from':0,'to':31},suffix=' TUỔI',label='LƯU DUNG KHI ĐỖ',countAt=[2,'ba']),
 p(3,'exam','TRANH TRƯỜNG THI · MINH HỌA'), p(4,'exam2','TRANH THI CỬ · MINH HỌA'),
 p(5,'exam3','TRANH XEM BẢNG THI · MINH HỌA'), f(6,'HÀN LÂM VIỆN','BIÊN TU','Chức đầu tiên được sử ghi'),
 f(7,'HÀN LÂM VIỆN','THỊ GIẢNG','Chức giảng sách'),
 ledger(8,'HAI CHA CON',[('CHA','QUÂN CƠ XỨ','cha'),('CON','BIÊN TU → THỊ GIẢNG','con')]),
 k(9,'CÙNG PHỤC VỤ TRIỀU ĐÌNH','phục'),
 f(10,'HAI CON ĐƯỜNG','CƠ MẬT · THI CỬ','Hai vị trí trong triều'), k(11,'BIẾN CỐ CỦA NGƯỜI CHA','cha'),
 dt(13,'LƯU THỐNG HUÂN BỊ TRỊ TỘI','1755'), k(14,'MIỀN TÂY BẮC · CHUẨN CÁT NHĨ','Chuẩn'),
 k(15,'VĨNH THƯỜNG RÚT QUÂN','rút'), f(16,'NHÀ VUA TRÁCH','LƯU THỐNG HUÂN','Phụ họa Vĩnh Thường'),
 k(17,'TRÁCH NHIỆM VỀ TRIỀU ĐÌNH','trách'), k(18,'SỬ KHÔNG NÊU CỤ THỂ','không'),
 p(19,'liu','TRANH LƯU DUNG'), k(20,'LƯU DUNG BỊ TƯỚC CHỨC','tước'),
 f(21,'BỘ HÌNH','LƯU DUNG VÀ ANH EM Ở KINH','Bị đưa vào ngục'), k(22,'NHÀ HỌ LƯU BỊ TỊCH BIÊN','biên'),
 sc('counter',23,**{'from':0,'to':35},suffix=' TUỔI',label='LƯU DUNG NĂM 1755',countAt=[23,'ba']),
 ledger(24,'HỆ QUẢ',[('NGƯỜI CON','MẤT CHỨC · BỊ GIAM','chức'),('GIA SẢN','BỊ TỊCH BIÊN','sản')]),
 p(25,'cells','Ô THI CỬ · MINH HỌA KIẾN TRÚC'), k(26,'TỪ BIÊN TU ĐẾN NHÀ NGỤC','ngục'),
 k(27,'VIỆC ĐƯỢC GIẢI','giải'), f(28,'TRỞ LẠI','BIÊN TU','Sau khi việc được giải'),
 mp(29,'An Huy'), k(30,'ĐỐC HỌC CHÍNH AN HUY','Huy'),
 p(31,'paper','BÀI THI TRIỀU THANH · MINH HỌA'), k(32,'TỪ KỲ THI ĐẾN BIẾN CỐ','thi'),
 k(33,'CHUYỆN KÊ BIÊN SẼ TRỞ LẠI','biên'), dt(34,'NHÀ HỌ LƯU BỊ TỊCH BIÊN','1755'),
])
CH['ch04'] = dict(hud={'k':'CHƯƠNG 04','t':'TRI PHỦ THÁI NGUYÊN'}, bgm={'mood':'tense','at':0,'gain':0.12}, scenes=[
 mp(0,'An Huy'), f(1,'CHỨC VỤ','TRI PHỦ','Quan đứng đầu một phủ'),
 k(2,'GIỮA DÂN VÀ TRIỀU ĐÌNH','dân'), f(3,'BỘ MÁY PHỦ','NGƯỜI DƯỚI QUYỀN','Làm việc dưới quyền tri phủ'),
 k(4,'CÔNG QUỸ CỦA PHỦ','quỹ'), p(5,'liu2','TRANH LƯU DUNG'),
 mp(6,'Sơn Tây'), dt(7,'THÁI NGUYÊN · THEO NGUỒN HIỆN ĐẠI','1762'),
 sc('counter',8,**{'from':0,'to':42},suffix=' TUỔI',label='LƯU DUNG',countAt=[8,'bốn']),
 k(9,'HƠN MƯỜI NĂM LÀM QUAN','năm'), dt(10,'ĐỖ TIẾN SĨ','1751'),
 k(11,'ĐÃ CÓ MỘT LẦN VÀO NGỤC','ngục'), p(12,'writing2','THƯ PHÁP LƯU DUNG · MINH HỌA'),
 k(13,'THUỘC HẠ BIỂN THỦ CÔNG QUỸ','biển'), k(14,'ÔNG KHÔNG PHÁT HIỆN','phát'),
 ledger(15,'LỖI ĐƯỢC GHI',[('TRI PHỦ','KHÔNG PHÁT HIỆN','phát'),('NGƯỜI DƯỚI QUYỀN','BIỂN THỦ','biển')]),
 k(16,'KHÔNG GHI TÊN HAY SỐ TIỀN','không'), k(17,'HÌNH PHẠT KHÔNG CHỈ DÀNH CHO NGƯỜI LẤY','riêng'),
 f(18,'HỆ QUẢ','NGƯỜI ĐỨNG ĐẦU RỜI CHỨC','Phải đi chịu phạt'), f(19,'HÌNH PHẠT','PHÁT ĐI QUÂN ĐÀI','Làm việc chuộc lỗi'),
 k(20,'LÀM VIỆC CHUỘC LỖI','chuộc'), f(21,'SAU HƠN MỘT NĂM','ĐƯỢC THA','Trở về quan trường'),
 k(22,'ĐƯỜNG QUAN BỊ NGẮT','ngắt'), p(23,'land','TRANH PHONG CẢNH · MINH HỌA'),
 k(24,'KHÔNG CÓ NHẬT KÝ TRONG ĐOẠN SỬ','nhật'), ledger(25,'HAI ĐIỀU CÒN LẠI',[('HÌNH PHẠT','BỊ ĐÀY','hai')]),
 k(26,'CHỊU PHẠT VÌ KHÔNG PHÁT HIỆN','đày'), k(27,'RỒI ĐƯỢC TRỞ VỀ','về'),
 ledger(28,'HAI LẦN ĐỨT ĐOẠN',[('LẦN TRƯỚC','BIẾN CỐ CỦA CHA','cha')]),
 ledger(29,'LẦN SAU',[('THUỘC HẠ','BIỂN THỦ','biển'),('LƯU DUNG','KHÔNG PHÁT HIỆN','phát')]),
 k(30,'HAI SỰ VIỆC KHÁC NHAU','khác'), k(31,'TRỞ VỀ QUAN TRƯỜNG','về'),
 mp(33,'Thiểm Tây'), f(34,'CHỨC VỤ','ÁN SÁT SỨ','Coi việc hình án của tỉnh'),
 k(35,'TỪ NGƯỜI BỊ ĐÀY ĐẾN QUAN XÉT ÁN','án'), f(36,'THANH SỬ CẢO','KHÔNG BÌNH THÊM','Đoạn truyện Lưu Dung'),
 k(37,'HAI CHỮ KHO BẠC','bạc'), k(38,'SẼ TRỞ LẠI','lại'),
])
CH['ch05'] = dict(hud={'k':'CHƯƠNG 05','t':'BÀI THƠ NĂM 1778'}, bgm={'mood':'tense','at':0,'gain':0.12}, scenes=[
 dt(0,'CÀN LONG NĂM THỨ 43','1778'), k(1,'MỘT VỤ ÁN VĂN TỰ','án'),
 f(2,'NGUỒN QUA BẢN TRÍCH','ĐÔNG HOA LỤC','Bản sử được trích lại'),
 f(3,'ĐOẠN TRUYỆN LƯU DUNG','THANH SỬ CẢO','Không kể vụ án này'),
 p(4,'official','TRANH QUAN VĂN · MINH HỌA'), f(5,'NGƯỜI LÀM THƠ','TỪ THUẬT QUỲ','Theo bản trích Đông Hoa lục'),
 p(6,'writing3','THƯ PHÁP LƯU DUNG · MINH HỌA'), k(7,'TRIỀU ĐÌNH COI LÀ PHẢN NGHỊCH','nghịch'),
 f(8,'VỤ ÁN VĂN TỰ','CHỮ TRÊN TRANG GIẤY','Đối tượng của vụ án'), k(9,'MỘT KẾT CỤC NGHIỆT NGÃ','cục'),
 f(10,'THEO ĐÔNG HOA LỤC','LƯU DUNG','Người tâu việc ấy'), p(11,'writing4','THƯ PHÁP LƯU DUNG · MINH HỌA'),
 k(12,'LỜI GHI NHẬN VIỆC TÂU','tâu'),
 sc('quote',13,text='Bài từ phản nghịch do Từ Thuật Quỳ làm, nếu không nhờ Lưu Dung...',by='ĐÔNG HOA LỤC · BẢN TRÍCH',lbl='TRÍCH DỊCH',qline=13,typeAt=[13,'Bài']),
 sc('quote',[13,'theo'],text='...theo đúng sự thật mà tâu lên, thì suýt đã lọt lưới.',by='ĐÔNG HOA LỤC · BẢN TRÍCH',lbl='TRÍCH DỊCH',qline=13,typeAt=[13,'theo']),
 k(14,'MỘ BỊ QUẬT · THI THỂ BỊ CHÉM','quật'), k(15,'NGƯỜI CHÁU CŨNG BỊ XỬ CHÉM','cháu'),
 f(16,'HỒ SƠ','VỤ ÁN VĂN TỰ','Theo bản trích Đông Hoa lục'),
 k(17,'TỘI NẰM TRONG CHỮ','chữ'), p(18,'writing5','THƯ PHÁP LƯU DUNG · MINH HỌA'),
 k(19,'KẾT CỤC KHÔNG DỪNG Ở NGƯỜI VIẾT','dừng'), k(20,'CẢ NGƯỜI THÂN','thân'),
 f(21,'PHIM','NGƯỜI NGAY THẲNG','Hình tượng được xây dựng'), k(22,'BẢN SỬ · MỘT VỤ QUẬT MỘ','quật'),
 ledger(23,'HAI LỚP',[('NHÂN VẬT','PHIM XÂY DỰNG','phim'),('SỰ VIỆC','BẢN SỬ GHI','sử')]),
 k(24,'LỜI TÂU VÀ KẾT CỤC','tâu'), k(25,'KHÔNG ĐOÁN ĐỘNG CƠ','động'),
 p(26,'writing6','THƯ PHÁP LƯU DUNG · MINH HỌA'),
 k(27,'QUẬT MỘ · XỬ CHÉM NGƯỜI CHÁU','cháu'), f(28,'ĐÔNG HOA LỤC · BẢN TRÍCH','TÊN LƯU DUNG','Gắn với việc phát hiện bài thơ'),
 k(29,'MỘT PHẦN CỦA HỒ SƠ','phần'), f(30,'KẾT CỤC','NGƯỜI CHÁU MẤT MẠNG','Theo bản trích'),
 k(31,'ĐƯỜNG QUAN TIẾP TỤC','tiếp'),
])
CH['ch06'] = dict(hud={'k':'CHƯƠNG 06','t':'TỪ HỒ NAM ĐẾN ĐÔ SÁT VIỆN'}, bgm={'mood':'mystery','at':0,'gain':0.12}, scenes=[
 f(0,'KHOẢNG 1776–1780','NỘI CÁC HỌC SĨ','Chức vụ trong kinh'),
 f([0,'rồi'],'CHỨC VỤ TRONG KINH','THỊ LANG','Bộ Hộ và Bộ Lại'),
 k(1,'CÙNG GIAI ĐOẠN VỤ ÁN BÀI THƠ','thơ'), k(2,'MỘT PHẦN DỰA VÀO NGUỒN HIỆN ĐẠI','nguồn'),
 f(3,'CHỨC VỤ','NỘI CÁC HỌC SĨ','Soạn và chuyển văn bản'),
 f(4,'CHỨC VỤ','THỊ LANG','Phó của thượng thư'),
 ledger(5,'HAI BỘ',[('BỘ HỘ','THUẾ','thuế'),('BỘ LẠI','BỔ NHIỆM QUAN LẠI','nhiệm')]),
 p(6,'robe','TRIỀU PHỤC · MINH HỌA'), dt(7,'LƯU DUNG SÁU MƯƠI TUỔI','1780'),
 mp(8,'Hồ Nam'), f(9,'CHỨC VỤ','TUẦN PHỦ','Quan đứng đầu một tỉnh'),
 k(10,'HỒ NAM · PHÍA NAM HỒ ĐỘNG ĐÌNH','nam'), k(11,'TỪ KINH THÀNH ĐẾN MỘT TỈNH','tỉnh'),
 f(12,'CHUYỂN CHỨC','TỪ HỒ NAM','Sau đó sang chức khác'), k(13,'TỪ CAI QUẢN ĐẾN GIÁM SÁT','sát'),
 f(14,'CHỨC VỤ','TẢ ĐÔ NGỰ SỬ','Đứng đầu ngành giám sát'),
 f(15,'ĐỒNG THỜI','NAM THƯ PHÒNG','Trực gần nhà vua'),
 k(16,'HAI NHIỆM VỤ CÙNG XUẤT HIỆN','hai'), p(17,'writing7','THƯ PHÁP LƯU DUNG · MINH HỌA'),
 dt(18,'TẢ ĐÔ NGỰ SỬ · THEO NGUỒN HIỆN ĐẠI','1781'),
 f(19,'CƠ QUAN','ĐÔ SÁT VIỆN','Giám sát quan lại'), k(20,'NGỰ SỬ CÓ QUYỀN TÂU HẶC','hặc'),
 k(21,'TẢ ĐÔ NGỰ SỬ ĐỨNG ĐẦU','đầu'), p(22,'rooms','TRANH QUAN VĂN · MINH HỌA'),
 ledger(23,'CÁC VỊ TRÍ',[('Ở XA','TUẦN PHỦ','xa'),('Ở GẦN','NAM THƯ PHÒNG','gần'),('GIÁM SÁT','TẢ ĐÔ NGỰ SỬ','giám')]),
 k(24,'SỬ KHÔNG KỂ CHI TIẾT','không'), k(25,'TỪ NHÀ NGỤC ĐẾN VỊ TRÍ GIÁM SÁT','ngục'),
 p(26,'heshen','TRANH HÒA THÂN'), k(27,'MỘT NGỰ SỬ KHÁC KHỞI ĐẦU','ngự'),
 p(28,'writing8','THƯ PHÁP LƯU DUNG · MINH HỌA'), k(29,'MỘT CÁI TÊN SẮP XUẤT HIỆN','tên'),
 k(30,'MỘT NGỰ SỬ','sử'), f(31,'NGỰ SỬ','TIỀN PHONG','Người khởi đầu cuộc tra xét'),
])

if __name__ == '__main__':
    sys.modules['gen_scenes'] = sys.modules[__name__]
    other = D / 'gen_scenes2.py'
    if other.exists():
        module_spec = importlib.util.spec_from_file_location('gen_scenes2', other)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        CH.update(module.CH)
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
    write(__file__, CH, {key:value for key,value in IMGS.items() if key in used}, GEO, endcardBg='liu')
    path = D / 'spec.json'
    spec = json.loads(path.read_text(encoding='utf-8'))
    spec.update({'title':'TỂ TƯỚNG LƯU GÙ Ngoài Đời Thật: Lưu Dung','channel':'CL','theme':'noir','look':'jade',
                 'acc':['lưu dung','lưu thống huân','hòa thân'], 'say':{}})
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=1)+'\n', encoding='utf-8')
