"""Builder + render cho fs_dot2_1622: Phủ FS đợt 2 (15 short 18-22/11/2026).

Phân bổ 15 short FS:
- 18/11 (1 short): slot 15:00 UTC (yeartable: 1983 Quý Hợi)
- 19/11 (3 short): slot 04:30 (month_sheet: T11 âm), 08:00 (yeartable: 1986 Bính Dần), 15:00 (yeartable: 1987 Đinh Mão)
- 20/11 (4 short): slot 04:30 (month_sheet: T12/2026 ngày hoàng đạo), 08:00 (yeartable: 1991 Tân Mùi), 12:00 (yeartable: 1993 Quý Dậu), 15:00 (yeartable: 1997 Đinh Sửu)
- 21/11 (3 short): slot 04:30 (month_sheet: T12/2026 khai trương), 08:00 (yeartable: tuổi đón quý nhân 2027), 15:00 (yeartable: công danh sự nghiệp 2027)
- 22/11 (4 short): slot 04:30 (month_sheet: T11 âm ngày đẹp), 08:00 (month_sheet: T1/2027 hoàng đạo trước Tết), 12:00 (yeartable: khai trương 2027), 15:00 (yeartable: mở rộng làm ăn 2027)
Tổng: 10 yeartable (6 khuôn năm sinh mệnh/màu + 4 bảng tuổi 2027) + 5 month_sheet (hoàng đạo & ngày tốt ngắn hạn).

Mọi số tính bằng code (amlich, canchi, saohan, tuvi_year, hoangdao_daily).
QA overflow và contrast đạt 100%.
"""
from __future__ import annotations
from shortbuild import validate

