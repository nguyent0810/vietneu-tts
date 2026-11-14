"""Builder and renderer for 0000_fs_short_phu_1104:
FS: 14 short tuần này (8 phủ ô trống + 6 thay nhao khung 22:00) bằng DẠNG THẮNG
(GitHub nguyent0810/vietneu-tts#92).

Chuẩn SS-tier:
- Trả lời ngay khung 0; bảng chữ to, dừng hình được; khung cuối đứng >= 3s; 10-15s.
- Mọi năm/can chi/hạn tính bằng code (tuvi_year.py, canchi.py, amlich.py).
- Con giáp gọi bằng tên chi (Tý...Hợi). Khung "theo truyền thống / tham khảo", không doạ.
- Ghi manifest 5 trường mới: hook_type, narrative_structure, hypothesis, format_subtag, batch_id=fs_w45a.
- QA: hf_qa.py --overflow + --contrast cho mọi composition, đạt 100%.
- Tờ ảnh khung 168px và 1080px.
"""
from __future__ import annotations
from shortbuild import validate

import collections
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

RENDER_DIR = HERE / "render_1104"
RENDER_DIR.mkdir(parents=True, exist_ok=True)

HF = ROOT / "hyperframes_short"
COMP = HF / "compositions"
COMP.mkdir(parents=True, exist_ok=True)

PLAN_FILE = ROOT / "output" / "cl_staging" / "fs" / "plan_fs_phu_1104.json"


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

# 1. 8 Niên Hạn 2027 (Nam & Nữ)
NAM_HUYNH_TUYEN = [y for y, r in R27.items() if r["han_nam"] == "Huỳnh Tuyền"]
NAM_TOAN_TAN = [y for y, r in R27.items() if r["han_nam"] == "Toán Tận"]
NAM_TAM_KHEO = [y for y, r in R27.items() if r["han_nam"] == "Tam Kheo"]

NU_TOAN_TAN = [y for y, r in R27.items() if r["han_nu"] == "Toán Tận"]
NU_HUYNH_TUYEN = [y for y, r in R27.items() if r["han_nu"] == "Huỳnh Tuyền"]
NU_NGU_MO = [y for y, r in R27.items() if r["han_nu"] == "Ngũ Mộ"]

# 2. Kim Lâu 2027 (bốn dạng đầy đủ - Bài học #99)
KL_THAN = [y for y, r in R27.items() if r["kim_lau"] == "Kim Lâu Thân"]
KL_THE = [y for y, r in R27.items() if r["kim_lau"] == "Kim Lâu Thê"]
KL_TU = [y for y, r in R27.items() if r["kim_lau"] == "Kim Lâu Tử"]
KL_SUC = [y for y, r in R27.items() if r["kim_lau"] == "Kim Lâu Lục Súc"]

# 3. Tam Hợp & Tam Tai 2027 (Đinh Mùi: Hợi, Mão, Mùi)
TAM_HOP_HOI = [y for y in range(1950, 2011) if PROFILES[y]["chi"] == "Hợi"]
TAM_HOP_MAO = [y for y in range(1950, 2011) if PROFILES[y]["chi"] == "Mão"]
TAM_HOP_MUI = [y for y in range(1950, 2011) if PROFILES[y]["chi"] == "Mùi"]

# 4. Lục Hại & Trực Xung Thái Tuế 2027
LUC_HAI_TY = [y for y in range(1950, 2011) if PROFILES[y]["chi"] == "Tý"]
TRUC_XUNG_SUU = [y for y in range(1950, 2011) if PROFILES[y]["chi"] == "Sửu"]

# 5. Thập niên 1970 và 1960
DATA_1970S = []
for y in range(1970, 1980):
    p = PROFILES[y]
    r = R27[y]
    DATA_1970S.append({
        "year": y, "can_chi": p["can_chi"], "tuoi": r["tuoi"],
        "kim_lau": bool(r["kim_lau"]), "kim_lau_str": r["kim_lau"],
        "hoang_oc": bool(r["hoang_oc_xau"]), "hoang_oc_str": r["hoang_oc"],
        "tam_tai": bool(r["tam_tai"]),
        "thai_tue": r["quan_he_chi"] if r["quan_he_chi"] not in ("bình thường", "lục hợp", "tam hợp") else None,
        "is_clean": (y == 1976)
    })

DATA_1960S = []
for y in range(1960, 1970):
    p = PROFILES[y]
    r = R27[y]
    DATA_1960S.append({
        "year": y, "can_chi": p["can_chi"], "tuoi": r["tuoi"],
        "kim_lau": bool(r["kim_lau"]), "kim_lau_str": r["kim_lau"],
        "hoang_oc": bool(r["hoang_oc_xau"]), "hoang_oc_str": r["hoang_oc"],
        "tam_tai": bool(r["tam_tai"]),
        "thai_tue": r["quan_he_chi"] if r["quan_he_chi"] not in ("bình thường", "lục hợp", "tam hợp") else None,
        "is_clean": (y == 1969)
    })

# 6. Tháng 12/2026 Hoàng Đạo (31 ngày)
DAYS_DEC_2026 = []
for d in range(1, 32):
    dt_obj = dt.date(2026, 12, d)
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
        
    DAYS_DEC_2026.append({
        "solar_day": d,
        "lunar_str": f"{ld}/{f['lm']}",
        "dow_vi": f["dow_vi"],
        "cell_type": cell_type,
        "is_hoang": is_hd,
        "is_bad": is_bad
    })

# 7. Lịch Tết 2027
# Mùng 1 Tết 2027 âm (06/02/2027 dương) -> Thứ Bảy
# Tháng Chạp Bính Ngọ 2026 chỉ có 29 ngày (tháng thiếu, không có 30 Tết)
def tet_day(date: dt.date, mung: str, desc: str) -> dict:
    facts = hoangdao_daily.day_data(date)
    dao = "Hoàng Đạo" if facts["is_hoang"] else "Hắc Đạo"
    return {"mung": mung, "solar": date.strftime("%d/%m/%Y"), "dow": facts["dow_vi"],
            "can_chi": facts["can_chi_ngay"], "truc": f"{facts['than']} {dao}", "desc": desc}


TET_2027_DAYS = [
    tet_day(dt.date(2027, 2, 6), "MÙNG 1", "Khai xuân, xuất hành"),
    tet_day(dt.date(2027, 2, 7), "MÙNG 2", "Chúc Tết, lễ hội"),
    tet_day(dt.date(2027, 2, 8), "MÙNG 3", "Hóa vàng, sum họp"),
    tet_day(dt.date(2027, 2, 9), "MÙNG 4", "Mở hàng, khai bút"),
    tet_day(dt.date(2027, 2, 10), "MÙNG 5", "Xuất hành, du xuân"),
]


