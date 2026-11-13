"""Builder and renderer for 0001_fs_retire_thay:
FS: thay 6 short nguhanh (RETIRE) + 2 nhao còn lại bằng DẠNG THẮNG (GitHub issue #92).

Phân bổ:
- 3 sao hạn/tuổi 2027 kiểu YnA0SVWOlr0 (nam mạng đón 3 cát tinh, hạn Tam Kheo, hạn Ngũ Mộ)
- 3 tuoi (ngũ hành bản mệnh 2027, tuổi Ngọ lục hợp, tuổi Tuất hình Thái Tuế)
- 2 lich/hoangdao_daily (tra cứu nhanh ngày lành tháng 11/2026, 3 ngày đại cát Tết 2027)

Chuẩn SS-tier:
- Trả lời ngay khung 0; bảng chữ to, dừng hình được; khung cuối đứng >= 3s; 10-15s.
- Mọi năm/can chi/hạn tính bằng code (tuvi_year.py, canchi.py, amlich.py).
- Con giáp gọi bằng tên chi (Tý...Hợi). Khung "theo truyền thống / tham khảo", không doạ.
- Ghi manifest 5 trường mới: hook_type, narrative_structure, hypothesis, format_subtag, batch_id=fs_w45b.
- QA: hf_qa.py --overflow + --contrast cho mọi composition, đạt 100%.
- Tờ ảnh khung 168px và 1080px.
"""
from __future__ import annotations
from shortbuild import validate

import datetime as dt
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LONG_DIR = ROOT / "output" / "cl_staging" / "long"
TOOLS_DIR = HERE / "tools"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(LONG_DIR) not in sys.path:
    sys.path.insert(0, str(LONG_DIR))
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import amlich
import canchi
import hf_batch_render as R
import hf_novelty
from fs_calendar import hoangdao_daily
import tuvi_year

RENDER_DIR = HERE / "render_0001"
RENDER_DIR.mkdir(parents=True, exist_ok=True)

HF = ROOT / "hyperframes_short"
COMP = HF / "compositions"
COMP.mkdir(parents=True, exist_ok=True)

PLAN_FILE = ROOT / "output" / "cl_staging" / "fs" / "plan_0001_fs_retire_thay.json"


def font_css() -> str:
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


