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
CLIPS = {'c1': '900001', 'c2': '900002', 'c3': '900003', 'c4': '900004', 'c5': '900005', 'c6': '900006', 'c7': '900007', 'c8': '900008'}
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


def BR(a, **kw):
    """Cảnh clip thuần (không chữ). vid nhận khoá clip c1..c8, gan_clip gán số thật."""
    return _fin(sc('broll', _a(a)), **kw)


LINES = {}


def _lines(ch):
    if ch not in LINES:
        raw = json.loads((D / f'{ch}.json').read_text(encoding='utf-8'))['lines']
        LINES[ch] = [x if isinstance(x, str) else x['t'] for x in raw]
    return LINES[ch]


def QX(ch, ln, by, a=None, **kw):
    """Thẻ trích dẫn lấy nguyên văn từ dòng ln của chương ch; a = dòng mở thẻ (câu dẫn) nếu có."""
    return QU(ln if a is None else a, _lines(ch)[ln], by, type_at=ln, qline=ln, **kw)


def NG(x):
    return 'NGUỒN: ' + x


# Nguồn ghi trên thẻ trích dẫn
S1 = 'CỰU ĐƯỜNG THƯ · Q.89'
Z202, Z204, Z205, Z206, Z207 = ('TƯ TRỊ THÔNG GIÁM · Q.%d' % n for n in (202, 204, 205, 206, 207))
BK = 'BÁCH KHOA'
ZZ = 'TƯ TRỊ THÔNG GIÁM'
PD = 'PHỎNG DỰNG'
PDV = 'PHỎNG DỰNG · MINH HỌA CHUNG'

CH = {}

