"""Builder và render cho 009_fs_pilot_saohan:
Dựng 3 pilot FS sao hạn bảng năm sinh 9,5s (PO duyệt GO 06/11).
Mould A, style yeartable, theme ivory, dur 9-11s, 2 câu.
Toàn bộ năm sinh trong rows, insight, mô tả SINH TỪ CODE (fs_calendar/saohan.py, fs_calendar/tuvi_year.py).
Assert đối chiếu hình ↔ insight 100%.
"""
from __future__ import annotations
from shortbuild import validate

import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "output" / "cl_staging" / "long"))

import canchi as C
import fs_calendar.saohan as saohan
import fs_calendar.tuvi_year as tuvi_year
import hf_batch_render as R
import hf_qa

RENDER_DIR = HERE / "render_009"
RENDER_DIR.mkdir(parents=True, exist_ok=True)

FS_DIR = ROOT / "output" / "cl_staging" / "fs"
FS_DIR.mkdir(parents=True, exist_ok=True)

HF = ROOT / "hyperframes_short"
COMP = HF / "compositions"
BGM = "bgm/asian_drums.mp3"
BGM_GAIN_A = 0.14
FOOTER_TEXT = "Kiến thức truyền thống — để tham khảo"
NONE = {"type": "none", "source": "rule", "confidence": 0.86, "reason": "visuals/media"}


def font_css() -> str:
    """Đọc font local để nhúng tránh lỗi missing font-face khi check layout/contrast."""
    faces = json.loads((HF / "studio" / "fonts" / "faces.json").read_text(encoding="utf-8"))
    out = []
    for face in faces:
        fam = face.get("family")
        css = face.get("css", "")
        if fam == "Be Vietnam Pro" and re.search(r"font-weight:\s*(600|700|800|900)", css):
            out.append(css.replace("url('fonts/", "url('../studio/fonts/"))
        elif fam == "JetBrains Mono" and "font-weight: 500" in css:
            out.append(css.replace("url('fonts/", "url('../studio/fonts/"))
    return "\n".join(out)


# =========================================================================
# 1. TÍNH TOÁN DỮ LIỆU TỪ CODE (KHÔNG GÕ TAY)
# =========================================================================

# pl_sh_1: Nữ mạng đón 3 cát tinh (Thái Dương, Thái Âm, Mộc Đức)
# Lấy từ saohan.years_of_sao cho nam=False, khoảng 1950-2010 theo chuẩn bài mẫu fs27_07_a
PL1_THAI_DUONG = saohan.years_of_sao("Thái Dương", nam=False, lo=1950, hi=2010, at=2027)
PL1_THAI_AM = saohan.years_of_sao("Thái Âm", nam=False, lo=1950, hi=2010, at=2027)
PL1_MOC_DUC = saohan.years_of_sao("Mộc Đức", nam=False, lo=1950, hi=2010, at=2027)

# pl_sh_2: Tam Tai 2027 (Hợi - Mão - Mùi vào năm thứ 3 / năm cuối)
# Lấy từ tuvi_year.chi_of cho 1950-2011 theo đúng brief
PL2_HOI = [y for y in range(1950, 2012) if tuvi_year.chi_of(y) == "Hợi"]
PL2_MAO = [y for y in range(1950, 2012) if tuvi_year.chi_of(y) == "Mão"]
PL2_MUI = [y for y in range(1950, 2012) if tuvi_year.chi_of(y) == "Mùi"]

# pl_sh_3: Hoang Ốc xấu 2027 (Tam Địa Sát, Ngũ Thọ Tử, Lục Hoang Ốc)
# Lấy từ tuvi_year.hoang_oc cho độ tuổi làm nhà (1965-2004) theo đúng brief
PL3_TAM_DIA = [y for y in range(1965, 2005) if tuvi_year.hoang_oc(tuvi_year.tuoi(y, 2027)) == "Tam Địa Sát"]
PL3_NGU_THO = [y for y in range(1965, 2005) if tuvi_year.hoang_oc(tuvi_year.tuoi(y, 2027)) == "Ngũ Thọ Tử"]
PL3_LUC_OC = [y for y in range(1965, 2005) if tuvi_year.hoang_oc(tuvi_year.tuoi(y, 2027)) == "Lục Hoang Ốc"]


