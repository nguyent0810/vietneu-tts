"""GH-378 bước 4 (v4): cảnh biên tập CH00–CH13 cho Long CL "Hoàng Kim Vinh Ngoài Đời Thật" theo script.md mới (trục nhân vật + cái giá).

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


def B(a, vid, **kw):
    """Cảnh clip toàn khung (không thẻ chữ): dùng cho cảnh mở đầu và cảnh phỏng dựng."""
    return _fin(sc('broll', _a(a)), vid=vid, **kw)


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



# ---------------------------------------------------------------- CH00–CH06 (v4: lời kể mới, trục nhân vật + cái giá)
PDL = 'PHỎNG DỰNG'
PDV = 'PHỎNG DỰNG · MINH HỌA CHUNG'


def pd(cap=None):
    return f'{PDL} · {cap}' if cap else PDL


CH = {}
CH['ch00'] = dict(hud={'k': 'MỞ ĐẦU', 't': 'CÂY CHỔI TRƯỚC ĐẠI THẾ GIỚI'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    B(None, ('c3',)),
    P((0, 'Giới'), 'greatworld', 'ĐẠI THẾ GIỚI · ẢNH NGÀY NAY', tone='night', move='in'),
    P(1, 'huang', pd('HOÀNG KIM VINH · THẬP NIÊN 1930'), tone='noir', move='in', focus=[0.5, 0.2]),
    S(2, 'HOÀNG KIM VINH', 'ÔNG TRÙM BẾN THƯỢNG HẢI', bg='bund30'),
    P(3, 'council', 'SỞ CẢNH SÁT TÔ GIỚI PHÁP · KHOẢNG 1908', tone='noir', move='out'),
    Q(4, 'ĐỐC SÁT TRƯỞNG\nVÀ MỘT CÂY CHỔI?', bg='police_ic'),
    DT(5, 'HAI TỜ BÁO ĐĂNG BẢN TỰ THÚ', '20.05.1951', vid='c7'),
    QU(6, 'Nguyện thẳng thắn thú nhận và hối lỗi trước nhân dân.', 'BẢN TỰ THÚ 1951 · THEO WIKIPEDIA TIẾNG TRUNG', bg='nanking3'),
    P(7, 'jinling', 'ĐẠI LỘ EDWARD VII · THẬP NIÊN 1930', tone='noir', move='pan'),
    K(8, 'GIÓ MÙA ĐÔNG\nQUA SẢNH LỚN', illus=pd(), bg='bundfc'),
    K(9, 'TIẾNG CHỔI\nTRÊN SÀN ĐÁ HOA', illus=pd(), vid='c1'),
    P(10, 'police_anam', 'CẢNH SÁT TÔ GIỚI PHÁP · KHOẢNG 1908', tone='noir'),
    S(11, 'CHỈ CÒN', 'MỘT CÂY CHỔI', bg='nanking2'),
    P(12, 'metropole', 'THƯỢNG HẢI · NHÀ CAO TẦNG ĐANG XÂY, 1930', tone='noir', move='pan'),
    K(13, 'MỌI PHÙ HOA\nKHÉP LẠI', ('BẰNG MỘT CÂY CHỔI', (13, 'bằng'), 'sm'), bg='bund30'),
    DT(14, 'MỘT CUỐN SÁCH DANH NHÂN', '1930', bg='nanking3'),
    S(15, 'CÔNG LỚN', 'VỚI TÔ GIỚI PHÁP', bg='council'),
    S(16, 'KHÔNG MỘT CHỮ', 'VỀ THANH BANG', bg='opium2'),
    Q(17, 'NGƯỜI NÀO\nMỚI LÀ ÔNG?', bg='jinling'),
    SP(18, 'MỘT NGƯỜI, HAI HÌNH ẢNH', ('police_anam', 'CẢNH SÁT TÔ GIỚI PHÁP'), ('opium3', 'TIỆM THUỐC PHIỆN')),
    K(19, 'ĐI DÂY GIỮA\nHAI LẰN RANH', bg='bund90'),
    S(20, 'MỘT CÁI GIÁ', 'RẤT ĐẮT', bg='rueconsul'),
    P(21, 'bund90', 'BẾN THƯỢNG HẢI · THẾ KỶ 19', tone='noir', move='in'),
    MP(22, 'jn', ['Tô Châu', 'Thượng Hải']),
])
CH['ch01'] = dict(hud={'k': 'CHƯƠNG 01', 't': 'ĐỨA TRẺ TÔ CHÂU'}, bgm={'mood': 'quiet', 'at': 0, 'gain': 0.12}, scenes=[
    DT(None, 'SINH RA Ở TÔ CHÂU', '1868', vid=('c6',)),
    P(1, 'huang', 'HOÀNG KIM VINH · THẬP NIÊN 1930', tone='noir', move='in', focus=[0.5, 0.2]),
    S((1, 'khiến'), 'HOÀNG RỖ', 'BIỆT DANH TỪ VẾT SẸO ĐẬU MÙA', bg='bund90'),
    K(3, 'CHA ÔNG LÀ\nVÕ QUAN', ('DỰ BỊ · GIANG TÔ', (3, 'từng'), 'sm'), bg='police_ic'),
    S(4, 'MỘT BẢN KHÁC', 'CHA MỞ QUÁN TRÀ', bg='rueconsul', srcnote='THEO WIKIPEDIA TIẾNG ANH'),
    P(5, 'bund90', pd('BẾN THƯỢNG HẢI THẾ KỶ 19'), tone='noir', move='pan'),
    K(6, 'TÀU NGOẠI QUỐC\nCHEN THUYỀN NAN', illus=pd(), bg='map1884'),
    S(7, 'CƠ HỘI\nVÀ CẠM BẪY', 'CÙNG MỘT TẤC ĐẤT', bg='nanking1'),
    DT(8, 'HỌC VIỆC · TIỆM ĐÓNG KHUNG TRANH', '1884', bg='map1884'),
    K(9, 'ĐÒI HỎI\nTỈ MỈ', bg='nanking3'),
    K(10, 'MÙI GIẤY DÓ\nMỰC NHO, HỒ DÁN', illus=PDV, vid=('c2',)),
    QU(11, 'Thuở đầu ông theo nghề giấy quạt, thư họa.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · 1930', bg='nanking3'),
    S(13, 'NGHỀ GIẤY MỰC', 'KHÔNG GIỮ ÔNG ĐƯỢC LÂU', bg='nanking2'),
    P(14, 'nanking1', pd('PHỐ THƯỢNG HẢI THẬP NIÊN 1930'), tone='noir', move='in'),
    K(15, 'TIỀN TÀI ĐI\nCÙNG QUYỀN LỰC', illus=pd(), bg='stamp'),
    DT(16, 'TÔ GIỚI PHÁP · LẬP NGÀY', '06.04.1849', bg='map1896'),
    CT(17, 66, ' HÉCTA', 'TÔ GIỚI PHÁP LÚC MỚI LẬP', bg='map1884'),
    P(18, 'council', 'HỘI ĐỒNG TÔ GIỚI · KHOẢNG 1908', tone='sepia', move='out'),
    CT(19, 1892, '', 'QUYẾT ĐỊNH BƯỚC NGOẶT', frm=1868, year=True, bg='police_ic'),
    QU(20, 'Tuổi đôi mươi, ông bỏ nghề buôn, vào làm ở sở bắt của tô giới Pháp ở Thượng Hải.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · 1930', bg='police_ic'),
    P(21, 'police_anam', 'CẢNH SÁT TÔ GIỚI PHÁP · KHOẢNG 1908', move='in'),
    S(22, 'CHIẾC ÁO\nCẢNH SÁT', 'MỞ RA CHÂN TRỜI MỚI', bg='bund30'),
    FL(23, 'THEO WIKIPEDIA TIẾNG ANH', 'BỎ VỀ\nTÔ CHÂU', 'Sau một lần cãi sĩ quan Pháp', bg='rueconsul'),
    S(24, 'ĐƯỢC GỌI\nTRỞ LẠI', 'LÀM VIỆC TRONG SỞ BẮT', bg='police_ic'),
    P(25, 'rueconsul', pd('PHỐ TÔ GIỚI PHÁP'), tone='noir', move='pan'),
    K(26, 'NGÕ TỐI\nLÃO BẮC MÔN', illus=pd(), bg='police_ic'),
    P(27, 'sikh', pd('CẢNH SÁT TÔ GIỚI · THẬP NIÊN 1930'), tone='noir', move='out'),
    Q(28, 'LEO ĐẾN ĐỈNH\nBẰNG CÁCH NÀO?', bg='bund30'),
])
CH['ch02'] = dict(hud={'k': 'CHƯƠNG 02', 't': 'CHIẾC HUY HIỆU HAI MẶT'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'TÔ GIỚI PHÁP\nLẤN RỘNG', bg='map1933'),
    TL(1, [('1849', '66 HÉCTA'), ('1900', 'GẤP ĐÔI'), ('1914', 'GẤP 15 LẦN')], bg='map1884'),
    DT(2, 'VIÊN THẾ KHẢI CHẤP THUẬN', '1914', bg='council'),
    K((2, 'đổi'), 'ĐỔI LẠI\nTRỤC XUẤT', ('NGƯỜI LÀM CÁCH MẠNG', (2, 'những'), 'sm'), bg='police_ic'),
    P(3, 'nanking3', pd('PHỐ TÔ GIỚI THẬP NIÊN 1930'), tone='noir', move='pan'),
    S(4, 'MUỐN LÊN CAO\nPHẢI LẬP CÔNG', 'MỘT CÚ LIỀU MẠNG', bg='police_anam'),
    K(6, 'VỤ CƯỚP\nTHÁI HỒ', ('ÔNG PHỤNG MỆNH ĐẾN TÔ CHÂU', (6, 'phụng'), 'sm'), vid=('c6',)),
    MP(7, 'jn', ['Tô Châu', 'Thượng Hải']),
    K(8, 'TRÊN NHỮNG\nMÁI NHÀ CỔ', illus=PDV, vid=('c3',)),
    QU(9, 'Tên cướp trèo lên mái nhà, ông cũng trèo lên rồi nhảy xuống, bị thương ở chân.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · 1930', bg='nanking1'),
    S(10, 'CHÂN ÔNG\nBỊ THƯƠNG NẶNG', 'CÚ NHẢY LIỀU LĨNH', bg='sikh'),
    CT(11, 1930, '', 'TRỜI MƯA GIÓ: CHÂN VẪN ĐAU', frm=1892, year=True, bg='jinling'),
    MY(12, 'GIAI THOẠI', 'ÔNG TỰ DÀN CẢNH CƯỚP', 'NGUỒN', 'KHÔNG DẪN NGUỒN NÀO', (12, 'nhưng'), (12, 'không'), bg='council'),
    K(13, 'CHỈ NÊN NGHE\nNHƯ GIAI THOẠI', bg='police_ic'),
    K(14, 'NGƯỜI PHÁP NỂ\nTHÁM TỬ MẶT RỖ', illus=pd(), bg='police_anam'),
    DT(15, 'CÁCH MẠNG TÂN HỢI · LO GIỮ YÊN', '1911', bg='bund90'),
    QU(16, 'Cách mạng Tân Hợi, ông bảo vệ dân, giữ yên địa phương ngày đêm không nghỉ, khiến Thượng Hải gà chó cũng không giật mình.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · MỤC HOÀNG KIM VINH', bg='nanking3'),
    K(17, 'ĐẠI TỔNG THỐNG\nHỌ LÊ', ('HÀM THƯỢNG TÁ BỘ BINH', (17, 'hàm'), 'sm'), bg='council'),
    TL(18, [('1921', 'HUÂN CHƯƠNG LẦN 1'), ('1924', 'HUÂN CHƯƠNG LẦN 2'), ('1928', 'HUÂN CHƯƠNG LẦN 3')], bg='police_ic'),
    S(19, 'SAU HUÂN CHƯƠNG', 'MỘT THẾ GIỚI NGẦM', vid=('c4',)),
    LD(20, 'NĂM 1900', [('CƯỚI', 'LÂM QUẾ SINH'), ('SAU NÀY', 'QUẢN MỘT PHẦN BUÔN THUỐC PHIỆN')], bg='jinling'),
    K(21, 'MỘT CƠ CHẾ\nHAI MẶT', bg='rueconsul'),
    FL(22, 'THEO WIKIPEDIA TIẾNG ANH', 'MỘT PHIÊN\nRIÊNG\nMỖI NGÀY', 'Ông quyết định ai giao cảnh sát, ai được thả', bg='sikh'),
    K(23, 'ÂN HUỆ CHO\nKẺ PHẠM TỘI', bg='police_ic'),
    PR(24, 'tram37', 'BẢN ĐỒ XE ĐIỆN · 1937', 'XE ĐIỆN\nTRÊN ĐẠI LỘ', [('TIẾNG CHUÔNG LENG KENG', (24, 'tiếng')), ('TÔ GIỚI PHÁP MỞ RỘNG', (24, 'tô'))],
       cap='THƯỢNG HẢI · TUYẾN XE ĐIỆN 1937', tone='color', maxw=600, maxh=780, right=True, illus=pd('MINH HỌA BẰNG BẢN ĐỒ NĂM 1937')),
    K(25, 'MỘT CÁI GẬT ĐẦU', ('ĐỊNH ĐOẠT SỐ PHẬN', (25, 'định'), 'sm'), illus=pd(), bg='opium2'),
    OR(26, ('SỞ BẮT PHÁP', 'NẤC CAO NHẤT'), [('THÁM TỬ', 'NGƯỜI HOA'), ('ĐỐC SÁT', 'TRƯỞNG')], bg='police_anam'),
    S(27, 'HUY HIỆU', 'THÀNH TẤM BÌNH PHONG', bg='council'),
    Q(28, 'THỨ LỢI NHUẬN\nSINH TỪ ĐÂU?', vid=('c5',)),
])
CH['ch03'] = dict(hud={'k': 'CHƯƠNG 03', 't': 'ĐẾ CHẾ KHÓI ĐEN'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'THUỐC PHIỆN\nDÒNG TIỀN ĐEN', vid=('c4',)),
    LD(1, 'HIỆP ƯỚC NAM KINH', [('MỞ', 'NĂM CẢNG'), ('TRONG ĐÓ', 'THƯỢNG HẢI')], bg='bund90'),
    P(2, 'opium1', 'NGƯỜI HÚT THUỐC PHIỆN · TRANH NĂM 1858', move='in'),
    TL(3, [('1907', 'ANH KÝ HIỆP ƯỚC CHẤM DỨT NHẬP'), ('1911', 'THUỐC TRONG NƯỚC BÙNG LẠI')], bg='opiummap'),
    S(4, 'SÒNG BẠC VÀ\nTHUỐC PHIỆN', 'SỐNG NHỜ SỰ LÀM NGƠ', bg='opium2'),
    P(5, 'opium3', 'TIỆM HÚT THUỐC PHIỆN · KHOẢNG 1880', move='out'),
    K(6, 'BÀ LÂM QUẾ SINH', ('QUẢN MỘT PHẦN VIỆC BUÔN', (6, 'quản'), 'sm'), bg='jinling'),
    P(7, 'rueconsul', pd('TÔ GIỚI PHÁP, THẬP NIÊN 1930'), tone='noir', move='in'),
    DT(8, 'ĐỖ NGUYỆT SANH · SINH Ở PHỐ ĐÔNG', '1888', bg='nanking2'),
    FL(9, 'NGƯỜI THANH NIÊN', 'ĐỖ NGUYỆT SANH', 'Phố Đông · vào làm trong dinh thự của Hoàng', bg='bund30'),
    K(11, 'BÀ CHỦ QUÝ CẬU', ('GIAO VIỆC NGÀY MỘT LỚN', (12, 'Từ'), 'sm'), bg='nanking2'),
    LD(13, 'TIỆM HÚT THUỐC PHIỆN', [('CHỦ', 'HOÀNG KIM VINH'), ('NGƯỜI TRÔNG COI', 'ĐỖ NGUYỆT SANH')], bg='opium4'),
    K(14, 'NGƯỜI THỰC THI', ('CỜ BẠC VÀ THUỐC PHIỆN', (14, 'cờ'), 'sm'), bg='police_ic'),
    DT(15, 'CÔNG TY TAM HÂM · LẬP', '1918', bg='map1933'),
    S(16, 'TAM HÂM', 'LŨNG ĐOẠN THUỐC PHIỆN', bg='nanking1'),
    OR(17, ('TAM HÂM', 'CÁC NGUỒN LỆCH'), [('HOÀNG KIM VINH', '1918'), ('ĐỖ NGUYỆT SANH', '1918'), ('TRƯƠNG', 'THẬP NIÊN 1920')], bg='council'),
    K(18, 'CHƯA VÀO\nTHANH BANG', ('DÙ THAO TÚNG ĐƯỜNG DÂY LỚN', (18, 'thao'), 'sm'), bg='police_anam'),
    S(19, 'ĐỨNG BÊN NGOÀI', 'BẢO TRỢ BẰNG HUY HIỆU', bg='council'),
    OR(20, ('BA VAI', 'MỘT ĐƯỜNG DÂY'), [('HOÀNG', 'GHẾ CẢNH SÁT'), ('ĐỖ', 'CỜ BẠC · THUỐC'), ('TRƯƠNG', 'CHUNG ĐƯỜNG')], bg='rueconsul'),
    K(21, 'KHÓI ĐẶC QUÁNH', ('TRONG GÓC TỐI', (21, 'trong'), 'sm'), illus=pd(), bg='opium4'),
    K(22, 'ĐỒNG BẠC HOA', ('LÁCH CÁCH TRÊN BÀN GỖ', (22, 'lách'), 'sm'), illus=pd(), bg='coupon'),
    SP(23, 'HAI LỰC LƯỢNG', ('council', 'QUYỀN LỰC THỰC DÂN'), ('opium2', 'BẠO LỰC GIANG HỒ')),
    S(24, 'NGAI VÀNG', 'VỮNG NHƯ BÀN THẠCH', bg='bund30'),
    K(25, 'NGẠO MẠN', ('ĐẨY ÔNG VÀO CẠM BẪY', (25, 'đẩy'), 'sm'), vid=('c8',)),
])
CH['ch04'] = dict(hud={'k': 'CHƯƠNG 04', 't': 'ĐÒN GHEN Ở NHÀ HÁT'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    DT(None, 'NHỮNG NĂM 1920 · NGOÀI NĂM MƯƠI TUỔI', '1920', vid=('c1',)),
    K((0, 'vừa'), 'VỪA GIỮ GHẾ\nTHÁM TỬ', ('VỪA CẦM ĐẦU ĐƯỜNG DÂY NGẦM', (0, 'cầm'), 'sm'), bg='police_anam'),
    S(1, 'QUÁ NHIỀU\nQUYỀN UY', 'KHÔNG AI KIỀM CHẾ', bg='council'),
    LD(2, 'NĂM 1922', [('ÔNG CƯỚI', 'LỘ LAN XUÂN'), ('NGHỀ', 'CÔ ĐÀO HÁT · CA SĨ SÂN KHẤU')], bg='jinling'),
    P(4, 'nanking2', pd('THƯỢNG HẢI THẬP NIÊN 1930'), tone='noir', move='pan'),
    DT(5, 'ĐÊM BÀ HÁT · MỌI CHUYỆN ĐỔ VỠ', '1924', bg='council'),
    FL(6, 'KHÁN GIẢ ĐÊM ẤY', 'LƯ TIỂU GIA', 'Con trai Lư Vĩnh Tường · quân phiệt phái An Huy', bg='sikh'),
    OR(8, ('ĐÊM ẤY', 'HAI BẢN KỂ'), [('BẢN MỘT', 'LA Ó ĐUỔI BÀ'), ('BẢN KHÁC', 'THEO ĐUỔI BÀ')], bg='nanking1'),
    S(10, 'MỘT TRẬN ĐÒN', 'THUỘC HẠ ĐÁNH CÔNG TỬ', bg='police_ic'),
    K(11, 'ĐÈN RỰC RỠ\nBỖNG IM BẶT', illus=pd(), bg='metropole'),
    P(12, 'armored', pd('THƯỢNG HẢI NĂM 1930'), tone='noir', move='pan'),
    S(13, 'ĐÁNH CÔNG KHAI', 'TRƯỚC MẮT ĐÁM ĐÔNG', bg='nanking3'),
    K(14, 'MỘT BÀI HỌC\nCHO CÔNG TỬ', illus=pd(), bg='bund30'),
    S(15, 'MÙ QUÁNG', 'TRƯỚC THỰC TẾ CHÍNH TRỊ', bg='map1933'),
    PR(16, 'map32', 'BẢN ĐỒ 1932', 'QUYỀN LỰC\nCHỈ TRONG\nTÔ GIỚI', [('ĐỊA GIỚI TÔ GIỚI PHÁP', (16, 'địa')), ('NGOÀI KIA: QUÂN PHIỆT', (17, 'Còn'))],
       cap='THƯỢNG HẢI · BẢN ĐỒ 1932', tone='color', maxw=1000, maxh=640, right=True),
    P(17, 'nra', 'TƯỚNG LĨNH TRUNG HOA · THẬP NIÊN 1920', move='in'),
    K(18, 'CƠN THỊNH NỘ\nCỦA HỌ LƯ', bg='police_ic'),
])
CH['ch05'] = dict(hud={'k': 'CHƯƠNG 05', 't': 'NGƯỜI BỊ BẮT GIỮ'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    DT(None, 'HÔM SAU · ÔNG BỊ BẮT', '1924', bg='council'),
    K(1, 'LƯ VĨNH TƯỜNG\nNỔI GIẬN', illus=pd(), bg='nra'),
    S(2, 'QUÂN ĐỒN TRÚ\nGIỮ ÔNG', 'TRONG TAY QUÂN ĐỘI', bg='armored'),
    K(4, 'NGƯỜI TỪNG\nXÉT XỬ', ('GIỜ NGỒI TRONG GIAN GIAM', (4, 'giờ'), 'sm'), illus=pd(), bg='police_ic'),
    K(5, 'GIÓ BẤC QUA\nSONG SẮT', illus=PDV, vid=('c8',)),
    P(6, 'police_anam', 'CẢNH SÁT TÔ GIỚI PHÁP · KHOẢNG 1908', tone='noir', move='in'),
    DT(7, 'SỞ CẢNH SÁT PHÁP · CHO THÔI VIỆC', '1924', bg='council', srcnote='THEO WIKIPEDIA TIẾNG ANH'),
    K(8, 'NGƯỜI PHÁP\nNÉ QUÂN PHIỆT', illus=pd(), bg='sikh'),
    LD(9, 'WIKIPEDIA TIẾNG ANH', [('BỊ CHO THÔI VIỆC', '1924'), ('LÝ DO', 'ĐÁNH CON QUÂN PHIỆT')], bg='jinling'),
    P(10, 'rueconsul', pd('PHỐ TÔ GIỚI PHÁP, GẦN BỐT MẠCH LAN'), tone='noir', move='out'),
    FL(11, 'SÁCH NĂM 1930', 'CÁCH KỂ KHÁC', 'Mùa đông năm Giáp Tý, tự xin nghỉ', bg='nanking3'),
    QU(12, 'Mùa đông năm Giáp Tý, vì vết thương chân cũ hễ trời âm u là tái phát, ông quyết xin thôi chức đốc sát.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · MỤC HOÀNG KIM VINH', bg='nanking3'),
    QU(13, 'Nhà cầm quyền Pháp một mực giữ lại; ông bất đắc dĩ nhận nghỉ, nhưng sau đó gặp việc vẫn giúp.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · MỤC HOÀNG KIM VINH', bg='jinling'),
    OR(14, ('HAI LỜI CHÉP', 'KHÔNG KHỚP'), [('WIKIPEDIA', 'BỊ CÁCH CHỨC'), ('SÁCH 1930', 'TỰ XIN NGHỈ')], bg='rueconsul'),
    S(15, 'AI ĐÚNG?', 'CÁC NGUỒN CHƯA ĐỦ ĐỂ PHÂN XỬ', bg='nanking1'),
    S(16, 'MẤT HUY HIỆU', 'MẤT CẢ TỰ DO', bg='police_ic'),
    K(17, 'MẠNG SỐNG\nTRONG TAY KẺ THÙ', bg='bund30'),
    Q(18, 'AI ĐỦ SỨC\nGIẢI CỨU ÔNG?', vid=('c5',)),
])
CH['ch06'] = dict(hud={'k': 'CHƯƠNG 06', 't': 'CUỘC GIẢI CỨU VÀ SỰ ĐẢO VAI'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'CHỈ CÒN BIẾT\nTRÔNG CHỜ', ('NHỮNG NGƯỜI ANH EM GIANG HỒ', (0, 'những'), 'sm'), vid=('c8',)),
    MP(1, 'jn', ['Hàng Châu', 'Thượng Hải']),
    P(2, 'zhang1', 'TRƯƠNG KHIẾU LÂM · THẬP NIÊN 1930', move='in', focus=[0.5, 0.25]),
    K(4, 'MŨI QUYẾT ĐỊNH\nỞ THƯỢNG HẢI', ('ĐỖ CHỌN TIỀN', (5, 'Đỗ'), 'acc'), bg='bundfc'),
    CT(6, 1000000, ' ĐỒNG', 'HỒI ỨC: ĐỖ VẬN ĐỘNG GÓP', prefix='HƠN ', bg='nanking3', srcnote='THEO HỒI ỨC WIKIPEDIA DẪN LẠI'),
    LD(7, 'SỐ TIỀN ẤY', [('LO CHO', 'HÀ PHONG LÂM'), ('CHỨC', 'HỘ QUÂN SỨ THƯỢNG HẢI')], bg='police_ic'),
    K(8, 'TÀU XUÔI NGƯỢC', ('TRONG SƯƠNG SỚM', (8, 'trong'), 'sm'), illus=PDV, vid=('c6',)),
    K(9, 'RƯƠNG TIỀN\nGIAO TRONG ĐÊM', illus=PDV, vid=('c5',)),
    S(10, 'ÔNG ĐƯỢC THẢ', 'ĐỖ LÊN NHANH', bg='council'),
    OR(12, ('KẾT NGHĨA', 'BA ĐẠI HANH'), [('HOÀNG KIM VINH', 'SINH 1868'), ('ĐỖ NGUYỆT SANH', 'SINH 1888'), ('TRƯƠNG', 'SINH 1877')], bg='bund30'),
    LD(14, 'TRƯƠNG KHIẾU LÂM · HAI NGUỒN', [('TÊN', 'TRƯƠNG DẦN'), ('QUÊ', 'TỪ KHÊ · CHIẾT GIANG'), ('SINH', '1877')], bg='nanking3'),
    QU(15, 'Rồi ông quen ông Hoàng Cẩm Dung và ông Đỗ Nguyệt Sanh, hai bên mến nhau, gặp nhau đã tiếc là muộn.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · MỤC TRƯƠNG KHIẾU LÂM', bg='nanking1'),
    QU(16, 'Ông hào phóng, trọng nghĩa, giúp người lúc cấp.', 'HẢI THƯỢNG DANH NHÂN TRUYỆN · MỤC ĐỖ NGUYỆT SANH', type_at=(17, 'Ông'), qline=17, bg='police_ic'),
    LD(18, 'CÂU TRUYỀN MIỆNG', [('HOÀNG KIM VINH', 'YÊU TIỀN'), ('TRƯƠNG KHIẾU LÂM', 'GIỎI ĐÁNH'), ('ĐỖ NGUYỆT SANH', 'BIẾT LÀM NGƯỜI')], bg='bund30'),
    S(20, 'CHUYỂN GIAO\nQUYỀN LỰC', 'ÂM THẦM MÀ QUYẾT LIỆT', bg='council'),
    K(21, 'HOÀNG MẤT CHỨC', ('DANH TIẾNG TỔN HẠI', (21, 'danh'), 'sm'), bg='police_anam'),
    S(22, 'ĐỖ VỪA CỨU THẦY', 'VỪA LÊN NHANH', bg='bund30'),
    SP(23, 'ĐỖ ĐIỀU HÀNH', ('opium3', 'THUỐC PHIỆN TÔ GIỚI PHÁP'), ('police_anam', 'CẢNH SÁT NGẦM ỦNG HỘ')),
    S(24, 'HỌC TRÒ', 'CAO HƠN THẦY', bg='nanking2'),
    OR(25, ('THẾ GIỚI NGẦM', 'CÁN CÂN LỆCH'), [('THẦY', 'HOÀNG KIM VINH'), ('TRÒ', 'ĐỖ NGUYỆT SANH')], bg='rueconsul'),
    Q(26, 'NGƯỜI THẦY\nSẼ LÀM GÌ?', bg='rueconsul'),
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


def gan_clip(limit=4):
    """Chọn clip cho cảnh có _vid: theo thứ tự ưu tiên, mỗi clip ≤ limit lần (long_gate: round(phút/6) = 4 cho ≈26 phút ở 4,1 từ/giây; 5 nếu TTS chậm hơn),
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
                if s['type'] == 'broll':
                    raise SystemExit(f'{ch}: hết clip cho cảnh broll at={s.get("at")}: giảm số cảnh vid')
                if s.get('illus') == TD:
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


