"""GH-476 bước 4: cảnh CH06–CH12 (xem gen_scenes.py)."""
from gen_scenes import (A, B, BR, CT, DT, FL, K, LD, MP, OR, P, PR, PAN, Q, QT, S, SP, TL, KN, card, NG, WK, HK, HR, PD,  # noqa: F401
                        G_PRISON, G_COURT, G_HK, G_PARIS, G_LAT)

CH = {}
G_THEATRE = 'MINH HỌA · SÂN KHẤU PARIS THẾ KỶ 19'
G_BOOK = 'MINH HỌA · NHỮNG NGƯỜI KHỐN KHỔ'

CH['ch06'] = dict(hud={'k': 'CHƯƠNG 06', 't': 'ĐỘI QUÂN CỦA QUỶ'}, bgm={'mood': 'dark', 'at': 0, 'gain': 0.12}, beats=[
    B(0, card('ch06', 'ai08'), DT('CUỐI NĂM', '1811', bg='ai08', illus=PD), P('pool:cruik', G_HK)),
    B(3, P('pool:paris', G_PARIS), P('pool:sat', G_LAT), LD('ĐỘI SÛRETÉ', [('BAN ĐẦU', '4 NGƯỜI'), ('RỒI', '6 · 12 NGƯỜI'), ('SAU NÀY', 'GẦN 30 MẬT VỤ')], bg='pool:paris', srcnote=NG(WK))),
    B(6, P('pool:brest', 'TƯ LIỆU · TRẠI KHỔ SAI BREST'), P('pool:sat', G_LAT), BR(vid='k3'), P('pool:paris', G_PARIS)),
    B(10, A('ai09', fx='candle_flicker'), PR('cr39', 'HỒI KÝ · 1829', 'BẬC THẦY\nCẢI TRANG', ['ÔNG LÃO ĂN XIN', 'GÃ THỦY THỦ SAY'], cap=G_HK),
         P('pool:paris', G_PARIS), P('pool:doc', 'MINH HỌA · TƯ LIỆU THẾ KỶ 19'), PR('cr39', 'HỒI KÝ · 1829', 'RÚT CÒNG\nSỐ TÁM', ['TRƯỚC BẦY TRÙM GIANG HỒ'], cap=G_HK, right=True), P('pool:paris', G_PARIS)),
    B(13, DT('THÁNG 10 · NĂM', '1812', bg='pool:paris', illus=G_PARIS), PR('pool:paris', 'LA BRIGADE DE SÛRETÉ', 'LỰC LƯỢNG\nAN NINH', ['SÁP NHẬP TỔNG NHA', 'VIDOCQ CHỈ HUY'], cap=G_PARIS, right=True)),
    B(15, FL('TRÁT TRUY NÃ', 'VIDOCQ', 'MỘT VẾT THƯƠNG NGẦM',
             rows=[('ÁN', 'TỬ HÌNH TREO LƠ LỬNG'), ('TÒA DOUAI', 'CHƯA HỦY TRÁT')], img='tconge', tone='sepia'),
         P('douai124', 'BẢN ĐỒ · DOUAI', cam='pan'), BR(vid='k6'), P('pool:paris', G_PARIS), P('pool:prison', G_PRISON)),
    B(19, TL([('1817–1818', 'ÂN XÁ DO VUA LOUIS XVIII KÝ')], bg='vdev', srcnote=NG(WK)), P('pool:paris', G_PARIS), P('pool:doc', 'MINH HỌA · TƯ LIỆU THẾ KỶ 19'), P('pool:brest', 'TƯ LIỆU · TRẠI KHỔ SAI BREST')),
    B(21, P('pool:prison', G_PRISON), S('GIÁ CỦA TỰ DO', 'HÀNG NGÀN TỘI PHẠM BỊ TỐNG VÀO NGỤC TỐI', bg='pool:toulon', illus='TRANH · KHỔ SAI THẾ KỶ 19')),
])
CH['ch07'] = dict(hud={'k': 'CHƯƠNG 07', 't': 'CON MẮT CỦA PARIS'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, beats=[
    B(0, card('ch07', 'ai10'), P('pool:portrait', cam='push_in'), LD('SÛRETÉ · 1817', [('MẬT VỤ', 'CHƯA ĐẾN 20 NGƯỜI'), ('VỤ BẮT GIỮ', 'HƠN 800')], bg='pool:paris', srcnote=NG(HR)),
         P('pool:prison', G_PRISON), CT(800, ' VỤ', 'BẮT GIỮ CHỈ TRONG NĂM 1817', bg='pool:paris', srcnote=NG(HR)), P('pool:paris', G_PARIS)),
    B(2, A('ai10', fx='dust', cam='dolly'), FL('THẺ TỘI PHẠM', 'SÛRETÉ', 'MỖI TÊN MỘT TẤM THẺ',
                                              rows=[('NHÂN DẠNG', 'SẸO · ĐẶC ĐIỂM'), ('GÂY ÁN', 'THÓI QUEN'), ('GIẤY TỜ', 'CHỮ VIẾT · BÍ DANH')], img='tconge', tone='bw'),
         P('vcard', 'HỒ SƠ TÙ · VIDOCQ'), CT(1200, ' CỰU TÙ', 'ĐƯỢC ÔNG THEO DÕI', prefix='HƠN ', bg='auto115', illus='MINH HỌA · HỒ SƠ THẾ KỶ 19', srcnote=NG(HR))),
    B(6, P('pool:prison', G_PRISON), P('pool:paris', G_PARIS), P('pool:prison', G_PRISON), P('pool:sat', G_LAT)),
    B(10, P('pool:sat', G_LAT), P('pool:paris', G_PARIS), BR(vid='k5'), P('pool:doc', 'MINH HỌA · TƯ LIỆU THẾ KỶ 19'), BR(vid='k6')),
    B(14, P('pool:paris', G_PARIS), PR('cr43', 'HỒI KÝ · 1829', 'BỊ SĂM SOI', ['THƯ KHIỂN TRÁCH', 'CẮT GIẢM CÔNG QUỸ'], cap=G_HK), P('pool:doc', 'MINH HỌA · TƯ LIỆU THẾ KỶ 19')),
    B(15, SP('MỘT QUY LUẬT TÀN NHẪN', ('cr41', 'ĐƯỜNG PHỐ CHÌM TRONG TỘI ÁC'), ('rue208', 'TRẬT TỰ ĐÃ VÃN HỒI'), bg='pool:paris'), P('pool:portrait', kin_=KN(('NẮM ĐẤM THÉP', 'acc'), ('RỒI LẠI THÀNH VẾT NHƠ', 'sm'))), BR(vid='k16')),
])
CH['ch08'] = dict(hud={'k': 'CHƯƠNG 08', 't': 'RŨ ÁO TỪ QUAN'}, bgm={'mood': 'sad', 'at': 0, 'gain': 0.12}, beats=[
    B(0, card('ch08', 'auto115'), P('pool:portrait', cam='pull_out')),
    B(2, DT('20 THÁNG 6 · NĂM', '1827', bg='auto115', illus='MINH HỌA · THƯ TỪ THẾ KỶ 19')),
    B(3, QT(3, 'THƯ TỪ CHỨC', 'Mười tám năm nay tôi phục vụ cảnh sát một cách xuất sắc.', bg='pool:portrait')),
    B(4, P('pool:doc', 'MINH HỌA · TƯ LIỆU THẾ KỶ 19', cam='push_in'), ),
    B(6, P('pool:portrait', cam='dolly'), P('stmande', cap='ẢNH NGÀY NAY · SAINT-MANDÉ'), P('pool:brest', 'TƯ LIỆU · TRẠI KHỔ SAI BREST')),
    B(9, A('ai28', cam='push_in', fx='dust'), A('ai28', focus=[0.72, 0.45], cam='dolly')),
    B(10, BR(vid='k8')),
    B(12, A('ai11', fx='dust', cam='dolly'), P('vmem', cam='pull_out'), P('vpost', cam='dolly')),
    B(14, P('vpost', cam='push_in'), P('pool:cruik', G_HK), CT(50000, ' BẢN', 'BÁN TRONG NĂM ĐẦU TIÊN', prefix='HƠN ', bg='vmem', illus='HỒI KÝ VIDOCQ · 1828', srcnote=NG(WK)), BR(vid='k18')),
    B(17, P('daum0', G_THEATRE, cam='pan'), P('vpost', cam='dolly'), TL([('1828', 'HỒI KÝ RA MẮT TẠI PARIS'), ('NĂM ĐẦU', 'HƠN 50.000 BẢN'), ('SAU ĐÓ', 'DỊCH SANG TIẾNG ANH')], bg='daum0', illus=G_THEATRE, srcnote=NG(WK))),
    B(19, P('pool:sat', G_LAT), P('pool:sat', G_LAT)),
    B(21, P('stmande', cap='ẢNH NGÀY NAY · SAINT-MANDÉ'), P('plan102', 'BẢN ĐỒ · PARIS THẾ KỶ 19', cam='pan')),
])
CH['ch09'] = dict(hud={'k': 'CHƯƠNG 09', 't': 'TRẬN BÃO THÁNG SÁU'}, bgm={'mood': 'dark', 'at': 0, 'gain': 0.12}, beats=[
    B(0, card('ch09', 'pool:paris'), P('pool:paris', G_PARIS, tone='bw'), P('pool:paris', G_PARIS)),
    B(2, P('pool:paris', G_PARIS), P('pool:paris', G_PARIS, tone='bw'), DT('31 THÁNG 3 · NĂM', '1832', bg='pool:portrait')),
    B(4, DT('5 THÁNG 6 · NĂM', '1832', bg='plan102', illus='BẢN ĐỒ · PARIS THẾ KỶ 19'), P('pool:paris', G_PARIS)),
    B(6, P('pool:paris', G_PARIS)),
    B(7, A('ai25', fx='fog', cam='push_in'), A('ai25', cam='dolly')),
    B(8, P('pool:paris', G_PARIS), P('pool:sat', G_LAT)),
    B(10, P('pool:paris', G_PARIS), P('pool:paris', G_PARIS), DT('15 THÁNG 11 · NĂM', '1832', bg='vcn1'), BR(vid='k10')),
    B(13, LD('SAU KHI VIDOCQ RỜI ĐI', [('SÛRETÉ CŨ', 'BỊ GIẢI THỂ'), ('LUẬT MỚI', 'CẤM TUYỂN NGƯỜI TỪNG CÓ TIỀN ÁN')], bg='pool:paris', illus=G_PARIS),
         P('pool:prison', G_PRISON), K('KỶ NGUYÊN DÙNG KẺ TRỘM\nBẮT KẺ TRỘM KHÉP LẠI', bg='pool:portrait'), P('pool:paris', G_PARIS), BR(vid='k17')),
])
CH['ch10'] = dict(hud={'k': 'CHƯƠNG 10', 't': 'THÁM TỬ ĐẦU TIÊN'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, beats=[
    B(0, card('ch10', 'pool:paris'), A('ai12', cam='push_in')),
    B(2, FL('LE BUREAU DES\nRENSEIGNEMENTS', 'GALERIE VIVIENNE', 'VĂN PHÒNG THÔNG TIN THƯƠNG MẠI',
            rows=[('KHAI SINH', 'CÔNG TY THÁM TỬ TƯ ĐẦU TIÊN')], bg='pool:paris'), A('ai12', focus=[0.75, 0.5], cam='dolly'), P('pool:paris', G_PARIS)),
    B(4, P('pool:paris', G_PARIS), P('pool:paris', G_PARIS), P('pool:doc', 'MINH HỌA · TƯ LIỆU THẾ KỶ 19'), BR(vid='k7')),
    B(7, P('pool:paris', G_PARIS), P('pool:paris', G_PARIS, tone='bw'), P('pool:sat', G_LAT)),
    B(10, BR(vid='k7'), P('pool:prison', G_PRISON)),
    B(12, A('ai26', focus=[0.55, 0.5], cam='dolly', fx='dust'), A('ai26', cam='push_in')),
    B(13, P('pool:prison', G_PRISON), P('pool:prison', G_PRISON), LD('BA TỘI DANH', [('LỪA ĐẢO', 'CHIẾM ĐOẠT TIỀN'), ('MUA CHUỘC', 'CÔNG CHỨC'), ('MẠO NHẬN', 'QUYỀN LỰC NHÀ NƯỚC')], bg='ai13', illus=PD)),
    B(15, P('cour118', G_COURT), PR('vcn1', 'PHIÊN TÒA · 1838', 'TỰ BÀO CHỮA', ['VẠCH TRẦN ÂM MƯU', 'CỦA BỘ MÁY CẢNH SÁT'], cap='VIDOCQ'), DT('THÁNG 2 · TUYÊN VÔ TỘI · NĂM', '1838', bg='cour118', illus=G_COURT), P('pool:cruik', G_HK)),
    B(18, P('pool:paris', G_PARIS), BR(vid='k13'), P('pool:portrait', kin_=KN(('THẮNG TỪNG PHIÊN TÒA', 'acc'), ('THUA CẢ BỘ MÁY', 'sm')))),
])
CH['ch11'] = dict(hud={'k': 'CHƯƠNG 11', 't': 'HAI NỬA LINH HỒN'}, bgm={'mood': 'sad', 'at': 0, 'gain': 0.12}, beats=[
    B(0, card('ch11', 'hugo187'), P('livret', G_BOOK), P('pool:hugo', cam='push_in')),
    B(1, P('balz1', cam='push_in'), P('balz159', cam='dolly'), P('balz161', cam='dolly'), P('balz32', 'MINH HỌA · VAUTRIN · BALZAC'), P('balz163', cam='pull_out'), P('hugo186', cam='dolly')),
    B(4, A('ai27', cam='push_in'), P('pool:paris', G_PARIS), OR(('VIDOCQ', 'MỘT NGƯỜI · BA TÁC PHẨM'), [('VAUTRIN', 'BALZAC'), ('DUPIN', 'EDGAR ALLAN POE'), ('VALJEAN · JAVERT', 'VICTOR HUGO')], bg='vpost'), P('pool:paris', G_PARIS)),
    B(5, P('hugo187', cam='push_in'), A('ai14', fx='candle_flicker', cam='dolly'), P('hugo185', cam='pull_out')),
    B(8, P('valj16', G_BOOK), SP('MỘT NGƯỜI · HAI NỬA', ('valj16', 'JEAN VALJEAN'), ('jav13', 'JAVERT'), bg='vlit'), P('madel', G_BOOK), P('jav85', G_BOOK), P('vjdeath', G_BOOK)),
    B(11, P('jav13', G_BOOK), P('jav97', G_BOOK), P('jav92', G_BOOK)),
    B(12, P('hugo194', cam='push_in'), QT(13, 'VICTOR HUGO', 'Một tên chỉ điểm bằng đá cẩm thạch, Brutus trong Vidocq.', bg='hugo184')),
    B(14, A('ai14', focus=[0.7, 0.5], cam='pull_out'), A('ai16', cam='push_in'), P('pool:hugo', cam='dolly'), P('pool:hugo', cam='pull_out')),
])
CH['ch12'] = dict(hud={'k': 'CHƯƠNG 12', 't': 'BÓNG HOÀNG HÔN'}, bgm={'mood': 'sad', 'at': 0, 'gain': 0.12}, beats=[
    B(0, card('ch12', 'vlit'), BR(vid='k9')),
    B(2, P('pool:paris', G_PARIS)),
    B(3, A('ai29', cam='push_in'), BR(vid='k14')),
    B(4, DT('11 THÁNG 5 · NĂM', '1857', bg='vcrop')),
    B(5, A('ai15', cam='push_in', fx='dust'), A('ai15', focus=[0.7, 0.4], cam='pull_out')),
    B(6, CT(3000, ' FRANC', 'TOÀN BỘ GIA SẢN', prefix='GẦN ', bg='vcn1', srcnote=NG(WK)), LD('DI CHÚC', [('SỐ TIỀN', 'GẦN 3.000 FRANC'), ('CHIA ĐỀU CHO', '11 NGƯỜI PHỤ NỮ NGHÈO')], bg='vbm', srcnote=NG(WK)), P('pool:portrait', cam='dolly')),
    B(8, P('vjdeath', 'MINH HỌA · HUGO, 1862', cam='pull_out'), BR(vid='k8')),
    B(10, P('pool:paris', G_PARIS, tone='bw'), DT('TRIỂN LÃM CHÂN DUNG CÁC SẾP SÛRETÉ', '1905', bg='pool:paris', illus=G_PARIS), P('pool:paris', G_PARIS)),
    B(12, P('pool:paris', G_PARIS), P('pool:doc', 'MINH HỌA · TƯ LIỆU THẾ KỶ 19')),
    B(13, P('pool:paris', G_PARIS), Q('CÁI GIÁ CỦA BẢN GIAO KÈO VỚI QUỶ DỮ\nĐẮT ĐẾN MỨC NÀO?', bg='vdev')),
    B(15, P('pool:portrait', kin_=KN(('SỰ CÔ ĐỘC VĨNH CỬU', 'acc'))), SP('HAI PHÍA CỦA MỘT NGƯỜI', ('bal206', 'THẾ GIỚI NGẦM: KẺ PHẢN BỘI'), ('marville', 'THỐNG TRỊ: CÔNG CỤ ĐÁNG NGỜ'), bg='pool:portrait'),
         P('pool:brest', 'TƯ LIỆU · TRẠI KHỔ SAI BREST'), P('pool:prison', G_PRISON), A('ai16', cam='dolly')),
    B(20, P('pool:portrait', cam='push_in'), P('pool:doc', 'MINH HỌA · TƯ LIỆU THẾ KỶ 19'), P('hugo185', cam='dolly'), P('jav85', G_BOOK), P('pool:lm', G_BOOK), P('pool:portrait', cam='pull_out'), P('pool:portrait', cam='push_in')),
])
