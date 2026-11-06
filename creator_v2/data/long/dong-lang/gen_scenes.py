"""Cảnh biên tập Đông Lăng Đạo Mộ 1928 (CL). Khung: data/long/hoa-than/gen_scenes.py.

Mốc `at` không gõ chỉ số câu: B("đoạn chữ trong câu", "từ neo", cảnh) tự tìm câu chứa đoạn chữ (từ câu hiện tại trở đi),
chọn từ neo duy nhất trong câu (engine so khớp nguyên từ, cadence.py so khớp chuỗi con) rồi kiểm mốc tăng dần.
Mốc con trong cảnh (hàng ledger, mục kinetic…) viết Z("từ"): tìm từ đó từ mốc cảnh trở đi.
"""
import json, sys, re, unicodedata, importlib.util
from pathlib import Path
D = Path(__file__).resolve().parent
ROOT = D.parents[2]
sys.path.insert(0, str(ROOT / "motion" / "long"))
from scenekit import sc, kin, write, FILMV

_RES = json.loads((ROOT / "output/long/dong-lang/research.json").read_text(encoding="utf-8"))["images"]
def im(i, must):
    f = _RES[i]["file"]
    if must not in f:
        raise ValueError(f"Ảnh {i} không khớp: {f}")
    return f

# (chỉ số research.json, chuỗi phải có trong tên file)
_R = {
 "sun": (0, "Sun Dianying"), "sun2": (133, "Sun Dianying"), "zaize": (12, "Zaize"), "puyi": (13, "Puyi, Manchukuo"),
 "puyi_tj": (84, "Zhang Garden"), "puyi_tj2": (85, "Tianjin"), "puyi_jing": (99, "Jing Garden"), "puyi_bed": (83, "bedroom"),
 "puyi_boy": (98, "Titular"), "puyi_x": (90, "Xuantong"), "puyi_p": (101, "溥仪"),
 "cixi1": (4, "Ci-Xi"), "cixi2": (28, "Cixi1"), "cixi3": (29, "On Throne 7"), "cixi4": (30, "Throne 2"), "cixi5": (31, "9.2"),
 "cixi6": (34, "Empress Dowager portrait"), "cixi7": (38, "孝钦"), "cixi8": (41, "Hair 2"), "cixi_fun": (17, "Funeral1908"), "cixi_fun2": (50, "葬礼"),
 "ql1": (51, "Horseback"), "ql2": (52, "Qianlong11"), "ql3": (70, "Young Man"), "ql4": (71, "乾隆皇帝朝服像轴"), "ql5": (72, "清人画弘历"),
 "ql6": (73, "Forbidden City, Peking"), "ql7": (56, "Qianlong and the Empress"), "ql8": (57, "Tombs of his Ancestors"), "ql9": (59, "hunting"),
 "ql10": (60, "hunting trip"), "ql_fu": (76, "Fu, Lu"),
 "dl1": (192, "Chiang Kai-shek and Dai Li.jpg"), "dl2": (193, "Dai Li6"), "dl3": (194, "U.S.navy"), "dl4": (195, "戴笠将军照片"),
 "dl5": (196, "杜月笙"), "dl6": (200, "戴笠军装照"), "dl7": (198, "遇難前"),
 "tv1": (205, "Tse-ven Soong"), "tv2": (206, "Sun Liren"), "tv3": (207, "1940 TV Soong"), "tv4": (208, "Xining"), "tv5": (209, "minister-president van China.jpg"),
 "tv6": (210, "Zhang Xueliang"), "tv7": (211, "900-8980.jpg"), "tv8": (214, "TV SOONG"),
 "yan1": (215, "Yan Xishan.jpg"), "yan2": (216, "1947"), "yan3": (219, "TIME"), "yan4": (220, "Yan Xishan0"), "yan5": (221, "Yan Xishan11"),
 "yan6": (222, "Yan Xishan2"), "yan7": (224, "Yan Xishan 4"), "yan8": (225, "Yan Xishan 1.jpg"),
 "he1": (229, "He Yingqin1"), "he2": (236, "cinematographer"), "he3": (238, "He Yingqin4"), "he4": (239, "Long Yun"),
 "cks1": (242, "Chiang Kai-shek（"), "cks2": (243, "Soong May-ling2"), "cks3": (244, "Feng Yuxiang2"), "cks4": (246, "Yan Xishan.jpg"),
 "cks5": (248, "Kaifeng 1928"), "cks6": (249, "Sun Yat-Sen"), "cks7": (252, "1928 AP"), "cks8": (253, "1928-05-30"), "cks9": (254, "horseback"),
 "cks10": (255, "Pacific"), "cks11": (245, "Feng Yuxiang3"), "cks12": (247, "Jieshi"), "cks13": (241, "Cairo"),
 "mei": (256, "May Ling"), "feng": (245, "Feng Yuxiang3"),
 "zzc": (106, "Zhang Zongchang5"), "zzl": (110, "Zhang Zuolin"), "bei": (102, "Beiyang"), "bei2": (130, "Gong An"), "ft17": (107, "FT-17"),
 "swords": (111, "swords"), "train": (113, "Armored"), "repub": (115, "republic forever"), "gold": (116, "Gold Units"), "nanjing": (121, "Nanking"),
 "m1925": (127, "1925-1926"), "m1927": (128, "1927-1928"), "m1929": (129, "1929-1930"), "m1921": (125, "1921-1922"), "mwar": (105, "coalitions"),
 "mnat": (104, "1929 - 1937"), "mciv": (117, "civil war"), "m1914": (114, "1914 map"), "wl25": (112, "Warlords 1925"),
 "dl_old": (1, "Tung-ling"), "dl_map": (2, "Layout"), "dl_air": (3, "Yuling in Eastern"), "dl_tower": (7, "Själstornet"), "dl_hall": (9, "隆恩殿"),
 "yl_door": (10, "裕陵地宫"), "yl_cut": (20, "月牙城"), "yl_ruin": (22, "Yuling4"), "yl_dmg": (16, "Looting Damage"), "yl_stone": (18, "Yuling2"),
 "yl_wall": (27, "清裕陵"), "yl_ming": (75, "明楼"), "yl_w": (188, "Yuling（West）"), "yl_c": (189, "Concubine"), "dd1": (19, "DingDongLing1"),
 "dd2": (137, "Tombs of Cixi"), "dd3": (142, "Ding Dongling 3"), "dd4": (143, "Ding Dongling 1"), "dd5": (144, "Ding Dongling 2"),
 "dd6": (145, "Ding Dongling 4"), "dd7": (146, "Putuo Yu Ding Dongling.jpg"), "dd8": (147, "Ding Dongling 9"), "dd9": (148, "Ding Dongling 8"),
 "dd10": (149, "Ding Dongling 7"), "dd11": (150, "Ding Dongling 6"), "dd12": (151, "Ding Dongling 5"),
 "eq1": (140, "DSC 2110"), "eq2": (141, "DSC 2099"), "eq3": (172, "Eastern Qing Tombs.jpg"), "eq4": (173, "Tombs 15"), "eq5": (174, "Tombs 08"),
 "eq6": (175, "Protection"), "eq7": (178, "2113"), "eq8": (179, "2130"), "eq9": (180, "2106"), "eq10": (181, "2102"), "eq11": (182, "2103"),
 "eq12": (183, "Ding Consort"), "eq13": (184, "Villages"), "eq14": (185, "Ding Tomb in Dong"), "eq15": (186, "Jing Tomb"), "eq16": (187, "Ding Tomb(east)"),
 "eq17": (190, "Dabeilou"), "eq18": (191, "Yu1"),
 "buddha": (5, "Amitayus"), "pearls": (6, "Muttugalu"), "guanyin": (8, "Guanyin"), "fluorite": (21, "Fluorit"), "garb1": (25, "Burial Garments NCSM"),
 "garb2": (26, "Garments 2"), "crown": (43, "Headdress"), "audience": (35, "Official Audience"), "puppet": (40, "游艺"),
 "bell_heart_sutra": "EXT:artic:89655", "melon_jade_pot": "EXT:artic:18438", "qianlong_buddhist_vase": "EXT:artic:25640",
 "qianlong_dragon_dish": "EXT:artic:41882", "qianlong_dragon_plaque": "EXT:artic:88234", "qianlong_dragon_vase": "EXT:artic:58180",
 "qianlong_lacquer_bowl": "EXT:artic:134", "qianlong_moon_flask": "EXT:artic:58053", "qing_brushpot_paradise": "EXT:artic:26882",
 "qing_jade_cup": "EXT:artic:2716", "qing_musical_chime": "EXT:artic:107912",
}
IMGS, DIMS = {}, {}
for _k, _v in _R.items():
    if isinstance(_v, str):
        IMGS[_k] = _v
    else:
        IMGS[_k] = im(*_v)
        DIMS[_k] = (_RES[_v[0]]["w"], _RES[_v[0]]["h"])
