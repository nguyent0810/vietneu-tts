"""GH-476 bước 4: cảnh biên tập CH00–CH12 cho Long CL "Vidocq - Javert" (cl-vidocq-javert).

Luật mới 18/11/2026 (đè mẫu Sarin): chữ toàn màn hình <= 15% giây (mục tiêu <= 12%), mỗi file ảnh tĩnh <= 6 lượt (tốt nhất <= 4),
ảnh AI phỏng tác nhân vật/sự kiện gắn chip PHỎNG DỰNG, ảnh chụp ngày nay gắn ẢNH NGÀY NAY, không in ghi công lên hình.
Hình đi trước: ảnh tư liệu Commons (thạch bản, tranh khắc, hồ sơ, bản đồ) giữ bằng camera/pano, clip, hồ sơ/file, timeline, bản đồ.

Cách viết: mỗi chương là danh sách "nhịp" B(dòng, cảnh1, cảnh2, ...). Nhịp phủ từ dòng đó tới dòng của nhịp kế; số cảnh trong nhịp
được chia đều theo số từ (cắt tại đầu dòng nếu gần, không thì tại một từ duy nhất trong dòng). Mỗi cảnh phải dài 12–32 từ
(= 2,5–9 s ở 3,7–4,4 từ/giây; pano 37–70 từ). Cổng tự kiểm: chạy file này, nó in nhịp nào sai số cảnh.
Chạy: python data/long/cl-vidocq-javert/gen_scenes.py  (gen_scenes2.py chứa CH06–CH12; spec_vidocq.py ghi spec.json).
"""
import importlib.util
import json
import math
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parent
ROOT = D.parents[2]
sys.path.insert(0, str(ROOT / 'motion/long'))
from scenekit import sc, kin, write, chapter  # noqa: E402

RES = json.loads((ROOT / 'output/long/cl-vidocq-javert/research.json').read_text(encoding='utf-8'))['images']


def im(i, must):
    f = RES[i]['file']
    if must not in f:
        raise ValueError(f'Ảnh {i} không khớp: {f}')
    return f


# ---------------------------------------------------------------- kho ảnh (khoá -> tên Commons; EXT:ai:ai_NN = ảnh AI phỏng tác)
IMGS = {
    # chân dung Vidocq
    'vdev': im(8, 'Achille Dev'), 'vgr': im(4, 'Vidocq.jpg'), 'vlit': im(37, 'Vidocq (1775-1857)'), 'vpost': im(38, 'roi des voleurs'),
    'vcrop': im(45, 'Vidocq (cropped)'), 'vbm': im(46, 'BM 1901'), 'vcn1': im(47, "Portrait d'Eug"), 'vcn2': im(49, "Portrait d'Eug"),
    'vrijk': im(51, 'Portret van Eug'), 'vmem': im(36, 'Mémoires - Tome 4'), 'vcard': im(6, 'DIV CondamnationBagne'),
    # Cruikshank 1829
    'cr39': im(39, 'hump-back'), 'cr40': im(40, 'old gallery guard'), 'cr41': im(41, 'discovers the doctor'), 'cr42': im(42, 'pursued by gendarmes'),
    'cr43': im(43, 'arresting Pons'), 'cr203': im(203, 'Fosse Family'),
    # Bicêtre, đường xích
    'bfer': im(53, 'ferrement'), 'bdep': im(54, 'D.3173'), 'bser': im(56, 'sermon'), 'btoi': im(58, 'toilette'),
    'bfer2': im(83, 'ferrement des for'), 'bdep2': im(80, 'Gabri'), 'bser2': im(82, 'sermon'), 'btoi2': im(81, 'toilette'),
    'bkr': im(31, 'Kremlin'), 'road52': im(52, 'Route de Toulon'), 'chain22': im(22, 'Chaine to Bagne'),
    # Toulon, Brest
    'tbag': im(20, 'Toulon- Bagnard'), 'tport': im(21, 'Bagne de Toulon.jpg'), 'tbazar': im(23, 'Bazar'), 'tesc': im(25, 'Escape attempt'),
    'tconge': im(26, 'conge du bagne'), 'gal35': im(35, 'Galley slave'), 'gal27': im(27, 'Galere Ordinaire'), 'valj16': im(16, 'Jean Valjean au bagne'),
    'brx': im(61, 'extrait registre'), 'brsortie': im(62, 'Sortie du Bagne'), 'brnoel': im(63, 'Attelage'), 'brport': im(67, 'travail dans le port'),
    'brelev': im(68, 'Choquet de Lindu - '), 'brform': im(69, 'P4'), 'brplan': im(70, 'P3'), 'br71': im(71, 'P1'), 'br73': im(73, 'P6'),
    'br74': im(74, 'P5'), 'br75': im(75, 'P9'), 'br76': im(76, 'P10'), 'brtrav': im(79, 'Forçats au travail'),
    'fcard5': im(5, 'LaForcePrison'), 'conc222': im(222, 'PRETRES'), 'conc228': im(228, 'prison du Prince'), 'conc221': im(221, 'Princess Elizabeth'), 'conc220': im(220, 'Frank Boggs'), 'rue209': im(209, 'Geneviève, G.5293(2)'), 'ref216': im(216, 'Hospitalit'),
    # bản đồ, Douai, Arras, Paris
    'mapldp': im(119, 'Lille Douai'), 'douai124': im(124, 'Grundriss'), 'arras141': im(141, 'Arras, B'), 'arras142': im(142, 'Kaart van Arras'),
    'plan102': im(102, 'Plan de Paris'), 'marville': im(107, 'Marville'), 'palais114': im(114, 'Palais de Justice'), 'travest': im(109, 'travestissement'),
    'pont155': im(155, 'Saints Peres'), 'bal204': im(204, 'Sont-ils fade'), 'bal205': im(205, 'queue devant'), 'bal206': im(206, 'vol au renfoncement'),
    'rue208': im(208, 'rue de la Montagne'), 'nuits214': im(214, 'NUITS DU BOULEVARD'),
    'refuge215': im(215, 'Hospitalit'), 'cour118': im(118, 'Anastay'), 'conc223': im(223, 'grande galerie'), 'conc224': im(224, 'porte du quai'),
    'conc225': im(225, 'salle des chemin'), 'conc227': im(227, 'préau des hommes'), 'conc230': im(230, 'Pont au Change'),
    'stmande': im(244, 'St Mand'), 'valmy': im(10, 'Valmy'), 'daum0': im(0, 'Daumier 026'), 'auto115': im(115, 'Collection d'),
    # Những người khốn khổ, Balzac, Hugo
    'jav13': im(13, 'Javert.jpg'), 'jav85': im(85, 'Gustave Brion, Javert'), 'jav91': im(91, 'Javert déraill'), 'jav92': im(92, 'Javert sur les traces'),
    'jav93': im(93, 'Javert l'), 'jav94': im(94, 'aux pieds de Javert'), 'jav95': im(95, 'Javert le regardait'), 'jav97': im(97, 'chapitre I Javert'),
    'madel': im(14, 'Madeleine'), 'bayard15': im(15, 'ferma les yeux'), 'fantine': im(17, 'Fantine'), 'cosette': im(18, 'Cosette'),
    'cab': im(19, 'Cab roule'), 'vjdeath': im(210, 'Mort de Jean Valjean'), 'lmis88': im(88, 'autorit'), 'lmis90': im(90, 'Pierre Georges Jeanniot'),
    'livret': im(98, 'Livret'), 'balz1': im(1, 'Balzac (1842).jpg'), 'balz161': im(161, 'Balzac Boulanger.jpg'), 'balz32': im(32, 'SplendorsMiseries'),
    'balz159': im(159, "David d'Angers"), 'balz161': im(161, 'Balzac Boulanger.jpg'), 'balz163': im(163, 'Gérard'), 'balz174': im(174, 'S632.jpg'),
    'hugo184': im(184, 'Brooding'), 'hugo185': im(185, 'Bonnat'), 'hugo187': im(187, 'Carjat'), 'hugo194': im(194, 'in Jersey'),
    'hugo186': im(186, 'c1853'), 'hugo195': im(195, 'Hugo Charles Hugo Fran'),
}
for _i in range(1, 30):
    IMGS[f'ai{_i:02d}'] = f'EXT:ai:ai_{_i:02d}'
