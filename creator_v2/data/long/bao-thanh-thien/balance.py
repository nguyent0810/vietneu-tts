"""Giữ mỗi ảnh <= 3 lần và mỗi clip <= 3 lần (cổng A8), thay các lần dùng thừa bằng tư liệu cùng nhóm.

1. Thẻ đồ họa (ledger/org/timeline/bars/file) lấy nền là clip b-roll (trừ các thẻ có ảnh mang nghĩa, khai ở KEEP_BG).
2. Clip dùng quá 3 lần: đổi sang clip cùng nhóm ít dùng nhất.
3. Ảnh của cảnh ảnh (photo/print/split/file...) được ưu tiên; nền (bg) của cảnh chữ lấy phần còn lại, hết thì thành clip.
Ba lần dùng đầu tiên theo thứ tự chương được giữ nguyên.
"""
import json

MAX_IMG = 3
MAX_VID = 3

# (chương, mốc at dạng JSON): thẻ giữ ảnh nền vì ảnh mang nghĩa (hồ sơ A/B, Lưu Thái hậu, Đoan Châu...)
KEEP_BG = {("ch01", "2"), ("ch01", "6"), ("ch04", "4"), ("ch10", "6"), ("ch11", "25"), ("ch11", "32"), ("ch12", "8"), ("ch12", '[17, "là"]'), ("ch13", "14"), ("ch13", "2")}
CARD_TYPES = {"ledger", "org", "timeline", "bars", "file"}
# cảnh mà ảnh nền/ảnh chính là ý nghĩa của câu (chiếc đao, nghiên mực, tuồng, Diêm La): được giữ ảnh trước khi chia phần còn lại
PINNED = {("ch00", "17"), ("ch00", "15"), ("ch00", "18"), ("ch03", "32"), ("ch04", "null"), ("ch04", "3"), ("ch09", "28"), ("ch11", "null"), ("ch11", "3"), ("ch11", "9"),
          ("ch13", "46")}

IMG_GROUPS = {
    "bao": ["statue", "tomb", "sketch", "p8", "p9", "p125", "p140", "bao124", "shrine", "hf153", "hf156", "hf165", "hf167", "bao155", "hf157", "hf163",
            "bao90", "park93", "hf166"],
    "stage": ["opera", "novel", "guil", "yanluo", "shrine", "bao124", "bao155"],
    "song": ["qm65", "qm118", "gate116", "street", "model1", "model2", "kfmap", "kf1950", "bjmap", "fu", "gate", "dragon", "xiang", "pag13", "pag203",
             "pag211", "pag216", "pag219", "pag77", "garden", "palace", "party", "guests", "cavalry", "hydro", "taizu", "literary", "go",
             "renzong", "ren181", "ren185", "rtomb", "liu", "caoemp", "pag17", "pag217", "pag218", "model3", "bridge18", "clock58", "star68", "star69",
             "ship67"],
    "doc": ["mifei", "yingzao", "slab", "epit", "breit", "wc196", "wc198", "banknote", "p141", "yuji", "map1141", "hefeimap", "kf1950", "bjmap"],
    "rel": ["rel1", "rel2", "rel3", "rel4"],
    "zq": ["zqwall", "zqrock", "zqview", "zqmei", "zqtower", "zqgate", "zq107", "zq109", "zq105"],
}
VID_GROUPS = {
    "ink": ["856911", "9785157", "39583060", "18333375"],
    "docs": ["30117908", "11765182", "6980366"],
    "temple": ["2865316", "34070866", "39579888", "39550230", "40233547", "36382688", "33009780", "35977046", "40442683", "40163649", "39407965", "39127118",
               "40310036", "40322765", "29335847", "39567005"],
    "night": ["17079051", "6252550", "40328878", "39333459", "35182250", "35244435", "32540543", "39139722", "33009796"],
    "town": ["39531176", "39519061", "36494728", "40479561", "30103886", "30103893", "30103899", "38368356", "39611578", "39532069", "38984159"],
    "stone": ["36239253"],
    "bones": ["5762177", "5762179", "10041487"],
    "misc": ["39277761", "19486650", "3967264", "5594429"],
}
# b-roll mượn làm nền thẻ: không lấy clip xương/sọ
ALL_VIDS = [x for g in ("docs", "ink", "temple", "night", "town", "stone", "misc") for x in VID_GROUPS[g]]
ALL_VIDS = [x for x in ALL_VIDS if x not in ("19486650", "3967264", "5594429")]   # lũ, đào đất, phá dỡ: chỉ dùng đúng cảnh