def make_plan() -> list[dict]:
    plan = [
        # Pilot 1: Nữ mạng đón 3 cát tinh
        {
            "id": "pl_sh_1",
            "day": "2026-11-23",
            "slot": "08:00",
            "mould": "A",
            "style": "yeartable",
            "series": "fs",
            "theme": "ivory",
            "dur": 9.5,
            "badge": "",
            "chip": "SAO HẠN 2027 · NỮ MẠNG",
            "title_html": '<span class="l s">NỮ MẠNG ĐÓN</span><span class="l gold">3 CÁT TINH</span>',
            "title": "Sao hạn 2027: nữ mạng đón 3 cát tinh",
            "script": [
                "Năm 2027, nữ giới sinh các năm này được sao tốt chiếu.",
                "Dừng hình tìm năm sinh của bạn, rồi lưu lại nhé."
            ],
            "media": {},
            "visuals": {},
            "figures": {str(i): dict(NONE) for i in range(1, 7)},
            "rows": [
                ("THÁI DƯƠNG", "SAO TỐT", PL1_THAI_DUONG),
                ("THÁI ÂM", "SAO TỐT", PL1_THAI_AM),
                ("MỘC ĐỨC", "SAO TỐT", PL1_MOC_DUC)
            ],
            "source": "",
            "tags": ["phong thuy", "sao han 2027", "nu mang", "dinh mui"],
            "tags_vi": ["sao hạn 2027", "nữ mạng 2027", "thái dương thái âm mộc đức"],
            "insight": (
                f"Năm 2027, nữ mạng đón ba sao tốt: Thái Dương ({', '.join(str(y) for y in PL1_THAI_DUONG)}), "
                f"Thái Âm ({', '.join(str(y) for y in PL1_THAI_AM)}), "
                f"Mộc Đức ({', '.join(str(y) for y in PL1_MOC_DUC)})."
            ),
            "lane": "tuoi",
            "hashtags": ["#Shorts", "#tuvi2027", "#saohan2027", "#numang"]
        },
        # Pilot 2: Tam Tai 2027
        {
            "id": "pl_sh_2",
            "day": "2026-11-24",
            "slot": "08:00",
            "mould": "A",
            "style": "yeartable",
            "series": "fs",
            "theme": "ivory",
            "dur": 9.5,
            "badge": "",
            "chip": "TAM TAI 2027 · ĐINH MÙI",
            "title_html": '<span class="l s">TAM TAI 2027</span><span class="l gold">VÀO NĂM CUỐI</span>',
            "title": "Tam Tai 2027: 3 con giáp vào năm cuối",
            "script": [
                "Năm 2027, người sinh các năm này vào năm cuối Tam Tai.",
                "Dừng hình tìm năm sinh của bạn, rồi lưu lại nhé."
            ],
            "media": {},
            "visuals": {},
            "figures": {str(i): dict(NONE) for i in range(1, 7)},
            "rows": [
                ("HỢI", "TAM TAI", PL2_HOI),
                ("MÃO", "TAM TAI", PL2_MAO),
                ("MÙI", "TAM TAI", PL2_MUI)
            ],
            "source": "",
            "tags": ["phong thuy", "nam 2027", "dinh mui", "tam tai 2027"],
            "tags_vi": ["năm 2027", "đinh mùi", "tam tai 2027", "hợi mão mùi"],
            "insight": (
                f"Năm 2027 Đinh Mùi là năm thứ ba (năm cuối) vận Tam Tai của nhóm tam hợp Hợi - Mão - Mùi: "
                f"tuổi Hợi ({', '.join(str(y) for y in PL2_HOI)}), "
                f"tuổi Mão ({', '.join(str(y) for y in PL2_MAO)}), "
                f"tuổi Mùi ({', '.join(str(y) for y in PL2_MUI)})."
            ),
            "lane": "tuoi",
            "hashtags": ["#Shorts", "#tuvi2027", "#tamtai2027", "#phongthuy"]
        },
        # Pilot 3: Hoang Ốc làm nhà 2027
        {
            "id": "pl_sh_3",
            "day": "2026-11-25",
            "slot": "08:00",
            "mould": "A",
            "style": "yeartable",
            "series": "fs",
            "theme": "ivory",
            "dur": 9.5,
            "badge": "",
            "chip": "LÀM NHÀ 2027 · HOANG ỐC",
            "title_html": '<span class="l s">LÀM NHÀ 2027</span><span class="l gold">PHẠM HOANG ỐC</span>',
            "title": "Năm 2027: tuổi nào chưa nên làm nhà?",
            "script": [
                "Năm 2027, người sinh các năm này phạm Hoang Ốc xấu.",
                "Dừng hình tìm năm sinh của bạn, rồi lưu lại nhé."
            ],
            "media": {},
            "visuals": {},
            "figures": {str(i): dict(NONE) for i in range(1, 7)},
            "rows": [
                ("TAM ĐỊA SÁT", "HOANG ỐC XẤU", PL3_TAM_DIA),
                ("NGŨ THỌ TỬ", "HOANG ỐC XẤU", PL3_NGU_THO),
                ("LỤC HOANG ỐC", "HOANG ỐC XẤU", PL3_LUC_OC)
            ],
            "source": "",
            "tags": ["phong thuy", "hoang oc 2027", "lam nha 2027", "dinh mui"],
            "tags_vi": ["hoang ốc 2027", "tam địa sát", "ngũ thọ tử", "lục hoang ốc"],
            "insight": (
                f"Năm 2027 Đinh Mùi, trong độ tuổi làm nhà (1965–2004) có ba cung Hoang Ốc xấu cần lưu ý: "
                f"Tam Địa Sát ({', '.join(str(y) for y in PL3_TAM_DIA)}), "
                f"Ngũ Thọ Tử ({', '.join(str(y) for y in PL3_NGU_THO)}), "
                f"Lục Hoang Ốc ({', '.join(str(y) for y in PL3_LUC_OC)})."
            ),
            "lane": "tuoi",
            "hashtags": ["#Shorts", "#tuvi2027", "#hoangoc", "#lamnha"]
        }
    ]
    return plan