# ---------------------------------------------------------------- CH00–CH06 (kịch bản v3, GH-395)
CH['ch00'] = dict(hud={'k': 'MỞ ĐẦU', 't': 'BA CHỮ CỨU MẠNG'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    BR(None, vid='c1'),                                                         # 0: hình động ngay khung 0
    P(1, 'dnk_a', 'ĐỊCH NHÂN KIỆT · TRANH CỔ', tone='noir', move='in', veil=0.3, focus=[0.5, 0.78]),
    P(2, 'wu2', 'VÕ TẮC THIÊN · TRANH CỔ', tone='noir', move='in', focus=[0.5, 0.3]),
    S((2, 'cam'), 'PHẢN\nLÀ THẬT!', 'LỜI ÔNG NÓI VỚI LAI TUẤN THẦN', bg='mirror', srcnote=NG(Z205)),   # sau giây 10
    Q(3, 'VÌ SAO ÔNG TỰ NHẬN\nMÌNH LÀ KẺ PHẢN?', bg='guard1'),
    FL(4, 'NGƯỜI HỎI CUNG', 'LAI TUẤN THẦN', 'Nắm mạng lưới người tố giác của triều Võ Chu', bg='off5'),
    K(5, 'AI NHẬN NGAY\nLẦN HỎI ĐẦU', ('ĐƯỢC GIẢM ÁN CHẾT', (5, 'thì'), 'sm'), bg='off1'),
    BR(6, vid='c8', illus=PDV),
    K(7, 'MỘT CÂU ĐÁP\nRẤT NGẮN', ('TRƯỚC MẶT VÕ TẮC THIÊN', (7, 'trước'), 'sm'), bg='wu3'),
    S(8, 'BA CHỮ ẤY', 'NẶNG ĐẾN ĐÂU?', bg='dnk_t'),
    P(9, 'ladies', 'TRANH VÁCH MỘ ĐƯỜNG · MINH HỌA', move='in'),
])
CH['ch01'] = dict(hud={'k': 'CHƯƠNG 01', 't': 'CẬU BÉ KHÔNG NGẨNG ĐẦU'}, bgm={'mood': 'quiet', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'x', bg='map700'),                                                  # thẻ chương
    OR(1, ('GIA ĐÌNH', 'LÀM QUAN'), [('ÔNG NỘI', 'TẢ THỪA THƯỢNG THƯ TỈNH'), ('CHA', 'TRƯỞNG SỬ QUỲ CHÂU')], bg='off7', srcnote=NG(S1)),
    K(2, 'ĐIỀU NGƯỜI TA NHỚ', ('LẠI LÀ MỘT CHUYỆN NHỎ HƠN NHIỀU', (2, 'lại'), 'sm'), bg='silk3'),
    P(3, 'off8', 'TƯỢNG GỐM QUAN ĐƯỜNG · MINH HỌA', focus=[0.5, 0.3]),
    BR(4, vid='c2'),
    P(5, 'silk1', PD, tone='color', focus=[0.5, 0.4]),
    K(6, 'CẬU ĐÁP LẠI', ('MỘT CÂU VỀ SAU CÒN ĐƯỢC KỂ', (6, 'một'), 'sm'), bg='off2'),
    QX('ch01', 7, S1, bg='dnk_b'),
    S(8, 'KHÔNG CÚI ĐẦU', 'TRƯỚC TIỂU LẠI', bg='off9'),
    K(9, 'NHIỀU CHỤC NĂM SAU', ('ÔNG SẼ PHẢI CÚI ĐẦU TRƯỚC KẺ CẦM QUYỀN LỚN HƠN', (9, 'ông'), 'sm'), bg='guard1'),
    DT(10, 'ĐỖ MINH KINH · PHÁN TÁ BIỆN CHÂU', '659', bg='off4', srcnote=NG(BK)),
    K(11, 'TIỂU LẠI VU CÁO', ('SỨ GIẢ DIÊM LẬP BẢN ĐẾN XÉT', (12, 'sứ'), 'sm'), bg='off3'),
    K((12, 'Ông'), 'CÂU AI LÀM QUAN\nCŨNG MƠ ĐƯỢC NGHE', bg='tzaud'),
    QX('ch01', 13, S1, bg='jar'),
    BR(14, vid='c6'),
    QX('ch01', 16, S1, a=15, bg='m220'),
    K(17, 'MÂY DỜI ĐI RỒI', ('ÔNG MỚI CHỊU BƯỚC TIẾP', (17, 'ông'), 'sm'), bg='mirror'),
    S((18, 'Nó'), 'MỘT NGƯỜI CON', 'TRƯỚC KHI LÀ MỘT VỊ QUAN', bg='dnk_b'),
    P(19, 'dnk_t', 'ĐỊCH NHÂN KIỆT · TRANG TÁN', move='in', focus=[0.5, 0.3]),
    FL(20, 'ĐỒNG LIÊU · TINH CHÂU', 'TRỊNH SÙNG CHẤT', 'Phải đi sứ nơi xa · mẹ già đang bệnh', bg='off8'),
    K(21, 'ÔNG XIN ĐI THAY', ('SAO NỠ ĐỂ MỘT NGƯỜI MANG NỖI LO NGÀN DẶM', (21, 'sao'), 'sm'), bg='off4'),
    S(22, 'LẬN NHÂN CƠ', 'TRƯỞNG SỬ · NGƯỜI ÔNG TÌM GẶP', bg='off9'),
    OR(23, ('LẬN NHÂN CƠ', 'VÀ LÝ HIẾU LIÊM'), [('BẤT HÒA', 'TRƯỚC LẦN ẤY'), ('HÒA THUẬN', 'SAU LẦN ẤY')], bg='off5'),
    K(24, 'NHẬN PHẦN THIỆT\nVỀ MÌNH', ('LÀM DỊU CẢ MỐI BẤT HÒA CỦA NGƯỜI KHÁC', (24, 'đến'), 'sm'), bg='dnk_c'),
    S(25, 'CHỈ LÀ\nCHUYỆN NHẸ', 'MỘT CHUYẾN ĐI XA THAY BẠN', bg='silk1'),
    Q(26, 'ÔNG SẼ RA SAO KHI PHẢI GÁNH\nMẠNG SỐNG CỦA HAI VỊ TƯỚNG?', bg='tguard'),
])
CH['ch02'] = dict(hud={'k': 'CHƯƠNG 02', 't': 'MƯỜI BẢY NGÀN NGƯỜI VÀ MỘT CÂY BÁCH'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'x', bg='wu3'),
    FL(1, 'THIÊN HẬU', 'VÕ TẮC THIÊN', 'Người ngồi cạnh nhà vua', bg='wu1'),
    DT(2, 'ĐẠI LÝ THỪA · ĐẠI LÝ TỰ · XÉT ÁN', '675', bg='hanguang', srcnote=NG(BK)),
    P(4, 'ministers', PD),
    CT(5, 17000, ' NGƯỜI', 'ÁN TỒN XỬ XONG TRONG MỘT NĂM', bg='off6', srcnote=NG(S1)),
    S(6, 'KHÔNG AI\nKÊU OAN', 'KHÔNG CÓ BẢNG KÊ TỪNG VỤ', bg='guard1'),
    BR(8, vid='c2', illus=PDV),
    K(9, 'LỜI KHEN', ('ĐẾN TAI CẢ TRIỀU ĐÌNH', (9, 'đến'), 'sm'), bg='off3'),
    S(10, 'MỘT CÁI CÂY', 'THỬ DANH TIẾNG ẤY', bg='zl1'),
    DT(11, 'CHIÊU LĂNG · HAI TƯỚNG CHẶT NHẦM MỘT CÂY BÁCH', '676', bg='zl2', srcnote=NG(Z202)),
    LD(12, 'HAI TƯỚNG CHẶT NHẦM', [('TƯỚNG', 'QUYỀN THIỆN TÀI'), ('TƯỚNG', 'PHẠM HOÀI NGHĨA')], bg='zhaoling'),
    K(13, 'LUẬT CHỈ ĐỊNH\nCÁCH CHỨC', ('NHƯNG HOÀNG ĐẾ RA LỆNH GIẾT CẢ HAI', (14, 'nhưng'), 'acc'), bg='zl3'),
    BR(15, vid='c3', illus=PDV),
    K(16, 'MUỐN LÀM NGƯỜI CON\nHIẾU THẢO', ('CAO TÔNG KHÔNG GIẤU LÝ DO', (16, 'cao'), 'sm'), bg='tz'),
    QX('ch02', 17, Z202, bg='tzaud'),
    Q(18, 'AI DÁM CÃI MỘT NGƯỜI\nĐANG NHÂN DANH LÒNG HIẾU VỚI CHA?', bg='off5'),
    S(19, 'ĐỊCH NHÂN KIỆT\nDÁM', 'NÓI TỘI HAI TƯỚNG CHƯA TỚI MỨC CHẾT', bg='dnk_c'),
    K(20, 'HOÀNG ĐẾ NỔI GIẬN', ('ÔNG KHÔNG LUI · ÔNG NÓI TIẾP', (21, 'ông'), 'acc'), bg='qian1'),
    S(22, 'BA CÂU NÓI', 'CÂU CUỐI HỎI ĐÚNG ĐIỀU VUA SỢ NHẤT', bg='guardo'),
])
CH['ch03'] = dict(hud={'k': 'CHƯƠNG 03', 't': 'BA CÂU NÓI TRƯỚC MẶT HOÀNG ĐẾ'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'x', bg='tzaud'),
    QX('ch03', 1, Z202, bg='zl2'),
    K(2, 'NẾU NGÀI LÀ\nNGHIÊU, THUẤN', ('THÌ CHẲNG AI PHẢI SỢ KHI CAN NGÀI', (2, 'thì'), 'sm'), bg='off5', illus=PD),
    S(3, 'CÂU THỨ HAI', 'ÔNG QUAY VỀ LUẬT', bg='guard2'),
    QX('ch03', 4, Z202, bg='qian1'),
    BR(5, vid='c3', illus=PDV),
    S(6, 'CÂU THỨ BA', 'ÔNG DÀNH CHO CUỐI CÙNG', bg='qian2'),
    QX('ch03', 7, Z202, bg='off10'),
    Q(8, 'NẾU CÓ KẺ TRỘM\nMỘT NẮM ĐẤT Ở TRƯỜNG LĂNG?', bg='qian3'),
    K(9, 'VÍ DỤ NHỎ', ('ĐẶT ĐÚNG CHỖ VUA TỰ HÀO LÀ CON HIẾU', (9, 'nhưng'), 'acc'), bg='zl3'),
    LD(10, 'HAI TƯỚNG SAU CUỘC CAN', [('HÌNH PHẠT', 'CÁCH CHỨC · ĐÀY LĨNH NAM'), ('MẠNG SỐNG', 'GIỮ ĐƯỢC')], bg='warrior', srcnote=NG(Z202)),
    K(12, 'VÀI NGÀY SAU', ('ĐƯỢC THĂNG THỊ NGỰ SỬ', (12, 'địch'), 'acc'), ('CHUYÊN HẶC TỘI CÁC QUAN KHÁC', (13, 'đó'), 'sm'), bg='off1'),
    K(14, 'CHỌC GIẬN NHÀ VUA', ('NHẬN VỀ ĐÚNG THỨ VŨ KHÍ ẤY', (14, 'nhận'), 'sm'), ('VÀ DÙNG ĐẾN NƠI ĐẾN CHỐN', (15, 'và'), 'acc'), bg='guard1'),
    LD(16, 'VI HOẰNG CƠ · 679', [('XÂY CUNG', 'TÚC VŨ'), ('XÂY CUNG', 'CAO SƠN'), ('XÂY CUNG', 'THƯỢNG DƯƠNG')], bg='cmodel', srcnote=NG(Z202)),
    K(17, 'DẪN VUA ĐI VÀO\nĐƯỜNG XA HOA', ('VI HOẰNG CƠ BỊ CÁCH CHỨC', (18, 'vi'), 'acc'), vid='c5'),
    K(19, 'VƯƠNG BẢN LẬP', ('ĐƯỢC CHÍNH NHÀ VUA CHE CHỞ', (19, 'kẻ'), 'sm'), ('ÔNG NÓI MỘT CÂU LIỀU HƠN', (19, 'lần'), 'acc'), bg='off6'),
    QX('ch03', 20, Z202, bg='hanguang'),
    K(21, 'BẢN LẬP BỊ TRỊ TỘI', ('TRIỀU ĐÌNH TỀ CHỈNH HẲN', (22, 'từ'), 'sm'), bg='off3'),
    S(23, 'MỘT NGÔI ĐỀN', 'CHẲNG AI TRONG TRIỀU MUỐN CHẠM TỚI', bg='sancaih'),
])
CH['ch04'] = dict(hud={'k': 'CHƯƠNG 04', 't': 'ĐỀN ĐỐ NỮ VÀ MỘT NGÀN BẢY TRĂM NGÔI MIẾU'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'x', bg='hh1'),
    S(1, 'ĐỀN ĐỐ NỮ', 'AI MẶC ĐẸP ĐI QUA SẼ GẶP SẤM GIÓ', bg='sancaih'),
    K(3, 'LÝ XUNG HUYỀN\nĐỔI ĐƯỜNG', ('HÀNG VẠN NGƯỜI BỊ GỌI ĐI ĐÀO ĐẮP', (3, 'hàng'), 'sm'), bg='off6'),
    P(4, 'guard1', PD),
    S(5, 'ÔNG PHẢN ĐỐI', 'VÀ CÓ CÂU ĐÁP RIÊNG', bg='dnk_c'),
    QX('ch04', 6, S1, bg='bod1'),
    K(7, 'CAO TÔNG KHEN', ('"BẬC ĐẠI TRƯỢNG PHU"', (7, 'đại'), 'acc'), ('RỒI BẠN CHỜ MỘT VỤ ÁN MA QUÁI', (8, 'bạn'), 'sm'), bg='off3'),
    MY(9, 'TRONG PHIM', 'ÁN MA QUÁI', 'TRONG HAI BỘ ĐƯỜNG THƯ', 'KHÔNG CÓ VỤ NÀO', (9, 'không'), (9, 'vụ'), bg='ministers'),
    K(10, 'MỘT CÂU GIỄU\nCỢT GIÓ SẤM', ('VỀ SAU ÔNG LÀM THỨ SỬ NINH CHÂU', (11, 'về'), 'sm'), bg='qian3'),
    K(12, 'CÁC CỤ GIÀ\nĐỨNG ĐẦY ĐƯỜNG', ('HÁT KHEN ÔNG', (12, 'mà'), 'acc'), ('NGỰ SỬ QUÁCH HÀN TIẾN CỬ ÔNG', (13, 'một'), 'sm'), vid='c6'),
    S(14, 'KỲ CHÂU', 'ÔNG XỬ LÝ THEO CÁCH KHÁC HẲN', bg='hh2'),
    K(15, 'MẤY TRĂM LÍNH\nĐÀO NGŨ', ('TRỐN VÀO NÚI · CƯỚP NGƯỜI ĐI ĐƯỜNG', (15, 'trốn'), 'sm'), ('BẮT ĐỒNG BỌN THÌ KHÔNG TRỊ NỔI', (16, 'bắt'), 'acc'), bg='tguard'),
    LD(17, 'LỆNH CỦA ÔNG', [('CHO PHÉP', 'TỰ THÚ'), ('THẢ', 'NGƯỜI ĐANG GIAM'), ('CẤP', 'LƯƠNG VỀ BÁO TIN')], bg='warrior'),
    K(18, 'CẢ TOÁN LÍNH\nTỰ TRÓI MÌNH', ('KÉO NHAU VỀ NỘP', (18, 'kéo'), 'acc'), ('NHÀ VUA KHEN: BIẾT TÙY CƠ ỨNG BIẾN', (19, 'nhà'), 'sm'), bg='guardo'),
    K(20, 'LÚC CỨNG, LÚC MỀM', ('NHƯNG ĐỪNG VẼ ÔNG QUÁ HIỀN LÀNH', (21, 'nhưng'), 'acc'), bg='dnk_b'),
    CT(22, 1700, ' NGÔI MIẾU', 'NĂM 688 · GIANG NAM · BỊ ĐỐT', prefix='HƠN ', bg='bod1', srcnote=NG(Z204)),
    LD(24, 'BỐN NƠI ĐƯỢC GIỮ', [('1', 'HẠ VŨ'), ('2', 'NGÔ THÁI BÁ'), ('3', 'QUÝ TRÁT'), ('4', 'NGŨ VIÊN')], bg='bod2'),
    S(25, 'KHÔNG SỢ ĐỀN\nĐỐ NỮ', 'VẪN ĐỐT HƠN 1.700 MIẾU CỦA DÂN', bg='fengxian'),
    Q(26, 'GIỮ LUẬT ĐẾN CÙNG,\nHAY CHỈ GIỮ ĐIỀU ÔNG TIN LÀ ĐÁNG GIỮ?', bg='dnk_a'),
    S(28, 'DỰ CHÂU', 'MỘT VIỆC LUẬT NÀO CŨNG KHÔNG GIẢI QUYẾT NỔI', bg='lych'),
])
CH['ch05'] = dict(hud={'k': 'CHƯƠNG 05', 't': 'DỰ CHÂU: LÁ THƯ VIẾT RỒI LẠI XÉ'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'x', bg='xian'),
    MP(1, 'ht1', ['Dự Châu', 'Lạc Dương']),
    K(2, 'NƠI NGƯỜI TA\nCHỜ ĐẾN LƯỢT', ('BỊ TRỪNG TRỊ', (2, 'đó'), 'acc'), bg='off6'),
    BR(3, vid='c3', illus=PDV),
    S(4, 'AI BỊ LIÊN LỤY?', 'CON SỐ ĐƯỢC KỂ KHÔNG GIỐNG NHAU', bg='guard1'),
    OR(5, ('DỰ CHÂU 688', 'BA CÁCH ĐẾM'), [('BỊ BUỘC TỘI', '600–700 GIA ĐÌNH · THÔNG GIÁM'), ('BỊ TỊCH THU', '5.000 NGƯỜI · THÔNG GIÁM'), ('BỊ ÁN TỬ', '2.000 NGƯỜI · TÂN ĐƯỜNG THƯ')], bg='dnk_t'),
    S(6, 'MỘT CẢ VÙNG\nNGƯỜI', 'DÙ CON SỐ NÀO ĐÚNG', bg='lych'),
    OR(7, ('ÔNG ĐỨNG GIỮA', 'HAI CÁCH SAI'), [('NÓI RA', 'BỊ COI LÀ BÊNH PHẢN'), ('IM LẶNG', 'CÓ THỂ TRÁI Ý VUA')], bg='off5'),
    BR(8, vid='c2', illus=PDV),
    QX('ch05', 9, Z204, bg='silk2'),
    K(10, 'TẤU THƯ VIẾT XONG', ('ÔNG LẠI XÉ', (10, 'ông'), 'acc'), ('RỒI VẪN GỬI MẬT TẤU ĐI', (11, 'rồi'), 'sm'), vid='c7'),
    K(12, 'VÕ TẮC THIÊN ĐỌC', ('ÂN XÁ · ĐÀY ĐẾN PHONG CHÂU', (12, 'và'), 'acc'), bg='wu2'),
    K(13, 'ĐOÀN NGƯỜI BỊ ĐÀY', ('ĐI QUA NINH CHÂU', (13, 'đi'), 'sm'), ('CÁC CỤ GIÀ KHÓC DƯỚI BIA CỦA ÔNG', (13, 'các'), 'acc'), vid='c6'),
    QX('ch05', 14, Z204, bg='stele'),
    P(15, 'stele', PD, tone='color'),
    K(16, 'BA NGÀY ĂN CHAY', ('DƯỚI BIA ẤY RỒI MỚI ĐI TIẾP', (16, 'dưới'), 'sm'), bg='off2'),
    K(17, 'ĐẾN NƠI ĐÀY', ('HỌ LẠI DỰNG THÊM MỘT TẤM BIA KHEN ÔNG', (17, 'họ'), 'acc'), bg='mingtang'),
    S(18, 'ÔNG LÀM ĐIỀU', 'NGƯỜI CÓ QUYỀN KHÔNG THỂ THA', bg='dnk_c'),
    FL(19, 'TƯỚNG ĐÓNG QUÂN Ở DỰ CHÂU', 'TRƯƠNG\nQUANG PHỤ', 'Quân dưới trướng đòi hỏi quá đáng · ông từ chối', bg='off7'),
    K(20, 'ÔNG NÓI THẲNG', ('MỘT LỜI TƯỚNG QUÂN NÀO CŨNG KHÓ NGHE', (20, 'một'), 'sm'), bg='off3'),
    QX('ch05', 21, Z204, bg='guard2'),
    K(22, 'GIẾT KẺ ĐÃ HÀNG\nĐỂ LẤY CÔNG', ('MÁU CHẢY ĐỎ CÁNH ĐỒNG · SINH RA VẠN TRINH', (22, 'máu'), 'sm'), bg='warrior'),
    K(23, 'TRƯƠNG QUANG PHỤ\nTÂU ÔNG BẤT KÍNH', ('ĐỊCH NHÂN KIỆT BỊ GIÁNG', (24, 'địch'), 'acc'), ('THỨ SỬ PHỤC CHÂU', (24, 'thứ'), 'sm'), bg='off9'),
    S(25, 'SÁU BẢY TRĂM\nGIA ĐÌNH', 'ĐỔI LẠI MỘT CHIẾC GHẾ THẤP HƠN', bg='dnk_a'),
    S(26, 'CÁI GIÁ\nBẮT ĐẦU NẶNG', 'HAI NĂM SAU · TRIỀU ĐẠI ĐỔI HỌ', bg='wu1'),
])
CH['ch06'] = dict(hud={'k': 'CHƯƠNG 06', 't': 'TRIỀU VÕ CHU VÀ CUỐN SỔ TỐ GIÁC'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'x', bg='wu2'),
    K(1, 'TỪ NIÊN HIỆU\nTHÙY CỦNG', ('BÀ DÙNG QUAN CHUYÊN TRA TẤN', (1, 'bà'), 'acc'), bg='mingtang'),
    LD(2, 'KHỐC LẠI GIẾT', [('TRƯỚC', 'HÀNG TRĂM NGƯỜI HỌ ĐƯỜNG'), ('SAU ĐÓ', 'HÀNG TRĂM NHÀ ĐẠI THẦN')], bg='guard1', srcnote=NG(ZZ)),
    BR(3, vid='c1', illus=PDV),
    DT(4, 'ĐỊCH NHÂN KIỆT LÀM TỂ TƯỚNG', '691', bg='off1', srcnote=NG(Z204)),
    S(5, 'GẦN QUYỀN LỰC\nGẦN LƯỠI DAO', 'CHIẾC GHẾ TỂ TƯỚNG', bg='off4'),
    K(6, 'VÕ TẮC THIÊN HỎI', ('ÔNG CÓ MUỐN BIẾT AI GIÈM PHA MÌNH?', (6, 'ông'), 'sm'), bg='wu3'),
    QX('ch06', 8, Z204, a=7, bg='wu1'),
    K(9, 'MỘT KHOẢNG TRỐNG', ('ĐỂ CÒN SỐNG CHUNG VỚI CẢ TRIỀU ĐÌNH', (9, 'để'), 'sm'), bg='off5'),
    FL(10, 'KHỐC LẠI', 'LAI TUẤN THẦN', 'Giữ hàng trăm người chuyên làm đơn tố cáo', bg='wu2'),
    K(11, 'CUỐN\nLA CHỨC KINH', ('DẠY CÁCH DỰNG HỒ SƠ VU CÁO', (11, 'dạy'), 'sm'), bg='off6'),
    S(12, 'TÊN NGƯỜI NÀO\nCŨNG THÀNH ĐƠN', 'CÁI MÁY ẤY CHẠY ĐẾN ĐÂU', bg='lymodel2'),
    CT(14, 850, ' NGƯỜI', 'ĐÃ NHẬN TỘI OAN · NGHIÊM THIỆN TƯ XÉT LẠI NĂM 692', prefix='HƠN ', bg='guardo', srcnote=NG(ZZ)),
    K(16, 'RỒI CHÍNH ÔNG', ('BỊ BÈ LŨ KHỐC LẠI VU CÁO · BỊ ĐÀY', (16, 'bị'), 'sm'), bg='off4'),
    K(17, 'NHẬN TỘI OAN', ('KHÔNG PHẢI CHUYỆN HIẾM', (17, 'ở'), 'acc'), ('LỐI THOÁT HÀNG TRĂM NGƯỜI ĐÃ CHỌN', (17, 'nó'), 'sm'), bg='wu3'),
    S(18, 'BẢY NGƯỜI\nBỊ TỐ MƯU PHẢN', 'DANH SÁCH CỦA LAI TUẤN THẦN', bg='off8'),
    LD(19, 'BA TỂ TƯỚNG TRONG BẢY NGƯỜI', [('1', 'NHÂM TRI CỔ'), ('2', 'BÙI HÀNH BẢN'), ('3', 'ĐỊCH NHÂN KIỆT')], bg='off10', srcnote=NG(Z204)),
    BR(20, vid='c4', illus=PDV),
    Q(21, 'ÔNG SẼ LÀM GÌ\nKHI CHỈ CÒN MỘT LẦN ĐƯỢC HỎI?', bg='dnk_a'),
])

