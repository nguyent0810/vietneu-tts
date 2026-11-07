"""Cảnh biên tập CL Long 4: Mata Hari ngoài đời thật (GH-228). Khung: data/long/dong-lang/gen_scenes.py.

Chương 00-02 ở file này; 03-05 ở gen_scenes2.py, 06-09 ở gen_scenes3.py, 10-13 ở gen_scenes4.py.
Chạy `python data/long/mata-hari/gen_scenes.py` để ghi spec.json và chNN.json (chỉ thêm hud, bgm, scenes; GIỮ NGUYÊN lines đã duyệt).

Mốc `at` không gõ chỉ số câu: c("đoạn chữ trong câu", "từ neo", cảnh) tự tìm câu chứa đoạn chữ (từ câu hiện tại trở đi),
chọn từ neo duy nhất trong câu (engine so khớp nguyên từ, cadence.py so khớp chuỗi con) rồi kiểm mốc tăng dần.
Mốc con trong cảnh (hàng ledger, mục kinetic…) viết Z("từ"): tìm từ đó từ mốc cảnh trở đi. ZL(n, lệch) = đầu câu (câu cảnh + n) lệch vài phần mười giây
(dùng để hàng thứ hai của ledger/file/timeline hiện trong 1 giây đầu cảnh). Không neo vào chữ số: TTS đọc số thành chữ.
Ước thời lượng: 4,2 âm tiết/giây (số đọc thành chữ tính theo số chữ số) + nghỉ `p` của câu.
"""
import json, sys, re, unicodedata, importlib.util
from collections import Counter
from pathlib import Path
D = Path(__file__).resolve().parent
ROOT = D.parents[2]
sys.path.insert(0, str(ROOT / "motion" / "long"))
from scenekit import sc, kin, write, FILMV

_RES = json.loads((ROOT / "output/long/mata-hari/research.json").read_text(encoding="utf-8"))["images"]


def im(i, must):
    f = _RES[i]["file"]
    if must not in f:
        raise ValueError(f"Ảnh {i} không khớp: {f}")
    return f


# (chỉ số research.json, chuỗi phải có trong tên file). Ảnh tư liệu Commons, engine tự tải.
_R = {
    # Mata Hari, ảnh thật (loại bỏ ảnh trước giờ hành quyết, ảnh phim xử bắn và ảnh khỏa thân)
    "mh_prof": (0, "Mata-Hari 1910"), "mh_arrest": (3, "day of her arrest"), "mh_merk": (5, "Jacob Merkelbach.jpg"),
    "mh_guimet": (8, "dancing in the Musée Guimet"), "mh_guimet2": (13, "Museum"), "mh_hat": (14, "Grietje"),
    "mh_pass": (16, "Mata-Hari 1915"), "mh_19": (19, "in 1917"), "mh_milan": (22, "in Milan"), "mh_veil": (17, "by Jacob Merkelbach"),
    "mh_1907": (15, "en 1907"), "mh_feather": (6, "MataHari15"),
    "pc1": (24, "Mata Hari 1.jpg"), "pc2": (25, "Mata Hari 2.jpg"), "pc3": (26, "Mata Hari 3.jpg"), "pc4": (27, "Mata Hari 4.jpg"),
    "pc5": (28, "Mata Hari 5.jpg"), "pc6": (29, "Mata Hari 6.jpg"), "pc7": (30, "Mata Hari 7.jpg"), "pc8": (31, "Mata Hari 8.jpg"),
    "pc9": (35, "MataHari16"), "pc10": (37, "5116"),
    "mh_film": (18, "1931 film promo"), "mh_stat": (1, "Mata Hari.jpg"), "mh_stat2": (23, "standbeeld"), "scrap": (2, "Plakboek"),
    "ladoux": (38, "Marthe Richard"),
    # Vincennes (ảnh hiện nay và tranh khắc)
    "vin_donjon": (40, "Donjon du Château de Vincennes.jpg"), "vin_water": (46, "VincennesWatercolor"), "vin_north": (47, "pixinn"),
    "vin_flag": (48, "Chateau de Vincennes.jpg"), "vin_moat": (54, "enceinte et douves"), "vin_keep": (55, "Vincennes - Chateau 02"),
    "vin_pav": (60, "Pavillon du roi"), "vin_chap": (66, "South-West View"), "vin_gate": (84, "Tour du village, Château"),
    "vin_entr": (91, "Entrance to the Château de Vincennes.jpg"), "vin_keep2": (92, "Keep of the"), "vin_side": (96, "Side of"),
    "vin_zeiller": (70, "Zeiller"), "vin_miller": (78, "William Miller"), "vin_lake": (39, "Bois de Vincennes"),
    # Leeuwarden
    "lw_old": (110, "Oldehove 1584"), "lw_waag": (123, "Waag"), "lw_stad": (106, "Stadhuis"), "lw_voor": (114, "Leeuwarden 1558"),
    "lw_fries": (111, "Fries Museum 1603"), "lw_fries2": (126, "Leeuwarden Fries Museum"), "lw_nieuw": (109, "Nieuwestad"),
    "lw_map": (102, "Beschrijving"), "lw_jus": (115, "Paleis van Justitie"), "lw_stat": (116, "Station Leeuwarden"),
    # Đông Ấn Hà Lan
    "dei_batavia": (137, "Hooggerechtshof"), "dei_deli": (139, "Deli Maatschappij"), "dei_gg": (143, "gouverneur-generaal aan het Koningsplein"),
    "dei_resid": (152, "huis van de resident"), "dei_castle": (153, "Kasteel Batavia"), "dei_map": (155, "Expansion"),
    "dei_art": (154, "1916 Dutch East Indies"), "dei_road": (162, "Rijweg op Buitenzorg"), "dei_road2": (168, "De weg van Buitenzorg naar de Preanger"),
    "dei_java": (166, "Java Topography"), "dei_knil": (157, "Elf Javaanse"), "dei_tea": (167, "theepluksters"),
    "dei_couple": (146, "Studioportret"), "dei_garden": (150, "Plantentuin"), "dei_bromo": (181, "Bromo"), "dei_dance": (185, "Ramayana"),
    "dei_hospital": (140, "STOVIA"), "dei_bank": (148, "Javasche Bank"),
    # Paris Belle Époque
    "paris_expo": (191, "Chateau d'eau"), "paris_cheret": (210, "Cheret"), "paris_mr": (217, "Paris 1914 Moulin Rouge"),
    "paris_fol": (200, "Grand-foyer"), "paris_fuller": (194, "Loie Fuller"), "paris_cine": (207, "Cinématographe"),
    "paris_tl": (214, "Toulouse-Lautrec, Moulin Rouge"), "paris_renoir": (206, "Dance at Le Moulin"), "paris_mist": (212, "Mistinguett"),
    "morse": (203, "Morsetaste"), "europe1911": (192, "Europe 1911"), "empires1914": (208, "Major World Empires"),
    "carte_fr": (205, "Carte de France"), "paris_mr2": (213, "April 2011"),
    # Bảo tàng Guimet
    "gui_rdc": (232, "Musee guimet rdc"), "gui_lib": (237, "Bibliotheque"), "gui_2013": (249, "Musee Guimet en 2013"),
    "gui_emile": (261, "Émile Guimet in his museum"), "gui_shiva": (240, "Shiva Natar"), "gui_brahma": (235, "Brahma Musée Guimet"),
}
IMGS, DIMS = {}, {}
for _k, _v in _R.items():
    IMGS[_k] = im(*_v)
    DIMS[_k] = (_RES[_v[0]]["w"], _RES[_v[0]]["h"])
# Tranh CC0 của Art Institute of Chicago (Belle Époque), engine tải qua EXT
IMGS.update({"paris_rain": "EXT:artic:20684", "jatte": "EXT:artic:27992", "terrace": "EXT:artic:14655"})
# Ảnh AI (Nhóm B/C): chỉ khai báo khóa theo ai_prompts.md, chưa dùng trong cảnh; Lead gắn khi ảnh về.
for _n in range(2, 17):
    IMGS[f"ai{_n:02d}"] = f"EXT:ai:ai_{_n:02d}"
PERSON = {k for k in _R if re.match(r"(mh_|pc[0-9]|ladoux)", k)}

# clip kho chung lib198v (thẻ minh_hoa_chung, credit false); bản sao ở output/long/mata-hari/broll/<mã>.mp4
V = {"h5": "198005", "h6": "198006", "h11": "198011", "h12": "198012", "h13": "198013", "h14": "198014", "h15": "198015"}
GEO = {
    "europe": {"countries": ["Netherlands", "France", "Spain", "United Kingdom"],
               "context": ["Belgium", "Germany", "Switzerland", "Italy", "Portugal", "Ireland", "Luxembourg", "Austria", "Denmark", "Andorra"],
               "labels": {"Netherlands": "HÀ LAN", "France": "PHÁP", "Spain": "TÂY BAN NHA", "United Kingdom": "ANH"},
               "bbox": [-11.0, 35.5, 15.5, 56.0], "box": [200, 120, 1720, 880],
               "pins": [{"name": "Leeuwarden", "lon": 5.79, "lat": 53.2, "label": "LEEUWARDEN"},
                        {"name": "Amsterdam", "lon": 4.9, "lat": 52.37, "label": "AMSTERDAM"},
                        {"name": "Paris", "lon": 2.35, "lat": 48.86, "label": "PARIS · VINCENNES"},
                        {"name": "Madrid", "lon": -3.7, "lat": 40.42, "label": "MADRID"},
                        {"name": "Falmouth", "lon": -5.07, "lat": 50.15, "label": "FALMOUTH"},
                        {"name": "London", "lon": -0.13, "lat": 51.51, "label": "LONDON"},
                        {"name": "Berlin", "lon": 13.4, "lat": 52.52, "label": "BERLIN"},
                        {"name": "Chemin des Dames", "lon": 3.7, "lat": 49.45, "label": "CHEMIN DES DAMES"}]},
    "indies": {"countries": ["Indonesia"], "context": ["Malaysia", "Singapore", "Thailand", "Brunei", "Philippines", "Australia", "Papua New Guinea", "Timor-Leste"],
               "labels": {"Indonesia": "ĐÔNG ẤN HÀ LAN (NAY LÀ INDONESIA)"},
               "bbox": [94.0, -11.5, 120.0, 6.5], "box": [200, 120, 1720, 880],
               "pins": [{"name": "Java", "lon": 110.0, "lat": -7.3, "label": "JAVA"},
                        {"name": "Sumatra", "lon": 101.5, "lat": -0.5, "label": "SUMATRA"}]},
}

TD = "TÁI DỰNG MINH HỌA"
NOW = "NGÀY NAY"
KB = "ẢNH TƯ LIỆU"


# ---------------------------------------------------------------- mốc
def norm(w):
    return re.sub(r"[^\w]", "", unicodedata.normalize("NFC", w.lower()))


class Z:
    def __init__(self, w):
        self.w = w


class ZL:
    """Đầu câu (câu của cảnh + n), lệch `off` giây."""
    def __init__(self, n=0, off=0.3):
        self.n, self.off = n, off


def _text(x):
    return x if isinstance(x, str) else x["t"]


def syl(tok):
    d = sum(ch.isdigit() for ch in tok)
    if d:
        return {1: 1, 2: 2, 3: 3, 4: 6, 5: 4, 6: 6}.get(d, 6)
    return 1


SYL_S = 1 / 4.2
SERIES = {"ledger": "rows", "file": "rows", "timeline": "items", "map": "pins", "bars": "items", "org": "nodes", "kinetic": "items"}


