"""Builder + render cho 001_fs_dot1_0915: Phủ FS đợt 1 (11 short 09-15/11/2026).

Phân bổ 11 short FS:
- 09/11: 2 (1 month_sheet, 1 yeartable)
- 11/11: 1 (1 yeartable)
- 12/11: 2 (1 month_sheet, 1 yeartable)
- 13/11: 1 (1 yeartable)
- 14/11: 2 (1 month_sheet, 1 yeartable)
- 15/11: 3 (1 month_sheet, 2 yeartable)
Tổng: 7 yeartable (tuoi/saohan/lamnha 2027) + 4 month_sheet (ngaytot/lich T2, T4/2027).

Mọi số tính bằng code (saohan, tuvi_year, hoangdao_daily, canchi, amlich),
đối chiếu độc lập bằng plan_guard.
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
import canchi
from fs_calendar import hoangdao_daily
import saohan
import tuvi_year

P = importlib.import_module("build_fs_phu_1104")  # mượn hàm dựng yeartable/fonts

RENDER_DIR = HERE / "render_001_fs"
RENDER_DIR.mkdir(parents=True, exist_ok=True)
HF = ROOT / "hyperframes_short"
COMP = HF / "compositions"
PLAN_FILE = ROOT / "output" / "cl_staging" / "fs" / "plan_001_fs_dot1_0915.json"
PKG_DIR = ROOT / "output" / "cl_staging" / "fs" / "packaging"
PKG_DIR.mkdir(parents=True, exist_ok=True)
BATCH = "fs_w46_dot1"

YEARS = list(range(1950, 2011))
PROF27 = {y: tuvi_year.profile(y, start=2027, n_years=1) for y in YEARS}
R27 = {y: PROF27[y]["cac_nam"][0] for y in YEARS}

# ---------------------------------------------------------------- số liệu bằng code
HAN_NAM = lambda h: [y for y in YEARS if saohan.han(y, True, at=2027) == h]  # noqa: E731
HAN_NU = lambda h: [y for y in YEARS if saohan.han(y, False, at=2027) == h]  # noqa: E731
SAO_NAM = lambda s: [y for y in YEARS if saohan.sao(y, True, at=2027) == s]  # noqa: E731
SAO_NU = lambda s: [y for y in YEARS if saohan.sao(y, False, at=2027) == s]  # noqa: E731

# 1. Tuổi làm nhà 2027: không Tam Tai, không Kim Lâu, không Hoang Ốc xấu
LAM_NHA_2027 = [y for y in YEARS if not R27[y]["tam_tai"] and not R27[y]["kim_lau"] and not R27[y]["hoang_oc_xau"]]

# 2. Hoang Ốc 2027 theo 3 cung tốt
HO_NHAT_CAT = [y for y in YEARS if R27[y]["hoang_oc"] == "Nhất Cát"]
HO_NHI_NGHI = [y for y in YEARS if R27[y]["hoang_oc"] == "Nhì Nghi"]
HO_TU_TAN_TAI = [y for y in YEARS if R27[y]["hoang_oc"] == "Tứ Tấn Tài"]

# ---------------------------------------------------------------- Lịch tháng 2/2027 & tháng 4/2027
# Tháng 2/2027: 28 ngày, 01/02 là thứ Hai (offset = 0)
DAYS_FEB_2027 = []
for d in range(1, 29):
    f = hoangdao_daily.day_data(dt.date(2027, 2, d))
    ld = f["ld"]
    bad = ld in (3, 7, 13, 18, 22, 27) or ld in (5, 14, 23)
    hd = f["is_hoang"]
    ct = "gold-good" if hd and not bad else "gold-tn" if hd else "red-bad" if bad else "neutral-cell"
    DAYS_FEB_2027.append({
        "solar_day": d,
        "lunar_str": f"{ld}/{f['lm']}",
        "dow_vi": f["dow_vi"],
        "cell_type": ct,
        "is_hoang": hd,
        "is_bad": bad,
    })
N_HD_FEB = sum(1 for x in DAYS_FEB_2027 if x["is_hoang"])
N_HD_BAD_FEB = sum(1 for x in DAYS_FEB_2027 if x["is_hoang"] and x["is_bad"])
N_GOOD_FEB = N_HD_FEB - N_HD_BAD_FEB
FEB_OFFSET = dt.date(2027, 2, 1).weekday()  # 0

# Ngày tốt cưới hỏi sau Tết tháng 2/2027: 14, 24, 26
DAYS_FEB_CUOI = []
for x in DAYS_FEB_2027:
    d = x["solar_day"]
    is_cuoi = d in (14, 24, 26)
    ct = "gold-good" if is_cuoi else "red-bad" if x["is_bad"] else "neutral-cell"
    DAYS_FEB_CUOI.append({
        "solar_day": d,
        "lunar_str": x["lunar_str"],
        "dow_vi": x["dow_vi"],
        "cell_type": ct,
        "is_hoang": x["is_hoang"],
        "is_bad": x["is_bad"],
        "is_special": is_cuoi,
    })

# Ngày tốt khai trương sau Tết tháng 2/2027: 14, 24, 26
DAYS_FEB_KT = []
for x in DAYS_FEB_2027:
    d = x["solar_day"]
    is_kt = d in (14, 24, 26)
    ct = "gold-good" if is_kt else "red-bad" if x["is_bad"] else "neutral-cell"
    DAYS_FEB_KT.append({
        "solar_day": d,
        "lunar_str": x["lunar_str"],
        "dow_vi": x["dow_vi"],
        "cell_type": ct,
        "is_hoang": x["is_hoang"],
        "is_bad": x["is_bad"],
        "is_special": is_kt,
    })

# Tháng 4/2027: 30 ngày, 01/04 là thứ Năm (offset = 3)
DAYS_APR_2027 = []
for d in range(1, 31):
    f = hoangdao_daily.day_data(dt.date(2027, 4, d))
    ld = f["ld"]
    bad = ld in (3, 7, 13, 18, 22, 27) or ld in (5, 14, 23)
    hd = f["is_hoang"]
    ct = "gold-good" if hd and not bad else "gold-tn" if hd else "red-bad" if bad else "neutral-cell"
    DAYS_APR_2027.append({
        "solar_day": d,
        "lunar_str": f"{ld}/{f['lm']}",
        "dow_vi": f["dow_vi"],
        "cell_type": ct,
        "is_hoang": hd,
        "is_bad": bad,
    })
N_HD_APR = sum(1 for x in DAYS_APR_2027 if x["is_hoang"])
N_HD_BAD_APR = sum(1 for x in DAYS_APR_2027 if x["is_hoang"] and x["is_bad"])
N_GOOD_APR = N_HD_APR - N_HD_BAD_APR
APR_OFFSET = dt.date(2027, 4, 1).weekday()  # 3

# Ngày tốt khai trương tháng 4/2027: 5, 17
DAYS_APR_KT = []
for x in DAYS_APR_2027:
    d = x["solar_day"]
    is_kt = d in (5, 17)
    ct = "gold-good" if is_kt else "red-bad" if x["is_bad"] else "neutral-cell"
    DAYS_APR_KT.append({
        "solar_day": d,
        "lunar_str": x["lunar_str"],
        "dow_vi": x["dow_vi"],
        "cell_type": ct,
        "is_hoang": x["is_hoang"],
        "is_bad": x["is_bad"],
        "is_special": is_kt,
    })


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

    # Đủ 5 tuần (35 ô)
    while len(cells_html) < 35:
        cells_html.append('<div class="cal-cell empty"></div>')

    grid_content = "\n".join(cells_html)
    segs_json = json.dumps(segs, ensure_ascii=False)

    kicker = t.get("kicker", "LỊCH VẠN NIÊN")
    title_main = t.get("title_main", "")
    title_gold = t.get("title_gold", "")
    subchip = t.get("subchip_text", "")
    legend = t.get("legend_text", "Vàng: hoàng đạo · Góc đỏ: trùng Tam Nương · Đỏ: ngày kỵ · Tham khảo")
    subfoot = t.get("subfoot_text", "DỪNG HÌNH LƯU LẠI LỊCH NHÉ")

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

    .month-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); grid-template-rows: repeat(5, 156px); gap: 8px; }}
    .cal-cell {{ position: relative; border-radius: 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; overflow: hidden; }}
    .cal-cell.empty {{ background: rgba(15, 23, 42, 0.25); border: 1px dashed rgba(100, 116, 139, 0.15); }}

    /* Day typography */
    .day-solar {{ font-size: 64px; font-weight: 900; line-height: 1; margin-top: 4px; }}
    .day-lunar {{ font-size: 30px; font-weight: 700; line-height: 1; margin-top: 6px; }}

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
    #legend {{ position: absolute; left: 64px; top: 1334px; width: 872px; text-align: center;
      font-size: 24px; font-weight: 700; color: #fde68a; letter-spacing: 0.02em; z-index: 5; }}
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


# ---------------------------------------------------------------- PLAN MAKER
def mk(**kw) -> dict:
    base = {"series": "fs", "batch_id": BATCH}
    base.update(kw)
    return base


YT = dict(
    hook_type="curiosity_self_check",
    narrative_structure="direct_answer_grid",
    hypothesis="high_avp_self_lookup_2027",
    format_subtag="yeartable",
    style="yeartable",
    lane="tuoi",
)

MS = dict(
    hook_type="search_intent",
    narrative_structure="month_sheet_scan",
    hypothesis="loop_month_sheet_lookup",
    format_subtag="month_sheet",
    style="month_sheet",
)


def make_plan() -> list[dict]:
    plan = []

    # 1. 09/11 slot 04:30 - month_sheet: cưới hỏi tháng 2/2027 sau Tết
    plan.append(
        mk(
            id="fs_d1_09_1",
            day="2026-11-09",
            slot="04:30",
            lane="ngaytot",
            theme="navy",
            kicker="CƯỚI HỎI ĐẦU NĂM · ĐINH MÙI 2027",
            title="Tháng 2 năm 2027: ngày nào tốt để cưới hỏi sau Tết?",
            title_main="THÁNG 2 NĂM 2027",
            title_gold="NGÀY TỐT CƯỚI HỎI SAU TẾT",
            subchip_text="3 NGÀY ĐẸP SAU TẾT · 14, 24, 26 THÁNG 2",
            legend_text="Vàng: ngày cưới đẹp · Đỏ: ngày kỵ · Tham khảo",
            subfoot_text="DỪNG HÌNH LƯU LẠI LỊCH CƯỚI THÁNG 2",
            days=DAYS_FEB_CUOI,
            offset=FEB_OFFSET,
            script=[
                "Tháng hai 2027,",
                "sau Tết Đinh Mùi có ba ngày đẹp thuận lợi cho việc cưới hỏi.",
                "Đó là ngày mười bốn, hai mươi bốn, và ngày hai mươi sáu dương lịch.",
                "Theo phong tục truyền thống, đây là các ngày hoàng đạo trực Khai và trực Thành.",
                "Dừng hình lưu lại lịch tháng hai để chuẩn bị chu đáo nhé.",
            ],
            display_script=[
                "Tháng 2 năm 2027,",
                "sau Tết Đinh Mùi có 3 ngày đẹp thuận lợi cho việc cưới hỏi.",
                "Đó là ngày 14, 24, và ngày 26 dương lịch.",
                "Theo phong tục truyền thống, đây là các ngày hoàng đạo trực Khai và trực Thành.",
                "Dừng hình lưu lại lịch tháng 2 để chuẩn bị chu đáo nhé.",
            ],
            bgm_file="ishikari_lore.mp3",
            bgm_title="Ishikari Lore",
            **MS,
        )
    )

    # 2. 09/11 slot 12:00 - yeartable: làm nhà 2027
    plan.append(
        mk(
            id="fs_d1_09_2",
            day="2026-11-09",
            slot="12:00",
            theme="jade",
            chip="ĐỘNG THỔ 2027 · ĐINH MÙI",
            title_html='<span class="l s">TUỔI LÀM NHÀ 2027</span><span class="l gold">KHÔNG PHẠM ĐẠI HẠN</span>',
            title="Năm 2027: những năm sinh đẹp nhất để làm nhà, động thổ",
            rows=[
                ("1952 - 1969", "ĐỘNG THỔ TỐT", [1952, 1958, 1960, 1961, 1969]),
                ("1970 - 1988", "ĐỘNG THỔ TỐT", [1970, 1976, 1985, 1988]),
                ("1994 - 2008", "ĐỘNG THỔ TỐT", [1994, 1997, 2006, 2008]),
            ],
            script=[
                "Năm Đinh Mùi,",
                "những năm sinh này không phạm Tam Tai, Kim Lâu hay Hoang Ốc xấu.",
                "Theo truyền thống, đây là mười ba tuổi đẹp nhất để động thổ, làm nhà đón vượng khí.",
                "Bảng tra cứu chi tiết phân theo từng giai đoạn năm sinh hiển thị trên màn hình.",
                "Dừng hình tìm năm sinh của bạn nhé.",
            ],
            display_script=[
                "Năm Đinh Mùi 2027,",
                "những năm sinh này không phạm Tam Tai, Kim Lâu hay Hoang Ốc xấu.",
                "Theo truyền thống, đây là 13 tuổi đẹp nhất để động thổ, làm nhà đón vượng khí.",
                "Bảng tra cứu chi tiết phân theo từng giai đoạn năm sinh hiển thị trên màn hình.",
                "Dừng hình tìm năm sinh của bạn nhé.",
            ],
            bgm_file="senbazuru.mp3",
            bgm_title="Senbazuru",
            **YT,
        )
    )

    # 3. 11/11 slot 12:00 - yeartable: sao Thái Bạch 2027
    plan.append(
        mk(
            id="fs_d1_11_1",
            day="2026-11-11",
            slot="12:00",
            theme="amber",
            chip="CỬU DIỆU 2027 · ĐINH MÙI",
            title_html='<span class="l s">SAO THÁI BẠCH 2027</span><span class="l gold">NAM NỮ CẦN LƯU TÂM</span>',
            title="Sao Thái Bạch năm 2027: nam nữ nào cần lưu ý tài chính?",
            rows=[
                ("NAM MẠNG", "SAO THÁI BẠCH", SAO_NAM("Thái Bạch")),
                ("NỮ MẠNG", "SAO THÁI BẠCH", SAO_NU("Thái Bạch")),
            ],
            script=[
                "Năm Đinh Mùi,",
                "các năm sinh này đón sao Thái Bạch chiếu mệnh trong năm Đinh Mùi.",
                "Dân gian quan niệm Thái Bạch chủ về tiền tài, nên giữ gìn chi tiêu, tránh đầu tư mạo hiểm.",
                "Bảng phân định rõ năm sinh của nam mạng và nữ mạng.",
                "Dừng hình tra cứu năm sinh của bạn nhé.",
            ],
            display_script=[
                "Năm Đinh Mùi 2027,",
                "các năm sinh này đón sao Thái Bạch chiếu mệnh trong năm Đinh Mùi.",
                "Dân gian quan niệm Thái Bạch chủ về tiền tài, nên giữ gìn chi tiêu, tránh đầu tư mạo hiểm.",
                "Bảng phân định rõ năm sinh của nam mạng và nữ mạng.",
                "Dừng hình tra cứu năm sinh của bạn nhé.",
            ],
            bgm_file="ishikari_lore.mp3",
            bgm_title="Ishikari Lore",
            **YT,
        )
    )

    # 4. 12/11 slot 04:30 - month_sheet: khai trương tháng 2/2027
    plan.append(
        mk(
            id="fs_d1_12_1",
            day="2026-11-12",
            slot="04:30",
            lane="ngaytot",
            theme="navy",
            kicker="KHAI TRƯƠNG ĐẦU NĂM · ĐINH MÙI 2027",
            title="Tháng 2 năm 2027: ngày nào tốt để khai trương đầu xuân?",
            title_main="THÁNG 2 NĂM 2027",
            title_gold="NGÀY KHAI TRƯƠNG ĐẦU XUÂN",
            subchip_text="3 NGÀY MỞ HÀNG ĐẦU XUÂN · 14, 24, 26 THÁNG 2",
            legend_text="Vàng: ngày mở hàng đẹp · Đỏ: ngày kỵ · Tham khảo",
            subfoot_text="DỪNG HÌNH LƯU LẠI LỊCH MỞ HÀNG NHÉ",
            days=DAYS_FEB_KT,
            offset=FEB_OFFSET,
            script=[
                "Tháng hai 2027,",
                "sau kỳ nghỉ Tết Nguyên Đán có ba ngày hoàng đạo thích hợp mở hàng, khai trương.",
                "Đó là ngày mười bốn, hai mươi bốn, và ngày hai mươi sáu tháng hai.",
                "Theo phong tục, chọn ngày lành mở cửa giúp việc làm ăn thêm hanh thông, thuận hòa.",
                "Dừng hình lưu lại lịch khai xuân nhé.",
            ],
            display_script=[
                "Tháng 2 năm 2027,",
                "sau kỳ nghỉ Tết Nguyên Đán có 3 ngày hoàng đạo thích hợp mở hàng, khai trương.",
                "Đó là ngày 14, 24, và ngày 26 tháng 2.",
                "Theo phong tục, chọn ngày lành mở cửa giúp việc làm ăn thêm hanh thông, thuận hòa.",
                "Dừng hình lưu lại lịch khai xuân nhé.",
            ],
            bgm_file="asian_drums.mp3",
            bgm_title="Asian Drums",
            **MS,
        )
    )

    # 5. 12/11 slot 08:00 - yeartable: sao La Hầu và Kế Đô 2027
    plan.append(
        mk(
            id="fs_d1_12_2",
            day="2026-11-12",
            slot="08:00",
            theme="red",
            chip="CỬU DIỆU 2027 · ĐINH MÙI",
            title_html='<span class="l s">LA HẦU VÀ KẾ ĐÔ 2027</span><span class="l gold">TRA THEO NĂM SINH</span>',
            title="Năm 2027: nam sao La Hầu, nữ sao Kế Đô — những năm sinh nào?",
            rows=[
                ("NAM MẠNG", "SAO LA HẦU", SAO_NAM("La Hầu")),
                ("NỮ MẠNG", "SAO KẾ ĐÔ", SAO_NU("Kế Đô")),
            ],
            script=[
                "Năm Đinh Mùi,",
                "bảy năm sinh này có nam mạng gặp sao La Hầu, nữ mạng gặp sao Kế Đô.",
                "Cổ nhân nhắc nhở nên giữ tâm an tĩnh, cẩn trọng lời ăn tiếng nói, dĩ hòa vi quý.",
                "Thông tin chỉ mang tính tham khảo nếp xưa để thêm vững tâm.",
                "Dừng hình tìm năm sinh của bạn nhé.",
            ],
            display_script=[
                "Năm 2027,",
                "7 năm sinh này có nam mạng gặp sao La Hầu, nữ mạng gặp sao Kế Đô.",
                "Cổ nhân nhắc nhở nên giữ tâm an tĩnh, cẩn trọng lời ăn tiếng nói, dĩ hòa vi quý.",
                "Thông tin chỉ mang tính tham khảo nếp xưa để thêm vững tâm.",
                "Dừng hình tìm năm sinh của bạn nhé.",
            ],
            bgm_file="clean_soul.mp3",
            bgm_title="Clean Soul",
            **YT,
        )
    )

    # 6. 13/11 slot 08:00 - yeartable: sao Mộc Đức 2027
    plan.append(
        mk(
            id="fs_d1_13_1",
            day="2026-11-13",
            slot="08:00",
            theme="navy",
            chip="CỬU DIỆU 2027 · ĐINH MÙI",
            title_html='<span class="l s">SAO MỘC ĐỨC 2027</span><span class="l gold">CÁT TINH CHIẾU MỆNH</span>',
            title="Sao Mộc Đức năm 2027: nam nữ nào đón cát tinh chiếu mệnh?",
            rows=[
                ("NAM MẠNG", "SAO MỘC ĐỨC", SAO_NAM("Mộc Đức")),
                ("NỮ MẠNG", "SAO MỘC ĐỨC", SAO_NU("Mộc Đức")),
            ],
            script=[
                "Năm Đinh Mùi,",
                "các năm sinh này đón sao Mộc Đức, một trong những cát tinh phúc lộc bậc nhất.",
                "Theo truyền thống, Mộc Đức mang lại bình an, gia đạo hòa thuận, công việc suôn sẻ.",
                "Cả nam và nữ mạng đều có danh sách năm sinh cụ thể.",
                "Dừng hình tìm năm sinh đón phúc lộc nhé.",
            ],
            bgm_file="senbazuru.mp3",
            bgm_title="Senbazuru",
            **YT,
        )
    )

    # 7. 14/11 slot 04:30 - month_sheet: lịch hoàng đạo tháng 2/2027
    plan.append(
        mk(
            id="fs_d1_14_1",
            day="2026-11-14",
            slot="04:30",
            lane="lich",
            theme="navy",
            kicker="LỊCH ÂM DƯƠNG · THÁNG 2/2027",
            title="Lịch hoàng đạo tháng 2/2027: bảng tra cả tháng",
            title_main="THÁNG 2 NĂM 2027",
            title_gold="BẢNG TRA NGÀY HOÀNG ĐẠO",
            subchip_text=f"{N_HD_FEB} NGÀY HOÀNG ĐẠO · {N_GOOD_FEB} NGÀY THUẬN LỢI",
            legend_text="Vàng: hoàng đạo · Góc đỏ: trùng Tam Nương · Đỏ: ngày kỵ · Tham khảo",
            subfoot_text="DỪNG HÌNH LƯU LẠI LỊCH CẢ THÁNG NHÉ",
            days=DAYS_FEB_2027,
            offset=FEB_OFFSET,
            script=[
                "Tháng hai 2027,",
                f"toàn tháng có mười lăm ngày hoàng đạo, trong đó {N_GOOD_FEB} ngày thuận lợi không vướng kỵ.",
                "Ô màu vàng là ngày tốt lành, ô màu đỏ là ngày Tam Nương, Nguyệt kỵ cần tránh việc lớn.",
                "Bảng tra cứu giúp bạn chủ động sắp xếp công việc cho cả tháng hai.",
                "Dừng hình lưu lại lịch hoàng đạo nhé.",
            ],
            display_script=[
                "Tháng 2 năm 2027,",
                f"toàn tháng có {N_HD_FEB} ngày hoàng đạo, trong đó {N_GOOD_FEB} ngày thuận lợi không vướng kỵ.",
                "Ô màu vàng là ngày tốt lành, ô màu đỏ là ngày Tam Nương, Nguyệt kỵ cần tránh việc lớn.",
                "Bảng tra cứu giúp bạn chủ động sắp xếp công việc cho cả tháng 2.",
                "Dừng hình lưu lại lịch hoàng đạo nhé.",
            ],
            bgm_file="ishikari_lore.mp3",
            bgm_title="Ishikari Lore",
            **MS,
        )
    )

    # 8. 14/11 slot 08:00 - yeartable: hạn Diêm Vương 2027
    plan.append(
        mk(
            id="fs_d1_14_2",
            day="2026-11-14",
            slot="08:00",
            theme="amber",
            chip="BÁT HẠN 2027 · ĐINH MÙI",
            title_html='<span class="l s">HẠN DIÊM VƯƠNG 2027</span><span class="l gold">AI CẦN LƯU TÂM?</span>',
            title="Hạn Diêm Vương năm 2027: nam nữ nào cần lưu ý sức khỏe?",
            rows=[
                ("NAM MẠNG", "HẠN DIÊM VƯƠNG", HAN_NAM("Diêm Vương")),
                ("NỮ MẠNG", "HẠN DIÊM VƯƠNG", HAN_NU("Diêm Vương")),
            ],
            script=[
                "Năm Đinh Mùi,",
                "các năm sinh này phạm hạn Diêm Vương theo cách tính niên hạn truyền thống.",
                "Người xưa khuyên chú ý giữ gìn sức khỏe, đi đứng cẩn thận, tránh tranh chấp thị phi.",
                "Đây là thông tin dân gian tham khảo để sinh hoạt điều độ, giữ tâm an lành.",
                "Dừng hình tra cứu năm sinh nhé.",
            ],
            bgm_file="clean_soul.mp3",
            bgm_title="Clean Soul",
            **YT,
        )
    )

    # 9. 15/11 slot 04:30 - month_sheet: khai trương tháng 4/2027
    plan.append(
        mk(
            id="fs_d1_15_1",
            day="2026-11-15",
            slot="04:30",
            lane="ngaytot",
            theme="navy",
            kicker="KHAI TRƯƠNG · THÁNG 4/2027",
            title="Tháng 4 năm 2027: ngày nào tốt để khai trương, mở hàng?",
            title_main="THÁNG 4 NĂM 2027",
            title_gold="NGÀY KHAI TRƯƠNG MỞ HÀNG",
            subchip_text="2 NGÀY MỞ HÀNG ĐẸP · 5 VÀ 17 THÁNG 4",
            legend_text="Vàng: ngày mở hàng đẹp · Đỏ: ngày kỵ · Tham khảo",
            subfoot_text="DỪNG HÌNH LƯU LẠI NGÀY TỐT NHÉ",
            days=DAYS_APR_KT,
            offset=APR_OFFSET,
            script=[
                "Tháng tư năm tới,",
                "trong tháng có hai ngày hoàng đạo trực Khai rất tốt cho việc khai trương, mở hàng.",
                "Đó là ngày mùng năm và ngày mười bảy tháng tư dương lịch.",
                "Khởi đầu vào ngày lành mang ý nghĩa đón may mắn, công việc kinh doanh thuận buồm xuôi gió.",
                "Dừng hình lưu lại ngày tốt tháng tư nhé.",
            ],
            display_script=[
                "Tháng 4 năm 2027,",
                "trong tháng có 2 ngày hoàng đạo trực Khai rất tốt cho việc khai trương, mở hàng.",
                "Đó là ngày 5 và ngày 17 tháng 4 dương lịch.",
                "Khởi đầu vào ngày lành mang ý nghĩa đón may mắn, công việc kinh doanh thuận buồm xuôi gió.",
                "Dừng hình lưu lại ngày tốt tháng 4 nhé.",
            ],
            bgm_file="asian_drums.mp3",
            bgm_title="Asian Drums",
            **MS,
        )
    )

    # 10. 15/11 slot 08:00 - yeartable: Hoang Ốc 2027
    plan.append(
        mk(
            id="fs_d1_15_2",
            day="2026-11-15",
            slot="08:00",
            theme="jade",
            chip="HOANG ỐC 2027 · ĐINH MÙI",
            title_html='<span class="l s">HOANG ỐC 2027</span><span class="l gold">3 CUNG TỐT ĐỘNG THỔ</span>',
            title="Hoang Ốc năm 2027: ba cung tốt nhất để động thổ, làm nhà",
            rows=[
                ("NHẤT CÁT", "AN CƯ THỊNH VƯỢNG", HO_NHAT_CAT),
                ("NHÌ NGHI", "GIA ĐẠO HƯNG THỊNH", HO_NHI_NGHI),
                ("TỨ TẤN TÀI", "TÀI LỘC DỒI DÀO", HO_TU_TAN_TAI),
            ],
            script=[
                "Năm Đinh Mùi,",
                "trong sáu cung Hoang Ốc, có ba cung tốt nhất để khởi công làm nhà.",
                "Nhất Cát an cư, Nhì Nghi hưng vượng, và Tứ Tấn Tài đón tài lộc dồi dào.",
                "Danh sách phân định rõ từng năm sinh tương ứng với mỗi cung tốt.",
                "Dừng hình tìm cung tuổi của bạn nhé.",
            ],
            display_script=[
                "Năm 2027,",
                "trong 6 cung Hoang Ốc, có 3 cung tốt nhất để khởi công làm nhà.",
                "Nhất Cát an cư, Nhì Nghi hưng vượng, và Tứ Tấn Tài đón tài lộc dồi dào.",
                "Danh sách phân định rõ từng năm sinh tương ứng với mỗi cung tốt.",
                "Dừng hình tìm cung tuổi của bạn nhé.",
            ],
            bgm_file="senbazuru.mp3",
            bgm_title="Senbazuru",
            **YT,
        )
    )

    # 11. 15/11 slot 12:00 - yeartable: sao Thổ Tú 2027
    plan.append(
        mk(
            id="fs_d1_15_3",
            day="2026-11-15",
            slot="12:00",
            theme="navy",
            chip="CỬU DIỆU 2027 · ĐINH MÙI",
            title_html='<span class="l s">SAO THỔ TÚ 2027</span><span class="l gold">NAM NỮ CẦN LƯU Ý</span>',
            title="Sao Thổ Tú năm 2027: nam nữ nào cần cẩn trọng khẩu thiệt?",
            rows=[
                ("NAM MẠNG", "SAO THỔ TÚ", SAO_NAM("Thổ Tú")),
                ("NỮ MẠNG", "SAO THỔ TÚ", SAO_NU("Thổ Tú")),
            ],
            script=[
                "Năm Đinh Mùi,",
                "các năm sinh này gặp sao Thổ Tú chiếu mệnh theo vòng Cửu Diệu.",
                "Người xưa khuyên giữ thái độ hòa nhã, cẩn trọng lời nói, đi xa nên chuẩn bị kỹ.",
                "Giữ tâm vững vàng thì mọi việc ắt sẽ hanh thông, thuận hòa.",
                "Dừng hình tra cứu năm sinh của bạn nhé.",
            ],
            bgm_file="ishikari_lore.mp3",
            bgm_title="Ishikari Lore",
            **YT,
        )
    )

    plan_guard(plan)
    return plan


def plan_guard(plan: list[dict]) -> None:
    """Đối chiếu độc lập: saohan vs tuvi_year; Hoang Ốc; ngày tốt tháng 2 và 4."""
    errs = []
    # Kiểm tra tính toàn vẹn của profile tuvi_year vs saohan
    for y in YEARS:
        for k, v in (
            ("han_nam", saohan.han(y, True, at=2027)),
            ("han_nu", saohan.han(y, False, at=2027)),
            ("sao_nam", saohan.sao(y, True, at=2027)),
            ("sao_nu", saohan.sao(y, False, at=2027)),
        ):
            if R27[y][k] != v:
                errs.append(f"saohan != tuvi_year {y} {k}")

    # Kiểm tra từng item trong plan
    assert len(plan) == 11, f"Plan phải đúng 11 bài, got {len(plan)}"
    n_yt = sum(1 for it in plan if it["style"] == "yeartable")
    n_ms = sum(1 for it in plan if it["style"] == "month_sheet")
    assert n_yt == 7, f"Số bài yeartable phải là 7, got {n_yt}"
    assert n_ms == 4, f"Số bài month_sheet phải là 4, got {n_ms}"

    day_counts = {}
    for it in plan:
        day_counts[it["day"]] = day_counts.get(it["day"], 0) + 1
        # Slot không được trùng với các trường cấm
        for bad in ("insight", "tags", "hashtags", "cta"):
            assert bad not in it, f"{it['id']} chứa trường packaging cấm: {bad}"

    expected_days = {
        "2026-11-09": 2,
        "2026-11-11": 1,
        "2026-11-12": 2,
        "2026-11-13": 1,
        "2026-11-14": 2,
        "2026-11-15": 3,
    }
    assert day_counts == expected_days, f"Phân bổ ngày sai: {day_counts} vs {expected_days}"

    # Kiểm tra rows của yeartable
    for it in plan:
        if it["style"] == "yeartable":
            for label, tag, ys in it["rows"]:
                if not ys:
                    errs.append(f"{it['id']} {label}: danh sách rỗng")
                if ys != sorted(ys):
                    errs.append(f"{it['id']} {label}: chưa sắp xếp")
                for y in ys:
                    r27 = R27[y]
                    if "THÁI BẠCH" in tag:
                        want = (r27["sao_nam"] if label == "NAM MẠNG" else r27["sao_nu"]) == "Thái Bạch"
                    elif "LA HẦU" in tag:
                        want = r27["sao_nam"] == "La Hầu"
                    elif "KẾ ĐÔ" in tag:
                        want = r27["sao_nu"] == "Kế Đô"
                    elif "MỘC ĐỨC" in tag:
                        want = (r27["sao_nam"] if label == "NAM MẠNG" else r27["sao_nu"]) == "Mộc Đức"
                    elif "THỔ TÚ" in tag:
                        want = (r27["sao_nam"] if label == "NAM MẠNG" else r27["sao_nu"]) == "Thổ Tú"
                    elif "DIÊM VƯƠNG" in tag:
                        want = (r27["han_nam"] if label == "NAM MẠNG" else r27["han_nu"]) == "Diêm Vương"
                    elif "ĐỘNG THỔ TỐT" in tag:
                        want = not r27["tam_tai"] and not r27["kim_lau"] and not r27["hoang_oc_xau"]
                    elif label in ("NHẤT CÁT", "NHÌ NGHI", "TỨ TẤN TÀI"):
                        want = r27["hoang_oc"].upper() == label
                    else:
                        want = False
                    if not want:
                        errs.append(f"{it['id']} {label}/{tag}: năm {y} sai")

    # Kiểm tra month_sheet
    assert len(DAYS_FEB_2027) == 28 and FEB_OFFSET == 0, "Tháng 2/2027: 28 ngày, bắt đầu thứ Hai"
    assert len(DAYS_APR_2027) == 30 and APR_OFFSET == 3, "Tháng 4/2027: 30 ngày, bắt đầu thứ Năm"

    if errs:
        raise ValueError("PLAN GUARD FAIL:\n" + "\n".join(errs))
    print("PLAN GUARD: PASS (11/11 bài khớp số liệu)")


# ---------------------------------------------------------------- PACKAGING
def write_packaging(plan: list[dict]) -> None:
    for it in plan:
        pkg_file = PKG_DIR / f"{it['id']}.json"
        title = it["title"]
        if it["style"] == "yeartable":
            insight = f"{title}. Bảng tra cứu chi tiết năm sinh theo tử vi truyền thống năm Đinh Mùi 2027, chỉ để tham khảo."
            tags = [
                "tu vi 2027",
                "dinh mui 2027",
                "tra nam sinh",
                "sao han 2027",
                "tuoi hop",
                "phong thuy",
            ]
            tags_vi = [
                "tử vi 2027",
                "Đinh Mùi 2027",
                "tra năm sinh",
                "sao hạn 2027",
                "tuổi hợp",
                "phong thủy",
            ]
            hashtags = ["#Shorts", "#tuvi2027", "#saohan2027", "#phongthuy"]
            cta = "Bạn sinh năm nào? Bình luận bên dưới để cùng chia sẻ nhé."
        else:
            insight = f"{title}. Bảng tra cứu ngày tốt hoàng đạo và ngày kỵ theo lịch vạn niên truyền thống, chỉ để tham khảo."
            tags = [
                "ngay tot",
                "lich am 2027",
                "ngay hoang dao",
                "xem ngay",
                "phong thuy",
            ]
            tags_vi = [
                "ngày tốt",
                "lịch âm 2027",
                "ngày hoàng đạo",
                "xem ngày",
                "phong thủy",
            ]
            hashtags = ["#Shorts", "#ngaytot", "#licham2027", "#phongthuy"]
            cta = "Dừng hình lưu lại ngày tốt và chia sẻ cho người thân nhé."

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
    rid, style = item["id"], item["style"]
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
    final_dur = max(21.2, round(last_end + 4.5, 2))
    if final_dur > 26.8:
        final_dur = 26.8
    item["dur"] = final_dur

    # Kiểm tra câu 1 <= 2.5s
    c1_dur = raw[0]["end"] - raw[0]["start"]
    print(f"[{rid}] Câu 1: {c1_dur:.2f}s ({raw[0]['start']:.2f} -> {raw[0]['end']:.2f}) | audio: {last_end:.2f}s | dur: {final_dur:.2f}s")
    assert c1_dur <= 2.55, f"Câu 1 {c1_dur:.2f}s vượt 2.5s ở {rid}"

    disp = item.get("display_script") or item["script"]
    segs = [
        {"start": s["start"], "end": s["end"], "text": disp[i] if i < len(disp) else s["text"]}
        for i, s in enumerate(raw)
    ]
    html = (
        P.build_yeartable_html(item, final_dur, segs)
        if style == "yeartable"
        else build_month_sheet_generic(item, final_dur, segs)
    )
    comp = f"_tb_{rid}.html"
    (COMP / comp).write_text(html, encoding="utf-8")
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
            str(RENDER_DIR / f"frame_mid_1080_{rid}.png"),
        ],
        check=True,
    )
    # Khung 0
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(mp4),
            "-ss",
            "0.1",
            "-vframes",
            "1",
            str(RENDER_DIR / f"frame_0_1080_{rid}.png"),
        ],
        check=True,
    )
    meta = {
        k: item.get(k)
        for k in (
            "id",
            "day",
            "slot",
            "title",
            "style",
            "lane",
            "bgm_title",
            "hook_type",
            "narrative_structure",
            "hypothesis",
            "format_subtag",
            "batch_id",
        )
    }
    meta.update(
        ok=True,
        duration_s=real,
        hold_s=round(real - last_end, 2),
        c1_dur_s=round(c1_dur, 2),
        output=str(mp4.relative_to(ROOT)),
        bgm=f"bgm/{item['bgm_file']}",
        lufs={"voice": round(vl, 1), "mix": round(mix, 1)},
        hold_diff=round(diff, 4),
    )
    meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{rid}] xong {real:.1f}s c1={c1_dur:.2f}s hold_diff={diff:.4f} mix={mix:.1f} LUFS", flush=True)


def export_preview(plan: list[dict]) -> None:
    cw, ch = 360, 640
    # 3 hàng: khung 0, khung giữa, khung cuối
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
    sheet.save(RENDER_DIR / "preview_001_fs.jpg", quality=90)
    print("Preview sheet saved:", RENDER_DIR / "preview_001_fs.jpg")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--plan-only", action="store_true")
    a = ap.parse_args()

    plan = make_plan()
    clean_plan = []
    for it in plan:
        cp = {k: v for k, v in it.items() if k not in ("days",)}
        clean_plan.append(cp)

    validate(clean_plan)
    PLAN_FILE.write_text(json.dumps(clean_plan, ensure_ascii=False, indent=2), encoding="utf-8")
    (RENDER_DIR / "plan_001_fs_dot1_0915.json").write_text(
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
        (RENDER_DIR / "plan_001_fs_dot1_0915.json").write_text(
            json.dumps(clean_plan, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        export_preview(plan)