def _group_of(key, groups):
    for g, items in groups.items():
        if key in items:
            return g
    return None


def _scenes(CH):
    for name in sorted(CH):
        for s in CH[name]["scenes"]:
            yield name, s


def balance(CH, IMGS):
    img_use, swaps = {}, []
    vid_use = {}
    for _, s in _scenes(CH):
        if s.get("vid"):
            vid_use[s["vid"]] = vid_use.get(s["vid"], 0) + 1

    def cur_vid_pick():
        c = [x for x in ALL_VIDS if vid_use.get(x, 0) < MAX_VID]
        return min(c, key=lambda x: (vid_use.get(x, 0), ALL_VIDS.index(x))) if c else None

    def to_vid(name, s, why):
        cv = cur_vid_pick()
        if not cv:
            return False
        swaps.append((name, s["type"], s.get("at"), why, "vid " + cv))
        del s["bg"]
        s["vid"] = cv
        s.setdefault("tone", "noir")
        vid_use[cv] = vid_use.get(cv, 0) + 1
        return True

    # 1. clip quá 3 lần -> clip cùng nhóm
    seen = {}
    for name, s in _scenes(CH):
        v = s.get("vid")
        if not v:
            continue
        if seen.get(v, 0) >= MAX_VID:
            g = _group_of(v, VID_GROUPS)
            pool = [x for x in VID_GROUPS.get(g, []) if x != v and seen.get(x, 0) < MAX_VID and vid_use.get(x, 0) < MAX_VID]
            pool = pool or [x for x in ALL_VIDS if x != v and seen.get(x, 0) < MAX_VID]
            if not pool:
                raise SystemExit(f"hết clip thay cho {v!r} ở {name}")
            new = min(pool, key=lambda x: (seen.get(x, 0), pool.index(x)))
            swaps.append((name, s["type"], s.get("at"), "vid " + v, "vid " + new))
            s["vid"] = v = new
        seen[v] = seen.get(v, 0) + 1
    vid_use = dict(seen)

    # 0. thẻ đồ họa: nền ảnh -> clip
    for name, s in _scenes(CH):
        if s["type"] in CARD_TYPES and s.get("bg") and not s.get("vid") and (name, json.dumps(s.get("at"), ensure_ascii=False)) not in KEEP_BG:
            to_vid(name, s, s["bg"])

    def pick(cur, avoid):
        g = _group_of(cur, IMG_GROUPS)
        ok = lambda k: k != cur and k not in avoid and img_use.get(k, 0) < MAX_IMG and k in IMGS  # noqa: E731
        pool = [k for k in IMG_GROUPS.get(g, []) if ok(k)] or [k for k in IMG_GROUPS["song"] if ok(k)]
        return min(pool, key=lambda k: (img_use.get(k, 0), pool.index(k))) if pool else None

    # 2. ảnh: lượt 0 cảnh ghim, lượt 1 cảnh ảnh, lượt 2 nền của cảnh chữ
    pinned = set()
    for name, s in _scenes(CH):
        if (name, json.dumps(s.get("at"))) in PINNED:
            pinned.add(id(s))
            for h, k in [(s, "img"), (s, "bg")]:
                if h.get(k):
                    img_use[h[k]] = img_use.get(h[k], 0) + 1
    for pass_no in (1, 2):
        for name, s in _scenes(CH):
            if id(s) in pinned:
                continue
            holders = ([(s, "img")] + [(s[x], "img") for x in ("a", "b") if isinstance(s.get(x), dict)]) if pass_no == 1 else [(s, "bg")]
            keys_here = {h.get(k) for h, k in holders if h.get(k)} | {s.get("img"), s.get("bg")}
            for h, k in holders:
                cur = h.get(k)
                if not cur:
                    continue
                if img_use.get(cur, 0) >= MAX_IMG:
                    new = pick(cur, keys_here)
                    if new is None and pass_no == 2 and not s.get("vid") and to_vid(name, s, cur):
                        continue
                    if new is None:
                        raise SystemExit(f"hết ảnh thay cho {cur!r} ở {name} {s['type']} {s.get('at')}")
                    swaps.append((name, s["type"], s.get("at"), cur, new))
                    h[k] = cur = new
                    keys_here.add(new)
                img_use[cur] = img_use.get(cur, 0) + 1
    return {k: IMGS[k] for k in IMGS if img_use.get(k)}, swaps