PERSON = {k for k in _R if re.match(r"(sun|zaize|puyi|cixi[0-9]|ql[0-9]|dl[0-9]|tv|yan|he[0-9]|cks|mei|feng|zz)", k)}

V = {"n11": "198011", "n12": "198012", "n13": "198013", "n14": "198014", "n15": "198015",
     "h1": "198101", "h3": "198103", "h5": "198105", "h7": "198107", "h8": "198108"}
GEO = json.loads((ROOT / "data/long/bao-thanh-thien/spec.json").read_text(encoding="utf-8"))["geo"]
GEO = {"china": dict(GEO["china"], bbox=[100.0, 22.0, 126.0, 44.0], pins=[
    {"name": "Tuân Hóa", "lon": 117.96, "lat": 40.19, "label": "TUÂN HÓA · ĐÔNG LĂNG"},
    {"name": "Bắc Kinh", "lon": 116.4, "lat": 39.9, "label": "BẮC KINH"},
    {"name": "Thiên Tân", "lon": 117.2, "lat": 39.13, "label": "THIÊN TÂN"},
    {"name": "Nam Kinh", "lon": 118.8, "lat": 32.06, "label": "NAM KINH"},
    {"name": "Vĩnh Thành", "lon": 116.43, "lat": 33.93, "label": "VĨNH THÀNH · HÀ NAM"},
    {"name": "Thang Âm", "lon": 114.36, "lat": 35.92, "label": "THANG ÂM"},
    {"name": "Thái Nguyên", "lon": 112.55, "lat": 37.87, "label": "THÁI NGUYÊN"},
    {"name": "Thanh Đảo", "lon": 120.38, "lat": 36.07, "label": "THANH ĐẢO"},
    {"name": "Đài Bắc", "lon": 121.56, "lat": 25.04, "label": "ĐÀI BẮC"},
    {"name": "Hà Nam", "lon": 113.6, "lat": 34.0, "label": "HÀ NAM"}])}