def verify_plan_data(plan: list[dict]) -> None:
    """So khớp 100% hình ↔ insight và dữ liệu code đối chiếu."""
    for t in plan:
        rid = t["id"]
        # 1. Khớp năm sinh giữa rows và insight
        all_row_years = []
        for label, tag, ys in t["rows"]:
            all_row_years.extend(ys)
        unique_row_years = sorted(set(all_row_years))

        # Tìm các năm sinh trong insight (bỏ qua năm mốc 2027)
        found_in_insight = [int(x) for x in re.findall(r"\b(19\d\d|20\d\d)\b", t["insight"]) if int(x) != 2027]
        unique_insight_years = sorted(set(found_in_insight))

        assert unique_row_years == unique_insight_years, (
            f"[{rid}] LỆCH HÌNH ↔ INSIGHT:\n"
            f"  Rows:    {unique_row_years}\n"
            f"  Insight: {unique_insight_years}"
        )

        # 2. Kiểm tra chi tiết từng hàng đối chiếu hàm code
        if rid == "pl_sh_1":
            assert t["rows"][0][2] == saohan.years_of_sao("Thái Dương", False, 1950, 2010, 2027)
            assert t["rows"][1][2] == saohan.years_of_sao("Thái Âm", False, 1950, 2010, 2027)
            assert t["rows"][2][2] == saohan.years_of_sao("Mộc Đức", False, 1950, 2010, 2027)
        elif rid == "pl_sh_2":
            assert t["rows"][0][2] == [y for y in range(1950, 2012) if tuvi_year.chi_of(y) == "Hợi"]
            assert t["rows"][1][2] == [y for y in range(1950, 2012) if tuvi_year.chi_of(y) == "Mão"]
            assert t["rows"][2][2] == [y for y in range(1950, 2012) if tuvi_year.chi_of(y) == "Mùi"]
        elif rid == "pl_sh_3":
            assert t["rows"][0][2] == [y for y in range(1965, 2005) if tuvi_year.hoang_oc(tuvi_year.tuoi(y, 2027)) == "Tam Địa Sát"]
            assert t["rows"][1][2] == [y for y in range(1965, 2005) if tuvi_year.hoang_oc(tuvi_year.tuoi(y, 2027)) == "Ngũ Thọ Tử"]
            assert t["rows"][2][2] == [y for y in range(1965, 2005) if tuvi_year.hoang_oc(tuvi_year.tuoi(y, 2027)) == "Lục Hoang Ốc"]

    print("ASSERT SO KHỚP HÌNH ↔ INSIGHT: ĐẠT 100% trên cả 3 pilot!")