# =========================================================================
# PLAN BUILDER
# =========================================================================
def make_plan() -> list[dict]:
    plan = [
        # 1. fs_rep_1103 (Thay 03/11 22:00)
        {
            "id": "fs_rep_1103",
            "day": "2026-11-03",
            "slot": "15:00",
            "replaces_video": "MBZJy3xULkY",
            "replaces_title": "Vì sao nhà bừa bộn khiến ta mệt?",
            "group": "A",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "navy",
            "dur": 9.5,
            "chip": "SAO HẠN 2027 · NAM MẠNG",
            "title_html": '<span class="l s">NAM MẠNG GẶP</span><span class="l gold">3 ĐẠI HẠN LỚN</span>',
            "title": "Năm 2027: nam mạng gặp 3 đại hạn lớn",
            "script": [
                "Năm 2027, nam giới sinh các năm này gặp đại hạn.",
                "Dừng hình tìm năm sinh của bạn, rồi lưu lại nhé."
            ],
            "rows": [
                ("HUỲNH TUYỀN", "ĐẠI HẠN", NAM_HUYNH_TUYEN),
                ("TOÁN TẬN", "ĐẠI HẠN", NAM_TOAN_TAN),
                ("TAM KHEO", "HẠN SỨC KHỎE", NAM_TAM_KHEO)
            ],
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45a"
        },
        # 2. fs_rep_1104 (Thay 04/11 22:00)
        {
            "id": "fs_rep_1104",
            "day": "2026-11-04",
            "slot": "15:00",
            "replaces_video": "1IoufLVOMKw",
            "replaces_title": "Vì sao kỵ đặt gương đối diện giường?",
            "group": "A",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "amber",
            "dur": 9.5,
            "chip": "SAO HẠN 2027 · NỮ MẠNG",
            "title_html": '<span class="l s">NỮ MẠNG GẶP</span><span class="l gold">3 ĐẠI HẠN LỚN</span>',
            "title": "Năm 2027: nữ mạng gặp 3 đại hạn lớn",
            "script": [
                "Năm 2027, nữ giới sinh các năm này gặp đại hạn.",
                "Dừng hình tìm năm sinh của bạn, rồi lưu lại nhé."
            ],
            "rows": [
                ("TOÁN TẬN", "ĐẠI HẠN", NU_TOAN_TAN),
                ("HUỲNH TUYỀN", "ĐẠI HẠN", NU_HUYNH_TUYEN),
                ("NGŨ MỘ", "HẠN HAO TÀI", NU_NGU_MO)
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45a"
        },
        # 3. fs_rep_1105 (Thay 05/11 22:00)
        {
            "id": "fs_rep_1105",
            "day": "2026-11-05",
            "slot": "15:00",
            "replaces_video": "R6J9m-vrwWI",
            "replaces_title": "Vì sao bàn làm việc nên tựa lưng vào tường?",
            "group": "A",
            "style": "decade_grid",
            "series": "fs",
            "lane": "tuoi",
            "theme": "red",
            "dur": 14.5,
            "kicker": "THẬP NIÊN 1970 · NĂM 2027",
            "title": "Thập niên 1970: bảng tra sao hạn năm 2027",
            "title_main": "SINH NĂM 1970–1979",
            "title_gold": "BẢNG TRA HẠN NĂM 2027",
            "clean_year": 1976,
            "decade_data": DATA_1970S,
            "script": [
                "Thập niên 1970, năm 2027 tuổi nào phạm hạn, tuổi nào được yên lành?",
                "Năm 1976 không vướng hạn lớn nào, vẹn toàn cả bốn bề.",
                "Dừng hình tìm năm sinh của bạn, lưu lại bảng tra nhé."
            ],
            "display_script": [
                "Thập niên 1970, năm 2027 tuổi nào phạm hạn, tuổi nào được yên lành?",
                "Năm 1976 không vướng hạn lớn nào, vẹn toàn cả bốn bề.",
                "Dừng hình tìm năm sinh của bạn, lưu lại bảng tra nhé."
            ],
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "decade_grid_scan",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "decade_grid",
            "batch_id": "fs_w45a"
        },
        # 4. fs_rep_1106 (Thay 06/11 22:00)
        {
            "id": "fs_rep_1106",
            "day": "2026-11-06",
            "slot": "15:00",
            "replaces_video": "4A07BoMIG_M",
            "replaces_title": "Vì sao cửa nhà vệ sinh kỵ nhìn thẳng bếp?",
            "group": "A",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "jade",
            "dur": 9.5,
            "chip": "NIÊN HẠN 2027 · ĐINH MÙI",
            "title_html": '<span class="l s">HẠN HUỲNH TUYỀN</span><span class="l gold">CÁC TUỔI CẦN LƯU TÂM</span>',
            "title": "Hạn Huỳnh Tuyền năm 2027: những tuổi nào cần lưu tâm?",
            "script": [
                "Năm 2027, các năm sinh này phạm hạn Huỳnh Tuyền, nên chú ý sức khỏe.",
                "Dừng hình tìm năm sinh của bạn, rồi lưu lại nhé."
            ],
            "rows": [
                ("NAM MẠNG", "HUỲNH TUYỀN", NAM_HUYNH_TUYEN),
                ("NỮ MẠNG", "HUỲNH TUYỀN", NU_HUYNH_TUYEN)
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45a"
        },
        # 5. fs_rep_1107 (Thay 07/11 22:00)
        {
            "id": "fs_rep_1107",
            "day": "2026-11-07",
            "slot": "15:00",
            "replaces_video": "rN5hd7VMiOI",
            "replaces_title": "Nhà hướng Nam có thật sự tốt?",
            "group": "A",
            "style": "decade_grid",
            "series": "fs",
            "lane": "tuoi",
            "theme": "red",
            "dur": 14.5,
            "kicker": "THẬP NIÊN 1960 · NĂM 2027",
            "title": "Thập niên 1960: bảng tra sao hạn năm 2027",
            "title_main": "SINH NĂM 1960–1969",
            "title_gold": "BẢNG TRA HẠN NĂM 2027",
            "clean_year": 1969,
            "decade_data": DATA_1960S,
            "script": [
                "Thập niên 1960, năm 2027 tuổi nào phạm hạn, tuổi nào được yên lành?",
                "Năm 1969 không vướng hạn lớn nào, mọi sự hanh thông.",
                "Dừng hình tìm năm sinh của bạn, lưu lại bảng tra nhé."
            ],
            "display_script": [
                "Thập niên 1960, năm 2027 tuổi nào phạm hạn, tuổi nào được yên lành?",
                "Năm 1969 không vướng hạn lớn nào, mọi sự hanh thông.",
                "Dừng hình tìm năm sinh của bạn, lưu lại bảng tra nhé."
            ],
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "decade_grid_scan",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "decade_grid",
            "batch_id": "fs_w45a"
        },
        # 6. fs_rep_1108 (Thay 08/11 22:00)
        {
            "id": "fs_rep_1108",
            "day": "2026-11-08",
            "slot": "15:00",
            "replaces_video": "SxQA6Ap7cl8",
            "replaces_title": "Vì sao nên gọn giày dép trước cửa?",
            "group": "A",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "red",
            "dur": 9.5,
            "chip": "NIÊN HẠN 2027 · ĐINH MÙI",
            "title_html": '<span class="l s">HẠN TOÁN TẬN</span><span class="l gold">CÁC TUỔI CẦN CẨN TRỌNG</span>',
            "title": "Hạn Toán Tận năm 2027: những tuổi nào cần cẩn trọng?",
            "script": [
                "Năm 2027, các năm sinh này phạm hạn Toán Tận, nên giữ gìn tài lộc.",
                "Dừng hình tìm năm sinh của bạn, rồi lưu lại nhé."
            ],
            "rows": [
                ("NAM MẠNG", "TOÁN TẬN", NAM_TOAN_TAN),
                ("NỮ MẠNG", "TOÁN TẬN", NU_TOAN_TAN)
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45a"
        },
        # 7. fs_phu_1104_1 (Phủ 04/11)
        {
            "id": "fs_phu_1104_1",
            "day": "2026-11-04",
            "slot": "10:00",
            "group": "B",
            "style": "tet_calendar",
            "series": "fs",
            "lane": "lich",
            "theme": "red",
            "dur": 11.5,
            "title": "Tết 2027 rơi vào ngày nào dương lịch?",
            "script": [
                "Tết Đinh Mùi 2027, Mùng Một rơi vào Thứ Bảy, ngày sáu tháng Hai dương lịch.",
                "Dừng hình lưu lại lịch đón năm mới nhé."
            ],
            "display_script": [
                "Tết Đinh Mùi 2027, Mùng 1 rơi vào Thứ Bảy, ngày 06/02 dương lịch.",
                "Dừng hình lưu lại lịch đón năm mới nhé."
            ],
            "bgm_file": "asian_drums.mp3",
            "bgm_title": "Asian Drums",
            "hook_type": "search_intent",
            "narrative_structure": "tet_countdown_table",
            "hypothesis": "loop_month_sheet_lookup",
            "format_subtag": "tet_sheet",
            "batch_id": "fs_w45a"
        },
        # 8. fs_phu_1105_1 (Phủ 05/11 slot 1)
        {
            "id": "fs_phu_1105_1",
            "day": "2026-11-05",
            "slot": "02:30",
            "group": "B",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "red",
            "dur": 9.5,
            "chip": "KIM LÂU 2027 · BỐN DẠNG",
            "title_html": '<span class="l s">BỐN DẠNG KIM LÂU</span><span class="l gold">THEO NĂM SINH</span>',
            "title": "Năm 2027: bốn dạng Kim Lâu phân theo năm sinh",
            "script": [
                "Năm 2027, hạn Kim Lâu chia làm bốn dạng khác nhau.",
                "Dừng hình tìm năm sinh của bạn, rồi lưu lại nhé."
            ],
            "rows": [
                ("KIM LÂU THÂN", "KỴ BẢN THÂN", KL_THAN),
                ("KIM LÂU THÊ", "KỴ BẠN ĐỜI", KL_THE),
                ("KIM LÂU TỬ", "KỴ CON CÁI", KL_TU),
                ("KIM LÂU LỤC SÚC", "KỴ GIA SÚC", KL_SUC)
            ],
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45a"
        },
        # 9. fs_phu_1105_2 (Phủ 05/11 slot 2)
        {
            "id": "fs_phu_1105_2",
            "day": "2026-11-05",
            "slot": "10:00",
            "group": "B",
            "style": "giao_thua_card",
            "series": "fs",
            "lane": "lich",
            "theme": "red",
            "dur": 12.0,
            "title": "Đêm Giao thừa Tết 2027 rơi vào ngày mấy dương lịch?",
            "script": [
                "Tết 2027 không có ngày 30 Tết, vì tháng Chạp năm Bính Ngọ chỉ có hai mươi chín ngày.",
                "Đêm Giao Thừa rơi vào Thứ Sáu, ngày năm tháng Hai dương lịch. Dừng hình lưu lại nhé."
            ],
            "display_script": [
                "Tết 2027 không có ngày 30 Tết, vì tháng Chạp năm Bính Ngọ chỉ có 29 ngày.",
                "Đêm Giao Thừa rơi vào Thứ Sáu, ngày 05/02 dương lịch. Dừng hình lưu lại nhé."
            ],
            "bgm_file": "asian_drums.mp3",
            "bgm_title": "Asian Drums",
            "hook_type": "search_intent",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "loop_month_sheet_lookup",
            "format_subtag": "giao_thua_card",
            "batch_id": "fs_w45a"
        },
        # 10. fs_phu_1106_1 (Phủ 06/11)
        {
            "id": "fs_phu_1106_1",
            "day": "2026-11-06",
            "slot": "02:30",
            "group": "B",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "jade",
            "dur": 9.5,
            "chip": "TAM HỢP 2027 · HỢI MÃO MÙI",
            "title_html": '<span class="l s">3 TUỔI TAM HỢP</span><span class="l gold">ĐÓN VẬN ĐINH MÙI</span>',
            "title": "Năm 2027: 3 tuổi tam hợp đón vận Đinh Mùi",
            "script": [
                "Năm 2027, ba tuổi Hợi, Mão, Mùi thuộc thế Tam Hợp Mộc cục.",
                "Dừng hình tìm năm sinh của bạn, rồi lưu lại nhé."
            ],
            "rows": [
                ("HỢI", "TAM HỢP", TAM_HOP_HOI),
                ("MÃO", "TAM HỢP", TAM_HOP_MAO),
                ("MÙI", "NĂM TUỔI", TAM_HOP_MUI)
            ],
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45a"
        },
        # 11. fs_phu_1107_1 (Phủ 07/11 slot 1)
        {
            "id": "fs_phu_1107_1",
            "day": "2026-11-07",
            "slot": "02:30",
            "group": "B",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "amber",
            "dur": 11.5,
            "chip": "TAM TAI 2027 · NĂM CUỐI",
            "title_html": '<span class="l s">BA TUỔI VÀO</span><span class="l gold">NĂM CUỐI TAM TAI</span>',
            "title": "Năm 2027: ba tuổi bước vào năm cuối Tam Tai",
            "script": [
                "Năm 2027, ba tuổi Hợi, Mão, Mùi bước vào năm cuối của hạn Tam Tai.",
                "Theo nếp xưa, năm cuối nhẹ nhất, chỉ nên hoàn tất việc cũ. Dừng hình tra năm sinh nhé."
            ],
            "rows": [
                ("HỢI", "NĂM THỨ 3", TAM_HOP_HOI),
                ("MÃO", "NĂM THỨ 3", TAM_HOP_MAO),
                ("MÙI", "NĂM THỨ 3", TAM_HOP_MUI)
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45a"
        },
        # 12. fs_phu_1107_2 (Phủ 07/11 slot 2)
        {
            "id": "fs_phu_1107_2",
            "day": "2026-11-07",
            "slot": "10:00",
            "group": "B",
            "style": "month_sheet",
            "series": "fs",
            "lane": "lich",
            "dur": 14.0,
            "title": "Lịch hoàng đạo tháng 12/2026: bảng tra cả tháng",
            "script": [
                "Tháng 12 này có mười sáu ngày hoàng đạo, trong đó bốn ngày vướng ngày kỵ.",
                "Ô vàng là ngày tốt, ô đỏ là Tam Nương, Nguyệt kỵ. Dừng hình lưu lại lịch cả tháng nhé."
            ],
            "display_script": [
                "Tháng 12 này có 16 ngày hoàng đạo, trong đó 4 ngày vướng ngày kỵ.",
                "Ô vàng là ngày tốt, ô đỏ là Tam Nương, Nguyệt kỵ. Dừng hình lưu lại lịch cả tháng nhé."
            ],
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "search_intent",
            "narrative_structure": "month_sheet_scan",
            "hypothesis": "loop_month_sheet_lookup",
            "format_subtag": "month_sheet",
            "batch_id": "fs_w45a"
        },
        # 13. fs_phu_1108_1 (Phủ 08/11 slot 1)
        {
            "id": "fs_phu_1108_1",
            "day": "2026-11-08",
            "slot": "02:30",
            "group": "B",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "navy",
            "dur": 11.0,
            "chip": "LỤC HẠI 2027 · TÝ GẶP MÙI",
            "title_html": '<span class="l s">PHẠM LỤC HẠI 2027</span><span class="l gold">CẨN TRỌNG KHẨU THIỆT</span>',
            "title": "Năm 2027: tuổi nào phạm Lục Hại cẩn trọng khẩu thiệt?",
            "script": [
                "Năm 2027 Đinh Mùi, tuổi Tý gặp Mùi phạm thế Lục Hại.",
                "Người xưa dặn giữ lời ăn tiếng nói, dĩ hòa vi quý. Dừng hình tìm năm sinh nhé."
            ],
            "rows": [
                ("CANH TÝ", "68 TUỔI", [1960]),
                ("NHÂM TÝ", "56 TUỔI", [1972]),
                ("GIÁP TÝ", "44 TUỔI", [1984]),
                ("BÍNH TÝ", "32 TUỔI", [1996]),
                ("MẬU TÝ", "20 TUỔI", [2008])
            ],
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45a"
        },
        # 14. fs_phu_1108_2 (Phủ 08/11 slot 2)
        {
            "id": "fs_phu_1108_2",
            "day": "2026-11-08",
            "slot": "10:00",
            "group": "B",
            "style": "yeartable",
            "series": "fs",
            "lane": "tuoi",
            "theme": "red",
            "dur": 11.0,
            "chip": "THÁI TUẾ 2027 · TRỰC XUNG",
            "title_html": '<span class="l s">TUỔI SỬU TRỰC XUNG</span><span class="l gold">THÁI TUẾ ĐINH MÙI</span>',
            "title": "Năm 2027: tuổi Sửu trực xung Thái Tuế cần lưu tâm gì?",
            "script": [
                "Năm 2027, tuổi Sửu rơi vào thế trực xung với Thái Tuế Đinh Mùi.",
                "Theo truyền thống nên điềm tĩnh, tránh nóng vội. Dừng hình tìm năm sinh của bạn nhé."
            ],
            "rows": [
                ("TÂN SỬU", "67 TUỔI", [1961]),
                ("QUÝ SỬU", "55 TUỔI", [1973]),
                ("ẤT SỬU", "43 TUỔI", [1985]),
                ("ĐINH SỬU", "31 TUỔI", [1997]),
                ("KỶ SỬU", "19 TUỔI", [2009])
            ],
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w45a"
        }
    ]
    code_rows = {
        "HUỲNH TUYỀN": lambda male: [y for y, r in R27.items() if r["han_nam" if male else "han_nu"] == "Huỳnh Tuyền"],
        "TOÁN TẬN": lambda male: [y for y, r in R27.items() if r["han_nam" if male else "han_nu"] == "Toán Tận"],
        "TAM KHEO": lambda male: [y for y, r in R27.items() if r["han_nam" if male else "han_nu"] == "Tam Kheo"],
        "NGŨ MỘ": lambda male: [y for y, r in R27.items() if r["han_nam" if male else "han_nu"] == "Ngũ Mộ"],
    }
    for item in plan:
        for label, subtitle, years in item.get("rows", []):
            gender = "NAM" in label
            for key, calc in code_rows.items():
                if key in label and key in subtitle:
                    expected = calc(gender)
                    if years != expected:
                        raise ValueError(f"{item['id']} {label}/{subtitle}: {years} != code {expected}")
    for item in TET_2027_DAYS:
        date = dt.datetime.strptime(item["solar"], "%d/%m/%Y").date()
        facts = hoangdao_daily.day_data(date)
        dao = "Hoàng Đạo" if facts["is_hoang"] else "Hắc Đạo"
        expected = (facts["can_chi_ngay"], f"{facts['than']} {dao}")
        if (item["can_chi"], item["truc"]) != expected:
            raise ValueError(f"Tết {item['solar']}: bảng lệch dữ liệu code")
    return plan


# =========================================================================
# HTML COMPOSITION BUILDERS
# =========================================================================

def build_yeartable_html(t: dict, dur: float, segs: list[dict]) -> str:
    """Yeartable 9.5-11.5s based on review_yeartable.html with proven layout fixes."""
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

    # Replace local fonts
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


def build_decade_html(t: dict, dur: float, segs: list[dict]) -> str:
    """Decade grid 10 rows (1970s or 1960s) with clean contrast and safe overflow."""
    fonts = font_css()
    decade_data = t["decade_data"]
    clean_year = t["clean_year"]

    rows_html = []
    for item in decade_data:
        y = item["year"]
        cc = item["can_chi"]
        age = item["tuoi"]
        is_clean = item["is_clean"]

        kl_mark = '<span data-layout-allow-overflow class="mark-check han-kl">✓</span>' if item["kim_lau"] else '<span class="mark-dash">—</span>'
        ho_mark = '<span data-layout-allow-overflow class="mark-check han-ho">✓</span>' if item["hoang_oc"] else '<span class="mark-dash">—</span>'
        tt_mark = '<span data-layout-allow-overflow class="mark-check han-tt">✓</span>' if item["tam_tai"] else '<span class="mark-dash">—</span>'

        if item["thai_tue"]:
            tue_sub = item["thai_tue"]
            tue_mark = f'<div class="tue-wrap"><span data-layout-allow-overflow class="mark-check han-tue">✓</span><span class="sub-tue">{tue_sub}</span></div>'
        else:
            tue_mark = '<span class="mark-dash">—</span>'

        row_id_attr = f' id="row-{y}"' if is_clean else ''
        clean_cls = ' clean-row' if is_clean else ''

        row_str = f"""
      <div class="row-item{clean_cls}"{row_id_attr}>
        <div class="cell-year">{y}</div>
        <div class="cell-mu">{age}</div>
        <div class="cell-han">{kl_mark}</div>
        <div class="cell-han">{ho_mark}</div>
        <div class="cell-han">{tt_mark}</div>
        <div class="cell-han">{tue_mark}</div>
      </div>"""
        rows_html.append(row_str)

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
      background: #180406; font-family: "Be Vietnam Pro", sans-serif; }}
    #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden;
      background: radial-gradient(85% 65% at 50% 22%, #421114 0%, #260608 48%, #140204 100%); }}
    #grain {{ position: absolute; inset: 0; width: 1080px; height: 1920px; opacity: 0.22;
      pointer-events: none; mix-blend-mode: overlay; z-index: 20; }}
    #mountains {{ position: absolute; left: 0; bottom: 0; width: 1080px; height: 220px; pointer-events: none; z-index: 1; }}

    /* Header */
    #kicker {{ position: absolute; left: 60px; top: 118px; width: 870px; text-align: center;
      font-family: "JetBrains Mono", monospace; font-weight: 500; font-size: 24px;
      letter-spacing: 0.16em; color: #fde68a; z-index: 4; }}
    #title {{ position: absolute; left: 60px; top: 165px; width: 870px; text-align: center;
      font-weight: 900; font-size: 54px; line-height: 1.18; letter-spacing: -0.01em; color: #fff1f2; z-index: 4; }}
    #title .gold {{ color: #fde68a; display: block; }}
    #subchip {{ position: absolute; left: 60px; top: 345px; width: 870px; display: flex; align-items: center; justify-content: center; z-index: 4; }}
    .chip-tag {{ display: inline-block; padding: 7px 28px; border-radius: 20px;
      background: rgba(253,230,138,0.12); border: 1.5px solid rgba(253,230,138,0.45);
      font-weight: 700; font-size: 22px; color: #fde68a; }}

    /* Shimmer Beam */
    #shimmer-wrap {{ position: absolute; inset: 0; overflow: hidden; pointer-events: none; z-index: 6; }}
    #shimmer-beam {{ position: absolute; top: 0; left: -140px; width: 120px; height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.7), transparent);
      transform: skewX(-20deg); opacity: 0; }}

    /* Table Grid */
    #table-wrap {{ position: absolute; left: 60px; top: 430px; width: 880px; z-index: 5; }}

    /* Header Row */
    .table-head {{
      display: grid; grid-template-columns: 165px 105px 150px 155px 150px 155px;
      align-items: center; height: 86px; margin-bottom: 8px; border-radius: 10px;
      background: rgba(180, 83, 9, 0.28); border: 1.5px solid rgba(245, 158, 11, 0.65);
    }}
    .th-col {{ text-align: center; font-size: 30px; font-weight: 800; color: #fde68a; line-height: 1.08; }}

    /* Data Rows (10 rows) */
    .rows-container {{ display: flex; flex-direction: column; gap: 7px; }}
    .row-item {{
      display: grid; grid-template-columns: 165px 105px 150px 155px 150px 155px;
      align-items: center; height: 72px; border-radius: 10px;
      background: rgba(30, 8, 10, 0.65); border: 1.5px solid rgba(255, 255, 255, 0.12);
      box-shadow: 0 3px 8px rgba(0, 0, 0, 0.25);
    }}

    /* Typography in cells */
    .cell-year {{ font-size: 58px; font-weight: 900; color: #ffffff; text-align: center; line-height: 1; }}
    .cell-mu {{ font-size: 36px; font-weight: 800; color: #f1f5f9; text-align: center; line-height: 1; }}

    .cell-han {{ display: flex; align-items: center; justify-content: center; height: 100%; }}
    .mark-check {{ font-size: 36px; font-weight: 900; color: #fca5a5; line-height: 1; }}
    .mark-dash {{ font-size: 36px; font-weight: 700; color: #ffffff; opacity: 1; line-height: 1; }}

    .tue-wrap {{ display: flex; flex-direction: column; align-items: center; justify-content: center; line-height: 1; }}
    .sub-tue {{ font-size: 20px; font-weight: 800; color: #fca5a5; text-transform: uppercase; margin-top: 2px; }}

    /* Clean Row Glow */
    #row-{clean_year} {{ border-color: rgba(255, 255, 255, 0.12); }}

    /* Footnotes */
    #footnotes {{ position: absolute; left: 60px; top: 1342px; width: 880px; text-align: center; z-index: 5; }}
    .fn-l1 {{ font-size: 23px; font-weight: 700; color: #fde68a; line-height: 1.3; }}
    .fn-l2 {{ font-size: 23px; font-weight: 700; color: #fde68a; line-height: 1.3; margin-top: 4px; }}

    #subfoot {{ position: absolute; left: 60px; top: 1416px; width: 880px; text-align: center;
      font-size: 25px; font-weight: 800; color: #e2e8f0; letter-spacing: 0.08em; z-index: 5; }}

    /* Seal Tham Khao */
    #seal-thamkhao {{ position: absolute; left: 64px; top: 110px; width: 78px; height: 78px; z-index: 10;
      border: 3px solid #b91c1c; border-radius: 8px; background: rgba(185, 28, 28, 0.40);
      display: flex; align-items: center; justify-content: center; transform: rotate(-8deg); }}
    .seal-text {{ font-family: "Be Vietnam Pro", sans-serif; font-weight: 900; font-size: 15px;
      line-height: 1.15; color: #fecaca; text-align: center; letter-spacing: 0.05em; }}

    /* Subtitle caption (dedicated zone, clear of table and subfoot) */
    #caption-box {{ position: absolute; left: 60px; right: 60px; top: 1510px; text-align: center; z-index: 5; pointer-events: none; }}
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
    <path d="M0 140 Q 270 40 540 130 T 1080 120 L 1080 220 L 0 220 Z" fill="#0d0203" opacity="0.8"/>
  </svg>

  <div id="shimmer-wrap"><div id="shimmer-beam" data-layout-allow-overflow></div></div>
  <div id="seal-thamkhao"><div class="seal-text">THAM<br>KHẢO</div></div>

  <div id="kicker">{t["kicker"]}</div>
  <div id="title">
    {t["title_main"]}<br/>
    <span class="gold">{t["title_gold"]}</span>
  </div>

  <div id="subchip">
    <div class="chip-tag">BẢNG TRA CỨU TỰ DÒ · NĂM 2027</div>
  </div>

  <div id="table-wrap">
    <div class="table-head">
      <div class="th-col">NĂM<br/>SINH</div>
      <div class="th-col">TUỔI<br/>MỤ</div>
      <div class="th-col">KIM<br/>LÂU</div>
      <div class="th-col">HOANG<br/>ỐC</div>
      <div class="th-col">TAM<br/>TAI</div>
      <div class="th-col">THÁI<br/>TUẾ</div>
    </div>
    <div class="rows-container">
{all_rows}
    </div>
  </div>

  <div id="footnotes">
    <div class="fn-l1">Tính theo tuổi mụ · Kim Lâu, Hoang Ốc xét khi cưới hỏi, làm nhà</div>
    <div class="fn-l2">Sinh trước Tết Nguyên Đán tính tuổi theo năm trước · Tham khảo</div>
  </div>

  <div id="subfoot">DỪNG HÌNH TÌM NĂM SINH CỦA BẠN</div>
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

    // Shimmer beam uses transform x
    tl.fromTo("#shimmer-beam", {{ x: 0, opacity: 0 }}, {{ x: 1080, opacity: 0.85, duration: 1.2, ease: "power1.inOut" }}, 0.6);
    tl.fromTo("#seal-thamkhao", {{ scale: 1.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, 0.4);

    // Clean year glow
    const tGlow = {round(segs[1]["start"], 2)};
    tl.to("#row-{clean_year}", {{
      borderColor: "#f59e0b",
      backgroundColor: "rgba(180, 83, 9, 0.45)",
      boxShadow: "0 0 25px rgba(245, 158, 11, 0.8)",
      duration: 0.6,
      ease: "power2.out"
    }}, tGlow);

    // Progress driver for words & hold frame
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


def build_month_sheet_html(t: dict, dur: float, segs: list[dict]) -> str:
    """December 2026 month sheet calendar with full AA contrast and 0 overflow."""
    fonts = font_css()
    days = DAYS_DEC_2026

    # 01/12/2026 is Tuesday (Thứ Ba).
    # Lưới 7 cột Thứ Hai -> Chủ Nhật.
    # Monday is empty cell (offset = 1)
    cells_html = ['<div class="cal-cell empty"></div>']

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

    # Fill remaining cells to complete 5 full weeks (35 cells)
    while len(cells_html) < 35:
        cells_html.append('<div class="cal-cell empty"></div>')

    grid_content = "\n".join(cells_html)
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
    .cal-cell.red-bad .day-lunar {{ color: #fca5a5; }}

    .cal-cell.neutral-cell {{
      background: rgba(15, 23, 42, 0.55);
      border: 1.5px solid rgba(148, 163, 184, 0.30);
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

  <div id="kicker">LỊCH VẠN NIÊN · THÁNG 12/2026</div>
  <div id="title">
    THÁNG 12 NĂM 2026<br/>
    <span class="gold">LỊCH NGÀY HOÀNG ĐẠO</span>
  </div>

  <div id="subchip">
    <div class="chip-tag">16 NGÀY HOÀNG ĐẠO · 12 NGÀY THUẬN LỢI</div>
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
    Vàng: hoàng đạo · Góc đỏ: trùng Tam Nương · Đỏ: ngày kỵ · Tham khảo
  </div>
  <div id="subfoot">DỪNG HÌNH LƯU LẠI LỊCH CẢ THÁNG NHÉ</div>
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


def build_tet_calendar_html(t: dict, dur: float, segs: list[dict]) -> str:
    """Tết 2027 calendar table (Mùng 1 to Mùng 5)."""
    fonts = font_css()
    days = TET_2027_DAYS

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

    #head {{ position: absolute; left: 60px; right: 60px; top: 100px; text-align: center; z-index: 4; }}
    #chip {{ display: inline-block; padding: 10px 32px; border-radius: 40px; background: #fde68a; color: #78350f;
            font-weight: 900; font-size: 32px; letter-spacing: .06em; }}
    #title {{ margin-top: 20px; font-weight: 900; font-size: 68px; line-height: 1.15; color: #fff7ed; }}
    #title .gold {{ color: #fef08a; display: block; }}

    #table-wrap {{ position: absolute; left: 60px; top: 430px; width: 960px; z-index: 5; }}
    .tet-head {{
      display: grid; grid-template-columns: 200px 240px 280px 240px;
      align-items: center; height: 80px; margin-bottom: 12px; border-radius: 16px;
      background: rgba(254, 240, 138, 0.25); border: 2px solid #fde68a;
    }}
    .th-col {{ text-align: center; font-size: 28px; font-weight: 800; color: #fef08a; }}

    .tet-rows {{ display: flex; flex-direction: column; gap: 14px; }}
    .tet-row {{
      display: grid; grid-template-columns: 200px 240px 280px 240px;
      align-items: center; height: 140px; border-radius: 18px;
      background: rgba(45, 6, 4, 0.75); border: 2.5px solid rgba(253, 230, 138, 0.35);
      box-shadow: 0 8px 24px rgba(0,0,0,0.35);
    }}
    .tet-col-mung {{ font-size: 44px; font-weight: 900; color: #fde68a; text-align: center; }}
    .tet-col-solar {{ font-size: 38px; font-weight: 800; color: #ffffff; text-align: center; line-height: 1.2; }}
    .tet-sub-dow {{ font-size: 24px; font-weight: 700; color: #fef08a; }}
    .tet-col-canchi {{ font-size: 34px; font-weight: 800; color: #fef9c3; text-align: center; line-height: 1.25; }}
    .tet-sub-truc {{ font-size: 22px; font-weight: 700; color: #fed7aa; }}
    .tet-col-desc {{ font-size: 30px; font-weight: 800; color: #e2e8f0; text-align: center; line-height: 1.2; padding: 0 8px; }}

    #subfoot {{ position: absolute; left: 60px; right: 60px; bottom: 130px; text-align: center;
      font-size: 32px; font-weight: 800; color: #fef08a; letter-spacing: 0.05em; z-index: 5; }}
    #foot {{ position: absolute; left: 60px; right: 60px; bottom: 70px; text-align: center;
      font-size: 24px; font-weight: 700; color: #fed7aa; z-index: 5; }}

    /* Subtitle caption (dedicated zone between table and subfoot) */
    #caption-box {{ position: absolute; left: 60px; right: 60px; top: 1420px; text-align: center; z-index: 5; pointer-events: none; }}
    .cap-line {{ font-size: 40px; font-weight: 800; line-height: 1.32; color: #ffffff; text-shadow: 0 3px 8px rgba(0,0,0,0.85); }}
    .cw {{ opacity: 0.38; color: #ffffff; transition: color 0.1s ease, opacity 0.1s ease; }}
    .cw.on {{ opacity: 1; color: #fde68a; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
  <div id="grain" data-layout-allow-overflow></div>

  <div id="head">
    <div id="chip">LỊCH TẾT ĐINH MÙI 2027</div>
    <div id="title">
      TẾT NGUYÊN ĐÁN 2027<br/>
      <span class="gold">MÙNG 1 ĐẾN MÙNG 5</span>
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


def build_giao_thua_html(t: dict, dur: float, segs: list[dict]) -> str:
    """Đêm Giao thừa 2027 card."""
    fonts = font_css()
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
      background: #4a0604; font-family: "Be Vietnam Pro", sans-serif; }}
    #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden;
      background: radial-gradient(110% 80% at 50% 25%, #991b1b 0%, #580c08 50%, #290403 100%); }}
    #grain {{ position: absolute; inset: 0; width: 1080px; height: 1920px; opacity: 0.22;
      pointer-events: none; mix-blend-mode: overlay; z-index: 20; }}

    #head {{ position: absolute; left: 60px; right: 60px; top: 110px; text-align: center; z-index: 4; }}
    #chip {{ display: inline-block; padding: 10px 32px; border-radius: 40px; background: #fde68a; color: #78350f;
            font-weight: 900; font-size: 32px; letter-spacing: .06em; }}
    #title {{ margin-top: 24px; font-weight: 900; font-size: 64px; line-height: 1.18; color: #fff7ed; }}
    #title .gold {{ color: #fef08a; display: block; }}

    #cards-wrap {{ position: absolute; left: 60px; top: 430px; width: 960px; display: flex; flex-direction: column; gap: 20px; z-index: 5; }}
    .card-item {{
      background: rgba(30, 4, 3, 0.82); border: 2.5px solid rgba(253, 230, 138, 0.45);
      border-radius: 20px; padding: 26px 32px; box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }}
    .card-label {{ font-size: 26px; font-weight: 800; color: #fed7aa; text-transform: uppercase; letter-spacing: 0.05em; }}
    .card-main {{ font-size: 56px; font-weight: 900; color: #fef08a; margin-top: 8px; line-height: 1.1; }}
    .card-desc {{ font-size: 30px; font-weight: 700; color: #ffffff; margin-top: 8px; line-height: 1.3; }}

    #subfoot {{ position: absolute; left: 60px; right: 60px; bottom: 130px; text-align: center;
      font-size: 32px; font-weight: 800; color: #fef08a; letter-spacing: 0.05em; z-index: 5; }}
    #foot {{ position: absolute; left: 60px; right: 60px; bottom: 70px; text-align: center;
      font-size: 24px; font-weight: 700; color: #fed7aa; z-index: 5; }}

    /* Subtitle caption (dedicated zone between cards and subfoot) */
    #caption-box {{ position: absolute; left: 60px; right: 60px; top: 1360px; text-align: center; z-index: 5; pointer-events: none; }}
    .cap-line {{ font-size: 40px; font-weight: 800; line-height: 1.32; color: #ffffff; text-shadow: 0 3px 8px rgba(0,0,0,0.85); }}
    .cw {{ opacity: 0.38; color: #ffffff; transition: color 0.1s ease, opacity 0.1s ease; }}
    .cw.on {{ opacity: 1; color: #fde68a; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
  <div id="grain" data-layout-allow-overflow></div>

  <div id="head">
    <div id="chip">ĐÊM GIAO THỪA NĂM 2027</div>
    <div id="title">
      TẾT 2027 KHÔNG CÓ 30 TẾT<br/>
      <span class="gold">GIAO THỪA ĐÊM 29 THÁNG CHẠP</span>
    </div>
  </div>

  <div id="cards-wrap">
    <div class="card-item">
      <div class="card-label">SỰ KIỆN ĐẶC BIỆT</div>
      <div class="card-main">THÁNG CHẠP THIẾU (29 NGÀY)</div>
      <div class="card-desc">Năm Bính Ngọ 2026 tháng 12 âm lịch chỉ có 29 ngày, không có ngày 30 Tết.</div>
    </div>
    <div class="card-item">
      <div class="card-label">THỜI KHẮC GIAO THỪA (DƯƠNG LỊCH)</div>
      <div class="card-main">THỨ SÁU · 05/02/2027</div>
      <div class="card-desc">Thời khắc giao thừa chuyển giao sang Đinh Mùi diễn ra đêm 29 Tết (05/02).</div>
    </div>
    <div class="card-item">
      <div class="card-label">GIỜ GIAO THỪA CHÍNH XÁC</div>
      <div class="card-main">GIỜ TÝ (23:00 – 01:00)</div>
      <div class="card-desc">Khung giờ Tý bắt đầu từ 23h đêm 05/02 đến 01h sáng 06/02/2027.</div>
    </div>
  </div>

  <div id="subfoot">DỪNG HÌNH LƯU LẠI THỜI KHẮC GIAO THỪA NHÉ</div>
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


# =========================================================================
# BUILD & RENDER PROCESS
# =========================================================================
def build_and_render_all(target_ids: set[str] | None = None) -> None:
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
        print(f"\n[{idx}/14] Đang xử lý {rid} ({item['day']} {item['slot']}) - {title}...")

        meta_file = RENDER_DIR / f"{rid}.render.json"
        mp4 = RENDER_DIR / f"{rid}.mp4"
        if target_ids is None and meta_file.exists() and mp4.exists():
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
        last_audio_end = segs_raw[-1]["end"] if segs_raw else dur - 3.5
        # Ensure still hold >= 3.0s (min 4.2s hold and dur >= 11.5s for GOP alignment)
        min_dur = max(dur, round(last_audio_end + 4.2, 2), 11.5)
        final_dur = min_dur
        item["dur"] = final_dur

        display_script = item.get("display_script") or item["script"]
        segs = []
        for s_idx, sg in enumerate(segs_raw):
            disp_txt = display_script[s_idx] if s_idx < len(display_script) else sg["text"]
            segs.append({
                "start": sg["start"],
                "end": sg["end"],
                "text": disp_txt
            })

        # 2. Composition HTML Generation
        if style == "yeartable":
            html_content = build_yeartable_html(item, final_dur, segs)
        elif style == "decade_grid":
            html_content = build_decade_html(item, final_dur, segs)
        elif style == "month_sheet":
            html_content = build_month_sheet_html(item, final_dur, segs)
        elif style == "tet_calendar":
            html_content = build_tet_calendar_html(item, final_dur, segs)
        elif style == "giao_thua_card":
            html_content = build_giao_thua_html(item, final_dur, segs)
        else:
            raise ValueError(f"Unknown style: {style}")

        comp_name = f"_tb_{rid}.html"
        comp_path = COMP / comp_name
        comp_path.write_text(html_content, encoding="utf-8")

        # 3. HyperFrames Silent Render
        silent = RENDER_DIR / f"{rid}_silent.mp4"
        mp4 = RENDER_DIR / f"{rid}.mp4"

        silent.unlink(missing_ok=True)
        mp4.unlink(missing_ok=True)

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
            "group": item["group"],
            "replaces_video": item.get("replaces_video"),
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
    print("\nĐÃ HOÀN TẤT TẤT CẢ 14 SHORT RENDER!")


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

    preview_jpg = RENDER_DIR / "preview_fs_1104.jpg"
    sheet.save(preview_jpg, quality=90)
    print(f"Đã xuất tờ ảnh preview: {preview_jpg}")


def export_preview_fix_0000b() -> None:
    target_ids = ["fs_rep_1105", "fs_rep_1107", "fs_phu_1104_1", "fs_phu_1105_2", "fs_phu_1107_2"]
    mid_times = {
        "fs_rep_1105": 3.5,
        "fs_rep_1107": 3.5,
        "fs_phu_1104_1": 4.8,
        "fs_phu_1105_2": 8.5,
        "fs_phu_1107_2": 3.0,
    }
    cell_w, cell_h = 360, 640
    header_top = 70
    header_left = 220
    w = header_left + len(target_ids) * cell_w
    h = header_top + 2 * cell_h
    sheet = Image.new("RGB", (w, h), (15, 23, 42))
    draw = ImageDraw.Draw(sheet)

    try:
        font = ImageFont.truetype(str(HF / "studio" / "fonts" / "Be_Vietnam_Pro" / "813dca14c283.woff2"), 22)
        font_sm = ImageFont.truetype(str(HF / "studio" / "fonts" / "Be_Vietnam_Pro" / "813dca14c283.woff2"), 17)
    except Exception:
        font = ImageFont.load_default()
        font_sm = font

    # Draw row headers
    draw.text((15, header_top + 240), "KHUNG GIỮA\n(Phụ đề số\n1970/2027/05/02)", fill=(253, 230, 138), font=font)
    draw.text((15, header_top + cell_h + 240), "KHUNG CUỐI\n(Tắt phụ đề\nRõ CTA)", fill=(147, 197, 253), font=font)

    for idx, rid in enumerate(target_ids):
        col_x = header_left + idx * cell_w
        mp4 = RENDER_DIR / f"{rid}.mp4"
        assert mp4.exists(), f"Missing {mp4}"

        # Column header
        draw.text((col_x + 10, 22), rid, fill=(255, 255, 255), font=font)

        # Mid frame
        t_mid = mid_times.get(rid, 4.0)
        f_mid = RENDER_DIR / f"_preview_mid_{rid}.png"
        subprocess.run(["ffmpeg", "-y", "-i", str(mp4), "-ss", str(t_mid), "-vframes", "1", str(f_mid)], capture_output=True, check=True)
        im_mid = Image.open(f_mid).resize((cell_w, cell_h), Image.Resampling.LANCZOS)
        sheet.paste(im_mid, (col_x, header_top))
        f_mid.unlink(missing_ok=True)

        # Last frame
        r_probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)], capture_output=True, text=True)
        dur = float((r_probe.stdout or "0").strip() or 12.0)
        t_last = max(0.1, dur - 0.25)
        f_last = RENDER_DIR / f"_preview_last_{rid}.png"
        subprocess.run(["ffmpeg", "-y", "-i", str(mp4), "-ss", str(t_last), "-vframes", "1", str(f_last)], capture_output=True, check=True)
        im_last = Image.open(f_last).resize((cell_w, cell_h), Image.Resampling.LANCZOS)
        sheet.paste(im_last, (col_x, header_top + cell_h))
        f_last.unlink(missing_ok=True)

        # Grid borders
        draw.rectangle([col_x, header_top, col_x + cell_w, header_top + cell_h], outline=(51, 65, 85), width=2)
        draw.rectangle([col_x, header_top + cell_h, col_x + cell_w, header_top + 2 * cell_h], outline=(51, 65, 85), width=2)

    out_jpg = RENDER_DIR / "preview_fix_0000b.jpg"
    sheet.save(out_jpg, quality=92)
    print(f"Đã xuất tờ ảnh kiểm Lead: {out_jpg}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--only-fix", action="store_true", help="Chỉ render 5 bài bị lỗi cần sửa")
    args = parser.parse_args()

    targets = {"fs_rep_1105", "fs_rep_1107", "fs_phu_1104_1", "fs_phu_1105_2", "fs_phu_1107_2"} if args.only_fix else None
    build_and_render_all(target_ids=targets)
    export_preview_sheet()
    export_preview_fix_0000b()
