"""Bộ sinh short "ngày tốt theo việc".

    .venv/bin/python output/cl_staging/grok/tools/ngaytot.py <việc> <tháng> <năm>
    .venv/bin/python output/cl_staging/grok/tools/ngaytot.py <việc> <tháng> <năm> --render
    .venv/bin/python output/cl_staging/grok/tools/ngaytot.py --de-xuat
    .venv/bin/python output/cl_staging/grok/tools/ngaytot.py --lich

Tính bằng amlich.py + canchi.py. Không dùng vnlunar cho thần, trực, nạp âm.
Mốc can chi ngày và tên thần theo output/cl_staging/grok/samples/01_hoangdao_v2_check.py
(đối chiếu fs/calendar_facts_verified.json). Bảng kỵ và việc của trực Thành/Khai
theo build_F12.py: cưới hỏi và khai trương; làm nhà đi cùng nhóm việc lớn;
nhập trạch chỉ trực Khai. Không nới hắc đạo.

Mỗi lần chạy tự kiểm 7 ngày verified. Lệch thì dừng.

Spec Studio xuất ra samples/specs/. Cỡ chữ bảng (ngày dương >= 90px, dòng phụ
>= 40px, khối nằm giữa khung) nằm trong khóa post_css. studio.py không đọc khóa
này. Render qua --render để chèn CSS vào job, không sửa mã dùng chung.
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import json
import math
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
if (ROOT / "output/cl_staging/long").is_dir():
    sys.path.insert(0, str(ROOT / "output/cl_staging/long"))
try:
    from . import amlich as A  # noqa: E402
    from . import canchi as K  # noqa: E402
except ImportError:
    import amlich as A  # noqa: E402
    import canchi as K  # noqa: E402

CHI, CAN = K.CHI, K.CAN
# Tên thần theo bản verified (F12 đọc Thiên Đức / Huyền Vũ / Câu Trận — cùng vị trí vòng).
THAN = ["Thanh Long", "Minh Đường", "Thiên Hình", "Chu Tước", "Kim Quỹ", "Kim Đường",
        "Bạch Hổ", "Ngọc Đường", "Thiên Lao", "Nguyên Vũ", "Tư Mệnh", "Câu Trần"]
HOANG = {0, 1, 4, 5, 7, 10}
TRUC = ["Kiến", "Trừ", "Mãn", "Bình", "Định", "Chấp", "Phá", "Nguy", "Thành", "Thu", "Khai", "Bế"]
GIO = [[0, 1, 3, 6, 8, 9], [2, 3, 5, 8, 10, 11], [0, 1, 4, 5, 7, 10],
       [0, 2, 3, 6, 7, 9], [2, 4, 5, 8, 9, 11], [1, 4, 6, 7, 10, 11]]
# Thành / Khai: build_F12 (cưới hỏi, khai trương). Làm nhà gán cùng nhóm việc lớn.
# Nhập trạch chỉ Khai. Bốn trực Định, Chấp, Phá, Nguy là bảng phổ thông, không đưa vào lời khuyên.
VIEC = {
    "Kiến": ["xuất hành"], "Trừ": ["chữa bệnh"], "Mãn": ["đi dạo"], "Bình": ["di chuyển"],
    "Định": ["giao dịch", "đính hôn"], "Chấp": ["ký giấy tờ"], "Phá": ["phá dỡ"], "Nguy": ["cúng lễ"],
    "Thành": ["cưới hỏi", "khai trương", "làm nhà"], "Thu": ["thu xếp", "nhận việc"],
    "Khai": ["cưới hỏi", "khai trương", "làm nhà", "nhập trạch"], "Bế": ["lập kế hoạch"],
}
TAM_NUONG, NGUYET_KY = {3, 7, 13, 18, 22, 27}, {5, 14, 23}
DUONG_CONG = {(1, 13), (2, 11), (3, 9), (4, 7), (5, 5), (6, 3), (7, 8), (7, 29),
              (8, 27), (9, 25), (10, 23), (11, 21), (12, 19)}
TIET = [(315, 2, "Lập xuân"), (345, 3, "Kinh trập"), (15, 4, "Thanh minh"), (45, 5, "Lập hạ"),
        (75, 6, "Mang chủng"), (105, 7, "Tiểu thử"), (135, 8, "Lập thu"), (165, 9, "Bạch lộ"),
        (195, 10, "Hàn lộ"), (225, 11, "Lập đông"), (255, 0, "Đại tuyết"), (285, 1, "Tiểu hàn")]
VIEC_OK = ("cưới hỏi", "khai trương", "làm nhà", "nhập trạch")
SLUG = {"cưới hỏi": "cuoi_hoi", "khai trương": "khai_truong", "làm nhà": "lam_nha", "nhập trạch": "nhap_trach"}
KICK = {"cưới hỏi": "CƯỚI HỎI", "khai trương": "KHAI TRƯƠNG", "làm nhà": "LÀM NHÀ", "nhập trạch": "NHẬP TRẠCH"}
CAU = {"cưới hỏi": "cưới", "khai trương": "khai trương", "làm nhà": "làm nhà", "nhập trạch": "nhập trạch"}
HOI = {
    "cưới hỏi": "Nhà bạn định cưới **ngày nào?**",
    "khai trương": "Bạn định khai trương **ngày nào?**",
    "làm nhà": "Bạn định làm nhà **ngày nào?**",
    "nhập trạch": "Bạn nhập trạch **ngày nào?**",
}
THANG_DOC = {1: "một", 2: "hai", 3: "ba", 4: "tư", 5: "năm", 6: "sáu", 7: "bảy", 8: "tám",
             9: "chín", 10: "mười", 11: "mười một", 12: "mười hai"}
SO_HOA = {1: "MỘT", 2: "HAI", 3: "BA", 4: "BỐN", 5: "NĂM", 6: "SÁU", 7: "BẢY", 8: "TÁM"}
SPEC_DIR = ROOT / "output/cl_staging/grok/samples/specs"
SAMPLE_DIR = ROOT / "output/cl_staging/grok/samples"
_PKG_VERIFIED = Path(__file__).resolve().parent / "calendar_facts_verified.json"
VERIFIED = _PKG_VERIFIED if _PKG_VERIFIED.is_file() else (ROOT / "output/cl_staging/fs/calendar_facts_verified.json")

_CACHE: dict = {}


def lon_deg(jd):
    return math.degrees(A._sun_longitude(jd)) % 360.0


def ict_date(jd):
    jdn = int(math.floor(jd + 19 / 24 + 1e-8))
    dd, mm, yy = A.jd_to_date(jdn)
    return dt.date(yy, mm, dd)


def find_tiet_days(year):
    """Mỗi tiết một lần trong năm dương. Không lùi 40 ngày: cửa sổ đó bắt Đại tuyết
    tháng 12 năm trước rồi dừng, nên cả tháng 12 năm nay vẫn bị tính là tháng Hợi."""
    start = A.jd_from_date(1, 1, year) - 2
    end = A.jd_from_date(31, 12, year) + 2
    out = []
    for deg, chi, name in TIET:
        prev, jd, hit = lon_deg(start), start, None
        while jd < end:
            jd += 1 / 24
            cur = lon_deg(jd)
            crossed = prev <= deg < cur or (prev > cur and (prev <= deg or deg < cur))
            prev = cur
            if not crossed:
                continue
            lo, hi = jd - 1 / 24, jd
            for _s in range(24):
                mid = (lo + hi) / 2
                lm, hm = lon_deg(lo), lon_deg(mid)
                if (lm <= deg < hm) or (lm > hm and (lm <= deg or deg < hm)):
                    hi = mid
                else:
                    lo = mid
            if ict_date(hi).year == year:
                hit = hi
                break
        if hit is None:
            raise SystemExit(name)
        out.append({"name": name, "chi": chi, "jd": hit, "date": ict_date(hit)})
    out.sort(key=lambda x: x["jd"])
    return out


def tiet_month_chi(day):
    for y in (day.year - 1, day.year):
        _CACHE.setdefault(y, find_tiet_days(y))
    jd_end = A.jd_from_date(day.day, day.month, day.year) - 19 / 24 + 1 - 1e-6
    current = None
    for ev in _CACHE[day.year - 1] + _CACHE[day.year]:
        if ev["jd"] <= jd_end:
            current = ev
    return current["chi"], current["name"], current["date"]


def fact(day: dt.date) -> dict:
    ld, lm, ly, leap = A.solar2lunar(day.day, day.month, day.year)
    i60 = (45 + A.jd_from_date(day.day, day.month, day.year) - A.jd_from_date(2, 10, 2026)) % 60
    can_i, chi_i = i60 % 10, i60 % 12
    mchi, tiet_name, tiet_date = tiet_month_chi(day)
    start = (2 * ((mchi - 2) % 12)) % 12
    dan = []
    if ld in TAM_NUONG:
        dan.append("Tam Nương")
    if ld in NGUYET_KY:
        dan.append("Nguyệt kỵ")
    if (lm, ld) in DUONG_CONG and not leap:
        dan.append("Dương Công")
    truc = TRUC[(chi_i - mchi) % 12]
    return {
        "date": day, "duong": day.isoformat(), "ld": ld, "lm": lm, "leap": leap,
        "am": f"{ld}/{lm}" + (" nhuận" if leap else ""),
        "ngay": f"{CAN[can_i]} {CHI[chi_i]}", "chi": CHI[chi_i],
        "than": THAN[(chi_i - start) % 12], "hoang": (chi_i - start) % 12 in HOANG,
        "truc": truc, "hop": VIEC[truc], "xung": CHI[(chi_i + 6) % 12],
        "gio": [CHI[g] for g in GIO[chi_i % 6]], "dan": dan,
        "tiet": tiet_name, "tiet_ngay": tiet_date.isoformat(), "tiet_thang": CHI[mchi],
        "solar_day": day.day, "solar_month": day.month,
    }


def good_for(f, viec):
    return f["hoang"] and viec in f["hop"] and not f["dan"]


def span(a, b):
    d, out = a, []
    while d <= b:
        out.append(d)
        d += dt.timedelta(days=1)
    return out


def month_span(year, month):
    last = calendar.monthrange(year, month)[1]
    return span(dt.date(year, month, 1), dt.date(year, month, last))


def tet_date(lunar_year: int) -> dt.date:
    dd, mm, yy = A.lunar2solar(1, 1, lunar_year, 0)
    return dt.date(yy, mm, dd)


def self_check() -> int:
    ver = json.loads(VERIFIED.read_text(encoding="utf-8"))
    bad = 0
    for iso, exp in ver.items():
        f = fact(dt.date.fromisoformat(iso))
        exp_gio = [p.split(" (")[0] for p in exp["gio_tot"].split(", ")]
        got = [f["am"], f["ngay"], f["than"], "hoàng đạo" if f["hoang"] else "hắc đạo", f["truc"], f["xung"], f["gio"]]
        want = [exp["am_lich"], exp["ngay"], exp["than"], exp["hoang_hac"], exp["truc"], exp["xung"], exp_gio]
        if got != want:
            bad += 1
            print("LỆCH", iso)
            print("  được", got)
            print("  muốn", want)
    if bad:
        raise SystemExit(f"tự kiểm verified lệch {bad}/{len(ver)}")
    neo = {
        dt.date(2026, 11, 6): ("28/9", "Giáp Thân", "Tuất", "Khai", "Kim Quỹ", True),
        dt.date(2026, 11, 17): ("9/10", "Ất Mùi", "Hợi", "Thành", "Minh Đường", True),
        dt.date(2026, 11, 29): ("21/10", "Đinh Mùi", "Hợi", "Thành", "Minh Đường", True),
    }
    for day, exp in neo.items():
        f = fact(day)
        got = (f["am"], f["ngay"], f["tiet_thang"], f["truc"], f["than"], f["hoang"])
        if got != exp:
            raise SystemExit(f"neo Lead lệch {day.isoformat()}: {got} != {exp}")
        if not good_for(f, "cưới hỏi"):
            raise SystemExit(f"{day} phải qua lọc cưới hỏi")
    f7 = fact(dt.date(2026, 11, 7))
    if (f7["tiet"], f7["tiet_thang"], f7["truc"], f7["ngay"], f7["than"], f7["hoang"], f7["xung"]) != (
            "Lập đông", "Hợi", "Khai", "Ất Dậu", "Chu Tước", False, "Mão"):
        raise SystemExit("7/11 không khớp Lập đông / Khai / hắc đạo")
    for iso, truc, ngay, than, xung in (
            ("2026-11-04", "Thành", "Nhâm Ngọ", "Thiên Hình", "Tý"),
            ("2026-11-19", "Khai", "Đinh Dậu", "Chu Tước", "Mão")):
        f = fact(dt.date.fromisoformat(iso))
        if (f["truc"], f["ngay"], f["than"], f["xung"], f["hoang"]) != (truc, ngay, than, xung, False):
            raise SystemExit(f"{iso} lệch {f['truc']} {f['ngay']} {f['than']} {f['xung']} hoang={f['hoang']}")
        if good_for(f, "cưới hỏi"):
            raise SystemExit(f"{iso} là hắc đạo, không được qua lọc")
    dai = next(ev for ev in find_tiet_days(2026) if ev["name"] == "Đại tuyết")
    if dai["date"].year != 2026 or dai["date"].month != 12:
        raise SystemExit(f"Đại tuyết 2026 lệch năm: {dai['date']}")
    # Sau Đại tuyết tháng tiết là Tý. Hai ngày này khớp báo cáo 01.
    for iso, am, ngay, than in (
            ("2026-12-12", "4/11", "Canh Thân", "Thanh Long"),
            ("2026-12-24", "16/11", "Nhâm Thân", "Thanh Long")):
        f = fact(dt.date.fromisoformat(iso))
        if (f["am"], f["ngay"], f["than"], f["truc"], f["xung"], f["hoang"], f["tiet_thang"]) != (
                am, ngay, than, "Thành", "Dần", True, "Tý"):
            raise SystemExit(f"{iso} lệch {f['am']} {f['ngay']} {f['than']} {f['truc']} {f['xung']} {f['tiet_thang']}")
        if not good_for(f, "cưới hỏi"):
            raise SystemExit(f"{iso} phải qua lọc cưới hỏi")
    print(f"tự kiểm verified {len(ver)}/{len(ver)}; neo tháng 11 và 12/12, 24/12 khớp")
    return len(ver)


def so(n: int) -> str:
    d = "không một hai ba bốn năm sáu bảy tám chín".split()
    if n < 10:
        return d[n]
    if n < 20:
        if n == 10:
            return "mười"
        if n == 15:
            return "mười lăm"
        return "mười " + d[n - 10]
    ch, dv = divmod(n, 10)
    head = d[ch] + " mươi"
    if dv == 0:
        return head
    if dv == 1:
        return head + " mốt"
    if dv == 5:
        return head + " lăm"
    return head + " " + d[dv]


def liet_ke(nums: list[str]) -> str:
    if len(nums) == 1:
        return nums[0]
    if len(nums) == 2:
        return f"{nums[0]} và {nums[1]}"
    return ", ".join(nums[:-1]) + " và " + nums[-1]


def words_of(line: str) -> int:
    return len(line.replace("**", "").split())


def board_box(n: int) -> dict:
    """Khối bảng giữa khung 1080x1920, trên dải phụ đề (y 1500) và trái cột nút (x 940)."""
    if n <= 2:
        day, sub, gap = 180, 48, 36
    elif n == 3:
        day, sub, gap = 156, 48, 28
    elif n == 4:
        day, sub, gap = 120, 44, 20
    else:
        day, sub, gap = 96, 42, 14
    if day < 90 or sub < 40:
        raise SystemExit(f"cỡ chữ dưới sàn: ngày {day}px, phụ {sub}px")
    # Khớp post_css: .lb-k = font*1.55 + padding 8, .lb-t = font*1.25, .lb-i padding-bottom 8.
    row = day * 1.55 + 8 + sub * 1.25 + 8
    block = n * row + max(0, n - 1) * gap
    top = 920 - block / 2
    if top + block > 1460:
        top = 1460 - block
    if top < 360:
        top = 360
    return {"day_px": day, "sub_px": sub, "gap": gap, "top": round(top), "title_top": round(top - 84),
            "n": n, "block": round(block)}


def post_css(box: dict) -> str:
    return f"""
