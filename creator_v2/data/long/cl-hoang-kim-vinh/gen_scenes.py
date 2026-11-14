"""GH-378 bước 4: cảnh biên tập CH00–CH13 cho Long CL "Hoàng Kim Vinh Ngoài Đời Thật".

Trục hình: "bốn mốc, bốn cách kể" (1924, 1930, 1931, 1951): thẻ mốc `date` cùng một khuôn "MỐC n/4 · <cách kể>".
Cảnh so sánh "ba cách kể" dùng `org` (ba cột). Mọi câu [TRÍCH DỊCH] có thẻ `quote` kèm nguồn.
Chạy: python data/long/cl-hoang-kim-vinh/gen_scenes.py (gen_scenes2.py chứa CH07–CH13).
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
from scenekit import sc, kin, write  # noqa: E402

RES = json.loads((ROOT / 'output/long/cl-hoang-kim-vinh/research.json').read_text(encoding='utf-8'))['images']


def im(i, must):
    f = RES[i]['file']
    if must not in f:
        raise ValueError(f'Ảnh {i} không khớp: {f}')
    return f


# Ảnh đã lọc tay qua sheet_0..3 (13/11): chỉ ảnh tư liệu đúng thời kỳ + vài ảnh "ngày nay" có nhãn riêng.
IMGS = {
    'huang': im(109, '黄金荣肖像'), 'cangku': im(110, 'Huangjinrong Cangku'),
    'zhang1': im(112, 'Zhang Siaolin'), 'zhang2': im(121, '張嘯林'),
    'jinling': im(3, 'East Jinling'), 'council': im(6, 'french municipal council'),
    'fc37': im(11, 'French Concession 1937'), 'cenotaph': im(18, 'Bund Cenotaph'),
    'bstone': im(19, 'Boundary stone'), 'pearlmap': im(20, 'Pearl Harbor attack force'),
    'map1884': im(22, 'Shanghai 1884'), 'map1935': im(23, 'Shanghai 1935'),
    'pearl': im(24, 'Pearl Harbor Attack'), 'coupon': im(25, 'Currency issued'),
    'marines': im(26, 'American marines'), 'stamp': im(27, 'Stamp Shanghai'),
    'map1896': im(28, 'mystic flowery land'), 'map1933': im(29, 'Shanghai 1933'),
    'izumo': im(33, 'Izumo'), 'bund30': im(35, '1930 Shanghai'), 'bund90': im(36, 'c1890s'),
    'greatworld': im(51, 'Great World'), 'canton26': im(73, 'Borodin'), 'whampoa': im(74, 'Whampoa3'),
    'nanjingmap': im(77, 'Nationalist government of Nanking'), 'nra': im(78, 'NRA Generals'),
    'chiang16': im(81, '三十歲的蔣介石'), 'chiang26': im(83, 'Chiang1926'),
    'police_ic': im(87, 'native chinese police'), 'opium1': im(88, 'Chinese opium smokers'),
    'opium2': im(89, 'China opium den'), 'patna': im(90, 'Patna'), 'opium3': im(91, 'Lai Afong'),
    'opium4': im(92, 'Opium Smokers - Beijing 1932'), 'opiummap': im(93, 'Map showing where opium'),
    'police_anam': im(125, 'anamites'), 'armored': im(127, 'Automitrailleuse'),
    'nanking1': im(128, 'Nanking Road 1930s'), 'sikh': im(132, 'Sikh 1935'),
    'bundfc': im(133, 'seen from the French Concession'), 'nanking2': im(134, 'c. 1930s'),
    'rueconsul': im(135, 'Rue de Consulate'), 'nanking3': im(136, 'circa 1930s'),
    'tram37': im(137, 'tram map'), 'metropole': im(138, 'Metropole Hotel'), 'map32': im(139, 'Jichisan'),
    'tomb': im(0, 'Tomb of Du Yuesheng'),
}
GEO = {
    'jn': {'countries': ['China'], 'labels': {'China': 'TRUNG QUỐC'}, 'bbox': [117.6, 29.4, 123.6, 32.8], 'box': [260, 110, 1660, 880],
           'pins': [{'name': 'Tô Châu', 'lon': 120.62, 'lat': 31.3, 'label': 'TÔ CHÂU'},
                    {'name': 'Thượng Hải', 'lon': 121.47, 'lat': 31.23, 'label': 'THƯỢNG HẢI'},
                    {'name': 'Hàng Châu', 'lon': 120.15, 'lat': 30.27, 'label': 'HÀNG CHÂU'}]},
    'dn': {'countries': ['China'], 'context': ['Taiwan', 'Vietnam', 'Laos'], 'labels': {'China': 'TRUNG QUỐC'},
           'bbox': [108, 20, 126, 36], 'box': [260, 110, 1660, 880],
           'pins': [{'name': 'Thượng Hải', 'lon': 121.47, 'lat': 31.23, 'label': 'THƯỢNG HẢI'},
                    {'name': 'Hồng Kông', 'lon': 114.17, 'lat': 22.32, 'label': 'HỒNG KÔNG'},
                    {'name': 'Tích Chỉ', 'lon': 121.66, 'lat': 25.06, 'label': 'TÍCH CHỈ'}]},
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
                # vid='c8' hoặc ('c8', 'c7'): ưu tiên theo thứ tự; gan_clip chọn clip còn hạn (mỗi clip ≤ 5 lần, cổng long_gate)
                s['_vid'] = [v] if isinstance(v, str) else list(v)
                s['illus'] = TD
            else:
                s[key] = v
    s.update({k: v for k, v in kw.items() if v is not None})
    return s


def P(a, img, cap, tone=None, move=None, focus=None, **kw):
    return _fin(sc('photo', _a(a), img=img, illus=cap, tone=tone, move=move, focus=focus or [0.5, 0.4]), **kw)


def PR(a, img, k, h, lines, cap=None, right=False, circles=None, tone=None, maxw=None, maxh=None, **kw):
    """Ảnh đặt như tờ in, cột ghi chú bên cạnh. lines: [(chữ, mốc)]; circles: [(x, y, r, mốc)]."""
    s = sc('print', _a(a), img=img, right=right, tone=tone, maxW=maxw, maxH=maxh, caption=cap,
           side={'k': k, 'h': h, 'lines': [{'text': t, 'at': _a(m)} for t, m in lines]})
    if circles:
        s['circles'] = [{'x': x, 'y': y, 'r': r, 'at': _a(m)} for x, y, r, m in circles]
    return _fin(s, **kw)


def K(a, text, *more, **kw):
    a0 = 0 if a is None else _a(a)      # cảnh đầu chương bắt đầu ở 0: mốc dòng 0
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
    """Hai ảnh đối chiếu (split). left/right: (ảnh, nhãn)."""
    s = sc('split', _a(a), title=title, a={'img': left[0], 'label': left[1]}, b={'img': right[0], 'label': right[1]})
    if sign:
        s['sign'] = sign
    return _fin(s, **kw)


def OR(a, root, kids, **kw):
    """Ba cột: nút gốc + các nút con (mỗi con: tên, dòng phụ)."""
    nodes = [{'id': 'r', 't': root[0], 's': root[1], 'cls': 'top', 'at': _a(a)}]
    nodes += [{'id': f'k{i}', 'p': 'r', 't': t, 's': s, 'at': _a(a)} for i, (t, s) in enumerate(kids)]
    return _fin(sc('org', _a(a), nodes=nodes), **kw)


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
    """Lòng thẻ file 872px ≈ 12 ký tự chữ hoa: tách tại '·', rồi chia đôi ở khoảng trắng cân nhất."""
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


CH = {}

# ---------------------------------------------------------------- CH00–CH06
CH['ch00'] = dict(hud={'k': 'MỞ ĐẦU', 't': 'HAI TỜ BÁO, 20/5/1951'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    DT(None, 'HAI TỜ BÁO · THƯỢNG HẢI', '20.05.1951', vid='c4'),
    P(1, 'huang', 'HOÀNG KIM VINH · THẬP NIÊN 1930', focus=[0.5, 0.2]),
    K(3, 'ÔNG VIẾT BẢN TỰ THÚ', bg='nanking3'),
    QU(4, 'Nguyện thẳng thắn thú nhận và hối lỗi trước nhân dân.', 'BẢN TỰ THÚ 1951 · THEO WIKIPEDIA TIẾNG TRUNG', bg='bund30'),
    DT(5, 'MỘT CUỐN SÁCH · MỘT TRANG', '1930', vid='c2'),
    Q(7, 'NGƯỜI NÀO MỚI LÀ ÔNG?', bg='jinling'),
    S(8, 'KHÔNG MỘT CHỮ', 'VỀ THANH BANG', vid='c7'),
    P(10, 'bundfc', 'THƯỢNG HẢI · KHOẢNG 1934'),
    DT(11, 'NĂM ÔNG BỊ BẮT · THEO WIKIPEDIA', '1924', bg='council'),
    Q(12, 'AI BỎ TIỀN?\nBỎ BAO NHIÊU?', bg='police_ic'),
])
CH['ch01'] = dict(hud={'k': 'CHƯƠNG 01', 't': 'BỐN MỐC, BỐN CÁCH KỂ'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, scenes=[
    P(0, 'nanking2', 'THƯỢNG HẢI · NHỮNG NĂM 1930'),
    FL(1, 'PHIM', 'BẾN THƯỢNG HẢI', 'TVB · THÁNG 3/1980', rows=[('SỐ TẬP', '25')], bg='rueconsul'),
    LD(2, 'PHIM · VAI DIỄN', [('CHÂU NHUẬN PHÁT', 'HỨA VĂN CƯỜNG'), ('LỮ LƯƠNG VỸ', 'ĐINH LỰC')], bg='nanking1'),
    S(3, 'ĐÓ LÀ PHIM', 'KHÔNG PHẢI HỒ SƠ', bg='map32'),
    K(5, 'NHỮNG BỘ PHIM KHÁC', bg='metropole'),
    TL(6, [('2015', 'KIÊU HÙNG · DỰA TRÊN ÔNG'), ('2021', '1921 · GỌI THẲNG TÊN')], bg='nanking3'),
    K(7, 'PHIM 1921 · NĂM 2021', ('gọi thẳng tên ông', [7, 'gọi'], 'sm')),
    K(8, 'MỘT PHIM DỰA TRÊN ÔNG', ('MỘT PHIM GỌI TÊN ÔNG', (8, 'gọi'), 'sm'), bg='bund90'),
    K(9, 'GIẤY TỜ THẬT:\nNHIỀU BẢN', vid='c2'),
    DT(11, 'MỐC 1/4 · ĐÊM BỊ BẮT', '1924', bg='council'),
    DT(12, 'MỐC 2/4 · TRANG SÁCH', '1930', bg='nanking2'),
    DT(13, 'MỐC 3/4 · ĐẠI THẾ GIỚI', '1931', bg='jinling'),
    DT(14, 'MỐC 4/4 · BẢN TỰ THÚ', '1951', bg='bundfc'),
    MP(15, 'jn', ['Tô Châu', 'Thượng Hải']),
    LD(16, 'CHỖ CÁC NGUỒN LỆCH', [('NGÀY SINH', '14/12 HOẶC 10/5'), ('TUỔI KHI MẤT', '84 HOẶC 85')], bg='rueconsul'),
])
CH['ch02'] = dict(hud={'k': 'CHƯƠNG 02', 't': 'ĐỨA TRẺ TÔ CHÂU'}, bgm={'mood': 'quiet', 'at': 0, 'gain': 0.12}, scenes=[
    DT(None, 'SINH RA Ở TÔ CHÂU', '1868', vid='c6'),
    MP(2, 'jn', ['Tô Châu', 'Thượng Hải']),
    OR(4, ('NGƯỜI CHA', 'HAI BẢN KỂ'), [('WIKIPEDIA TIẾNG ANH', 'MỞ MỘT QUÁN TRÀ'), ('SÁCH NĂM 1930', 'VÕ QUAN DỰ BỊ')], bg='jinling'),
    K((5, 'võ'), 'QUÁN TRÀ', ('VÕ QUAN DỰ BỊ', (6, 'võ'), 'sm'), bg='rueconsul'),
    S(7, 'CHƯA ĐỦ', 'ĐỂ BIẾT CUỘC ĐỜI NGƯỜI CHA', bg='nanking1'),
    P(8, 'huang', '"HOÀNG RỖ" · CHÂN DUNG THẬP NIÊN 1930', focus=[0.5, 0.2]),
    DT(10, 'HỌC VIỆC · TIỆM ĐÓNG KHUNG TRANH', '1884', vid='c2'),
    QU(12, 'Thuở đầu ông theo nghề giấy quạt, thư họa.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · 1930', bg='nanking3'),
    QU(14, 'Tuổi đôi mươi, ông bỏ nghề buôn, vào làm ở sở bắt của tô giới Pháp ở Thượng Hải.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · 1930', bg='police_anam'),
    CT(16, 1892, '', 'HAI BÁCH KHOA: VÀO SỞ BẮT', frm=1868, year=True, bg='council'),
    LD(17, 'HAI NĂM · HAI NGUỒN', [('1892', 'HAI BÁCH KHOA · 24 TUỔI'), ('1900', 'BÀI BÁO PHỔ THÔNG')], bg='police_ic'),
    DT(19, 'TÔ GIỚI PHÁP · LẬP NGÀY', '06.04.1849', bg='map1884'),
    PR(20, 'map1896', 'BẢN ĐỒ 1896', 'BA CÕI\nTHƯỢNG HẢI', [('LUẬT PHÁP', (20, 'luật')), ('CẢNH SÁT PHÁP RIÊNG', (20, 'cảnh'))],
       cap='THƯỢNG HẢI · SÁCH NĂM 1896', circles=[(0.62, 0.54, 90, (20, 'mảnh'))], tone='color', maxw=1000, maxh=640, right=True),
    K(21, 'SAU CHIẾN TRANH NHA PHIẾN', ('HIỆP ƯỚC BẤT BÌNH ĐẲNG', (21, 'hiệp'), 'sm'), bg='opium1'),
    CT(22, 66, ' HÉCTA', 'TÔ GIỚI PHÁP LÚC MỚI LẬP', bg='stamp'),
    TL(23, [('1849', '66 HÉCTA'), ('1900', 'GẤP ĐÔI'), ('1914', '15 LẦN PHẦN ĐẤT BAN ĐẦU')], bg='map1933'),
    P(25, 'bund90', 'TÔ GIỚI QUỐC TẾ · BẾN THƯỢNG HẢI THẾ KỶ 19'),
    DT(26, 'PHÁP RÚT KHỎI HỘI ĐỒNG CHUNG', '1862', bg='council'),
    OR(27, ('THƯỢNG HẢI', 'BA CÕI'), [('THÀNH PHỐ NGƯỜI HOA', 'LUẬT NHÀ THANH'), ('TÔ GIỚI QUỐC TẾ', 'HỘI ĐỒNG ANH · MỸ'), ('TÔ GIỚI PHÁP', 'CẢNH SÁT PHÁP')], bg='map1884'),
    P(28, 'bundfc', 'RANH GIỚI HAI TÔ GIỚI · KHOẢNG 1934'),
    P(29, 'police_anam', 'CẢNH SÁT TÔ GIỚI PHÁP · KHOẢNG 1908'),
    K(30, 'MỘT THÁM TỬ NGƯỜI HOA', vid='c8'),
    Q(31, 'ÔNG GIỎI ĐẾN MỨC NÀO?', bg='sikh'),
    FL(33, 'THEO WIKIPEDIA TIẾNG ANH', 'MỜI TRỞ LẠI', 'Sau khi cãi sĩ quan Pháp, bỏ về Tô Châu', bg='rueconsul'),
    K(34, 'CÁI GIÁ CỦA\nSỰ CẦN THIẾT', bg='sikh'),
])
CH['ch03'] = dict(hud={'k': 'CHƯƠNG 03', 't': 'CHIẾC GHẾ CỦA NGƯỜI THÁM TỬ'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, scenes=[
    OR(0, ('HOÀNG KIM VINH', 'HAI BẢN KỂ SONG SONG'), [('BẢN 1: CHIẾC GHẾ', 'THÁM TỬ NGƯỜI HOA'), ('BẢN 2: CỬA SAU', 'THUỐC PHIỆN · SÒNG BẠC')], bg='police_anam'),
    P(2, 'council', 'HỘI ĐỒNG TÔ GIỚI PHÁP · 1908'),
    K(3, 'KHÔNG GÁN MỘT NĂM', ('NGUỒN LỆCH NHAU', (3, 'nhau'), 'sm'), bg='police_ic'),
    S(4, 'CỬA SAU', 'BẢN KỂ THỨ HAI', vid='c8'),
    LD((5, 'ông'), 'THEO WIKIPEDIA TIẾNG ANH', [('TỔ CHỨC', 'BUÔN THUỐC PHIỆN'), ('MỞ', 'SÒNG BẠC'), ('BAN ƠN CHO', 'TỘI PHẠM')], bg='opium3'),
    FL(6, 'THEO WIKIPEDIA TIẾNG ANH', 'MỘT PHIÊN\nRIÊNG\nMỖI NGÀY', 'Ông quyết định ai giao cảnh sát, ai được thả', bg='sikh'),
    K(8, 'GIAO CẢNH SÁT', ('HAY THẢ?', (8, 'kẻ'), 'sm'), vid='c1'),
    DT(9, 'CƯỚI BÀ LÂM QUẾ SINH · THEO WIKIPEDIA TIẾNG ANH', '1900', bg='jinling'),
    K(11, 'KHÔNG CHỈ LÀ VỢ\nCỦA MỘT THÁM TỬ', bg='rueconsul'),
    K(12, 'GIAI THOẠI:\nÔNG TỰ DÀN CẢNH CƯỚP', illus='GIAI THOẠI · BÀI BÁO KHÔNG DẪN NGUỒN', bg='nanking1'),
    K(14, 'BÁO TRƯỚC CHO THÁM TỬ PHÁP', ('RỒI BẮT ĐÚNG NHỮNG KẺ ẤY', (14, 'rồi'), 'sm'), illus='GIAI THOẠI · BÀI BÁO KHÔNG DẪN NGUỒN', bg='police_anam'),
    MY(15, 'GIAI THOẠI', 'ÔNG TỰ DÀN CẢNH CƯỚP', 'NGUỒN', 'KHÔNG DẪN NGUỒN NÀO', (15, 'không'), (15, 'nguồn'), bg='council'),
    LD(16, 'NĂM 1913', [('PHÁP XIN', 'QUYỀN CẢNH SÁT'), ('VÀ', 'THU THUẾ NGOÀI TÔ GIỚI')], bg='map1933'),
    K(18, 'ĐỔI LẠI: TRỤC XUẤT\nNGƯỜI CÁCH MẠNG', bg='police_ic'),
    DT(19, 'THỎA THUẬN ĐƯỢC CÔNG BỐ', '1914', bg='map1884'),
    P(20, 'rueconsul', 'KHU PHỐ TÔ GIỚI PHÁP · THẬP NIÊN 1930'),
    K(21, 'QUEN LUÔN NHỮNG KẺ\nHỌ CÓ NHIỆM VỤ BẮT', bg='sikh'),
    OR(23, ('NGƯỜI CẦM HUY HIỆU', 'CẦU NỐI HAI BÊN'), [('CẢNH SÁT PHÁP', 'HUY HIỆU'), ('THẾ GIỚI NGẦM', 'KHU PHỐ')], bg='police_anam'),
    K(24, 'BÊN NÀO CŨNG CẦN ANH TA', ('GIAO NGƯỜI PHẠM TỘI CHO CẢNH SÁT HAY KHÔNG?', (25, 'Theo'), 'sm'), bg='council'),
    Q(26, 'AI Ở NGOÀI\nĐỂ KIỂM TRA?', vid='c8'),
    P(27, 'jinling', 'PHỐ TÔ GIỚI PHÁP · THẬP NIÊN 1930'),
    CT(28, 20, ' NĂM', 'ĐỖ NGUYỆT SANH TRẺ HƠN ÔNG', bg='bund30'),
])
CH['ch04'] = dict(hud={'k': 'CHƯƠNG 04', 't': 'MỘT TRANG SÁCH NĂM 1930'}, bgm={'mood': 'quiet', 'at': 0, 'gain': 0.12}, scenes=[
    DT(0, 'MỐC 2/4 · TRANG SÁCH', '1930', vid='c2'),
    FL(1, 'SÁCH NĂM 1930', 'HẢI THƯỢNG\nDANH NHÂN\nTRUYỆN', 'Truyện các danh nhân Thượng Hải', bg='nanking3'),
    OR(3, ('MỘT CUỐN SÁCH', 'BA MỤC RIÊNG'), [('HOÀNG KIM VINH', 'MỘT MỤC'), ('ĐỖ NGUYỆT SANH', 'MỘT MỤC'), ('TRƯƠNG KHIẾU LÂM', 'MỘT MỤC')], bg='nanking2'),
    K(4, 'MỞ BẰNG GIA THẾ', ('VÀ LÒNG HIẾU THẢO', (4, 'lòng'), 'sm'), bg='jinling'),
    K(5, 'BĂNG CƯỚP THÁI HỒ', ('ÔNG ĐƯỢC LỆNH ĐẾN ĐẤT TÔ', (5, 'được'), 'sm'), vid='c4'),
    K(6, 'ĐI BẮT TÊN ĐẦU BỌN', bg='police_anam'),
    QU(7, 'Tên cướp trèo lên mái nhà, ông cũng trèo lên rồi nhảy xuống, bị thương ở chân.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · MỤC HOÀNG KIM VINH', bg='rueconsul'),
    K(8, 'TRỜI MƯA GIÓ LẠNH\nCHÂN ÔNG VẪN ĐAU', bg='sikh'),
    K(9, 'PHẦN THƯỞNG CỦA NGƯỜI PHÁP', bg='council'),
    LD(10, 'HUÂN CHƯƠNG NGƯỜI PHÁP', [('VÀNG VÀ BẠC', 'HẠNG NHẤT · HẠNG NHÌ'), ('SỐ LẦN', 'BA LẦN')], bg='police_ic'),
    TL(11, [('1921', 'MỘT NĂM TRAO'), ('1924', 'MỘT NĂM TRAO KHÁC'), ('1928', 'MỘT NĂM TRAO NỮA')], bg='nanking1'),
    K(12, 'SÁCH KHÔNG NÓI HUÂN CHƯƠNG NÀO, NĂM NÀO', ('NĂM TÂN HỢI · 1911', (13, 'Tân'), 'sm'), bg='jinling'),
    QU(14, 'Cách mạng Tân Hợi, ông bảo vệ dân, giữ yên địa phương ngày đêm không nghỉ, khiến Thượng Hải gà chó cũng không giật mình.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · MỤC HOÀNG KIM VINH', bg='bund90'),
    K(15, 'ĐẠI TỔNG THỐNG HỌ LÊ', ('HÀM THƯỢNG TÁ BỘ BINH', (15, 'hàm'), 'sm'), bg='council'),
    QU(16, 'Ông có công lớn nhất với tô giới Pháp, tiếng vang đến tận chính phủ Pháp.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · MỤC HOÀNG KIM VINH', type_at=(17, 'Ông'), qline=17, bg='nanking3'),
    K(18, 'TỪ ĐƯỜNG HỌ HOÀNG\nỞ TÀO HÀ KÍNH', bg='map32'),
    CT(20, 1000, '+', 'HỌC TRÒ · TRƯỜNG MIỄN PHÍ KHI SÁCH IN', bg='nanking2'),
    K(21, 'TỪ ĐƯỜNG: NHỚ VỀ NGUỒN CỘI', bg='bundfc'),
    K(22, 'TRƯỜNG KIM VINH', ('TÊN CỦA CHÍNH ÔNG', (22, 'tên'), 'sm'), bg='nanking2'),
    K(24, 'MỘT NHÀ HẢO TÂM', bg='jinling'),
    MY(25, 'TRANG SÁCH', 'MỘT NHÀ HẢO TÂM', 'TRONG MỤC ẤY', 'KHÔNG CÓ CHỮ NÀO VỀ THANH BANG', (25, 'Nhưng'), (25, 'không'), bg='nanking1'),
    K(26, 'KHÔNG BIẾT AI VIẾT', ('KHÔNG BIẾT ÔNG CÓ ĐỌC', (27, 'Ta'), 'sm'), bg='rueconsul'),
    P(28, 'huang', 'MỌI BẢN CHÂN DUNG ĐỀU BỎ BỚT THỨ GÌ ĐÓ', focus=[0.5, 0.2]),
    S(30, 'THUỐC PHIỆN', 'KHÔNG CÓ TRONG TRANG ẤY', bg='opium2'),
    K(31, 'ĐIỀU BỊ BỎ ẤY\nNẰM TRONG MỘT THỨ HÀNG', vid='c5'),
])
CH['ch05'] = dict(hud={'k': 'CHƯƠNG 05', 't': 'THỨ HÀNG NẰM TRONG KHO'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    K(0, 'TRƯỚC TAM HÂM', ('THỨ HÀNG ẤY: THUỐC PHIỆN', (0, 'thuốc'), 'sm'), vid='c5'),
    P(1, 'opium1', 'NGƯỜI HÚT THUỐC PHIỆN · TRANH NĂM 1858'),
    DT(2, 'CHIẾN TRANH NHA PHIẾN LẦN THỨ NHẤT', '1839 – 1842', bg='patna'),
    LD(3, 'HIỆP ƯỚC NAM KINH', [('MỞ', 'NĂM CẢNG'), ('TRONG ĐÓ', 'THƯỢNG HẢI')], bg='bund90'),
    P(4, 'opium3', 'TIỆM HÚT THUỐC PHIỆN · KHOẢNG 1880'),
    DT(5, 'NƯỚC ANH KÝ HIỆP ƯỚC CHẤM DỨT NHẬP KHẨU', '1907', bg='opiummap'),
    DT(6, 'NHÀ THANH SỤP ĐỔ · THUỐC PHIỆN BÙNG LẠI', '1911', vid='c8'),
    PR(7, 'opiummap', 'BẢN ĐỒ 1908', 'NƠI TRỒNG\nTHUỐC PHIỆN', [('MỘT BÀI TỔNG QUAN', (7, 'bài')), ('GIAI ĐOẠN 1928–1937', (7, 'viết'))], cap='TRUNG QUỐC · SÁCH NĂM 1908',
       tone='color', maxw=640, maxh=720, right=True, circles=[(0.4, 0.62, 80, (7, 'Một'))]),
    K(8, 'TƯỞNG PHẢN ĐỐI VỀ ĐẠO ĐỨC', ('NHIỀU BỘ TRƯỞNG: NGUỒN THU QUÝ', (8, 'nhiều'), 'sm'), bg='chiang26'),
    K(9, 'TRONG CÙNG CHÍNH QUYỀN', ('THÁI ĐỘ KHÔNG GIỐNG NHAU', (9, 'thái'), 'sm'), bg='nra'),
    S(10, 'KHÔNG Ở NGƯỜI HÚT', 'MÀ Ở NGƯỜI CẦM CỔNG', vid='c8'),
    FL(12, 'THEO WIKIPEDIA TIẾNG ANH', 'ĐỖ NGUYỆT SANH', 'Gây dựng tài sản bằng buôn thuốc phiện', bg='bund30'),
    P(13, 'cangku', 'KHO HÀNG HOÀNG KIM VINH · ẢNH NGÀY NAY'),
    Q(15, 'AI ĐANG\nGÕ CỬA NHÀ ÔNG?', bg='jinling'),
])
CH['ch06'] = dict(hud={'k': 'CHƯƠNG 06', 't': 'TAM HÂM VÀ CẬU HỌC TRÒ'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, scenes=[
    DT(0, 'ĐỖ NGUYỆT SANH · SINH Ở PHỐ ĐÔNG', '1888', bg='jinling'),
    K(1, 'CẬU VÀO TÔ GIỚI PHÁP', ('LÀM VIỆC VẶT TRONG NHÀ ÔNG', (1, 'làm'), 'sm'), bg='rueconsul'),
    K(2, 'BÀ LÂM QUẾ SINH\nĐỂ MẮT ĐẾN CẬU', bg='nanking2'),
    K(3, 'HOÀNG GIAO ĐỖ QUẢN\nMỘT SỐ ĐIỂM BÁN', vid='c5'),
    LD(4, 'THEO BÁCH KHOA TIẾNG TRUNG · 1918', [('NĂM', '1918'), ('NGƯỜI 1', 'HOÀNG KIM VINH'), ('NGƯỜI 2', 'ĐỖ NGUYỆT SANH'), ('NGƯỜI 3', 'KIM ĐÌNH TÔN')], bg='police_anam'),
    S(6, 'TAM HÂM', 'TÊN CỦA CÔNG TY', bg='nanking1'),
    OR(8, ('CÔNG TY TAM HÂM', 'HAI TRANG, HAI BẢN'), [('BẢN THỨ NHẤT', '1918 · BA NGƯỜI'), ('BẢN THỨ HAI', 'THẬP NIÊN 1920 · THÊM TRƯƠNG KHIẾU LÂM')], bg='bund90'),
    K(9, 'LỆCH VỀ NGƯỜI\nVÀ VỀ NĂM', bg='bund90'),
    S(10, 'KHÔNG LỆCH:', 'TÊN TAM HÂM · THUỐC PHIỆN', bg='opium2'),
    SP(11, 'THẦY VÀ TRÒ', ('police_anam', 'GHẾ CẢNH SÁT · TÔ GIỚI PHÁP'), ('opium3', 'THUỐC PHIỆN · TIỆM HÚT KHOẢNG 1880')),
    K(13, 'HOÀNG KHI ẤY\nCHƯA VÀO THANH BANG', bg='council'),
    K(14, 'ĐỖ VẪN LÀM VIỆC CHO ÔNG', ('CỜ BẠC · THUỐC PHIỆN', (14, 'như'), 'sm'), bg='nanking3'),
    Q(15, 'BẠN THẤY CHỖ LẠ KHÔNG?', bg='rueconsul'),
    DT(17, 'CHÍNH THỨC VÀO BĂNG · THEO WIKIPEDIA', '1927', bg='chiang26'),
    FL(19, 'SÁCH NĂM 1930', 'MỤC CỦA ĐỖ NGUYỆT SANH', 'Mở bằng một câu khác hẳn', bg='jinling'),
    QU(20, 'Ông hào phóng, trọng nghĩa, giúp người lúc cấp.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · MỤC ĐỖ NGUYỆT SANH', bg='police_ic'),
    LD(22, 'MỤC ĐỖ NGUYỆT SANH · CÁC CHỨC', [('GIỚI THƯƠNG NHÂN', 'CHỦ TỊCH HỘI LIÊN HIỆP'), ('TÔ GIỚI', 'ỦY VIÊN NGƯỜI HOA'), ('NGÂN HÀNG', 'CHỦ TỊCH')], bg='nanking2'),
    S(23, 'KHÔNG TAM HÂM', 'KHÔNG THUỐC PHIỆN', vid='c8'),
    QU(25, 'Rồi ông quen ông Hoàng Cẩm Dung và ông Đỗ Nguyệt Sanh, hai bên mến nhau, gặp nhau đã tiếc là muộn.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · MỤC TRƯƠNG KHIẾU LÂM', bg='nanking1'),
    P(26, 'zhang1', 'TRƯƠNG KHIẾU LÂM · THẬP NIÊN 1930', focus=[0.5, 0.25]),
    K(27, 'RẼ SANG MỘT NHÀ HÁT', vid='c1'),
])

# ---------------------------------------------------------------- hậu kỳ

NEN = {
    'ch00': ['bund30', 'jinling', 'nanking1', 'bundfc', 'police_ic'],
    'ch01': ['nanking2', 'rueconsul', 'metropole', 'jinling', 'map32', 'bund90'],
    'ch02': ['map1884', 'bund90', 'stamp', 'police_anam', 'council', 'map1896'],
    'ch03': ['police_ic', 'police_anam', 'council', 'sikh', 'fc37', 'rueconsul', 'jinling'],
    'ch04': ['map32', 'nanking3', 'nanking1', 'jinling', 'bund30'],
    'ch05': ['opium1', 'opium2', 'patna', 'opium3', 'opium4', 'opiummap'],
    'ch06': ['jinling', 'rueconsul', 'nanking2', 'opium3', 'police_anam'],
    'ch07': ['jinling', 'nanking1', 'sikh', 'police_ic', 'council'],
    'ch08': ['rueconsul', 'nanking3', 'jinling', 'map32', 'police_anam'],
    'ch09': ['chiang16', 'chiang26', 'canton26', 'whampoa', 'nra', 'nanking3', 'marines'],
    'ch10': ['bund30', 'nanking1', 'nanking2', 'metropole', 'jinling', 'bundfc'],
    'ch11': ['izumo', 'fc37', 'marines', 'map1935', 'pearl', 'coupon', 'bund30'],
    'ch12': ['nanking3', 'bund30', 'bundfc', 'nanking2', 'jinling'],
    'ch13': ['bund30', 'nanking1', 'bundfc', 'jinling', 'rueconsul'],
}
CARD_TYPES = {'kinetic', 'slam', 'date', 'counter', 'question', 'quote', 'ledger', 'timeline', 'org', 'myth', 'file'}
KIDS = {'ledger': 'rows', 'timeline': 'items', 'file': 'rows', 'map': 'pins', 'org': 'nodes'}
LATE_WORDS = ('cần kiểm', 'webfetch', 'factcheck')


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
    """Mốc phải có thật trong câu; mốc cảnh tăng dần (cảnh sau không neo ngược cảnh trước)."""
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
    """Chọn clip cho cảnh có _vid: theo thứ tự ưu tiên, mỗi clip ≤ limit lần (long_gate: round(phút/6) = 5 cho ~29 phút),
    không lặp clip ở hai cảnh vid liền nhau trong chương và cách chương khác ≥ 1 chương khi còn lựa chọn."""
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
                s.pop('illus', None)       # hết clip: để gan_nen gán ảnh nền
                continue
            k = ok[0]
            used[k] += 1
            last_ch[k] = n
            prev = k
            s['vid'] = CLIPS[k]
    return used


def gan_nen():
    """Cảnh thẻ chưa có nền: gán ảnh tư liệu cùng thời kỳ trong NEN[chương], mỗi ảnh ≤ 4 lần, không trùng cảnh liền trước."""
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


CHAPTER_TITLES = ['HAI TỜ BÁO, 20/5/1951', 'BỐN MỐC, BỐN CÁCH KỂ', 'ĐỨA TRẺ TÔ CHÂU', 'CHIẾC GHẾ CỦA NGƯỜI THÁM TỬ',
                  'MỘT TRANG SÁCH NĂM 1930', 'THỨ HÀNG NẰM TRONG KHO', 'TAM HÂM VÀ CẬU HỌC TRÒ', 'NGƯỜI ĐÀO HÁT VÀ ĐÊM BỊ BẮT',
                  'KHU VƯỜN Ở TÀO HÀ KÍNH', 'MÙA XUÂN 1927', 'ĐẠI THẾ GIỚI', 'NGƯỜI Ở LẠI', 'BẢN TỰ THÚ', 'BA TỜ GIẤY, MỘT NGƯỜI']

if __name__ == '__main__':
    sys.modules['gen_scenes'] = sys.modules[__name__]
    other = D / 'gen_scenes2.py'
    module_spec = importlib.util.spec_from_file_location('gen_scenes2', other)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    CH.update(module.CH)
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
    # Cổng nhịp cảnh (build_long.late_first): phần tử con hiện ≤ 1 s sau đầu cảnh -> neo con theo mốc của cảnh; counter đếm ngay.
    for chapter in CH.values():
        for scene in chapter['scenes']:
            field = KIDS.get(scene.get('type'))
            if field:
                for kid in scene.get(field) or []:
                    if isinstance(kid, dict) and 'at' in kid and scene.get('at') is not None:
                        kid['at'] = scene['at']
            if scene.get('type') == 'counter':
                scene.pop('countAt', None)
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
    write(__file__, CH, {key: value for key, value in IMGS.items() if key in used}, GEO, endcardBg='bund30')
    # spec cuối cùng (youtube, credits, mix...) do spec_hkv.py ghi, vì cần siêu dữ liệu Commons.
    spec_mod = D / 'spec_hkv.py'
    if spec_mod.exists():
        s2 = importlib.util.spec_from_file_location('spec_hkv', spec_mod)
        m2 = importlib.util.module_from_spec(s2)
        s2.loader.exec_module(m2)
        m2.apply(CH, CHAPTER_TITLES, sorted(used), IMGS)