AIKEYS = {k for k in IMGS if k.startswith('ai')}
NOW = {'stmande'}                       # ảnh chụp ngày nay -> nhãn ẢNH NGÀY NAY
GEO = {
    'fr1': {'countries': ['France'], 'labels': {'France': 'PHÁP'}, 'bbox': [-5.2, 42.2, 8.4, 51.3], 'box': [260, 100, 1660, 900],
            'pins': [{'name': 'Arras', 'lon': 2.78, 'lat': 50.29, 'label': 'ARRAS'},
                     {'name': 'Douai', 'lon': 3.08, 'lat': 50.37, 'label': 'DOUAI'},
                     {'name': 'Paris', 'lon': 2.35, 'lat': 48.86, 'label': 'PARIS'},
                     {'name': 'Brest', 'lon': -4.49, 'lat': 48.39, 'label': 'BREST'},
                     {'name': 'Toulon', 'lon': 5.93, 'lat': 43.12, 'label': 'TOULON'},
                     {'name': 'Rouen', 'lon': 1.1, 'lat': 49.44, 'label': 'ROUEN'}]},
}
CLIPS = {'k1': '198005', 'k2': '198011', 'k3': '198013', 'k4': '198014', 'k5': '198015',
         'k6': '12550702', 'k7': '12123574', 'k8': '10425839', 'k9': '4765799', 'k10': '32540543', 'k11': '30493711',
         'k12': '7343476', 'k13': '30117908', 'k14': '11765182', 'k15': '3999371', 'k16': '9455503', 'k17': '18360083',
         'k18': '8720604', 'k19': '4889026', 'k20': '4296589'}
CLIP_SRC = {'198005': 'output/asset_library/lib198v/vid_05.mp4', '198011': 'output/asset_library/lib198v/vid_11.mp4',
            '198013': 'output/asset_library/lib198v/vid_13.mp4', '198014': 'output/asset_library/lib198v/vid_14.mp4',
            '198015': 'output/asset_library/lib198v/vid_15.mp4'}
MC = 'MINH HỌA CHUNG'
PD = 'PHỎNG DỰNG'
PDV = 'PHỎNG DỰNG'

# ---------------------------------------------------------------- hàm dựng cảnh (mỗi hàm trả một cảnh CHƯA có at)
_CAMS = ['push_in', 'dolly', 'pull_out', 'pan', 'tilt_up']
_cam_n = [0]


def _cam():
    _cam_n[0] += 1
    return _CAMS[_cam_n[0] % len(_CAMS)]


def _fin(s, **kw):
    for key in ('bg', 'vid'):
        v = kw.pop(key, None)
        if v:
            if key == 'vid':
                s['_vid'] = [v] if isinstance(v, str) else list(v)
                s.setdefault('illus', MC)
            else:
                s[key] = v
    s.update({k: v for k, v in kw.items() if v is not None})
    return s


def P(img, cap=None, tone=None, move=None, focus=None, cam=None, fx=None, kin_=None, **kw):
    """Ảnh tư liệu/AI. cam tự đổi vòng nếu không nêu; kin_ = chữ khoá phủ lên ảnh (không tính ngân sách chữ)."""
    if img in AIKEYS:
        cap = cap or PD
        tone = tone or 'color'
    s = sc('photo', None, img=img)
    for k_, v_ in (('illus', cap), ('tone', tone), ('focus', focus)):
        if v_ is not None:
            s[k_] = v_
    if move:
        s['move'] = move
    else:
        s['cam'] = cam or _cam()
    if fx:
        s['fx'] = fx
    if kin_:
        s['kin'] = kin_
    return _fin(s, **kw)


def A(img, **kw):
    return P(img, PD, **kw)


def KN(*items):
    return kin(*[(t, 0, *fl) for t, *fl in items])


def PR(img, k, h, lines, cap=None, right=False, tone=None, maxw=None, maxh=None, **kw):
    s = sc('print', None, img=img, right=right, side={'k': k, 'h': h, 'lines': [{'text': t, 'at': 0} for t in lines]})
    for k_, v_ in (('tone', tone), ('maxW', maxw), ('maxH', maxh), ('caption', cap)):
        if v_ is not None:
            s[k_] = v_
    return _fin(s, **kw)


def PAN(img, x0=0.0, x1=1.0, cap=None, tone=None, **kw):
    return _fin(sc('pano', None, img=img, tone=tone, illus=cap, _pano=(x0, x1)), **kw)


def K(text, *more, **kw):
    items = [(text, 0, 'acc')] + [(t, 0, *fl) for t, *fl in more]
    return _fin(sc('kinetic', None, items=kin(*items)), **kw)


def S(text, sub=None, **kw):
    return _fin(sc('slam', None, text=text, sub=sub), **kw)


def DT(day, date, **kw):
    return _fin(sc('date', None, day=day, date=date), **kw)


def CT(to, suffix, label, frm=0, year=False, prefix=None, **kw):
    s = sc('counter', None, suffix=suffix, label=label, **{'from': frm, 'to': to})
    if prefix:
        s['prefix'] = prefix
    if year or 1000 <= to <= 2100:
        s['year'] = bool(year)
    return _fin(s, **kw)


def QT(ln, by, text, **kw):
    """Thẻ trích dẫn: ln = dòng chứa câu trích (nguyên văn trong lời đọc); nhịp phải bắt đầu ở dòng <= ln."""
    return _fin(sc('quote', None, text=text, by=by, lbl='TRÍCH DỊCH', qline=ln, typeAt=ln), **kw)


def Q(text, **kw):
    return _fin(sc('question', None, text=text), **kw)


def LD(title, rows, **kw):
    return _fin(sc('ledger', None, title=title, rows=[{'k': k, 'v': v, 'at': 0} for k, v in rows]), **kw)


def TL(items, **kw):
    return _fin(sc('timeline', None, title=None, items=[{'year': y, 'text': t, 'at': 0} for y, t in items]), **kw)


def SP(title, left, right, sign=None, **kw):
    s = sc('split', None, title=title, a={'img': left[0], 'label': left[1]}, b={'img': right[0], 'label': right[1]})
    if sign:
        s['sign'] = sign
    return _fin(s, **kw)