def build_composition_html(t: dict, dur: float, segs: list[dict]) -> str:
    """Tạo HTML composition theo khuôn yeartable ivory, nhúng local font và hold frame fix."""
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
  #title .gold { font-size: 72px !important; }
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
        '<div class="years${r.years && r.years.length >= 7 ? " col4" : ""}">'
        '${r.years.map((y) => `<span class="y">${y}</span>`).join("")}</div>'
    )
    base = base.replace(old_row_gen, new_row_gen)

    # Hold frame fix (Luật 20): đứng yên các animation ở khung cuối
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

    # Nhúng local font CSS
    fonts = font_css()
    base = base.replace(
        '<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@500;700;800;900&display=swap" rel="stylesheet" />',
        f"<style>\n{fonts}\n</style>"
    )

    data = {
        "dur": dur,
        "theme": t.get("theme", "ivory"),
        "segs": segs,
        "rows": [{"chi": c, "tag": tag, "years": ys} for c, tag, ys in t["rows"]]
    }

    title_val = t.get("title_html") or t["title"]
    html = (
        base.replace("__DUR__", str(dur))
        .replace("__CHIP__", t["chip"])
        .replace("__TITLE__", title_val)
        .replace("__DATA__", json.dumps(data, ensure_ascii=False))
    )
    return html


def extract_frames(mp4: Path, rid: str, dur: float) -> dict[str, Path]:
    """Trích xuất frame 0, giữa, cuối (1080px và 168px)."""
    p_0 = RENDER_DIR / f"frame_0_{rid}.png"
    p_mid = RENDER_DIR / f"frame_mid_{rid}.png"
    p_last = RENDER_DIR / f"frame_last_{rid}.png"
    p_last_168 = RENDER_DIR / f"frame_last_168_{rid}.png"

    t_mid = round(dur / 2.0, 2)
    t_last = max(0.1, round(dur - 0.25, 2))

    subprocess.run(["ffmpeg", "-y", "-ss", "0.0", "-i", str(mp4), "-vframes", "1", str(p_0)], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-ss", str(t_mid), "-i", str(mp4), "-vframes", "1", str(p_mid)], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-ss", str(t_last), "-i", str(mp4), "-vframes", "1", str(p_last)], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-ss", str(t_last), "-i", str(mp4), "-vframes", "1", "-vf", "scale=168:-1", str(p_last_168)], check=True, capture_output=True)

    return {"frame_0": p_0, "frame_mid": p_mid, "frame_last": p_last, "frame_last_168": p_last_168}