TD = "TÁI DỰNG MINH HỌA"
LK = "THEO LỜI KỂ"
_LKV = [LK, "THEO CÁC BẢN KỂ", "LỜI KỂ VỀ SAU", "CHƯA CÓ TÀI LIỆU ĐƯƠNG THỜI", "CHỈ LÀ LỜI KỂ"]
_LKN = [0]


def LKX():
    """Nhãn lời kể đổi chữ để không lặp > 2 lần (long_gate)."""
    _LKN[0] += 1
    return _LKV[_LKN[0] % len(_LKV)]


# ---------------------------------------------------------------- mốc
def norm(w):
    return re.sub(r"[^\w]", "", unicodedata.normalize("NFC", w.lower()))


class Z:
    def __init__(self, w):
        self.w = w


def _text(x):
    return x if isinstance(x, str) else x["t"]


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
            cands = []
            if w:
                cands = [k for k, x in enumerate(self.toks[i]) if norm(x) == norm(w)][:1]
            else:
                cands = list(range(k0, min(len(self.toks[i]), k0 + max(1, len(sub.split())))))
            for k in cands:
                if (i, k) > self.cur and self._ok(i, k):
                    self.cur = (i, k)
                    return [i, self._tok(i, k)]
            if (i, 0) > self.cur or True:
                continue
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

    def tm(self, pos):
        """Ước giờ bắt đầu (giây) của mốc (câu, từ): 0,30 s/âm tiết + nghỉ."""
        i, k = pos
        t = sum(len(self.toks[j]) * 0.30 + self.pz[j] for j in range(max(i, 0)))
        if k > 0:
            t += k * 0.30
        return t

    def done(self, hud, bgm):
        end = self.tm((len(self.lines), 0))
        ts = [self.tm(p) for p in self.pos] + [end]
        for n, (a, b) in enumerate(zip(ts, ts[1:])):
            if b - a < 2.55 or b - a > 7.6:
                print(f"  ! {self.name} cảnh {n} ({self.out[n]['type']}) ước {b - a:.1f}s")
        return dict(hud=hud, bgm=bgm, scenes=self.out)


