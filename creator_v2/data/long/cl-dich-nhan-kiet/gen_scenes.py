"""GH-395 bước 4: cảnh biên tập CH00–CH13 cho Long CL "Địch Nhân Kiệt Ngoài Đời Thật".

Trục hình: "hai cuốn sổ đặt cạnh nhau". Mỗi chặng đời có một thẻ `org` cùng khuôn: gốc "CHẶNG n · <tên>" + "HAI CUỐN SỔ",
hai cột "NẾU LÀ PHIM" / "SỬ CHÉP". Mọi câu [TRÍCH DỊCH] có thẻ `quote` kèm nguồn (Cựu Đường thư q.89, Tư trị thông giám q.202–207).
Ba cách đếm Dự Châu: ba cột `org` khác loại số (không cộng). Dòng thời gian Võ Chu: `timeline` ở CH07 và CH13.
Chạy: python data/long/cl-dich-nhan-kiet/gen_scenes.py (gen_scenes2.py chứa CH07–CH13; spec_dnk.py ghi spec.json).
"""
import importlib.util
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[2]
sys.path.insert(0, str(ROOT / 'motion/long'))
from scenekit import sc, kin, write, chapter  # noqa: E402

RES = json.loads((ROOT / 'output/long/cl-dich-nhan-kiet/research.json').read_text(encoding='utf-8'))['images']


def im(i, must):
    f = RES[i]['file']
    if must not in f:
        raise ValueError(f'Ảnh {i} không khớp: {f}')
    return f


# Ảnh đã mở hết sheet_0..9 và lọc tay (15/11): chỉ ảnh tư liệu/hiện vật/bản đồ thời Đường–Võ Chu + vài ảnh "ngày nay" có nhãn riêng.
IMGS = {
    # chân dung và mộ
    'dnk_a': im(2, 'Famous Men - Di Renjie.jpg'), 'dnk_b': im(1, '狄仁杰.jpg'), 'dnk_c': im(109, 'File:Di Renjie.jpg'),
    'dnk_t': im(269, 'Di Renjie 2'), 'yao': im(108, 'Yao Chong'),
    'tomb1': im(0, '狄仁杰墓'), 'tomb2': im(265, '2017-02-25 Tomb'), 'tomb3': im(272, '20251018 Tomb'),
    # Võ Tắc Thiên
    'wu1': im(15, 'Wuhou (2)'), 'wu2': im(69, '武曌像'), 'wu3': im(16, '武則天'), 'stele': im(4, '升仙太子碑'),
    'wudio': im(187, 'Diorama'), 'wugold': im(188, 'Gold Strip'), 'wustat': im(197, 'Gilded Statue'),
    'coin': im(281, 'Qian Feng'), 'mingtang': im(17, 'cropped'),
    # Thái Tông, Chiêu Lăng, Càn Lăng
    'tz': im(3, 'Taizong'), 'tzaud': im(25, 'gives an audience'), 'zl1': im(294, 'Stone Relief'), 'zl2': im(296, 'Stone Relief'),
    'zl3': im(298, 'Stone Relief'), 'zhaoling': im(293, 'Zhao Mausoleum'), 'guard1': im(300, 'Soldiers of the Guard'),
    'guard2': im(301, 'Honour guard'), 'guardo': im(45, 'Officer of the Guard'),
    'qian1': im(200, 'Qianling Mausoleum 02'), 'qian2': im(216, 'dignitary'), 'qian3': im(217, 'statue'),
    'qianmap': im(218, 'Map of Qianling'), 'qian4': im(208, 'Mausoleum 36'),
    # cung đình, quan lại
    'ladies': im(175, 'Court Ladies of the Tang.jpg'), 'outing': im(52, 'Spring Outing'), 'concert': im(178, 'palace concert'),
    'silk1': im(173, 'pounding silk'), 'silk2': im(181, 'cropped to show'), 'silk3': im(183, '(cropped).jpg'),
    'ministers': im(177, 'Twenty-Four Ministers'),
    'off1': im(35, 'civil official'), 'off2': im(275, 'sancai pottery, civil'), 'off3': im(277, 'Court Official'),
    'off4': im(279, 'two officials'), 'off5': im(283, 'Lokapala'), 'off6': im(284, 'Xinxiang 02'), 'off7': im(286, 'Sancai Porcelain Official'),
    'off8': im(288, 'Tang Sancai Official'), 'off9': im(289, 'Civil Official'), 'off10': im(291, 'V&A'),
    'warrior': im(111, 'Tang Warrior'), 'tguard': im(24, 'Cernuschi'),
    # bản đồ, mô hình
    'map700': im(6, 'circa 700'), 'map669': im(110, '669AD'), 'turk1': im(136, 'First Turkic'), 'turk2': im(148, 'Second Turkic'),
    'henan': im(73, 'ChinaHenanLuoyang'), 'changmap': im(43, "Chang'an of Tang"), 'xian': im(119, "History of Xi'an"),
    'lych': im(322, "Lo-yang and Ch'ang-an"), 'cmodel': im(316, "Chang'an City in Tang"), 'cmodel2': im(317, '9923627634'),
    'lymodel': im(14, 'Luoyang in Sui'), 'lymodel2': im(46, 'A model of Luoyang'), 'hanguang': im(314, 'Hanguang'),
    # Đột Quyết, biên cương
    'gokturk': im(126, 'Gokturk'), 'turkh': im(129, 'Turkic horsemen'), 'kol': im(130, 'Koltegin'), 'mogao': im(48, 'Mogao Cave 156'),
    'samar': im(66, 'Varkhuman'), 'm220': im(290, 'Mogao Cave 220'),
    # Phật giáo, Long Môn
    'vairo': im(13, 'Fengxian Temple, Vairocana'), 'fengxian': im(10, 'Luoyang 2006 7-29'), 'longmen': im(18, 'Grutes de longmen'),
    'bod1': im(50, 'TangBodhisattva'), 'bod2': im(104, 'Seated bodhisattva'), 'wh1': im(72, 'white-horse-temple-entrance'),
    # hiện vật làm nền
    'mirror': im(39, 'Mirror with phoenixes'), 'coin2': im(47, 'Kaiyuan'), 'jar': im(23, 'Gilt silver jar'), 'sancaih': im(34, 'pottery horse, detail'),
    'horse1': im(64, 'Pottery Horse & Rider2'), 'camel': im(68, 'Musicians on a Camel'), 'zodiac': im(152, 'zodiac'),
    'hh1': im(157, 'horse with rider'), 'hh2': im(159, 'horse, China'),
}
GEO = {
    'ht1': {'countries': ['China'], 'labels': {'China': 'TRUNG QUỐC'}, 'bbox': [105.5, 31, 121.5, 41], 'box': [260, 110, 1660, 880],
            'pins': [{'name': 'Trường An', 'lon': 108.94, 'lat': 34.27, 'label': 'TRƯỜNG AN'},
                     {'name': 'Lạc Dương', 'lon': 112.45, 'lat': 34.62, 'label': 'LẠC DƯƠNG'},
                     {'name': 'Dự Châu', 'lon': 114.35, 'lat': 33.0, 'label': 'DỰ CHÂU'},
                     {'name': 'Ngụy Châu', 'lon': 115.2, 'lat': 36.3, 'label': 'NGỤY CHÂU'}]},
    'ht2': {'countries': ['China'], 'labels': {'China': 'TRUNG QUỐC'}, 'bbox': [111.5, 35, 119.5, 40.5], 'box': [260, 110, 1660, 880],
            'pins': [{'name': 'Ký Châu', 'lon': 115.57, 'lat': 37.55, 'label': 'KÝ CHÂU'},
                     {'name': 'Triệu Châu', 'lon': 114.0, 'lat': 37.75, 'label': 'TRIỆU CHÂU'},
                     {'name': 'Định Châu', 'lon': 115.0, 'lat': 38.5, 'label': 'ĐỊNH CHÂU'},
                     {'name': 'Ngụy Châu', 'lon': 115.2, 'lat': 36.3, 'label': 'NGỤY CHÂU'}]},
}
CLIPS = {'c1': '900001', 'c2': '900002', 'c4': '900004', 'c5': '900005', 'c6': '900006', 'c7': '900007', 'c8': '900008'}
TD = 'MINH HỌA CHUNG'          # nhãn clip AI chung (không phải tư liệu)

