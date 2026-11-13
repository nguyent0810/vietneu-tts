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


TD = '\u0054\u00c1I D\u1ef0NG MINH H\u1eccA'
V = {f'v{i}': f'90000{i}' for i in range(1, 9)}
IMGS.update({f'ai{i:02}': f'EXT:ai:ai_{i:02}' for i in range(1, 19)})
IMGS.update({
 'r37': im(37, 'Pr\u00fcfungszellen'), 'r45': im(45, 'imperial exam winner'),
 'r48': im(48, '国子监'), 'r73': im(73, 'Mid-Autumn'),
 'r74': im(74, 'Boyuan'), 'r82': im(82, 'Kaishu'),
 'r85': im(85, 'LantingXu'), 'r88': im(88, 'Chinesecalligraphy'),
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
                scene.update(vid=V[v], illus=TD, tags=['minh_hoa_chung'])
                continue
            choices = NEN[kind]
            available = [x for x in choices if used[x] < (6 if x.startswith('ai') else 4)]
            if not available: raise ValueError(f'no background {chapter} {index} {kind}')
            img = min(available, key=lambda x: (used[x], choices.index(x)))
            used[img] += 1
            scene['bg'] = img
            if img.startswith('ai'):
                scene.update(credit=False, illus=TD, tags=['minh_hoa_chung'])
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
                 'acc':['lưu dung','lưu thống huân','hòa thân'], 'say':{}, 'chapters':list(CH)})
    spec.setdefault('youtube', {})['chapter_titles'] = CHAPTER_TITLES
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=1)+'\n', encoding='utf-8')