# ---------------------------------------------------------------- hậu kỳ

NEN = {
    'ch00': ['mirror', 'ladies', 'off1', 'guard1', 'wu1', 'hh1', 'dnk_t'],
    'ch01': ['ladies', 'outing', 'concert', 'silk3', 'map700', 'off8', 'tz', 'jar', 'camel'],
    'ch02': ['ministers', 'zl1', 'zl2', 'zl3', 'hanguang', 'qian1', 'off6', 'zhaoling'],
    'ch03': ['tzaud', 'qian2', 'qian3', 'guard2', 'warrior', 'zl2', 'sancaih', 'mingtang'],
    'ch04': ['sancaih', 'bod1', 'bod2', 'hh2', 'tguard', 'fengxian', 'guardo', 'camel', 'qian3'],
    'ch05': ['lych', 'xian', 'mingtang', 'guard2', 'silk2', 'stele', 'off2', 'jar'],
    'ch06': ['mingtang', 'lymodel2', 'lymodel', 'guard1', 'off10', 'silk1', 'hanguang', 'stele'],
    'ch07': ['guard1', 'off4', 'tguard', 'mirror', 'jar', 'qian1', 'warrior', 'silk2'],
    'ch08': ['silk3', 'silk1', 'silk2', 'off2', 'off9', 'ladies', 'wu2', 'mirror'],
    'ch09': ['ministers', 'off10', 'wu2', 'silk1', 'hanguang', 'bod2', 'zl1'],
    'ch10': ['turk1', 'gokturk', 'turkh', 'mogao', 'samar', 'kol', 'camel', 'hh1'],
    'ch11': ['turk2', 'gokturk', 'kol', 'warrior', 'hh2', 'sancaih', 'qian3', 'vairo'],
    'ch12': ['mingtang', 'qian2', 'concert', 'ladies', 'wudio', 'wugold', 'stele', 'zl2'],
    'ch13': ['longmen', 'vairo', 'bod1', 'wugold', 'coin2', 'qian3', 'stele', 'tomb2', 'tomb3', 'ministers'],
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


def gan_clip(limit=4):  # long_gate: cap = max(MAX_SAME_CLIP, round(phút/6)) = 4 với 26 phút
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


# Thẻ chương (ch01–ch13): sub là ý có sẵn trong lời đọc của chính chương đó.
CARDS = {
    'ch01': ('CẬU BÉ\nKHÔNG NGẨNG\nĐẦU', 'SINH NĂM 630 · THÁI NGUYÊN', 'replace'),
    'ch02': ('17.000 NGƯỜI\nVÀ MỘT CÂY\nBÁCH', 'NĂM 674 · ĐẠI LÝ THỪA', 'replace'),
    'ch03': ('BA CÂU NÓI\nTRƯỚC MẶT\nHOÀNG ĐẾ', 'CÂU THỨ BA HỎI ĐÚNG ĐIỀU VUA SỢ', 'replace'),
    'ch04': ('ĐỀN ĐỐ NỮ,\nHƠN 1.700\nNGÔI MIẾU', 'LÚC CỨNG · LÚC MỀM', 'replace'),
    'ch05': ('DỰ CHÂU:\nLÁ THƯ VIẾT\nRỒI LẠI XÉ', 'VIỆT VƯƠNG KHỞI BINH RỒI THUA', 'replace'),
    'ch06': ('TRIỀU VÕ CHU\nVÀ CUỐN SỔ\nTỐ GIÁC', 'NĂM 690 · VÕ TẮC THIÊN LÊN NGÔI', 'replace'),
    'ch07': ('LỜI\nNHẬN TỘI', 'CÁI BẪY CỦA LAI TUẤN THẦN', 'replace'),
    'ch08': ('MẢNH LỤA\nTRONG\nÁO BÔNG', 'MỘT CÂY BÚT · MỘT NGHIÊN MỰC', 'replace'),
    'ch09': ('CẬU BÉ CHƯA\nMƯỜI TUỔI', 'CON TRAI LẠC TƯ HỐI', 'replace'),
    'ch10': ('KHI QUÂN\nKHIẾT ĐAN\nGÕ CỬA', 'NĂM 696 · KÝ CHÂU BỊ HẠ', 'replace'),
    'ch11': ('HÀ BẮC\nSAU CƠN GIẶC', 'NĂM 697 · LAI TUẤN THẦN BỊ XỬ TỬ', 'replace'),
    'ch12': ('"VIỆC\nNHÀ TA"', 'NĂM 698 · NGÔI THÁI TỬ', 'replace'),
    'ch13': ('QUỐC LÃO', 'NĂM 700 · ÔNG QUA ĐỜI', 'replace'),
}
CARD_BG = {}

CHAPTER_TITLES = ['BA CHỮ CỨU MẠNG', 'CẬU BÉ KHÔNG NGẨNG ĐẦU', 'MƯỜI BẢY NGÀN NGƯỜI VÀ MỘT CÂY BÁCH', 'BA CÂU NÓI TRƯỚC MẶT HOÀNG ĐẾ',
                  'ĐỀN ĐỐ NỮ VÀ MỘT NGÀN BẢY TRĂM NGÔI MIẾU', 'DỰ CHÂU: LÁ THƯ VIẾT RỒI LẠI XÉ', 'TRIỀU VÕ CHU VÀ CUỐN SỔ TỐ GIÁC',
                  'LỜI NHẬN TỘI', 'MẢNH LỤA TRONG ÁO BÔNG', 'CẬU BÉ CHƯA MƯỜI TUỔI', 'KHI QUÂN KHIẾT ĐAN GÕ CỬA', 'HÀ BẮC SAU CƠN GIẶC',
                  '"VIỆC NHÀ TA"', 'QUỐC LÃO']

# Câu {pd} của script.md (chỉ số dòng trong chNN.json): cảnh bao câu đó phải mang nhãn PHỎNG DỰNG.
PD_LINES = {'ch00': [6], 'ch01': [5], 'ch02': [4, 8, 15], 'ch03': [2, 5], 'ch04': [4], 'ch05': [3, 8, 15], 'ch06': [3, 20],
            'ch07': [3, 4, 21], 'ch08': [4, 10, 21], 'ch09': [3, 6, 21], 'ch10': [3, 8, 23], 'ch11': [11, 17],
            'ch12': [13, 20, 27], 'ch13': [25]}


def kiem_tra_pd(CH):
    errs = []
    for name, lines in PD_LINES.items():
        sc_ = CH[name]['scenes']
        starts = []
        for s in sc_:
            at = s.get('at')
            starts.append(-1 if at is None else (at if isinstance(at, int) else at[0]))
        for ln in lines:
            idx = max(i for i, a in enumerate(starts) if a <= ln)
            if not str(sc_[idx].get('illus') or '').startswith('PHỎNG DỰNG'):
                errs.append(f'{name}: câu {{pd}} #{ln} nằm trong cảnh #{idx} chưa có nhãn PHỎNG DỰNG')
    return errs


def ngat_dong(text, limit=16):
    """Chữ lớn (slam, kinetic không sm): mỗi dòng <= limit ký tự; chỉ ngắt tại dấu cách, giữ dấu xuống dòng sẵn có."""
    out = []
    for line in text.split('\n'):
        cur = ''
        for w in line.split(' '):
            if cur and len(cur) + 1 + len(w) > limit:
                out.append(cur)
                cur = w
            else:
                cur = (cur + ' ' + w) if cur else w
        out.append(cur)
    return '\n'.join(out)


def can_bang_nen(cap=7):
    """Thẻ chữ có nền (bg) bị lặp > cap lần trong cả Long: đổi sang ảnh ít dùng hơn trong NEN[chương] (không đổi cảnh ảnh chính)."""
    used = Counter()
    for v in CH.values():
        for s_ in v['scenes']:
            for k_ in ('bg', 'img'):
                if s_.get(k_):
                    used[s_[k_]] += 1
    for ch, v in CH.items():
        sc_list = v['scenes']
        for i, s_ in enumerate(sc_list):
            k_ = s_.get('bg')
            if not k_ or used[k_] <= cap or s_['type'] not in CARD_TYPES or s_['type'] == 'chapter':
                continue
            near = {sc_list[x].get('bg') or sc_list[x].get('img') for x in (i - 1, i + 1) if 0 <= x < len(sc_list)}
            pool = [x for x in NEN[ch] if used[x] <= 5 and x not in near and x != k_]
            if pool:
                pick = min(pool, key=lambda x: (used[x], NEN[ch].index(x)))
                used[k_] -= 1
                used[pick] += 1
                s_['bg'] = pick
                s_.pop('focus', None)


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
    # long_gate: ảnh dọc làm nền phải có focus (Lead 15/11)
    for v in CH.values():
        for sc_ in v['scenes']:
            if sc_.get('bg') in ('wu1', 'wu2', 'wu3', 'off2', 'off6') and 'focus' not in sc_:
                sc_['focus'] = [0.5, 0.3]
            if 'dnk_a' in (sc_.get('bg'), sc_.get('img')):
                sc_['focus'] = [0.5, 0.78]  # Lead 15/11: tranh dọc, mặt ở 3/4 dưới; 0.3 cắt ra giấy trống
    for v in CH.values():
        for sc_ in v['scenes']:
            if sc_['type'] == 'slam':
                sc_['text'] = ngat_dong(sc_['text'])
            elif sc_['type'] == 'kinetic':
                for it in sc_['items']:
                    if not it.get('sm'):
                        it['text'] = ngat_dong(it['text'])
    gan_nen()
    can_bang_nen()
    VERT = {k_ for k_, f_ in IMGS.items() if any(r_['file'] == f_ and r_['h'] > r_['w'] * 1.1 for r_ in RES)}
    for v in CH.values():
        for sc_ in v['scenes']:
            if sc_.get('bg') in VERT and 'focus' not in sc_ and sc_.get('bg') != 'dnk_a':
                sc_['focus'] = [0.5, 0.3]
    # Lead 16/11 QA img_sheet: mặt nằm thấp, focus 0.3 chỉ ra mũ đen / giấy trắng
    MAT = {'dnk_b': [0.5, 0.55], 'wu1': [0.5, 0.7], 'yao': [0.5, 0.7]}
    for v in CH.values():
        for sc_ in v['scenes']:
            k_ = sc_.get('img') or sc_.get('bg')
            if k_ in MAT:
                sc_['focus'] = MAT[k_]
    errs = kiem_tra_pd(CH)
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