def create_preview_sheet(plan: list[dict], out_jpg: Path) -> None:
    """Ghép tờ preview_009.jpg gồm frame 0, giữa, cuối của cả 3 pilot."""
    rows_imgs = []
    card_w, card_h = 360, 640
    padding = 20
    header_h = 60

    total_w = card_w * 3 + padding * 4
    total_h = header_h + (card_h + 50) * len(plan) + padding

    sheet = Image.new("RGB", (total_w, total_h), (24, 24, 28))
    draw = ImageDraw.Draw(sheet)

    # Tiêu đề bảng
    draw.text((padding, 18), "009 PILOT SAOHAN 2027 — PREVIEW FRAME 0 / GIỮA / CUỐI (9.5s IVORY)", fill=(255, 230, 160))

    for idx, t in enumerate(plan):
        rid = t["id"]
        y_offset = header_h + idx * (card_h + 50)

        # Chú thích hàng
        label = f"{t['id']} ({t['day']} {t['slot']} UTC) — {t['title']}"
        draw.text((padding, y_offset), label, fill=(240, 240, 240))

        frame_paths = [
            RENDER_DIR / f"frame_0_{rid}.png",
            RENDER_DIR / f"frame_mid_{rid}.png",
            RENDER_DIR / f"frame_last_{rid}.png"
        ]
        col_labels = ["Frame 0 (0.0s)", "Frame giữa", "Frame cuối"]

        for c_idx, (fpath, clab) in enumerate(zip(frame_paths, col_labels)):
            x_offset = padding + c_idx * (card_w + padding)
            draw.text((x_offset, y_offset + 22), clab, fill=(180, 180, 180))
            if fpath.exists():
                im = Image.open(fpath).convert("RGB")
                im_thumb = im.resize((card_w, card_h), Image.Resampling.LANCZOS)
                sheet.paste(im_thumb, (x_offset, y_offset + 42))

    sheet.save(out_jpg, quality=90)
    print(f"Đã tạo tờ preview tổng hợp: {out_jpg}")