def OR(root, kids, **kw):
    nodes = [{'id': 'r', 't': root[0], 's': root[1], 'cls': 'top', 'at': 0}]
    nodes += [{'id': f'k{i}', 'p': 'r', 't': t, 's': s, 'at': 0} for i, (t, s) in enumerate(kids)]
    return _fin(sc('org', None, nodes=nodes), **kw)


def MP(geo, names, **kw):
    return _fin(sc('map', None, geo=geo, pins=[{'name': n, 'at': 0} for n in names]), **kw)


def FL(k, name, desc='', rows=None, **kw):
    s = sc('file', None, k=k, name=_wrap(name), desc=desc)
    if rows:
        s['rows'] = [{'k': x, 'v': y, 'at': 0} for x, y in rows]
    return _fin(s, **kw)


def BR(**kw):
    return _fin(sc('broll', None), **kw)


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


def NG(x):
    return 'NGUỒN: ' + x


WK = 'WIKIPEDIA'
HK = 'HỒI KÝ VIDOCQ'
HR = 'HERODOTE.NET'

# ---------------------------------------------------------------- bộ máy nhịp
CHAPTERS = {}
LINES = {}


def _lines(ch):
    if ch not in LINES:
        raw = json.loads((D / f'{ch}.json').read_text(encoding='utf-8'))['lines']
        LINES[ch] = [x if isinstance(x, str) else x['t'] for x in raw]
    return LINES[ch]


def B(line, *vis):
    return (line, list(vis))


def _norm(w):
    return unicodedata.normalize('NFC', re.sub(r'[^\w]', '', w, flags=re.U)).casefold()


def _strip(tok):
    return tok.strip('.,;:!?…"“”‘’()«»—-')


def _anchor_at(toks, ln, k):
    """Mốc cho từ thứ k của dòng ln: k=0 -> số dòng; ngược lại [ln, từ] với từ xuất hiện đầu tiên đúng tại k (nhích nếu trùng)."""
    if k == 0:
        return 0, ln
    nt = [_norm(t) for t in toks]
    for d in (0, 1, -1, 2, -2, 3, -3, 4, -4):
        kk = k + d
        if 1 <= kk < len(toks) and nt[kk] and nt.index(nt[kk]) == kk:
            return d, [ln, _strip(toks[kk])]
    return None, None


MIN_W, MAX_W = 12, 32.6
GAP = 1.2
PMIN_W, PMAX_W = 37, 70


def _gapw(W, q, pl):
    """Khoảng nghỉ trước dòng bắt đầu tại vị trí q của W, quy ra số từ (0,32 s + nghỉ p của dòng trước) * 3,7 từ/giây."""
    prev_ln = W[q - 1][0]
    return GAP + 3.7 * pl[prev_ln]


def plan_chapter(ch, beats, errs):
    """Trả danh sách cảnh (đã có at) của chương."""
    lines = _lines(ch)
    toks = [l.split() for l in lines]
    raw = json.loads((D / f'{ch}.json').read_text(encoding='utf-8'))['lines']
    pl = [0.0 if isinstance(x, str) else float(x.get('p') or 0) for x in raw]
    scenes = []
    for bi, (l0, vis) in enumerate(beats):
        l1 = beats[bi + 1][0] if bi + 1 < len(beats) else len(lines)
        W = [(ln, k) for ln in range(l0, l1) for k in range(len(toks[ln]))]
        N, n = len(W), len(vis)
        starts = sorted(i for i, (ln, k) in enumerate(W) if k == 0 and i > 0)
        gapq = starts + ([N] if bi + 1 < len(beats) else [])
        ideals = [int(round(j * N / n)) for j in range(1, n)]
        opts = []
        for ideal in ideals:
            near = [s for s in starts if abs(s - ideal) <= 7]
            opts.append([ideal] + near)
        lo_b = [PMIN_W if v['type'] == 'pano' else (10 if v['type'] == 'quote' else MIN_W) for v in vis]
        hi_b = [PMAX_W if v['type'] == 'pano' else MAX_W for v in vis]
        best = None
        import itertools
        for combo in itertools.product(*opts) if n > 1 else [()]:
            cs = [0, *combo, N]
            if any(cs[x + 1] <= cs[x] for x in range(n)):
                continue
            sizes = [cs[x + 1] - cs[x] + sum(_gapw(W, q, pl) for q in gapq if cs[x] < q <= cs[x + 1]) for x in range(n)]
            bad = sum(max(0, lo_b[x] - sizes[x]) + max(0, sizes[x] - hi_b[x]) for x in range(n))
            nsnap = sum(1 for c in combo if c in starts)
            dev = sum(abs(c - i) for c, i in zip(combo, ideals))
            key = (bad, -nsnap, dev)
            if best is None or key < best[0]:
                best = (key, cs)
        cuts = []
        for ci, c in enumerate(best[1]):
            if 0 < c < N:
                ln, k = W[c]
                d, anc = _anchor_at(toks[ln], ln, k)
                if anc is None:
                    errs.append(f'{ch} nhịp #{bi} (dòng {l0}): không tìm được từ neo gần dòng {ln} từ {k}')
                    d = 0
                c = c + d
                c = max(c, (cuts[-1] + 1) if cuts else 1)
            cuts.append(c)
        for j, v in enumerate(vis):
            size = cuts[j + 1] - cuts[j] + sum(_gapw(W, q, pl) for q in gapq if cuts[j] < q <= cuts[j + 1])
            pano = v['type'] == 'pano'
            lo, hi = (PMIN_W, PMAX_W) if pano else (MIN_W, MAX_W)
            if v['type'] == 'chapter':
                lo, hi = 12, MAX_W
            if v['type'] == 'quote':
                lo = 10
            if not lo <= size <= hi:
                errs.append(f'{ch} nhịp #{bi} (dòng {l0}, {N} từ, {n} cảnh): cảnh {j} dài {size:.0f} từ, cần {lo}-{hi}; gợi ý {max(1, round(N / 26))} cảnh')
            ln, k = W[cuts[j]]
            _, anc = _anchor_at(toks[ln], ln, k)
            s = dict(v)
            if bi == 0 and j == 0:
                s['at'] = None
            else:
                s['at'] = anc if anc is not None else ln
            s['_span'] = (W[cuts[j]][0], W[cuts[j + 1] - 1][0], size)
            if pano:
                x0, x1 = s.pop('_pano')
                a0 = s['at'] if s['at'] is not None else 0
                pe = cuts[j] + int(size * 0.62)
                lnp, kp = W[pe]
                dd, ancp = _anchor_at(toks[lnp], lnp, kp)
                s['stops'] = [{'x': x0, 'at': a0}, {'x': x1, 'at': ancp if ancp is not None else lnp}]
            scenes.append(s)
    return scenes


def kiem_ngan(scene):
    return scene


def _set_children(s):
    """Phần tử con hiện ngay đầu cảnh (cổng nhịp cảnh: con hiện <= 1 s sau đầu cảnh): at con = at cảnh."""
    at = s.get('at')
    a0 = 0 if at is None else at
    typ = s['type']
    if typ in ('pano', 'quote', 'chapter'):
        return
    for key in ('items', 'rows', 'pins', 'nodes'):
        for kid in s.get(key) or []:
            if isinstance(kid, dict) and 'at' in kid:
                kid['at'] = a0
    if isinstance(s.get('kin'), list):
        for kid in s['kin']:
            kid['at'] = a0
    if typ == 'print':
        for ln_ in s['side']['lines']:
            ln_['at'] = a0