GENERIC = ['bund30', 'bundfc', 'bund90', 'jinling', 'nanking1', 'nanking2', 'nanking3', 'rueconsul', 'sikh', 'metropole', 'fc37']


def chia_nen():
    """Nền thẻ chữ chỉ là ảnh phố Thượng Hải mờ phía sau: dàn đều các ảnh phố chung, mỗi ảnh ≤ trần, không trùng cảnh liền trước."""
    uses = Counter(s['bg'] for v in CH.values() for s in v['scenes'] if s.get('bg') in GENERIC)
    cap = -(-sum(uses.values()) // len(GENERIC)) + 1
    for ch, v in CH.items():
        prev = None
        for s in v['scenes']:
            bg = s.get('bg')
            if ch != 'ch00' and bg in GENERIC and s['type'] in CARD_TYPES:
                alt = [x for x in GENERIC if x != prev and uses[x] < cap and x != bg]
                if uses[bg] > cap and alt:
                    pick = min(alt, key=lambda x: (uses[x], GENERIC.index(x)))
                    uses[bg] -= 1
                    uses[pick] += 1
                    s['bg'] = bg = pick
            prev = s.get('bg') or s.get('img')


CHAPTER_TITLES = ['CÂY CHỔI TRƯỚC ĐẠI THẾ GIỚI', 'ĐỨA TRẺ TÔ CHÂU', 'CHIẾC HUY HIỆU HAI MẶT', 'ĐẾ CHẾ KHÓI ĐEN',
                  'ĐÒN GHEN Ở NHÀ HÁT', 'NGƯỜI BỊ BẮT GIỮ', 'CUỘC GIẢI CỨU VÀ SỰ ĐẢO VAI', 'KHU VƯỜN ẨN MÌNH',
                  'MÙA XUÂN ĐẪM MÁU 1927', 'SỰ THẬT DƯỚI TRANG SÁCH 1930', 'LÂU ĐÀI CỦA NHỮNG CÁM DỖ',
                  'KẺ Ở LẠI THÀNH PHỐ ĐỔ NÁT', 'BẢN TỰ THÚ MÙA XUÂN 1951', 'CÁI GIÁ CỦA HAI BỜ QUYỀN LỰC']


def kiem_pd():
    """Mỗi câu {pd} trong script.md phải nằm trong cảnh có nhãn PHỎNG DỰNG (storytelling-guide §14.3)."""
    text = (D / 'script.md').read_text(encoding='utf-8')
    parts = re.split(r'^## CH(\d\d)[^\n]*\n', text, flags=re.M)
    errs = []
    for k in range(1, len(parts), 2):
        name, body = f'ch{parts[k]}', parts[k + 1].split('\n## Ghi chú')[0]
        lines = [x for x in body.split('\n') if x.strip() and not x.startswith(('---', '**'))]
        scenes = CH[name]['scenes']
        starts = [0 if s.get('at') is None else (s['at'] if isinstance(s['at'], int) else s['at'][0]) for s in scenes]
        for i, ln in enumerate(lines):
            if '{pd}' in ln:
                j = max(x for x in range(len(scenes)) if starts[x] <= i)
                if 'PHỎNG DỰNG' not in str(scenes[j].get('illus') or ''):
                    errs.append(f'{name}: câu {i} {{pd}} nằm trong cảnh #{j} ({scenes[j]["type"]}) không có nhãn PHỎNG DỰNG')
    return errs


if __name__ == '__main__':
    sys.modules['gen_scenes'] = sys.modules[__name__]
    other = D / 'gen_scenes2.py'
    module_spec = importlib.util.spec_from_file_location('gen_scenes2', other)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    CH.update(module.CH)
    clip_used = gan_clip()
    gan_nen()
    chia_nen()
    print('clip:', dict(clip_used), '· cảnh vid:', sum(clip_used.values()), '· tổng cảnh:', sum(len(v['scenes']) for v in CH.values()))
    errs = kiem_pd()
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
