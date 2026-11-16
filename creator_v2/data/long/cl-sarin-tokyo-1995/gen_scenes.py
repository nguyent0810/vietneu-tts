"""GH-420 bước 4: cảnh biên tập CH00–CH13 cho Long CL "Sarin Tokyo 1995" (cl-sarin-tokyo-1995).

Trục hình: "ba khoản nợ thời gian" (cái tên · mẫu đất · ngày trên lịch) và dòng thời gian giữa hai ngày 27/6/1994 và 20/3/1995.
Ảnh thật tự do (Wikimedia Commons, có ghi công trong spec_sarin.py) + 29 ảnh AI minh họa chung: mọi cảnh dùng ảnh AI đều mang nhãn
PHỎNG DỰNG (câu {pd}) hoặc MINH HỌA CHUNG; không ảnh AI nào mô tả người cụ thể. Clip b-roll: kho chung (minh_hoa_chung) + clip stock Pexels.
Chạy: python data/long/cl-sarin-tokyo-1995/gen_scenes.py (gen_scenes2.py chứa CH07–CH13; spec_sarin.py ghi spec.json).
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

RES = json.loads((ROOT / 'output/long/cl-sarin-tokyo-1995/research.json').read_text(encoding='utf-8'))['images']


def im(i, must):
    f = RES[i]['file']
    if must not in f:
        raise ValueError(f'Ảnh {i} không khớp: {f}')
    return f


IMGS = {
    'tl_chi': im(2, 'Tokyo Chiyoda Line Sarin Attack.jpg'),
    'map_mar': im(10, 'Marunouchi-ogi map sarin attack.png'),
    'map_hib': im(12, 'HibiyaLine ne bound sarin attack.png'),
    'jr1': im(1, 'Japanese-national-railways-203-Mato67-20'),
    'mm8': im(8, 'Tokyo Metro Series 02 02-116F in Yotsuya'),
    'emer3': im(3, 'Emergency personnel respond to the Tokyo'),
    'hz15': im(15, '【地下鉄サリン事件】化学機動中隊の活動の様子.jpg'),
    'sdf16': im(16, '【地下鉄サリン事件】除染を行う自衛隊員.jpg'),
    'sdf17': im(17, '【地下鉄サリン事件】除染を行う自衛隊員と警察官.jpg'),
    'sdf19': im(19, 'Self-defense officers spraying decontami'),
    'conv24': im(24, 'Subway sarin attack 1995.png'),
    'spray25': im(25, 'Subway sarin attack 1995-2.png'),
    'sdf26': im(26, '【地下鉄サリン事件】出発準備完了報告をする自衛隊員（市ヶ谷駐屯地）.jpg'),
    'sdf27': im(27, '【地下鉄サリン事件】除染活動に向かう自衛隊員.jpg'),
    'jeep29': im(29, '地下鉄サリン事件の災害派遣対応での練馬駐屯地出発.jpg'),
    'sat7': im(7, 'サティアン.jpg'),
    'sat36': im(36, 'サティアン②.jpg'),
    'prot20': im(20, 'Anti-Aum Shinrikyo protest.JPG'),
    'psia33': im(33, 'PSIA Aum Shinrikyo facility inspection 0'),
    'psia34': im(34, 'PSIA Aum Shinrikyo facility inspection 0'),
    'motosu40': im(40, 'Lake Motosu03.jpg'),
    'kofu41': im(41, 'Kofu City Hall Kamikuishiki Branch Offic'),
    'cas42': im(42, 'Matsumoto castle01s2048.jpg'),
    'cas54': im(54, 'Matsumoto Castle Keep Tower.jpg'),
    'cas46': im(46, '130608 Matsumoto Castle Matsumoto Nagano'),
    'cas45': im(45, 'Matsumoto Castle09n4592.jpg'),
    'mat55': im(55, 'View to the east of the Metoba River fro'),
    'kasu61': im(61, 'Kasumigaseki Station, Tokyo.jpg'),
    'kasu68': im(68, 'Kasumigaseki Station platforms 20130302.'),
    'kasu78': im(78, 'Tokyo-metro Kasumigaseki-STA Platform2.j'),
    'tsuk119': im(119, 'TokyoMetro-H10-Tsukiji-station-platform.'),
    'tsuk122': im(122, 'Tsukiji station - hibiya line - nov 2014'),
    'tsuk132': im(132, 'Tsukiji-STA Platform1.jpg'),
    'tspol118': im(118, 'Tsukiji Police Station.jpg'),
    'sak117': im(117, 'Omachi Dam park Sakamoto Tatsuhiko cenot'),
    'toky113': im(113, 'Tokyo Station Chuo Line platform.jpg'),
    'mar83': im(83, 'Tokyo Metro Marunouchi Line above Kanda '),
    'hib96': im(96, 'Hibiya Line-2005-10-24 1.jpg'),
    'hib105': im(105, 'Tokyo-Metro Hibiya-STA Platform2.jpg'),
    'ai01': 'EXT:ai:ai_01',
    'ai02': 'EXT:ai:ai_02',
    'ai03': 'EXT:ai:ai_03',
    'ai04': 'EXT:ai:ai_04',
    'ai05': 'EXT:ai:ai_05',
    'ai06': 'EXT:ai:ai_06',
    'ai07': 'EXT:ai:ai_07',
    'ai08': 'EXT:ai:ai_08',
    'ai09': 'EXT:ai:ai_09',
    'ai10': 'EXT:ai:ai_10',
    'ai11': 'EXT:ai:ai_11',
    'ai12': 'EXT:ai:ai_12',
    'ai13': 'EXT:ai:ai_13',
    'ai14': 'EXT:ai:ai_14',
    'ai15': 'EXT:ai:ai_15',
    'ai16': 'EXT:ai:ai_16',
    'ai17': 'EXT:ai:ai_17',
    'ai18': 'EXT:ai:ai_18',
    'ai19': 'EXT:ai:ai_19',
    'ai20': 'EXT:ai:ai_20',
    'ai21': 'EXT:ai:ai_21',
    'ai22': 'EXT:ai:ai_22',
    'ai23': 'EXT:ai:ai_23',
    'ai24': 'EXT:ai:ai_24',
    'ai25': 'EXT:ai:ai_25',
    'ai26': 'EXT:ai:ai_26',
    'ai27': 'EXT:ai:ai_27',
    'ai28': 'EXT:ai:ai_28',
    'ai29': 'EXT:ai:ai_29',
}
GEO = {
    'jp1': {'countries': ['Japan'], 'labels': {'Japan': 'NHẬT BẢN'}, 'bbox': [136.0, 34.6, 141.0, 37.2], 'box': [260, 110, 1660, 880],
            'pins': [{'name': 'Matsumoto', 'lon': 137.97, 'lat': 36.24, 'label': 'MATSUMOTO'},
                     {'name': 'Kamikuishiki', 'lon': 138.6, 'lat': 35.49, 'label': 'KAMIKUISHIKI'},
                     {'name': 'Yokohama', 'lon': 139.64, 'lat': 35.44, 'label': 'KANAGAWA'},
                     {'name': 'Tokyo', 'lon': 139.69, 'lat': 35.69, 'label': 'TOKYO'}]},
}
CLIPS = {'c1': '198013', 'c2': '198012', 'c3': '198011', 'c4': '198014', 'c5': '198015', 'c6': '198005', 'c7': '3192916',
         'c8': '35830059', 'c9': '4296589', 'c10': '8233026', 'c11': '10480415', 'c12': '6980366', 'c13': '8731439',
         'c14': '9160920', 'c15': '33068304', 'c16': '7430218', 'c17': '1793371'}
TD = 'MINH HỌA CHUNG'          # nhãn clip chung (không phải tư liệu của vụ việc)
MC = 'MINH HỌA CHUNG'

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


WK = 'WIKIPEDIA'
NP = 'NIPPON.COM'
AP = 'AP 2025'
AJ = 'AL JAZEERA'
PD = 'PHỎNG DỰNG'
PDV = 'PHỎNG DỰNG · MINH HỌA CHUNG'

CH = {}

CH['ch00'] = dict(hud={'k': 'MỞ ĐẦU', 't': 'SÁNG THỨ HAI'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    BR(None, vid='c1'),                                                        # 0: clip động từ khung 0
    P((0, 'chí'), 'ai03', MC, tone='noir', move='in'),
    P(2, 'mm8', 'TOKYO METRO · ẢNH NGÀY NAY', move='in'),
    Q(3, 'VÌ SAO CẢ NƯỚC NHẬT\nNHÌN NHẦM CHỖ?', bg='ai10', illus=MC),
    P(4, 'ai11', PD, move='in'),
    P(5, 'ai14', PD, move='in'),
    P(6, 'ai12', PD, move='in'),
    S(7, 'NĂM CHUYẾN TÀU', 'KHOẢNG 8 GIỜ SÁNG · 20/3/1995', bg='emer3', srcnote=NG(WK)),
    S(8, '12 ĐẾN 14\nNGƯỜI CHẾT', 'TÙY CÁCH TÍNH', bg='ai29', srcnote=NG(WK)),
    MP(9, 'jp1', ['Matsumoto', 'Tokyo']),
    K(10, 'AI ĐÃ NHÌN\nSANG CHỖ KHÁC?', ('HÃY Ở LẠI · TÔI KỂ TỪNG DẤU HIỆU', (10, 'hãy'), 'sm'), vid='c1'),
])
CH['ch01'] = dict(hud={'k': 'CHƯƠNG 01', 't': 'BA KHOẢN NỢ THỜI GIAN'}, bgm={'mood': 'quiet', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'x', bg='cas42'),
    DT(1, 'GIỮA HAI NGÀY', '1994 → 1995', bg='kasu61', srcnote=NG(WK)),
    K(2, 'KHOẢN THỨ NHẤT', ('MỘT CÁI TÊN', (2, 'một'), 'acc'), ('VÌ SAO CHỌN ÔNG KONO?', (2, 'vì'), 'sm'), bg='ai06', illus=MC),
    S(3, 'KHOẢN THỨ HAI', 'CÂY CỐI CHẾT · MỘT MẪU ĐẤT', bg='motosu40'),
    S(4, 'KHOẢN THỨ BA', 'MỘT NGÀY TRÊN TỜ LỊCH', vid='c14'),
    K(5, 'KHÔNG CHỈ TAY\nVÀO MỘT NGƯỜI', ('HỒ SƠ KHÔNG CHO PHÉP LÀM THẾ', (6, 'hồ'), 'sm'), bg='ai08', illus=MC),
    S(7, 'MỘT CHUỖI\nQUYẾT ĐỊNH', 'MỖI QUYẾT ĐỊNH CÓ LÝ DO RIÊNG', bg='toky113'),
    LD(8, 'TÔI DỰA VÀO', [('BÁO CÁO', 'NIPPON.COM'), ('BẢN TIN', 'AP · 30 NĂM VỤ TÀU ĐIỆN'), ('BẢN TIN', 'PHÁN QUYẾT 2004'), ('VÀ', 'CÁC TRANG BÁCH KHOA')], vid='c15'),
    BR(9, vid='c11'),
    OR(10, ('HAI LOẠI CÂU', 'TÔI SẼ GỌI TÊN'), [('ĐIỀU CÓ DẪN CHỨNG', 'NÓI RÕ NGUỒN'), ('ĐIỀU TÔI SUY ĐOÁN', 'GỌI LÀ GIẢ THUYẾT')], bg='kasu68'),
    S(11, 'PHỎNG DỰNG', 'NHÃN CHO MỖI CẢNH DỰNG LẠI', bg='ai13', illus=PD),
    K(12, 'KHÔNG PHẢI ẢNH CHỤP', ('KHÔNG CÓ LỜI CỦA NGƯỜI THẬT', (12, 'và'), 'sm'), bg='ai14', illus=PD),
    S(13, 'BA CÁCH ĐẾM', 'SỐ NGƯỜI CHẾT · SẼ NÓI Ở ĐÚNG CHỖ', bg='ai19', illus=MC),
    MP(14, 'jp1', ['Matsumoto', 'Kamikuishiki']),
    K(15, 'KHÔNG CẦN BIẾT TRƯỚC\nVỀ NHẬT BẢN', ('CHỈ CẦN ĐI THEO TỪNG NGÀY', (16, 'chỉ'), 'sm'), bg='kasu78'),
    P(17, 'cas54', 'LÂU ĐÀI MATSUMOTO · ẢNH NGÀY NAY', move='in'),
])
CH['ch02'] = dict(hud={'k': 'CHƯƠNG 02', 't': 'MỘT KHU NHÀ YÊN TĨNH'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'x', bg='cas46'),
    P(1, 'cas45', 'LÂU ĐÀI MATSUMOTO · ẢNH NGÀY NAY', move='in'),
    DT(2, 'ĐÊM MATSUMOTO · TỈNH NAGANO', '27/6/1994', bg='mat55', srcnote=NG(WK)),
    P(3, 'ai01', PD, move='in', tone='noir'),
    P(5, 'ai03', PD, move='in'),
    P(6, 'ai02', PD, move='in'),
    S(7, 'KHOẢNG 22 GIỜ 40', 'KHÍ ĐỘC ĐƯỢC THẢ RA GẦN NƠI Ở CỦA CÁC THẨM PHÁN', vid='c10', srcnote=NG(WK)),
    K(8, 'TÒA ÁN SAU NÀY', ('KẾT LUẬN: GIÁO PHÁI AUM SHINRIKYO', (8, 'về'), 'acc'), ('ĐÊM ẤY CẢNH SÁT CHƯA BIẾT GÌ', (9, 'nhưng'), 'sm'), bg='prot20'),
    S(10, '23 GIỜ 30', 'BÁO CÁO KHẨN TỪ CẤP CỨU', bg='ai17', illus=MC),
    P(11, 'ai05', PD, move='in'),
    K(12, 'SÁNG HÔM SAU', ('CÁ CHẾT · CHIM CHẾT · CHÓ CHẾT', (12, 'cá'), 'acc'), vid='c8'),
    S(13, 'SARIN', 'MÁY SẮC KÝ KHÍ KHỐI PHỔ XÁC ĐỊNH', bg='ai07', illus=MC),
    K(14, 'KẾ HOẠCH BAN ĐẦU', ('THẢ KHÍ NGAY TẠI TÒA ÁN THÀNH PHỐ', (14, 'thả'), 'sm'), ('NHƯNG HỌ ĐẾN SAU GIỜ ĐÓNG CỬA', (14, 'nhưng'), 'acc'), bg='kasu61'),
    S(15, 'TÒA NHÀ BA TẦNG', 'NƠI CÁC THẨM PHÁN CỦA THÀNH PHỐ SINH SỐNG', bg='kasu68'),
    K(16, 'MỤC TIÊU', ('CÁC THẨM PHÁN SẮP XỬ VỤ TRANH CHẤP ĐẤT', (16, 'những'), 'acc'), ('AUM CÓ KHẢ NĂNG THUA', (16, 'mà'), 'sm'), bg='cas42'),
    K(17, 'DÂN MATSUMOTO\nPHẢN ĐỐI', ('MỘT VĂN PHÒNG VÀ MỘT NHÀ MÁY CỦA ÔNG ASAHARA', (17, 'một'), 'sm'), bg='mat55'),
    CT(18, 140000, ' CHỮ KÝ', 'KHOẢNG 70% DÂN SỐ THÀNH PHỐ LÚC ẤY', bg='cas54', srcnote=NG(WK)),
    K(19, 'MỘT THÀNH PHỐ NHỎ\nNÓI KHÔNG RẤT RÕ RÀNG', ('BẢY NGƯỜI CHẾT TRONG VÀ NGAY SAU ĐÊM ẤY', (20, 'bảy'), 'acc'), bg='cas46', srcnote=NG(WK)),
    S(21, 'NGƯỜI THỨ TÁM', 'BÀ SUMIKO KONO · SAU 14 NĂM HÔN MÊ', bg='ai28', illus=MC, srcnote=NG(WK)),
    LD(22, 'SỐ NGƯỜI BỊ THƯƠNG', [('MỘT NGUỒN', '144 NGƯỜI'), ('NGUỒN KHÁC', 'HƠN 500 NGƯỜI')], bg='kasu68', srcnote=NG(WK)),
    K(23, 'CÓ CHỖ GHI 274 NGƯỜI\nĐƯỢC ĐIỀU TRỊ', ('CÓ CHỖ TÁCH: 58 NHẬP VIỆN · 253 KHÁM NGOẠI TRÚ', (23, 'tách'), 'sm'), vid='c7', srcnote=NG(WK)),
    S(24, '150 MÉT', 'BÁN KÍNH QUANH TÂM ĐIỂM', bg='ai04', illus=MC),
    K(25, 'TÔI KHÔNG KỂ TÊN\nHAY BỆNH TÌNH', ('VÌ NHIỀU NGƯỜI VẪN CÒN SỐNG', (25, 'vì'), 'sm'), vid='c15'),
    P(26, 'ai07', PD, move='in'),
    P(27, 'ai08', PD, move='in'),
    S(28, 'NGƯỜI GỌI CUỘC\nCẤP CỨU ĐẦU TIÊN', 'LÀ MỘT CƯ DÂN SỐNG NGAY CẠNH ĐÓ', bg='ai05', illus=MC),
    S(29, 'MỤC TIÊU', 'CỦA CHÍNH CÂU HỎI ẤY', vid='c1'),
])
CH['ch03'] = dict(hud={'k': 'CHƯƠNG 03', 't': 'HAI THÂN PHẬN MỘT LÚC'}, bgm={'mood': 'sad', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'x', bg='mat55'),
    FL(1, 'NGƯỜI GỌI CẤP CỨU', 'ÔNG YOSHIYUKI KONO', 'Nghề bán máy móc · sống cạnh bãi đất nơi chiếc xe đỗ', bg='cas45', srcnote=NG(WK)),
    K(2, 'KHI VỢ ÔNG GỤC XUỐNG', ('ÔNG LÀ NGƯỜI GỌI CẤP CỨU ĐẦU TIÊN', (2, 'ông'), 'acc'), bg='ai05', illus=MC),
    BR(3, vid='c6'),
    S(5, 'NẠN NHÂN\nVÀ NGHI PHẠM', 'CÙNG MỘT NGƯỜI', vid='c4'),
    K(6, 'CẢNH SÁT NAGANO', ('COI NHÀ ÔNG LÀ ĐIỂM KHÍ ĐỘC PHÁT RA', (6, 'coi'), 'sm'), bg='kofu41'),
    S(8, 'KHÔNG BAO GIỜ\nBỊ BUỘC TỘI', 'KHÔNG CÓ CÁO BUỘC CHÍNH THỨC NÀO', bg='ai22', illus=MC, srcnote=NG(WK)),
    K(9, 'CHÍN THÁNG', ('THIẾU MỘT KẾT LUẬN CHÍNH THỨC KHÔNG BẢO VỆ ĐƯỢC ÔNG', (9, 'dù'), 'sm'), bg='kasu61'),
    K(10, 'TÔI KHÔNG BIẾT ÔNG\nNGHĨ GÌ', ('VÀ TÔI SẼ KHÔNG DỰNG LỜI CHO ÔNG', (10, 'và'), 'sm'), vid='c15'),
    K(11, 'HỒ SƠ CHỈ CHO TÔI DỮ KIỆN', ('ÔNG GỌI CẤP CỨU · NẰM VIỆN · NHÀ ÔNG BỊ COI LÀ NƠI BẮT ĐẦU', (11, 'ông'), 'sm'), bg='cas46'),
    S(12, 'PHÍA BÊN KIA BÀN', 'TRONG PHÒNG ĐIỀU TRA', bg='ai07', illus=MC),
    P(13, 'ai06', PD, move='in'),
    P(15, 'ai10', PD, move='in'),
    P(16, 'ai06', PD, move='in'),
    K(17, 'BẠN THỬ NGHĨ XEM', ('NHÀ BẠN ĐƯỢC BÁO LÀ ĐIỂM BẮT ĐẦU · AI SẼ NGHE BẠN?', (17, 'ai'), 'sm'), vid='c10'),
    S(18, 'NGHI NGỜ ĐI NHANH', 'HƠN MỌI BẰNG CHỨNG', bg='ai10', illus=MC),
    K(19, 'NGƯỜI BÁO TIN ĐẦU TIÊN', ('THƯỜNG LÀ NGƯỜI BỊ HỎI NHIỀU NHẤT', (19, 'thường'), 'sm'), ('ĐIỀU ĐÓ KHÔNG PHẢI LÚC NÀO CŨNG SAI', (20, 'điều'), 'acc'), bg='kasu68'),
    S(21, 'NHƯNG Ở ĐÂY', 'NÓ ĐÃ DẪN ĐẾN MỘT ĐIỀU SAI', vid='c13'),
    K(22, 'GIẢ THUYẾT CỦA TÔI', ('CÂU TRẢ LỜI GẦN DỄ CHỌN HƠN CÂU TRẢ LỜI XA', (22, 'một'), 'sm'), bg='cas46'),
    S(23, 'Ở CHÂN\nMỘT NGỌN NÚI', 'CẦN THÊM CHÍN THÁNG ĐỂ LỘ RA', bg='motosu40'),
])
CH['ch04'] = dict(hud={'k': 'CHƯƠNG 04', 't': 'KHOẢNG 20 LOẠI HÓA CHẤT'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'x', bg='kasu78'),
    LD(1, 'KHOẢNG 20 LOẠI HÓA CHẤT TRONG NHÀ ÔNG', [('RỬA', 'ẢNH'), ('LÀM', 'GỐM'), ('KÈM', 'MỘT SỐ THUỐC TRỪ SÂU')], bg='ai09', illus=MC, srcnote=NG(WK)),
    S(2, 'KHÔNG THỂ\nĐIỀU CHẾ SARIN', 'TỪ NHỮNG THỨ ẤY', vid='c11'),
    K(3, 'NHƯNG ĐIỀU ĐÓ', ('CHỈ ĐƯỢC BIẾT SAU, RẤT LÂU SAU', (3, 'chỉ'), 'sm'), bg='kasu61'),
    DT(4, 'BÁO ASAHI ĐĂNG Ý KIẾN SỬ GIA KEIICHI TSUNEISHI', '28/6/1994', bg='ai09', illus=MC, srcnote=NG(WK)),
    K(5, 'SARIN CÓ THỂ LÀM TỪ', ('MỘT LOẠI THUỐC TRỪ SÂU', (5, 'một'), 'acc'), vid='c15'),
    DT(6, 'BÀI THỨ HAI CỦA ÔNG', '4/7/1994', bg='kasu78', srcnote=NG(WK)),
    P(7, 'ai07', PD, move='in'),
    P(8, 'ai09', PD, move='in'),
    P(9, 'ai10', PD, move='in'),
    K(10, 'VỀ SAU', ('BỊ COI LÀ SAI', (10, 'bị'), 'acc'), ('NHƯNG ĐÓ LÀ LỜI GIẢI THÍCH NGHE HỢP LÝ NHẤT', (11, 'nhưng'), 'sm'), bg='ai09', illus=MC),
    S((11, 'và'), 'NẰM TRÊN\nMỘT TỜ BÁO LỚN', 'LỜI GIẢI THÍCH ẤY ĐƯỢC ĐĂNG RA CÔNG CHÚNG', vid='c15'),
    K(12, 'THEO BÀI BÁO 2018', ('TIN CẢNH SÁT NAGANO ĐÃ BỊ RÒ RA BÁO CHÍ', (12, 'thông'), 'sm'), ('BIỆT DANH: NGƯỜI KHÍ ĐỘC', (13, 'báo'), 'acc'), bg='kofu41'),
    K(14, 'THƯ CĂM GHÉT\nGỬI ĐẾN NHÀ', ('CẢ NHỮNG LỜI ĐE DỌA GIẾT', (14, 'cả'), 'acc'), bg='ai04', illus=MC),
    K(15, 'MỘT NGHI NGỜ NHỎ', ('LỚN DẦN THÀNH BẢN ÁN TRONG MẮT CÔNG CHÚNG', (15, 'cách'), 'sm'), bg='cas46'),
    BR(16, vid='c5'),
    K(18, 'ÔNG CHƯA BAO GIỜ\nBỊ BUỘC TỘI', ('KHÔNG BỊ BẮT · KHÔNG BỊ ĐƯA RA TÒA', (19, 'ông'), 'sm'), vid='c13'),
    OR(20, ('ÔNG BỊ XỬ', 'Ở NHỮNG NƠI KHÁC'), [('TRÊN MẶT BÁO', ''), ('Ở KHU PHỐ', ''), ('TRONG NHỮNG BỨC THƯ', '')], bg='ai19', illus=MC),
    S(21, 'THUA MỘT VỤ ÁN', 'MÀ KHÔNG CÓ VỤ ÁN NÀO', bg='ai06', illus=MC),
    K(22, 'SAI LẦM ẤY', ('KHÔNG ĐẾN TỪ MỘT KẺ ÁC', (22, 'không'), 'acc'), bg='mat55'),
    S(23, 'MỘT CHUỖI NGƯỜI\nBÌNH THƯỜNG', 'MỖI NGƯỜI NGHE MỘT LỜI · TIN MỘT LỜI · CHUYỂN TIẾP ĐI', bg='kasu78'),
    S(24, 'Ở MỘT NƠI KHÁC', 'CÓ NGƯỜI NHÌN VỀ MỘT HƯỚNG HOÀN TOÀN KHÁC', vid='c9'),
])
CH['ch05'] = dict(hud={'k': 'CHƯƠNG 05', 't': 'MỘT BẢN TIN NỘI BỘ VÀ BA TỈNH'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'x', bg='toky113'),
    K(1, 'CUỐI NĂM 1989', ('LUẬT SƯ TSUTSUMI SAKAMOTO VÀ GIA ĐÌNH BIẾN MẤT', (1, 'luật'), 'sm'), bg='ai04', illus=MC, srcnote=NG(WK)),
    P(2, 'sak117', 'BIA TƯỞNG NIỆM · ẢNH NGÀY NAY', move='in'),
    P(3, 'ai08', PD, move='in'),
    P(4, 'ai09', PD, move='in'),
    K(5, 'MỘT BẢN TIN CỦA AUM', ('PHÁT HÀNH TRƯỚC VỤ MATSUMOTO ĐÃ NHẮC ĐẾN CHẤT ẤY', (5, 'một'), 'sm'), vid='c15'),
    K(6, 'MỘT CÔNG TY LIÊN QUAN', ('ĐÃ MUA HÓA CHẤT CÓ THỂ LÀM RA LOẠI KHÍ NÀY', (6, 'một'), 'sm'), bg='ai07', illus=MC),
    FL(7, 'CỤC TRƯỞNG CỤC HÌNH SỰ', 'TAKASHI KAKIMI', 'Cơ quan Cảnh sát Quốc gia', bg='kasu61', srcnote=NG(WK)),
    K(8, 'THEO ÔNG', ('LÚC ẤY CƠ QUAN NHẬN RA AUM NGUY HIỂM ĐẾN MỨC NÀO', (8, 'đó'), 'sm'), vid='c4'),
    S(9, 'NHẬN RA LÀ MỘT CHUYỆN', 'HÀNH ĐỘNG LÀ CHUYỆN KHÁC', bg='ai06', illus=MC),
    MP(10, 'jp1', ['Matsumoto', 'Kamikuishiki', 'Yokohama']),
    OR(13, ('BA MẢNH', 'CỦA MỘT BỨC TRANH'), [('NAGANO', 'MATSUMOTO'), ('YAMANASHI', 'KAMIKUISHIKI'), ('KANAGAWA', 'VỤ MẤT TÍCH SAKAMOTO')], bg='cas42'),
    K(14, 'CHỈ CẢNH SÁT BA TỈNH', ('CÓ THẨM QUYỀN VỚI AUM', (14, 'có'), 'acc'), bg='kasu68'),
    K(15, 'CHƯA VỤ NÀO LIÊN QUAN\nĐẾN GIÁO PHÁI', ('XẢY RA Ở TOKYO', (15, 'xảy'), 'acc'), bg='toky113'),
    K(16, 'VÌ THẾ', ('CƠ QUAN CẢNH SÁT QUỐC GIA KHÔNG THỂ DỄ DÀNG', (16, 'cơ'), 'sm'), ('ĐƯA ĐIỀU TRA VIÊN GIỎI CỦA TOKYO VÀO CUỘC', (16, 'đưa'), 'acc'), bg='kasu61'),
    S(17, 'LÀM VIỆC RIÊNG', 'ÍT NÓI CHUYỆN VỚI NHAU', vid='c11'),
    S(18, 'KHÔNG HỎNG VÌ\nMỘT NGƯỜI LƯỜI', 'NÓ CHẬM VÌ MỖI TẦNG ĐỀU CẨN THẬN', bg='ai06', illus=MC),
    FL(20, 'NGƯỜI VIẾT ĐIỂM SÁCH', 'YUSAKU TAKINO', 'Bài điểm sách đăng trên Nippon.com', bg='ai09', illus=MC, srcnote=NG(NP)),
    K((21, 'nếu'), 'NẾU VỤ MẤT TÍCH 1989\nĐƯỢC TRUY ĐẾN CÙNG', ('GIÁO PHÁI CÓ THỂ ĐÃ BỊ CHẶN SỚM HƠN', (21, 'có'), 'acc'), vid='c10'),
    S(22, 'MỘT NHẬN ĐỊNH', 'KHÔNG PHẢI MỘT BẰNG CHỨNG', bg='ai08', illus=MC),
    K(23, 'HỒ SƠ CŨ KHÔNG CHẾT', ('NÓ NẰM CHỜ AI ĐÓ MỞ LẠI', (23, 'nó'), 'sm'), vid='c12'),
    S(24, 'MỘT NGƯỜI ĐÀN ÔNG', 'VẪN MANG TRÊN MÌNH LỜI ĐỒN VỀ MÌNH', bg='ai04', illus=MC),
    Q(25, 'AUM LÀ GÌ,\nVÀ VÌ SAO LẠI LÀ AUM?', vid='c10'),
])
CH['ch06'] = dict(hud={'k': 'CHƯƠNG 06', 't': 'TỪ LỚP YOGA ĐẾN CHÂN NÚI PHÚ SĨ'}, bgm={'mood': 'dark', 'at': 0, 'gain': 0.12}, scenes=[
    K(None, 'x', bg='motosu40'),
    DT(1, 'CON TRAI THỨ TƯ · KUMAMOTO', '1955', bg='kasu61', srcnote=NG(WK)),
    K(3, 'NĂM 1981', ('BỊ PHẠT VÌ BÁN THUỐC KHÔNG GIẤY PHÉP', (3, 'bị'), 'sm'), bg='toky113', srcnote=NG(WK)),
    K(5, 'SAU CHUYẾN ĐI ẤN ĐỘ', ('TỰ XƯNG BẬC THẦY · NÓI MÌNH ĐÃ GIÁC NGỘ', (5, 'tự'), 'sm'), bg='kasu68'),
    S(6, 'LỚP YOGA\nVÀ THIỀN', 'SHIBUYA · TOKYO', bg='toky113'),
    K(7, 'CÁC NGUỒN\nKHÔNG THỐNG NHẤT', ('MỘT TRANG GHI 1984 · TRANG KHÁC GHI 1987', (7, 'một'), 'sm'), bg='kasu78', srcnote=NG(WK)),
    TL(8, [('LÚC ĐẦU', 'AUM SHINSEN NO KAI'), ('1989', 'ĐƯỢC CÔNG NHẬN LÀ TỔ CHỨC TÔN GIÁO')], bg='toky113', srcnote=NG(WK)),
    K(10, 'NĂM 1990', ('LẬP ĐẢNG CHÍNH TRỊ · 25 ỨNG CỬ VIÊN QUỐC HỘI', (10, 'họ'), 'acc'), bg='kasu68', srcnote=NG(WK)),
    S(11, 'DỪNG Ở ĐÂY\nMỘT NHỊP', 'VÌ ĐIỀU NÀY QUAN TRỌNG', bg='ai12', illus=MC),
    K(12, 'TÒA ÁN NHẬT VỀ SAU', ('KẾT ÁN CÁC THỦ LĨNH CỦA GIÁO PHÁI NÀY', (12, 'kết'), 'sm'), vid='c13'),
    S(13, 'KHÔNG CÓ NGHĨA\nYOGA LÀ NGUY HIỂM', 'VÀ TÔN GIÁO NÀO KHÁC CŨNG KHÔNG PHẢI GÁNH LỖI', bg='ai22', illus=MC),
    S(14, 'MỘT TỔ CHỨC\nCỤ THỂ', 'NHỮNG QUYẾT ĐỊNH CỤ THỂ CỦA NHỮNG CON NGƯỜI CỤ THỂ', bg='kasu61'),
    K(15, 'CUỐI NĂM 1989', ('LUẬT SƯ SAKAMOTO · VỢ 29 TUỔI · CON 14 THÁNG', (15, 'luật'), 'sm'), bg='ai29', illus=MC, srcnote=NG(WK)),
    S(16, 'TÒA ÁN XÁC ĐỊNH', 'ÔNG ASAHARA LÀ NGƯỜI CHỦ MƯU', vid='c13', srcnote=NG(WK)),
    K(17, 'NĂM 1994', ('VỤ ÁN VẪN CHƯA CÓ LỜI GIẢI', (17, 'nhưng'), 'acc'), bg='ai09', illus=MC),
    P(18, 'sat7', 'ĐỊA ĐIỂM LIÊN QUAN AUM · ẢNH TƯ LIỆU', move='in'),
    P(20, 'ai24', PD, move='in'),
    P(22, 'ai23', PD, move='in'),
    K(23, 'VỤ TÌM KIẾM SAU NÀY', ('CẢNH SÁT VÀO CHÍNH KHU NÀY', (23, 'cảnh'), 'sm'), bg='sat36'),
    DT(24, 'ASAHARA BỊ BẮT · TÒA NHÀ SỐ 6', '5/1995', bg='sat7', srcnote=NG(WK)),
    S(25, 'NHƯNG BÂY GIỜ\nMỚI LÀ CUỐI 1994', 'AI ĐỨNG BÊN NGOÀI ĐÃ NHẬN RA ĐIỀU KHÔNG BÌNH THƯỜNG', vid='c9'),
])
# ---------------------------------------------------------------- hậu kỳ

NEN = {
    'ch00': ['kasu61', 'toky113', 'mm8', 'jr1'],
    'ch01': ['kasu61', 'cas42', 'toky113', 'kasu68', 'motosu40'],
    'ch02': ['cas42', 'cas46', 'cas54', 'mat55', 'cas45', 'kasu68'],
    'ch03': ['mat55', 'cas45', 'cas46', 'kasu61', 'kofu41'],
    'ch04': ['kasu78', 'kasu61', 'kofu41', 'cas46', 'toky113'],
    'ch05': ['toky113', 'kasu61', 'kasu68', 'cas42', 'sak117'],
    'ch06': ['motosu40', 'sat7', 'sat36', 'kasu68', 'toky113', 'kasu78'],
    'ch07': ['motosu40', 'sat36', 'kofu41', 'toky113', 'kasu61', 'sat7'],
    'ch08': ['toky113', 'kasu61', 'kasu68', 'sat36', 'kasu78'],
    'ch09': ['kasu68', 'kasu61', 'kasu78', 'mm8', 'tsuk119', 'tsuk132'],
    'ch10': ['sdf16', 'sdf17', 'sdf19', 'kasu61', 'sdf26', 'hz15', 'mm8'],
    'ch11': ['sat36', 'sat7', 'kofu41', 'kasu61', 'cas46', 'prot20'],
    'ch12': ['kasu61', 'toky113', 'prot20', 'kasu78', 'mar83'],
    'ch13': ['cas46', 'cas54', 'kasu68', 'toky113', 'mat55', 'kasu78'],
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


def gan_clip(limit=3):  # long_gate: cap = max(MAX_SAME_CLIP, round(phút/6)) = 4 với 26 phút
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
    'ch01': ('BA KHOẢN NỢ\nTHỜI GIAN', 'GIỮA 27/6/1994 VÀ 20/3/1995', 'replace'),
    'ch02': ('MỘT KHU NHÀ\nYÊN TĨNH', 'ĐÊM 27/6/1994 · MATSUMOTO', 'replace'),
    'ch03': ('NGƯỜI GỌI\nCẤP CỨU', 'HAI THÂN PHẬN MỘT LÚC', 'replace'),
    'ch04': ('KHOẢNG\n20 LOẠI\nHÓA CHẤT', 'MỘT LỜI GIẢI THÍCH NGHE CÓ LÝ', 'replace'),
    'ch05': ('MỘT BẢN TIN\nNỘI BỘ\nVÀ BA TỈNH', 'BA MẢNH CỦA MỘT BỨC TRANH', 'replace'),
    'ch06': ('TỪ LỚP YOGA\nĐẾN CHÂN NÚI\nPHÚ SĨ', 'AUM SHINRIKYO · KAMIKUISHIKI', 'replace'),
    'ch07': ('MỘT\nMẪU ĐẤT', 'CUỐI 1994 · CHÂN NÚI PHÚ SĨ', 'replace'),
    'ch08': ('MỘT CÁI TÊN\nTRÊN LỆNH\nKHÁM XÉT', 'THÁNG 2 · THÁNG 3/1995', 'replace'),
    'ch09': ('TÁM GIỜ\nMƯỜI PHÚT', 'SÁNG 20 THÁNG 3 · TOKYO', 'replace'),
    'ch10': ('BÀI HỌC\nTỪ MATSUMOTO', 'BA TIẾNG ĐỒNG HỒ', 'replace'),
    'ch11': ('NGÀY KHÁM XÉT\nĐẾN MUỘN', 'HAI NGÀY SAU · 22/3/1995', 'replace'),
    'ch12': ('TÁM NĂM\nTRÊN GHẾ\nBỊ CÁO', 'PHÁN QUYẾT 2004 · 2006 · 2018', 'replace'),
    'ch13': ('NHỮNG NGƯỜI\nCÒN LẠI', 'KẾT TOÁN BA KHOẢN NỢ', 'replace'),
}
CARD_BG = {}

CHAPTER_TITLES = ['SÁNG THỨ HAI', 'BA KHOẢN NỢ THỜI GIAN', 'MỘT KHU NHÀ YÊN TĨNH', 'HAI THÂN PHẬN MỘT LÚC', 'KHOẢNG 20 LOẠI HÓA CHẤT',
                  'MỘT BẢN TIN NỘI BỘ VÀ BA TỈNH', 'TỪ LỚP YOGA ĐẾN CHÂN NÚI PHÚ SĨ', 'MỘT MẪU ĐẤT', 'MỘT CÁI TÊN TRÊN LỆNH KHÁM XÉT',
                  'TÁM GIỜ MƯỜI PHÚT', 'BÀI HỌC TỪ MATSUMOTO', 'NGÀY KHÁM XÉT ĐẾN MUỘN', 'TÁM NĂM TRÊN GHẾ BỊ CÁO', 'NHỮNG NGƯỜI CÒN LẠI']

# Câu {pd} của script.md (chỉ số dòng trong chNN.json): cảnh bao câu đó phải mang nhãn PHỎNG DỰNG.
PD_LINES = {'ch00': [4, 5, 6], 'ch01': [], 'ch02': [3, 4, 5, 6, 11, 26, 27], 'ch03': [13, 14, 15, 16], 'ch04': [7, 8, 9], 'ch05': [3, 4],
            'ch06': [20, 21, 22], 'ch07': [9, 10, 11], 'ch08': [14, 15], 'ch09': [1, 2, 14, 15], 'ch10': [12, 13], 'ch11': [0, 1],
            'ch12': [0, 1], 'ch13': [27, 28]}


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
    NOW = {'mm8', 'jr1', 'psia33', 'psia34', 'motosu40', 'kofu41', 'cas42', 'cas54', 'cas46', 'cas45', 'mat55', 'kasu61', 'kasu68', 'kasu78',
           'tsuk119', 'tsuk122', 'tsuk132', 'tspol118', 'sak117', 'toky113', 'mar83', 'hib96', 'hib105', 'prot20'}
    MODEL = set()
    AIKEYS = {k for k, v in IMGS.items() if str(v).startswith('EXT:ai')}
    for chapter in CH.values():
        for scene in chapter['scenes']:
            if scene.get('illus') or scene['type'] in ('split', 'print'):
                continue
            key = scene.get('img') or scene.get('bg')
            if key in NOW:
                scene['illus'] = 'ẢNH NGÀY NAY'
            elif key in MODEL:
                scene['illus'] = 'MÔ HÌNH · BẢO TÀNG'
    for chapter in CH.values():          # ảnh AI luôn mang nhãn PHỎNG DỰNG hoặc MINH HỌA CHUNG; không cảnh nào để trần
        for scene in chapter['scenes']:
            keys = {scene.get('img'), scene.get('bg')} | {(scene.get(x) or {}).get('img') for x in ('a', 'b')}
            if keys & AIKEYS:
                scene['illus'] = scene.get('illus') or MC
                if not str(scene['illus']).startswith(('PHỎNG DỰNG', 'MINH HỌA CHUNG')):
                    errs.append(f'cảnh dùng ảnh AI có nhãn lạ: {scene["illus"]!r}')
    DEF_SRC = {'ch12': NG('WIKIPEDIA · AL JAZEERA'), 'ch13': NG('WIKIPEDIA · NIPPON.COM · AP')}
    DIGIT = re.compile(r'\d{2,}|\d+/\d+')
    for chn, chapter in CH.items():            # con số, mốc ngày trên chữ: luôn có "NGUỒN: …"
        for scene in chapter['scenes']:
            if scene['type'] == 'chapter' or scene.get('srcnote'):
                continue
            shown = [scene.get(k) for k in ('text', 'sub', 'title', 'day', 'date', 'label', 'suffix')]
            shown += [i.get('text') for i in scene.get('items') or [] if isinstance(i, dict)]
            shown += [r.get(k) for r in scene.get('rows') or [] if isinstance(r, dict) for k in ('k', 'v')]
            shown += [n.get(k) for n in scene.get('nodes') or [] if isinstance(n, dict) for k in ('t', 's')]
            if any(isinstance(x, str) and DIGIT.search(x) for x in shown):
                scene['srcnote'] = DEF_SRC.get(chn, NG('WIKIPEDIA'))
    if errs:
        print('\n'.join(errs))
        raise SystemExit(f'{len(errs)} lỗi nhãn')
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
    write(__file__, CH, {key: value for key, value in IMGS.items() if key in used}, GEO, endcardBg='kasu68')
    spec_mod = D / 'spec_sarin.py'
    if spec_mod.exists():
        s2 = importlib.util.spec_from_file_location('spec_sarin', spec_mod)
        m2 = importlib.util.module_from_spec(s2)
        s2.loader.exec_module(m2)
        m2.apply(CH, CHAPTER_TITLES, sorted(used), IMGS)
    print('clip dùng:', dict(clip_used), '| ảnh img:', len(img_uses), '| ảnh khai:', len(used))