def ngat_dong(text, limit=16):
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


def _norm_s(w):
    return _norm(w)


def _anchors(obj):
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
    texts = [(x if isinstance(x, str) else x['t']).split() for x in lines]
    last, errs = (-1, -1), []
    for i, s in enumerate(scenes):
        for a in _anchors(s):
            ln, w = a[0], a[1]
            if ln >= len(texts):
                errs.append(f'{name}#{i}: câu {ln} không tồn tại')
            elif w and _norm(w) not in [_norm(t) for t in texts[ln]]:
                errs.append(f'{name}#{i}: câu {ln} không có chữ {w!r}')
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


def gan_clip(CHS, limit=6):
    """Chọn clip cho cảnh có _vid: mỗi clip <= limit lần (long_gate: max(2, round(phút/6)) = 7), không lặp liền nhau."""
    used = Counter()
    last_ch = {}
    for ch, v in CHS.items():
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


PD_LINES = {'ch00': [0, 1], 'ch01': [0, 10, 25], 'ch02': [3], 'ch03': [2, 9, 19, 32], 'ch04': [4, 27], 'ch05': [1, 29],
            'ch09': [7], 'ch10': [12], 'ch12': [5]}

CARDS = {
    'ch01': ('ĐỨA CON\nCỦA BÃO GIÔNG', 'ARRAS · 1775 → LILLE · 1795'),
    'ch02': ('VÀNH MÓNG NGỰA\nVÀ CHIẾC VÉ', 'DOUAI · THÁNG 12/1796'),
    'ch03': ('ĐOÀN NGƯỜI\nMANG XÍCH', 'BICÊTRE · BREST · TOULON'),
    'ch04': ('SÔNG SCARPE\nĐÊM TỐI', 'CHÍN NĂM TRỐN CHẠY · 1800–1809'),
    'ch05': ('BẢN GIAO KÈO\nTRONG NGỤC TỐI', 'PARIS · 1809–1811'),
    'ch06': ('ĐỘI QUÂN\nCỦA QUỶ', 'LA BRIGADE DE SÛRETÉ · 1811–1818'),
    'ch07': ('CON MẮT\nCỦA PARIS', 'ĐỈNH CAO VÀ LƯỠI DAO GHEN GHÉT'),
    'ch08': ('RŨ ÁO\nTỪ QUAN', 'THÁNG 6/1827 · HỒI KÝ 1828'),
    'ch09': ('TRẬN BÃO\nTHÁNG SÁU', 'PARIS · 1832'),
    'ch10': ('THÁM TỬ ĐẦU TIÊN\nTRONG VÒNG VÂY', 'GALERIE VIVIENNE · 1833–1838'),
    'ch11': ('HAI NỬA\nLINH HỒN', 'BALZAC · POE · VICTOR HUGO'),
    'ch12': ('BÓNG HOÀNG HÔN\nTRÊN DÒNG NƯỚC LŨ', '1847 → 1857'),
}
CHAPTER_TITLES = ['BẢN ÁN MÙA ĐÔNG VÀ KẺ HAI MẶT', 'ĐỨA CON CỦA BÃO GIÔNG VÀ TỜ GIẤY ĐỊNH MỆNH', 'VÀNH MÓNG NGỰA VÀ CHIẾC VÉ XUỐNG ĐỊA NGỤC',
                  'ĐOÀN NGƯỜI MANG XÍCH VÀ TIẾNG THẦN CÔNG TOULON', 'SÔNG SCARPE ĐÊM TỐI VÀ KẺ BỊ SĂN ĐUỔI',
                  'BẢN GIAO KÈO TRONG NGỤC TỐI VÀ CỖ XE LIỄU GAI', 'ĐỘI QUÂN CỦA QUỶ VÀ TẤM BẰNG TRẮNG ÁN', 'CON MẮT CỦA PARIS VÀ LƯỠI DAO GHEN GHÉT',
                  'RŨ ÁO TỪ QUAN VÀ TIẾNG VANG CHÂU LỤC', 'TRẬN BÃO THÁNG SÁU VÀ CÁNH CỬA KHÉP LẠI', 'THÁM TỬ ĐẦU TIÊN TRONG VÒNG VÂY THÙ ĐỊCH',
                  'HAI NỬA LINH HỒN DƯỚI NGÒI BÚT ĐẠI THI HÀO', 'BÓNG HOÀNG HÔN TRÊN DÒNG NƯỚC LŨ']
CARD_BG = {}


def card(ch, bg, sub=None):
    """Thẻ chương: nền = ảnh tư liệu/ AI (bg)."""
    no = str(int(ch[2:]))
    title, sub0 = CARDS[ch]
    word = _lines(ch)[0].split()[0]
    c = chapter(no, f'CHƯƠNG {int(no):02d}', title, sub or sub0, word)
    c['bg'] = bg
    if bg in AIKEYS:
        c['illus'] = PD
    return c


# ---------------------------------------------------------------- chương CH00–CH05 (CH06–CH12 ở gen_scenes2.py)
G_PRISON = 'MINH HỌA · NHÀ GIAM PHÁP THẾ KỶ 19'
G_COURT = 'MINH HỌA · PHIÊN TÒA PHÁP THẾ KỶ 19'
G_HK = 'MINH HỌA · HỒI KÝ VIDOCQ, 1829'
G_ROAD = 'MINH HỌA · ĐƯỜNG QUA NƯỚC PHÁP'
G_SEA = 'MINH HỌA · CẢNG BIỂN PHÁP THẾ KỶ 19'
G_PARIS = 'MINH HỌA · PARIS THẾ KỶ 19'
G_LAT = 'MINH HỌA · TRANH CHÂM BIẾM DAUMIER'