class Ch:
    def __init__(self, name):
        self.name = name
        d = json.loads((D / f"{name}.json").read_text(encoding="utf-8"))
        self.lines = [_text(x) for x in d["lines"]]
        self.pz = [0.0 if isinstance(x, str) else float(x.get("p", 0)) for x in d["lines"]]
        self.toks = [l.split() for l in self.lines]
        self.cur = (-1, -1)
        self.out = []
        self.pos = []

    def _ok(self, i, k):
        t = self.toks[i]
        n = norm(t[k])
        if not n or any(c.isdigit() for c in n):
            return False
        if sum(1 for x in t if norm(x) == n) != 1:
            return False
        if any(n in norm(x) for x in t[:k]):
            return False
        return True

    def _tok(self, i, k):
        return re.sub(r"^[^\w]+|[^\w]+$", "", self.toks[i][k])

    def anchor(self, sub, w):
        sub_c = sub.casefold()
        for i in range(max(self.cur[0], 0), len(self.lines)):
            if sub_c not in self.lines[i].casefold():
                continue
            if w == "^":
                if i > self.cur[0]:
                    self.cur = (i, -1)
                    return i
                continue
            pre = self.lines[i].casefold().index(sub_c)
            k0 = len(self.lines[i][:pre].split())
            if w:
                cands = [k for k, x in enumerate(self.toks[i]) if norm(x) == norm(w)][:1]
            else:
                cands = list(range(k0, min(len(self.toks[i]), k0 + max(1, len(sub.split())))))
            for k in cands:
                if (i, k) > self.cur and self._ok(i, k):
                    self.cur = (i, k)
                    return [i, self._tok(i, k)]
        raise ValueError(f"{self.name}: không neo được {sub!r}/{w!r} sau mốc {self.cur}")

    def find(self, word, start):
        i0, k0 = start
        for i in range(max(i0, 0), min(len(self.lines), i0 + 5)):
            for k, x in enumerate(self.toks[i]):
                if i == i0 and k < k0:
                    continue
                if norm(x) == norm(word) and self._ok(i, k):
                    return [i, self._tok(i, k)]
        raise ValueError(f"{self.name}: không thấy Z({word!r}) từ {start}")

    def _res(self, o, start):
        if isinstance(o, Z):
            return self.find(o.w, start)
        if isinstance(o, ZL):
            return [start[0] + o.n, None, 0, o.off]
        if isinstance(o, dict):
            return {k: self._res(v, start) for k, v in o.items()}
        if isinstance(o, list):
            return [self._res(v, start) for v in o]
        return o

    def __call__(self, sub, w, scene):
        a = self.anchor(sub, w)
        start = (a, 0) if isinstance(a, int) else (a[0], self.cur[1])
        scene = self._res(scene, start)
        scene["at"] = a
        self.out.append(scene)
        self.pos.append(self.cur)

    def first(self, scene):
        scene = self._res(scene, (0, 0))
        self.out.append(scene)
        self.pos.append((0, -1))
        self.cur = (0, 0)

    # ----- ước giờ
    def tm(self, pos):
        i, k = pos
        t = sum(sum(syl(x) for x in self.toks[j]) * SYL_S + self.pz[j] for j in range(max(i, 0)))
        if k > 0:
            t += sum(syl(x) for x in self.toks[i][:k]) * SYL_S
        return t

    def at_t(self, a):
        if isinstance(a, int):
            return self.tm((a, 0))
        if isinstance(a, list):
            i = a[0]
            if len(a) > 1 and a[1] is not None:
                k = next(k for k, x in enumerate(self.toks[i]) if norm(x) == norm(a[1]))
                return self.tm((i, k))
            return self.tm((i, 0)) + (a[3] if len(a) > 3 else 0)
        return float(a)

    def done(self, hud, bgm):
        end = self.tm((len(self.lines), 0))
        starts = [self.tm(p) for p in self.pos]
        starts[0] = 0.0
        ts = starts + [end]
        changes = 0
        worst = 0
        for n, s in enumerate(self.out):
            a, b = ts[n], ts[n + 1]
            dur = b - a
            if dur < 3.1 or dur > 8.5:
                print(f"  ! {self.name} cảnh {n} ({s['type']}) ước {dur:.1f}s")
            ev = {round(a, 2)}
            key = SERIES.get(s["type"])
            if key and isinstance(s.get(key), list):
                sub = sorted(self.at_t(it["at"]) for it in s[key] if isinstance(it, dict) and "at" in it)
                ev |= {round(x, 2) for x in sub if a < x < b}
                if s["type"] in ("ledger", "file", "timeline", "map", "org") and len(sub) >= 2 and sub[1] - a > 1.05:
                    print(f"  ! {self.name} cảnh {n} ({s['type']}) phần tử con thứ hai lúc +{sub[1] - a:.1f}s")
            if s["type"] == "split":
                tb = self.at_t(s["b"]["at"])
                ev.add(round(tb, 2))
                if tb - a > 1.05:
                    print(f"  ! {self.name} cảnh {n} (split) vế b lúc +{tb - a:.1f}s")
            if s["type"] == "evidence":
                sub = sorted(self.at_t(it["at"]) for it in s["callouts"])
                if len(sub) >= 2 and sub[1] - a > 1.05:
                    print(f"  ! {self.name} cảnh {n} (evidence) callout thứ hai lúc +{sub[1] - a:.1f}s")
            if s["type"] == "counter" and s.get("countAt") is not None and self.at_t(s["countAt"]) - a > 1.05:
                print(f"  ! {self.name} cảnh {n} (counter) đứng yên {self.at_t(s['countAt']) - a:.1f}s")
            if s["type"] not in FRAME and not (s.get("bg") or s.get("img") or s.get("vid")):
                firsts = []
                def _walk(o, k=None):
                    if isinstance(o, dict):
                        for kk, vv in o.items():
                            if kk == "at" and o is s:
                                continue
                            _walk(vv, kk)
                    elif isinstance(o, list) and not (len(o) >= 1 and isinstance(o[0], int) and k):
                        for vv in o:
                            _walk(vv, k)
                    elif isinstance(o, list) or isinstance(o, int):
                        if k and (k == "at" or k.endswith("At")):
                            firsts.append(self.at_t(o))
                _walk(s)
                if firsts and min(firsts) - a > 1.05 and s["type"] != "kinetic":
                    print(f"  ! {self.name} cảnh {n} ({s['type']}) màn trống {min(firsts) - a:.1f}s")
            pts = sorted(ev | {round(b, 2)})
            changes += len(pts) - 1
            worst = max(worst, max(y - x for x, y in zip(pts, pts[1:])))
        avg = end / max(changes, 1)
        flag = "  <<< > 5 s" if avg > 5 else ""
        print(f"{self.name}: {len(self.out)} cảnh · ước {end:.0f}s · {changes} lần đổi hình · {avg:.2f}s/lần · khoảng dài nhất {worst:.1f}s{flag}")
        STATS[self.name] = (end, changes)
        DURS[self.name] = [ts[n + 1] - ts[n] for n in range(len(self.out))]
        return dict(hud=hud, bgm=bgm, scenes=self.out)


STATS = {}
DURS = {}
FRAME = {"chapter", "brand", "endcard", "question", "quote", "ledger", "bars", "print", "photo", "broll", "file", "map"}


# ---------------------------------------------------------------- dựng cảnh
def ph(img, illus=None, move="in", **k):
    d = dict(img=img, tone="color", move=move, **k)
    if illus:
        d["illus"] = illus
    if img in DIMS and DIMS[img][1] > DIMS[img][0] * 1.15 and "focus" not in d:
        d["focus"] = [0.5, 0.22 if img in PERSON else 0.45]
        d.setdefault("frame", True)
    return sc("photo", **d)


def _kin(items):
    out = []
    for it in items:
        t, w, *r = it
        e = {"text": t, "at": Z(w) if isinstance(w, str) else w}
        for x in r:
            e[x] = True
        out.append(e)
    return out


def K(*items, bg=None, **k):
    d = dict(items=_kin(items), **k)
    if bg:
        d["bg"] = bg
    return sc("kinetic", **d)


def S(text, w, bg=None, sub=None, **k):
    d = dict(text=text, hitAt=Z(w), **k)
    if bg:
        d["bg"] = bg
    if sub:
        d["sub"] = sub
    return sc("slam", **d)


def Dt(day, date, bg, sub=None):
    d = dict(bg=bg, day=day, date=date)
    if sub:
        d["sub"] = sub
    return sc("date", **d)


def Q(text, bg):
    return sc("question", bg=bg, text=text)


def F(k, name, desc, bg=None, rows=None, **kw):
    d = dict(k=k, name=name, desc=desc, **kw)
    if bg:
        d["bg"] = bg
    if rows:
        d["rows"] = [{"k": a, "v": b, "at": Z(c) if isinstance(c, str) else c} for a, b, c in rows]
    return sc("file", **d)


def L(title, rows, bg=None):
    d = dict(title=title, rows=[{"k": a, "v": b, "at": Z(c) if isinstance(c, str) else c} for a, b, c in rows])
    if bg:
        d["bg"] = bg
    return sc("ledger", **d)


def T(items, bg=None, title=None):
    d = dict(items=[{"year": a, "text": b, "at": Z(c) if isinstance(c, str) else c} for a, b, c in items])
    if bg:
        d["bg"] = bg
    if title:
        d["title"] = title
    return sc("timeline", **d)


def C(to, suffix, label, w, bg, year=False, frm=0):
    """w=None: đếm ngay từ đầu cảnh (build_long cấm số đứng yên > 1 s)."""
    d = {"from": frm, "to": to, "suffix": suffix, "label": label, "bg": bg}
    if w:
        d["countAt"] = Z(w)
    if year:
        d["year"] = True
    return sc("counter", **d)


def VC(v, *items, tone="noir", veil=0.4):
    return sc("broll", vid=V[v], tone=tone, veil=veil, illus=FILMV, kin=_kin(items))


def SP(title, a, b):
    return sc("split", title=title, a={"img": a[0], "label": a[1], "at": Z(a[2]) if isinstance(a[2], str) else a[2]},
              b={"img": b[0], "label": b[1], "at": Z(b[2]) if isinstance(b[2], str) else b[2]})


def O(nodes, bg=None):
    ns = []
    for id_, t, s, p, cls, w in nodes:
        n = {"id": id_, "t": t, "s": s, "at": Z(w) if isinstance(w, str) else w}
        if p:
            n["p"] = p
        if cls:
            n["cls"] = cls
        ns.append(n)
    d = dict(nodes=ns)
    if bg:
        d["bg"] = bg
    return sc("org", **d)


def M(geo, pins, zoom=None, zk=1.5):
    d = dict(geo=geo, pins=[{"name": n, "label": lb, "at": Z(w) if isinstance(w, str) else w} for n, lb, w in pins])
    if zoom:
        d.update(zoom=zoom, zoomK=zk)
    return sc("map", **d)


def PR(img, k, h, lines, **kw):
    return sc("print", img=img, tone="color", side={"k": k, "h": h, "hAt": Z(lines[0][1]),
              "lines": [{"text": t, "at": Z(w)} for t, w in lines]}, **kw)


def EV(img, calls, **kw):
    return sc("evidence", img=img, tone="color", maxW=700, maxH=760,
              callouts=[{"x": x, "y": y, "text": t, "side": s, "at": Z(w)} for x, y, t, s, w in calls], **kw)


def BR(title, unit, items, bg=None):
    d = dict(title=title, unit=unit, items=[dict(k=a, v=b, at=Z(c) if isinstance(c, str) else c) for a, b, c in items])
    if bg:
        d["bg"] = bg
    return sc("bars", **d)


def Bq(c, text, by, sub, w, lbl="TRÍCH DỊCH", bg=None):
    """Cảnh quote: qline = câu chứa lời trích."""
    a = c.anchor(sub, w)
    li = a if isinstance(a, int) else a[0]
    s = sc("quote", text=text, by=by, lbl=lbl, qline=li, typeAt=a)
    if bg:
        s["bg"] = bg
    s["at"] = a
    c.out.append(s)
    c.pos.append(c.cur)


CH = {}
CHAPTERS = [f"ch{n:02d}" for n in range(14)]
TITLES = ["HÀO NƯỚC VINCENNES", "BỐN CON SỐ", "CÔ BÉ Ở LEEUWARDEN", "ĐÔNG ẤN HÀ LAN", "CÁI TÊN", "NGHỀ DIỄN VÀ HỘ CHIẾU HÀ LAN",
          "MỘT TRIỆU FRANC", "FALMOUTH VÀ MADRID", "BỨC ĐIỆN H-21", "KHÁCH SẠN ELYSÉE PALACE", "PHIÊN TÒA", "MÙA XUÂN NĂM 1917",
          "TỪ CHỐI ÂN XÁ", "HỒ SƠ MỞ NĂM 2017"]
SAY = {"Margaretha": "Mác-ga-rê-ta", "Zelle": "Zê-lơ", "Geertruida": "Gát-tra-i-đa", "Leeuwarden": "Lê-oa-đen", "Friesland": "Phờ-ri-xlan",
       "Fries": "Phờ-rít", "Museum": "Mu-dê-um", "Mata": "Ma-ta", "Hari": "Ha-ri", "Vincennes": "Vanh-xen", "Paris": "Pa-ri",
       "Adam": "A-đam", "Antje": "An-chơ", "Meulen": "Mơ-len", "Rudolf": "Ru-đôn", "MacLeod": "Mác-lau", "Amsterdam": "Am-xtơ-đam",
       "Java": "Gia-va", "Sumatra": "Xu-ma-tra", "Indonesia": "In-đô-nê-xi-a", "Norman-John": "Noóc-man Giôn", "Louise": "Lu-ít",
       "Jeanne": "Giăn", "Lady": "Lê-đi", "Guimet": "Ghi-mê", "Émile": "Ê-min", "Bouchardon": "Bu-sác-đông", "Pierre": "Pi-e",
       "Belle": "Bên", "Époque": "Ê-pốc", "Hollywood": "Hô-li-út", "Greta": "Grê-ta", "Garbo": "Gác-bô", "Wilhelm": "Vin-hem",
       "Maslov": "Mát-lốp", "Vadim": "Va-đim", "Ladoux": "La-đu", "Georges": "Giooc", "Deuxième": "Đơ-di-em", "Bureau": "Bi-rô",
       "Zeelandia": "Giê-lan-đi-a", "Falmouth": "Phan-mớt", "London": "Lân-đơn", "Thomson": "Tôm-xơn", "Basil": "Ba-din",
       "Scotland": "Xcốt-len", "Yard": "Gia", "Canon": "Ca-nần", "Row": "Râu", "Savoy": "Xa-voa", "Madrid": "Ma-đrít", "Arnold": "Ác-nôn",
       "Kalle": "Ka-lơ", "Berlin": "Béc-lin", "Wesley": "Oét-li", "Wark": "Voóc", "Julie": "Giu-li", "Wheelwright": "Quin-rai",
       "Pat": "Pát", "Shipman": "Síp-man", "Elysée": "Ê-li-dê", "Champs-Élysées": "Săng Ê-li-dê", "Palace": "Pa-lát",
       "Saint-Lazare": "Săng La-da", "Mornet": "Moóc-nê", "Édouard": "Ê-đu-a", "Clunet": "Clu-nê", "Nivelle": "Ni-ven",
       "Robert": "Rô-be", "Aisne": "En", "Chemin": "Sơ-manh", "Dames": "Đam", "Pétain": "Pê-tanh", "Poincaré": "Poăng-ca-rê",
       "Raymond": "Rê-mông", "Bizard": "Bi-da", "Philippe": "Phi-líp", "Collas": "Cô-la", "MI5": "Em Ai Năm", "H-21": "Hát hai mốt",
       "KV": "Ca Vê"}
SOURCES = ["https://en.wikipedia.org/wiki/Mata_Hari", "https://fr.wikipedia.org/wiki/Mata_Hari",
           "https://en.wikipedia.org/wiki/Nivelle_offensive", "https://en.wikipedia.org/wiki/Mata_Hari_(1931_film)",
           "https://en.wikipedia.org/wiki/Guimet_Museum", "https://en.wikipedia.org/wiki/Leeuwarden",
           "https://en.wikipedia.org/wiki/Dutch_East_Indies", "https://discovery.nationalarchives.gov.uk/"]
SPEC = {
    "title": "Mata Hari Ngoài Đời Thật: Bốn Con Số Và Hồ Sơ Mở Năm 2017",
    "channel": "CL", "accent": "#5f93b8", "look": "steel", "theme": "noir", "autoTr": True, "master": True, "craft": True,
    "endcard": 9, "endcardSub": "HỒ SƠ TIẾP THEO",
    "acc": ["mata hari", "margaretha zelle", "vincennes", "ladoux", "bouchardon", "maslov", "kalle", "h-21"],
    "say": SAY, "chapters": CHAPTERS,
    "youtube": {
        "titles": ["MATA HARI Ngoài Đời Thật: Một Triệu Franc Chưa Trả, 50.000 Lính Không Ai Đếm",
                   "MATA HARI Ngoài Đời Thật: Nữ Điệp Viên Quyến Rũ Và Hồ Sơ 1.275 Trang Mở Năm 2017",
                   "MATA HARI Ngoài Đời Thật: Nụ Hôn Gió Không Có Trong Biên Bản — Vậy Điều Gì Có?"],
        "summary": "Hồ sơ Mata Hari qua bốn con số: một triệu franc chưa bao giờ trả, 20.000 franc có thật nhưng hai cách đọc, 50.000 lính chưa từng có nguồn kiểm đếm, và 12 người trong hàng súng. Đi từ cô bé Margaretha Zelle ở Leeuwarden, Đông Ấn Hà Lan, sân khấu Paris, Deuxième Bureau, Falmouth, Madrid, bức điện H-21, phiên tòa tháng 7/1917 đến hồ sơ 1.275 trang mở năm 2017: chuyện nào là hồ sơ, chuyện nào chỉ là giai thoại.",
        "more": [], "sources": SOURCES,
        "tags": ["mata hari", "mata hari ngoài đời thật", "margaretha zelle", "nữ điệp viên", "điệp viên thế chiến 1", "vincennes 1917",
                 "ladoux", "bouchardon", "maslov", "bức điện h-21", "hồ sơ 1.275 trang", "greta garbo mata hari", "hồ sơ hình sự",
                 "into the killer's mind"],
        "hashtags": ["MataHari", "HoSo", "ChienTranhTheGioi1"], "category": "24",
        "ch00_title": "Mở đầu: Hào nước Vincennes, 15/10/1917", "thumb": "t1.jpg", "publish_at": "2026-11-29T14:00:00Z", "playlist": "Ngoài Đời Thật",
        "chapter_titles": TITLES, "video_credits": [],
    },
}