# ---------------------------------------------------------------- dựng cảnh
def ph(img, illus=None, move="in", **k):
    d = dict(img=img, tone="color", move=move, **k)
    if illus:
        d["illus"] = illus
    if "focus" not in d and img in DIMS and DIMS[img][1] > DIMS[img][0] * 1.15:
        d["focus"] = [0.5, 0.2 if img in PERSON else 0.45]
    return sc("photo", **d)


def _kin(items):
    out = []
    for it in items:
        t, w, *r = it
        e = {"text": t, "at": Z(w)}
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


def F(k, name, desc, bg, rows=None, **kw):
    d = dict(k=k, name=name, desc=desc, bg=bg, **kw)
    if rows:
        d["rows"] = [{"k": a, "v": b, "at": Z(c)} for a, b, c in rows]
    return sc("file", **d)


def L(title, rows, bg=None):
    d = dict(title=title, rows=[{"k": a, "v": b, "at": Z(c)} for a, b, c in rows])
    if bg:
        d["bg"] = bg
    return sc("ledger", **d)


def T(items, bg, title=None):
    d = dict(bg=bg, items=[{"year": a, "text": b, "at": Z(c)} for a, b, c in items])
    if title:
        d["title"] = title
    return sc("timeline", **d)


def C(to, suffix, label, w, bg, year=False, frm=0):
    d = {"from": frm, "to": to, "suffix": suffix, "label": label, "countAt": Z(w), "bg": bg}
    if year:
        d["year"] = True
    return sc("counter", **d)


def VC(v, *items, tone="noir", veil=0.4):
    return sc("broll", vid=V[v], tone=tone, veil=veil, illus=FILMV, kin=_kin(items))


def QT(text, by, line_sub, w, lbl="TRÍCH DỊCH"):
    return dict(__qt=(text, by, line_sub, w, lbl))


def SP(title, a, b):
    return sc("split", title=title, a={"img": a[0], "label": a[1], "at": Z(a[2])}, b={"img": b[0], "label": b[1], "at": Z(b[2])})


def O(nodes, bg=None):
    ns = []
    for id_, t, s, p, cls, w in nodes:
        n = {"id": id_, "t": t, "s": s, "at": Z(w)}
        if p:
            n["p"] = p
        if cls:
            n["cls"] = cls
        ns.append(n)
    d = dict(nodes=ns)
    if bg:
        d["bg"] = bg
    return sc("org", **d)


def M(pins, zoom=None, zk=1.5):
    d = dict(geo="china", pins=[{"name": n, "label": lb, "at": Z(w)} for n, lb, w in pins])
    if zoom:
        d.update(zoom=zoom, zoomK=zk)
    return sc("map", **d)


def PR(img, k, h, lines, **kw):
    return sc("print", img=img, tone="color", side={"k": k, "h": h, "hAt": Z(lines[0][1]),
              "lines": [{"text": t, "at": Z(w)} for t, w in lines]}, **kw)