CH = {}
CH['ch00'] = dict(hud={'k': 'MỞ ĐẦU', 't': 'BẢN ÁN MÙA ĐÔNG'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, beats=[
    B(0, A('ai01', fx='candle_flicker', cam='push_in'), A('ai01', focus=[0.78, 0.45], cam='dolly')),
    B(2, BR(vid='k13', illus=PD)),
    B(3, QT(3, 'THẨM PHÁN TÒA DOUAI', 'Tuyên François Vidocq và César Herbaux chịu hình phạt khổ sai tám năm.', bg='ai01', illus=PD)),
    B(4, FL('BẢN ÁN · DOUAI', 'VIDOCQ', 'MỘT TỜ GIẤY RA TÙ LÀM GIẢ',
            rows=[('TỘI', 'LÀM GIẢ GIẤY RA TÙ'), ('ÁN', 'TÁM NĂM KHỔ SAI'), ('TUỔI', 'HAI MƯƠI MỐT')], img='vcard', tone='sepia')),
    B(6, P('tbag', G_PRISON, cam='push_in')),
    B(7, S('NGHỊCH LÝ', 'BẮT ĐẦU TỪ CHÍNH BẢN ÁN ẤY', bg='vlit')),
    B(8, TL([('1796', 'BẢN ÁN KHỔ SAI'), ('CUỐI 1811', 'VÀO HÀNH LANG QUYỀN LỰC'), ('CUỐI 1812', 'NẮM TRỌN QUYỀN BÍNH')], bg='tport', srcnote=NG(WK)),
         BR(vid='k5')),
    B(9, P('valj16', 'TRANH MINH HỌA · JEAN VALJEAN', cam='pull_out'), SP('MỘT CON NGƯỜI', ('valj16', 'JEAN VALJEAN'), ('jav13', 'JAVERT'), bg='vlit'),
         A('ai16', cam='push_in')),
    B(10, Q('VÌ SAO PARIS DÁM GIAO MẠNG SỐNG\nCHO MỘT TÊN VƯỢT NGỤC?', bg='vdev'), P('vdev', cam='dolly')),
])
CH['ch01'] = dict(hud={'k': 'CHƯƠNG 01', 't': 'ĐỨA CON CỦA BÃO GIÔNG'}, bgm={'mood': 'quiet', 'at': 0, 'gain': 0.12}, beats=[
    B(0, card('ch01', 'ai17', ), ),
    B(1, P('arras141', 'BẢN ĐỒ ARRAS', cam='pan'), PR('vcrop', 'ARRAS · 1775', 'EUGÈNE-FRANÇOIS\nVIDOCQ', ['SINH ĐÊM MÙA HẠ 1775', 'CON NHÀ THỢ BÁNH'], cap='VIDOCQ')),
    B(3, P('pool:prison', G_PRISON), P('pool:prison', G_PRISON)),
    B(6, BR(vid='k17'), S('CHA RUỘT\nBÁO CẢNH SÁT', 'MƯỜI NGÀY SAU, CẬU MỚI BIẾT', bg='conc225')),
    B(7, P('pool:portrait', kin_=KN(('KHÔNG THỂ\nQUAY VỀ', 'acc'))), P('arras142', 'BẢN ĐỒ ARRAS', cam='dolly')),
    B(9, P('road52', G_ROAD)),
    B(10, A('ai18', fx='rain'), A('ai18', cam='dolly')),
    B(11, P('tport', G_SEA), P('pool:sat', G_LAT), P('daum0', G_LAT), BR(vid='k8')),
    B(14, A('ai02'), P('valmy', 'TRANH · TRẬN VALMY 1792', cam='pan'), A('ai02', focus=[0.75, 0.5], cam='dolly'), PR('cr42', 'HỒI KÝ · 1829', 'BỊ ĐUỔI BẮT', ['ĐÀO NGŨ TRONG ĐÊM'], cap=G_HK), P('pool:prison', G_PRISON)),
    B(19, P('mapldp', 'BẢN ĐỒ · LILLE · DOUAI 1786'), P('pool:prison', G_PRISON), DT('BA THÁNG TÙ · LILLE · MÙA THU', '1795', bg='conc227', illus=G_PRISON)),
    B(22, P('pool:cruik', G_HK, kin_=KN(('MỘT ÂM MƯU LIỀU LĨNH', 'sm'))), BR(vid='k19'), P('pool:prison', G_PRISON)),
    B(25, A('ai19', fx='candle_flicker')),
    B(26, PR('brx', 'HỒ SƠ KHỔ SAI', 'MỘT TỜ GIẤY\nTẨM MỰC ĐEN', ['TỪ ÁN VẶT VÃNH', 'THÀNH VÉ MỘT CHIỀU'], cap='SỔ BỘ KHỔ SAI · BREST', right=True),
         P('pool:prison', G_PRISON), P('pool:cruik', G_HK), S('VÉ MỘT CHIỀU', 'XUỐNG ĐỊA NGỤC KHỔ SAI', bg='pool:toulon', illus='TRANH · KHỔ SAI THẾ KỶ 19')),
])
CH['ch02'] = dict(hud={'k': 'CHƯƠNG 02', 't': 'VÀNH MÓNG NGỰA'}, bgm={'mood': 'sad', 'at': 0, 'gain': 0.12}, beats=[
    B(0, card('ch02', 'conc225')),
    B(1, P('cour118', G_COURT), FL('HỒ SƠ · LILLE 1795', 'VIDOCQ', 'CỰU BINH · ĐÀO NGŨ · ẨU ĐẢ',
                                  rows=[('TỘI MỚI', 'LÀM GIẢ CÔNG VĂN'), ('BẰNG CHỨNG', 'KHÔNG CẦN THÊM')], img='brx', tone='sepia'),
         BR(vid='k2')),
    B(3, A('ai20', cam='push_in'), A('ai20', focus=[0.3, 0.5], cam='dolly')),
    B(4, P('douai124', 'BẢN ĐỒ · DOUAI THẾ KỶ 18', cam='pan'), DT('TÒA ÁN DOUAI MỞ PHIÊN · CUỐI THÁNG 12', '1796', bg='douai124', illus='BẢN ĐỒ · DOUAI')),
    B(7, P('pool:paris', G_PARIS), PR('cr43', 'HỒI KÝ · 1829', 'HAI BỊ CÁO', ['VIDOCQ', 'CÉSAR HERBAUX'], cap=G_HK), P('pool:prison', G_PRISON), P('pool:paris', G_PARIS)),
    B(12, CT(8, ' NĂM', 'KHỔ SAI · TUỔI HAI MƯƠI MỐT', bg='pool:toulon', illus='TRANH · KHỔ SAI THẾ KỶ 19'), P('gal35', 'TRANH · TÙ KHỔ SAI THẾ KỶ 19'), P('pool:prison', G_PRISON)),
    B(15, BR(vid='k4')),
    B(16, K('KHÁNG CÁO Ư?', ('CHỈ GIAM CHÂN THÊM VÀI THÁNG', 'sm'), bg='conc227', illus=G_PRISON), BR(vid='k17')),
    B(21, P('road52', G_ROAD), P('chain22', 'TRANH · ĐOÀN TÙ KHỔ SAI TOULON')),
])
CH['ch03'] = dict(hud={'k': 'CHƯƠNG 03', 't': 'ĐOÀN NGƯỜI MANG XÍCH'}, bgm={'mood': 'dark', 'at': 0, 'gain': 0.12}, beats=[
    B(0, card('ch03', 'bdep')),
    B(1, P('bkr', 'ẢNH CŨ · BICÊTRE', tone='bw')),
    B(2, A('ai03', cam='pull_out'), A('ai03', focus=[0.25, 0.55], cam='dolly')),
    B(3, P('pool:bicetre', 'TRANH · BICÊTRE'), P('pool:bicetre', 'TRANH · BICÊTRE')),
    B(5, P('chain22', 'TRANH · ĐOÀN TÙ KHỔ SAI'), CT(26, ' NGƯỜI', 'KHÓA CHUNG MỘT SỢI XÍCH', bg='pool:bicetre', illus='TRANH · BICÊTRE'), P('pool:bicetre', 'TRANH · BICÊTRE')),
    B(7, MP('fr1', ['Paris', 'Brest']), CT(24, ' NGÀY', 'CUỐC BỘ XUYÊN MÙA ĐÔNG', bg='road52', illus=G_ROAD)),
    B(9, A('ai21', focus=[0.15, 0.6], cam='tilt_up'), A('ai21', focus=[0.2, 0.5], cam='push_in')),
    B(10, PR('cr203', 'HỒI KÝ · 1829', 'TRỐN KHỎI\nPONT-À-LEZEN', ['CƯA XÍCH', 'KHOÉT VÁCH TƯỜNG'], cap=G_HK), P('tesc', 'TRANH · VƯỢT NGỤC KHỔ SAI'), BR(vid='k19'), PR('cr42', 'HỒI KÝ · 1829', 'GÃY CHÂN', ['BÒ LẠI BUỒNG GIAM'], cap=G_HK, right=True), P('pool:prison', G_PRISON)),
    B(17, P('pool:brest', 'TƯ LIỆU · TRẠI KHỔ SAI BREST'), P('pool:brest', 'TƯ LIỆU · TRẠI KHỔ SAI BREST', cam='pan')),
    B(19, A('ai04', cam='dolly'), A('ai04', focus=[0.75, 0.5], cam='pull_out')),
    B(20, P('pool:brest', 'TƯ LIỆU · TRẠI KHỔ SAI BREST'), P('pool:brest', 'TƯ LIỆU · TRẠI KHỔ SAI BREST'), P('pool:brest', 'TƯ LIỆU · TRẠI KHỔ SAI BREST'), BR(vid='k20')),
    B(23, P('pool:doc', 'MINH HỌA · TƯ LIỆU THẾ KỶ 19'), P('pool:cruik', G_HK), BR(vid='k11')),
    B(26, P('tport', 'TRANH · TOULON'), P('tbag', 'TRANH · TÙ NHÂN TOULON'), P('gal27', 'TÀU GALERE · BẢO TÀNG'), BR(vid='k15'), P('gal35', 'TRANH · TÙ KHỔ SAI'), P('tesc', 'TRANH · VƯỢT NGỤC KHỔ SAI')),
    B(30, P('pool:toulon', 'TRANH · TOULON'), DT('6 THÁNG 3 · NĂM', '1800', bg='tport', illus=G_SEA), BR(vid='k15')),
    B(32, A('ai05', cam='push_in'), A('ai05', focus=[0.8, 0.5], cam='pull_out')),
])
CH['ch04'] = dict(hud={'k': 'CHƯƠNG 04', 't': 'KẺ BỊ SĂN ĐUỔI'}, bgm={'mood': 'tense', 'at': 0, 'gain': 0.12}, beats=[
    B(0, card('ch04', 'plan102')),
    B(1, CT(9, ' NĂM', 'BỊ SĂN ĐUỔI · 1800 → 1809', bg='pool:portrait'), P('pool:paris', G_PARIS)),
    B(2, P('arras141', 'BẢN ĐỒ ARRAS', cam='dolly'), BR(vid='k1')),
    B(4, A('ai22', fx='rain', cam='push_in'), A('ai22', focus=[0.2, 0.6], cam='tilt_up')),
    B(5, P('pool:paris', G_PARIS), MP('fr1', ['Rouen', 'Paris', 'Arras'])),
    B(7, P('pool:sat', G_LAT), P('pool:sat', G_LAT), BR(vid='k3')),
    B(10, P('tconge', G_PRISON), FL('SỔ ĐEN HIẾN BINH', 'VIDOCQ', 'MỘT DÒNG CHỮ LẠNH NGẮT',
                                   rows=[('ÁN', 'TỬ HÌNH VẮNG MẶT'), ('TỘI', 'VƯỢT NGỤC · TÁI PHẠM')], img='vcard', tone='sepia'),
         S('TỬ HÌNH\nVẮNG MẶT', 'KHÔNG CÒN LÀ TÁM NĂM KHỔ SAI', bg='gal35'), P('pool:paris', G_PARIS)),
    B(15, P('douai124', 'BẢN ĐỒ · DOUAI', cam='pan'), PR('cr40', 'DOUAI · 1805', 'QUẢN NGỤC\nWETTU', ['MỜI VIDOCQ ĂN TỐI', 'TRONG PHÒNG RIÊNG'], cap=G_HK), P('pool:prison', G_PRISON), P('pool:paris', G_PARIS)),
    B(19, P('conc230', 'MINH HỌA · SÔNG VÀ NHÀ TÙ PARIS', cam='pan')),
    B(20, PR('cr41', 'HỒI KÝ · 1829', 'VIÊN ĐẶC VỤ', ['BƯỚC VÀO PHÒNG'], cap=G_HK, right=True)),
    B(21, QT(21, 'VIÊN ĐẶC VỤ', 'Cửa sổ không song!', bg='conc225', illus=G_PRISON)),
    B(24, QT(24, 'VIDOCQ', 'Sông Scarpe rất sâu với người không biết bơi.', bg='conc230', illus=G_PARIS)),
    B(26, BR(vid='k12')),
    B(27, A('ai23', fx='rain', cam='dolly'), A('ai23', cam='tilt_up')),
    B(28, K('TÙM!', ('DÒNG SCARPE NUỐT CHỬNG GÃ', 'sm'), bg='conc230', illus=G_PARIS)),
    B(31, PR('cr203', 'HỒI KÝ · 1829', 'LẶN SÂU\nDƯỚI ĐÁY SÔNG', ['BƠI QUA CỐNG NGẦM'], cap=G_HK), P('pool:prison', G_PRISON)),
    B(32, BR(vid='k11'), P('road52', G_ROAD)),
    B(34, MP('fr1', ['Arras', 'Rouen', 'Paris', 'Brest', 'Toulon']), P('pool:portrait', kin_=KN(('KHÔNG NHÀ CỬA', 'acc'), ('KHÔNG DANH TÍNH', 'sm'))), K('MỘT LỐI THOÁT\nCHƯA TỪNG CÓ TIỀN LỆ', bg='pool:portrait')),
])
CH['ch05'] = dict(hud={'k': 'CHƯƠNG 05', 't': 'BẢN GIAO KÈO'}, bgm={'mood': 'mystery', 'at': 0, 'gain': 0.12}, beats=[
    B(0, card('ch05', 'pool:paris')),
    B(1, A('ai08', fx='fog', cam='pull_out')),
    B(2, PR('cr42', 'HỒI KÝ · 1829', 'BA GIỜ SÁNG', ['TIẾNG ĐẬP CỬA', 'TRÈO NÓC NHÀ'], cap=G_HK), P('pool:paris', G_PARIS)),
    B(5, P('pool:paris', G_PARIS, tone='bw'), P('pool:paris', G_PARIS), P('pool:prison', G_PRISON)),
    B(8, P('tbag', G_PRISON), A('ai07', fx='candle_flicker'), A('ai07', focus=[0.25, 0.5], cam='dolly'), P('pool:prison', G_PRISON)),
    B(11, A('ai07', focus=[0.7, 0.5], cam='push_in'),
         LD('BẢN GIAO KÈO', [('VIDOCQ ĐƯA RA', 'TAI MẮT TRONG GIỚI TỘI PHẠM'), ('ĐỔI LẠI', 'KHÔNG BAO GIỜ BỊ ĐƯA VỀ TRẠI KHỔ SAI')], bg='conc225', illus=G_PRISON),
         P('pool:paris', G_PARIS), BR(vid='k9')),
    B(15, P('pool:paris', G_PARIS), OR(('BẢN GIAO KÈO', 'HAI NGƯỜI GẬT ĐẦU'), [('JEAN HENRY', 'CHẤP THUẬN'), ('PASQUIER', 'CHUẨN Y')], bg='pool:paris')),
    B(16, DT('20 THÁNG 7 · NĂM', '1809', bg='bkr'), P('fcard5', 'NHÀ TÙ LA FORCE · PARIS'), TL([('20/7/1809', 'NGỤC BICÊTRE'), ('3 THÁNG SAU', 'NHÀ TÙ LA FORCE')], bg='fcard5')),
    B(19, P('pool:prison', G_PRISON), PR('cr40', 'HỒI KÝ · 1829', 'GIÁN ĐIỆP\nHAI MANG', ['SỐNG NHƯ TÙ NHÂN', 'BÁO CÁO CHO HENRY'], cap=G_HK, right=True)),
    B(20, BR(vid='k8'), P('pool:doc', 'MINH HỌA · TƯ LIỆU THẾ KỶ 19'), P('pool:prison', G_PRISON), P('pool:prison', G_PRISON)),
    B(23, BR(vid='k20')),
    B(24, Q('LÀM SAO RA NGOÀI\nMÀ KHÔNG BỊ NGHI?', bg='fcard5')),
    B(26, BR(vid='k17'), P('road52', G_ROAD)),
    B(27, PR('cr203', 'HỒI KÝ · 1829', 'CỖ XE\nLIỄU GAI', ['BẺ KHÓA CÒNG', 'LAO XUỐNG ĐƯỜNG'], cap=G_HK), P('pool:paris', G_PARIS)),
    B(29, A('ai24', fx='fog', cam='push_in')),
    B(30, P('fcard5', 'NHÀ TÙ LA FORCE · PARIS'), P('pool:sat', G_LAT)),
    B(31, P('pool:portrait', kin_=KN(('MỘT CƠN ÁC MỘNG', 'acc'), ('CỦA THẾ GIỚI NGẦM', 'sm'))), P('pool:prison', G_PRISON)),
])

# Nhóm ảnh cùng vai (tư liệu chung): 'pool:<tên>' được gán ảnh ít dùng nhất trong nhóm, không trùng cảnh liền kề -> mỗi ảnh <= 4-5 lượt.
POOLS = {
    'portrait': ['vdev', 'vgr', 'vlit', 'vcrop', 'vbm', 'vcn1', 'vcn2', 'vrijk'],
    'paris': ['palais114', 'marville', 'rue208', 'nuits214', 'plan102', 'refuge215', 'pont155', 'conc230', 'rue209', 'ref216', 'conc220'],
    'prison': ['conc223', 'conc224', 'conc225', 'conc227', 'fcard5', 'bkr', 'conc222', 'conc228', 'conc221', 'bfer2', 'bdep2', 'bser2', 'btoi2',
               'br71', 'br73', 'br75', 'br76', 'brform', 'brplan', 'tbazar', 'gal27', 'br74'],
    'cruik': ['cr39', 'cr40', 'cr41', 'cr43'],
    'doc': ['auto115', 'travest', 'brx', 'tconge', 'vmem'],
    'sat': ['bal204', 'bal205', 'bal206', 'daum0'],
    'brest': ['brport', 'brelev', 'brnoel', 'brtrav', 'brsortie', 'br71', 'br73', 'br75', 'br76', 'brform', 'brplan'],
    'bicetre': ['bfer', 'bdep', 'bser', 'btoi', 'bfer2', 'bdep2', 'bser2', 'btoi2'],
    'toulon': ['tport', 'tbag', 'tbazar', 'gal35', 'gal27', 'tesc'],
    'hugo': ['hugo184', 'hugo185', 'hugo187', 'hugo194', 'hugo186', 'hugo195'],
    'lm': ['jav13', 'jav85', 'jav91', 'jav92', 'jav93', 'jav94', 'jav95', 'jav97', 'madel', 'valj16', 'cosette', 'fantine', 'cab', 'lmis88', 'lmis90', 'vjdeath', 'bayard15'],
}


CLIP_BY_POOL = {'paris': ['k5', 'k3', 'k10'], 'prison': ['k2', 'k17', 'k19'], 'portrait': ['k4', 'k9', 'k8'], 'cruik': ['k6', 'k18', 'k7'],
                'sat': ['k6', 'k18'], 'doc': ['k6', 'k18', 'k7'], 'brest': ['k15', 'k20'], 'toulon': ['k15', 'k20'], 'bicetre': ['k11', 'k16'],
                'hugo': ['k8', 'k19'], 'lm': ['k8', 'k19']}


def thin_pool(OUT, pool_name='paris', every=2, offset=1):
    """Pool ảnh Paris dùng quá dày: cứ mỗi `every` cảnh pool:paris đổi một cảnh thành clip b-roll (MINH HỌA CHUNG)."""
    n = 0
    for v in OUT.values():
        sl = v['scenes']
        for j, c in enumerate(sl):
            if c['type'] == 'photo' and c.get('img') == f'pool:{pool_name}' and 'kin' not in c:
                n += 1
                if n % every == offset:
                    sl[j] = {'type': 'broll', 'at': c['at'], '_vid': list(CLIP_BY_POOL[pool_name]), 'illus': MC, '_span': c['_span']}


def break_runs(OUT, run_max=5):
    """craft: không quá 5 cảnh photo liền nhau — đổi một ảnh tư liệu chung (pool) trong dãy thành clip b-roll (có nhãn MINH HỌA CHUNG)."""
    for name, v in OUT.items():
        sl = v['scenes']
        run = 0
        for i, s in enumerate(sl):
            run = run + 1 if s['type'] == 'photo' else 0
            if run >= run_max:
                done = False
                for strict in (True, False):
                    for j in (i, i - 1, i - 2, i - 3):
                        c = sl[j]
                        key = str(c.get('img') or '')
                        if c['type'] != 'photo' or 'kin' in c or key in AIKEYS or str(c.get('illus') or '').startswith(PD):
                            continue
                        if strict and not key.startswith('pool:'):
                            continue
                        pool = key[5:] if key.startswith('pool:') else ''
                        new = {'type': 'broll', 'at': c['at'], '_vid': list(CLIP_BY_POOL.get(pool, ['k1', 'k8', 'k9'])), 'illus': MC, '_span': c['_span']}
                        sl[j] = new
                        run = i - j
                        done = True
                        break
                    if done:
                        break


def resolve_pools(OUT):
    uses = Counter()
    iuses = Counter()
    flat = [(name, i, s) for name, v in OUT.items() for i, s in enumerate(v['scenes'])]
    for _, _, s in flat:
        for key in ('img', 'bg'):
            val = s.get(key)
            if val and not str(val).startswith('pool:'):
                uses[val] += 1
                if key == 'img':
                    iuses[val] += 1
        for x in ('a', 'b'):
            if (s.get(x) or {}).get('img'):
                uses[s[x]['img']] += 1
    prev = None
    for idx, (_, _, s) in enumerate(flat):
        for key in ('img', 'bg'):
            val = s.get(key)
            if val and str(val).startswith('pool:'):
                pool = POOLS[val[5:]]
                near = {prev}
                for j in (idx + 1,):
                    if j < len(flat):
                        near |= {flat[j][2].get('img'), flat[j][2].get('bg')}
                cand = [k for k in pool if k not in near] or pool
                pick = min(cand, key=lambda k: ((iuses[k] >= 3) if key == 'img' else False, uses[k], pool.index(k)))
                s[key] = pick
                uses[pick] += 1
                if key == 'img':
                    iuses[pick] += 1
        prev = s.get('img') or s.get('bg')


DEF_SRC = NG('WIKIPEDIA · HỒI KÝ VIDOCQ')
DIGIT = re.compile(r'\d{2,}|\d+/\d+')


def build_all():
    sys.modules['gen_scenes'] = sys.modules[__name__]
    other = D / 'gen_scenes2.py'
    module_spec = importlib.util.spec_from_file_location('gen_scenes2', other)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    CH.update(module.CH)
    errs = []
    OUT = {}
    for name, v in CH.items():
        scenes = plan_chapter(name, v['beats'], errs)
        OUT[name] = dict(hud=v['hud'], bgm=v['bgm'], scenes=scenes)
    if errs:
        print('\n'.join(errs))
        raise SystemExit(f'{len(errs)} lỗi nhịp (số cảnh / độ dài)')
    thin_pool(OUT)
    break_runs(OUT)
    resolve_pools(OUT)
    for v in OUT.values():
        for s in v['scenes']:
            _set_children(s)
    clip_used = gan_clip(OUT)
    for v in OUT.values():
        for s in v['scenes']:
            if s['type'] == 'slam':
                s['text'] = ngat_dong(s['text'])
            elif s['type'] == 'kinetic':
                for it in s['items']:
                    if not it.get('sm'):
                        it['text'] = ngat_dong(it['text'])
    # PHỎNG DỰNG: mọi cảnh chạm câu {pd} phải mang nhãn PHỎNG DỰNG; ảnh AI luôn mang nhãn PHỎNG DỰNG.
    for name, lines in PD_LINES.items():
        for i, s in enumerate(OUT[name]['scenes']):
            a, b, _ = s['_span']
            if any(a <= ln <= b for ln in lines) and not str(s.get('illus') or '').startswith(PD):
                errs.append(f'{name}#{i}: cảnh chạm câu {{pd}} (dòng {a}-{b}) chưa có nhãn PHỎNG DỰNG: {s.get("illus")!r}')
    for name, v in OUT.items():
        for i, s in enumerate(v['scenes']):
            keys = {s.get('img'), s.get('bg')} | {(s.get(x) or {}).get('img') for x in ('a', 'b')}
            if keys & AIKEYS:
                if s.get('illus') and not str(s['illus']).startswith(PD):
                    errs.append(f'{name}#{i}: cảnh dùng ảnh AI có nhãn lạ: {s["illus"]!r}')
                s['illus'] = s.get('illus') or PD
            elif s.get('illus') and str(s['illus']).startswith(PD) and not s.get('vid'):
                errs.append(f'{name}#{i}: nhãn PHỎNG DỰNG trên ảnh không phải AI')
            key = s.get('img') or s.get('bg')
            if key in NOW and not s.get('illus'):
                s['illus'] = 'ẢNH NGÀY NAY'
            if s['type'] != 'chapter' and not s.get('srcnote'):
                shown = [s.get(k) for k in ('text', 'sub', 'title', 'day', 'date', 'label', 'suffix')]
                shown += [x.get('text') for x in s.get('items') or [] if isinstance(x, dict)]
                shown += [r.get(k) for r in s.get('rows') or [] if isinstance(r, dict) for k in ('k', 'v')]
                shown += [x.get(k) for x in s.get('nodes') or [] if isinstance(x, dict) for k in ('t', 's')]
                if s['type'] in ('date', 'counter', 'timeline', 'ledger', 'org', 'file') and any(isinstance(x, str) and DIGIT.search(x) for x in shown):
                    s['srcnote'] = DEF_SRC
    for name, v in OUT.items():
        lines = json.loads((D / f'{name}.json').read_text(encoding='utf-8'))['lines']
        errs += kiem_tra_moc(name, v['scenes'], lines)
    uses = Counter()
    for v in OUT.values():
        for s in v['scenes']:
            for key in (s.get('img'), s.get('bg')):
                if key:
                    uses[key] += 1
            for x in ('a', 'b'):
                if (s.get(x) or {}).get('img'):
                    uses[s[x]['img']] += 1
    if '--where' in sys.argv:
        where = {}
        for name, v in OUT.items():
            for i, s in enumerate(v['scenes']):
                for key in (s.get('img'), s.get('bg')):
                    if key:
                        where.setdefault(key, []).append(f'{name[2:]}.{i}')
        for k, n in uses.most_common():
            if n > 4:
                print(k, n, ' '.join(where[k]))
    if '--uses' in sys.argv:
        print(' '.join(f'{k}:{n}' for k, n in uses.most_common()))
        print('chưa dùng:', ' '.join(sorted(set(IMGS) - set(uses))))
    errs += [f'ảnh {k} dùng {n} lần (> 6)' for k, n in uses.items() if n > 6]
    errs += [f'khoá ảnh lạ: {k}' for k in uses if k not in IMGS]
    if errs:
        print('\n'.join(errs))
        raise SystemExit(f'{len(errs)} lỗi')
    for v in OUT.values():
        for s in v['scenes']:
            s.pop('_span', None)
    used = set(uses)
    write(__file__, OUT, {k: val for k, val in IMGS.items() if k in used}, GEO, endcardBg='vdev')
    spec_mod = D / 'spec_vidocq.py'
    if spec_mod.exists():
        s2 = importlib.util.spec_from_file_location('spec_vidocq', spec_mod)
        m2 = importlib.util.module_from_spec(s2)
        s2.loader.exec_module(m2)
        m2.apply(OUT, CHAPTER_TITLES, sorted(used), IMGS)
    nscenes = sum(len(v['scenes']) for v in OUT.values())
    top = uses.most_common(8)
    print('cảnh:', nscenes, '| clip:', dict(clip_used), '| ảnh khai:', len(used), '| lặp nhiều nhất:', top)
    # sao clip vào output/ (gitignored) để cổng đo độ dài clip chạy thật
    import shutil
    bdir = ROOT / 'output/long/cl-vidocq-javert/broll'
    bdir.mkdir(parents=True, exist_ok=True)
    for cid in set(clip_used) | set():
        pass
    for key in clip_used:
        cid = CLIPS[key]
        dst = bdir / f'{cid}.mp4'
        if dst.exists():
            continue
        if cid in CLIP_SRC:
            shutil.copy2(ROOT.parent / CLIP_SRC[cid], dst)
            (bdir / f'{cid}.json').write_text(json.dumps({'ai_generated': True, 'credit': False, 'source_name': Path(CLIP_SRC[cid]).name}, indent=2), encoding='utf-8')
        else:
            for cand in (f'pexels-{cid}.mp4', f'pexels-{cid}.full.mp4'):
                src = ROOT / 'motion/hf/assets/clips' / cand
                if src.exists():
                    shutil.copy2(src, dst)
                    break
            else:
                print('THIẾU clip', cid)


if __name__ == '__main__':
    build_all()