def walk_used(x, used):
    if isinstance(x, dict):
        for k, v in x.items():
            if k in ("img", "bg") and isinstance(v, str):
                used.append(v)
            walk_used(v, used)
    elif isinstance(x, list):
        for v in x:
            walk_used(v, used)


def run_all():
    sys.modules["gen_scenes"] = sys.modules[__name__]
    for n in ("2", "3", "4"):
        p = D / f"gen_scenes{n}.py"
        if not p.exists():
            continue
        spec = importlib.util.spec_from_file_location(f"g{n}", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        CH.update(mod.CH)


def B(c, mood):
    return {"mood": mood, "at": 0, "gain": 0.12}


# ================================================================ CH00
c = Ch("ch00")
c.first(Dt("RẠNG SÁNG · VINCENNES", "15.10.1917", "vin_moat"))
c("Trời chưa sáng hẳn", "^", VC("h15", ("TRỜI CHƯA SÁNG HẲN", "Trời"), ("MỘT TIỂU ĐỘI ĐÃ ĐỨNG SẴN", "tiểu", "acc")))
c("Họ là lính Pháp", "^", ph("mh_arrest", "ẢNH NGÀY BỊ BẮT · 13.02.1917"))
c("Khai sinh", "^", F("KHAI SINH", "MARGARETHA\nZELLE", "Sinh ở Leeuwarden, Hà Lan", bg="mh_pass", rows=[("TÊN KHÁC", "MATA HARI", Z("Mata"))]))
c("Theo lời một phóng viên", "^", K(("THEO MỘT PHÓNG VIÊN ANH", "phóng"), ("BÀ KHÔNG BỊ TRÓI", "trói", "acc"), ("TỪ CHỐI BỊT MẮT", "chối"), bg="vin_keep2"))
c("Ông kể thêm", "^", Q("MỘT NỤ HÔN GIÓ?", "mh_milan"))
c("Đó là lời kể", "^", K(("LỜI KỂ CỦA MỘT NHÀ BÁO", "nhà"), ("KHÔNG PHẢI BIÊN BẢN CỦA TÒA", "biên", "acc"), bg="scrap"))
c("Biên bản của tòa nói", "^", F("BIÊN BẢN CỦA TÒA", "MỘT ĐIỀU\nKHÁC", "Không phải lời kể của nhà báo", bg="vin_gate", rows=[("CÁO TRẠNG", "CHUYỂN TIN CHO ĐỨC", Z("chuyển"))]))
c("Ít nhất", "^", C(50000, " LÍNH", "THEO CÁO TRẠNG · KHÔNG CÓ NGUỒN KIỂM ĐẾM", None, "vin_chap"))
c("năm 2017", "năm", Dt("QUÂN ĐỘI PHÁP MỞ HỒ SƠ NIÊM PHONG", "2017", "vin_pav"))
c("Hồ sơ dày", "^", VC("h14", ("HỒ SƠ DÀY 1.275 TRANG", "trang"), ("CHUYỆN CŨ CÓ NHỮNG CHỖ HỞ", "chỗ", "acc")))
c("Bà đã chuyển đi", "^", Q("BÀ ĐÃ CHUYỂN ĐI ĐIỀU GÌ, NẾU CÓ?", "mh_19"))
CH["ch00"] = c.done({"k": "MỞ ĐẦU", "t": "HÀO NƯỚC VINCENNES"}, B(c, "tense"))
# ================================================================ CH01
c = Ch("ch01")
c.first(K(("MATA HARI", "Mata"), ("THÀNH DANH TỪ CHUNG", "chung", "acc"), ("NỮ ĐIỆP VIÊN QUYẾN RŨ", "viên"), bg="paris_cheret"))
c("Năm 1931", "^", ph("mh_film", "QUẢNG CÁO PHIM · 1931"))
c("Từ đó", "^", SP("PHIM VÀ NGƯỜI THẬT", ("mh_film", "TRÊN PHIM", ZL(0, 0.2)), ("mh_hat", "NGƯỜI THẬT", ZL(0, 0.8))))
c("Nó cho người xem", "^", K(("MỘT NGƯỜI PHỤ NỮ", "phụ"), ("MỘT BÍ MẬT", "bí"), ("MỘT ĐÊM TỐI", "đêm", "acc"), bg="paris_fol"))
c("Và một cái kết", "^", S("MỘT CÁI KẾT VIẾT TRƯỚC", "trước", bg="paris_cine"))
c("Nhưng dễ nhớ", "^", VC("h13", ("DỄ NHỚ KHÔNG NGHĨA LÀ ĐÚNG", "đúng"), ("MỘT CÁCH KHÁC", "cách"), ("BỐN CON SỐ", "bốn", "acc")))
c("Con số đầu tiên", "^", C(1000000, " FRANC", "LỜI HỨA · CHƯA BAO GIỜ TRẢ", None, "paris_expo"))
c("Con số thứ hai", "^", F("CON SỐ THỨ HAI", "20.000 FRANC", "Một khoản tiền có thật", bg="paris_mr", rows=[("NGƯỜI ĐƯA", "NHÀ NGOẠI GIAO ĐỨC", Z("ngoại"))]))
c("Con số thứ ba", "^", C(50000, " LÍNH", "THEO CÁO TRẠNG · KHÔNG CÓ NGUỒN KIỂM ĐẾM", None, "vin_zeiller"))
c("Con số thứ tư", "^", S("12 NGƯỜI TRONG HÀNG SÚNG", "hàng", bg="vin_moat"))
c("Mỗi con số", "^", K(("MỖI CON SỐ MỘT NGUỒN", "nguồn"), ("MỖI NGUỒN MỘT ĐỘ TIN CẬY", "tin"), ("TÁCH HAI LOẠI CHUYỆN", "tách", "acc"), bg="paris_rain"))
c("Chuyện nào hồ sơ", "^", SP("HAI LOẠI CHUYỆN", ("vin_gate", "HỒ SƠ", ZL(0, 0.2)), ("scrap", "GIAI THOẠI", ZL(0, 0.8))))
c("Có biên bản", "^", L("CÁC LỚP HỒ SƠ", [("PHÁP", "BIÊN BẢN THẨM VẤN", ZL(0, 0.3)), ("ANH", "MI5 · LƯU TRỮ QUỐC GIA ANH", ZL(0, 0.9))]))
c("Có tập hồ sơ", "^", F("LỚP THỨ BA", "1.275 TRANG", "Pháp mở năm 2017", bg="vin_pav", rows=[("MỞ NĂM", "2017", Z("mở"))]))
c("Và có công trình", "^", K(("CÔNG TRÌNH CỦA CÁC SỬ GIA", "công"), bg="gui_lib"))
c("Câu nào gán", "^", S("KHÔNG KIỂM CHỨNG ĐƯỢC · TA NÓI RÕ", "kiểm", bg="mh_guimet"))
c("Báo chí thời ấy", "^", K(("BÁO CHÍ KỂ", "Báo"), ("ĐIỆN ẢNH KỂ", "Điện"), ("CHÍNH BÀ CŨNG KỂ", "Chính", "acc"), bg="paris_tl"))
c("Nhưng muốn hiểu bà", "^", M("europe", [("Leeuwarden", "LEEUWARDEN", "thành")], zoom="Leeuwarden", zk=2.0))
CH["ch01"] = c.done({"k": "CHƯƠNG 01", "t": "BỐN CON SỐ"}, B(c, "mystery"))
# ================================================================ CH02
c = Ch("ch02")
c.first(Dt("LEEUWARDEN · HÀ LAN", "07.08.1876", "lw_old"))
c("Một bé gái", "^", F("TÊN KHAI SINH", "MARGARETHA\nGEERTRUIDA\nZELLE", "Bé gái ra đời ở Leeuwarden", bg="lw_voor", rows=[("CHA", "ADAM ZELLE", Z("Adam"))]))
c("Ông có một cửa hiệu", "^", K(("MỘT CỬA HIỆU BÁN MŨ", "cửa"), ("KÈM XƯỞNG LÀM MŨ", "xưởng", "acc"), ("NHỮNG NĂM ĐẦU NHÀ KHÁ GIẢ", "năm"), bg="lw_nieuw"))
c("Theo các tiểu sử", "^", ph("lw_waag", "LEEUWARDEN NGÀY NAY"))
c("Đó là lời kể", "^", S("KHÔNG PHẢI GIẤY TỜ", "giấy", bg="scrap"))
c("Leeuwarden là thủ phủ", "^", M("europe", [("Leeuwarden", "LEEUWARDEN", "Leeuwarden")], zoom="Leeuwarden", zk=2.2))
c("bức tượng", "tượng", SP("LEEUWARDEN HÔM NAY", ("mh_stat", "TƯỢNG CỦA BÀ", ZL(0, 0.2)), ("lw_fries", "FRIES MUSEUM", ZL(0, 0.8))))
c("Nhưng ta đang nói", "^", ph("lw_stad", "LEEUWARDEN NGÀY NAY", move="pan"))
c("Năm 1889", "^", Dt("CỬA HIỆU PHÁ SẢN · CHA MẸ LY HÔN", "1889", "lw_jus"))
c("Cô bé chưa đầy", "^", S("MẤT MỘT NGÔI NHÀ", "ngôi", bg="lw_fries2"))
c("Năm 1891", "^", Dt("MẸ QUA ĐỜI · ANTJE VAN DER MEULEN", "1891", "lw_voor"))
c("Từ đó, bà sống", "^", K(("SỐNG NHỜ HỌ HÀNG", "nhờ"), ("VÀ NGƯỜI QUEN", "quen", "acc"), ("TIỂU SỬ DỪNG LẠI Ở ĐÂY", "dừng"), bg="lw_nieuw"))
c("Người viết thường nói", "^", K(("KHÔNG TIỀN", "tiền"), ("KHÔNG AI BẢO HỘ", "bảo"), ("ÁNH NHÌN CỦA NGƯỜI KHÁC", "nhìn", "acc"), bg="mh_hat"))
c("Đó là cách đọc", "^", S("CÁCH ĐỌC · KHÔNG PHẢI HỒ SƠ", "hồ", bg="scrap"))
c("Rồi đến năm 1895", "^", Dt("BÀ 18 TUỔI", "1895", "lw_stad"))
c("Theo các tiểu sử, bà trả lời", "^", K(("MỘT MỤC TÌM BẠN ĐỜI", "mục"), ("ĐĂNG TRÊN BÁO", "báo"), ("NGƯỜI ĐĂNG: MỘT SĨ QUAN", "sĩ", "acc"), bg="scrap"))
c("Tên ông là", "^", F("TÊN ÔNG", "RUDOLF\nMACLEOD", "Sĩ quan quân đội Hà Lan", bg="paris_rain", rows=[("CƯỚI NGÀY", "11.07.1895 · AMSTERDAM", Z("cưới"))]))
c("Ông lớn hơn", "^", K(("ÔNG LỚN TUỔI HƠN BÀ", "lớn"), ("ÔNG SẮP SANG THUỘC ĐỊA", "thuộc"), ("BÀ ĐI CÙNG", "cùng", "acc"), bg="dei_gg"))
c("Đến một nơi", "^", S("MỘT NƠI ĐỂ ĐẶT TÊN CHO ĐỜI MÌNH", "tên", bg="dei_castle"))
CH["ch02"] = c.done({"k": "CHƯƠNG 02", "t": "CÔ BÉ Ở LEEUWARDEN"}, B(c, "quiet"))

# ================================================================ CH03
c = Ch("ch03")
c.first(ph("dei_map", "BẢN ĐỒ ĐÔNG ẤN HÀ LAN · MỞ RỘNG THEO THỜI KỲ"))
c("Gia đình sống", "^", M("indies", [("Java", "JAVA", ZL(0, 0.3)), ("Sumatra", "SUMATRA", ZL(0, 0.9))]))
c("Con trai tên", "^", F("BÀ SINH HAI CON", "NORMAN-JOHN\nLOUISE JEANNE", "Hai đứa trẻ sinh ở Đông Ấn Hà Lan", bg="dei_garden", rows=[("SINH NĂM 1897", "CON TRAI", "trai"), ("SINH NĂM 1898", "CON GÁI", ZL(0, 0.95))]))
c("Bà khi ấy", "^", K(("BÀ CÒN RẤT TRẺ", "trẻ"), ("HÔN NHÂN KHÔNG ÊM", "Hôn", "acc"), bg="dei_couple"))
c("Các tiểu sử mô tả", "^", K(("THEO CÁC TIỂU SỬ", "Các"), ("CHỒNG HAY UỐNG RƯỢU, HAY NỔI GIẬN", "uống", "acc"), ("TỪ LỜI KỂ CỦA BÀ", "kể"), bg="dei_resid"))
c("Ta chỉ có thể", "^", S("CHỈ LÀ ĐIỀU ĐƯỢC KỂ LẠI", "kể", bg="scrap"))
c("Ở đoạn đời này", "^", K(("ÍT TÀI LIỆU GỐC NHẤT", "ít"), ("THƯ TỪ", "thư"), ("LỜI KHAI", "khai"), ("HỒI ỨC", "hồi", "acc"), bg="dei_hospital"))
c("Điều ấy không", "^", S("PHẢI NÓI CHẬM HƠN", "chậm", bg="dei_bank"))
c("Và phải nhớ", "^", Q("NGƯỜI KỂ CÓ LÝ DO ĐỂ KỂ?", "dei_road"))
c("Java là hòn đảo", "^", M("indies", [("Java", "JAVA · ĐÔNG DÂN NHẤT", "Java"), ("Sumatra", "SUMATRA", ZL(0, 0.9))]))
c("Đối với một cô gái", "^", ph("dei_road2", "TRANH KHẮC · ĐƯỜNG Ở JAVA"))
c("Chính trong thế giới ấy", "^", ph("dei_dance", "MÚA RAMAYANA Ở JAVA · ẢNH NGÀY NAY", move="pan"))
c("Năm 1899", "^", F("1899 · NORMAN-JOHN QUA ĐỜI", "TÀI LIỆU\nTIẾNG PHÁP", "Chỉ cô con gái sống sót", bg="dei_resid", rows=[("GHI RẰNG", "HAI ĐỨA TRẺ BỊ ĐẦU ĐỘC", "đầu")]))
c("Các tài liệu tiếng Anh", "^", F("TÀI LIỆU TIẾNG ANH", "NGUYÊN NHÂN\nCÒN TRANH CÃI", "Ta giữ cả hai cách ghi", bg="dei_bank", rows=[("TA GIỮ", "CẢ HAI CÁCH GHI", Z("giữ"))]))
c("Gia đình trở về", "^", Dt("HAI VỢ CHỒNG LY THÂN", "30.08.1902", "lw_stad"))
c("Việc ly hôn", "^", T([("1902", "LY THÂN", ZL(0, 0.1)), ("1906", "LY HÔN HOÀN TẤT", "hoàn")], bg="lw_voor"))
c("Có tài liệu nói", "^", SP("AI NUÔI CÔ CON GÁI?", ("lw_fries2", "TÀI LIỆU NÓI: BÀ NUÔI", ZL(0, 0.2)), ("dei_gg", "TÀI LIỆU KHÁC: CHỒNG ĐƯA ĐI", ZL(0, 0.8))))
c("Điều chắc chắn", "^", Dt("LOUISE JEANNE MẤT · HAI NĂM SAU MẸ", "1919", "lw_jus"))
c("Khi hôn nhân", "^", K(("KHÔNG CÒN CHỒNG", "chồng"), ("KHÔNG CÒN CON TRAI", "trai"), ("KHÔNG CÓ NGHỀ", "nghề", "acc"), bg="lw_nieuw"))
c("Và bà quyết định", "^", K(("MỘT NƠI KHÁC", "khác"), ("ÁNH NHÌN CỦA NGƯỜI KHÁC", "nhìn"), ("LÀ THỨ CÓ THỂ BÁN", "bán"), ("ĐÓ LÀ PARIS", "Đó", "acc"), bg="paris_fol"))
CH["ch03"] = c.done({"k": "CHƯƠNG 03", "t": "ĐÔNG ẤN HÀ LAN"}, B(c, "mystery"))


# ================================================================ CH04
c = Ch("ch04")
c.first(Dt("BÀ ĐẾN PARIS", "1903", "paris_expo"))
c("Có nguồn kể bà làm", "^", K(("CÓ NGUỒN KỂ: MẪU VẼ", "mẫu"), ("CÓ NGUỒN KỂ: RẠP XIẾC", "xiếc", "acc"), bg="paris_tl"))
c("Ta nên nói rõ, những", "^", S("TỪ TIỂU SỬ · KHÔNG TỪ GIẤY TỜ", "giấy", bg="scrap"))
c("Rồi bà tìm ra", "^", F("TỰ GỌI MÌNH", "LADY\nMACLEOD", "Họ của người chồng cũ", bg="mh_hat", rows=[("HỌ CỦA", "NGƯỜI CHỒNG CŨ", "họ")]))
c("Bà bỏ ông", "^", K(("BỎ ÔNG · GIỮ TÊN ÔNG", "giữ"), ("NHƯ MỘT DANH XƯNG QUÝ TỘC", "danh", "acc"), ("RỒI ĐỔI SANG TÊN KHÁC", "đổi"), bg="paris_cheret"))
c("Mata Hari.", "^", S("MATA HARI", "Mata", bg="mh_prof"))
c("Nghĩa là mặt trời", "^", K(("MẶT TRỜI", "mặt"), ("MẮT CỦA NGÀY", "mắt", "acc"), bg="dei_bromo"))
c("Ta nên dừng một chút", "^", S("NGHE NHƯ MỘT LỜI TUYÊN BỐ", "tuyên", bg="pc3"))
c("Nó không nói bà", "^", SP("CÁI TÊN NÓI GÌ?", ("mh_hat", "KHÔNG NÓI BÀ LÀ AI", ZL(0, 0.2)), ("pc5", "NÓI BÀ MUỐN ĐƯỢC NHÌN NHƯ THẾ NÀO", ZL(0, 0.8))))
c("Theo nhiều tiểu sử", "^", K(("THEO NHIỀU TIỂU SỬ", "Theo"), ("NGƯỜI ĐẾN TỪ PHƯƠNG ĐÔNG", "phương", "acc"), ("HỒ SƠ KỂ CHUYỆN KHÁC", "Hồ"), bg="gui_shiva"))
c("Bà lớn lên", "^", ph("lw_old", "LEEUWARDEN NGÀY NAY"))
c("Cũng nên nói", "^", F("BẢO TÀNG GUIMET", "ÉMILE\nGUIMET", "Nhà công nghiệp · người lập bảo tàng", img="gui_emile", rows=[("LẬP RA", "BẢO TÀNG GUIMET", "Bảo")]))
c("Nó được dựng", "^", ph("gui_rdc", "BẢO TÀNG GUIMET NGÀY NAY"))
c("Với công chúng", "^", S("XA LẠ · HẤP DẪN", "hấp", bg="gui_brahma"))
c("Bà hiểu điều đó", "^", S("BÀ BIẾT CÁCH DÙNG NÓ", "dùng", bg="pc2"))
c("Ta cần nói rõ một điều", "^", K(("CÁCH TA KỂ CHUYỆN NÀY", "cách"), ("NGHỀ DIỄN · MỘT SỰ THẬT NGHỀ NGHIỆP", "thật", "acc"), bg="paris_mist"))
c("Một người phụ nữ làm", "^", K(("MỘT NGHỀ", "nghề"), ("MỘT THỜI ĐIỂM", "điểm"), ("MỘT CÔNG CHÚNG", "chúng", "acc"), bg="paris_mr"))
c("Và không cần thêm", "^", S("KHÔNG CẦN THÊM GÌ", "thêm", bg="pc6"))
c("Thẩm phán quân sự", "^", F("THẨM PHÁN QUÂN SỰ", "PIERRE\nBOUCHARDON", "Chứng minh phần lớn thân thế ấy là bịa", bg="paris_rain", rows=[("VỤ ÁN", "CHI TIẾT QUAN TRỌNG", "quan")]))
c("Vì khi bà bị bắt", "^", K(("MỖI LỜI NÓI DỐI NHỎ", "mỗi"), ("LÀ BẰNG CHỨNG CỦA", "chứng"), ("MỘT LỜI NÓI DỐI LỚN", "lớn", "acc"), bg="mh_arrest"))
c("Ngày 13 tháng 3", "^", Dt("RA MẮT CÔNG CHÚNG PARIS", "13.03.1905", "gui_2013"))
c("Địa điểm là", "^", ph("mh_guimet", "MATA HARI MÚA Ở GUIMET · 1905", move="pan"))
c("Đó là một tiết mục", "^", K(("MỘT TIẾT MỤC MÚA PHƯƠNG ĐÔNG", "múa"), ("DO BÀ TỰ DỰNG", "tự", "acc"), ("NGƯỜI BIỂU DIỄN · 28 TUỔI", "biểu"), bg="mh_guimet2"))
c("Bối cảnh là Paris", "^", ph("paris_fuller", "LOIE FULLER · 1902 · VŨ NỮ CÙNG THỜI"))
c("Chỉ sau vài buổi", "^", K(("CHỈ SAU VÀI BUỔI", "buổi"), ("TÊN MATA HARI CÓ CHỖ ĐỨNG", "chỗ", "acc"), ("NHƯNG CÓ MẶT TRÁI", "trái"), bg="pc4"))
c("Nó là một vai", "^", K(("MỘT CÁI TÊN LÀ MỘT VAI", "vai"), ("ĐÂU LÀ NGƯỜI, ĐÂU LÀ VAI?", ZL(2, 0.2), "acc"), bg="pc8"))
CH["ch04"] = c.done({"k": "CHƯƠNG 04", "t": "CÁI TÊN"}, B(c, "mystery"))


# ================================================================ CH05
c = Ch("ch05")
c.first(Dt("BIỂU DIỄN Ở NHIỀU THÀNH PHỐ CHÂU ÂU · SAU NĂM", "1905", "pc7"))
c("Bà có mặt trên", "^", K(("SÂN KHẤU", "sân"), ("TIỆC RIÊNG", "tiệc"), ("SĨ QUAN VÀ QUAN CHỨC", "sĩ", "acc"), bg="pc9"))
c("Ta không có danh sách", "^", S("KHÔNG ĐỌC TÊN AI", "đọc", bg="paris_tl"))
c("Có một chi tiết", "^", F("TIỂU SỬ TIẾNG ANH", "THÁI TỬ\nWILHELM", "Một chi tiết trong các tiểu sử", bg="europe1911", rows=[("TRƯỚC CHIẾN TRANH", "BIỂU DIỄN VÀI LẦN", "vài")]))
c("Nhưng chúng cũng nói", "^", K(("MỐI LIÊN HỆ RẤT ÍT", "ít"), ("SẼ BỊ DÙNG NHƯ MỘT MẮT XÍCH", "mắt", "acc"), ("CỦA VỤ ÁN", "vụ"), bg="mh_19"))
c("Tháng 7 năm 1914", "^", Dt("CHIẾN TRANH BÙNG NỔ · HÀ LAN GIỮ TRUNG LẬP", "07.1914", "paris_mr2"))
c("Điều đó có nghĩa", "^", K(("HỘ CHIẾU HÀ LAN", "hộ"), ("ĐI QUA CÁC BIÊN GIỚI", "biên"), ("NGƯỜI PHÁP · NGƯỜI ĐỨC KHÔNG ĐI ĐƯỢC", "Đức", "acc"), bg="mh_pass"))
c("Buổi diễn cuối cùng", "^", Dt("BUỔI DIỄN CUỐI CÙNG", "13.03.1915", "mh_milan"))
c("Sân khấu châu Âu", "^", S("SÂN KHẤU KHÔNG CÒN NHƯ TRƯỚC", "trước", bg="paris_fol"))
c("Giữa Pháp và Hà Lan", "^", M("europe", [("Paris", "PARIS", "Pháp"), ("Amsterdam", "HÀ LAN", "Hà"), ("Madrid", "TÂY BAN NHA", "Tây"), ("London", "ANH", "Anh")]))
c("Với các cơ quan", "^", Q("VỚI PHẢN GIÁN, ĐÓ LÀ MỘT DẤU HỎI?", "empires1914"))
c("Ở các nước tham chiến", "^", K(("THƯ TỪ BỊ KIỂM DUYỆT", "thư"), ("NGƯỜI LẠ BỊ ĐỂ Ý", "lạ", "acc"), bg="morse"))
c("Một người nước ngoài", "^", K(("NGƯỜI NƯỚC NGOÀI ĐI LẠI NHIỀU", "nước"), ("QUEN NHIỀU SĨ QUAN", "quen"), ("SỐNG BẰNG NGHỀ BIỂU DIỄN", "nghề"), ("MỘT DÒNG TRONG SỔ THEO DÕI", "dòng", "acc"), bg="carte_fr"))
c("Chuyện đó không cần", "^", S("MỘT CUỘC SỐNG KHÓ GIẢI THÍCH", "giải", bg="pc1"))
c("Trong thời gian này", "^", F("KHOẢN TIỀN THỨ HAI", "20.000\nFRANC", "Bà nhận trong thời gian này", bg="paris_tl", rows=[("NGUỒN TIỀN", "NHÀ NGOẠI GIAO ĐỨC", "ngoại")]))
c("Cuộc thẩm vấn", "^", S("TIỀN CÔNG GIÁN ĐIỆP", "công", bg="vin_gate"))
c("Bà nói đó là", "^", S("BỒI THƯỜNG ĐỒ ĐẠC BỊ TỊCH THU", "thường", bg="mh_hat"))
c("Một tài liệu tiếng Pháp", "^", F("TÀI LIỆU TIẾNG PHÁP", "MỘT CÂU\nCỦA BÀ", "Về khoản tiền ấy", bg="scrap", rows=[("NÓI VỀ", "NHỮNG NGƯỜI ĐÀN ÔNG ĐÃ GIÚP BÀ", "đàn")]))
Bq(c, "Là giá của những ân huệ tôi đã dành cho họ.", "LỜI GÁN CHO BÀ · THEO TÀI LIỆU TIẾNG PHÁP", "Là giá của", "^", bg="pc10")
c("Một cách đọc của người buộc", "^", SP("HAI CÁCH ĐỌC", ("vin_gate", "NGƯỜI BUỘC TỘI", ZL(0, 0.2)), ("mh_hat", "NGƯỜI BỊ BUỘC TỘI", ZL(0, 0.8))))
c("Và không có tờ giấy", "^", S("KHÔNG TỜ GIẤY NÀO PHÂN XỬ", "phân", bg="scrap"))
c("Một triệu franc, người ta", "^", L("HAI CON SỐ CẠNH NHAU", [("NGƯỜI TA NÓI ĐÃ HỨA", "MỘT TRIỆU FRANC · CHƯA BAO GIỜ TRẢ", "triệu"), ("CÓ THẬT · ĐÃ NẰM TRONG TAY BÀ", "20.000 FRANC", ZL(0, 0.95))]))
c("Con số hứa lớn", "^", BR("LỜI HỨA SO VỚI TIỀN NHẬN", "FRANC", [("TIỀN NHẬN", 20000, ZL(0, 0.2)), ("LỜI HỨA", 1000000, ZL(0, 0.8))]))
c("Nhưng nó đáng để ý", "^", K(("ĐÁNG ĐỂ Ý", "ý"), ("NGƯỜI BỊ COI LÀ GIÁN ĐIỆP GIÁ CAO", "coi", "acc"), ("CON SỐ THỨ HAI", "thứ"), bg="morse"))
c("Nó có thật", "^", S("CHƯA NÓI BÀ ĐÃ LÀM GÌ", "làm", bg="mh_19"))
CH["ch05"] = c.done({"k": "CHƯƠNG 05", "t": "NGHỀ DIỄN VÀ HỘ CHIẾU HÀ LAN"}, B(c, "quiet"))


# ================================================================ CH06
c = Ch("ch06")
c.first(Dt("MẶT TRẬN PHÍA BẮC NƯỚC PHÁP", "04.1916", "vin_zeiller"))
c("một đại úy", "đại", VC("h12", ("MỘT ĐẠI ÚY NGƯỜI NGA", "đại"), ("VADIM MASLOV", "Vadim", "acc")))
c("Ông mất thị lực", "^", F("ĐẠI ÚY NGƯỜI NGA", "VADIM\nMASLOV", "Bị thương, mất thị lực mắt trái", bg="carte_fr", rows=[("QUAN HỆ", "NGƯỜI YÊU CỦA BÀ", "yêu")]))
c("Bà xin vào thăm", "^", K(("XIN VÀO THĂM ÔNG", "thăm"), ("Ở BỆNH VIỆN GẦN MẶT TRẬN", "bệnh", "acc"), ("ÔNG TRẺ HƠN BÀ RẤT NHIỀU", "trẻ"), bg="pc8"))
c("Các tiểu sử mô tả", "^", S("MỐI GẮN BÓ SÂU NHẤT", "sâu", bg="mh_19"))
c("Ta sẽ gặp lại", "^", K(("SẼ GẶP LẠI ÔNG Ở PHIÊN TÒA", "gặp"), ("LẦN ẤY ÔNG KHÔNG ĐỨNG VỀ PHÍA BÀ", "đứng", "acc"), bg="paris_mr"))
c("Muốn vào vùng", "^", K(("MUỐN VÀO VÙNG QUÂN SỰ", "quân"), ("CẦN GIẤY PHÉP", "giấy"), ("NẰM TRONG TAY PHẢN GIÁN PHÁP", "phản", "acc"), bg="morse"))
c("Người liên hệ", "^", PR("ladoux", "NGƯỜI LIÊN HỆ", "ĐẠI ÚY\nGEORGES LADOUX", [("Phản gián Pháp", "Georges"), ("Đại úy", "Ladoux")], caption="LADOUX VÀ MARTHE RICHARD · KHOẢNG 1932"))
c("ngày 2 tháng", "ngày", Dt("LADOUX GẶP BÀ · THEO TÀI LIỆU TIẾNG PHÁP", "02.09.1916", "paris_expo"))
c("Theo các tài liệu tiếng Anh", "^", K(("THEO TÀI LIỆU TIẾNG ANH", "Anh"), ("LÀM QUEN VỚI THÁI TỬ ĐỨC", "quen", "acc"), ("ĐỂ THU TIN QUÂN SỰ", "thu"), ("MỘT KHOẢN THÙ LAO", "thù"), bg="empires1914"))
c("Một triệu franc.", "^", C(1000000, " FRANC", "THÙ LAO ĐƯỢC NÊU · KHÔNG BAO GIỜ TRẢ", None, "pc5"))
c("Đó là phòng hai", "^", F("DEUXIÈME BUREAU", "PHÒNG HAI\nBỘ THAM MƯU", "Cơ quan tình báo của Pháp", bg="carte_fr", rows=[("NHIỆM VỤ", "BIẾT NGƯỜI ĐỨC ĐANG LÀM GÌ", "biết")]))
c("Họ không cần một điệp viên", "^", K(("KHÔNG CẦN MỘT ĐIỆP VIÊN GIỎI", "giỏi"), ("CẦN MỘT NGƯỜI ĐI LẠI ĐƯỢC", "đi"), ("VÀ CHỊU NGHE LỜI", "nghe", "acc"), bg="vin_gate"))
c("Tài liệu tiếng Pháp ghi", "^", SP("AI NÊU CON SỐ?", ("ladoux", "TÀI LIỆU TIẾNG ANH: CƠ QUAN NÊU", ZL(0, 0.2)), ("mh_hat", "TÀI LIỆU TIẾNG PHÁP: BÀ ĐÒI", ZL(0, 0.8))))
c("Số tiền ấy", "^", S("KHÔNG BAO GIỜ ĐƯỢC TRẢ", "trả", bg="paris_rain", sub="Câu hỏi về động cơ"))
c("Vì sao bà nhận lời", "^", K(("VÌ SAO BÀ NHẬN LỜI?", "nhận"), ("KHI BÀ KHÔNG CÓ NGHỀ ẤY", "nghề", "acc"), bg="gui_lib"))
c("Hồ sơ và các tiểu sử", "^", K(("HAI ĐIỀU ĐI CÙNG NHAU", "hai"), ("BÀ YÊU MỘT NGƯỜI BỊ THƯƠNG", "yêu"), ("VÀ BÀ CẦN TIỀN", "cần", "acc"), bg="pc2"))
c("Đó không phải lời", "^", S("CÁC NGUỒN TỰ NỐI HAI VIỆC LẠI", "nối", bg="vin_gate"))
c("Một người phụ nữ gần", "^", K(("GẦN BỐN MƯƠI TUỔI", "gần"), ("HẾT THỜI", "hết"), ("CÓ NGƯỜI CẦN ĐƯỢC CHĂM SÓC", "chăm"), ("DỄ NHẬN LỜI ĐỀ NGHỊ CÓ TIỀN", "nhận", "acc"), bg="mh_arrest"))
c("Đại úy Ladoux, về sau", "^", S("LADOUX VỀ SAU BUỘC TỘI BÀ", "buộc", bg="ladoux"))
c("Người đã đề nghị", "^", S("BÊN KIA CỦA VỤ ÁN", "bên", bg="paris_mr"))
c("Câu hỏi về động cơ, vậy", "^", K(("CÂU HỎI VỀ ĐỘNG CƠ ĐÓNG Ở ĐÂY", "đóng"), ("KHÔNG THẤY MỘT LÝ TƯỞNG", "tưởng", "acc"), bg="gui_lib"))
c("tình yêu", "tình", L("ĐỘNG CƠ · THEO CÁC NGUỒN", [("MỘT", "TÌNH YÊU", "tình"), ("HAI", "TIỀN", "tiền")]))
c("Một triệu franc là một", "^", S("KHÔNG QUY ĐỔI RA TIỀN NGÀY NAY", "quy", bg="paris_mr2"))
c("Tỷ giá thời chiến", "^", K(("TỶ GIÁ THỜI CHIẾN DAO ĐỘNG", "dao"), ("PHÉP QUY ĐỔI DỄ GÂY HIỂU LẦM", "hiểu"), ("LỚN HƠN NHIỀU LẦN MỌI KHOẢN KHÁC", "lớn", "acc"), bg="paris_tl"))
c("Và vì chưa bao giờ", "^", S("CHỈ TỒN TẠI NHƯ MỘT LỜI HỨA", "hứa", bg="pc3"))
CH["ch06"] = c.done({"k": "CHƯƠNG 06", "t": "MỘT TRIỆU FRANC"}, B(c, "mystery"))


# ================================================================ CH07
c = Ch("ch07")
c.first(Dt("TÀU ZEELANDIA · TỪ TÂY BAN NHA", "11.1916", "paris_rain"))
c("Tàu ghé cảng", "^", M("europe", [("Falmouth", "FALMOUTH · BỊ BẮT", "Falmouth"), ("London", "LONDON", ZL(0, 0.9))]))
c("Ta nên để ý", "^", K(("THỨ TỰ", "thứ"), ("NƯỚC ANH TRƯỚC", "Anh", "acc"), ("RỒI MỚI ĐẾN PHÁP", "Pháp"), ("HỎI CUNG MỘT LẦN", "cung"), bg="empires1914"))
c("Người thẩm vấn bà", "^", F("NGƯỜI THẨM VẤN", "BASIL\nTHOMSON", "Scotland Yard", bg="carte_fr", rows=[("GIỮ BÀ Ở", "ĐỒN CANON ROW", "Canon")]))
c("Sau đó bà được thả", "^", K(("ĐƯỢC THẢ", "thả"), ("Ở LẠI KHÁCH SẠN SAVOY", "Savoy"), ("THOMSON VIẾT: BÀ THỪA NHẬN", "thừa", "acc"), ("LÀM VIỆC CHO PHẢN GIÁN PHÁP", "phản"), bg="paris_mr"))
c("Các tài liệu tiếng Anh", "^", S("KHÔNG AI BIẾT CHẮC", "chắc", bg="mh_19", sub="Bà nói thật, hay nói điều người nghe muốn nghe?"))
c("Hồ sơ của MI5", "^", F("MI5 · LƯU TRỮ QUỐC GIA ANH", "HỒ SƠ KV 2", "Người Anh theo dõi bà", bg="carte_fr"))
c("Nhưng họ không đưa ra", "^", S("KHÔNG CÓ BẰNG CHỨNG DỨT KHOÁT", "dứt", bg="mh_arrest"))
c("Cuối năm 1916", "^", M("europe", [("Madrid", "MADRID · KALLE", "Madrid")], zoom="Madrid", zk=2.0))
c("Bà hỏi về cách", "^", K(("HỎI VỀ CÁCH GẶP THÁI TỬ", "hỏi"), ("CÓ VẺ ĐỀ NGHỊ BÁN TIN CỦA PHÁP", "bán", "acc"), ("ĐỂ LẤY TIỀN", "lấy"), bg="paris_expo"))
c("Tháng 12 năm 1916", "^", Dt("MỘT VIỆC KHÁC", "12.1916", "morse"))
c("Cơ quan phản gián Pháp để", "^", S("TÊN SÁU ĐIỆP VIÊN BỈ", "sáu", bg="carte_fr"))
c("Đức bắt và xử tử", "^", K(("ĐỨC BẮT VÀ XỬ TỬ MỘT NGƯỜI", "xử"), ("CƠ QUAN XEM ĐÂY LÀ BẰNG CHỨNG", "bằng"), ("BÀ ĐÃ CHUYỂN TÊN CHO ĐỨC", "chuyển", "acc"), bg="pc4"))
c("Nhưng ta nên dừng", "^", O([("a", "CƠ QUAN PHẢN GIÁN PHÁP", "TỰ SẮP ĐẶT CHUỖI NÀY", None, "top", ZL(0, 0.2)), ("b", "GIAO MỘT THÔNG TIN", "", "a", None, ZL(0, 0.8)), ("c", "CHỜ XEM CÓ ĐẾN ĐÍCH KHÔNG", "", "b", None, "chờ")], bg="empires1914"))
c("Rồi họ dùng kết quả", "^", S("CHỨNG MINH ĐIỀU ĐÃ TIN TỪ TRƯỚC", "chứng", bg="pc2"))
c("Một phép thử", "^", K(("PHÉP THỬ CHỈ CÓ GIÁ TRỊ KHI KHÔNG CÒN ĐƯỜNG NÀO KHÁC", "phép"), ("HỒ SƠ KHÔNG LOẠI TRỪ ĐƯỜNG KHÁC", "loại", "acc"), bg="morse"))
c("Tây Ban Nha giữ", "^", K(("TÂY BAN NHA TRUNG LẬP", "Tây"), ("MADRID: NGƯỜI CỦA CẢ HAI PHÍA", "Madrid", "acc"), bg="paris_mr2"))
c("Một người đến đó", "^", SP("ĐẾN MADRID", ("pc3", "KHÔNG NHẤT THIẾT LÀ GIÁN ĐIỆP", ZL(0, 0.2)), ("pc6", "NHƯNG GIÁN ĐIỆP THÌ RẤT CÓ THỂ ĐẾN ĐÓ", ZL(0, 0.8))))
c("Ta cũng nên nhìn", "^", T([("ANH", "FALMOUTH · BẮT, HỎI CUNG, THẢ", ZL(0, 0.3)), ("PHÁP", "PARIS · BẮT VÀI TUẦN SAU", ZL(0, 0.9))], bg="empires1914"))
c("Cùng một người phụ nữ", "^", K(("CÙNG MỘT NGƯỜI PHỤ NỮ", "Cùng"), ("HAI CƠ QUAN", "cơ"), ("HAI KẾT LUẬN", "kết", "acc"), bg="pc7"))
c("Nhưng nó cho thấy", "^", S("BẰNG CHỨNG CHƯA BAO GIỜ THỐNG NHẤT", "thống", bg="mh_19"))
CH["ch07"] = c.done({"k": "CHƯƠNG 07", "t": "FALMOUTH VÀ MADRID"}, B(c, "tense"))


# ================================================================ CH08
c = Ch("ch08")
c.first(Dt("KALLE GỬI ĐIỆN VỀ BERLIN", "01.1917", "morse"))
c("Trong đó nói về", "^", O([("h", "ĐIỆP VIÊN MÃ H-21", "", None, "top", ZL(0, 0.2)), ("b", "TIỂU SỬ KHỚP VỚI BÀ", "GẦN NHƯ HOÀN TOÀN", "h", None, ZL(0, 0.8))], bg="carte_fr"))
c("Pháp bắt được", "^", K(("PHÁP BẮT ĐƯỢC CÁC ĐIỆN", "bắt"), ("MỘT CHI TIẾT NỔI BẬT", "nổi"), ("MẬT MÃ PHÁP ĐÃ GIẢI TỪ TRƯỚC", "giải", "acc"), bg="empires1914"))
c("Một người làm nghề", "^", Q("VÌ SAO NGƯỜI ĐỨC DÙNG MỘT MÃ MÀ PHÁP ĐỌC ĐƯỢC?", "carte_fr"))
c("Một số tài liệu", "^", K(("MỘT KHẢ NĂNG", "khả"), ("ĐIỆN CỐ Ý GỬI ĐỂ PHÁP BẮT", "cố"), ("NẾU ĐÚNG · MỘT CÁI BẪY", "bẫy", "acc"), bg="pc2"))
c("Hồ sơ không cho biết ai", "^", S("HỒ SƠ KHÔNG CHO BIẾT AI ĐẶT BẪY", "đặt", bg="paris_rain"))
c("Một dòng chữ mã hóa", "^", M("europe", [("Madrid", "MADRID", ZL(0, 0.3)), ("Berlin", "BERLIN", ZL(0, 0.9))]))
c("Nó nêu một mã", "^", F("BỨC ĐIỆN", "MÃ H-21", "Một mã và một tiểu sử", bg="morse", rows=[("NGƯỜI ĐỌC", "GHÉP TIỂU SỬ ẤY VỚI BÀ", "ghép")]))
c("Nhưng ghép được", "^", S("GHÉP ĐƯỢC KHÔNG CÓ NGHĨA LÀ BÀ ĐÃ LÀM", "ghép", bg="pc10"))
c("Điều hồ sơ cho biết", "^", K(("CÁC ĐIỆN ẤY TỒN TẠI", "tồn"), ("XƯƠNG SỐNG CỦA CÁO TRẠNG", "xương", "acc"), bg="vin_gate"))
c("Giờ ta quay lại", "^", Q("BÀ CÓ CHUYỂN ĐƯỢC TIN NÀO CÓ GIÁ TRỊ KHÔNG?", "mh_19"))
c("Sử gia Wesley Wark", "^", F("SỬ GIA", "WESLEY\nWARK", "Bà chưa bao giờ là một điệp viên quan trọng", bg="gui_lib"))
c("Sử gia Julie", "^", F("SỬ GIA", "JULIE\nWHEELWRIGHT", "Điều bà chuyển đi, ai cũng đọc được trên báo Tây Ban Nha", bg="paris_mr2"))
c("Năm 2001", "^", Dt("MỘT QUỸ CỦA HÀ LAN YÊU CẦU PHÁP XEM LẠI", "2001", "lw_jus"))
c("Quỹ ấy nói bà", "^", K(("NHIỀU LẮM · ĐIỆP VIÊN CẤP THẤP", "cấp"), ("KHÔNG ĐỂ LỘ BÍ MẬT NÀO", "lộ", "acc"), bg="lw_stad"))
c("Họ cũng nói thêm", "^", S("CÓ THỂ KHÔNG HOÀN TOÀN VÔ CAN", "vô", bg="lw_stad", sub="Một nhận định thận trọng"))
c("Nhà nghiên cứu Pat", "^", F("NHÀ NGHIÊN CỨU", "PAT\nSHIPMAN", "Bằng chứng cho thấy bà hoàn toàn vô tội về tội gián điệp", bg="gui_rdc"))
c("Ta ghi lại cả hai", "^", SP("HAI NHẬN ĐỊNH", ("lw_jus", "QUỸ HÀ LAN: CẤP THẤP, CÓ THỂ KHÔNG VÔ CAN", ZL(0, 0.2)), ("gui_lib", "SHIPMAN: HOÀN TOÀN VÔ TỘI VỀ GIÁN ĐIỆP", ZL(0, 0.8))))
c("Câu hỏi ấy, vì vậy", "^", S("ĐÓNG THEO KIỂU CỦA SỬ HỌC", "sử", bg="gui_lib"))
c("Không có tài liệu nào", "^", S("KHÔNG CÓ BÍ MẬT QUÂN SỰ CÓ GIÁ TRỊ", "mật", bg="mh_19"))
c("Và không có gì cho thấy", "^", C(50000, " LÍNH", "CHƯA TỪNG CÓ NGUỒN KIỂM ĐẾM", None, "vin_chap"))
c("Nó là một cáo buộc", "^", S("MỘT CÁO BUỘC · KHÔNG PHẢI SỐ THỐNG KÊ", "thống", bg="vin_gate"))
c("Một thông tin có giá trị", "^", L("BA THỨ ĐỂ GỌI LÀ GIÁN ĐIỆP", [("1", "MỘT THÔNG TIN CÓ GIÁ TRỊ", ZL(0, 0.1)), ("2", "MỘT ĐƯỜNG TRUYỀN ĐẾN NƯỚC ĐỐI ĐỊCH", ZL(0, 0.9)), ("3", "MỘT THIỆT HẠI GẮN VỚI THÔNG TIN ẤY", ZL(2, 0.0))]))
c("Trong hồ sơ của bà", "^", L("TRONG HỒ SƠ CỦA BÀ", [("THẤY", "CÁC KHOẢN TIỀN", ZL(0, 0.3)), ("THẤY", "CÁC CUỘC GẶP", ZL(0, 0.9)), ("CHƯA THẤY RÕ", "BA THỨ KIA", "kia")]))
c("Đó là khoảng trống", "^", S("KHOẢNG TRỐNG GIỮA NGHI NGỜ VÀ BẰNG CHỨNG", "khoảng", bg="mh_19"))
CH["ch08"] = c.done({"k": "CHƯƠNG 08", "t": "BỨC ĐIỆN H-21"}, B(c, "mystery"))


# ================================================================ CH09
c = Ch("ch09")
c.first(Dt("BÀ BỊ BẮT TRONG PHÒNG KHÁCH SẠN", "13.02.1917", "mh_arrest"))
c("Đó là khách sạn", "^", F("KHÁCH SẠN", "ELYSÉE\nPALACE", "Đại lộ Champs-Élysées · Paris", bg="paris_expo", rows=[("NGƯỜI BẮT BÀ", "ĐẠI ÚY BOUCHARDON · THEO MỘT TÀI LIỆU", "úy")]))
c("Bà bị thẩm vấn", "^", K(("THẨM VẤN Ở SAINT-LAZARE", "thẩm"), ("CHỜ XÉT XỬ SUỐT NHIỀU THÁNG", "chờ", "acc"), bg="paris_mr2"))
c("Bouchardon là người", "^", F("PIERRE BOUCHARDON", "NGƯỜI THẨM\nVẤN CHÍNH", "Về sau cũng là người buộc tội bà", bg="paris_cheret", rows=[("XÁC LẬP", "NHIỀU ĐIỀU BÀ KỂ VỀ THÂN THẾ LÀ BỊA", "xác")]))
c("Và ông lập luận", "^", K(("LẬP LUẬN: KHÔNG TRUNG THỰC", "lập"), ("LÀ BẰNG CHỨNG CỦA TỘI", "chứng", "acc"), ("TA CỘNG LẠI NHỮNG GÌ ÔNG CÓ", "cộng"), bg="gui_lib"))
c("Một khoản 20.000", "^", L("BỐN THỨ TRONG TAY ÔNG · PHẦN MỘT", [("MỘT", "20.000 FRANC TỪ MỘT NHÀ NGOẠI GIAO ĐỨC", ZL(0, 0.2)), ("HAI", "CÁC ĐIỆN VỀ H-21, GỬI TỪ MADRID", ZL(0, 0.9))]))
c("Một việc lộ tên", "^", L("BỐN THỨ TRONG TAY ÔNG · PHẦN HAI", [("BA", "LỘ TÊN SÁU ĐIỆP VIÊN BỈ · DO PHÁP SẮP ĐẶT", ZL(0, 0.2)), ("BỐN", "MỘT TIỂU SỬ ĐẦY NHỮNG CHỖ BỊA", ZL(0, 0.9))]))
c("Bốn thứ ấy", "^", Q("ĐỦ ĐỂ NGHI. NHƯNG ĐỦ ĐỂ KẾT ÁN?", "vin_gate"))
c("Đây là một logic", "^", S("MỘT LOGIC CÓ THỂ HIỂU ĐƯỢC", "hiểu", bg="mh_hat"))
c("Nhưng nó cũng là", "^", S("NHƯNG KHÔNG ĐỦ", "đủ", bg="pc4"))
c("Một vũ nữ vốn", "^", K(("MỘT VŨ NỮ", "vũ"), ("SỐNG BẰNG HÌNH ẢNH DỰNG SẴN", "dựng", "acc"), ("BÀ LUÔN NÓI KHÔNG LÀM GIÁN ĐIỆP", "luôn"), bg="paris_mist"))
c("Bà viết rằng", "^", K(("BÀ VIẾT: KHÔNG HỀ LÀM ĐIỀU ẤY", "hề"), ("NHẬN CÓ NHẬN TIỀN", "tiền"), ("NHẬN CÓ TIẾP XÚC VỚI NGƯỜI ĐỨC", "xúc", "acc"), bg="pc6"))
c("Nhưng bà nói chúng", "^", K(("NHƯNG BÀ NÓI: ĐỜI TƯ", "tư"), ("VÀ CHUYỆN LÀM ĂN", "làm"), ("VẪN LÀ NGƯỜI NỔI TIẾNG", "nổi", "acc"), bg="mh_19"))
c("Một vụ gián điệp, trong", "^", K(("MỘT TIN CÓ SỨC HÚT LỚN", "sức"), ("BÁO CHÍ VIẾT NHIỀU VỀ BÀ", "Báo", "acc"), bg="paris_cine"))
c("Và phần lớn họ", "^", S("NƠI GIAI THOẠI BẮT ĐẦU LỚN LÊN", "giai", bg="paris_tl"))
c("Một nhân vật quyến rũ", "^", K(("MỘT NHÂN VẬT QUYẾN RŨ", "quyến"), ("MỘT NỮ ĐIỆP VIÊN NGUY HIỂM", "nguy"), ("DỄ VIẾT HƠN MỘT BẢN KÊ CÁC KHOẢN TIỀN", "bản"), ("VÀ BÁN CHẠY HƠN", "chạy", "acc"), bg="pc9"))
CH["ch09"] = c.done({"k": "CHƯƠNG 09", "t": "KHÁCH SẠN ELYSÉE PALACE"}, B(c, "mystery"))


# ================================================================ CH10
c = Ch("ch10")
c.first(Dt("PHIÊN TÒA BẮT ĐẦU", "24.07.1917", "paris_mr2"))
c("Theo tài liệu tiếng Pháp", "^", F("NƠI XỬ · PARIS", "HỘI ĐỒNG\nCHIẾN TRANH\nTHỨ BA", "Theo tài liệu tiếng Pháp, phiên kéo dài ba ngày", bg="paris_expo"))
c("Đây là một tòa án", "^", L("MỘT TÒA ÁN QUÂN SỰ", [("TÒA", "HỘI ĐỒNG CHIẾN TRANH", ZL(0, 0.3)), ("CÔNG TỐ", "ÔNG MORNET", ZL(0, 0.9)), ("BÀO CHỮA", "ÉDOUARD CLUNET", "Clunet")]))
c("Có một điều quan trọng", "^", S("BỊ TỪ CHỐI QUYỀN CHẤT VẤN", "chất", bg="paris_cheret"))
c("Ông cũng không được hỏi", "^", K(("CŨNG KHÔNG ĐƯỢC HỎI TRỰC TIẾP", "hỏi"), ("NHÂN CHỨNG CỦA CHÍNH MÌNH", "chính", "acc"), bg="pc7"))
c("Cáo buộc là bà làm", "^", K(("CÁO BUỘC: GIÁN ĐIỆP CHO ĐỨC", "điệp"), ("VÀ GÂY RA CÁI CHẾT CỦA ÍT NHẤT 50.000 BINH SĨ", "chết", "acc"), bg="vin_chap"))
c("Các tài liệu nói rõ", "^", F("CÁC TÀI LIỆU NÓI RÕ", "KHÔNG CÓ\nBẰNG CHỨNG", "Cơ quan Pháp hay Anh nào cũng không đưa ra được bằng chứng dứt khoát", bg="paris_tl"))
c("Có một chi tiết nữa", "^", S("MASLOV TỪ CHỐI RA LÀM CHỨNG", "chối", bg="pc3"))
c("Theo một số tài liệu", "^", K(("KHI BIẾT ÔNG BỎ RƠI BÀ", "bỏ"), ("BÀ NGẤT ĐI", "ngất", "acc"), ("MỘT CÂU ĐƯỢC GÁN CHO BÀ", "gán"), bg="mh_hat"))
c("Nó được chép", "^", sc("quote", text="Gái điếm thì có, nhưng kẻ phản bội thì không bao giờ.", by="LỜI GÁN CHO BÀ · CHÉP BẰNG TIẾNG ANH", lbl="TRÍCH DỊCH", qline=18, typeAt=18, bg="pc10"))
c("Ta không có bản ghi", "^", S("KHÔNG CÓ BẢN GHI NGUYÊN VĂN", "nguyên", bg="scrap"))
c("Vì vậy ta nói rõ", "^", K(("LỜI ĐƯỢC GHI LẠI", "được"), ("KHÔNG PHẢI MỘT DÒNG BIÊN BẢN", "dòng", "acc"), bg="gui_lib"))
c("Phiên tòa kết thúc", "^", K(("KẾT THÚC BẰNG MỘT BẢN ÁN", "án"), ("BIÊN BẢN NẰM TRONG HỒ SƠ BỊ NIÊM PHONG", "niêm", "acc"), bg="vin_gate"))
c("Phải đến năm 2017", "^", Dt("QUÂN ĐỘI PHÁP MỞ HỒ SƠ", "2017", "vin_pav"))
c("Nghĩa là suốt một thế kỷ", "^", K(("SUỐT MỘT THẾ KỶ · CHỈ CÓ LỜI KỂ", "kể"), ("BÁO CHÍ KỂ", "Báo"), ("HỒI KÝ KỂ", "Hồi"), ("VÀ ĐIỆN ẢNH KỂ", "điện", "acc"), bg="paris_cine"))
c("Tử hình", "^", S("TỬ HÌNH", "Tử", bg="vin_water"))
c("Ở đó, người ta xét", "^", K(("XÉT MỘT VỤ VÌ QUÂN ĐỘI", "quân"), ("KHÔNG VÌ DƯ LUẬN", "dư"), ("NHƯNG DƯ LUẬN VẪN CÓ MẶT", "vẫn", "acc"), bg="vin_keep"))
c("Một cái tên nổi tiếng", "^", S("SỰ CHÚ Ý CẦN MỘT KẾT QUẢ", "kết", bg="paris_fol"))
c("Trong một phiên tòa kín", "^", S("GẦN NHƯ KHÔNG CÓ CHỖ ĐỂ TỰ BẢO VỆ", "chỗ", bg="mh_19"))
c("Và sau mùa xuân", "^", K(("SAU MÙA XUÂN ẤY", "mùa"), ("MỘT NƯỚC KHÔNG BÌNH THƯỜNG", "bình", "acc"), bg="empires1914"))
c("Quyền chất vấn nhân chứng", "^", K(("QUYỀN CHẤT VẤN LÀ NỀN CỦA MỘT PHIÊN TÒA", "nền"), ("CÓ NÓ: THỬ ĐƯỢC BẰNG CHỨNG", "thử", "acc"), bg="pc4"))
c("Không có nó", "^", S("CHỊU NỔI SỰ KIỂM TRA HAY KHÔNG?", "chịu", bg="morse"))
c("Đó là lý do", "^", S("NẶNG HƠN VẺ NGOÀI CỦA NÓ", "nặng", bg="paris_mr"))
CH["ch10"] = c.done({"k": "CHƯƠNG 10", "t": "PHIÊN TÒA"}, B(c, "tense"))


# ================================================================ CH11
c = Ch("ch11")
c.first(K(("ĐỂ HIỂU BẢN ÁN", "hiểu"), ("TA PHẢI NHÌN QUANH NÓ", "nhìn"), ("PHIÊN TÒA · THÁNG 7 NĂM 1917", "tháng", "acc"), bg="paris_rain"))
c("Trước đó ba tháng", "^", S("MỘT MÙA XUÂN RẤT NẶNG", "nặng", bg="empires1914"))
c("Ngày 16 tháng 4", "^", Dt("QUÂN PHÁP MỞ CUỘC TẤN CÔNG LỚN Ở SÔNG AISNE", "16.04.1917", "carte_fr"))
c("Mục tiêu là dãy đồi", "^", M("europe", [("Chemin des Dames", "CHEMIN DES DAMES", "Chemin")], zoom="Chemin des Dames", zk=2.0))
c("Nó bị đình lại", "^", Dt("CHIẾN DỊCH BỊ ĐÌNH LẠI · TỔN THẤT RẤT LỚN", "09.05.1917", "paris_mr2"))
c("Một ước tính ghi 118.000", "^", BR("TỔN THẤT CỦA PHÁP · MỘT SỐ ƯỚC TÍNH", "NGƯỜI", [("MƯỜI NGÀY ĐẦU · MỘT ƯỚC TÍNH", 118000, ZL(0, 0.3)), ("MƯỜI NGÀY ĐẦU · ƯỚC TÍNH KHÁC", 134000, ZL(0, 0.9))]))
c("Tổng cộng cho cả", "^", C(187000, " NGƯỜI", "CẢ CHIẾN DỊCH · CON SỐ THƯỜNG ĐƯỢC DẪN", None, "empires1914"))
c("Ngày 3 tháng 5", "^", T([("03.05", "MỘT SƯ ĐOÀN PHÁP TỪ CHỐI TẤN CÔNG", ZL(0, 0.2)), ("05.1917", "21 SƯ ĐOÀN XẢY RA NỔI LOẠN", ZL(0, 0.9))], bg="carte_fr"))
c("Ngày 16 tháng 5", "^", Dt("NIVELLE BỊ CÁCH CHỨC · PÉTAIN LÊN THAY", "16.05.1917", "paris_mr"))
c("Khi phiên tòa mở", "^", K(("PHIÊN TÒA MỞ · CHUYỆN ẤY MỚI VỪA QUA", "mới"), ("KHÔNG VĂN BẢN NÀO NÓI", "văn"), ("TÒA XỬ BÀ ĐỂ CHUYỂN HƯỚNG CƠN GIẬN", "chuyển", "acc"), bg="paris_expo"))
c("Điều ấy không được viết", "^", S("ĐIỀU ẤY KHÔNG ĐƯỢC VIẾT RA Ở ĐÂU CẢ", "viết", bg="gui_lib"))
c("Ta dễ bị cuốn", "^", K(("MỘT CUỘC NỔI LOẠN", "nổi"), ("MỘT THẤT BẠI", "thất"), ("MỘT PHIÊN TÒA", "phiên", "acc"), ("TRÔNG NHƯ MỘT MẠCH", "trông"), bg="paris_tl"))
c("Nhưng một mạch như thế", "^", K(("MỘT MẠCH PHẢI ĐƯỢC CHỨNG MINH BẰNG TÀI LIỆU", "chứng"), ("KHÔNG PHẢI BẰNG CẢM GIÁC", "cảm", "acc"), bg="morse"))
c("Nhưng một số sử gia", "^", K(("MỘT SỐ SỬ GIA ĐỌC RA NHƯ THẾ", "gia"), ("WESLEY WARK: VẬT TẾ THẦN", "Wesley"), ("CHO THẤT BẠI CỦA QUÂN ĐỘI PHÁP", "thất", "acc"), bg="pc7"))
c("Đó là một nhận định", "^", S("ĐÓ LÀ MỘT NHẬN ĐỊNH · TA GỌI NÓ LÀ NHẬN ĐỊNH", "gọi", bg="gui_rdc"))
c("Ta cũng cần thẳng thắn", "^", K(("CÁO BUỘC 50.000 LÍNH", "buộc"), ("KHÔNG NÓI HỌ CHẾT Ở CHEMIN DES DAMES", "chết", "acc"), bg="vin_zeiller"))
c("Ta không có chứng cứ", "^", S("KHÔNG CÓ CHỨNG CỨ NỐI VỚI CHIẾN DỊCH MÙA XUÂN", "nối", bg="paris_cine"))
c("Các nhà sử học ghi rằng", "^", K(("THEO CÁC NHÀ SỬ HỌC", "sử"), ("NĂM 1917 · MỘT CON SỐ KỶ LỤC", "kỷ"), ("LÍNH PHÁP ĐÀO NGŨ", "đào", "acc"), bg="empires1914"))
c("Con số ấy là", "^", C(27000, " NGƯỜI", "LÍNH PHÁP ĐÀO NGŨ NĂM 1917 · KỶ LỤC", None, "carte_fr"))
c("Ta chỉ thấy", "^", K(("MỘT SỰ TRÙNG KHỚP VỀ THỜI GIAN", "trùng"), ("VÀ MỘT NƯỚC ĐANG CẦN MỘT LỜI GIẢI THÍCH", "giải", "acc"), bg="paris_mist"))
c("Câu hỏi về phiên tòa", "^", L("ĐÓNG ĐƯỢC MỘT NỬA", [("CÂU HỎI VỀ PHIÊN TÒA", "CHỈ ĐÓNG ĐƯỢC MỘT NỬA", ZL(0, 0.2)), ("HỒ SƠ CHO THẤY", "QUYỀN BÀO CHỮA BỊ HẠN CHẾ", ZL(0, 0.9))]))
c("Hồ sơ cho thấy một cáo buộc", "^", S("CÁO BUỘC KHÔNG CÓ CHỨNG CỨ DỨT KHOÁT", "dứt", bg="pc8"))
c("Còn vì sao nó kết thúc", "^", K(("VÌ SAO KẾT THÚC BẰNG ÁN TỬ HÌNH", "tử"), ("LÀ PHẦN SỬ GIA PHẢI SUY RA", "suy", "acc"), bg="vin_water"))
c("Ta cũng nên nói rõ", "^", K(("PHẦN KHÓ NHẤT", "khó"), ("CHỨNG MINH MỘT Ý ĐỒ", "chứng"), ("CẦN LỜI CỦA NGƯỜI RA QUYẾT ĐỊNH", "quyết", "acc"), bg="vin_pav"))
c("Một bức thư", "^", L("NHỮNG THỨ TA KHÔNG CÓ", [("MỘT", "BỨC THƯ", "thư"), ("HAI", "BIÊN BẢN HỌP", ZL(0, 0.95)), ("BA", "MỆNH LỆNH", "lệnh"), ("CHỈ CÓ", "MỘT CHUỖI SỰ KIỆN VÀ NHỮNG CÁCH ĐỌC", "chuỗi")]))
CH["ch11"] = c.done({"k": "CHƯƠNG 11", "t": "MÙA XUÂN NĂM 1917"}, B(c, "mystery"))


# ================================================================ CH12
c = Ch("ch12")
c.first(F("ÁN TỬ HÌNH", "ĐƠN XIN\nÂN XÁ", "Bà bị kết án tử hình · theo một tài liệu, đơn xin ân xá bị bác", bg="paris_mr2", rows=[("TỔNG THỐNG", "RAYMOND POINCARÉ · BÁC ĐƠN", "Poincaré")]))
c("Rạng sáng ngày 15", "^", Dt("RẠNG SÁNG", "15.10.1917", "vin_moat"))
c("tại hào nước", "tại", ph("vin_flag", "LÂU ĐÀI VINCENNES · ẢNH NGÀY NAY", move="pan"))
c("Từ ngày bà bị bắt", "^", BR("TỪ NGÀY BỊ BẮT VÀ TỪ PHIÊN TÒA ĐẾN NGÀY CUỐI", "NGÀY", [("TỪ NGÀY BỊ BẮT · HƠN TÁM THÁNG", 244, ZL(0, 0.2)), ("TỪ PHIÊN TÒA · GẦN BA THÁNG", 83, ZL(0, 0.9))], bg="vin_pav"))
c("Đó là khoảng thời gian", "^", S("THỜI GIAN ĐỂ CÂN NHẮC · HOẶC KHÔNG", "khoảng", bg="vin_side"))
c("Phần còn lại là", "^", K(("PHẦN CÒN LẠI LÀ NHỮNG GÌ XẢY RA SAU", "sau"), ("KHÔNG CÓ THÂN NHÂN NÀO ĐẾN NHẬN", "nhận"), ("DÙNG CHO NGHIÊN CỨU Y HỌC", "nghiên", "acc"), bg="gui_lib"))
c("Hồ sơ năm 1918", "^", F("HỒ SƠ NĂM 1918", "BẢO TÀNG\nGIẢI PHẪU", "Paris", rows=[("PHẦN CÒN LẠI", "ĐƯỢC CHUYỂN ĐẾN", "chuyển")]))
c("Đến năm 2000", "^", Dt("BẢO TÀNG KHÔNG CÒN TÌM THẤY", "2000", "paris_rain"))
c("Người ta kể về ngày", "^", K(("NGƯỜI TA KỂ RẤT NHIỀU", "kể"), ("PHẦN LỚN TỪ MỘT NHÀ BÁO", "nhà"), ("VÀ VÀI NGƯỜI KHÁC TRONG HỒI KÝ", "hồi", "acc"), bg="paris_cine"))
c("Những chuyện ấy", "^", S("CHỈ ĐÁNG GIỮ NHƯ GIAI THOẠI", "giai", bg="scrap"))
c("Có một câu nữa", "^", F("DO BIZARD CHÉP LẠI", "MỘT CÂU\nGÁN CHO BÀ", "Ngay trước giờ ấy", bg="pc9"))
Bq(c, "Thật là một tập quán lạ của người Pháp, bắn người ta lúc rạng sáng.", "BIZARD CHÉP LẠI · KHÔNG KIỂM CHỨNG ĐƯỢC", "Thật là", "^", bg="vin_zeiller")
c("Ta giữ nó như", "^", S("MỘT LỜI KỂ · KHÔNG HƠN", "hơn", bg="pc2"))
c("Bà nói mình không", "^", K(("BÀ NÓI MÌNH KHÔNG LÀM GIÁN ĐIỆP", "điệp"), ("VÀ KHÔNG ĐỔI LỜI", "đổi"), ("BÀ CHẾT KHI VẪN BỊ MỘT CON SỐ ĐEO THEO", "đeo", "acc"), bg="mh_hat"))
c("50.000 binh sĩ", "^", C(50000, " BINH SĨ", "CON SỐ KHÔNG CÓ NGƯỜI KIỂM ĐẾM", None, "mh_19"))
c("Nhưng nó là con số", "^", S("CON SỐ LÀM NÊN TÊN TUỔI BÀ SUỐT MỘT THẾ KỶ", "tuổi", bg="mh_prof"))
CH["ch12"] = c.done({"k": "CHƯƠNG 12", "t": "TỪ CHỐI ÂN XÁ"}, B(c, "quiet"))


# ================================================================ CH13
c = Ch("ch13")
c.first(Dt("YÊU CẦU XEM LẠI VỤ ÁN", "2001", "lw_jus"))
c("Có tài liệu cho biết", "^", S("YÊU CẦU ẤY BỊ BÁC", "bác", bg="gui_lib"))
c("Năm 2003", "^", F("NĂM 2003", "PHILIPPE\nCOLLAS", "Xuất bản tiểu sử đầy đủ đầu tiên về bà", bg="gui_emile"))
c("Năm 2017, một trăm năm", "^", T([("1876", "SINH Ở LEEUWARDEN", ZL(0, 0.2)), ("1917", "NGÀY CUỐI · VINCENNES", ZL(0, 0.8)), ("2017", "QUÂN ĐỘI PHÁP MỞ HỒ SƠ", "quân")]))
c("Tổng cộng 1.275", "^", C(1275, " TRANG", "TỔNG CỘNG", None, "vin_pav"))
c("Ở quê nhà", "^", ph("lw_fries2", "FRIES MUSEUM · LEEUWARDEN"))
c("Cuộc triển lãm", "^", Dt("TRIỂN LÃM LỚN NHẤT VỀ BÀ KHAI MẠC", "14.10.2017", "lw_fries"))
c("Đó là một ngày", "^", S("MỘT NGÀY TRƯỚC NGÀY GIỖ MỘT TRĂM NĂM", "giỗ", bg="mh_stat2"))
c("Giờ ta quay lại", "^", L("BỐN CON SỐ · LƯỢT ĐẦU", [("MỘT TRIỆU FRANC", "CHƯA BAO GIỜ TRẢ", ZL(0, 0.3)), ("20.000 FRANC", "CÓ THẬT · HAI CÁCH ĐỌC", ZL(0, 0.9))]))
c("50.000 người lính", "^", L("BỐN CON SỐ · LƯỢT SAU", [("50.000 NGƯỜI LÍNH", "KHÔNG CÓ NGUỒN KIỂM ĐẾM", ZL(0, 0.3)), ("12 NGƯỜI", "TRONG HÀNG SÚNG", ZL(0, 0.9))]))
c("Câu hỏi mà một thế kỷ", "^", Q("BÀ LÀ MỘT ĐIỆP VIÊN VỤNG VỀ…", "mh_hat"))
c("Hay chỉ là một người", "^", Q("…HAY CHỈ LÀ NGƯỜI PHỤ NỮ NHẬN TIỀN TỪ NHIỀU PHÍA?", "mh_milan"))
c("Hồ sơ không viết sẵn", "^", K(("HỒ SƠ KHÔNG VIẾT SẴN CÂU TRẢ LỜI", "viết"), ("KHÔNG KẾT LUẬN BÀ VÔ TỘI", "vô"), ("CŨNG KHÔNG KẾT LUẬN BÀ CÓ TỘI", "Cũng", "acc"), bg="pc5"))
c("Bà nhận tiền từ một", "^", L("NHỮNG ĐIỀU CÓ THỂ NÓI", [("MỘT", "BÀ NHẬN TIỀN TỪ MỘT NHÀ NGOẠI GIAO ĐỨC", ZL(0, 0.2)), ("HAI", "BÀ NHẬN LỜI VỚI CƠ QUAN PHÁP", ZL(0, 0.9)), ("BA", "BÀ DỰNG MỘT THÂN THẾ BỊA", "dựng")]))
c("Còn điều mà cáo trạng", "^", K(("ĐIỀU MÀ CÁO TRẠNG BUỘC CHO BÀ", "trạng"), ("CHO ĐẾN NAY CHƯA AI ĐƯA RA ĐƯỢC", "nay"), ("BẰNG CHỨNG DỨT KHOÁT", "dứt", "acc"), bg="vin_pav"))
c("Có lẽ đó là điều", "^", K(("CÓ LẼ ĐÓ LÀ ĐIỀU ĐÁNG GIỮ NHẤT", "giữ"), ("KHÔNG PHẢI MỘT LỜI PHÁN XỬ MỚI", "phán"), ("MÀ LÀ THÓI QUEN HỎI", "thói"), ("TRƯỚC MỖI CON SỐ, NÓ ĐẾN TỪ ĐÂU", "đâu", "acc"), bg="paris_rain"))
c("Điều ta có thể nói", "^", SP("TÒA ÁN · MỘT CÁI TÊN NỔI TIẾNG", ("vin_gate", "CẦN BẰNG CHỨNG", ZL(0, 0.2)), ("mh_prof", "CẦN MỘT CÂU CHUYỆN", ZL(0, 0.8))))
c("Trong vụ này", "^", S("TRONG VỤ NÀY, CÂU CHUYỆN ĐI TRƯỚC", "trước", bg="pc1"))
c("Mỗi khi gặp một câu chuyện", "^", K(("MỘT NGƯỜI PHỤ NỮ QUYẾN RŨ VÀ NGUY HIỂM", "quyến"), ("HÃY HỎI", "hỏi", "acc"), ("AI VIẾT CÂU CHUYỆN ẤY?", "viết"), ("VÀ HỌ CÓ TÀI LIỆU NÀO?", "tài"), bg="paris_fol"))
c("Trong vụ Mata Hari", "^", T([("BÁO CHÍ", "VIẾT TRONG THỜI CHIẾN", ZL(0, 0.3)), ("TÒA ÁN QUÂN SỰ", "VIẾT TRONG THỜI CHIẾN", ZL(0, 0.9))], bg="empires1914"))
c("Điện ảnh đã làm", "^", SP("ĐIỆN ẢNH TỪ 1931", ("mh_hat", "NGƯỜI THẬT", ZL(0, 0.2)), ("mh_film", "MỘT NHÂN VẬT", ZL(0, 0.8))))
c("Nhân vật ấy hấp dẫn", "^", S("NHÂN VẬT SỐNG LÂU HƠN CÁC BIÊN BẢN", "sống", bg="paris_cine"))
c("Về tin tức", "^", L("BA CÂU HỎI LỚN · TIN TỨC VÀ ĐỘNG CƠ", [("TIN TỨC", "KHÔNG THẤY BÀ CHUYỂN ĐƯỢC GÌ CÓ GIÁ TRỊ", ZL(0, 0.3)), ("ĐỘNG CƠ", "NỐI VỚI TÌNH YÊU VÀ TIỀN", ZL(0, 0.9))]))
c("Về phiên tòa", "^", L("BA CÂU HỎI LỚN · PHIÊN TÒA", [("QUYỀN BÀO CHỮA", "BỊ HẠN CHẾ", ZL(0, 0.3)), ("LÝ DO", "CÒN LÀ SUY LUẬN", ZL(0, 0.9))]))
c("Còn bằng chứng", "^", S("BẰNG CHỨNG, MỘT THẾ KỶ SAU, VẪN CÒN THIẾU", "thiếu", bg="mh_hat"))
CH["ch13"] = c.done({"k": "KẾT", "t": "HỒ SƠ MỞ NĂM 2017"}, B(c, "quiet"))


# ==== MAIN
POOLS = {
    "port": ["mh_prof", "mh_arrest", "mh_merk", "mh_guimet", "mh_guimet2", "mh_hat", "mh_pass", "mh_19", "mh_milan",
             "pc1", "pc2", "pc3", "pc4", "pc5", "pc6", "pc7", "pc8", "pc9", "pc10"],
    "paris": ["paris_expo", "paris_cheret", "paris_mr", "paris_fol", "paris_fuller", "paris_cine", "paris_tl", "paris_renoir", "paris_mist",
              "paris_mr2", "paris_rain", "jatte", "terrace"],
    "doc": ["carte_fr", "empires1914", "europe1911", "morse", "scrap", "gui_lib", "lw_map"],
    "vin": ["vin_donjon", "vin_water", "vin_north", "vin_flag", "vin_moat", "vin_keep", "vin_pav", "vin_chap", "vin_gate", "vin_entr",
            "vin_keep2", "vin_side", "vin_zeiller", "vin_miller", "vin_lake"],
    "lw": ["lw_old", "lw_waag", "lw_stad", "lw_voor", "lw_fries", "lw_fries2", "lw_nieuw", "lw_jus", "lw_stat"],
    "dei": ["dei_batavia", "dei_deli", "dei_gg", "dei_resid", "dei_castle", "dei_map", "dei_art", "dei_road", "dei_road2", "dei_java",
            "dei_knil", "dei_tea", "dei_couple", "dei_garden", "dei_bromo", "dei_dance", "dei_hospital", "dei_bank"],
    "gui": ["gui_rdc", "gui_lib", "gui_2013", "gui_emile", "gui_shiva", "gui_brahma"],
}
POOLOF = {}
for _n, _p in POOLS.items():
    for _k in _p:
        POOLOF.setdefault(_k, _p)
LIMIT = 4
PHOTO_LABEL = [("vin_water", "TRANH VINCENNES"), ("vin_zeiller", "TRANH KHẮC VINCENNES"), ("vin_miller", "TRANH KHẮC VINCENNES"),
               ("vin_", "VINCENNES · NGÀY NAY"), ("lw_map", "BẢN ĐỒ LEEUWARDEN · 1664"), ("lw_", "LEEUWARDEN · NGÀY NAY"),
               ("dei_bromo", "JAVA · NGÀY NAY"), ("dei_dance", "JAVA · NGÀY NAY"), ("dei_java", "JAVA · NGÀY NAY"),
               ("dei_", "ĐÔNG ẤN HÀ LAN · TƯ LIỆU"), ("gui_", "BẢO TÀNG GUIMET"), ("paris_", "PARIS THỜI BELLE ÉPOQUE · TƯ LIỆU"),
               ("morse", "MÁY ĐIỆN BÁO MORSE"), ("jatte", "TRANH · BELLE ÉPOQUE"), ("terrace", "TRANH · BELLE ÉPOQUE")]


def label_of(k):
    for pre, lab in PHOTO_LABEL:
        if k == pre or (pre.endswith("_") and k.startswith(pre)):
            return lab
    return None


def all_scenes():
    return [(n, i, s) for n in CHAPTERS if n in CH for i, s in enumerate(CH[n]["scenes"])]


def refs_of(s):
    out = []
    walk_used(s, out)
    return out


def to_broll(s, vid):
    if s["type"] == "kinetic":
        kn = s["items"]
    else:  # slam
        kn = [{"text": s["text"], "at": s["hitAt"], "acc": True}]
        if s.get("sub"):
            kn.append({"text": s["sub"], "at": s["hitAt"], "sm": True})
    new = {"type": "broll", "at": s["at"], "vid": V[vid], "tone": "noir", "veil": 0.4, "illus": FILMV, "kin": kn}
    s.clear()
    s.update(new)


def assign_clips():
    """Cần >= 30 cảnh b-roll, mỗi clip <= 5 lần; clip kho chung (h11-h15 noir, h5 mưa, h6 đồng xu cho cảnh tiền)."""
    uses = Counter(s.get("vid") for _, _, s in all_scenes() if s.get("vid"))
    inv = {v: k for k, v in V.items()}
    cnt = Counter({inv[k]: n for k, n in uses.items()})
    order = ["h11", "h12", "h13", "h14", "h15", "h5"]
    plan = {"ch00": 1, "ch01": 2, "ch02": 2, "ch03": 2, "ch04": 2, "ch05": 3, "ch06": 2, "ch07": 2, "ch08": 2, "ch09": 2, "ch10": 3, "ch11": 3, "ch12": 1, "ch13": 1}
    prev, rot = None, 0
    for n in CHAPTERS:
        sc_ = CH[n]["scenes"]
        cands = [j for j, s in enumerate(sc_) if s["type"] in ("kinetic", "slam") and s.get("bg") and 2 <= j <= len(sc_) - 3]
        want = plan[n]
        pick = []
        for q in range(want):
            if not cands:
                break
            j = cands[min(len(cands) - 1, (q * 2 + 1) * len(cands) // (2 * want))]
            pick.append(j)
        for j in sorted(set(pick)):
            s = sc_[j]
            txt = json.dumps(s, ensure_ascii=False).upper()
            money = "TIỀN" in txt and cnt["h6"] < 3
            if money:
                k = "h6"
            else:
                ks = sorted([k for k in order if cnt[k] < 5 and k != prev], key=lambda k: (cnt[k], (order.index(k) - rot) % len(order)))
                k = ks[0] if ks else "h6"
            cnt[k] += 1
            prev = k
            rot += 2
            to_broll(s, k)


def rebalance():
    """Mỗi ảnh <= LIMIT lần: `bg` thừa đổi sang ảnh ít dùng nhất cùng nhóm (không đụng ảnh `img`, ảnh của split/file/print)."""
    img_uses = Counter()
    for _, _, s in all_scenes():
        d = {k: v for k, v in s.items() if k != "bg"}
        for k in refs_of(d):
            img_uses[k] += 1
    kept = Counter()
    repl = []
    for _, _, s in all_scenes():
        k = s.get("bg")
        if not isinstance(k, str):
            continue
        if img_uses[k] + kept[k] < LIMIT:
            kept[k] += 1
        else:
            repl.append(s)
    tot = lambda m: img_uses[m] + kept[m]
    prev = None
    for s in repl:
        pool = POOLOF.get(s["bg"])
        if not pool:
            print(f"  ! ảnh {s['bg']} quá {LIMIT} lần và không có nhóm thay")
            continue
        cands = [m for m in pool if tot(m) < LIMIT and m != s["bg"] and m != prev]
        if not cands:   # nhóm hết ảnh: lấy ảnh ít dùng nhất ở nhóm khác (nền chữ đã phủ tối, không gắn nghĩa)
            allk = [m for nm in ("paris", "vin", "lw", "dei", "gui", "port", "doc") for m in POOLS[nm]]
            cands = [m for m in allk if tot(m) < LIMIT and m != s["bg"] and m != prev and m not in ("vin_zeiller", "vin_miller", "lw_map")]
            pool = allk
        if not cands:
            print(f"  ! hết ảnh thay cho {s['bg']}")
            continue
        m = min(cands, key=lambda m: (tot(m), pool.index(m)))
        kept[m] += 1
        s["bg"] = m
        prev = m


def to_photo():
    """Một phần cảnh kinetic nền ảnh ngang -> ảnh tư liệu chuyển động (Ken Burns) + chữ kin: tăng nhóm A."""
    img_n = Counter()
    for _, _, s in all_scenes():
        for k in refs_of({a: b for a, b in s.items() if a != "bg"}):
            img_n[k] += 1
    moves = ["in", "pan", "out"]
    q = 0
    for n in CHAPTERS:
        ks = [s for s in CH[n]["scenes"] if s["type"] == "kinetic" and isinstance(s.get("bg"), str)]
        for t, s in enumerate(ks):
            k = s["bg"]
            if t % 2:
                continue
            if k in DIMS:
                if DIMS[k][0] < DIMS[k][1] * 1.25:
                    continue
            elif k not in ("paris_rain", "jatte"):
                continue
            if img_n[k] >= 3:
                continue
            img_n[k] += 1
            new = {"type": "photo", "img": k, "tone": "color", "move": moves[q % 3], "veil": 0.52, "kin": s["items"]}
            if "at" in s:
                new["at"] = s["at"]
            lab = label_of(k)
            if lab:
                new["illus"] = lab
            q += 1
            s.clear()
            s.update(new)


def strip_file_bg():
    """Thẻ hồ sơ (file) và số đếm (counter) không ảnh nền: nhóm D (đồ họa chuyển động) ~20% thời lượng; giữ nền cho mỗi thẻ hồ sơ thứ sáu và 3 số đếm."""
    t = c_ = 0
    for _, _, s in all_scenes():
        if s["type"] == "file" and s.get("bg") and not s.get("img"):
            if t % 6 != 5:
                del s["bg"]
            t += 1
        elif s["type"] == "counter" and s.get("bg"):
            if c_ % 3 != 1:
                del s["bg"]
            c_ += 1


def group_seconds():
    g = Counter()
    for n in CHAPTERS:
        for s, d in zip(CH[n]["scenes"], DURS[n]):
            if s.get("vid"):
                g["broll"] += d
            elif refs_of(s):
                g["A"] += d
            else:
                g["D"] += d
    return g


def attach_ai():
    # Chỉ thay nền minh họa, giữ nguyên mốc, chỉ vẽ ảnh tư liệu nhân vật.
    images = {
        "ch01": [(13, "ai02")], "ch03": [(5, "ai03")],
        "ch04": [(13, "ai04")], "ch05": [(8, "ai05"), (13, "ai06")],
        "ch06": [(11, "ai07"), (3, "ai08")], "ch08": [(4, "ai09")],
        "ch09": [(0, "ai10")], "ch10": [(3, "ai11")],
        "ch11": [(0, "ai12"), (19, "ai13")], "ch12": [(4, "ai14")],
        "ch13": [(12, "ai15"), (17, "ai16")],
    }
    for chapter, entries in images.items():
        for index, key in entries:
            scene = CH[chapter]["scenes"][index]
            scene["bg"] = key
            scene["credit"] = False
            scene["illus"] = TD
            if key == "ai03":
                text, hit = scene["text"], scene["hitAt"]
                at = scene["at"]
                scene.clear()
                scene.update(type="photo", img=key, at=at, tone="color", move="in", veil=0.52,
                             credit=False, illus=TD, kin=[{"text": text, "at": hit, "acc": True}])
    clips = {
        "ch00": [(1, "900001"), (10, "900006")],
        "ch02": [(4, "900006")], "ch03": [(4, "900002"), (6, "900002")],
        "ch05": [(12, "900003")], "ch06": [(6, "900004")],
        "ch07": [(5, "900006")], "ch08": [(18, "900006")],
        "ch10": [(12, "900005"), (18, "900005")],
        "ch11": [(11, "900006"), (15, "900005"), (21, "900005")],
    }
    for chapter, entries in clips.items():
        for index, vid in entries:
            CH[chapter]["scenes"][index]["vid"] = vid


if __name__ == "__main__":
    run_all()
    assign_clips()
    rebalance()
    to_photo()
    strip_file_bg()
    attach_ai()
    g = group_seconds()
    tot = sum(g.values())
    print("nhóm (ước): " + ", ".join(f"{k} {100 * v / tot:.0f}%" for k, v in g.items()))
    used = []
    walk_used(CH, used)
    cnt = Counter(used)
    # ghi công ảnh CC BY / BY-SA
    cred = []
    for k in sorted(cnt):
        if k in DIMS:
            r = next(x for x in _RES if x["file"] == IMGS[k])
            lic = r.get("license", "")
            if lic and not lic.lower().startswith(("public", "cc0", "pd")):
                cred.append(f"{r['file'].removeprefix('File:')} — Wikimedia Commons — {lic} — {r.get('url', '').split('?')[0]}")
    SPEC["youtube"]["video_credits"] = sorted(set(cred))
    (D / "spec.json").write_text(json.dumps(SPEC, ensure_ascii=False, indent=1), encoding="utf-8")
    ai_keys = {k: v for k, v in IMGS.items() if k.startswith("ai") and k[2:].isdigit()}
    write(__file__, CH, {k: v for k, v in IMGS.items() if k in cnt or k in ai_keys}, GEO, endcardBg="mh_hat")
    tot = sum(v[0] for v in STATS.values()); chg = sum(v[1] for v in STATS.values())
    print(f"TỔNG: ước {tot / 60:.1f} phút, {chg} lần đổi hình, {tot / max(chg, 1):.2f}s/lần")
    img_only = Counter()
    for _, _, s in all_scenes():
        if isinstance(s.get("img"), str):
            img_only[s["img"]] += 1
    for k, n in cnt.items():
        if n > LIMIT or img_only[k] > 3:
            print(f"  ! ảnh {k}: tổng {n} lần, img {img_only[k]}")