def EV(img, calls, **kw):
    return sc("evidence", img=img, tone="color", maxW=700, maxH=760,
              callouts=[{"x": x, "y": y, "text": t, "side": s, "at": Z(w)} for x, y, t, s, w in calls], **kw)


def BR(title, unit, items, bg):
    return sc("bars", title=title, unit=unit, bg=bg, items=[dict(k=a, v=b, at=Z(c)) for a, b, c in items])


def Bq(c, text, by, sub, w, lbl="TRÍCH DỊCH"):
    """Cảnh quote: qline = câu chứa lời trích."""
    a = c.anchor(sub, w)
    li = a if isinstance(a, int) else a[0]
    s = sc("quote", text=text, by=by, lbl=lbl, qline=li, typeAt=a)
    s["at"] = a
    c.out.append(s)
    c.pos.append(c.cur)


CH = {}
SAY = {"Yoshiko": "Yô-shi-cô", "Kawashima": "Ca-oa-shi-ma"}
CHAPTERS = [f"ch{n:02d}" for n in range(14)]
TITLES = ["TIẾNG MÌN ĐÊM 4/7/1928", "NGHỊCH LÝ ĐÔNG LĂNG", "KẺ VÔ LẠI CỜ BẠC", "TƯỚNG CƯỚP MẶC QUÂN PHỤC", "KẾ HOẠCH TẬP TRẬN",
          "PHÁ CỬA DỤ LĂNG", "QUAN TÀI TỪ HI", "CƠN THỊNH NỘ Ở THIÊN TÂN", "BẢN KÊ BÁU VẬT", "MẠNG LƯỚI MUA ĐƯỜNG",
          "PHIÊN TÒA NAM KINH", "CỬU LONG BẢO KIẾM", "DẠ MINH CHÂU VÀ TỐNG MỸ LINH", "HẦM MỘ TRƠ ĐÁY"]
SOURCES = ["https://en.wikipedia.org/wiki/Sun_Dianying", "https://vi.wikipedia.org/wiki/Tôn_Điện_Anh",
           "https://en.wikipedia.org/wiki/Eastern_Qing_tombs", "https://en.wikipedia.org/wiki/Yuling_(Qing_dynasty)",
           "https://en.wikipedia.org/wiki/Ding_Dongling", "https://en.wikipedia.org/wiki/Empress_Dowager_Cixi",
           "https://en.wikipedia.org/wiki/Puyi", "https://en.wikipedia.org/wiki/Dai_Li",
           "https://en.wikipedia.org/wiki/Soong_Mei-ling", "https://en.wikipedia.org/wiki/T._V._Soong",
           "https://en.wikipedia.org/wiki/He_Yingqin", "https://en.wikipedia.org/wiki/Yan_Xishan",
           "https://en.wikipedia.org/wiki/From_Emperor_to_Citizen", "https://en.wikipedia.org/wiki/Yoshiko_Kawashima"]
SPEC = {
    "title": "ĐÔNG LĂNG ĐẠO MỘ Ngoài Đời Thật: Tôn Điện Anh — Mở Lăng Càn Long, Không Ai Bị Kết Án",
    "channel": "CL", "accent": "#d4b23a", "look": "sulfur", "theme": "shanghai", "autoTr": True, "master": True, "craft": True,
    "endcard": 9, "endcardSub": "HỒ SƠ TIẾP THEO",
    "acc": ["tôn điện anh", "đông lăng", "càn long", "từ hi", "dụ lăng", "định đông lăng", "đới lạp", "tống mỹ linh", "phổ nghi", "hà ứng khâm"],
    "say": SAY, "chapters": CHAPTERS,
    "youtube": {
        "titles": ["ĐÔNG LĂNG ĐẠO MỘ Ngoài Đời Thật: Tôn Điện Anh — Mở Lăng Càn Long, Không Ai Bị Kết Án"],
        "summary": "Hồ sơ vụ nổ mìn mở hai địa cung ở Đông Lăng tháng 7 năm 1928: người chỉ huy Tôn Điện Anh, đơn kiện của hoàng tộc, phiên tòa Nam Kinh dừng lại không có bản án, và những món đồ chỉ còn trong lời kể.",
        "more": [], "sources": SOURCES,
        "tags": ["đông lăng đạo mộ", "đông lăng đạo mộ ngoài đời thật", "tôn điện anh", "tôn đại ma đầu", "đông lăng 1928", "dụ lăng", "định đông lăng",
                 "càn long", "từ hi", "phổ nghi", "đới lạp", "tống mỹ linh", "hà ứng khâm", "cửu long bảo kiếm", "dạ minh châu", "hồ sơ hình sự",
                 "into the killer's mind"],
        "hashtags": ["DongLangDaoMo", "TonDienAnh", "HoSo"], "category": "24",
        "ch00_title": "Mở đầu: Tiếng mìn đêm 4/7/1928", "thumb": "t1.jpg", "publish_at": "2026-11-22T14:00:00Z", "playlist": "Ngoài Đời Thật",
        "chapter_titles": TITLES, "video_credits": [],
    },
}