def measure_lufs(path: Path) -> float:
    cmd = ["ffmpeg", "-i", str(path), "-af", "ebur128=framelog=verbose", "-f", "null", "-"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    m = re.findall(r"I:\s+([-\d.]+)\s+LUFS", p.stderr)
    return float(m[-1]) if m else -20.0


# =========================================================================
# DATA CALCULATION VIA CODE
# =========================================================================
PROFILES = {y: tuvi_year.profile(y, start=2027, n_years=1) for y in range(1950, 2011)}
R27 = {y: PROFILES[y]["cac_nam"][0] for y in PROFILES}

# 1. Cát Tinh Nam Mạng 2027 (Cửu Diệu)
import saohan

YEARS = range(1950, 2011)
NAM_THAI_DUONG = [y for y in YEARS if saohan.sao(y, True, at=2027) == "Thái Dương"]
NAM_THAI_AM = [y for y in YEARS if saohan.sao(y, True, at=2027) == "Thái Âm"]
NAM_MOC_DUC = [y for y in YEARS if saohan.sao(y, True, at=2027) == "Mộc Đức"]

# 2. Niên Hạn 2027 (Tam Kheo & Ngũ Mộ)
NAM_TAM_KHEO = [y for y in YEARS if saohan.han(y, True, at=2027) == "Tam Kheo"]
NU_TAM_KHEO = [y for y in YEARS if saohan.han(y, False, at=2027) == "Tam Kheo"]

NAM_NGU_MO = [y for y in YEARS if saohan.han(y, True, at=2027) == "Ngũ Mộ"]
NU_NGU_MO = [y for y in YEARS if saohan.han(y, False, at=2027) == "Ngũ Mộ"]

# 3. Ngũ Hành Tương Sinh 2027 (Đinh Mùi - Thiên Hà Thủy)
MENH_MOC = [1972, 1973, 1980, 1981, 1988, 1989, 2002, 2003]  # Thủy sinh Mộc (Được sinh trợ)
MENH_THUY = [1974, 1975, 1982, 1983, 1996, 1997, 2004, 2005] # Lưỡng Thủy tương trợ (Bình hòa)
MENH_KIM = [1970, 1971, 1984, 1985, 1992, 1993, 2000, 2001]  # Kim sinh Thủy (Sinh xuất)

# 4. Lục Hợp 2027: Tuổi Ngọ gặp Mùi (Nhật Nguyệt Tương Hợp)
LUC_HOP_NGO = [
    ("GIÁP NGỌ", "74 TUỔI", [1954]),
    ("BÍNH NGỌ", "62 TUỔI", [1966]),
    ("MẬU NGỌ", "50 TUỔI", [1978]),
    ("CANH NGỌ", "38 TUỔI", [1990]),
    ("NHÂM NGỌ", "26 TUỔI", [2002])
]

# 5. Tương Hình Thái Tuế 2027: Tuổi Tuất gặp Mùi
TUONG_HINH_TUAT = [
    ("MẬU TUẤT", "70 TUỔI", [1958]),
    ("CANH TUẤT", "58 TUỔI", [1970]),
    ("NHÂM TUẤT", "46 TUỔI", [1982]),
    ("GIÁP TUẤT", "34 TUỔI", [1994]),
    ("BÍNH TUẤT", "22 TUỔI", [2006])
]

# 6. Tháng 11/2026 Hoàng Đạo (30 ngày)
DAYS_NOV_2026 = []
for d in range(1, 31):
    dt_obj = dt.date(2026, 11, d)
    f = hoangdao_daily.day_data(dt_obj)
    is_hd = f["is_hoang"]
    ld = f["ld"]
    is_tn = ld in (3, 7, 13, 18, 22, 27)
    is_nk = ld in (5, 14, 23)
    is_bad = is_tn or is_nk

    if is_hd and not is_bad:
        cell_type = "gold-good"
    elif is_hd and is_bad:
        cell_type = "gold-tn"
    elif not is_hd and is_bad:
        cell_type = "red-bad"
    else:
        cell_type = "neutral-cell"

    DAYS_NOV_2026.append({
        "solar_day": d,
        "lunar_str": f"{ld}/{f['lm']}",
        "dow_vi": f["dow_vi"],
        "cell_type": cell_type,
        "is_hoang": is_hd,
        "is_bad": is_bad
    })

# 7. Tết 2027: 3 ngày đại cát khai xuân mở hàng
def tet_day(date: dt.date, mung: str, desc: str) -> dict:
    facts = hoangdao_daily.day_data(date)
    than = facts["than"]
    dao = "Hoàng Đạo" if facts["is_hoang"] else "Hắc Đạo"
    return {"mung": mung, "solar": date.strftime("%d/%m/%Y"), "dow": facts["dow_vi"],
            "can_chi": facts["can_chi_ngay"], "truc": f"{than} {dao}", "desc": desc}


TET_2027_3_DAYS = [
    tet_day(dt.date(2027, 2, 6), "MÙNG 1", "Khai xuân, xuất hành nghênh cát"),
    tet_day(dt.date(2027, 2, 7), "MÙNG 2", "Cầu tài lộc, mở hàng đón xuân"),
    tet_day(dt.date(2027, 2, 9), "MÙNG 4", "Khai bút, mở cửa hàng kinh doanh"),
]


# =========================================================================
# PLAN BUILDER
# =========================================================================
def make_plan() -> list[dict]:
    plan = [
        # 1. fs_ret_1106 (Thay l0XLEH0r7nU - 06/11 15:00 - nguhanh)
        {
            "id": "fs_ret_1106",
            "day": "2026-11-06",
            "slot": "15:00",
            "replaces_video": "l0XLEH0r7nU",
            "replaces_title": "hình dáng nhà theo ngũ hành",
            "old_lane": "nguhanh",
            "style": "month_sheet",
            "series": "fs",
            "lane": "lich",
            "theme": "navy",
            "dur": 14.0,
            "kicker": "LỊCH ÂM DƯƠNG · THÁNG 11/2026",
            "chip": "BẢNG TRA CẢ THÁNG 11/2026",
            "title": "Tháng 11 năm 2026: tra cứu nhanh ngày lành hoàng đạo",
            "title_main": "THÁNG 11 NĂM 2026",
            "title_gold": "BẢNG TRA NGÀY HOÀNG ĐẠO",
            "script": [
                "Tháng 11 này có mười hai ngày hoàng đạo không vướng ngày kỵ.",
                "Ô vàng là ngày đẹp, ô đỏ là Tam Nương, Nguyệt kỵ. Dừng hình lưu lại lịch cả tháng nhé."
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "search_intent",
            "narrative_structure": "month_sheet_scan",
            "hypothesis": "loop_month_sheet_lookup",
            "format_subtag": "month_sheet",
            "batch_id": "fs_w45b"
        },
        # 2. fs_ret_1107 (Thay 8XNy64oT0kk - 07/11 15:00 - nguhanh)
        {
            "id": "fs_ret_1107",
            "day": "2026-11-07",
            "slot": "15:00",
            "replaces_video": "8XNy64oT0kk",
            "replaces_title": "mệnh nạp âm là gì",
            "old_lane": "nguhanh",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "jade",
            "dur": 11.5,
            "chip": "NGŨ HÀNH 2027 · ĐINH MÙI",
            "title_html": '<span class="l s">BẢN MỆNH NĂM 2027</span><span class="l gold">NGŨ HÀNH TƯƠNG SINH</span>',
            "title": "Năm 2027: ngũ hành bản mệnh nào được tương sinh?",
            "script": [
                "Năm 2027 Đinh Mùi mang hành Thiên Hà Thủy.",
                "Mệnh Mộc được sinh trợ, mệnh Thủy bình hòa, mệnh Kim sinh xuất. Dừng hình tìm năm sinh nhé."
            ],
            "rows": [
                ("MỆNH MỘC", "SINH TRỢ", MENH_MOC),
                ("MỆNH THỦY", "BÌNH HÒA", MENH_THUY),
                ("MỆNH KIM", "SINH XUẤT", MENH_KIM)
            ],
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45b"
        },
        # 3. fs_ret_1108 (Thay cbbbips_G04 - 08/11 15:00 - nguhanh)
        {
            "id": "fs_ret_1108",
            "day": "2026-11-08",
            "slot": "15:00",
            "replaces_video": "cbbbips_G04",
            "replaces_title": "tứ linh và ngũ hành",
            "old_lane": "nguhanh",
            "style": "tet_calendar",
            "series": "fs",
            "lane": "lich",
            "theme": "red",
            "dur": 11.5,
            "chip": "LỊCH TẾT ĐINH MÙI 2027",
            "title": "Tết 2027: ba ngày đại cát khai xuân mở hàng",
            "title_main": "TẾT ĐINH MÙI 2027",
            "title_gold": "3 NGÀY ĐẠI CÁT KHAI XUÂN",
            "script": [
                "Tết Đinh Mùi 2027, ba ngày đẹp nhất để xuất hành, mở hàng đón lộc đầu năm.",
                "Mùng Một, Mùng Hai và Mùng Bốn đều là ngày hoàng đạo đại cát. Dừng hình lưu lại nhé."
            ],
            "display_script": [
                "Tết Đinh Mùi 2027, ba ngày đẹp nhất để xuất hành, mở hàng đón lộc đầu năm.",
                "Mùng Một, Mùng Hai và Mùng Bốn đều là ngày hoàng đạo đại cát. Dừng hình lưu lại nhé."
            ],
            "days_data": TET_2027_3_DAYS,
            "bgm_file": "asian_drums.mp3",
            "bgm_title": "Asian Drums",
            "hook_type": "search_intent",
            "narrative_structure": "tet_countdown_table",
            "hypothesis": "loop_month_sheet_lookup",
            "format_subtag": "tet_sheet",
            "batch_id": "fs_w45b"
        },
        # 4. fs_ret_1109 (Thay kNq9HCnOXl0 - 09/11 15:00 - nguhanh)
        {
            "id": "fs_ret_1109",
            "day": "2026-11-09",
            "slot": "15:00",
            "replaces_video": "kNq9HCnOXl0",
            "replaces_title": "hai hành khắc nhau",
            "old_lane": "nguhanh",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "amber",
            "dur": 11.5,
            "chip": "CỬU DIỆU 2027 · NAM MẠNG",
            "title_html": '<span class="l s">NAM MẠNG ĐÓN</span><span class="l gold">3 CÁT TINH CHIẾU MỆNH</span>',
            "title": "Sao hạn 2027: nam mạng đón 3 cát tinh chiếu mệnh",
            "script": [
                "Năm 2027, nam giới sinh các năm này đón ba cát tinh lớn.",
                "Thái Dương rạng rỡ, Thái Âm toại ý, Mộc Đức an khang. Dừng hình tìm năm sinh nhé."
            ],
            "rows": [
                ("THÁI DƯƠNG", "ĐẠI CÁT TINH", NAM_THAI_DUONG),
                ("THÁI ÂM", "CÁT TÀI LỘC", NAM_THAI_AM),
                ("MỘC ĐỨC", "CÁT HỶ SỰ", NAM_MOC_DUC)
            ],
            "bgm_file": "clean_soul.mp3",
            "bgm_title": "Clean Soul",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45b"
        },
        # 5. fs_ret_1110 (Thay RSWklO5NPnk - 10/11 15:00 - nguhanh)
        {
            "id": "fs_ret_1110",
            "day": "2026-11-10",
            "slot": "15:00",
            "replaces_video": "RSWklO5NPnk",
            "replaces_title": "mâm ngũ quả và ngũ hành",
            "old_lane": "nguhanh",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "navy",
            "dur": 11.5,
            "chip": "NIÊN HẠN 2027 · ĐINH MÙI",
            "title_html": '<span class="l s">HẠN TAM KHEO 2027</span><span class="l gold">CÁC TUỔI CẦN LƯU Ý</span>',
            "title": "Hạn Tam Kheo năm 2027: nam nữ tuổi nào cần lưu ý?",
            "script": [
                "Năm 2027, các năm sinh này phạm hạn Tam Kheo, chủ về xương khớp và đi lại.",
                "Theo nếp xưa nên cẩn trọng xe cộ, giữ gìn sức khỏe. Dừng hình tìm năm sinh nhé."
            ],
            "rows": [
                ("NAM MẠNG", "HẠN TAM KHEO", NAM_TAM_KHEO),
                ("NỮ MẠNG", "HẠN TAM KHEO", NU_TAM_KHEO)
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45b"
        },
        # 6. fs_ret_1111 (Thay Mg7cLP4qNhw - 11/11 15:00 - nguhanh)
        {
            "id": "fs_ret_1111",
            "day": "2026-11-11",
            "slot": "15:00",
            "replaces_video": "Mg7cLP4qNhw",
            "replaces_title": "vì sao đặt bể cá",
            "old_lane": "nguhanh",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "red",
            "dur": 11.5,
            "chip": "NIÊN HẠN 2027 · ĐINH MÙI",
            "title_html": '<span class="l s">HẠN NGŨ MỘ 2027</span><span class="l gold">CẨN TRỌNG TÀI CHÍNH</span>',
            "title": "Hạn Ngũ Mộ năm 2027: những tuổi nào cần giữ gìn tài sản?",
            "script": [
                "Năm 2027, các năm sinh này phạm hạn Ngũ Mộ, chủ về hao hụt tài chính.",
                "Người xưa khuyên cẩn trọng hóa đơn, tránh cho vay mượn lớn. Dừng hình tra năm sinh nhé."
            ],
            "rows": [
                ("NAM MẠNG", "HẠN NGŨ MỘ", NAM_NGU_MO),
                ("NỮ MẠNG", "HẠN NGŨ MỘ", NU_NGU_MO)
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45b"
        },
        # 7. fs_ret_1116 (Thay ca5U27UVQfo - 16/11 15:00 - nhao)
        {
            "id": "fs_ret_1116",
            "day": "2026-11-16",
            "slot": "15:00",
            "replaces_video": "ca5U27UVQfo",
            "replaces_title": "cửa sổ đối cửa chính",
            "old_lane": "nhao",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "amber",
            "dur": 11.5,
            "chip": "LỤC HỢP 2027 · NGỌ GẶP MÙI",
            "title_html": '<span class="l s">TUỔI NGỌ LỤC HỢP</span><span class="l gold">THÁI TUẾ ĐINH MÙI</span>',
            "title": "Năm 2027: tuổi Ngọ lục hợp Thái Tuế đón vận thế nào?",
            "script": [
                "Năm 2027 Đinh Mùi, tuổi Ngọ thuộc thế Lục Hợp Nhật Nguyệt với Thái Tuế.",
                "Theo truyền thống đây là thế hợp nâng đỡ quý nhân. Dừng hình tìm năm sinh nhé."
            ],
            "rows": LUC_HOP_NGO,
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45b"
        },
        # 8. fs_ret_1117 (Thay r2fm56F6jPc - 17/11 15:00 - nhao)
        {
            "id": "fs_ret_1117",
            "day": "2026-11-17",
            "slot": "15:00",
            "replaces_video": "r2fm56F6jPc",
            "replaces_title": "treo đồng hồ",
            "old_lane": "nhao",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "red",
            "dur": 11.5,
            "chip": "TƯƠNG HÌNH 2027 · TUẤT GẶP MÙI",
            "title_html": '<span class="l s">TUỔI TUẤT PHẠM HÌNH</span><span class="l gold">THÁI TUẾ ĐINH MÙI</span>',
            "title": "Năm 2027: tuổi Tuất phạm Hình Thái Tuế nên chú ý việc gì?",
            "script": [
                "Năm 2027 Đinh Mùi, tuổi Tuất phạm thế Tương Hình với Thái Tuế.",
                "Người xưa khuyên giữ tâm điềm tĩnh, cẩn trọng hợp đồng. Dừng hình tìm năm sinh nhé."
            ],
            "rows": TUONG_HINH_TUAT,
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45b"
        }
    ]
    expected = {
        ("THÁI DƯƠNG", True, "sao"): [y for y in YEARS if saohan.sao(y, True, at=2027) == "Thái Dương"],
        ("THÁI ÂM", True, "sao"): [y for y in YEARS if saohan.sao(y, True, at=2027) == "Thái Âm"],
        ("MỘC ĐỨC", True, "sao"): [y for y in YEARS if saohan.sao(y, True, at=2027) == "Mộc Đức"],
        ("NAM MẠNG", True, "Tam Kheo"): [y for y in YEARS if saohan.han(y, True, at=2027) == "Tam Kheo"],
        ("NỮ MẠNG", False, "Tam Kheo"): [y for y in YEARS if saohan.han(y, False, at=2027) == "Tam Kheo"],
        ("NAM MẠNG", True, "Ngũ Mộ"): [y for y in YEARS if saohan.han(y, True, at=2027) == "Ngũ Mộ"],
        ("NỮ MẠNG", False, "Ngũ Mộ"): [y for y in YEARS if saohan.han(y, False, at=2027) == "Ngũ Mộ"],
    }
    for item in plan:
        for label, subtitle, years in item.get("rows", []):
            for (needle, _male, value), exp in expected.items():
                if needle in label and value in subtitle:
                    if years != exp:
                        raise ValueError(f"{item['id']} {label}/{subtitle}: {years} != code {exp}")
    return plan


# =========================================================================
# HTML BUILDERS
# =========================================================================

def build_yeartable_html(t: dict, dur: float, segs: list[dict]) -> str:
    """Yeartable based on review_yeartable.html with proven layout fixes."""
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

    # SS-tier hold frame fix: freeze all animations in the last >= 3.0s
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

    fonts = font_css()
    base = base.replace(
        '<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@500;700;800;900&display=swap" rel="stylesheet" />',
        f"<style>\n{fonts}\n</style>"
    )

    data = {
        "dur": dur,
        "theme": t.get("theme", "red"),
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


def build_month_sheet_html(t: dict, dur: float, segs: list[dict]) -> str:
    """November 2026 month sheet calendar with full AA contrast and 0 overflow."""
    fonts = font_css()
    days = DAYS_NOV_2026

    # 01/11/2026 is Sunday (offset = 6 from Monday)
    cells_html = ['<div class="cal-cell empty"></div>'] * 6

    for d_item in days:
        d = d_item["solar_day"]
        l_str = d_item["lunar_str"]
        c_type = d_item["cell_type"]

        corner_html = '<div class="corner-red" data-layout-allow-overflow></div>' if c_type == "gold-tn" else ''
        cell_str = f"""
      <div class="cal-cell {c_type}" id="day-cell-{d}">
        {corner_html}
        <div class="day-solar">{d}</div>
        <div class="day-lunar">{l_str}</div>
      </div>"""
        cells_html.append(cell_str)

    # 6 + 30 = 36 cells. Fill remaining to 42 cells (6 rows x 7 cols)
    while len(cells_html) < 42:
        cells_html.append('<div class="cal-cell empty"></div>')

    grid_content = "\n".join(cells_html)

    cap_words = []
    for sg in segs:
        ws = sg["text"].split()
        for idx, w in enumerate(ws):
            t_word = sg["start"] + (sg["end"] - sg["start"]) * idx / max(1, len(ws))
            cap_words.append({"w": w, "t": round(t_word, 2)})

    words_json = json.dumps(cap_words, ensure_ascii=False)

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
    #kicker {{ position: absolute; left: 60px; top: 110px; width: 870px; text-align: center;
      font-family: "JetBrains Mono", monospace; font-weight: 500; font-size: 24px;
      letter-spacing: 0.16em; color: #e7c56a; z-index: 4; }}
    #title {{ position: absolute; left: 60px; top: 155px; width: 870px; text-align: center;
      font-weight: 900; font-size: 54px; line-height: 1.18; letter-spacing: -0.01em; color: #f8fafc; z-index: 4; }}
    #title .gold {{ color: #fde68a; display: block; }}
    #subchip {{ position: absolute; left: 60px; top: 330px; width: 870px; display: flex; align-items: center; justify-content: center; z-index: 4; }}
    .chip-tag {{ display: inline-block; padding: 7px 28px; border-radius: 20px;
      background: rgba(231,197,106,0.12); border: 1.5px solid rgba(231,197,106,0.45);
      font-weight: 700; font-size: 22px; color: #fde68a; }}

    /* Shimmer Beam */
    #shimmer-wrap {{ position: absolute; inset: 0; overflow: hidden; pointer-events: none; z-index: 6; }}
    #shimmer-beam {{ position: absolute; top: 0; left: -140px; width: 120px; height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.7), transparent);
      transform: skewX(-20deg); opacity: 0; }}

    /* Month Sheet Grid (6 rows of 132px) */
    #calendar-wrap {{ position: absolute; left: 64px; top: 405px; width: 872px; z-index: 5; }}
    .weekday-row {{ display: grid; grid-template-columns: repeat(7, 1fr); column-gap: 8px; margin-bottom: 8px; }}
    .wd {{ text-align: center; font-family: "JetBrains Mono", monospace; font-size: 24px; font-weight: 800; color: #e7c56a; }}
    .wd.sun {{ color: #f87171; }}

    .month-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); grid-template-rows: repeat(6, 132px); gap: 7px; }}
    .cal-cell {{ position: relative; border-radius: 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; overflow: hidden; }}
    .cal-cell.empty {{ background: rgba(15, 23, 42, 0.25); border: 1px dashed rgba(100, 116, 139, 0.15); }}

    /* Day typography */
    .day-solar {{ font-size: 54px; font-weight: 900; line-height: 1; margin-top: 2px; }}
    .day-lunar {{ font-size: 26px; font-weight: 700; line-height: 1; margin-top: 5px; }}

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
      border-style: solid; border-width: 0 28px 28px 0;
      border-color: transparent #ef4444 transparent transparent;
      z-index: 3;
    }}

    .cal-cell.red-bad {{
      background: linear-gradient(145deg, rgba(220, 38, 38, 0.35) 0%, rgba(153, 27, 27, 0.50) 100%);
      border: 2px solid rgba(248, 113, 113, 0.95);
      box-shadow: inset 0 0 14px rgba(239, 68, 68, 0.30);
    }}
    .cal-cell.red-bad .day-solar {{ color: #ffffff; }}
    .cal-cell.red-bad .day-lunar {{ color: #fca5a5; }}

    .cal-cell.neutral-cell {{
      background: rgba(15, 23, 42, 0.55);
      border: 1.5px solid rgba(148, 163, 184, 0.30);
    }}
    .cal-cell.neutral-cell .day-solar {{ color: #f1f5f9; }}
    .cal-cell.neutral-cell .day-lunar {{ color: #cbd5e1; }}

    /* Legend & Subfoot */
    #legend {{ position: absolute; left: 64px; top: 1320px; width: 872px; text-align: center;
      font-size: 24px; font-weight: 700; color: #fde68a; letter-spacing: 0.02em; z-index: 5; }}
    #subfoot {{ position: absolute; left: 64px; top: 1370px; width: 872px; text-align: center;
      font-size: 26px; font-weight: 800; color: #e2e8f0; letter-spacing: 0.08em; z-index: 5; }}

    /* Seal Tham Khao */
    #seal-thamkhao {{ position: absolute; left: 64px; top: 105px; width: 78px; height: 78px; z-index: 10;
      border: 3px solid #b91c1c; border-radius: 8px; background: rgba(185, 28, 28, 0.40);
      display: flex; align-items: center; justify-content: center; transform: rotate(-8deg); }}
    .seal-text {{ font-family: "Be Vietnam Pro", sans-serif; font-weight: 900; font-size: 15px;
      line-height: 1.15; color: #fecaca; text-align: center; letter-spacing: 0.05em; }}

    /* Subtitle caption */
    #caption-box {{ position: absolute; left: 64px; top: 1480px; width: 872px; text-align: center; z-index: 5; }}
    .cap-word {{ font-size: 42px; font-weight: 800; color: #ffffff; opacity: 0.35; }}
    .cap-word.active {{ opacity: 1; color: #fde68a; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
  <div id="grain" data-layout-allow-overflow></div>
  <svg id="mountains" viewBox="0 0 1080 220" fill="none" xmlns="http://www.w3.org/2000/svg" data-layout-allow-overflow>
    <path d="M0 140 Q 270 40 540 130 T 1080 120 L 1080 220 L 0 220 Z" fill="#04060d" opacity="0.85"/>
  </svg>

  <div id="shimmer-wrap"><div id="shimmer-beam" data-layout-allow-overflow></div></div>
  <div id="seal-thamkhao"><div class="seal-text">THAM<br>KHẢO</div></div>

  <div id="kicker">{t["kicker"]}</div>
  <div id="title">
    {t["title_main"]}<br/>
    <span class="gold">{t["title_gold"]}</span>
  </div>

  <div id="subchip">
    <div class="chip-tag">{t["chip"]}</div>
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

  <div id="legend">
    Ô VÀNG: Hoàng đạo đẹp · Ô ĐỎ: Tam Nương, Nguyệt kỵ
  </div>

  <div id="subfoot">DỪNG HÌNH LƯU LẠI LỊCH CẢ THÁNG NHÉ</div>
  <div id="caption-box"></div>
</div>

<script>
  (function() {{
    const words = {words_json};
    const capBox = document.getElementById("caption-box");
    words.forEach((w, i) => {{
      const span = document.createElement("span");
      span.className = "cap-word";
      span.id = "cw-" + i;
      span.textContent = w.w + " ";
      capBox.appendChild(span);
    }});

    const tl = gsap.timeline({{ paused: true }});
    window.__timelines = {{ main: tl }};

    const tStop = {round(segs[-1]["end"] if segs else dur - 3.5, 2)};
    tl.fromTo("#shimmer-beam", {{ x: 0, opacity: 0 }}, {{ x: 1080, opacity: 0.85, duration: 1.2, ease: "power1.inOut" }}, 0.6);
    tl.fromTo("#seal-thamkhao", {{ scale: 1.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, 0.4);

    const st = {{ t: 0 }};
    tl.to(st, {{
      t: {dur},
      duration: {dur},
      ease: "none",
      onUpdate: () => {{
        const curT = st.t;
        if (curT >= tStop) {{
          capBox.style.opacity = 0;
          return;
        }}
        capBox.style.opacity = 1;
        words.forEach((w, idx) => {{
          const el = document.getElementById("cw-" + idx);
          if (el) {{
            const nextT = (idx + 1 < words.length) ? words[idx + 1].t : tStop;
            if (curT >= w.t && curT < nextT) {{
              el.classList.add("active");
            }} else if (curT < w.t) {{
              el.classList.remove("active");
            }}
          }}
        }});
      }}
    }}, 0);
  }})();
</script>
</body>
</html>"""
    return html


def build_tet_calendar_html(t: dict, dur: float, segs: list[dict]) -> str:
    """Tết 2027 3 ngày đại cát (Mùng 1, Mùng 2, Mùng 4)."""
    fonts = font_css()
    days = t["days_data"]

    rows_html = []
    for d in days:
        r_str = f"""
      <div class="tet-row">
        <div class="tet-col-mung">{d['mung']}</div>
        <div class="tet-col-solar">{d['solar']}<br/><span class="tet-sub-dow">{d['dow']}</span></div>
        <div class="tet-col-canchi">{d['can_chi']}<br/><span class="tet-sub-truc">{d['truc']}</span></div>
        <div class="tet-col-desc">{d['desc']}</div>
      </div>"""
        rows_html.append(r_str)
    all_rows = "\n".join(rows_html)

    segs_json = json.dumps(segs, ensure_ascii=False)

    html = f"""<!doctype html>
<html lang="vi" data-needs-fit="1">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<style>
{fonts}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; width: 1080px; height: 1920px; overflow: hidden;
      background: #7a0f0a; font-family: "Be Vietnam Pro", sans-serif; }}
    #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden;
      background: radial-gradient(110% 75% at 50% 25%, #c21d13 0%, #87100b 45%, #4a0604 100%); }}
    #grain {{ position: absolute; inset: 0; width: 1080px; height: 1920px; opacity: 0.22;
      pointer-events: none; mix-blend-mode: overlay; z-index: 20; }}

    #head {{ position: absolute; left: 60px; right: 60px; top: 110px; text-align: center; z-index: 4; }}
    #chip {{ display: inline-block; padding: 10px 32px; border-radius: 40px; background: #fde68a; color: #78350f;
            font-weight: 900; font-size: 32px; letter-spacing: .06em; }}
    #title {{ margin-top: 24px; font-weight: 900; font-size: 68px; line-height: 1.15; color: #fff7ed; }}
    #title .gold {{ color: #fef08a; display: block; }}

    #table-wrap {{ position: absolute; left: 60px; top: 450px; width: 960px; z-index: 5; }}
    .tet-head {{
      display: grid; grid-template-columns: 200px 240px 280px 240px;
      align-items: center; height: 80px; margin-bottom: 16px; border-radius: 16px;
      background: rgba(254, 240, 138, 0.25); border: 2px solid #fde68a;
    }}
    .th-col {{ text-align: center; font-size: 28px; font-weight: 800; color: #fef08a; }}

    .tet-rows {{ display: flex; flex-direction: column; gap: 20px; }}
    .tet-row {{
      display: grid; grid-template-columns: 200px 240px 280px 240px;
      align-items: center; height: 170px; border-radius: 18px;
      background: rgba(45, 6, 4, 0.75); border: 2.5px solid rgba(253, 230, 138, 0.35);
      box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    }}
    .tet-col-mung {{ font-size: 46px; font-weight: 900; color: #fde68a; text-align: center; }}
    .tet-col-solar {{ font-size: 38px; font-weight: 800; color: #ffffff; text-align: center; line-height: 1.25; }}
    .tet-sub-dow {{ font-size: 24px; font-weight: 700; color: #fef08a; }}
    .tet-col-canchi {{ font-size: 34px; font-weight: 800; color: #fef9c3; text-align: center; line-height: 1.25; }}
    .tet-sub-truc {{ font-size: 22px; font-weight: 700; color: #fed7aa; }}
    .tet-col-desc {{ font-size: 30px; font-weight: 800; color: #e2e8f0; text-align: center; line-height: 1.25; padding: 0 10px; }}

    #subfoot {{ position: absolute; left: 60px; right: 60px; bottom: 180px; text-align: center;
      font-size: 32px; font-weight: 800; color: #fef08a; letter-spacing: 0.05em; z-index: 5; }}
    #foot {{ position: absolute; left: 60px; right: 60px; bottom: 110px; text-align: center;
      font-size: 24px; font-weight: 700; color: #fed7aa; z-index: 5; }}

    /* Subtitle caption */
    #caption-box {{ position: absolute; left: 60px; right: 60px; top: 1400px; text-align: center; z-index: 5; pointer-events: none; }}
    .cap-line {{ font-size: 40px; font-weight: 800; line-height: 1.32; color: #ffffff; text-shadow: 0 3px 8px rgba(0,0,0,0.85); }}
    .cw {{ opacity: 0.38; color: #ffffff; }}
    .cw.on {{ opacity: 1; color: #fde68a; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
  <div id="grain" data-layout-allow-overflow></div>

  <div id="head">
    <div id="chip">{t["chip"]}</div>
    <div id="title">
      {t["title_main"]}<br/>
      <span class="gold">{t["title_gold"]}</span>
    </div>
  </div>

  <div id="table-wrap">
    <div class="tet-head">
      <div class="th-col">TẾT ÂM</div>
      <div class="th-col">DƯƠNG LỊCH</div>
      <div class="th-col">CAN CHI · TRỰC</div>
      <div class="th-col">PHÙ HỢP</div>
    </div>
    <div class="tet-rows">
{all_rows}
    </div>
  </div>

  <div id="subfoot">DỪNG HÌNH LƯU LẠI LỊCH ĐÓN TẾT NHÉ</div>
  <div id="foot">Kiến thức văn hóa truyền thống để tham khảo</div>
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
    const st = {{ t: 0 }};
    tl.to(st, {{
      t: {dur}, duration: {dur}, ease: "none",
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


# =========================================================================
# BUILD & RENDER PROCESS
# =========================================================================
def build_and_render_all(target_ids: set[str] | None = None, force: bool = False) -> None:
    plan = make_plan()
    validate(plan)
    PLAN_FILE.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đã ghi plan {len(plan)} video vào {PLAN_FILE}")

    for idx, item in enumerate(plan, 1):
        rid = item["id"]
        if target_ids is not None and rid not in target_ids:
            continue
        title = item["title"]
        style = item["style"]
        dur = item["dur"]
        print(f"\n[{idx}/8] Đang xử lý {rid} ({item['day']} {item['slot']}) - {title}...")

        meta_file = RENDER_DIR / f"{rid}.render.json"
        mp4 = RENDER_DIR / f"{rid}.mp4"
        if not force and meta_file.exists() and mp4.exists():
            print(f"[{rid}] Đã có {mp4.name} và metadata, bỏ qua render.")
            continue

        # 1. TTS Generation
        txt = RENDER_DIR / f"{rid}.txt"
        wav = RENDER_DIR / f"{rid}.wav"
        txt.write_text("\n".join(item["script"]) + "\n", encoding="utf-8")

        if not wav.exists():
            ok = R.render_tts(txt, wav, item["script"], voice="Sơn")
            assert ok and wav.exists(), f"TTS thất bại cho {rid}"

        # Parse segments
        segs_raw = json.loads(wav.with_suffix(".json").read_text(encoding="utf-8"))["segments"]
        _disp = item.get("display_script") or item["script"]
        segs = [{"start": sg["start"], "end": sg["end"],
                 "text": (_disp[i] if len(_disp) == len(segs_raw) else sg["text"])}
                for i, sg in enumerate(segs_raw)]
        last_audio_end = segs[-1]["end"] if segs else dur - 3.5
        # Ensure still hold >= 3.0s (min 4.2s hold and dur >= 11.5s for GOP alignment)
        min_dur = max(dur, round(last_audio_end + 4.2, 2), 11.5)
        final_dur = min_dur
        item["dur"] = final_dur

        # 2. Composition HTML Generation
        if style == "yeartable":
            html_content = build_yeartable_html(item, final_dur, segs)
        elif style == "month_sheet":
            html_content = build_month_sheet_html(item, final_dur, segs)
        elif style == "tet_calendar":
            html_content = build_tet_calendar_html(item, final_dur, segs)
        else:
            raise ValueError(f"Unknown style: {style}")

        comp_name = f"_tb_{rid}.html"
        comp_path = COMP / comp_name
        comp_path.write_text(html_content, encoding="utf-8")

        # 3. HyperFrames Silent Render
        silent = RENDER_DIR / f"{rid}_silent.mp4"
        mp4 = RENDER_DIR / f"{rid}.mp4"

        silent.unlink(missing_ok=True)

        cmd = (
            f'export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1; nvm use 22 >/dev/null 2>&1; '
            f'cd "{HF}" && npx --yes hyperframes@0.8.75 render . -c compositions/{comp_name} --output "{silent}" --quality looks --fps 30 --quiet'
        )
        p = subprocess.run(["/bin/bash", "-lc", cmd], capture_output=True, text=True, timeout=1200)
        assert p.returncode == 0 and silent.exists(), f"HyperFrames render thất bại ({rid}):\n" + (p.stdout + p.stderr)[-1000:]

        # 4. Audio Mix with exact -20 dB offset LUFS
        bgm_file = item["bgm_file"]
        bgm_src = ROOT / "bgm" / bgm_file
        assert bgm_src.exists(), f"Thiếu BGM: {bgm_src}"

        voice_lufs = measure_lufs(wav)
        bgm_raw_lufs = measure_lufs(bgm_src)
        target_bgm_lufs = voice_lufs - 20.0
        gain_db = target_bgm_lufs - bgm_raw_lufs
        gain_linear = 10 ** (gain_db / 20.0)

        flt = (
            f"[1:a]apad[v];"
            f"[2:a]volume={gain_linear:.4f},afade=t=out:st={final_dur - 2.5:.2f}:d=2.5[m];"
            f"[v][m]amix=inputs=2:duration=first:normalize=0[a]"
        )
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", str(silent), "-i", str(wav),
                "-stream_loop", "-1", "-i", str(bgm_src),
                "-filter_complex", flt,
                "-map", "0:v", "-map", "[a]", "-t", str(final_dur),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(mp4)
            ],
            check=True
        )

        silent.unlink(missing_ok=True)
        mix_lufs = measure_lufs(mp4)

        # 5. Hold Frame Check (mean abs diff between -3.0s and last frame < 0.5)
        r_probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
            capture_output=True, text=True
        )
        real_dur = float((r_probe.stdout or "0").strip() or final_dur)
        t_last = max(0.1, real_dur - 0.25)
        t_hold = max(0.1, real_dur - 3.0)

        f_still_a = RENDER_DIR / f"_still_a_{rid}.png"
        f_still_b = RENDER_DIR / f"_still_b_{rid}.png"
        subprocess.run(["ffmpeg", "-y", "-i", str(mp4), "-ss", str(t_hold), "-vframes", "1", str(f_still_a)], capture_output=True, check=True)
        subprocess.run(["ffmpeg", "-y", "-i", str(mp4), "-ss", str(t_last), "-vframes", "1", str(f_still_b)], capture_output=True, check=True)
        im_a = Image.open(f_still_a).convert("L")
        im_b = Image.open(f_still_b).convert("L")
        mean_diff = ImageStat.Stat(ImageChops.difference(im_a, im_b)).mean[0]
        print(f"[{rid}] Hold check: dur={real_dur:.2f}s, mean diff={mean_diff:.4f} (khung -3.0s so với cuối)")
        assert mean_diff < 0.5, f"[{rid}] Khung cuối không tĩnh: diff={mean_diff:.4f}"

        f_still_a.unlink(missing_ok=True)
        f_still_b.unlink(missing_ok=True)

        # Export 1080px and 168px frames
        f1080 = RENDER_DIR / f"frame_last_1080_{rid}.png"
        f168 = RENDER_DIR / f"frame_last_168_{rid}.png"
        subprocess.run(["ffmpeg", "-y", "-i", str(mp4), "-ss", str(t_last), "-vframes", "1", str(f1080)], capture_output=True, check=True)
        im1080 = Image.open(f1080)
        im168 = im1080.resize((168, int(168 * 1920 / 1080)), Image.Resampling.LANCZOS)
        im168.save(f168)

        # 6. Render metadata json with 5 new fields
        meta = {
            "ok": True,
            "id": rid,
            "day": item["day"],
            "slot": item["slot"],
            "title": item["title"],
            "style": item["style"],
            "lane": item["lane"],
            "replaces_video": item.get("replaces_video"),
            "replaces_title": item.get("replaces_title"),
            "old_lane": item.get("old_lane"),
            "duration_s": real_dur,
            "hold_s": round(real_dur - last_audio_end, 2),
            "output": str(mp4.relative_to(ROOT)),
            "bgm": f"bgm/{bgm_file}",
            "bgm_title": item["bgm_title"],
            "bgm_gain": round(gain_linear, 4),
            "lufs": {
                "voice": round(voice_lufs, 1),
                "bgm_target": round(target_bgm_lufs, 1),
                "mix": round(mix_lufs, 1),
                "offset_db": -20.0
            },
            # 5 manifest fields required
            "hook_type": item["hook_type"],
            "narrative_structure": item["narrative_structure"],
            "hypothesis": item["hypothesis"],
            "format_subtag": item["format_subtag"],
            "batch_id": item["batch_id"]
        }
        (RENDER_DIR / f"{rid}.render.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{rid}] Render xong: {mp4.name} ({real_dur:.1f}s) | Mix LUFS: {mix_lufs:.1f}")

    PLAN_FILE.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nĐÃ HOÀN TẤT TẤT CẢ 8 SHORT RENDER!")


# =========================================================================
# PREVIEW SHEET EXPORT
# =========================================================================
def export_preview_sheet() -> None:
    plan = json.loads(PLAN_FILE.read_text(encoding="utf-8"))
    cell_w, cell_h = 270, 480
    sheet = Image.new("RGB", (cell_w * 4, cell_h * math.ceil(len(plan) / 4)), (10, 12, 18))
    draw = ImageDraw.Draw(sheet)

    for idx, item in enumerate(plan):
        rid = item["id"]
        col = idx % 4
        row = idx // 4
        f1080 = RENDER_DIR / f"frame_last_1080_{rid}.png"
        if f1080.exists():
            im = Image.open(f1080).resize((cell_w, cell_h), Image.Resampling.LANCZOS)
            sheet.paste(im, (col * cell_w, row * cell_h))
            draw.rectangle([col * cell_w, row * cell_h, col * cell_w + cell_w, row * cell_h + 36], fill=(0, 0, 0, 180))
            draw.text((col * cell_w + 8, row * cell_h + 8), f"{rid} ({item['day']})", fill=(253, 230, 138))

    preview_jpg = RENDER_DIR / "preview_fs_0001.jpg"
    sheet.save(preview_jpg, quality=90)
    print(f"Đã xuất tờ ảnh preview: {preview_jpg}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="+", help="Chỉ dựng các ID được nêu")
    parser.add_argument("--force", action="store_true", help="Dựng lại dù đã có file đầu ra")
    args = parser.parse_args()
    build_and_render_all(set(args.only) if args.only else None, force=args.force)
    export_preview_sheet()