import datetime as dt
import importlib
import json
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in (ROOT, ROOT / "output" / "cl_staging" / "long", HERE / "tools", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import hf_batch_render as R
import amlich
import canchi
from fs_calendar import hoangdao_daily
import saohan
import tuvi_year
import fs_mau_ngay as FMN

P = importlib.import_module("build_fs_phu_1104")

RENDER_DIR = HERE / "render_fs_dot2"
RENDER_DIR.mkdir(parents=True, exist_ok=True)
ROOT_RENDER_DIR = RENDER_DIR

HF = ROOT / "hyperframes_short"
COMP = HF / "compositions"
PLAN_FILE = ROOT / "output" / "cl_staging" / "fs" / "plan_fs_dot2_1622.json"
PKG_DIR = ROOT / "output" / "cl_staging" / "fs" / "packaging"
PKG_DIR.mkdir(parents=True, exist_ok=True)
BATCH = "fs_dot2_1622"

YEARS = list(range(1950, 2011))
PROF27 = {y: tuvi_year.profile(y, start=2027, n_years=1) for y in YEARS}
R27 = {y: PROF27[y]["cac_nam"][0] for y in YEARS}

# ---------------------------------------------------------------- Số liệu tính bằng code
# 1. Kiểm tra 6 năm sinh mệnh/màu
P83 = tuvi_year.profile(1983, start=2027, n_years=1)
assert P83["can_chi"] == "Quý Hợi" and P83["nap_am"] == "Đại Hải Thủy" and P83["hanh"] == "Thủy"

P86 = tuvi_year.profile(1986, start=2027, n_years=1)
assert P86["can_chi"] == "Bính Dần" and P86["nap_am"] == "Lư Trung Hỏa" and P86["hanh"] == "Hỏa"

P87 = tuvi_year.profile(1987, start=2027, n_years=1)
assert P87["can_chi"] == "Đinh Mão" and P87["nap_am"] == "Lư Trung Hỏa" and P87["hanh"] == "Hỏa"

P91 = tuvi_year.profile(1991, start=2027, n_years=1)
assert P91["can_chi"] == "Tân Mùi" and P91["nap_am"] == "Lộ Bàng Thổ" and P91["hanh"] == "Thổ"

P93 = tuvi_year.profile(1993, start=2027, n_years=1)
assert P93["can_chi"] == "Quý Dậu" and P93["nap_am"] == "Kiếm Phong Kim" and P93["hanh"] == "Kim"

P94 = tuvi_year.profile(1994, start=2027, n_years=1)
assert P94["can_chi"] == "Giáp Tuất" and P94["nap_am"] == "Sơn Đầu Hỏa" and P94["hanh"] == "Hỏa"

P97 = tuvi_year.profile(1997, start=2027, n_years=1)
assert P97["can_chi"] == "Đinh Sửu" and P97["nap_am"] == "Giản Hạ Thủy" and P97["hanh"] == "Thủy"

# 2. Bảng tuổi 2027
# Công danh 2027: Nam mạng sao Thái Dương & Nữ mạng sao Thái Âm (cát tinh lớn)
SAO_THAI_DUONG_NAM = [y for y in YEARS if saohan.sao(y, True, at=2027) == "Thái Dương"]
SAO_THAI_AM_NU = [y for y in YEARS if saohan.sao(y, False, at=2027) == "Thái Âm"]
assert SAO_THAI_DUONG_NAM == [1951, 1960, 1969, 1978, 1987, 1996, 2005]
assert SAO_THAI_AM_NU == [1952, 1961, 1970, 1979, 1988, 1997, 2006]

# Khai trương 2027: Cung Tứ Tấn Tài không Tam Tai
HO_TU_TAN_TAI_27 = [y for y in YEARS if R27[y]["hoang_oc"] == "Tứ Tấn Tài" and not R27[y]["tam_tai"]]
assert HO_TU_TAN_TAI_27 == [1964, 1973, 1982, 1988, 1997, 2000, 2006, 2009]

# Khởi sự làm ăn 2027: Nhất Cát và Nhì Nghi không Tam Tai
HO_NHAT_CAT_27 = [y for y in YEARS if R27[y]["hoang_oc"] == "Nhất Cát" and not R27[y]["tam_tai"]]
HO_NHI_NGHI_27 = [y for y in YEARS if R27[y]["hoang_oc"] == "Nhì Nghi" and not R27[y]["tam_tai"]]
assert HO_NHAT_CAT_27 == [1952, 1958, 1961, 1970, 1976, 1985, 1994]
assert HO_NHI_NGHI_27 == [1957, 1960, 1966, 1969, 1984, 1993, 2002, 2008]

# ---------------------------------------------------------------- Dữ liệu month_sheet (ngắn hạn trong 2 tháng tới)
# Mọi ô lấy từ day_data qua FMN.month_cells. "Kỵ" = day_data["dan"] (Tam Nương, Nguyệt kỵ, Dương Công).
# Mọi số đếm / danh sách ngày trong tiêu đề, chip, lời đọc đều sinh từ CÙNG danh sách ô (không gõ tay).
# 1. Tháng 12/2026 dương lịch (31 ngày, 01/12 là thứ Ba, offset = 1)
DAYS_DEC_2026 = FMN.month_cells(dt.date(2026, 12, 1), dt.date(2026, 12, 31))
_c = FMN.counts(DAYS_DEC_2026)
N_HD_DEC, N_GOOD_DEC = _c["hoang"], _c["thuan_loi"]
DEC_OFFSET = dt.date(2026, 12, 1).weekday()  # 1

# Khai trương tháng 12/2026: hoàng đạo, không kỵ, VIEC[trực] có "khai trương" (trực Thành / Khai)
DAYS_DEC_KT = FMN.month_cells(dt.date(2026, 12, 1), dt.date(2026, 12, 31), special=FMN.khai_truong)
_c = FMN.counts(DAYS_DEC_KT)
KT_DAYS, KT_TRUC = _c["special"], _c["truc_special"]

# 2. Tháng 11 âm lịch năm 2026 (09/12/2026 đến 07/01/2027: 30 ngày), ô hiển thị ngày âm
DAYS_LUNAR11_2026 = FMN.month_cells(dt.date(2026, 12, 9), dt.date(2027, 1, 7), lunar_axis=True)
_c = FMN.counts(DAYS_LUNAR11_2026)
N_HD_L11, N_GOOD_L11 = _c["hoang"], _c["thuan_loi"]
L11_OFFSET = dt.date(2026, 12, 9).weekday()  # 2 (thứ Tư)

# Tháng 11 âm: ngày "việc lớn" = hoàng đạo, không kỵ, VIEC[trực] có cưới hỏi / khai trương / làm nhà
DAYS_LUNAR11_SPECIAL = FMN.month_cells(dt.date(2026, 12, 9), dt.date(2027, 1, 7), lunar_axis=True, special=FMN.viec_lon)
_c = FMN.counts(DAYS_LUNAR11_SPECIAL)
L11_BIG_DAYS, L11_BIG_TRUC = _c["special"], _c["truc_special"]

# 3. Tháng 1/2027 dương lịch (31 ngày, 01/01 là thứ Sáu, offset = 4)
DAYS_JAN27_2027 = FMN.month_cells(dt.date(2027, 1, 1), dt.date(2027, 1, 31))
_c = FMN.counts(DAYS_JAN27_2027)
N_HD_JAN27, N_GOOD_JAN27 = _c["hoang"], _c["thuan_loi"]
JAN27_OFFSET = dt.date(2027, 1, 1).weekday()  # 4

# Câu giải thích ô lịch dùng chung cho các bảng hoàng đạo (khớp legend FMN.LEGEND_HD)
LINE_O_LICH = ("Ô vàng là hoàng đạo thuận lợi, ô vàng góc đỏ là hoàng đạo vướng ngày kỵ, "
               "ô đỏ là ngày kỵ cần tránh việc lớn.")


def _kt_chip(days: list[int], am: bool = False) -> str:
    head = f"MÙNG {days[0]}" if (am and days[0] <= 10) else str(days[0])
    return ", ".join([head] + [str(d) for d in days[1:]])


# ---------------------------------------------------------------- HTML GENERATORS
def build_yeartable_custom(t: dict, dur: float, segs: list[dict]) -> str:
    """Xây HTML yeartable với override font-size và hold frame chống tràn tuyệt đối."""
    base = (COMP / "review_yeartable.html").read_text(encoding="utf-8")

    theme_amber = (
        'amber: { b1: "#d97706", b2: "#b45309", b3: "#78350f", b4: "#451a03", '
        'r1: "rgba(120,53,15,.94)", r2: "rgba(69,26,3,.94)", gold: "#fde68a", gold2: "#fef08a", '
        'chip: "#fffbeb", chipfg: "#78350f", chiptop: "#fde68a", chiptopfg: "#78350f" },'
    )
    if "amber:" not in base:
        base = base.replace("const THEMES = {", f"const THEMES = {{\n    {theme_amber}")

    layout_override = """
  #head { top: 90px; }
  #title { font-size: 68px !important; }
  #title .gold { font-size: 56px !important; }
  #title .s { font-size: 56px !important; }
  #rows { top: 430px; bottom: 310px; gap: 14px; }
  .row, #rows.big .row { padding: 12px 18px; }
  .years.col4 { grid-template-columns: repeat(4, 1fr) !important; gap: 8px 10px !important; }
  .years.col4 .y, #rows.big .years.col4 .y { font-size: 52px !important; padding: 6px 0 !important; border-radius: 14px !important; white-space: nowrap !important; }
  #cap { bottom: 195px; font-size: 44px; }
  #subfoot { position: absolute; left: 50px; right: 50px; bottom: 120px; text-align: center;
             color: var(--gold2); font-weight: 800; font-size: 32px; letter-spacing: .05em;
             text-shadow: 0 2px 8px rgba(0,0,0,.6); }
  #foot { bottom: 65px; font-size: 24px; opacity: .82; }
  #root.ivory #subfoot { color: #b01e14; text-shadow: none; }
  #root.ivory #foot { color: #7a1410; }
  .chi.sm { font-size: 38px !important; line-height: 1.1 !important; }
  /* chip màu (chữ, không phải năm sinh): tự xuống dòng theo số màu, tên dài như "Xanh nước biển" không tràn */
  .years.txt { display: flex !important; flex-wrap: wrap; align-content: center; gap: 10px 12px !important; }
  .years.txt .y, #rows.big .years.txt .y { font-size: 62px !important; padding: 6px 24px !important; border-radius: 16px !important; white-space: nowrap !important; flex: 0 0 auto; }
"""
    base = base.replace("</style>", layout_override + "</style>")
    subfoot_div = '<div id="subfoot">DỪNG HÌNH TÌM NĂM SINH CỦA BẠN</div>'
    base = base.replace('<div id="foot">', f"{subfoot_div}\n  <div id=\"foot\">")

    old_big = 'if ((DATA.rows || []).length && DATA.rows.length <= 3) rows.classList.add("big");'
    new_big = (
        'const maxYears = Math.max(...(DATA.rows || []).map(r => (r.years || []).length), 0);\n'
        '  if ((DATA.rows || []).length && DATA.rows.length <= 3 && maxYears < 7) rows.classList.add("big");'
    )
    base = base.replace(old_big, new_big)

    old_row_gen = '<div class="years">${r.years.map((y) => `<span class="y">${y}</span>`).join("")}</div>'
    new_row_gen = (
        '<div class="years${r.years && r.years.length >= 7 ? " col4" : ""}${r.years && r.years.some((y) => isNaN(+y)) ? " txt" : ""}">'
        '${r.years.map((y) => `<span class="y">${y}</span>`).join("")}</div>'
    )
    base = base.replace(old_row_gen, new_row_gen)

    # Đóng băng chuyển động trong 3.2s cuối để khung cuối hoàn toàn tĩnh (Luật 20)
    old_onupdate = """  tl.to(st, { t: DUR, duration: DUR, ease: "none", onUpdate: () => {
    const t = st.t, p = t / DUR;           // p: 0 -> 1, khung cuối = khung đầu (lặp liền)
    svg.style.transform = `rotate(${p * 45}deg)`;   // 45 độ = một quẻ -> trùng khung đầu
    document.getElementById("glow").style.opacity = 0.85 + 0.15 * Math.sin(p * Math.PI * 2);
    SP.forEach((o) => { o.d.style.opacity = 0.25 + 0.6 * (0.5 + 0.5 * Math.sin(o.ph + p * Math.PI * 2 * Math.round(o.sp * 2))); });  // số vòng nguyên -> lặp liền
    // dải sáng quét từng hàng trong 75% đầu, rồi nghỉ
    // vệt cuối xong trước 85% thời lượng (bảng 6 hàng từng kẹt ở khung cuối)
    shines.forEach((el, i) => { const a = 0.12 + i * (0.5 / Math.max(1, shines.length - 1)), q = (p - a) / 0.22; el.style.transform = `translateX(${-260 + Math.min(Math.max(q, 0), 1) * 1300}px)`; el.style.opacity = q > 0 && q < 1 ? 1 : 0; });
    // viên năm sinh sáng lần lượt (nhịp nhẹ)
    ys.forEach((el, i) => { const q = Math.sin((p * ys.length * 0.5 - i * 0.5) * Math.PI); el.style.transform = `scale(${1 + Math.max(q, 0) * 0.035})`; });
    // phụ đề: câu đang đọc
    const cur = DATA.segs.find((sg) => t >= sg.start - 0.05 && t < sg.end + 0.25);
    if (cur) {
      if (cap.dataset.s !== cur.text) { cap.dataset.s = cur.text; cap.innerHTML = words.filter((w) => w.s === cur).map((w) => `<span class="cw" data-t="${w.t}">${w.w}</span>`).join(" "); }
      cap.querySelectorAll(".cw").forEach((e) => e.classList.toggle("on", +e.dataset.t <= t + 0.02));
      cap.style.opacity = 1;
    } else { cap.style.opacity = 0; }
  } });"""

    new_onupdate = """  const tStop = (DATA.segs && DATA.segs.length) ? DATA.segs[DATA.segs.length - 1].end : Math.max(1.0, DUR - 3.2);
  tl.to(st, { t: DUR, duration: DUR, ease: "none", onUpdate: () => {
    const t = st.t;
    const p = Math.min(1.0, t / tStop);
    svg.style.transform = `rotate(${p * 45}deg)`;
    document.getElementById("glow").style.opacity = 0.85 + 0.15 * Math.sin(p * Math.PI * 2);
    SP.forEach((o) => { o.d.style.opacity = 0.25 + 0.6 * (0.5 + 0.5 * Math.sin(o.ph + p * Math.PI * 2 * Math.round(o.sp * 2))); });
    shines.forEach((el, i) => { const a = 0.12 + i * (0.5 / Math.max(1, shines.length - 1)), q = (p - a) / 0.22; el.style.transform = `translateX(${-260 + Math.min(Math.max(q, 0), 1) * 1300}px)`; el.style.opacity = q > 0 && q < 1 ? 1 : 0; });
    ys.forEach((el, i) => { const q = Math.sin((p * ys.length * 0.5 - i * 0.5) * Math.PI); el.style.transform = `scale(${1 + Math.max(q, 0) * 0.035})`; });

    const cur = t < tStop ? DATA.segs.find((sg) => t >= sg.start - 0.05 && t < sg.end) : null;
    if (cur) {
      if (cap.dataset.s !== cur.text) { cap.dataset.s = cur.text; cap.innerHTML = words.filter((w) => w.s === cur).map((w) => `<span class="cw" data-t="${w.t}">${w.w}</span>`).join(" "); }
      cap.querySelectorAll(".cw").forEach((e) => e.classList.toggle("on", +e.dataset.t <= t + 0.02));
      cap.style.opacity = 1;
    } else { cap.style.opacity = 0; }
  } });"""
    base = base.replace(old_onupdate, new_onupdate)

    data = {
        "dur": dur,
        "theme": t.get("theme", "navy"),
        "segs": segs,
        "rows": [{"chi": c, "tag": tag, "years": ys} for c, tag, ys in t["rows"]],
    }

    title_val = t.get("title_html") or t["title"]
    html = (
        base.replace("__DUR__", str(dur))
        .replace("__CHIP__", t["chip"])
        .replace("__TITLE__", title_val)
        .replace("__DATA__", json.dumps(data, ensure_ascii=False))
    )
    return html


def build_month_sheet_generic(t: dict, dur: float, segs: list[dict]) -> str:
    """Tạo HTML month_sheet tổng quát, hỗ trợ offset và số ngày bất kỳ."""
    fonts = P.font_css()
    days = t["days"]
    offset = t["offset"]

    cells_html = ['<div class="cal-cell empty"></div>'] * offset

    for d_item in days:
        d = d_item["solar_day"]
        l_str = d_item["lunar_str"]
        c_type = d_item["cell_type"]

        corner_html = '<div class="corner-red" data-layout-allow-overflow></div>' if c_type == "gold-tn" else ""
        cell_str = f"""
      <div class="cal-cell {c_type}" id="day-cell-{d}">
        {corner_html}
        <div class="day-solar">{d}</div>
        <div class="day-lunar">{l_str}</div>
      </div>"""
        cells_html.append(cell_str)

    # Đủ 5 hoặc 6 tuần
    total_cells = math.ceil(len(cells_html) / 7) * 7
    total_cells = max(35, total_cells)
    while len(cells_html) < total_cells:
        cells_html.append('<div class="cal-cell empty"></div>')

    grid_content = "\n".join(cells_html)
    segs_json = json.dumps(segs, ensure_ascii=False)

    kicker = t.get("kicker", "LỊCH VẠN NIÊN")
    title_main = t.get("title_main", "")
    title_gold = t.get("title_gold", "")
    subchip = t.get("subchip_text", "")
    legend = t.get("legend_text", "Vàng: hoàng đạo · Góc đỏ: trùng Tam Nương · Đỏ: ngày kỵ · Tham khảo")
    subfoot = t.get("subfoot_text", "DỪNG HÌNH LƯU LẠI LỊCH NHÉ")
    n_rows = total_cells // 7
    row_height = 135 if n_rows >= 6 else 156

    html = f"""<!doctype html>
<html lang="vi" data-needs-fit="1">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<style>
{fonts}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; width: 1080px; height: 1920px; overflow: hidden;
      background: #070b14; font-family: "Be Vietnam Pro", sans-serif; }}
    #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden;
      background: radial-gradient(90% 70% at 50% 18%, #142036 0%, #0a111f 45%, #050810 100%); }}
    #grain {{ position: absolute; inset: 0; width: 1080px; height: 1920px; opacity: 0.22;
      pointer-events: none; mix-blend-mode: overlay; z-index: 20; }}
    #mountains {{ position: absolute; left: 0; bottom: 0; width: 1080px; height: 220px; pointer-events: none; z-index: 1; }}

    /* Header */
    #kicker {{ position: absolute; left: 60px; top: 118px; width: 870px; text-align: center;
      font-family: "JetBrains Mono", monospace; font-weight: 500; font-size: 24px;
      letter-spacing: 0.16em; color: #e7c56a; z-index: 4; }}
    #title {{ position: absolute; left: 60px; top: 165px; width: 870px; text-align: center;
      font-weight: 900; font-size: 54px; line-height: 1.18; letter-spacing: -0.01em; color: #f8fafc; z-index: 4; }}
    #title .gold {{ color: #fde68a; display: block; }}
    #subchip {{ position: absolute; left: 60px; top: 345px; width: 870px; display: flex; align-items: center; justify-content: center; z-index: 4; }}
    .chip-tag {{ display: inline-block; padding: 7px 28px; border-radius: 20px;
      background: rgba(231,197,106,0.12); border: 1.5px solid rgba(231,197,106,0.45);
      font-weight: 700; font-size: 22px; color: #fde68a; }}

    /* Shimmer Beam */
    #shimmer-wrap {{ position: absolute; inset: 0; overflow: hidden; pointer-events: none; z-index: 6; }}
    #shimmer-beam {{ position: absolute; top: 0; left: -140px; width: 120px; height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.7), transparent);
      transform: skewX(-20deg); opacity: 0; }}

    /* Month Sheet Grid */
    #calendar-wrap {{ position: absolute; left: 64px; top: 430px; width: 872px; z-index: 5; }}
    .weekday-row {{ display: grid; grid-template-columns: repeat(7, 1fr); column-gap: 8px; margin-bottom: 8px; }}
    .wd {{ text-align: center; font-family: "JetBrains Mono", monospace; font-size: 24px; font-weight: 800; color: #e7c56a; }}
    .wd.sun {{ color: #f87171; }}

    .month-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); grid-template-rows: repeat({n_rows}, {row_height}px); gap: 8px; }}
    .cal-cell {{ position: relative; border-radius: 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; overflow: hidden; }}
    .cal-cell.empty {{ background: rgba(15, 23, 42, 0.25); border: 1px dashed rgba(100, 116, 139, 0.15); }}

    /* Day typography */
    .day-solar {{ font-size: {54 if n_rows >= 6 else 64}px; font-weight: 900; line-height: 1; margin-top: 4px; }}
    .day-lunar {{ font-size: {26 if n_rows >= 6 else 30}px; font-weight: 700; line-height: 1; margin-top: 6px; }}

    /* Cell Types with High Contrast */
    .cal-cell.gold-good {{
      background: linear-gradient(145deg, rgba(234, 179, 8, 0.32) 0%, rgba(161, 98, 7, 0.45) 100%);
      border: 2px solid rgba(253, 224, 71, 0.95);
      box-shadow: inset 0 0 14px rgba(234, 179, 8, 0.25);
    }}
    .cal-cell.gold-good .day-solar {{ color: #fef08a; }}
    .cal-cell.gold-good .day-lunar {{ color: #fef9c3; }}

    .cal-cell.gold-tn {{
      background: linear-gradient(145deg, rgba(234, 179, 8, 0.32) 0%, rgba(161, 98, 7, 0.45) 100%);
      border: 2px solid rgba(253, 224, 71, 0.95);
      box-shadow: inset 0 0 14px rgba(234, 179, 8, 0.25);
    }}
    .cal-cell.gold-tn .day-solar {{ color: #fef08a; }}
    .cal-cell.gold-tn .day-lunar {{ color: #fef9c3; }}
    .corner-red {{
      position: absolute; top: 0; right: 0; width: 0; height: 0;
      border-style: solid; border-width: 0 34px 34px 0;
      border-color: transparent #ef4444 transparent transparent;
      z-index: 3;
    }}

    .cal-cell.red-bad {{
      background: linear-gradient(145deg, rgba(220, 38, 38, 0.35) 0%, rgba(153, 27, 27, 0.50) 100%);
      border: 2px solid rgba(248, 113, 113, 0.95);
      box-shadow: inset 0 0 14px rgba(239, 68, 68, 0.30);
    }}
    .cal-cell.red-bad .day-solar {{ color: #ffffff; }}
    .cal-cell.red-bad .day-lunar {{ color: #fecaca; }}

    .cal-cell.neutral-cell {{
      background: rgba(30, 41, 59, 0.50);
      border: 1px solid rgba(148, 163, 184, 0.30);
    }}
    .cal-cell.neutral-cell .day-solar {{ color: #f1f5f9; }}
    .cal-cell.neutral-cell .day-lunar {{ color: #cbd5e1; }}

    /* Legend & Subfoot */
    #legend {{ position: absolute; left: 40px; top: 1338px; width: 920px; text-align: center;
      font-size: 21px; font-weight: 700; color: #fde68a; letter-spacing: 0.01em; white-space: nowrap; z-index: 5; }}
    #subfoot {{ position: absolute; left: 64px; top: 1386px; width: 872px; text-align: center;
      font-size: 26px; font-weight: 800; color: #e2e8f0; letter-spacing: 0.08em; z-index: 5; }}

    /* Seal Tham Khao */
    #seal-thamkhao {{ position: absolute; left: 64px; top: 110px; width: 78px; height: 78px; z-index: 10;
      border: 3px solid #b91c1c; border-radius: 8px; background: rgba(185, 28, 28, 0.40);
      display: flex; align-items: center; justify-content: center; transform: rotate(-8deg); }}
    .seal-text {{ font-family: "Be Vietnam Pro", sans-serif; font-weight: 900; font-size: 15px;
      line-height: 1.15; color: #fecaca; text-align: center; letter-spacing: 0.05em; }}

    /* Subtitle caption */
    #caption-box {{ position: absolute; left: 60px; right: 60px; top: 1490px; text-align: center; z-index: 5; pointer-events: none; }}
    .cap-line {{ font-size: 40px; font-weight: 800; line-height: 1.32; color: #ffffff; text-shadow: 0 3px 8px rgba(0,0,0,0.85); }}
    .cw {{ opacity: 0.38; color: #ffffff; transition: color 0.1s ease, opacity 0.1s ease; }}
    .cw.on {{ opacity: 1; color: #fde68a; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
  <div id="grain" data-layout-allow-overflow></div>
  <svg id="mountains" viewBox="0 0 1080 220" fill="none" xmlns="http://www.w3.org/2000/svg" data-layout-allow-overflow>
    <path d="M0 140 Q 270 40 540 130 T 1080 120 L 1080 220 L 0 220 Z" fill="#050810" opacity="0.9"/>
  </svg>

  <div id="shimmer-wrap"><div id="shimmer-beam" data-layout-allow-overflow></div></div>
  <div id="seal-thamkhao"><div class="seal-text">THAM<br>KHẢO</div></div>

  <div id="kicker">{kicker}</div>
  <div id="title">
    {title_main}<br/>
    <span class="gold">{title_gold}</span>
  </div>

  <div id="subchip">
    <div class="chip-tag">{subchip}</div>
  </div>

  <div id="calendar-wrap">
    <div class="weekday-row">
      <div class="wd">T2</div>
      <div class="wd">T3</div>
      <div class="wd">T4</div>
      <div class="wd">T5</div>
      <div class="wd">T6</div>
      <div class="wd">T7</div>
      <div class="wd sun">CN</div>
    </div>
    <div class="month-grid">
{grid_content}
    </div>
  </div>

  <div id="legend">{legend}</div>
  <div id="subfoot">{subfoot}</div>
  <div id="caption-box"></div>
</div>

<script>
  (function() {{
    const segs = {segs_json};
    const tStop = (segs && segs.length) ? segs[segs.length - 1].end : Math.max(1.0, {dur} - 3.2);
    const capBox = document.getElementById("caption-box");

    const words = [];
    segs.forEach((sg) => {{
      const ws = sg.text.split(/\\s+/).filter(Boolean);
      ws.forEach((w, idx) => {{
        const tWord = sg.start + (sg.end - sg.start) * idx / Math.max(1, ws.length);
        words.push({{ w, t: Math.round(tWord * 100) / 100, s: sg }});
      }});
    }});

    const tl = gsap.timeline({{ paused: true }});
    window.__timelines = {{ main: tl }};

    tl.fromTo("#shimmer-beam", {{ x: 0, opacity: 0 }}, {{ x: 1080, opacity: 0.85, duration: 1.2, ease: "power1.inOut" }}, 0.6);
    tl.fromTo("#seal-thamkhao", {{ scale: 1.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, 0.4);

    const st = {{ t: 0 }};
    tl.to(st, {{
      t: {dur},
      duration: {dur},
      ease: "none",
      onUpdate: () => {{
        const curT = st.t;
        const cur = curT < tStop ? segs.find((sg) => curT >= sg.start - 0.05 && curT < sg.end) : null;
        if (cur) {{
          if (capBox.dataset.s !== cur.text) {{
            capBox.dataset.s = cur.text;
            capBox.innerHTML = '<div class="cap-line">' +
              words.filter((w) => w.s === cur).map((w) => `<span class="cw" data-t="${{w.t}}">${{w.w}}</span>`).join(" ") +
              '</div>';
          }}
          capBox.querySelectorAll(".cw").forEach((el) => {{
            el.classList.toggle("on", +el.dataset.t <= curT + 0.02);
          }});
          capBox.style.opacity = "1";
        }} else {{
          capBox.style.opacity = "0";
        }}
      }}
    }}, 0);
  }})();
</script>
</body>
</html>"""
    return html


# ---------------------------------------------------------------- MAKE PLAN
def make_plan() -> list[dict]:
    plan = [
        # ================================================================ 18/11 (1 short)
        # 1. 18/11 15:00 UTC (22:00 VN) - yeartable: 1983 Quý Hợi mệnh gì, hợp màu gì?
        {
            "id": "fs_d2_18_1",
            "day": "2026-11-18",
            "slot": "15:00",
            "series": "fs",
            "lane": "nam_sinh_menh",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "navy",
            "chip": "BẢN MỆNH · MÀU HỢP MỆNH",
            "title_html": '<span class="l s">SINH NĂM 1983 QUÝ HỢI</span><span class="l gold">MỆNH GÌ, HỢP MÀU GÌ?</span>',
            "title": "Sinh năm 1983 Quý Hợi mệnh gì, hợp màu gì?",
            **FMN.menh_fields(P83["hanh"], 1983, "Quý Hợi", "Hợi", "một chín tám ba", P83["nap_am"], "tức nước biển lớn"),
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "yeartable_lookup",
            "hypothesis": "loop_yeartable_lookup",
            "batch_id": BATCH,
        },

        # ================================================================ 19/11 (3 short)
        # 2. 19/11 04:30 UTC (11:30 VN) - month_sheet: Lịch hoàng đạo tháng 11 âm lịch
        {
            "id": "fs_d2_19_1",
            "day": "2026-11-19",
            "slot": "04:30",
            "series": "fs",
            "lane": "lich",
            "style": "month_sheet",
            "format_subtag": "month_sheet",
            "theme": "navy",
            "kicker": "LỊCH HOÀNG ĐẠO · THÁNG 11 ÂM",
            "title": "Lịch hoàng đạo tháng 11 âm lịch: bảng tra trọn tháng",
            "title_main": "THÁNG 11 ÂM LỊCH",
            "title_gold": "BẢNG TRA NGÀY HOÀNG ĐẠO",
            "subchip_text": f"{N_HD_L11} NGÀY HOÀNG ĐẠO · {N_GOOD_L11} NGÀY THUẬN LỢI",
            "legend_text": FMN.LEGEND_HD,
            "subfoot_text": "DỪNG HÌNH LƯU LẠI LỊCH CẢ THÁNG NHÉ",
            "days": DAYS_LUNAR11_2026,
            "offset": L11_OFFSET,
            "script": [
                "Tháng mười một âm,",
                f"toàn tháng có {FMN.so_doc(N_HD_L11)} ngày hoàng đạo, trong đó {FMN.so_doc(N_GOOD_L11)} ngày thuận lợi không vướng kỵ.",
                LINE_O_LICH,
                "Bảng tra cứu giúp bạn chủ động sắp xếp kế hoạch cho cả tháng mười một âm.",
                "Dừng hình lưu lại lịch hoàng đạo nhé.",
            ],
            "display_script": [
                "Tháng 11 âm lịch,",
                f"toàn tháng có {N_HD_L11} ngày hoàng đạo, trong đó {N_GOOD_L11} ngày thuận lợi không vướng kỵ.",
                LINE_O_LICH,
                "Bảng tra cứu giúp bạn chủ động sắp xếp kế hoạch cho cả tháng 11 âm lịch.",
                "Dừng hình lưu lại lịch hoàng đạo nhé.",
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "search_intent",
            "narrative_structure": "month_sheet_scan",
            "hypothesis": "loop_month_sheet_lookup",
            "batch_id": BATCH,
        },

        # 3. 19/11 08:00 UTC (15:00 VN) - yeartable: 1986 Bính Dần
        {
            "id": "fs_d2_19_2",
            "day": "2026-11-19",
            "slot": "08:00",
            "series": "fs",
            "lane": "nam_sinh_menh",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "red",
            "chip": "BẢN MỆNH · MÀU HỢP MỆNH",
            "title_html": '<span class="l s">SINH NĂM 1986 BÍNH DẦN</span><span class="l gold">MỆNH GÌ, HỢP MÀU GÌ?</span>',
            "title": "Sinh năm 1986 Bính Dần mệnh gì, hợp màu gì?",
            **FMN.menh_fields(P86["hanh"], 1986, "Bính Dần", "Dần", "một chín tám sáu", P86["nap_am"], "tức lửa trong lò"),
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "yeartable_lookup",
            "hypothesis": "loop_yeartable_lookup",
            "batch_id": BATCH,
        },

        # 4. 19/11 15:00 UTC (22:00 VN) - yeartable: 1987 Đinh Mão
        {
            "id": "fs_d2_19_3",
            "day": "2026-11-19",
            "slot": "15:00",
            "series": "fs",
            "lane": "nam_sinh_menh",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "red",
            "chip": "BẢN MỆNH · MÀU HỢP MỆNH",
            "title_html": '<span class="l s">SINH NĂM 1987 ĐINH MÃO</span><span class="l gold">MỆNH GÌ, HỢP MÀU GÌ?</span>',
            "title": "Sinh năm 1987 Đinh Mão mệnh gì, hợp màu gì?",
            **FMN.menh_fields(P87["hanh"], 1987, "Đinh Mão", "Mão", "một chín tám bảy", P87["nap_am"], "tức lửa trong lò"),
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "yeartable_lookup",
            "hypothesis": "loop_yeartable_lookup",
            "batch_id": BATCH,
        },

        # ================================================================ 20/11 (4 short)
        # 5. 20/11 04:30 UTC (11:30 VN) - month_sheet: Tháng 12/2026 ngày hoàng đạo
        {
            "id": "fs_d2_20_1",
            "day": "2026-11-20",
            "slot": "04:30",
            "series": "fs",
            "lane": "lich",
            "style": "month_sheet",
            "format_subtag": "month_sheet",
            "theme": "navy",
            "kicker": "LỊCH VẠN NIÊN · THÁNG 12/2026",
            "title": "Tháng 12 năm 2026: bảng ngày hoàng đạo không vướng kỵ",
            "title_main": "THÁNG 12 NĂM 2026",
            "title_gold": "NGÀY HOÀNG ĐẠO THUẬN LỢI",
            "subchip_text": f"{N_GOOD_DEC} NGÀY HOÀNG ĐẠO THUẬN LỢI · CUỐI NĂM",
            "legend_text": FMN.LEGEND_HD,
            "subfoot_text": "DỪNG HÌNH LƯU LẠI LỊCH CUỐI NĂM NHÉ",
            "days": DAYS_DEC_2026,
            "offset": DEC_OFFSET,
            "script": [
                "Tháng mười hai này,",
                f"toàn tháng có {FMN.so_doc(N_HD_DEC)} ngày hoàng đạo, trong đó {FMN.so_doc(N_GOOD_DEC)} ngày thuận lợi không vướng kỵ.",
                LINE_O_LICH,
                "Bảng lịch đánh dấu rõ ràng từng ngày cho cả tháng mười hai.",
                "Dừng hình lưu lại ngày tốt bạn nhé.",
            ],
            "display_script": [
                "Tháng 12 năm 2026,",
                f"toàn tháng có {N_HD_DEC} ngày hoàng đạo, trong đó {N_GOOD_DEC} ngày thuận lợi không vướng kỵ.",
                LINE_O_LICH,
                "Bảng lịch đánh dấu rõ ràng từng ngày cho cả tháng 12.",
                "Dừng hình lưu lại ngày tốt bạn nhé.",
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "search_intent",
            "narrative_structure": "month_sheet_scan",
            "hypothesis": "loop_month_sheet_lookup",
            "batch_id": BATCH,
        },

        # 6. 20/11 08:00 UTC (15:00 VN) - yeartable: 1991 Tân Mùi
        {
            "id": "fs_d2_20_2",
            "day": "2026-11-20",
            "slot": "08:00",
            "series": "fs",
            "lane": "nam_sinh_menh",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "amber",
            "chip": "BẢN MỆNH · MÀU HỢP MỆNH",
            "title_html": '<span class="l s">SINH NĂM 1991 TÂN MÙI</span><span class="l gold">MỆNH GÌ, HỢP MÀU GÌ?</span>',
            "title": "Sinh năm 1991 Tân Mùi mệnh gì, hợp màu gì?",
            **FMN.menh_fields(P91["hanh"], 1991, "Tân Mùi", "Mùi", "một chín chín một", P91["nap_am"], "tức đất ven đường"),
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "yeartable_lookup",
            "hypothesis": "loop_yeartable_lookup",
            "batch_id": BATCH,
        },

        # 7. 20/11 12:00 UTC (19:00 VN) - yeartable: 1993 Quý Dậu
        {
            "id": "fs_d2_20_3",
            "day": "2026-11-20",
            "slot": "12:00",
            "series": "fs",
            "lane": "nam_sinh_menh",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "navy",
            "chip": "BẢN MỆNH · MÀU HỢP MỆNH",
            "title_html": '<span class="l s">SINH NĂM 1993 QUÝ DẬU</span><span class="l gold">MỆNH GÌ, HỢP MÀU GÌ?</span>',
            "title": "Sinh năm 1993 Quý Dậu mệnh gì, hợp màu gì?",
            **FMN.menh_fields(P93["hanh"], 1993, "Quý Dậu", "Dậu", "một chín chín ba", P93["nap_am"], "tức vàng mũi kiếm"),
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "yeartable_lookup",
            "hypothesis": "loop_yeartable_lookup",
            "batch_id": BATCH,
        },

        # 8. 20/11 15:00 UTC (22:00 VN) - yeartable: 1997 Đinh Sửu
        {
            "id": "fs_d2_20_4",
            "day": "2026-11-20",
            "slot": "15:00",
            "series": "fs",
            "lane": "nam_sinh_menh",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "navy",
            "chip": "BẢN MỆNH · MÀU HỢP MỆNH",
            "title_html": '<span class="l s">SINH NĂM 1997 ĐINH SỬU</span><span class="l gold">MỆNH GÌ, HỢP MÀU GÌ?</span>',
            "title": "Sinh năm 1997 Đinh Sửu mệnh gì, hợp màu gì?",
            **FMN.menh_fields(P97["hanh"], 1997, "Đinh Sửu", "Sửu", "một chín chín bảy", P97["nap_am"], "tức nước dưới khe"),
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "yeartable_lookup",
            "hypothesis": "loop_yeartable_lookup",
            "batch_id": BATCH,
        },

        # ================================================================ 21/11 (3 short)
        # 9. 21/11 04:30 UTC (11:30 VN) - month_sheet: Tháng 12/2026 khai trương
        {
            "id": "fs_d2_21_1",
            "day": "2026-11-21",
            "slot": "04:30",
            "series": "fs",
            "lane": "lich",
            "style": "month_sheet",
            "format_subtag": "month_sheet",
            "theme": "navy",
            "kicker": "KHAI TRƯƠNG · MỞ HÀNG CUỐI NĂM",
            "title": f"Tháng 12 năm 2026: {FMN.so_doc(len(KT_DAYS))} ngày tốt mở hàng đón tài lộc",
            "title_main": "THÁNG 12 NĂM 2026",
            "title_gold": "NGÀY TỐT KHAI TRƯƠNG",
            "subchip_text": f"{len(KT_DAYS)} NGÀY MỞ HÀNG ĐẸP · {_kt_chip(KT_DAYS)} THÁNG 12",
            "legend_text": "Vàng: ngày mở hàng đẹp · Đỏ: ngày kỵ · Tham khảo",
            "subfoot_text": "DỪNG HÌNH LƯU LẠI LỊCH MỞ HÀNG NHÉ",
            "days": DAYS_DEC_KT,
            "offset": DEC_OFFSET,
            "script": [
                "Tháng mười hai này,",
                f"có {FMN.so_doc(len(KT_DAYS))} ngày hoàng đạo không vướng kỵ, hợp để khai trương, mở hàng cuối năm.",
                f"Đó là {FMN.list_ngay_doc(KT_DAYS)} dương lịch, {FMN.truc_cau(KT_TRUC)}.",
                "Khởi sự vào ngày lành mang ý nghĩa đón may mắn, cầu việc kinh doanh thuận lợi.",
                "Dừng hình lưu lại lịch mở hàng nhé.",
            ],
            "display_script": [
                "Tháng 12 năm 2026,",
                f"có {len(KT_DAYS)} ngày hoàng đạo không vướng kỵ, hợp để khai trương, mở hàng cuối năm.",
                f"Đó là {', '.join('ngày ' + str(d) for d in KT_DAYS[:-1])} và ngày {KT_DAYS[-1]} dương lịch, {FMN.truc_cau(KT_TRUC)}." if len(KT_DAYS) > 1 else f"Đó là ngày {KT_DAYS[0]} dương lịch, {FMN.truc_cau(KT_TRUC)}.",
                "Khởi sự vào ngày lành mang ý nghĩa đón may mắn, cầu việc kinh doanh thuận lợi.",
                "Dừng hình lưu lại lịch mở hàng nhé.",
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "search_intent",
            "narrative_structure": "month_sheet_scan",
            "hypothesis": "loop_month_sheet_lookup",
            "batch_id": BATCH,
        },

        # 10. 21/11 08:00 UTC (15:00 VN) - yeartable: 1994 Giáp Tuất
        {
            "id": "fs_d2_21_2",
            "day": "2026-11-21",
            "slot": "08:00",
            "series": "fs",
            "lane": "nam_sinh_menh",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "red",
            "chip": "BẢN MỆNH · MÀU HỢP MỆNH",
            "title_html": '<span class="l s">SINH NĂM 1994 GIÁP TUẤT</span><span class="l gold">MỆNH GÌ, HỢP MÀU GÌ?</span>',
            "title": "Sinh năm 1994 Giáp Tuất mệnh gì, hợp màu gì?",
            **FMN.menh_fields(P94["hanh"], 1994, "Giáp Tuất", "Tuất", "một chín chín tư", P94["nap_am"], "tức lửa trên núi"),
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "yeartable_lookup",
            "hypothesis": "loop_yeartable_lookup",
            "batch_id": BATCH,
        },

        # 11. 21/11 15:00 UTC (22:00 VN) - yeartable: Năm 2027: tuổi nào thuận đường công danh sự nghiệp?
        {
            "id": "fs_d2_21_3",
            "day": "2026-11-21",
            "slot": "15:00",
            "series": "fs",
            "lane": "tuoi",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "jade",
            "chip": "CỬU DIỆU 2027 · CÁT TINH",
            "title_html": '<span class="l s">CÔNG DANH 2027</span><span class="l gold">THÁI DƯƠNG VÀ THÁI ÂM</span>',
            "title": "Năm 2027: tuổi nào thuận đường công danh sự nghiệp?",
            "rows": [
                ("NAM MẠNG", "SAO THÁI DƯƠNG", SAO_THAI_DUONG_NAM),
                ("NỮ MẠNG", "SAO THÁI ÂM", SAO_THAI_AM_NU),
            ],
            "script": [
                "Năm Đinh Mùi,",
                "nam mệnh sao Thái Dương và nữ mệnh sao Thái Âm được xem là đón nhiều thuận lợi.",
                "Theo truyền thống, đây là hai cát tinh chủ về công danh sáng tỏ và gia đạo an vui.",
                "Bảng phân định rõ năm sinh của cả nam và nữ mạng hiển thị trên màn hình.",
                "Dừng hình tra cứu năm sinh của bạn nhé.",
            ],
            "display_script": [
                "Năm Đinh Mùi 2027,",
                "nam mệnh sao Thái Dương và nữ mệnh sao Thái Âm được xem là đón nhiều thuận lợi.",
                "Theo truyền thống, đây là hai cát tinh chủ về công danh sáng tỏ và gia đạo an vui.",
                "Bảng phân định rõ năm sinh của cả nam và nữ mạng hiển thị trên màn hình.",
                "Dừng hình tra cứu năm sinh của bạn nhé.",
            ],
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "yeartable_lookup",
            "hypothesis": "loop_yeartable_lookup",
            "batch_id": BATCH,
        },

        # ================================================================ 22/11 (4 short)
        # 12. 22/11 04:30 UTC (11:30 VN) - month_sheet: Tháng 11 âm những ngày hoàng đạo đẹp nhất
        {
            "id": "fs_d2_22_1",
            "day": "2026-11-22",
            "slot": "04:30",
            "series": "fs",
            "lane": "lich",
            "style": "month_sheet",
            "format_subtag": "month_sheet",
            "theme": "navy",
            "kicker": "LỊCH VẠN NIÊN · THÁNG 11 ÂM",
            "title": f"Tháng 11 âm lịch: {len(L11_BIG_DAYS)} ngày hoàng đạo hợp việc lớn",
            "title_main": "THÁNG 11 ÂM LỊCH",
            "title_gold": f"{len(L11_BIG_DAYS)} NGÀY HỢP VIỆC LỚN",
            "subchip_text": f"{_kt_chip(L11_BIG_DAYS, am=True)} ÂM LỊCH · TRỰC {' / '.join(t.upper() for t in L11_BIG_TRUC)}",
            "legend_text": "Vàng: ngày hợp việc lớn · Đỏ: ngày kỵ · Tham khảo",
            "subfoot_text": "DỪNG HÌNH LƯU LẠI NGÀY ĐẸP NHÉ",
            "days": DAYS_LUNAR11_SPECIAL,
            "offset": L11_OFFSET,
            "script": [
                "Tháng mười một âm,",
                f"có {FMN.so_doc(len(L11_BIG_DAYS))} ngày hoàng đạo hợp việc lớn như cưới hỏi, khai trương, làm nhà.",
                f"Đó là {FMN.list_ngay_doc(L11_BIG_DAYS, am=True)} âm lịch, {FMN.truc_cau(L11_BIG_TRUC)}.",
                "Các ngày này không vướng Tam Nương, Nguyệt kỵ hay Dương Công theo sách xưa.",
                "Dừng hình lưu lại ngày đẹp bạn nhé.",
            ],
            "display_script": [
                "Tháng 11 âm lịch,",
                f"có {len(L11_BIG_DAYS)} ngày hoàng đạo hợp việc lớn như cưới hỏi, khai trương, làm nhà.",
                f"Đó là {_kt_chip(L11_BIG_DAYS, am=True).lower()} âm lịch, {FMN.truc_cau(L11_BIG_TRUC)}.",
                "Các ngày này không vướng Tam Nương, Nguyệt kỵ hay Dương Công theo sách xưa.",
                "Dừng hình lưu lại ngày đẹp bạn nhé.",
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "search_intent",
            "narrative_structure": "month_sheet_scan",
            "hypothesis": "loop_month_sheet_lookup",
            "batch_id": BATCH,
        },

        # 13. 22/11 08:00 UTC (15:00 VN) - month_sheet: Tháng 1/2027 bảng tra ngày hoàng đạo trước Tết
        {
            "id": "fs_d2_22_2",
            "day": "2026-11-22",
            "slot": "08:00",
            "series": "fs",
            "lane": "lich",
            "style": "month_sheet",
            "format_subtag": "month_sheet",
            "theme": "navy",
            "kicker": "LỊCH ÂM DƯƠNG · THÁNG 1/2027",
            "title": "Tháng 1 năm 2027: bảng tra ngày hoàng đạo trước Tết",
            "title_main": "THÁNG 1 NĂM 2027",
            "title_gold": "BẢNG TRA NGÀY HOÀNG ĐẠO",
            "subchip_text": f"{N_HD_JAN27} NGÀY HOÀNG ĐẠO · {N_GOOD_JAN27} NGÀY THUẬN LỢI",
            "legend_text": FMN.LEGEND_HD,
            "subfoot_text": "DỪNG HÌNH LƯU LẠI LỊCH GIÁP TẾT NHÉ",
            "days": DAYS_JAN27_2027,
            "offset": JAN27_OFFSET,
            "script": [
                "Tháng một dương lịch,",
                f"tháng giáp Tết có {FMN.so_doc(N_HD_JAN27)} ngày hoàng đạo, trong đó {FMN.so_doc(N_GOOD_JAN27)} ngày thuận lợi không vướng kỵ.",
                LINE_O_LICH,
                "Bảng tra cứu giúp bạn chuẩn bị chu đáo mọi công việc đón Tết Đinh Mùi.",
                "Dừng hình lưu lại lịch tháng một nhé.",
            ],
            "display_script": [
                "Tháng 1 năm 2027,",
                f"tháng giáp Tết có {N_HD_JAN27} ngày hoàng đạo, trong đó {N_GOOD_JAN27} ngày thuận lợi không vướng kỵ.",
                LINE_O_LICH,
                "Bảng tra cứu giúp bạn chuẩn bị chu đáo mọi công việc đón Tết Đinh Mùi.",
                "Dừng hình lưu lại lịch tháng 1 nhé.",
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "search_intent",
            "narrative_structure": "month_sheet_scan",
            "hypothesis": "loop_month_sheet_lookup",
            "batch_id": BATCH,
        },

        # 14. 22/11 12:00 UTC (19:00 VN) - yeartable: Năm 2027: những tuổi hợp khai trương đón lộc Đinh Mùi
        {
            "id": "fs_d2_22_3",
            "day": "2026-11-22",
            "slot": "12:00",
            "series": "fs",
            "lane": "tuoi",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "amber",
            "chip": "HOANG ỐC 2027 · TỨ TẤN TÀI",
            "title_html": '<span class="l s">MỞ HÀNG 2027</span><span class="l gold">TUỔI ĐÓN TỨ TẤN TÀI</span>',
            "title": "Năm 2027: những tuổi hợp khai trương đón lộc Đinh Mùi",
            "rows": [
                ("1964 - 1988", "TÀI LỘC DỒI DÀO", [1964, 1973, 1982, 1988]),
                ("1997 - 2009", "TÀI LỘC DỒI DÀO", [1997, 2000, 2006, 2009]),
            ],
            "script": [
                "Năm Đinh Mùi,",
                "các năm sinh này thuộc cung Tứ Tấn Tài, cung tốt chủ về tài lộc và kinh doanh thuận lợi.",
                "Theo dân gian, đây là những tuổi rất hợp để mở mang cửa hàng, khởi sự làm ăn.",
                "Bảng phân theo từng giai đoạn năm sinh hiển thị chi tiết trên màn hình.",
                "Dừng hình tra cứu năm sinh đón lộc nhé.",
            ],
            "display_script": [
                "Năm Đinh Mùi 2027,",
                "các năm sinh này thuộc cung Tứ Tấn Tài, cung tốt chủ về tài lộc và kinh doanh thuận lợi.",
                "Theo dân gian, đây là những tuổi rất hợp để mở mang cửa hàng, khởi sự làm ăn.",
                "Bảng phân theo từng giai đoạn năm sinh hiển thị chi tiết trên màn hình.",
                "Dừng hình tra cứu năm sinh đón lộc nhé.",
            ],
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "yeartable_lookup",
            "hypothesis": "loop_yeartable_lookup",
            "batch_id": BATCH,
        },

        # 15. 22/11 15:00 UTC (22:00 VN) - yeartable: Năm 2027: các năm sinh hợp mở rộng làm ăn
        {
            "id": "fs_d2_22_4",
            "day": "2026-11-22",
            "slot": "15:00",
            "series": "fs",
            "lane": "tuoi",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "jade",
            "chip": "HOANG ỐC 2027 · AN CƯ HƯNG THỊNH",
            "title_html": '<span class="l s">KHỞI SỰ 2027</span><span class="l gold">NHẤT CÁT VÀ NHÌ NGHI</span>',
            "title": "Năm 2027: các năm sinh hợp mở rộng làm ăn",
            "rows": [
                ("NHẤT CÁT", "AN CƯ THỊNH VƯỢNG", HO_NHAT_CAT_27),
                ("NHÌ NGHI", "GIA ĐẠO HƯNG THỊNH", HO_NHI_NGHI_27),
            ],
            "script": [
                "Năm Đinh Mùi,",
                "các tuổi thuộc cung Nhất Cát và Nhì Nghi được xem là vững vàng gia đạo và công việc.",
                "Theo sách xưa, khởi sự vào năm thuận bản mệnh giúp công việc hanh thông, bền vững.",
                "Bảng tra cứu đầy đủ các năm sinh hiển thị rõ ràng trên màn hình.",
                "Dừng hình kiểm tra năm sinh của bạn nhé.",
            ],
            "display_script": [
                "Năm Đinh Mùi 2027,",
                "các tuổi thuộc cung Nhất Cát và Nhì Nghi được xem là vững vàng gia đạo và công việc.",
                "Theo sách xưa, khởi sự vào năm thuận bản mệnh giúp công việc hanh thông, bền vững.",
                "Bảng tra cứu đầy đủ các năm sinh hiển thị rõ ràng trên màn hình.",
                "Dừng hình kiểm tra năm sinh của bạn nhé.",
            ],
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "yeartable_lookup",
            "hypothesis": "loop_yeartable_lookup",
            "batch_id": BATCH,
        },
    ]
    return plan


# ---------------------------------------------------------------- GUARD
def plan_guard(plan: list[dict]) -> None:
    assert len(plan) == 15, f"Tổng số bài phải là 15, got {len(plan)}"
    n_yt = sum(1 for it in plan if it["style"] == "yeartable")
    n_ms = sum(1 for it in plan if it["style"] == "month_sheet")
    assert n_yt == 10, f"Số bài yeartable phải là 10, got {n_yt}"
    assert n_ms == 5, f"Số bài month_sheet phải là 5, got {n_ms}"

    # Kiểm tra phân bổ ngày
    days_count = {}
    for it in plan:
        d = it["day"]
        days_count[d] = days_count.get(d, 0) + 1
    assert days_count == {
        "2026-11-18": 1,
        "2026-11-19": 3,
        "2026-11-20": 4,
        "2026-11-21": 3,
        "2026-11-22": 4,
    }, f"Phân bổ ngày sai: {days_count}"

    # Kiểm tra quy tắc tên con giáp (<= 3 tên chi mỗi câu)
    chis = ("Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi")
    for it in plan:
        for idx, line in enumerate(it["script"]):
            found = [c for c in chis if c in line]
            assert len(found) <= 3, f"Quá 3 tên chi ở {it['id']} câu {idx + 1}: {found}"

    print(f"PLAN GUARD: PASS (15/15 bài chuẩn luật)")


# ---------------------------------------------------------------- PACKAGING
def write_packaging(plan: list[dict]) -> None:
    for it in plan:
        pkg_file = PKG_DIR / f"{it['id']}.json"
        title = it["title"]
        insight = f"{title}. Bảng tra cứu phong thủy và tử vi truyền thống, nội dung mang tính tham khảo chiêm nghiệm."
        if it.get("hanh"):  # mô tả màu sinh từ cùng bảng HANH_MAU với chip và lời đọc
            insight += " " + FMN.mau_mo_ta(it["hanh"])
        tags = [
            "tu vi",
            "phong thuy",
            "tra nam sinh",
            "nam 2027",
            "dinh mui 2027",
            "van han",
        ]
        tags_vi = [
            "tử vi",
            "phong thủy",
            "tra năm sinh",
            "năm 2027",
            "Đinh Mùi 2027",
            "vận hạn",
        ]
        hashtags = ["#Shorts", "#tuvi", "#phongthuy", "#dinhmui2027"]
        cta = "Bạn sinh năm nào? Dừng hình tra cứu và để lại bình luận nhé."

        pkg = {
            "insight": insight,
            "hashtags": hashtags,
            "tags": tags,
            "tags_vi": tags_vi,
            "cta": cta,
        }
        pkg_file.write_text(json.dumps(pkg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Packaging written: {len(plan)} files -> {PKG_DIR}")


# ---------------------------------------------------------------- RENDER
def render_one(item: dict) -> None:
    rid = item["id"]
    meta_file, mp4 = RENDER_DIR / f"{rid}.render.json", RENDER_DIR / f"{rid}.mp4"
    if mp4.exists() and meta_file.exists():
        print(f"[{rid}] đã có mp4 + meta, bỏ qua render lại", flush=True)
        return

    txt, wav = RENDER_DIR / f"{rid}.txt", RENDER_DIR / f"{rid}.wav"
    txt.write_text("\n".join(item["script"]) + "\n", encoding="utf-8")
    if not wav.exists():
        assert R.render_tts(txt, wav, item["script"], voice="Sơn"), f"TTS lỗi {rid}"
    raw = json.loads(wav.with_suffix(".json").read_text(encoding="utf-8"))["segments"]
    last_end = raw[-1]["end"]

    # Bảo đảm tổng thời lượng nằm trong 21 - 27 giây
    final_dur = max(21.4, round(last_end + 4.2, 2))
    if final_dur > 26.8:
        final_dur = 26.8
    item["dur"] = final_dur

    # Kiểm tra câu 1 <= 2.5s
    c1_dur = raw[0]["end"] - raw[0]["start"]
    print(f"[{rid}] Câu 1: {c1_dur:.2f}s ({raw[0]['start']:.2f} -> {raw[0]['end']:.2f}) | audio: {last_end:.2f}s | dur: {final_dur:.2f}s")
    assert c1_dur <= 2.5, f"Câu 1 {c1_dur:.2f}s vượt 2.5s ở {rid}"

    disp = item.get("display_script") or item["script"]
    segs = [
        {"start": s["start"], "end": s["end"], "text": disp[i] if i < len(disp) else s["text"]}
        for i, s in enumerate(raw)
    ]
    if item["style"] == "yeartable":
        html = build_yeartable_custom(item, final_dur, segs)
    else:
        html = build_month_sheet_generic(item, final_dur, segs)
    comp = f"_tb_{rid}.html"
    (COMP / comp).write_text(html, encoding="utf-8")

    # QA trước render
    ovf_res = subprocess.run(
        [sys.executable, str(ROOT / "hf_qa.py"), "--overflow", str(COMP / comp)],
        capture_output=True,
        text=True,
    )
    assert "ĐẠT" in ovf_res.stdout, f"QA overflow thất bại ở {rid}:\n{ovf_res.stdout}\n{ovf_res.stderr}"

    ctr_res = subprocess.run(
        [sys.executable, str(ROOT / "hf_qa.py"), "--contrast", str(COMP / comp)],
        capture_output=True,
        text=True,
    )
    assert "ĐẠT" in ctr_res.stdout, f"QA contrast thất bại ở {rid}:\n{ctr_res.stdout}\n{ctr_res.stderr}"
    print(f"[{rid}] QA overflow: ĐẠT | QA contrast: ĐẠT")

    silent = RENDER_DIR / f"{rid}_silent.mp4"
    silent.unlink(missing_ok=True)
    mp4.unlink(missing_ok=True)

    cmd = (
        f'export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1; nvm use 22 >/dev/null 2>&1; '
        f'cd "{HF}" && npx --yes hyperframes@0.8.75 render . -c compositions/{comp} --output "{silent}" '
        f"--quality looks --fps 30 --quiet"
    )
    pr = subprocess.run(["/bin/bash", "-lc", cmd], capture_output=True, text=True, timeout=1200)
    assert pr.returncode == 0 and silent.exists(), f"render lỗi {rid}: " + (pr.stdout + pr.stderr)[-800:]

    bgm = ROOT / "bgm" / item["bgm_file"]
    assert bgm.exists()
    vl, bl = P.measure_lufs(wav), P.measure_lufs(bgm)
    gain = 10 ** ((vl - 20.0 - bl) / 20.0)
    flt = (
        f"[1:a]apad[v];[2:a]volume={gain:.4f},afade=t=out:st={final_dur - 2.5:.2f}:d=2.5[m];"
        f"[v][m]amix=inputs=2:duration=first:normalize=0[a]"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(silent),
            "-i",
            str(wav),
            "-stream_loop",
            "-1",
            "-i",
            str(bgm),
            "-filter_complex",
            flt,
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-t",
            str(final_dur),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(mp4),
        ],
        check=True,
    )
    silent.unlink(missing_ok=True)
    mix = P.measure_lufs(mp4)

    pr = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
        capture_output=True,
        text=True,
    )
    real = float(pr.stdout.strip())
    t_last, t_hold = real - 0.25, max(0.1, real - 3.0)
    ims = []
    for tt in (t_hold, t_last):
        f = RENDER_DIR / f"_st_{rid}.png"
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-ss", str(tt), "-vframes", "1", str(f)],
            check=True,
        )
        ims.append(Image.open(f).convert("L").copy())
        f.unlink(missing_ok=True)
    diff = ImageStat.Stat(ImageChops.difference(*ims)).mean[0]
    assert diff < 1.0, f"{rid} khung cuối không tĩnh {diff}"

    f1080 = RENDER_DIR / f"frame_last_1080_{rid}.png"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-ss", str(t_last), "-vframes", "1", str(f1080)],
        check=True,
    )
    t_mid = min(last_end * 0.8, last_end - 0.3)
    f_mid = RENDER_DIR / f"frame_mid_1080_{rid}.png"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(mp4),
            "-ss",
            f"{t_mid:.2f}",
            "-vframes",
            "1",
            str(f_mid),
        ],
        check=True,
    )
    f0 = RENDER_DIR / f"frame_0_1080_{rid}.png"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-ss", "0.05", "-vframes", "1", str(f0)],
        check=True,
    )

    meta = {
        "id": rid,
        "style": item["style"],
        "day": item["day"],
        "slot": item["slot"],
        "duration_s": real,
        "audio_s": last_end,
        "c1_s": round(c1_dur, 2),
        "hold_diff": round(diff, 4),
        "lufs_mix": round(mix, 1),
        "rendered_at": dt.datetime.now().isoformat(),
        "ok": True,
    }
    meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{rid}] xong {real:.1f}s c1={c1_dur:.2f}s hold_diff={diff:.4f} mix={mix:.1f} LUFS", flush=True)