def _pool(prefix, n):
    return [f"{prefix}{i}" for i in range(1, n + 1)]


WAR = ["bei", "bei2", "swords", "ft17", "train", "zzc", "zzl", "wl25", "mwar", "m1921", "m1925", "m1927", "m1929", "repub", "gold", "m1914", "mciv"]
TOMB = (_pool("eq", 18) + _pool("dd", 12) + ["dl_old", "dl_air", "dl_map", "dl_tower", "dl_hall", "yl_door", "yl_cut", "yl_ruin", "yl_stone", "yl_wall",
        "yl_ming", "yl_w", "yl_c", "yl_dmg"])
NJ = ["nanjing", "mnat", "m1927", "m1929"] + _pool("cks", 13) + _pool("he", 4) + _pool("tv", 8) + _pool("yan", 8) + _pool("dl", 7)
POOLOF = {}
for _p in (WAR, TOMB, NJ):
    for _k in _p:
        POOLOF.setdefault(_k, _p)
POOLOF["sun"] = POOLOF["sun2"] = WAR
ALL = list(dict.fromkeys(WAR + TOMB + NJ + ["puyi_x", "puyi_bed", "puyi_boy", "feng", "cixi_fun", "cixi_fun2", "audience", "ql8", "ql9", "ql10", "ql6", "ql7",
                         "cixi5", "cixi6", "cixi7", "garb1", "garb2", "crown", "ql_fu", "bell_heart_sutra", "qing_brushpot_paradise", "qing_musical_chime"]))
OBJ = ["fluorite", "pearls", "guanyin", "garb1", "garb2", "crown", "buddha", "bell_heart_sutra", "qing_jade_cup", "qianlong_dragon_vase",
       "qianlong_buddhist_vase", "qianlong_moon_flask", "qianlong_dragon_plaque", "qing_musical_chime", "qing_brushpot_paradise", "melon_jade_pot", "ql_fu"]
ALL = list(dict.fromkeys(ALL + OBJ))
for _k in ALL:
    POOLOF.setdefault(_k, ALL)
for _k in ("fluorite", "buddha", "melon_jade_pot"):
    POOLOF[_k] = OBJ
LIMIT = 3