# ---------------------------------------------------------------- helpers (mỗi helper trả một cảnh)


def _a(a):
    return list(a) if isinstance(a, tuple) else a


def _fin(s, **kw):
    for key in ('bg', 'vid'):
        v = kw.pop(key, None)
        if v:
            if key == 'vid':
                s['_vid'] = [v] if isinstance(v, str) else list(v)
                s['illus'] = TD
            else:
                s[key] = v
    s.update({k: v for k, v in kw.items() if v is not None})
    return s


def P(a, img, cap, tone=None, move=None, focus=None, **kw):
    return _fin(sc('photo', _a(a), img=img, illus=cap, tone=tone, move=move, focus=focus or [0.5, 0.4]), **kw)


def PR(a, img, k, h, lines, cap=None, right=False, circles=None, tone=None, maxw=None, maxh=None, **kw):
    """Ảnh đặt như tờ in, cột ghi chú bên cạnh. lines: [(chữ, mốc)]."""
    s = sc('print', _a(a), img=img, right=right, tone=tone, maxW=maxw, maxH=maxh, caption=cap,
           side={'k': k, 'h': h, 'lines': [{'text': t, 'at': _a(m)} for t, m in lines]})
    if circles:
        s['circles'] = [{'x': x, 'y': y, 'r': r, 'at': _a(m)} for x, y, r, m in circles]
    return _fin(s, **kw)


def K(a, text, *more, **kw):
    a0 = 0 if a is None else _a(a)
    items = [(text, a0, 'acc')] + [(t, _a(m), *fl) for t, m, *fl in more]
    return _fin(sc('kinetic', _a(a), items=kin(*items)), **kw)


def S(a, text, sub=None, **kw):
    return _fin(sc('slam', _a(a), text=text, sub=sub), **kw)


def DT(a, day, date, **kw):
    return _fin(sc('date', _a(a), day=day, date=date), **kw)


def CT(a, to, suffix, label, frm=0, year=False, prefix=None, **kw):
    s = sc('counter', _a(a), suffix=suffix, label=label, **{'from': frm, 'to': to})
    if prefix:
        s['prefix'] = prefix
    if year or 1000 <= to <= 2100:
        s['year'] = bool(year)
    return _fin(s, **kw)


def QU(a, text, by, type_at=None, qline=None, **kw):
    """Thẻ trích dẫn. type_at/qline: khi thẻ mở trước câu trích (câu dẫn nằm ở dòng trước)."""
    ta = type_at if type_at is not None else a
    ql = qline if qline is not None else (ta if isinstance(ta, int) else ta[0])
    return _fin(sc('quote', _a(a), text=text, by=by, lbl='TRÍCH DỊCH', qline=ql, typeAt=_a(ta)), **kw)


def Q(a, text, **kw):
    return _fin(sc('question', _a(a), text=text), **kw)


def LD(a, title, rows, **kw):
    return _fin(sc('ledger', _a(a), title=title, rows=[{'k': k, 'v': v, 'at': _a(a)} for k, v in rows]), **kw)


def TL(a, items, **kw):
    return _fin(sc('timeline', _a(a), title=None, items=[{'year': y, 'text': t, 'at': _a(a)} for y, t in items]), **kw)


def SP(a, title, left, right, sign=None, **kw):
    s = sc('split', _a(a), title=title, a={'img': left[0], 'label': left[1]}, b={'img': right[0], 'label': right[1]})
    if sign:
        s['sign'] = sign
    return _fin(s, **kw)


def OR(a, root, kids, **kw):
    nodes = [{'id': 'r', 't': root[0], 's': root[1], 'cls': 'top', 'at': _a(a)}]
    nodes += [{'id': f'k{i}', 'p': 'r', 't': t, 's': s, 'at': _a(a)} for i, (t, s) in enumerate(kids)]
    return _fin(sc('org', _a(a), nodes=nodes), **kw)


def SO(a, no, name, film, sri, **kw):
    """Thẻ cố định "hai cuốn sổ" của mỗi chặng đời: gốc CHẶNG n · tên; cột NẾU LÀ PHIM / SỬ CHÉP."""
    return OR(a, (f'CHẶNG {no} · {name}', 'HAI CUỐN SỔ'), [('NẾU LÀ PHIM', film), ('SỬ CHÉP', sri)], **kw)


def MP(a, geo, names, **kw):
    return _fin(sc('map', _a(a), geo=geo, pins=[{'name': n} for n in names]), **kw)


def MY(a, mlab, myth, tlab, truth, strike, truth_at, **kw):
    return _fin(sc('myth', _a(a), mythLab=mlab, myth=myth, truthLab=tlab, truth=truth, strikeAt=_a(strike), truthAt=_a(truth_at)), **kw)


def _split2(text):
    words, best = text.split(' '), None
    for i in range(1, len(words)):
        a, b = ' '.join(words[:i]), ' '.join(words[i:])
        cost = max(len(a), len(b))
        if best is None or cost < best[0]:
            best = (cost, [a, b])
    return best[1] if best else [text]


def _wrap(name, limit=12):
    if len(name) <= limit or '\n' in name:
        return name
    parts = [x.strip() for x in name.split('·')] if '·' in name else [name]
    out = []
    while parts:
        part = parts.pop(0)
        if len(part) > limit and ' ' in part:
            parts[:0] = _split2(part)
        else:
            out.append(part)
    return '\n'.join(out)