[data-device="list_build"] .lb-title {{
  left: 80px; right: 160px; top: {box["title_top"]}px; text-align: center;
  font-size: 36px; letter-spacing: .14em; color: var(--accent);
}}
[data-device="list_build"] .lb {{
  left: 70px; right: 160px; top: {box["top"]}px; height: auto;
  display: flex; flex-direction: column; justify-content: flex-start;
  align-items: stretch; gap: {box["gap"]}px;
}}
[data-device="list_build"] .lb-i,
[data-device="list_build"] .lb-k,
[data-device="list_build"] .lb-t,
[data-device="list_build"] .lb-title {{
  visibility: inherit !important;
}}
[data-device="list_build"] .lb-i {{
  display: flex; flex-direction: column; align-items: center; text-align: center;
  grid-template-columns: none; width: 100%;
  padding-bottom: 8px; border-bottom: 2px solid var(--line);
  opacity: 1 !important; transform: none !important;
}}
[data-device="list_build"] .lb-i:last-child {{ border-bottom: none; }}
[data-device="list_build"] .lb-k {{
  width: auto; height: auto; min-width: 0; padding: 4px 0; border-radius: 0;
  background: transparent; color: var(--accent);
  font-family: var(--font-mono); font-weight: 800; display: block;
  font-size: {box["day_px"]}px; line-height: 1.55; letter-spacing: -0.04em;
}}
[data-device="list_build"] .lb-t {{
  font-size: {box["sub_px"]}px; font-weight: 700; line-height: 1.25;
  color: var(--ink); text-align: center; max-width: 860px;
}}
[data-device="quote"] .qt-mark {{ top: 340px; font-size: 120px; line-height: 1; }}
[data-device="quote"] .qt {{ top: 560px; font-size: 72px; line-height: 1.28; }}
[data-device="hook_poster"] .hp-big {{ font-size: 136px; line-height: 1.05; right: 160px; }}
[data-device="list_build"] .lb-t small {{
  display: block; font-size: {box["sub_px"]}px; font-weight: 700;
  color: var(--ink); margin-top: 0;
}}
"""


def sub_line(f) -> str:
    return f"{f['am']} · trực {f['truc']} · xung {f['xung']}"


def truc_lines(rows: list[dict]) -> list[str]:
    groups = []
    for f in rows:
        key = (f["truc"], f["xung"])
        if groups and groups[-1][0] == key:
            groups[-1][1].append(f)
        else:
            groups.append([key, [f]])
    lines = []
    for (truc, xung), gs in groups[:2]:
        names = liet_ke([so(g["solar_day"]) for g in gs])
        if len(gs) == 1:
            lines.append(f"Ngày {names} trực {truc}, tuổi {xung} nên tránh.")
        else:
            lines.append(f"Ngày {names} trực {truc}, tuổi {xung} xung.")
        if words_of(lines[-1]) > 22:
            raise SystemExit("câu trực dài quá 22 chữ: " + lines[-1])
        chi_set = [w.strip(",.") for w in lines[-1].split() if w.strip(",.") in set(CHI)]
        if len(chi_set) > 3:
            raise SystemExit("quá 3 tên chi: " + lines[-1])
    if len(groups) > 2:
        lines.append("Những ngày còn lại, tuổi xung có trên bảng.")
    return lines


def scripts(viec: str, month: int, year: int, rows: list[dict]) -> tuple[list[str], list[str]]:
    n = len(rows)
    thang = THANG_DOC[month]
    dem = so(n)
    viec_cau = CAU[viec]
    days = liet_ke([so(r["solar_day"]) for r in rows])
    a = [
        f"Tháng {thang} có {dem} ngày {viec_cau}.",
        f"Đó là ngày {days}.",
        *truc_lines(rows),
        "Theo truyền thống thôi, chỉ để tham khảo.",
        HOI[viec],
    ]
    if words_of(a[0]) > 10:
        raise SystemExit("câu 1 dài hơn 10 chữ: " + a[0])
    b = [
        f"Tháng {thang} có {dem} ngày {viec_cau}.",
        f"Ngày {days}, lưu lại nhé.",
    ]
    if words_of(b[0]) > 10:
        raise SystemExit("câu 1 biến thể B dài hơn 10 chữ: " + b[0])
    return a, b


def spec_paths(viec, month, year):
    stem = f"{SLUG[viec]}_{year}_{month:02d}"
    return SPEC_DIR / f"{stem}_a.json", SPEC_DIR / f"{stem}_b.json"


def build_specs(viec: str, month: int, year: int, rows: list[dict]) -> tuple[dict, dict]:
    lines_a, lines_b = scripts(viec, month, year, rows)
    box = board_box(len(rows))
    css = post_css(box)
    n = len(rows)
    title = f"{SO_HOA.get(n, str(n))} NGÀY HOÀNG ĐẠO"
    items = []
    for f in rows:
        items.append({
            "key": f"{f['solar_day']}/{month}",
            "text": sub_line(f),
            "at": [1, "ngày"],
        })
    kick = f"{KICK[viec]} THÁNG {month}"
    foot = "Theo truyền thống · chỉ để tham khảo"
    common = {
        "channel": "demo", "theme": "tet-poster", "kicker": kick, "foot": foot,
        "voice_series": "fs", "tts": True, "loop": True, "capGroup": 3,
        "board": box, "post_css": css,
    }
    big = "**NGÀY CƯỚI**" if viec == "cưới hỏi" else f"**{KICK[viec]}**"
    spec_a = {
        **common,
        "id": f"ngaytot_{SLUG[viec]}_{year}_{month:02d}_a",
        "lines": lines_a,
        "tail": 1.4,
        "scenes": [
            {"device": "hook_poster", "line": 0, "num": str(n), "kick": f"THÁNG {month} NĂM {year}",
             "big": big, "markAt": [0, "có"], "ghost": str(month)},
            {"device": "list_build", "line": 1, "seam": "zoom", "title": title, "ghost": "", "items": items},
            {"device": "quote", "line": len(lines_a) - 2, "seam": "side", "mode": "karaoke",
             "text": lines_a[-2], "source": "chỉ để tham khảo", "ghost": ""},
            {"device": "close", "line": len(lines_a) - 1, "seam": "curve", "q": lines_a[-1],
             "markSpan": 2, "ghost": "?"},
        ],
        "out": str((SAMPLE_DIR / f"02_{SLUG[viec]}_{year}_{month:02d}_a.mp4").relative_to(ROOT)),
    }
    items_b = []
    for f in rows:
        items_b.append({"key": f"{f['solar_day']}/{month}", "text": sub_line(f), "at": 0})
    spec_b = {
        **common,
        "id": f"ngaytot_{SLUG[viec]}_{year}_{month:02d}_b",
        "lines": lines_b,
        "tail": 1.6,
        "scenes": [
            {"device": "list_build", "line": 0, "title": title, "ghost": "", "items": items_b},
        ],
        "out": str((SAMPLE_DIR / f"02_{SLUG[viec]}_{year}_{month:02d}_b.mp4").relative_to(ROOT)),
    }
    return spec_a, spec_b


def write_spec(path: Path, spec: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def select_rows(viec: str, month: int, year: int, sau_tet: bool) -> tuple[list[dict], list[dict], dt.date | None]:
    tet = tet_date(year) if sau_tet or month == 2 else (tet_date(year) if year >= 2027 else None)
    rows, skipped = [], []
    for day in month_span(year, month):
        f = fact(day)
        if not good_for(f, viec):
            continue
        if sau_tet and day < tet_date(year):
            skipped.append(f)
            continue
        rows.append(f)
    return rows, skipped, tet


def print_table(viec, month, year, rows, skipped, han):
    print(f"\n{viec} · tháng {month}/{year}")
    if not rows:
        print("không có ngày qua lọc. Không làm short.")
        return
    print(f"{'dương':<12} {'âm':<10} {'can chi':<12} {'thần':<12} {'trực':<6} {'xung':<6} tiết")
    for f in rows:
        print(f"{f['duong']:<12} {f['am']:<10} {f['ngay']:<12} {f['than']:<12} {f['truc']:<6} {f['xung']:<6} {f['tiet_thang']} ({f['tiet']} {f['tiet_ngay']})")
    if skipped:
        print("trước Tết, không đưa vào short:", ", ".join(f["duong"] for f in skipped))
    print(f"ngày đầu {rows[0]['duong']} · hạn đăng {han.isoformat()} (5 ngày trước)")


_ORIG_COMPOSE = None


def patch_compose(css: str):
    import studio
    global _ORIG_COMPOSE
    if _ORIG_COMPOSE is None:
        _ORIG_COMPOSE = studio.compose
    orig = _ORIG_COMPOSE

    def patched(*a, **k):
        html = orig(*a, **k)
        if "</style>" not in html:
            raise SystemExit("job không có </style> để chèn cỡ chữ")
        return html.replace("</style>", css + "\n</style>", 1)

    studio.compose = patched
    return studio


def speech_end(job: Path) -> float:
    man = json.loads((job / "assets" / "vo.json").read_text(encoding="utf-8"))
    return float(man["segments"][-1]["end"])


def fit_tail(spec_path: Path, kind: str) -> float:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    studio = patch_compose(spec["post_css"])
    studio.build(spec_path, render=False, do_qa=False, strict=False, use_ledger=False)
    job = studio.JOBS / spec["id"]
    speech = speech_end(job)
    dur = round(speech + spec["tail"], 2)
    lo, hi, target = (15.0, 20.0, 17.5) if kind == "A" else (8.0, 10.0, 9.0)
    if not (lo <= dur <= hi):
        tail = round(target - speech, 2)
        tail = min(max(tail, 0.8), 4.5 if kind == "A" else 3.2)
        spec["tail"] = tail
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        dur = round(speech + tail, 2)
    if not (lo <= dur <= hi):
        raise SystemExit(f"biến thể {kind} dài {dur}s (giọng {speech}s, đuôi {spec['tail']}s), ngoài {lo}-{hi}")
    print(f"  biến thể {kind}: giọng {speech:.2f}s + đuôi {spec['tail']}s = {dur:.2f}s")
    return dur


def render_spec(spec_path: Path, kind: str) -> None:
    fit_tail(spec_path, kind)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    studio = patch_compose(spec["post_css"])
    studio.build(spec_path, render=True, do_qa=True, strict=False, use_ledger=False)
    job = studio.JOBS / spec["id"]
    mp4 = ROOT / spec["out"]
    sheet = job / "qa_sheet.jpg"
    if sheet.is_file():
        dst = mp4.with_name(mp4.stem + "_qa.jpg")
        shutil.copy(sheet, dst)
        print("  tờ QA", dst.relative_to(ROOT))
    qaj = job / "qa.json"
    if qaj.is_file():
        shutil.copy(qaj, mp4.with_suffix(".qa.json"))


def han_dang(rows: list[dict]) -> dt.date | None:
    if not rows:
        return None
    return rows[0]["date"] - dt.timedelta(days=5)


def export_one(viec: str, month: int, year: int, sau_tet: bool, render: bool) -> dict:
    if viec not in VIEC_OK:
        raise SystemExit(f"việc không có trong bộ lọc: {viec}. Chọn: {', '.join(VIEC_OK)}")
    rows, skipped, _tet = select_rows(viec, month, year, sau_tet)
    han = han_dang(rows)
    print_table(viec, month, year, rows, skipped, han)
    info = {"viec": viec, "month": month, "year": year, "rows": rows, "skipped": skipped,
            "han": han, "sau_tet": sau_tet, "specs": []}
    if not rows:
        return info
    spec_a, spec_b = build_specs(viec, month, year, rows)
    pa, pb = spec_paths(viec, month, year)
    write_spec(pa, spec_a)
    write_spec(pb, spec_b)
    info["specs"] = [pa, pb]
    print("spec A", pa.relative_to(ROOT))
    print("spec B", pb.relative_to(ROOT))
    print("lời A:")
    for i, line in enumerate(spec_a["lines"], 1):
        print(f"  {i}. {line.replace('**', '')}")
    print("lời B:")
    for i, line in enumerate(spec_b["lines"], 1):
        print(f"  {i}. {line}")
    if render:
        render_spec(pa, "A")
        render_spec(pb, "B")
    return info


def write_de_xuat() -> None:
    cases = [
        ("cưới hỏi", 11, 2026, False),
        ("khai trương", 11, 2026, False),
        ("cưới hỏi", 12, 2026, False),
        ("làm nhà", 12, 2026, False),
        ("khai trương", 1, 2027, False),
        ("khai trương", 2, 2027, True),
        ("nhập trạch", 2, 2027, True),
    ]
    tet2027 = tet_date(2027)
    nt12, _, _ = select_rows("nhập trạch", 12, 2026, False)
    nt12_txt = ("có ngày qua lọc: " + ", ".join(f["duong"] for f in nt12)) if nt12 else "không có ngày Khai hoàng đạo qua lọc"
    lines = [
        "# Đề xuất short ngày tốt theo việc",
        "",
        "Chưa render, trừ cưới hỏi tháng 11 khi chạy riêng `--render`.",
        "Lọc: hoàng đạo + trực có việc + không Tam Nương, Nguyệt kỵ, Dương Công.",
        "Nhập trạch chỉ trực Khai. Không nới hắc đạo.",
        f"Tháng 12/2026 nhập trạch: {nt12_txt}. Không làm short.",
        f"Tết {tet2027.isoformat()} là mùng 1 tháng Giêng (tính bằng amlich.lunar2solar).",
        "Tháng 2/2027 chỉ lấy ngày từ mùng 1 Tết trở đi.",
        "Hạn đăng = đúng 5 ngày trước ngày dương đầu tiên trong bảng.",
        "",
    ]
    for viec, month, year, sau in cases:
        rows, skipped, _ = select_rows(viec, month, year, sau)
        title = f"Tháng {month} năm {year} ngày nào tốt để {viec}?"
        lines.append(f"## {title}")
        lines.append("")
        if sau:
            lines.append(f"Phạm vi: từ Tết {tet2027.isoformat()} trở đi.")
            lines.append("")
        if skipped:
            lines.append("Trước Tết, qua lọc nhưng không đưa vào short: "
                         + ", ".join(f"{f['solar_day']}/{month} ({f['am']}, trực {f['truc']}, xung {f['xung']})" for f in skipped)
                         + ".")
            lines.append("")
        if not rows:
            lines.append("Không có ngày qua lọc. Không làm short.")
            lines.append("")
            continue
        han = han_dang(rows)
        lines.append(f"Hạn đăng: {han.strftime('%-d/%-m/%Y')} (ngày đầu {rows[0]['date'].strftime('%-d/%-m/%Y')}).")
        lines.append("")
        lines.append("| Dương | Âm | Can chi | Thần | Trực | Xung | Tháng tiết |")
        lines.append("|---|---|---|---|---|---|---|")
        for f in rows:
            lines.append(f"| {f['date'].strftime('%-d/%-m')} | {f['am']} | {f['ngay']} | {f['than']} | {f['truc']} | {f['xung']} | {f['tiet_thang']} |")
        lines.append("")
        pa, pb = spec_paths(viec, month, year)
        spec_a, spec_b = build_specs(viec, month, year, rows)
        write_spec(pa, spec_a)
        write_spec(pb, spec_b)
        lines.append(f"Spec: `{pa.relative_to(ROOT)}`, `{pb.relative_to(ROOT)}`.")
        lines.append("")
    out = SAMPLE_DIR / "02_ngaytot_de_xuat.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("đề xuất", out.relative_to(ROOT))


# Thứ tự chọn ngày tiêu biểu cho short tổng. Không phải xếp hạng khoa học:
# Thanh Long / Minh Đường hay được kể trước trong nhóm hoàng đạo, rồi các thần còn lại.
# Cùng bậc thì lấy ngày sớm hơn.
HANG_THAN = {"Thanh Long": 0, "Minh Đường": 1, "Kim Quỹ": 2, "Ngọc Đường": 3, "Kim Đường": 4, "Tư Mệnh": 5}


def add_months(d: dt.date, n: int) -> dt.date:
    m0 = d.year * 12 + (d.month - 1) + n
    y, m = divmod(m0, 12)
    last = calendar.monthrange(y, m + 1)[1]
    return dt.date(y, m + 1, min(d.day, last))


def nd(d: dt.date) -> str:
    return f"{d.day}/{d.month}/{d.year}"


def nd_ngan(d: dt.date) -> str:
    return f"{d.day}/{d.month}"


def am_hien(f: dict) -> str:
    return f"{f['am']} âm"


def hang(f: dict):
    return (HANG_THAN.get(f["than"], 9), f["date"])


def gom_truc(rows: list[dict]) -> list[tuple]:
    """Gom theo (trực, xung), không cần liền ngày."""
    order, bucket = [], {}
    for f in rows:
        key = (f["truc"], f["xung"])
        if key not in bucket:
            order.append(key)
            bucket[key] = []
        bucket[key].append(f)
    return [(k, bucket[k]) for k in order]


def chi_trong(text: str) -> list[str]:
    return [w.strip(",.()·") for w in text.replace("·", " ").split() if w.strip(",.()·") in set(CHI)]


def cua_so_thang(first: dt.date, som: int, muon: int) -> tuple[dt.date, dt.date]:
    """som < muon: đăng từ `muon` tháng trước tới `som` tháng trước ngày đầu."""
    return add_months(first, -muon), add_months(first, -som)


def cua_so_ngay(first: dt.date, som: int, muon: int) -> tuple[dt.date, dt.date]:
    return first - dt.timedelta(days=muon), first - dt.timedelta(days=som)


def tom_ngay(rows: list[dict]) -> str:
    if not rows:
        return "không có ngày qua lọc"
    return "; ".join(
        f"{nd_ngan(f['date'])} ({am_hien(f)}, {f['ngay']}, {f['than']}, trực {f['truc']}, xung {f['xung']})"
        for f in rows)


def chon_tieu_bieu() -> list[dict]:
    """Mỗi tháng 1 ngày, tối đa 6 hàng. Tháng trống thì nhường suất cho ngày hạng cao hơn của tháng khác."""
    chosen, extras = [], []
    for month in range(1, 7):
        rows, _sk, _ = select_rows("cưới hỏi", month, 2027, month == 2)
        if not rows:
            continue
        ranked = sorted(rows, key=hang)
        chosen.append(ranked[0])
        if len(ranked) > 1:
            extras.append(ranked[1])
    extras.sort(key=hang)
    for extra in extras:
        if len(chosen) >= 6:
            break
        chosen.append(extra)
    chosen.sort(key=lambda f: f["date"])
    return chosen


def _dat_ngay(items: list[dict], today: dt.date) -> None:
    """Ưu tiên số nhỏ được giữ ngày trước. Trùng dưới 2 ngày thì đẩy mục sau, nếu còn trong cửa sổ."""
    occupied: list[dt.date] = []
    for it in sorted(items, key=lambda x: (x["uu"], x["muon"])):
        som, muon = it["som"], it["muon"]
        prefer = it.get("prefer")
        if prefer is not None and som <= prefer <= muon:
            d, note = prefer, "mốc Lead nằm trong cửa sổ"
        elif today > muon:
            d, note = today, "đã qua cửa sổ — đề xuất đăng ngay"
        else:
            d = som + dt.timedelta(days=(muon - som).days // 2)
            if d < today:
                d, note = today, "trong cửa sổ, mốc giữa đã qua"
            else:
                note = "giữa cửa sổ"
        pushed = 0
        while any(abs((d - o).days) < 2 for o in occupied) and pushed < 8:
            nxt = d + dt.timedelta(days=2)
            if today > muon or nxt <= muon:
                d = nxt
                pushed += 1
            else:
                note += "; trùng ngày khác vì hết cửa sổ"
                break
        if pushed:
            note += f"; đẩy {pushed * 2} ngày để khỏi trùng"
        occupied.append(d)
        it["dang"] = d
        it["dang_note"] = note


def write_lich() -> None:
    today = dt.date.today()
    tet = tet_date(2027)
    items: list[dict] = []

    def add(uu, title, rows, som, muon, prefer=None, extra=""):
        items.append({"uu": uu, "title": title, "rows": rows, "som": som, "muon": muon,
                      "prefer": prefer, "extra": extra})

    # Cưới hỏi tháng 1–6/2027. Tháng 2 chỉ từ mùng 1 Tết.
    for month in range(1, 7):
        rows, skipped, _ = select_rows("cưới hỏi", month, 2027, month == 2)
        extra = ""
        if month == 2:
            extra = f"Chỉ từ mùng 1 Tết {nd(tet)}. Trước Tết không đưa: " + (
                ", ".join(f"{nd_ngan(f['date'])} ({am_hien(f)}, trực {f['truc']}, xung {f['xung']})" for f in skipped)
                if skipped else "không có") + "."
        if not rows:
            items.append({"uu": 50 + month, "title": f"Tháng {month} năm 2027 ngày nào tốt để cưới hỏi?",
                          "rows": [], "som": None, "muon": None, "prefer": None, "extra": extra, "bo": True})
            continue
        som, muon = cua_so_thang(rows[0]["date"], 3, 5)
        add(1 if month == 1 else 10 + month,
            f"Tháng {month} năm 2027 ngày nào tốt để cưới hỏi?", rows, som, muon, extra=extra)

    tong = chon_tieu_bieu()
    som_t, muon_t = cua_so_thang(tong[0]["date"], 3, 5)
    add(3, "Ngày cưới đẹp năm 2027: 6 tháng đầu năm", tong, som_t, muon_t,
        extra="Mỗi tháng 1 ngày tiêu biểu; tháng 2 thêm 1 ngày vì tháng 3 không có suất. Tối đa 6 hàng.")

    rows, _, _ = select_rows("khai trương", 11, 2026, False)
    som, muon = cua_so_ngay(rows[0]["date"], 14, 28)
    add(2, "Tháng 11 năm 2026 ngày nào tốt để khai trương?", rows, som, muon)

    rows, skipped, _ = select_rows("khai trương", 2, 2027, True)
    som, muon = cua_so_ngay(rows[0]["date"], 14, 28)
    prefer = dt.date(2027, 1, 17)
    add(20, "Tháng 2 năm 2027 ngày nào tốt để khai trương?", rows, som, muon, prefer,
        extra=f"Sau Tết {nd(tet)}. Lead: đăng giữa tháng 1. Mốc 17/1 là 28 ngày trước {nd_ngan(rows[0]['date'])}. "
              f"Bỏ trước Tết: " + ", ".join(nd_ngan(f["date"]) for f in skipped) + ".")

    rows, skipped, _ = select_rows("nhập trạch", 2, 2027, True)
    som, muon = cua_so_ngay(rows[0]["date"], 14, 28)
    add(21, "Tháng 2 năm 2027 ngày nào tốt để nhập trạch?", rows, som, muon, dt.date(2027, 1, 19),
        extra=f"Sau Tết. Nhập trạch chỉ trực Khai. Mốc 19/1 còn trong 2–4 tuần trước {nd_ngan(rows[0]['date'])}.")

    for month, year, uu in ((12, 2026, 8), (1, 2027, 12)):
        rows, _, _ = select_rows("làm nhà", month, year, False)
        som, muon = cua_so_thang(rows[0]["date"], 1, 3)
        add(uu, f"Tháng {month} năm {year} ngày nào tốt để làm nhà, động thổ?", rows, som, muon,
            extra="Động thổ dùng cùng ngày làm nhà (trực Thành hoặc Khai, cùng lọc).")

    xep = [it for it in items if not it.get("bo")]
    _dat_ngay(xep, today)

    # Tháng cô hồn: tháng 7 âm.
    d0, d1, co = None, None, []
    d = dt.date(2027, 1, 1)
    while d <= dt.date(2027, 12, 31):
        f = fact(d)
        if f["lm"] == 7 and not f["leap"]:
            co.append(d)
        d += dt.timedelta(days=1)
    if co:
        d0, d1 = co[0], co[-1]

    # Gần đúng tháng 3: trực Thành/Khai nhưng không qua lọc.
    gan = []
    for day in month_span(2027, 3):
        f = fact(day)
        if f["truc"] in ("Thành", "Khai") and not good_for(f, "cưới hỏi"):
            gan.append(f)

    lines = [
        "# Lịch đăng đề xuất — ngày tốt",
        "",
        "Chưa render. Không ghi sổ, không đăng.",
        f"Mốc tính cửa sổ: hôm nay {nd(today)}.",
        "Lọc giữ nguyên: hoàng đạo + trực có việc + không Tam Nương, Nguyệt kỵ, Dương Công. Không nới hắc đạo.",
        "Cưới hỏi đăng trước 3–5 tháng (tính từ ngày dương đầu tiên trong bảng).",
        "Khai trương và nhập trạch đăng trước 2–4 tuần. Sau Tết, Lead chốt giữa tháng 1/2027.",
        "Làm nhà và động thổ đăng trước 1–3 tháng. Động thổ dùng cùng ngày với làm nhà.",
        f"Tết {nd(tet)} là mùng 1 tháng Giêng (amlich.lunar2solar).",
        "",
        "## Bảng",
        "",
        "| Đăng | Tiêu đề | Ngày tốt | Cửa sổ | Ghi chú |",
        "|---|---|---|---|---|",
    ]
    for it in sorted(items, key=lambda x: (x.get("dang") or dt.date(2099, 1, 1), x["uu"])):
        if it.get("bo"):
            lines.append(f"| — | {it['title']} | không có ngày qua lọc | — | {it['extra']} |")
            continue
        cua = f"{nd(it['som'])} – {nd(it['muon'])}"
        lines.append(
            f"| {nd(it['dang'])} | {it['title']} | {tom_ngay(it['rows'])} | {cua} | {it['dang_note']}. {it['extra']} |"
        )
    lines += [
        "",
        "## Tháng 3/2027",
        "",
        "Không có ngày cưới hỏi qua lọc. Không làm short tháng 3.",
        "Các ngày trực Thành hoặc Khai trong tháng đều không phải hoàng đạo, hoặc dính kỵ:",
        "",
    ]
    for f in gan:
        ly = "hắc đạo" if not f["hoang"] else "hoàng đạo"
        ky = (", " + ", ".join(f["dan"])) if f["dan"] else ""
        lines.append(f"- {nd_ngan(f['date'])} ({am_hien(f)}, {f['ngay']}, {f['than']}, trực {f['truc']}, xung {f['xung']}, {ly}{ky})")
    lines += [
        "",
        "## Short tổng",
        "",
        "Quy tắc chọn (trong code): Thanh Long, Minh Đường, Kim Quỹ, Ngọc Đường, Kim Đường, Tư Mệnh; cùng bậc thì ngày sớm hơn.",
        "Mỗi tháng lấy 1 ngày. Tháng không có ngày thì suất đó cho ngày hạng cao kế tiếp của tháng khác, dừng ở 6 hàng.",
        "",
        "| Dương | Âm | Can chi | Thần | Trực | Xung |",
        "|---|---|---|---|---|---|",
    ]
    for f in tong:
        lines.append(f"| {nd_ngan(f['date'])} | {am_hien(f)} | {f['ngay']} | {f['than']} | {f['truc']} | {f['xung']} |")
    xung = []
    for f in tong:
        if f["xung"] not in xung:
            xung.append(f["xung"])
    lines += [
        "",
        f"Chi xung trên một khung nếu ghi hết: {', '.join(xung)} ({len(xung)} tên). Khi dựng short tổng, không ghi quá 3 tên chi một khung.",
        "",
        "## Tháng cô hồn",
        "",
    ]
    if d0:
        lines.append(f"Tháng 7 âm 2027: {nd(d0)} đến {nd(d1)} (quét từng ngày, tháng âm 7, không nhuận).")
        lines.append("Theo truyền thống, tháng cô hồn dân gian kiêng cưới. Nếu làm nửa cuối năm thì bỏ khoảng này, nói theo truyền thống.")
    lines += [
        "",
        "## Không xếp vào lịch này",
        "",
    ]
    for viec, month, year, sau, ly in (
        ("khai trương", 1, 2027, False, "trước Tết; Lead không giữ. Cửa sổ 2–4 tuần sẽ rơi giữa tháng 12/2026."),
        ("nhập trạch", 1, 2027, False, "trước Tết; cùng lý do."),
        ("nhập trạch", 12, 2026, False, "không có ngày Khai hoàng đạo qua lọc."),
        ("khai trương", 3, 2027, False, "không có ngày qua lọc; giữa tháng 1 là quá sớm so với cửa sổ 2–4 tuần."),
        ("nhập trạch", 3, 2027, False, "không có ngày qua lọc."),
    ):
        rows, skipped, _ = select_rows(viec, month, year, sau)
        lines.append(f"- {viec} tháng {month}/{year}: {tom_ngay(rows) if rows else 'không có ngày'}. {ly}")
    lines += [
        "",
        "Mẫu bố cục P1–P3 render riêng. Tháng 3 không có ngày nên mẫu dùng tháng 2/2027 (14, 24, 26/2, sau Tết).",
        "",
    ]
    out = SAMPLE_DIR / "04_lich_dang.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("lịch đăng", out.relative_to(ROOT))


def main() -> int:
    self_check()
    if "--de-xuat" in sys.argv:
        write_de_xuat()
        return 0
    if "--lich" in sys.argv:
        write_lich()
        return 0
    ap = argparse.ArgumentParser(description="In bảng ngày tốt và xuất spec Studio A/B.")
    ap.add_argument("viec")
    ap.add_argument("thang", type=int)
    ap.add_argument("nam", type=int)
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--sau-tet", action="store_true")
    a = ap.parse_args()
    export_one(a.viec, a.thang, a.nam, a.sau_tet, a.render)
    return 0


if __name__ == "__main__":
    sys.exit(main())