def export_preview(plan: list[dict]) -> None:
    cw, ch = 360, 640
    sheet = Image.new("RGB", (cw * len(plan), ch * 3 + 50), (10, 12, 18))
    dr = ImageDraw.Draw(sheet)
    for i, it in enumerate(plan):
        rid = it["id"]
        for row, kind in enumerate(("0", "mid", "last")):
            f = RENDER_DIR / (
                f"frame_0_1080_{rid}.png"
                if kind == "0"
                else f"frame_mid_1080_{rid}.png"
                if kind == "mid"
                else f"frame_last_1080_{rid}.png"
            )
            if f.exists():
                sheet.paste(
                    Image.open(f).convert("RGB").resize((cw, ch), Image.Resampling.LANCZOS),
                    (i * cw, 50 + row * ch),
                )
        dr.text((i * cw + 8, 12), f"{it['id']} {it['day'][5:]} {it['slot']}", fill=(253, 230, 138))

    preview_path = RENDER_DIR / "preview_fs_dot2.jpg"
    sheet.save(preview_path, quality=90)
    sheet.save(ROOT_RENDER_DIR / "preview_fs_dot2.jpg", quality=90)
    print("Preview sheet saved:", preview_path)

    # Bản 168px cho Lead soát độ đọc trên mobile
    w_168 = 168 * len(plan)
    h_168 = round((ch * 3 + 50) * (168 / cw))
    sheet_168 = sheet.resize((w_168, h_168), Image.Resampling.LANCZOS)
    sheet_168.save(RENDER_DIR / "preview_fs_dot2_168.jpg", quality=90)
    sheet_168.save(ROOT_RENDER_DIR / "preview_fs_dot2_168.jpg", quality=90)
    print("Preview 168 saved:", RENDER_DIR / "preview_fs_dot2_168.jpg")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--plan-only", action="store_true")
    a = ap.parse_args()

    plan = make_plan()
    plan_guard(plan)

    clean_plan = []
    for it in plan:
        cp = {k: v for k, v in it.items()}
        clean_plan.append(cp)

    validate(clean_plan)
    PLAN_FILE.write_text(json.dumps(clean_plan, ensure_ascii=False, indent=2), encoding="utf-8")
    (RENDER_DIR / "plan_fs_dot2_1622.json").write_text(
        json.dumps(clean_plan, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("plan ->", PLAN_FILE)

    write_packaging(plan)

    if not a.plan_only:
        for it in plan:
            if a.only and it["id"] not in a.only:
                continue
            render_one(it)
        for it in clean_plan:
            mf = RENDER_DIR / f"{it['id']}.render.json"
            if mf.exists():
                it["dur"] = round(json.loads(mf.read_text(encoding="utf-8"))["duration_s"], 2)
        PLAN_FILE.write_text(json.dumps(clean_plan, ensure_ascii=False, indent=2), encoding="utf-8")
        (RENDER_DIR / "plan_fs_dot2_1622.json").write_text(
            json.dumps(clean_plan, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        export_preview(plan)