def FL(a, k, name, desc='', rows=None, **kw):
    s = sc('file', _a(a), k=k, name=_wrap(name), desc=desc)
    if rows:
        s['rows'] = [{'k': x, 'v': y, 'at': _a(a)} for x, y in rows]
    return _fin(s, **kw)


# Nguồn ghi trên thẻ trích dẫn
S1 = 'CỰU ĐƯỜNG THƯ · Q.89'
Z202, Z204, Z205, Z206, Z207 = ('TƯ TRỊ THÔNG GIÁM · Q.%d' % n for n in (202, 204, 205, 206, 207))
BK = 'BÁCH KHOA'

CH = {}

# ---------------------------------------------------------------- CH00–CH06
CH['ch00'] = dict(hud={'k': 'MỞ ĐẦU', 't': 'MỘT CHỮ "THẬT"'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    P(None, 'dnk_a', 'ĐỊCH NHÂN KIỆT · TRANH CỔ', tone='noir', veil=0.35, focus=[0.5, 0.3]),
    P(1, 'off1', 'TƯỢNG GỐM QUAN ĐƯỜNG · MINH HỌA', focus=[0.5, 0.3]),
    K(2, 'AI NHẬN NGAY\nLẦN HỎI ĐẦU', ('ĐƯỢC GIẢM ÁN CHẾT', (2, 'được'), 'sm'), bg='hh1'),
    S(3, 'ĐỊCH NHÂN KIỆT', 'SỬ CHÉP CÂU ÔNG ĐÁP LẠI', vid='c4'),
    QU(5, 'Đại Chu đổi mệnh, muôn vật đổi mới. Bề tôi cũ nhà Đường cam chịu bị giết.', Z205, bg='mirror'),
    S((5, 'Phản'), 'PHẢN\nLÀ THẬT!', 'THEO TƯ TRỊ THÔNG GIÁM · Q.205', bg='guardo'),
    CT((6, 'xử'), 17000, ' NGƯỜI', 'KHÔNG AI KÊU OAN · ÁN TỒN XỬ XONG TRONG MỘT NĂM', bg='ministers'),
    Q(7, 'VÌ SAO ÔNG TỰ NHẬN\nMÌNH LÀ KẺ PHẢN?', bg='guard1'),
    K(8, 'MỘT ĐỊCH NHÂN KIỆT\nKHÁC', ('THÁM TỬ LẬT BÀN CỜ BẰNG MỘT PHÁT HIỆN', (9, 'thám'), 'sm'), bg='concert'),
    S(10, 'HỒ SƠ KỂ KHÁC', 'KHÔNG LẬT BÀN CỜ', bg='dnk_c'),
    K(11, 'XIN NGƯỜI CANH', ('MỘT CÂY BÚT', (11, 'một'), 'acc'), vid='c8'),
])
CH['ch01'] = dict(hud={'k': 'CHƯƠNG 01', 't': 'HAI CUỐN SỔ ĐẶT CẠNH NHAU'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, scenes=[
    K(0, 'NẾU BẠN TỪNG XEM PHIM', ('MỘT NGƯỜI RẤT GIỎI PHÁ ÁN', (0, 'một'), 'sm'), vid='c2'),
    FL(1, 'PHIM · NĂM 2004', 'THẦN THÁM ĐỊCH NHÂN KIỆT', 'CCTV · Lương Quán Hoa đóng vai chính', bg='ladies'),
    TL(2, [('2004', 'CCTV · LƯƠNG QUÁN HOA'), ('2010', 'TỪ KHẮC · LƯU ĐỨC HOA')], bg='outing'),
    S(3, 'ĐÓ LÀ PHIM', 'KHÔNG PHẢI HỒ SƠ', bg='concert'),
    K(5, 'TIỂU THUYẾT ĐỜI THANH', ('ĐỊCH CÔNG ÁN', (5, 'địch'), 'sm'), bg='ministers'),
    DT(6, 'ROBERT VAN GULIK · DỊCH ĐỊCH CÔNG ÁN SANG TIẾNG ANH', '1949', bg='guard2'),
    K(8, 'JUDGE DEE', ('HÌNH TƯỢNG BÁN HƯ CẤU · THEO BÁCH KHOA', (8, 'hình'), 'sm'), illus=BK, bg='off3'),
    OR(9, ('NGƯỜI THẬT', 'BA BỘ SÁCH'), [('CỰU ĐƯỜNG THƯ', 'TRUYỆN Q.89'), ('TÂN ĐƯỜNG THƯ', 'Q.115 · ĐỜI TỐNG'), ('THÔNG GIÁM', 'Q.202–207')], bg='dnk_t'),
    K(11, 'CẢ BA LÀ SÁCH\nCỦA NGƯỜI ĐỜI SAU', ('CHỖ NÀO KHÁC, TA NÓI RÕ', (11, 'chỗ'), 'sm'), vid='c7'),
    S(12, 'HÀNG VẠN CHỮ', 'LỜI TÂU CỦA ÔNG', bg='map669'),
    FL(13, 'KHAI NGUYÊN · LÝ UNG', 'LƯƠNG CÔNG BIỆT TRUYỆN', 'Chép lại những lời tâu của ông', rows=[('NAY', 'CHƯA ĐỌC ĐƯỢC')], bg='ministers'),
    K(14, 'CUỐN ẤY: CHƯA ĐỌC ĐƯỢC', ('CHỈ BIẾT QUA MỘT DÒNG CỰU ĐƯỜNG THƯ', (14, 'chỉ'), 'sm'), bg='off5'),
    OR(15, ('HAI CUỐN SỔ', 'ĐẶT CẠNH NHAU'), [('SỔ CỦA PHIM', 'ÔNG SẼ LÀM GÌ?'), ('SỔ CỦA SỬ', 'ÔNG ĐÃ LÀM GÌ?')], bg='lymodel'),
    K(17, 'RỒI ĐỌC XEM\nSỬ GHI GÌ', ('ÔNG ĐỨNG TRƯỚC NHỮNG NGƯỜI KHÁC NHAU', (18, 'ông'), 'sm'), bg='cmodel'),
    P(19, 'silk2', 'TRANH THỜI TỐNG · LỤA MỚI DỆT', tone='color'),
    Q(20, 'CẬU BÉ ẤY\nTỪ ĐÂU TỚI?', bg='tz'),
])
CH['ch02'] = dict(hud={'k': 'CHƯƠNG 02', 't': 'CẬU BÉ NGỒI ĐỌC SÁCH'}, bgm={'mood': 'quiet', 'at': 0, 'gain': 0.12}, scenes=[
    DT(0, 'SINH RA Ở THÁI NGUYÊN · TINH CHÂU', '630', vid='c6'),
    OR(1, ('GIA ĐÌNH', 'LÀM QUAN'), [('ÔNG NỘI', 'TẢ THỪA THƯỢNG THƯ TỈNH'), ('CHA', 'TRƯỞNG SỬ QUỲ CHÂU')], bg='off7'),
    P(2, 'dnk_b', 'ĐỊCH NHÂN KIỆT · TRANH CỔ', focus=[0.5, 0.3]),
    K(3, 'TIỂU LẠI ĐẾN HỎI', ('AI CŨNG RA ĐỐI ĐÁP', (3, 'ai'), 'sm'), ('RIÊNG CẬU BÉ ĐỌC SÁCH', (3, 'riêng'), 'acc'), bg='dnk_t'),
    SO(4, 1, 'THUỞ NHỎ', 'CẬU BÉ NHÌN RA MANH MỐI', 'CẬU VẪN ĐỌC SÁCH', bg='ladies'),
    QU(6, 'Trong sách vàng có đủ thánh hiền, ta còn chưa đối đáp xuể, đâu rảnh tiếp tiểu lại mà bị trách!', S1, type_at=7, qline=7, bg='silk3'),
    K(8, 'CHỈ CÓ TRONG', ('HAI BỘ ĐƯỜNG THƯ', (8, 'hai'), 'acc'), ('KHÔNG THẤY Ở THÔNG GIÁM', (8, 'không'), 'sm'), bg='dnk_t'),
    DT(9, 'MINH KINH · PHÁN TÁ BIỆN CHÂU · THEO BÁCH KHOA', '659', illus=BK, bg='off2'),
    QU(11, 'Ông là viên ngọc ở góc biển, báu vật bị bỏ sót của miền Đông Nam.', S1, type_at=12, qline=12, bg='jar'),
    P(13, 'map700', 'TRUNG HOA ĐỜI ĐƯỜNG · KHOẢNG NĂM 700', tone='color'),
    QU(15, 'Cha mẹ ta ở dưới đám mây ấy.', S1, type_at=16, qline=16, bg='m220'),
    K(17, 'ĐỨNG NHÌN RẤT LÂU', ('MÂY DỜI MỚI CẤT BƯỚC', (17, 'mãi'), 'sm'), vid='c6'),
    FL(18, 'ĐỒNG LIÊU · TINH CHÂU', 'TRỊNH SÙNG CHẤT', 'Phải đi sứ nơi xa · mẹ già đang bệnh', bg='off8'),
    K(19, 'ÔNG XIN ĐI THAY', ('CẢ TƯ TRỊ THÔNG GIÁM CŨNG CHÉP', (20, 'chuyện'), 'sm'), bg='off4'),
    OR(21, ('LẬN NHÂN CƠ', 'TRƯỞNG SỬ'), [('BẤT HÒA', 'VỚI MỘT NGƯỜI CÙNG SỞ'), ('SAU ĐÓ', 'XẤU HỔ · LÀM LÀNH')], bg='off9'),
    S(22, 'CHƯA CÓ VỤ ÁN NÀO', 'DO ÔNG PHÁ', bg='off10'),
    K(23, 'MỘT CẬU BÉ ĐỌC SÁCH', ('MỘT NGƯỜI LỚN XIN ĐI THAY', (23, 'một'), 'acc'), bg='dnk_b'),
    S(24, 'HAI CHUYỆN NHỎ', 'CHƯA PHẢI CHUYỆN THÁM TỬ', vid='c1'),
])
CH['ch03'] = dict(hud={'k': 'CHƯƠNG 03', 't': 'ĐẠI LÝ THỪA, VÀ CON SỐ 17.000'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, scenes=[
    OR(0, ('TRIỀU ĐÌNH', 'HAI NGƯỜI CÙNG ĐỨNG'), [('CAO TÔNG', 'THIÊN HOÀNG'), ('HOÀNG HẬU VÕ', 'THIÊN HẬU')], bg='wu3'),
    DT(2, 'ĐẠI LÝ THỪA · ĐẠI LÝ TỰ · THEO BÁCH KHOA', '675', illus=BK, bg='hanguang'),
    SO(3, 2, 'ĐẠI LÝ THỪA', 'MỘT VỤ ÁN LỚN ĐANG CHỜ', 'MỘT CHỒNG HỒ SƠ CŨ', bg='lymodel2'),
    CT(5, 17000, ' NGƯỜI', 'ÁN TỒN XỬ XONG TRONG MỘT NĂM · CỰU ĐƯỜNG THƯ', bg='off6'),
    S(6, 'KHÔNG CÓ AI\nKÊU OAN', 'BỐN CHỮ CUỐI CÂU', bg='guard1'),
    K(7, 'TÂN ĐƯỜNG THƯ CHÉP KHÁC', ('NGƯỜI ĐỜI KHEN: CÔNG BẰNG, KHOAN DUNG', (7, 'người'), 'sm'), bg='dnk_t'),
    K(8, 'MỘT VẠN BẢY NGHÌN NGƯỜI', ('HAI BỘ SỬ GHI CON SỐ ẤY', (9, 'hai'), 'sm'), ('KHÔNG CÓ BẢNG KÊ TỪNG VỤ', (9, 'nhưng'), 'sm'), vid='c5'),
    LD(10, '17.000 · MỖI BỘ MỘT CÂU', [('CỰU ĐƯỜNG THƯ', 'MỘT CÂU'), ('TÂN ĐƯỜNG THƯ', 'MỘT CÂU'), ('BẢNG KÊ TỪNG VỤ', 'KHÔNG CÓ')], bg='lych'),
    OR(12, ('CON SỐ 17.000', 'HAI CÁCH GỌI'), [('BẢN TIẾNG ANH', '17.000 VỤ'), ('SỬ', '17.000 NGƯỜI')], bg='xian'),
    K(14, 'MỘT DÒNG SỬ', ('KHÔNG PHẢI MỘT BIÊN BẢN', (14, 'không'), 'acc'), bg='ministers'),
    SP(15, 'HAI CÁCH HIỂU', ('lymodel', 'NẾU LÀ PHIM · PHÁ ÁN BẰNG TRÍ TUỆ'), ('off3', 'SỬ CHÉP · XỬ XONG VIỆC DỒN LẠI')),
    K(16, 'SỬ MỞ CÁCH HIỂU KHÁC', ('XỬ XONG VIỆC MÀ NGƯỜI KHÁC ĐỂ DỒN', (16, 'một'), 'sm'), bg='off7'),
    S(17, 'KHÔNG AI KÊU OAN', 'THEO CỰU ĐƯỜNG THƯ', vid='c2'),
    P(18, 'zhaoling', 'CHIÊU LĂNG · ẢNH NGÀY NAY', tone='color'),
    S(19, 'KHÔNG XÁC CHẾT', 'CHỈ MỘT CÂY BÁCH', bg='zl1'),
])
CH['ch04'] = dict(hud={'k': 'CHƯƠNG 04', 't': 'CÂY BÁCH Ở CHIÊU LĂNG'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    DT(0, 'THÁNG CHÍN · CHẶT NHẦM CÂY BÁCH', '676', bg='zl2'),
    P(1, 'tz', 'ĐƯỜNG THÁI TÔNG · TRANH CỔ', focus=[0.5, 0.3]),
    S(3, 'XỬ TỬ', 'CAO TÔNG RA LỆNH', vid='c4'),
    QU(5, 'Bọn Thiện Tài chặt cây bách ở lăng, ta mà không giết thì ta bất hiếu.', Z202, bg='tzaud'),
    K(6, 'VIÊN ĐẠI LÝ THỪA', ('VẪN GIỮ LỜI TÂU', (6, 'vẫn'), 'acc'), ('HAI NGƯỜI ẤY KHÔNG ĐÁNG CHẾT', (7, 'hai'), 'sm'), bg='off1'),
    S(8, 'BỆ HẠ NỔI GIẬN', 'ÔNG TIẾP TỤC CAN', bg='qian1'),
    QU(10, 'Đụng đến mặt rồng mà can, từ xưa ai cũng cho là khó. Thần cho rằng gặp Kiệt, Trụ thì khó, gặp Nghiêu, Thuấn thì dễ.', Z202, bg='guard2'),
    Q(11, 'NẾU CÓ KẺ TRỘM MỘT NẮM ĐẤT\nỞ LĂNG HÁN CAO TỔ?', bg='qian3'),
    FL(13, 'TIỀN LỆ · TÂN ĐƯỜNG THƯ', 'HÁN VĂN ĐẾ TRU CẢ HỌ', 'Một kẻ trộm ngọc ở miếu tổ', bg='off4'),
    K(14, 'TRƯƠNG THÍCH CHI CAN\nNGAY GIỮA TRIỀU', ('TỘI CHỈ DỪNG Ở MỘT NGƯỜI', (14, 'và'), 'sm'), ('RỒI ÔNG NÓI VỀ LUẬT', (15, 'rồi'), 'sm'), bg='guardo'),
    QU(16, 'Luật chưa đến mức chết mà bệ hạ riêng giết họ, thế là luật không còn khiến người tin. Dân biết đặt tay chân vào đâu?', Z202, bg='zl3'),
    QU(17, 'Nay vì một cây bách mà giết hai tướng, đời sau sẽ gọi bệ hạ là vua thế nào?', Z202, type_at=18, qline=18, bg='qian2'),
    OR(19, ('BA BỘ SỬ', 'CÙNG CHÉP CẢNH NÀY'), [('CÂU CHỮ', 'MỖI NƠI MỘT KHÁC'), ('TA DÙNG BẢN', 'TƯ TRỊ THÔNG GIÁM')], bg='dnk_t'),
    LD(20, 'HAI NGƯỜI SAU CUỘC CAN', [('THÔNG GIÁM', 'CÁCH CHỨC · ĐÀY LĨNH NAM'), ('CỰU ĐƯỜNG THƯ', 'THIỆN TÀI THOÁT CHẾT')], bg='warrior'),
    K(22, 'VÀI HÔM SAU', ('ÔNG LÊN LÀM THỊ NGỰ SỬ', (22, 'địch'), 'acc'), vid='c8'),
    SO(24, 3, 'CÂY BÁCH', 'MỘT CẢNH TÒA', 'HAI TƯỚNG THOÁT CHẾT', bg='zl1'),
    S(26, 'KHÔNG BẮT AI', 'HAI NGƯỜI BỊ ĐÀY', bg='tguard'),
])
CH['ch05'] = dict(hud={'k': 'CHƯƠNG 05', 't': 'THỨ GẦN VỚI MA QUÁI NHẤT'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, scenes=[
    K(0, 'THỊ NGỰ SỬ', ('DÂNG LỜI HẶC CẢ NGƯỜI CÓ THẾ', (0, 'dâng'), 'sm'), bg='off2'),
    LD(1, 'VI HOẰNG CƠ · 679', [('CHỨC', 'TƯ NÔNG'), ('XÂY CUNG', 'TÚC VŨ'), ('XÂY CUNG', 'CAO SƠN'), ('XÂY CUNG', 'THƯỢNG DƯƠNG')], bg='lymodel'),
    K(2, 'VI HOẰNG CƠ BỊ CÁCH CHỨC', ('DẪN VUA VÀO CHỖ XA HOA', (2, 'dẫn'), 'sm'), bg='mingtang'),
    K(3, 'VƯƠNG BẢN LẬP', ('ĐƯỢC VUA CHE CHỞ', (3, 'được'), 'sm'), ('NHÀ VUA ĐỊNH THA · ÔNG KHÔNG CHỊU', (4, 'nhà'), 'acc'), bg='off5'),
    QU(6, 'Nếu nhất định tha Bản Lập một cách thiên vị, xin vứt thần ra nơi không người, để răn kẻ trung trinh về sau.', Z202, bg='guard1'),
    K(7, 'BẢN LẬP BỊ TỘI', ('TRIỀU ĐÌNH TỪ ĐÓ NGHIÊM CHỈNH', (7, 'và'), 'sm'), ('CHUYẾN ĐI KHÁC · TÂN ĐƯỜNG THƯ', (8, 'tân'), 'sm'), bg='wu3'),
    P(9, 'guard2', 'LÍNH ĐƯỜNG · TRANH VÁCH MỘ'),
    K(10, 'MẤY TRĂM LÍNH TRỐN', ('BỌN CÒN LẠI CÀNG KÉO ĐÔNG', (10, 'nhưng'), 'sm'), vid='c5'),
    S(11, 'NGƯỜI CÙNG ĐƯỜNG', 'DỄ THÀNH HỌA', bg='warrior'),
    LD(12, 'MỘT TỜ LỆNH', [('CHO PHÉP', 'TỰ THÚ'), ('THẢ', 'NGƯỜI ĐANG GIAM'), ('CẤP', 'LƯƠNG VỀ BÁO TIN')], bg='tguard'),
    K(13, 'CẢ TOÁN LÍNH TỰ TRÓI', ('HOÀNG ĐẾ KHEN: BIẾT TÙY CƠ', (14, 'hoàng'), 'sm'), bg='guardo'),
    SO(15, 4, 'KỲ CHÂU', 'CẢNH BẮT CƯỚP', 'TOÁN LÍNH TỰ NỘP MÌNH', bg='hh2'),
    Q(17, 'NẾU PHIM CÓ MA QUÁI,\nSỬ CÓ GÌ?', bg='dnk_c'),
    MY(19, 'TRONG PHIM', 'ÁN MA QUÁI', 'TRONG HAI BỘ ĐƯỜNG THƯ', 'KHÔNG CÓ VỤ NÀO', (19, 'không'), (19, 'quái'), bg='ministers'),
    K(20, 'ĐIỀU GẦN NHẤT\nLÀ MỘT NGÔI ĐỀN', ('CAO TÔNG ĐI PHẦN DƯƠNG · ÔNG LÀM TRI ĐỐN SỨ', (21, 'cao'), 'sm'), bg='qian4'),
    K(22, 'ĐỀN ĐỐ NỮ', ('MẶC ĐẸP ĐI QUA · GẶP SẤM GIÓ', (23, 'tục'), 'sm'), vid='c1'),
    S(24, 'MẤY VẠN NGƯỜI', 'MỞ ĐƯỜNG VÒNG', bg='sancaih'),
    QU(26, 'Thiên tử đi, Phong Bá quét bụi, Vũ Sư rưới đường, Đố Nữ làm hại gì được?', S1, bg='tzaud'),
    K(27, 'CAO TÔNG KHEN', ('"BẬC ĐẠI TRƯỢNG PHU"', (27, 'bậc'), 'acc'), bg='off3'),
    K(28, 'CHỈ CÓ TRONG HAI BỘ ĐƯỜNG THƯ', ('ÍT NĂM SAU: THỨ SỬ NINH CHÂU', (29, 'ít'), 'sm'), bg='off10'),
    K(30, 'NINH CHÂU', ('CÁC CỤ GIÀ HÁT KHEN THỨ SỬ', (30, 'thấy'), 'sm'), vid='c6'),
    DT(31, 'ĐI XEM XÉT GIANG NAM', '688', bg='map700'),
    CT(33, 1700, ' ĐỀN MIẾU', 'BỊ ĐỐT · THEO TƯ TRỊ THÔNG GIÁM', prefix='HƠN ', bg='bod1'),
    LD(34, 'BỐN NƠI ĐƯỢC GIỮ', [('1', 'HẠ VŨ'), ('2', 'NGÔ THÁI BÁ'), ('3', 'QUÝ TRÁT'), ('4', 'NGŨ VIÊN')], bg='bod2'),
    SO(35, 5, 'ĐỀN MIẾU', 'CẢNH TRỪ TÀ', 'HƠN 1.700 MIẾU BỊ ĐỐT', bg='fengxian'),
    S(37, 'VỪA GIỮ LUẬT', 'VỪA PHÁ MIẾU', bg='dnk_a'),
])
CH['ch06'] = dict(hud={'k': 'CHƯƠNG 06', 't': 'DỰ CHÂU: SÁU BẢY TRĂM GIA ĐÌNH'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    MP(1, 'ht1', ['Dự Châu', 'Lạc Dương']),
    K(2, 'SÁU BẢY TRĂM GIA ĐÌNH\nBỊ BUỘC TỘI', ('NĂM NGHÌN NGƯỜI BỊ TỊCH THU', (2, 'năm'), 'sm'), illus='THEO TƯ TRỊ THÔNG GIÁM', bg='guard1'),
    K(3, 'CƠ QUAN THI HÀNH ÁN THÚC GIỤC', ('TÂU THÌ NHƯ BÊNH NGƯỜI CÓ TỘI', (4, 'tâu'), 'sm'), ('KHÔNG TÂU THÌ TRÁI Ý NHÂN TỪ', (4, 'không'), 'sm'), bg='off6'),
    S(5, 'VIẾT XONG\nRỒI LẠI XÉ', 'THEO CỰU ĐƯỜNG THƯ', vid='c7'),
    QU(7, 'Thần muốn tâu công khai, e như đứng về phía kẻ phản; biết mà không nói, lại e trái ý nhân từ của bệ hạ.', Z204, bg='silk1'),
    K(8, 'VÕ TẮC THIÊN THA CHẾT', ('ĐÀY ĐI PHONG CHÂU', (8, 'đày'), 'acc'), ('ĐOÀN NGƯỜI QUA NINH CHÂU', (9, 'đoàn'), 'sm'), bg='wu2'),
    QU(10, 'Sứ quân Địch của chúng ta đã cứu sống các ngươi sao!', Z204, type_at=11, qline=11, bg='tz'),
    K(12, 'HỌ ĂN CHAY BA NGÀY', ('RỒI MỚI ĐI', (12, 'rồi'), 'sm'), bg='off2'),
    K(13, 'ĐẾN NƠI ĐÀY', ('HỌ LẠI DỰNG BIA CHO ÔNG', (13, 'họ'), 'sm'), vid='c6'),
    K(14, 'THÔNG GIÁM GHI', ('SÁU BẢY TRĂM GIA ĐÌNH BỊ BUỘC TỘI', (14, 'sáu'), 'sm'), ('NĂM NGHÌN NGƯỜI BỊ TỊCH THU', (14, 'năm'), 'sm'), bg='off8'),
    OR(15, ('DỰ CHÂU 688', 'BA CÁCH ĐẾM'), [('BỊ BUỘC TỘI', '600–700 GIA ĐÌNH · THÔNG GIÁM'), ('BỊ TỊCH THU', '5.000 NGƯỜI · THÔNG GIÁM'), ('BỊ ÁN TỬ', '2.000 NGƯỜI · TÂN ĐƯỜNG THƯ')], bg='dnk_t'),
    K(17, 'THEO SỬ: ĐƯỢC THA CHẾT', ('MỘT CUỘC ĐỐI ĐẦU KHÁC', (17, 'một'), 'sm'), bg='qian1'),
    FL(18, 'TỂ TƯỚNG', 'TRƯƠNG QUANG PHỤ', 'Đóng quân ở Dự Châu · để quân tướng đòi hỏi đủ thứ', bg='off7'),
    K(20, 'TRƯƠNG QUANG PHỤ GIẬN', ('HỎI ÔNG CÓ COI THƯỜNG QUAN NGUYÊN SOÁI', (20, 'hỏi'), 'sm'), bg='off3'),
    QU(21, 'Kẻ làm loạn Hà Nam chỉ có Việt vương Trinh. Nay một Trinh chết, vạn Trinh sinh ra.', Z204, bg='guard2'),
    K(22, 'NGƯỜI TRONG THÀNH TRÈO TƯỜNG RA HÀNG', ('ĐẤT THÀNH THÀNH ĐƯỜNG MÒN BỐN PHÍA', (22, 'đông'), 'sm'), vid='c5'),
    S(23, 'GIẾT NGƯỜI ĐÃ HÀNG', 'ĐỂ LẤY CÔNG', bg='warrior'),
    K(24, 'MUỐN CÓ THANH KIẾM\nCHÉM NGỰA CỦA VUA', ('ĐẶT LÊN CỔ TƯỚNG QUÂN', (24, 'để'), 'sm'), bg='hh1'),
    DT(26, 'BỊ GIÁNG LÀM THỨ SỬ PHỤC CHÂU', '688', bg='off3'),
    SO(28, 6, 'DỰ CHÂU', 'NGƯỜI TỐT THẮNG Ở CẢNH CUỐI', 'HỌ ĐƯỢC THA · ÔNG BỊ GIÁNG', bg='off9'),
])

# ---------------------------------------------------------------- hậu kỳ

NEN = {
    'ch00': ['mirror', 'wu1', 'dnk_a', 'ladies', 'hh1', 'off1'],
    'ch01': ['ladies', 'outing', 'concert', 'ministers', 'dnk_t', 'cmodel', 'lych'],
    'ch02': ['dnk_t', 'jar', 'off7', 'off8', 'tz', 'map700', 'ladies', 'silk3'],
    'ch03': ['hanguang', 'lymodel2', 'wu3', 'xian', 'lych', 'off6', 'guard1'],
    'ch04': ['zl1', 'zl2', 'zl3', 'qian1', 'guard2', 'tzaud', 'tz'],
    'ch05': ['off2', 'off3', 'guard1', 'guardo', 'warrior', 'tguard', 'sancaih', 'bod1'],
    'ch06': ['off6', 'off7', 'off8', 'silk1', 'wu2', 'guard2', 'qian1', 'hh1'],
    'ch07': ['wu1', 'wu2', 'wu3', 'stele', 'lymodel', 'hanguang', 'off5', 'mingtang'],
    'ch08': ['off1', 'off4', 'guard1', 'wu3', 'mirror', 'jar', 'dnk_t'],
    'ch09': ['silk1', 'silk2', 'silk3', 'wu2', 'ladies', 'guard2', 'off9'],
    'ch10': ['turk1', 'gokturk', 'turkh', 'mogao', 'wu1', 'off6', 'camel', 'samar'],
    'ch11': ['wu3', 'wu1', 'mingtang', 'wudio', 'wugold', 'qian2', 'concert', 'ladies'],
    'ch12': ['gokturk', 'kol', 'turk2', 'vairo', 'longmen', 'mogao', 'wu2', 'm220'],
    'ch13': ['tomb2', 'dnk_a', 'wu1', 'off10', 'qian3', 'stele', 'coin2', 'ministers'],
}
CARD_TYPES = {'kinetic', 'slam', 'date', 'counter', 'question', 'quote', 'ledger', 'timeline', 'org', 'myth', 'file'}
KIDS = {'ledger': 'rows', 'timeline': 'items', 'file': 'rows', 'map': 'pins', 'org': 'nodes'}


def _norm(w):
    return unicodedata.normalize('NFC', re.sub(r'[^\w]', '', w, flags=re.U)).casefold()


def _anchors(obj):
    """Mọi mốc [dòng, 'từ'] hoặc số nguyên trong cảnh (khoá at/…At)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'at' or k.endswith('At'):
                if isinstance(v, list) and len(v) >= 2 and isinstance(v[0], int) and isinstance(v[1], str):
                    yield v
                elif isinstance(v, int) and not isinstance(v, bool):
                    yield [v, None]
            else:
                yield from _anchors(v)
    elif isinstance(obj, list):
        for x in obj:
            yield from _anchors(x)


def kiem_tra_moc(name, scenes, lines):
    """Mốc phải có thật trong câu; mốc cảnh tăng dần."""
    texts = [(x if isinstance(x, str) else x['t']).split() for x in lines]
    last, errs = (-1, -1), []
    for i, s in enumerate(scenes):
        for a in _anchors(s):
            ln, w = a[0], a[1]
            if ln >= len(texts):
                errs.append(f'{name}#{i}: câu {ln} không tồn tại')
            elif w and _norm(w) not in [_norm(t) for t in texts[ln]]:
                errs.append(f'{name}#{i}: câu {ln} không có chữ {w!r}: {" ".join(texts[ln])}')
        at = s.get('at')
        if i == 0 and at is None:
            continue
        if at is None:
            errs.append(f'{name}#{i}: thiếu at')
            continue
        ln, w = (at, None) if isinstance(at, int) else (at[0], at[1])
        idx = -1
        if w and ln < len(texts):
            toks = [_norm(t) for t in texts[ln]]
            idx = toks.index(_norm(w)) if _norm(w) in toks else -1
        pos = (ln, idx)
        if pos <= last:
            errs.append(f'{name}#{i}: mốc {at!r} không tăng sau {last}')
        last = pos
    return errs


def gan_clip(limit=5):
    """Chọn clip cho cảnh có _vid: mỗi clip ≤ limit lần, không lặp ở hai cảnh vid liền nhau, cách chương khác khi còn lựa chọn."""
    used = Counter()
    last_ch = {}
    for ch, v in CH.items():
        n = int(ch[2:])
        prev = None
        for s in v['scenes']:
            pref = s.pop('_vid', None)
            if not pref:
                continue
            order = pref + [k for k in CLIPS if k not in pref]
            good = [k for k in order if used[k] < limit and k != prev and last_ch.get(k, -9) < n]
            ok = good or [k for k in order if used[k] < limit and k != prev]
            if not ok:
                s.pop('illus', None)
                continue
            k = ok[0]
            used[k] += 1
            last_ch[k] = n
            prev = k
            s['vid'] = CLIPS[k]
    return used


def gan_nen():
    """Cảnh thẻ chưa có nền: gán ảnh tư liệu trong NEN[chương], mỗi ảnh ≤ 4 lần, không trùng cảnh liền trước."""
    used = Counter()
    for ch, sceness in CH.items():
        for s in sceness['scenes']:
            for k in ('bg', 'img'):
                if s.get(k):
                    used[s[k]] += 1
    for ch, v in CH.items():
        prev = None
        for s in v['scenes']:
            if s['type'] in CARD_TYPES and not (s.get('bg') or s.get('img') or s.get('vid')):
                pool = [x for x in NEN[ch] if used[x] < 4 and x != prev] or [x for x in NEN[ch] if x != prev]
                pick = min(pool, key=lambda x: (used[x], NEN[ch].index(x)))
                s['bg'] = pick
                used[pick] += 1
            prev = s.get('bg') or s.get('img')


# Thẻ chương (ch01–ch13): sub là câu/ý có sẵn trong kịch bản (nghịch lý hoặc mốc mở chương), không thêm chữ ngoài lời đọc.
CARDS = {
    'ch01': ('HAI CUỐN SỔ\nĐẶT CẠNH\nNHAU', 'MỘT NGƯỜI RẤT GIỎI PHÁ ÁN', 'replace'),
    'ch02': ('CẬU BÉ NGỒI\nĐỌC SÁCH', 'SINH NĂM 630 · THÁI NGUYÊN · TINH CHÂU', 'replace'),
    'ch03': ('ĐẠI LÝ THỪA,\nVÀ CON SỐ\n17.000', 'THIÊN HOÀNG · THIÊN HẬU', 'replace'),
    'ch04': ('CÂY BÁCH Ở\nCHIÊU LĂNG', 'HAI TƯỚNG LỠ TAY CHẶT CÂY BÁCH', 'replace'),
    'ch05': ('THỨ GẦN VỚI\nMA QUÁI NHẤT', 'KHÔNG CÓ MỘT VỤ ÁN MA QUÁI NÀO', 'replace'),
    'ch06': ('DỰ CHÂU:\nSÁU BẢY TRĂM\nGIA ĐÌNH', 'NĂM 688 · VIỆT VƯƠNG KHỞI BINH, THẤT BẠI', 'prepend'),
    'ch07': ('LẠC DƯƠNG\nDƯỚI TRIỀU\nVÕ CHU', 'NĂM 690 · VÕ TẮC THIÊN LÊN NGÔI, LẬP TRIỀU CHU', 'prepend'),
    'ch08': ('CHỮ "THẬT"\nĐƯỢC NÓI RA', 'MỘT TRONG BA TỂ TƯỚNG BỊ TỐ', 'replace'),
    'ch09': ('MẢNH LỤA\nTRONG ÁO BÔNG', 'ÔNG XÉ MẢNH LỤA Ở ĐẦU CHĂN', 'replace'),
    'ch10': ('TỪ BÀNH\nTRẠCH VỀ\nNGỤY CHÂU', 'BÀNH TRẠCH · HẠN HÁN · DÂN HẾT LƯƠNG', 'replace'),
    'ch11': ('CÔ CHÁU\nHAY MẸ CON', 'NĂM 698 · NGÔI THÁI TỬ CÒN BỎ TRỐNG', 'replace'),
    'ch12': ('BIÊN CƯƠNG,\nHÀ BẮC,\nMỘT PHO TƯỢNG', 'NĂM 697 · XIN BỎ CÁC TRẤN XA Ở TÂY VỰC', 'replace'),
    'ch13': ('NGƯỜI TRONG\nHỒ SƠ, NGƯỜI\nTRONG PHIM', 'SỬ GHI MỘT VIỆC KHÁC: TIẾN CỬ NGƯỜI', 'replace'),
}
CARD_BG = {'ch06': 'wu1', 'ch07': 'wu2'}

CHAPTER_TITLES = ['MỘT CHỮ "THẬT"', 'HAI CUỐN SỔ ĐẶT CẠNH NHAU', 'CẬU BÉ NGỒI ĐỌC SÁCH', 'ĐẠI LÝ THỪA, VÀ CON SỐ 17.000',
                  'CÂY BÁCH Ở CHIÊU LĂNG', 'THỨ GẦN VỚI MA QUÁI NHẤT', 'DỰ CHÂU: SÁU BẢY TRĂM GIA ĐÌNH', 'LẠC DƯƠNG DƯỚI TRIỀU VÕ CHU',
                  'CHỮ "THẬT" ĐƯỢC NÓI RA', 'MẢNH LỤA TRONG ÁO BÔNG', 'TỪ BÀNH TRẠCH VỀ NGỤY CHÂU', 'CÔ CHÁU HAY MẸ CON',
                  'BIÊN CƯƠNG, HÀ BẮC, MỘT PHO TƯỢNG', 'NGƯỜI TRONG HỒ SƠ, NGƯỜI TRONG PHIM']

if __name__ == '__main__':
    sys.modules['gen_scenes'] = sys.modules[__name__]
    other = D / 'gen_scenes2.py'
    module_spec = importlib.util.spec_from_file_location('gen_scenes2', other)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    CH.update(module.CH)
    for ch, (title, sub, mode) in CARDS.items():
        first = CH[ch]['scenes'][0]
        no = str(int(ch[2:]))
        word = json.loads((D / f'{ch}.json').read_text(encoding='utf-8'))['lines'][0]
        word = (word if isinstance(word, str) else word['t']).split()[0]
        card = chapter(no, f'CHƯƠNG {int(no):02d}', title, sub, word)
        if mode == 'replace':       # thẻ chương kế thừa nền/clip của cảnh đầu cũ
            for key in ('_vid', 'bg', 'illus'):
                if first.get(key):
                    card[key] = first[key]
            CH[ch]['scenes'][0] = card
        else:
            card['bg'] = CARD_BG[ch]
            CH[ch]['scenes'].insert(0, card)
    clip_used = gan_clip()
    gan_nen()
    errs = []
    img_uses = Counter(s['img'] for v in CH.values() for s in v['scenes'] if s.get('img'))
    errs += [f'ảnh {k} dùng {n} lần (img > 3)' for k, n in img_uses.items() if n > 3]
    errs += [f'scene dùng phím ảnh lạ: {k}' for v in CH.values() for s in v['scenes'] for k in (s.get('img'), s.get('bg')) if k and k not in IMGS]
    for name, v in CH.items():
        lines = json.loads((D / f'{name}.json').read_text(encoding='utf-8'))['lines']
        errs += kiem_tra_moc(name, v['scenes'], lines)
    if errs:
        print('\n'.join(errs))
        raise SystemExit(f'{len(errs)} lỗi mốc')
    # Cổng nhịp cảnh: phần tử con hiện ≤ 1 s sau đầu cảnh -> neo con theo mốc của cảnh; counter đếm ngay.
    for chapter in CH.values():
        for scene in chapter['scenes']:
            field = KIDS.get(scene.get('type'))
            if field:
                for kid in scene.get(field) or []:
                    if isinstance(kid, dict) and 'at' in kid and scene.get('at') is not None:
                        kid['at'] = scene['at']
            if scene.get('type') == 'counter':
                scene.pop('countAt', None)
    # Nhãn cho ảnh chụp ngày nay / mô hình bảo tàng khi dùng làm nền hay ảnh chính (không để ảnh hiện đại không nhãn).
    NOW = {'zhaoling', 'qian1', 'qian2', 'qian3', 'qian4', 'vairo', 'fengxian', 'longmen', 'tomb1', 'tomb2', 'tomb3', 'wh1'}
    MODEL = {'lymodel', 'lymodel2', 'cmodel', 'cmodel2', 'hanguang', 'wudio', 'mingtang', 'wustat'}
    for chapter in CH.values():
        for scene in chapter['scenes']:
            if scene.get('illus') or scene['type'] in ('split', 'print'):
                continue
            key = scene.get('img') or scene.get('bg')
            if key in NOW:
                scene['illus'] = 'ẢNH NGÀY NAY'
            elif key in MODEL:
                scene['illus'] = 'MÔ HÌNH · BẢO TÀNG'
    used = set()

    def collect(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ('img', 'bg') and isinstance(value, str):
                    used.add(value)
                collect(value)
        elif isinstance(obj, list):
            for value in obj:
                collect(value)

    collect(CH)
    spec_path = D / 'spec.json'
    if not spec_path.exists():
        spec_path.write_text(json.dumps({'title': 'x', 'chapters': list(CH), 'youtube': {}}, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    write(__file__, CH, {key: value for key, value in IMGS.items() if key in used}, GEO, endcardBg='dnk_a')
    spec_mod = D / 'spec_dnk.py'
    if spec_mod.exists():
        s2 = importlib.util.spec_from_file_location('spec_dnk', spec_mod)
        m2 = importlib.util.module_from_spec(s2)
        s2.loader.exec_module(m2)
        m2.apply(CH, CHAPTER_TITLES, sorted(used), IMGS)
    print('clip dùng:', dict(clip_used), '| ảnh img:', len(img_uses), '| ảnh khai:', len(used))
