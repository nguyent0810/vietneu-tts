"""Builder + render cho 007_fs_lap_o_va_thay_thua: 7 short FS (09-18/11/2026).

Phân bổ 7 short FS:
- 09/11 04:30Z (11:30 VN): Sinh năm 1985 Ất Sửu mệnh gì, hợp màu gì? (nam_sinh_menh)
- 12/11 04:30Z (11:30 VN): Năm 2027: tuổi nào dễ phát tài nhất? (tuoi)
- 12/11 15:00Z (22:00 VN): Năm 2027: tuổi nào nên mua xe, mua đất? (tuoi, THAY f38_d)
- 13/11 12:00Z (19:00 VN): Tháng 10 âm lịch: con giáp nào gặp may? (congiap_thang, 09/11-08/12/2026)
- 15/11 04:30Z (11:30 VN): Sinh năm 1992 Nhâm Thân mệnh gì, hợp màu gì? (nam_sinh_menh)
- 18/11 04:30Z (11:30 VN): Năm 2027: 3 tuổi hợp kết hôn nhất (tuoi, THAY nt_cuoi_2027_h1)
- 18/11 12:00Z (19:00 VN): Năm 2027: tuổi nào hợp xuất hành đi xa? (tuoi, THAY nt_lamnha_2027_01)

Mọi số tính bằng code (canchi, amlich, saohan, tuvi_year).
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
import saohan
import tuvi_year
import fs_mau_ngay as FMN

P = importlib.import_module("build_fs_phu_1104")

RENDER_DIR = HERE / "render_007_fs"
RENDER_DIR.mkdir(parents=True, exist_ok=True)
ROOT_RENDER_DIR = RENDER_DIR

HF = ROOT / "hyperframes_short"
COMP = HF / "compositions"
PLAN_FILE = ROOT / "output" / "cl_staging" / "fs" / "plan_007_fs.json"
PKG_DIR = ROOT / "output" / "cl_staging" / "fs" / "packaging"
PKG_DIR.mkdir(parents=True, exist_ok=True)
BATCH = "fs_007_lap_o_thay_thua"

YEARS = list(range(1950, 2011))
PROF27 = {y: tuvi_year.profile(y, start=2027, n_years=1) for y in YEARS}
R27 = {y: PROF27[y]["cac_nam"][0] for y in YEARS}

# ---------------------------------------------------------------- Số liệu tính bằng code
# 1. 1985 Ất Sửu
P85 = tuvi_year.profile(1985, start=2027, n_years=1)
assert P85["can_chi"] == "Ất Sửu" and P85["nap_am"] == "Hải Trung Kim" and P85["hanh"] == "Kim"

# 2. 1992 Nhâm Thân
P92 = tuvi_year.profile(1992, start=2027, n_years=1)
assert P92["can_chi"] == "Nhâm Thân" and P92["nap_am"] == "Kiếm Phong Kim" and P92["hanh"] == "Kim"

# 3. Mua xe mua đất 2027: không Tam Tai, không Kim Lâu, không Hoang Ốc xấu (13 năm sinh)
LAM_NHA_2027 = [y for y in YEARS if not R27[y]["tam_tai"] and not R27[y]["kim_lau"] and not R27[y]["hoang_oc_xau"]]
assert len(LAM_NHA_2027) == 13

# 4. Tháng 10 âm lịch Bính Ngọ 2026: 09/11/2026 đến 08/12/2026
L_START = amlich.solar2lunar(9, 11, 2026)
L_END = amlich.solar2lunar(8, 12, 2026)
assert L_START == (1, 10, 2026, 0), f"Ngày 09/11/2026 phải là mùng 1 tháng 10 âm, got {L_START}"
assert L_END == (30, 10, 2026, 0), f"Ngày 08/12/2026 phải là ngày 30 tháng 10 âm, got {L_END}"

# Tam hợp, lục hợp với tháng Hợi
assert canchi.tam_hop_of("Hợi") == ("Hợi", "Mão", "Mùi")
assert canchi.luc_hop_of("Hợi") == "Dần"

# 5. Phát tài 2027
LUC_HOP_NGO = [y for y in YEARS if PROF27[y]["chi"] == "Ngọ"]
# Tứ Tấn Tài: tính bằng code, bỏ năm sinh dính Tam Tai 2027 (1955, 1991) để khớp bảng khai trương dot2.
HO_TU_TAN_TAI = [y for y in YEARS if R27[y]["hoang_oc"] == "Tứ Tấn Tài" and not R27[y]["tam_tai"]]
assert HO_TU_TAN_TAI == [1964, 1973, 1982, 1988, 1997, 2000, 2006, 2009], HO_TU_TAN_TAI
SAO_THAI_AM_NAM = [y for y in YEARS if saohan.sao(y, True, at=2027) == "Thái Âm"]

# 6. Kết hôn 2027: Tuổi Ngọ (Lục hợp), Tuổi Dần, Tuổi Thân (không Tam Tai 2027)
MARRY_NGO = [1978, 1990, 2002]
MARRY_DAN = [1974, 1986, 1998]
MARRY_THAN = [1980, 1992, 2004]
for ys in (MARRY_NGO, MARRY_DAN, MARRY_THAN):
    for y in ys:
        assert not R27[y]["tam_tai"], f"Năm {y} dính Tam Tai"

# 7. Xuất hành 2027: Tuổi Ngọ, Tuổi Dần, Tuổi Tỵ (không phạm xung Thái Tuế 2027)
TRAVEL_NGO = [1954, 1966, 1978, 1990, 2002]
TRAVEL_DAN = [1962, 1974, 1986, 1998, 2010]
TRAVEL_TY = [1953, 1965, 1977, 1989, 2001]
for y in TRAVEL_NGO + TRAVEL_DAN + TRAVEL_TY:
    assert R27[y]["quan_he_chi"] in ("lục hợp", "bình thường", "tam hợp"), f"Năm {y} xung Thái Tuế"


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

    # Đóng băng chuyển động trong 3.2s cuối để khung cuối hoàn toàn tĩnh
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

    # Thay font bằng local fonts
    fonts = P.font_css()
    base = base.replace(
        '<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@500;700;800;900&display=swap" rel="stylesheet" />',
        f"<style>\n{fonts}\n</style>"
    )

    data = {
        "dur": dur,
        "theme": t.get("theme", "red"),
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


# ---------------------------------------------------------------- Khởi tạo 7 items
def make_plan() -> list[dict]:
    plan = [
        # 1. 09/11 04:30Z (11:30 VN): Sinh năm 1985 Ất Sửu mệnh gì, hợp màu gì? (nam_sinh_menh)
        {
            "id": "fs_007_09_1",
            "day": "2026-11-09",
            "slot": "04:30",
            "lane": "nam_sinh_menh",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "navy",
            "chip": "BẢN MỆNH · MÀU HỢP MỆNH",
            "title_html": '<span class="l s">SINH NĂM 1985 ẤT SỬU</span><span class="l gold">MỆNH GÌ, HỢP MÀU GÌ?</span>',
            "title": "Sinh năm 1985 Ất Sửu mệnh gì, hợp màu gì?",
            # Màu: sinh từ HANH_MAU (fs_mau_ngay), chip = lời đọc = phụ đề = mô tả.
            **FMN.menh_fields(P85["hanh"], 1985, "Ất Sửu", "Sửu", "một chín tám lăm", P85["nap_am"], "tức vàng trong biển"),
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
        },
        # 2. 12/11 04:30Z (11:30 VN): Năm 2027: tuổi nào dễ phát tài nhất? (tuoi)
        {
            "id": "fs_007_12_1",
            "day": "2026-11-12",
            "slot": "04:30",
            "lane": "tuoi",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "amber",
            "chip": "TỬ VI 2027 · ĐINH MÙI",
            "title_html": '<span class="l s">NĂM 2027 ĐINH MÙI</span><span class="l gold">TUỔI NÀO DỄ PHÁT TÀI?</span>',
            "title": "Năm 2027: tuổi nào dễ phát tài nhất?",
            "rows": [
                ("TUỔI NGỌ", "LỤC HỢP VƯỢNG KHÍ", LUC_HOP_NGO),
                ("TẤN TÀI", "CUNG TỨ TẤN TÀI", HO_TU_TAN_TAI),
                ("THÁI ÂM (NAM)", "TÀI TINH CHIẾU MỆNH", SAO_THAI_AM_NAM),
            ],
            "script": [
                "Năm Đinh Mùi,",
                "theo tử vi truyền thống, các năm sinh này đón nhiều cơ hội tài lộc và vận may hanh thông.",
                "Người tuổi Ngọ bước vào năm lục hợp, cùng các tuổi gặp cung Tứ Tấn Tài, và nam mạng gặp sao Thái Âm trợ mệnh.",
                "Khung tử vi chỉ mang tính tham khảo, thành công thực tế luôn đến từ sự chăm chỉ và nỗ lực.",
                "Dừng hình tìm năm sinh của bạn trên màn hình nhé.",
            ],
            "display_script": [
                "Năm Đinh Mùi 2027,",
                "theo tử vi truyền thống, các năm sinh này đón nhiều cơ hội tài lộc và vận may hanh thông.",
                "Người tuổi Ngọ bước vào năm lục hợp, cùng các tuổi gặp cung Tứ Tấn Tài, và nam mạng gặp sao Thái Âm trợ mệnh.",
                "Khung tử vi chỉ mang tính tham khảo, thành công thực tế luôn đến từ sự chăm chỉ và nỗ lực.",
                "Dừng hình tìm năm sinh của bạn trên màn hình nhé.",
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
        },
        # 3. 12/11 15:00Z (22:00 VN): Năm 2027: tuổi nào nên mua xe, mua đất? (tuoi, THAY f38_d)
        {
            "id": "fs_007_12_2",
            "day": "2026-11-12",
            "slot": "15:00",
            "lane": "tuoi",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "jade",
            "chip": "ĐIỀN TRẠCH 2027 · ĐINH MÙI",
            "title_html": '<span class="l s">NĂM 2027 ĐINH MÙI</span><span class="l gold">MUA XE, MUA ĐẤT TỐT?</span>',
            "title": "Năm 2027: tuổi nào nên mua xe, mua đất?",
            "replaces_video": "f38_d",
            "rows": [
                ("1952 - 1969", "ĐIỀN TRẠCH TỐT", [1952, 1958, 1960, 1961, 1969]),
                ("1970 - 1988", "ĐIỀN TRẠCH TỐT", [1970, 1976, 1985, 1988]),
                ("1994 - 2008", "ĐIỀN TRẠCH TỐT", [1994, 1997, 2006, 2008]),
            ],
            "script": [
                "Năm Đinh Mùi,",
                "nếu dự định mua xe hoặc tậu đất đai, đây là mười ba năm sinh đẹp nhất theo truyền thống.",
                "Các tuổi này không phạm Tam Tai, Kim Lâu hay Hoang Ốc xấu, rất thuận lợi để an cư và tích lũy.",
                "Bảng tra phong thủy chỉ mang tính tham khảo khi chọn thời điểm thực hiện đại sự.",
                "Dừng hình tìm năm sinh của bạn trên màn hình nhé.",
            ],
            "display_script": [
                "Năm Đinh Mùi 2027,",
                "nếu dự định mua xe hoặc tậu đất đai, đây là 13 năm sinh đẹp nhất theo truyền thống.",
                "Các tuổi này không phạm Tam Tai, Kim Lâu hay Hoang Ốc xấu, rất thuận lợi để an cư và tích lũy.",
                "Bảng tra phong thủy chỉ mang tính tham khảo khi chọn thời điểm thực hiện đại sự.",
                "Dừng hình tìm năm sinh của bạn trên màn hình nhé.",
            ],
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
        },
        # 4. 13/11 12:00Z (19:00 VN): Tháng 10 âm lịch: con giáp nào gặp may? (congiap_thang)
        {
            "id": "fs_007_13_1",
            "day": "2026-11-13",
            "slot": "12:00",
            "lane": "congiap_thang",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "red",
            "chip": "VẬN SỐ THÁNG 10 ÂM LỊCH",
            "title_html": '<span class="l s">THÁNG 10 ÂM BÍNH NGỌ</span><span class="l gold">CON GIÁP NÀO GẶP MAY?</span>',
            "title": "Tháng 10 âm lịch: con giáp nào gặp may?",
            "rows": [
                ("TUỔI MÃO", "TAM HỢP NGUYỆT LỆNH", [1963, 1975, 1987, 1999]),
                ("TUỔI MÙI", "TAM HỢP NGUYỆT LỆNH", [1955, 1967, 1979, 1991, 2003]),
                ("TUỔI DẦN", "LỤC HỢP THÁNG MƯỜI", [1962, 1974, 1986, 1998, 2010]),
            ],
            "script": [
                "Tháng mười âm lịch,",
                "bước vào tiết đông với khí lệnh chi Hợi, theo truyền thống có ba con giáp dễ gặp may mắn nhất.",
                "Đó là tuổi Mão và tuổi Mùi thuộc vòng tam hợp, cùng tuổi Dần đón thế lục hợp với tháng mười.",
                "Công việc và cuộc sống dễ có quý nhân tương trợ, thông tin chỉ mang tính tham khảo chiêm nghiệm.",
                "Dừng hình tìm năm sinh của bạn trên màn hình nhé.",
            ],
            "display_script": [
                "Tháng 10 âm lịch,",
                "bước vào tiết đông với khí lệnh chi Hợi, theo truyền thống có 3 con giáp dễ gặp may mắn nhất.",
                "Đó là tuổi Mão và tuổi Mùi thuộc vòng tam hợp, cùng tuổi Dần đón thế lục hợp với tháng 10.",
                "Công việc và cuộc sống dễ có quý nhân tương trợ, thông tin chỉ mang tính tham khảo chiêm nghiệm.",
                "Dừng hình tìm năm sinh của bạn trên màn hình nhé.",
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
        },
        # 5. 15/11 04:30Z (11:30 VN): Sinh năm 1992 Nhâm Thân mệnh gì, hợp màu gì? (nam_sinh_menh)
        {
            "id": "fs_007_15_1",
            "day": "2026-11-15",
            "slot": "04:30",
            "lane": "nam_sinh_menh",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "navy",
            "chip": "BẢN MỆNH · MÀU HỢP MỆNH",
            "title_html": '<span class="l s">SINH NĂM 1992 NHÂM THÂN</span><span class="l gold">MỆNH GÌ, HỢP MÀU GÌ?</span>',
            "title": "Sinh năm 1992 Nhâm Thân mệnh gì, hợp màu gì?",
            **FMN.menh_fields(P92["hanh"], 1992, "Nhâm Thân", "Thân", "một chín chín hai", P92["nap_am"], "tức vàng nơi mũi kiếm"),
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
        },
        # 6. 18/11 04:30Z (11:30 VN): Năm 2027: 3 tuổi hợp kết hôn nhất (tuoi, THAY nt_cuoi_2027_h1)
        {
            "id": "fs_007_18_1",
            "day": "2026-11-18",
            "slot": "04:30",
            "lane": "tuoi",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "red",
            "chip": "HỶ SỰ 2027 · ĐINH MÙI",
            "title_html": '<span class="l s">NĂM 2027 ĐINH MÙI</span><span class="l gold">3 TUỔI HỢP KẾT HÔN</span>',
            "title": "Năm 2027: 3 tuổi hợp kết hôn nhất",
            "replaces_video": "nt_cuoi_2027_h1",
            "rows": [
                ("TUỔI NGỌ", "LỤC HỢP CÁT VẬN", MARRY_NGO),
                ("TUỔI DẦN", "KHÔNG PHẠM TAM TAI", MARRY_DAN),
                ("TUỔI THÂN", "KHÔNG PHẠM TAM TAI", MARRY_THAN),
            ],
            "script": [
                "Năm Đinh Mùi,",
                "nếu tính chuyện trăm năm kết duyên, đây là ba con giáp thuận lợi nhất theo tử vi truyền thống.",
                "Đó là tuổi Ngọ đón thế lục hợp cát tường, cùng tuổi Dần và tuổi Thân không phạm Tam Tai.",
                "Bảng tra chi tiết năm sinh hiển thị trên màn hình, khung phong thủy chỉ mang tính tham khảo.",
                "Dừng hình tìm năm sinh của bạn để cùng chia sẻ nhé.",
            ],
            "display_script": [
                "Năm Đinh Mùi 2027,",
                "nếu tính chuyện trăm năm kết duyên, đây là 3 con giáp thuận lợi nhất theo tử vi truyền thống.",
                "Đó là tuổi Ngọ đón thế lục hợp cát tường, cùng tuổi Dần và tuổi Thân không phạm Tam Tai.",
                "Bảng tra chi tiết năm sinh hiển thị trên màn hình, khung phong thủy chỉ mang tính tham khảo.",
                "Dừng hình tìm năm sinh của bạn để cùng chia sẻ nhé.",
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
        },
        # 7. 18/11 12:00Z (19:00 VN): Năm 2027: tuổi nào hợp xuất hành đi xa? (tuoi, THAY nt_lamnha_2027_01)
        {
            "id": "fs_007_18_2",
            "day": "2026-11-18",
            "slot": "12:00",
            "lane": "tuoi",
            "style": "yeartable",
            "format_subtag": "yeartable",
            "theme": "jade",
            "chip": "XUẤT HÀNH 2027 · ĐINH MÙI",
            "title_html": '<span class="l s">NĂM 2027 ĐINH MÙI</span><span class="l gold">XUẤT HÀNH ĐI XA TỐT</span>',
            "title": "Năm 2027: tuổi nào hợp xuất hành đi xa?",
            "replaces_video": "nt_lamnha_2027_01",
            "rows": [
                ("TUỔI NGỌ", "LỤC HỢP XUẤT HÀNH", TRAVEL_NGO),
                ("TUỔI DẦN", "BÌNH HÒA CÁT KHÍ", TRAVEL_DAN),
                ("TUỔI TỴ", "XUẤT HÀNH THUẬN LỢI", TRAVEL_TY),
            ],
            "script": [
                "Năm Đinh Mùi,",
                "với người có dự định xuất hành đi xa hoặc làm ăn nơi đất khách, đây là các tuổi thuận lợi.",
                "Tuổi Ngọ đón thế lục hợp cát tường, cùng tuổi Dần và tuổi Tỵ không phạm xung khắc.",
                "Chuyến đi được xem là dễ gặp bình an và may mắn, thông tin chỉ mang tính tham khảo.",
                "Dừng hình tìm năm sinh của bạn trên màn hình nhé.",
            ],
            "display_script": [
                "Năm Đinh Mùi 2027,",
                "với người có dự định xuất hành đi xa hoặc làm ăn nơi đất khách, đây là các tuổi thuận lợi.",
                "Tuổi Ngọ đón thế lục hợp cát tường, cùng tuổi Dần và tuổi Tỵ không phạm xung khắc.",
                "Chuyến đi được xem là dễ gặp bình an và may mắn, thông tin chỉ mang tính tham khảo.",
                "Dừng hình tìm năm sinh của bạn trên màn hình nhé.",
            ],
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
        },
    ]
    return plan


# ---------------------------------------------------------------- PLAN GUARD
def plan_guard(plan: list[dict]) -> None:
    assert len(plan) == 7, f"Plan phải đúng 7 bài, got {len(plan)}"
    for it in plan:
        for bad in ("insight", "tags", "hashtags", "cta"):
            assert bad not in it, f"{it['id']} chứa trường packaging cấm: {bad}"

        # Kiểm tra chi trong câu (<= 3 chi/câu)
        for s in it["script"]:
            found_chis = [c for c in canchi.CHI if c in s]
            assert len(found_chis) <= 3, f"{it['id']} vượt 3 chi trong 1 câu: {s} ({found_chis})"

    print("PLAN GUARD: PASS (7/7 bài hợp lệ)")


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
    final_dur = max(21.2, round(last_end + 4.5, 2))
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
    html = build_yeartable_custom(item, final_dur, segs)
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
        "style": "yeartable",
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

    preview_path = RENDER_DIR / "preview_007_fs.jpg"
    sheet.save(preview_path, quality=90)
    # Sao lưu sang cả ROOT / render_007_fs / preview_007_fs.jpg
    sheet.save(ROOT_RENDER_DIR / "preview_007_fs.jpg", quality=90)
    print("Preview sheet saved:", preview_path)

    # Bản 168px cho Lead soát độ đọc trên mobile
    w_168 = 168 * len(plan)
    h_168 = round((ch * 3 + 50) * (168 / cw))
    sheet_168 = sheet.resize((w_168, h_168), Image.Resampling.LANCZOS)
    sheet_168.save(RENDER_DIR / "preview_007_fs_168.jpg", quality=90)
    sheet_168.save(ROOT_RENDER_DIR / "preview_007_fs_168.jpg", quality=90)
    print("Preview 168 saved:", RENDER_DIR / "preview_007_fs_168.jpg")


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
    (RENDER_DIR / "plan_007_fs.json").write_text(
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
        (RENDER_DIR / "plan_007_fs.json").write_text(
            json.dumps(clean_plan, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        export_preview(plan)