def rebalance():
    """Mỗi ảnh ≤ 3 lần: phần `bg` thừa của cảnh chữ được đổi sang ảnh ít dùng nhất cùng nhóm."""
    scenes = [s for n in CHAPTERS if n in CH for s in CH[n]["scenes"]]
    img_uses, nested = {}, []
    def nest(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "img" and isinstance(v, str):
                    img_uses[v] = img_uses.get(v, 0) + 1
                elif k != "bg":
                    nest(v)
        elif isinstance(x, list):
            for v in x:
                nest(v)
    for s in scenes:
        nest({k: v for k, v in s.items() if k != "bg"})
    kept, repl = {}, []
    for s in scenes:
        k = s.get("bg")
        if not isinstance(k, str):
            continue
        used = img_uses.get(k, 0) + kept.get(k, 0)
        if used < LIMIT:
            kept[k] = kept.get(k, 0) + 1
        else:
            repl.append(s)
    tot = lambda m: img_uses.get(m, 0) + kept.get(m, 0)
    prev = None
    for s in repl:
        pool = POOLOF.get(s["bg"])
        if not pool:
            print(f"  ! ảnh {s['bg']} quá {LIMIT} lần và không có nhóm thay")
            continue
        cands = [m for m in pool if tot(m) < LIMIT and m != s["bg"] and m != prev]
        if not cands:
            cands = [m for m in ALL if tot(m) < LIMIT and m != s["bg"] and m != prev]
        if not cands:
            print(f"  ! nhóm của {s['bg']} hết ảnh")
            continue
        m = min(cands, key=lambda m: (tot(m), ALL.index(m) if m in ALL else 0))
        kept[m] = kept.get(m, 0) + 1
        s["bg"] = m
        prev = m


def to_clips():
    """Đổi một số cảnh kinetic có nền ảnh thành b-roll (clip kho chung): cần >= 30 cảnh b-roll, mỗi clip <= 4 lần."""
    uses = {k: 0 for k in V}
    inv = {v: k for k, v in V.items()}
    for n in CHAPTERS:
        for s in CH[n]["scenes"]:
            if s.get("vid") in inv:
                uses[inv[s["vid"]]] += 1
    rot = 0
    prev = None
    for i, n in enumerate(CHAPTERS):
        sc_ = CH[n]["scenes"]
        ks = [j for j, s in enumerate(sc_) if s["type"] == "kinetic" and s.get("bg") and len(s["items"]) <= 3 and 3 <= j < len(sc_) - 2]
        pick = [ks[len(ks) // 3], ks[2 * len(ks) // 3]] if i < 6 else [ks[len(ks) // 2]]
        for j in pick:
            s = sc_[j]
            order = sorted(V, key=lambda k: (uses[k], (list(V).index(k) - rot) % len(V)))
            k = next(k for k in order if uses[k] < 4 and k != prev)
            uses[k] += 1; rot += 3; prev = k
            s["kin"] = s.pop("items"); s.pop("bg", None)
            s.update(type="broll", vid=V[k], tone="noir", veil=0.4, illus=FILMV)


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


def walk_used(x, used):
    if isinstance(x, dict):
        for k, v in x.items():
            if k in ("img", "bg") and isinstance(v, str):
                used.append(v)
            walk_used(v, used)
    elif isinstance(x, list):
        for v in x:
            walk_used(v, used)


if __name__ == "__main__":
    run_all()
    to_clips()
    rebalance()
    used = []
    walk_used(CH, used)
    from collections import Counter
    cnt = Counter(used)
    for k, n in cnt.items():
        if n > 3:
            print(f"  ! ảnh {k} dùng {n} lần")
    # ghi công ảnh CC BY / BY-SA
    cred = []
    for k in sorted(cnt):
        if k in DIMS:
            r = next(x for x in _RES if x["file"] == IMGS[k])
            lic = r.get("license", "")
            if lic and not lic.lower().startswith(("public", "cc0", "pd")):
                cred.append(f"{r['file'].removeprefix('File:')} — Wikimedia Commons — {lic} — {r.get('url', '')}")
    SPEC["youtube"]["video_credits"] = sorted(set(cred))
    spec = dict(SPEC)
    (D / "spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    _keep = {f.name: json.loads(f.read_text(encoding="utf-8")) for f in D.glob("ch[0-9][0-9].json")}
    write(__file__, CH, {k: v for k, v in IMGS.items() if k in cnt}, GEO, endcardBg="sun")
    # script_lines.py giữ nguyên 'lines' đã sinh: ghi lại từ bản cũ để mốc `at` không lệch
    for _n, _old in _keep.items():
        _f = D / _n
        _d = json.loads(_f.read_text(encoding="utf-8")); _d["lines"] = _old["lines"]; _d["title"] = _old["title"]
        _f.write_text(json.dumps(_d, ensure_ascii=False, indent=1), encoding="utf-8")