def run_build_and_render() -> None:
    plan = make_plan()

    # 1. Kiểm tra toàn vẹn và assert dữ liệu code
    verify_plan_data(plan)

    # 2. Ghi plan vào output/cl_staging/fs/plan_009_pilot_saohan.json
    plan_file = FS_DIR / "plan_009_pilot_saohan.json"
    validate(plan)
    plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đã ghi plan vào {plan_file} ({len(plan)} pilot)")

    # 3. TTS + Render từng video
    qa_results = []
    durations = {}

    for t in plan:
        rid = t["id"]
        print(f"\n==========================================")
        print(f"BẮT ĐẦU XỬ LÝ: {rid} — {t['title']}")
        print(f"==========================================")

        txt = RENDER_DIR / f"{rid}.txt"
        wav = RENDER_DIR / f"{rid}.wav"
        lines = t["script"]
        txt.write_text("\n".join(lines) + "\n", encoding="utf-8")

        # TTS
        if not wav.exists():
            print(f"[{rid}] Đang chạy TTS (giọng FS: Sơn)...")
            assert R.render_tts(txt, wav, lines, R.voice_for("fs")), f"TTS thất bại cho {rid}"

        wav_json = json.loads(wav.with_suffix(".json").read_text(encoding="utf-8"))
        segs = wav_json["segments"]
        sg = [{"start": round(s["start"], 3), "end": round(s["end"], 3), "text": x} for s, x in zip(segs, lines)]
        
        # Độ dài video theo TTS + buffer ~1.7s, chặn trong 9.0–11.0s
        dur = max(9.5, min(11.0, round(sg[-1]["end"] + 1.8, 2)))
        durations[rid] = dur
        print(f"[{rid}] Thời lượng tính toán: {dur}s (câu cuối kết thúc lúc {sg[-1]['end']}s)")

        # Tạo file composition
        comp_file = COMP / f"_tb_{rid}.html"
        html_content = build_composition_html(t, dur, sg)
        comp_file.write_text(html_content, encoding="utf-8")
        print(f"[{rid}] Đã tạo composition: {comp_file}")

        # QA checks: overflow & contrast
        print(f"[{rid}] Chạy hf_qa.py --overflow...")
        overflow_issues = hf_qa.gate_overflow(comp_file)
        overflow_res = "ĐẠT" if not overflow_issues else "TRÀN"
        print(f"  {comp_file.name}: {overflow_res}")
        for iss in overflow_issues:
            print(f"    {iss}")
        assert not overflow_issues, f"QA overflow thất bại cho {comp_file.name}: {overflow_issues}"

        print(f"[{rid}] Chạy hf_qa.py --contrast...")
        contrast_issues = hf_qa.gate_contrast(comp_file)
        contrast_res = "ĐẠT" if not contrast_issues else "TƯƠNG PHẢN KÉM"
        print(f"  {comp_file.name}: {contrast_res}")
        for iss in contrast_issues:
            print(f"    {iss}")
        assert not contrast_issues, f"QA contrast thất bại cho {comp_file.name}: {contrast_issues}"

        qa_results.append({
            "id": rid,
            "comp": comp_file.name,
            "overflow": overflow_res,
            "contrast": contrast_res
        })

        # HyperFrames render silent mp4
        silent_mp4 = RENDER_DIR / f"{rid}_silent.mp4"
        cmd = (
            f'export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1; nvm use 22 >/dev/null 2>&1; '
            f'cd "{HF}" && npx --yes hyperframes@0.8.75 render . -c compositions/{comp_file.name} --output "{silent_mp4}" --quality looks --fps 30 --quiet'
        )
        print(f"[{rid}] Đang render HyperFrames silent mp4...")
        p = subprocess.run(["/bin/bash", "-lc", cmd], capture_output=True, text=True, timeout=1800)
        if p.returncode != 0 or not silent_mp4.exists():
            raise RuntimeError(f"Render HyperFrames lỗi ({rid}):\n" + (p.stdout + p.stderr)[-2000:])

        # Ghép âm thanh TTS + BGM
        final_mp4 = RENDER_DIR / f"{rid}.mp4"
        bgm_path = ROOT / BGM
        print(f"[{rid}] Ghép TTS + BGM vào {final_mp4.name}...")
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error", "-i", str(silent_mp4), "-i", str(wav),
                "-stream_loop", "-1", "-i", str(bgm_path),
                "-filter_complex",
                f"[1:a]apad[v];[2:a]volume={BGM_GAIN_A},afade=t=out:st={dur - 1.2}:d=1.2[m];[v][m]amix=inputs=2:duration=first:normalize=0[a]",
                "-map", "0:v", "-map", "[a]", "-t", str(dur),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(final_mp4)
            ],
            check=True
        )
        silent_mp4.unlink(missing_ok=True)

        # Kiểm tra độ dài file mp4 xuất ra
        r_probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(final_mp4)],
            capture_output=True, text=True
        )
        real_dur = float((r_probe.stdout or "0").strip() or 0)
        print(f"[{rid}] Render thành công: {real_dur:.2f}s, dung lượng: {final_mp4.stat().st_size / 1e6:.2f} MB")
        assert 9.0 <= real_dur <= 11.0, f"Độ dài video {rid} ({real_dur}s) ngoài khoảng 9–11 s!"

        # Trích xuất frames
        frames = extract_frames(final_mp4, rid, real_dur)
        print(f"[{rid}] Đã trích xuất các khung hình: frame_0, frame_mid, frame_last")

    # Tạo preview contact sheet
    preview_jpg = RENDER_DIR / "preview_009.jpg"
    create_preview_sheet(plan, preview_jpg)

    print("\n==========================================")
    print("TỔNG KẾT BATCH 009 PILOT SAOHAN 2027:")
    print("==========================================")
    for q in qa_results:
        print(f"  {q['comp']}: overflow={q['overflow']}, contrast={q['contrast']}")
    print(f"Plan file: {plan_file}")
    print(f"Tờ preview: {preview_jpg}")


if __name__ == "__main__":
    run_build_and_render()
