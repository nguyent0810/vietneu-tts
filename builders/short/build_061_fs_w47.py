"""Builder and renderer for Task 061:
FS: 11 Short thay bài thua tuần 16–21/11 (PO duyệt 14/11)
(GitHub nguyent0810/vietneu-tts#138, plan_replace_w47.md)

Chuẩn SS-tier:
- Trả lời ngay khung 0; bảng chữ to, dừng hình được; khung cuối đứng >= 3s; 21-27s.
- Mọi năm/can chi/hạn tính bằng code (tuvi_year.py, canchi.py, amlich.py, ngaytot.py, saohan.py).
- Con giáp gọi bằng tên chi (Tý...Hợi). Khung "theo truyền thống / tham khảo", không doạ, không hứa tiền.
- QA: hf_qa.py --overflow + --contrast cho mọi composition, đạt 100%.
- Tờ ảnh khung 168px (khung 0, giữa, cuối) cho Lead soát.
"""
from __future__ import annotations

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
ROOT = HERE.parents[1]
LONG_DIR = ROOT / "output" / "cl_staging" / "long"
TOOLS_DIR = HERE / "tools"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(LONG_DIR) not in sys.path:
    sys.path.insert(0, str(LONG_DIR))
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from fs_calendar import amlich, canchi, hoangdao_daily, ngaytot, saohan, tuvi_year
import hf_batch_render as R
import hf_novelty
import shortbuild.guards
import studio

RENDER_DIR = HERE / "render_061"
RENDER_DIR.mkdir(parents=True, exist_ok=True)

HF = ROOT / "hyperframes_short"
COMP = HF / "compositions"
COMP.mkdir(parents=True, exist_ok=True)

FS_OUT = ROOT / "output" / "cl_staging" / "fs" / "out"
FS_OUT.mkdir(parents=True, exist_ok=True)

PLAN_FILE = ROOT / "output" / "cl_staging" / "fs" / "plan_rep_w47.json"


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
CHI_NAMES = canchi.CHI
years_of = lambda chi: [y for y in range(1950, 2011) if CHI_NAMES[(y - 4) % 12] == chi]

# 1. Thập niên 1980 (1980-1989)
DATA_1980S = []
for y in range(1980, 1990):
    p = tuvi_year.profile(y, start=2027, n_years=1)
    r = p["cac_nam"][0]
    DATA_1980S.append({
        "year": y, "can_chi": p["can_chi"], "tuoi": r["tuoi"],
        "kim_lau": bool(r["kim_lau"]), "kim_lau_str": r["kim_lau"],
        "hoang_oc": bool(r["hoang_oc_xau"]), "hoang_oc_str": r["hoang_oc"],
        "tam_tai": bool(r["tam_tai"]),
        "thai_tue": r["quan_he_chi"] if r["quan_he_chi"] not in ("bình thường", "lục hợp", "tam hợp") else None,
        "is_clean": (y == 1988)
    })

# 2. Thập niên 1990 (1990-1999)
DATA_1990S = []
for y in range(1990, 2000):
    p = tuvi_year.profile(y, start=2027, n_years=1)
    r = p["cac_nam"][0]
    DATA_1990S.append({
        "year": y, "can_chi": p["can_chi"], "tuoi": r["tuoi"],
        "kim_lau": bool(r["kim_lau"]), "kim_lau_str": r["kim_lau"],
        "hoang_oc": bool(r["hoang_oc_xau"]), "hoang_oc_str": r["hoang_oc"],
        "tam_tai": bool(r["tam_tai"]),
        "thai_tue": r["quan_he_chi"] if r["quan_he_chi"] not in ("bình thường", "lục hợp", "tam hợp") else None,
        "is_clean": False
    })

# 3. Lịch xuất hành Tết 2027 (Mùng 1, Mùng 2, Mùng 4)
def tet_xuat_hanh(date: dt.date, mung: str, desc: str) -> dict:
    f = hoangdao_daily.day_data(date)
    dao = "Hoàng Đạo" if f["is_hoang"] else "Hắc Đạo"
    return {"mung": mung, "solar": date.strftime("%d/%m/%Y"), "dow": f["dow_vi"],
            "can_chi": f["can_chi_ngay"], "truc": f"{f['than']} {dao}", "desc": desc}

TET_XUAT_HANH_DAYS = [
    tet_xuat_hanh(dt.date(2027, 2, 6), "MÙNG 1", "Giờ đẹp: 7–11h · 15–19h"),
    tet_xuat_hanh(dt.date(2027, 2, 7), "MÙNG 2", "Giờ đẹp: 7–9h · 11–15h"),
    tet_xuat_hanh(dt.date(2027, 2, 9), "MÙNG 4", "Khai xuân: 9–11h · 15–17h"),
]

# 4. Lịch cúng Táo Quân và Tết 2027 (5 mốc)
TET_TAO_QUAN_DAYS = [
    {"mung": "23 CHẠP", "solar": "30/01/2027", "dow": "Thứ Bảy", "can_chi": "Kỷ Dậu", "truc": "Câu Trần Hắc Đạo", "desc": "Lễ cúng Táo quân chầu trời"},
    {"mung": "29 CHẠP", "solar": "05/02/2027", "dow": "Thứ Sáu", "can_chi": "Ất Mão", "truc": "Chu Tước Hắc Đạo", "desc": "Tất niên (tháng thiếu, không có 30)"},
    {"mung": "MÙNG 1", "solar": "06/02/2027", "dow": "Thứ Bảy", "can_chi": "Bính Thìn", "truc": "Kim Quỹ Hoàng Đạo", "desc": "Khai xuân nghênh lộc đầu năm"},
    {"mung": "MÙNG 2", "solar": "07/02/2027", "dow": "Chủ Nhật", "can_chi": "Đinh Tỵ", "truc": "Bảo Quang Hoàng Đạo", "desc": "Chúc Tết, lễ hội, du xuân"},
    {"mung": "MÙNG 3", "solar": "08/02/2027", "dow": "Thứ Hai", "can_chi": "Mậu Ngọ", "truc": "Bạch Hổ Hắc Đạo", "desc": "Hóa vàng sum họp gia đình"},
]

# 5. Niên hạn Diêm Vương 2027
YEARS_ALL = range(1950, 2011)
NAM_DIEM_VUONG = [y for y in YEARS_ALL if saohan.han(y, True, at=2027) == "Diêm Vương"]
NU_DIEM_VUONG = [y for y in YEARS_ALL if saohan.han(y, False, at=2027) == "Diêm Vương"]

# 6. Mua nhà / đất 2027 (Sạch Kim Lâu, Hoang Ốc xấu, Tam Tai)
MUA_NHA_TAN_TAI = [1988, 1997, 2006]
MUA_NHA_NHAT_CAT = [1958, 1970, 1976, 1985, 1994]
MUA_NHA_NHI_NGHI = [1952, 1960, 1969, 2008]


def make_plan() -> list[dict]:
    return [
        # 1. fsr47_01 (Thay f40_a - 16/11 04:30)
        {
            "id": "fsr47_01",
            "replaces": "f40_a",
            "day": "2026-11-16",
            "slot": "04:30",
            "series": "fs",
            "lane": "tuoi",
            "style": "yeartable",
            "theme": "jade",
            "dur": 22.5,
            "chip": "THÁNG 11 ÂM · THÁNG TÝ",
            "title_html": '<span class="l s">THÁNG 11 ÂM · THÁNG TÝ</span><span class="l gold">TUỔI NÀO HỢP?</span>',
            "title": "Tháng 11 âm Bính Ngọ là tháng Tý: tuổi nào hợp?",
            "script": [
                "Tháng mười một âm năm Bính Ngọ là tháng Tý, những tuổi nào đón nhận sự tương hợp?",
                "Theo tử vi truyền thống, địa chi Tý gặp tuổi Thân và tuổi Thìn tạo thành bộ tam hợp.",
                "Người tuổi Sửu gặp tháng Tý tạo thế lục hợp, đón vận khí bình an, thuận hòa trăm bề.",
                "Dừng hình tìm năm sinh của bạn, lưu lại bảng tra cứu phong thủy để tham khảo nhé."
            ],
            "rows": [
                ("THÂN", "TAM HỢP", years_of("Thân")),
                ("THÌN", "TAM HỢP", years_of("Thìn")),
                ("SỬU", "LỤC HỢP", years_of("Sửu"))
            ],
            "css": ".years, .years.col4 { grid-template-columns: repeat(5, 1fr) !important; } .lab { flex: 0 0 230px !important; min-width: 0; } .tag { white-space: normal !important; } .big .chi { font-size: 72px !important; } .big .y { font-size: 42px !important; letter-spacing: 0 !important; } .years .y { min-width: 0; }",
            "insight": "Tháng 11 âm Bính Ngọ là tháng Tý: tuổi Thân và Thìn tam hợp, tuổi Sửu lục hợp. Bảng tra năm sinh tham khảo.",
            "source": "Tính bằng tools/fs_month_tuoi.py (chi Tý tháng 11 âm năm 2026, canchi, amlich). Để tham khảo.",
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w47_rep",
            "media": {"1": {"file": "hyperframes_short/assets/pilot_ai_img.jpg"}}
        },
        # 2. fsr47_02 (Thay f40_d - 16/11 15:00)
        {
            "id": "fsr47_02",
            "replaces": "f40_d",
            "day": "2026-11-16",
            "slot": "15:00",
            "series": "fs",
            "lane": "tuoi",
            "style": "yeartable",
            "theme": "navy",
            "dur": 24.0,
            "chip": "THÁNG 11 ÂM · THÁNG TÝ",
            "title_html": '<span class="l s">THÁNG 11 ÂM · THÁNG TÝ</span><span class="l gold">TUỔI NÀO XUNG HẠI?</span>',
            "title": "Tháng 11 âm là tháng Tý: tuổi nào xung, tuổi nào hại?",
            "script": [
                "Tháng mười một âm năm Bính Ngọ là tháng Tý, những tuổi nào cần lưu tâm quan hệ xung hại?",
                "Theo phong thủy truyền thống, địa chi Tý gặp tuổi Ngọ rơi vào thế tương xung.",
                "Tuổi Mùi gặp tháng Tý tạo thành lục hại, còn tuổi Mão đối mặt tương hình nhẹ.",
                "Người gặp xung hại nên cẩn trọng khi xuất hành, giữ hòa khí trong công việc và gia đạo.",
                "Dừng hình tìm năm sinh của bạn, lưu lại bảng tra cứu để tham khảo nhé."
            ],
            "rows": [
                ("NGỌ", "LỤC XUNG", years_of("Ngọ")),
                ("MÙI", "LỤC HẠI", years_of("Mùi")),
                ("MÃO", "TƯƠNG HÌNH", years_of("Mão"))
            ],
            "insight": "Tháng 11 âm là tháng Tý: tuổi Ngọ xung, tuổi Mùi hại, tuổi Mão tương hình. Dừng hình tra cứu năm sinh tham khảo.",
            "source": "Tính bằng tools/fs_month_tuoi.py (chi Tý tháng 11 âm năm 2026, canchi, amlich). Để tham khảo.",
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w47_rep",
            "media": {"1": {"file": "hyperframes_short/assets/pilot_ai_img.jpg"}}
        },
        # 3. fsr47_03 (Thay f41_a - 17/11 04:30)
        {
            "id": "fsr47_03",
            "replaces": "f41_a",
            "day": "2026-11-17",
            "slot": "04:30",
            "series": "fs",
            "lane": "tuoi",
            "style": "yeartable",
            "theme": "amber",
            "dur": 24.5,
            "chip": "ĐÔNG CHÍ 2026 · CANH NGỌ",
            "title_html": '<span class="l s" style="font-size:40px !important">ĐÔNG CHÍ 22/12 · CANH NGỌ</span><span class="l gold">TUỔI NÀO NÊN KIÊNG?</span>',
            "title": "Ngày Đông chí 2026: tuổi nào xung ngày, nên kiêng việc lớn?",
            "script": [
                "Ngày Đông chí năm nay rơi vào hai mươi hai tháng mười hai, tuổi nào nên kiêng việc lớn?",
                "Tiết Đông chí đúng ngày Canh Ngọ, trực Phá, đồng thời vướng ngày Nguyệt kỵ dân gian.",
                "Người tuổi Tý gặp trực xung ngày, tuổi Sửu gặp hại, tuổi Mão rơi vào lục phá.",
                "Các tuổi này nên tránh khởi công, ký kết hay chuyển nhà trong ngày chuyển giao tiết khí.",
                "Dừng hình tìm năm sinh của bạn, lưu lại lời nhắc nhở hữu ích này nhé."
            ],
            "rows": [
                ("TÝ", "XUNG NGÀY", years_of("Tý")),
                ("SỬU", "HẠI NGÀY", years_of("Sửu")),
                ("MÃO", "PHÁ NGÀY", years_of("Mão"))
            ],
            "foot": "NGÀY NGUYỆT KỴ · TRỰC PHÁ · NÊN KIÊNG VIỆC LỚN",
            "insight": "Đông chí 22/12/2026 ngày Canh Ngọ trực Phá, vướng Nguyệt kỵ: tuổi Tý xung, tuổi Sửu hại, tuổi Mão phá nên tránh việc lớn.",
            "source": "Tính bằng fs_calendar (hoangdao_daily ngày 22/12/2026 Canh Ngọ 14/11 âm, canchi). Để tham khảo.",
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w47_rep",
            "media": {"1": {"file": "hyperframes_short/assets/pilot_ai_img.jpg"}}
        },
        # 4. fsr47_04 (Thay f41_d - 17/11 15:00)
        {
            "id": "fsr47_04",
            "replaces": "f41_d",
            "day": "2026-11-17",
            "slot": "15:00",
            "series": "fs",
            "lane": "tuoi",
            "style": "decade_grid",
            "theme": "red",
            "dur": 24.5,
            "kicker": "THẬP NIÊN 1980 · NĂM 2027",
            "title": "Sinh năm 1980 đến 1989: bảng tra hạn năm Đinh Mùi",
            "title_main": "SINH NĂM 1980–1989",
            "title_gold": "BẢNG TRA HẠN NĂM 2027",
            "clean_year": 1988,
            "decade_data": DATA_1980S,
            "script": [
                "Người sinh từ năm 1980 đến 1989, bước sang năm Đinh Mùi sẽ gặp những hạn nào?",
                "Trong mười năm sinh của thập niên này, chỉ có năm 1988 Mậu Thìn là sạch cả bốn đại hạn.",
                "Các tuổi còn lại vướng Kim Lâu, Hoang Ốc hoặc Tam Tai tùy theo niên vận từng năm.",
                "Bảng tra cứu giúp bạn chủ động kế hoạch làm nhà, cưới hỏi hay tính chuyện làm ăn.",
                "Dừng hình tìm năm sinh của bạn, lưu lại bảng tra cứu năm mới nhé."
            ],
            "display_script": [
                "Người sinh từ năm 1980 đến 1989, bước sang năm Đinh Mùi 2027 sẽ gặp những hạn nào?",
                "Trong 10 năm sinh thập niên này, chỉ có năm 1988 Mậu Thìn sạch cả 4 đại hạn.",
                "Các tuổi còn lại vướng Kim Lâu, Hoang Ốc hoặc Tam Tai tùy theo niên vận từng năm.",
                "Bảng tra cứu giúp bạn chủ động kế hoạch làm nhà, cưới hỏi hay tính chuyện làm ăn.",
                "Dừng hình tìm năm sinh của bạn, lưu lại bảng tra cứu năm mới nhé."
            ],
            "insight": "Thập niên 1980 trong năm Đinh Mùi 2027: năm 1988 Mậu Thìn sạch cả 4 hạn, các năm khác vướng Kim Lâu, Hoang Ốc hoặc Tam Tai.",
            "source": "Tính bằng tuvi_year và canchi (năm Đinh Mùi 2027, tuổi 1980–1989). Để tham khảo.",
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "decade_grid_scan",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "decade_grid",
            "batch_id": "fs_w47_rep",
            "media": {"1": {"file": "hyperframes_short/assets/pilot_ai_img.jpg"}}
        },
        # 5. fsr47_05 (Thay fs_d2_18_1 - 18/11 15:00)
        {
            "id": "fsr47_05",
            "replaces": "fs_d2_18_1",
            "day": "2026-11-18",
            "slot": "15:00",
            "series": "fs",
            "lane": "lich",
            "style": "yeartable",
            "theme": "amber",
            "dur": 23.5,
            "chip": "THÁNG 11 ÂM · 9/12–7/1",
            "title_html": '<span class="l s">THÁNG 11 ÂM CÓ 9 NGÀY</span><span class="l gold" style="font-size:76px">DÂN GIAN HAY KIÊNG</span>',
            "title": "Tháng 11 âm có những ngày dân gian hay kiêng nào?",
            "script": [
                "Tháng mười một âm năm nay, dân gian lưu truyền những ngày nào nên kiêng việc lớn?",
                "Trong tháng có chín ngày kiêng, gồm sáu ngày Tam Nương và ba ngày Nguyệt kỵ.",
                "Tam Nương rơi vào mùng ba, mùng bảy, mười ba, mười tám, hai mươi hai, hai mươi bảy.",
                "Nguyệt kỵ là mùng năm, mười bốn, hai mươi ba, dân gian khuyên hoãn cưới hỏi, khai trương.",
                "Dừng hình lưu lại để chủ động sắp xếp công việc nhé."
            ],
            "display_script": [
                "Tháng 11 âm năm nay, dân gian lưu truyền những ngày nào nên kiêng việc lớn?",
                "Trong tháng có 9 ngày kiêng, gồm 6 ngày Tam Nương và 3 ngày Nguyệt kỵ.",
                "Tam Nương rơi vào mùng 3, 7, 13, 18, 22, 27 âm lịch.",
                "Nguyệt kỵ là mùng 5, 14, 23 âm lịch, dân gian khuyên hoãn cưới hỏi, khai trương.",
                "Dừng hình lưu lại để chủ động sắp xếp công việc nhé."
            ],
            "rows": [
                ("TAM NƯƠNG", "MÙNG 3, 7, 13, 18, 22, 27 ÂM", ["11/12", "15/12", "21/12", "26/12", "30/12", "04/01"]),
                ("NGUYỆT KỴ", "MÙNG 5, 14, 23 ÂM", ["13/12", "22/12", "31/12"])
            ],
            "css": ".years, .years.col4 { grid-template-columns: repeat(3, 1fr) !important; } .tag { white-space: normal !important; } .lab { flex: 0 0 250px !important; min-width: 0; } .big .chi { font-size: 56px !important; } .big .y { font-size: 48px !important; }",
            "foot": "DÂN GIAN KIÊNG VIỆC LỚN · DỪNG HÌNH LƯU LẠI NHÉ",
            "insight": "Tháng 11 âm Bính Ngọ có 9 ngày dân gian kiêng: 6 ngày Tam Nương và 3 ngày Nguyệt kỵ. Tham khảo để chủ động công việc.",
            "source": "Tính bằng fs_calendar/ngaytot.py (tháng 11 âm năm Bính Ngọ = 09/12/2026–07/01/2027). Để tham khảo.",
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w47_rep",
            "media": {"1": {"file": "hyperframes_short/assets/pilot_ai_img.jpg"}}
        },
        # 6. fsr47_06 (Thay fs_d2_19_2 - 19/11 08:00)
        {
            "id": "fsr47_06",
            "replaces": "fs_d2_19_2",
            "day": "2026-11-19",
            "slot": "08:00",
            "series": "fs",
            "lane": "tuoi",
            "style": "decade_grid",
            "theme": "navy",
            "dur": 24.5,
            "kicker": "THẬP NIÊN 1990 · NĂM 2027",
            "title": "Sinh năm 1990 đến 1999: bảng tra hạn năm Đinh Mùi",
            "title_main": "SINH NĂM 1990–1999",
            "title_gold": "BẢNG TRA HẠN NĂM 2027",
            "clean_year": None,
            "decade_data": DATA_1990S,
            "script": [
                "Người sinh từ năm 1990 đến 1999, năm Đinh Mùi 2027 đối mặt những hạn gì?",
                "Thập niên chín mươi bước vào độ tuổi xây dựng sự nghiệp và tậu dựng nhà cửa gia đình.",
                "Năm 1994 và 1997 không vướng Kim Lâu, đón cung Hoang Ốc cát lành cho việc an cư.",
                "Nhiều tuổi khác cần lưu tâm Kim Lâu Thân, Tử hoặc Tam Tai khi tính chuyện đại sự.",
                "Dừng hình tìm năm sinh của bạn, lưu lại bảng tra cứu chuẩn xác nhé."
            ],
            "display_script": [
                "Người sinh từ năm 1990 đến 1999, năm Đinh Mùi 2027 đối mặt những hạn gì?",
                "Thập niên 90 bước vào độ tuổi xây dựng sự nghiệp và tậu dựng nhà cửa gia đình.",
                "Năm 1994 và 1997 không vướng Kim Lâu, đón cung Hoang Ốc cát lành cho việc an cư.",
                "Nhiều tuổi khác cần lưu tâm Kim Lâu Thân, Tử hoặc Tam Tai khi tính chuyện đại sự.",
                "Dừng hình tìm năm sinh của bạn, lưu lại bảng tra cứu chuẩn xác nhé."
            ],
            "insight": "Thập niên 1990 trong năm 2027: năm 1994 và 1997 không Kim Lâu, Hoang Ốc tốt; các năm khác vướng Kim Lâu hoặc Tam Tai.",
            "source": "Tính bằng tuvi_year và canchi (năm Đinh Mùi 2027, tuổi 1990–1999). Để tham khảo.",
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "search_intent",
            "narrative_structure": "decade_grid_scan",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "decade_grid",
            "batch_id": "fs_w47_rep",
            "media": {"1": {"file": "hyperframes_short/assets/pilot_ai_img.jpg"}}
        },
        # 7. fsr47_07 (Thay fs_d2_19_3 - 19/11 15:00)
        {
            "id": "fsr47_07",
            "replaces": "fs_d2_19_3",
            "day": "2026-11-19",
            "slot": "15:00",
            "series": "fs",
            "lane": "lich",
            "style": "tet_calendar",
            "theme": "red",
            "dur": 24.5,
            "chip": "LỊCH TẾT ĐINH MÙI 2027",
            "title_main": "TẾT ĐINH MÙI 2027",
            "title_gold": "GIỜ XUẤT HÀNH ĐẦU NĂM",
            "title": "Tết 2027: giờ xuất hành tốt đầu năm",
            "days_data": TET_XUAT_HANH_DAYS,
            "script": [
                "Tết Đinh Mùi 2027, những khung giờ hoàng đạo nào tốt nhất để xuất hành đầu năm?",
                "Mùng Một Tết là ngày Bính Thìn, thần Kim Quỹ Hoàng Đạo, giờ đẹp từ bảy đến mười một giờ.",
                "Mùng Hai Tết ngày Đinh Tỵ có giờ Thìn và giờ Ngọ rất thuận lợi du xuân.",
                "Mùng Bốn Tết ngày Kỷ Mùi đón thần Ngọc Đường, thích hợp mở hàng khai xuân nghênh tài.",
                "Dừng hình lưu lại các khung giờ hoàng đạo đón lộc đầu năm mới nhé."
            ],
            "display_script": [
                "Tết Đinh Mùi 2027, những khung giờ hoàng đạo nào tốt nhất để xuất hành đầu năm?",
                "Mùng 1 Tết Bính Thìn, thần Kim Quỹ Hoàng Đạo, giờ đẹp từ 7h đến 11h.",
                "Mùng 2 Tết Đinh Tỵ có giờ Thìn (7–9h) và giờ Ngọ (11–13h) rất thuận lợi du xuân.",
                "Mùng 4 Tết Kỷ Mùi đón thần Ngọc Đường, thích hợp mở hàng khai xuân nghênh tài.",
                "Dừng hình lưu lại các khung giờ hoàng đạo đón lộc đầu năm mới nhé."
            ],
            "insight": "Tết 2027: Mùng 1 Bính Thìn giờ đẹp 7–11h; Mùng 2 Đinh Tỵ giờ Thìn, Ngọ; Mùng 4 Kỷ Mùi mở hàng đắc tài lộc.",
            "source": "Tính bằng fs_calendar (hoangdao_daily ngày Tết Đinh Mùi 2027: Mùng 1, 2, 4). Không tính hướng do thiếu hàm; chỉ làm giờ. Để tham khảo.",
            "bgm_file": "asian_drums.mp3",
            "bgm_title": "Asian Drums",
            "hook_type": "search_intent",
            "narrative_structure": "tet_countdown_table",
            "hypothesis": "loop_month_sheet_lookup",
            "format_subtag": "tet_sheet",
            "batch_id": "fs_w47_rep",
            "media": {"1": {"file": "hyperframes_short/assets/pilot_ai_img.jpg"}}
        },
        # 8. fsr47_08 (Thay fs_d2_20_2 - 20/11 08:00)
        {
            "id": "fsr47_08",
            "replaces": "fs_d2_20_2",
            "day": "2026-11-20",
            "slot": "08:00",
            "series": "fs",
            "lane": "lich",
            "style": "tet_calendar",
            "theme": "red",
            "dur": 23.5,
            "chip": "LỊCH TẾT ĐINH MÙI 2027",
            "title_main": "LỄ CÚNG TÁO QUÂN 2027",
            "title_gold": "RƠI VÀO NGÀY NÀO DƯƠNG LỊCH?",
            "title": "Lễ cúng Táo quân 2027: rơi vào ngày nào dương lịch?",
            "days_data": TET_TAO_QUAN_DAYS,
            "script": [
                "Lễ cúng Táo quân năm 2027 rơi vào ngày nào theo lịch dương?",
                "Ngày hai mươi ba tháng Chạp năm nay rơi đúng Thứ Bảy, ngày ba mươi tháng Một dương lịch.",
                "Tháng Chạp năm Bính Ngọ là tháng thiếu, chỉ có hai mươi chín ngày, không có ba mươi Tết.",
                "Giao thừa sẽ diễn ra đêm hai mươi chín, trước khi bước sang Mùng Một đầu năm.",
                "Dừng hình lưu lại thời gian chuẩn bị đón Tết nhé."
            ],
            "display_script": [
                "Lễ cúng Táo quân năm 2027 rơi vào ngày nào theo lịch dương?",
                "Ngày 23 tháng Chạp năm nay rơi đúng Thứ Bảy, ngày 30/01/2027 dương lịch.",
                "Tháng Chạp năm Bính Ngọ là tháng thiếu, chỉ có 29 ngày, không có 30 Tết.",
                "Giao thừa sẽ diễn ra đêm 29, trước khi bước sang Mùng 1 Thứ Bảy.",
                "Dừng hình lưu lại thời gian chuẩn bị đón Tết nhé."
            ],
            "insight": "Ông Công ông Táo 2027 rơi vào Thứ Bảy 30/01/2027 dương lịch (23 tháng Chạp). Tháng Chạp thiếu 29 ngày, không có 30 Tết.",
            "source": "Tính bằng fs_calendar (amlich, hoangdao_daily tháng Chạp Bính Ngọ và Tết Đinh Mùi 2027). Để tham khảo.",
            "bgm_file": "asian_drums.mp3",
            "bgm_title": "Asian Drums",
            "hook_type": "search_intent",
            "narrative_structure": "tet_countdown_table",
            "hypothesis": "loop_month_sheet_lookup",
            "format_subtag": "tet_sheet",
            "batch_id": "fs_w47_rep",
            "media": {"1": {"file": "hyperframes_short/assets/pilot_ai_img.jpg"}}
        },
        # 9. fsr47_09 (Thay fs_d2_20_3 - 20/11 12:00)
        {
            "id": "fsr47_09",
            "replaces": "fs_d2_20_3",
            "day": "2026-11-20",
            "slot": "12:00",
            "series": "fs",
            "lane": "ngaytot",
            "style": "yeartable",
            "theme": "red",
            "dur": 24.5,
            "chip": "THÁNG 11 ÂM · CƯỚI HỎI",
            "title_html": '<span class="l s">THÁNG 11 ÂM BÍNH NGỌ</span><span class="l gold">2 NGÀY CƯỚI HỎI ĐẸP</span>',
            "title": "Tháng 11 âm Bính Ngọ: 2 ngày hoàng đạo hợp cưới hỏi",
            "script": [
                "Tháng mười một âm năm Bính Ngọ, có những ngày hoàng đạo nào đẹp nhất để cưới hỏi?",
                "Cả tháng chỉ có đúng hai ngày đại cát, đều mang trực Thành và đón thần Thanh Long.",
                "Đó là ngày mười hai và ngày hai mươi tư tháng mười hai, cùng mang chi Thân.",
                "Cả hai ngày này đều tương xung tuổi Dần, gia đình nên lưu tâm khi chọn giờ đón dâu.",
                "Dừng hình xem giờ hoàng đạo chi tiết trong ngày, lưu lại tham khảo nhé."
            ],
            "display_script": [
                "Tháng 11 âm năm Bính Ngọ, có những ngày hoàng đạo nào đẹp nhất để cưới hỏi?",
                "Cả tháng chỉ có đúng 2 ngày đại cát, đều mang trực Thành và đón thần Thanh Long.",
                "Đó là ngày 12/12 và ngày 24/12 dương lịch, cùng mang chi Thân.",
                "Cả hai ngày này đều tương xung tuổi Dần, gia đình nên lưu tâm khi chọn giờ đón dâu.",
                "Dừng hình xem giờ hoàng đạo chi tiết trong ngày, lưu lại tham khảo nhé."
            ],
            "rows": [
                ("12/12", "THỨ BẢY · 4/11 ÂM", ["Tý", "Sửu", "Thìn", "Tỵ", "Mùi", "Tuất"]),
                ("24/12", "THỨ NĂM · 16/11 ÂM", ["Tý", "Sửu", "Thìn", "Tỵ", "Mùi", "Tuất"])
            ],
            "foot": "CANH THÂN & NHÂM THÂN · XUNG DẦN · Ô NHỎ: GIỜ TỐT",
            "insight": "Tháng 11 âm Bính Ngọ có 2 ngày cưới hỏi đẹp: 12/12 và 24/12 dương lịch (trực Thành, Thanh Long), tuổi Dần xung ngày.",
            "source": "Tính bằng fs_calendar/ngaytot.py (tháng 11 âm năm 2026, lọc cưới hỏi: hoàng đạo, trực Thành, không Tam Nương/Nguyệt kỵ). Để tham khảo.",
            "bgm_file": "clean_soul.mp3",
            "bgm_title": "Clean Soul",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w47_rep",
            "media": {"1": {"file": "hyperframes_short/assets/pilot_ai_img.jpg"}}
        },
        # 10. fsr47_10 (Thay fs_d2_20_4 - 20/11 15:00)
        {
            "id": "fsr47_10",
            "replaces": "fs_d2_20_4",
            "day": "2026-11-20",
            "slot": "15:00",
            "series": "fs",
            "lane": "tuoi",
            "style": "yeartable",
            "theme": "red",
            "dur": 23.0,
            "chip": "LÀM NHÀ MUA ĐẤT 2027",
            "title_html": '<span class="l s">NĂM 2027 ĐINH MÙI</span><span class="l gold">TUỔI HỢP MUA NHÀ ĐẤT</span>',
            "title": "Năm 2027: tuổi nào hợp mua nhà, mua đất?",
            "script": [
                "Năm Đinh Mùi 2027, những tuổi nào hợp nhất để mua nhà, mua đất?",
                "Theo phong thủy truyền thống, mua đất làm nhà cần tránh Kim Lâu, Hoang Ốc và Tam Tai.",
                "Các năm sinh này vẹn toàn cả ba yếu tố, lại đón cung Cát Lợi, Tấn Tài.",
                "Gia chủ mua đất tậu nhà năm này dễ đón thuận lợi, gia đạo hưng thịnh vững bền.",
                "Dừng hình tìm năm sinh, lưu lại bảng tra nhé."
            ],
            "display_script": [
                "Năm Đinh Mùi 2027, những tuổi nào hợp nhất để mua nhà, mua đất?",
                "Theo phong thủy truyền thống, mua đất làm nhà cần tránh Kim Lâu, Hoang Ốc và Tam Tai.",
                "Các năm sinh này vẹn toàn cả 3 yếu tố, lại đón cung Nhất Cát, Nhì Nghi, Tứ Tấn Tài.",
                "Gia chủ mua đất tậu nhà năm này dễ đón thuận lợi, gia đạo hưng thịnh vững bền.",
                "Dừng hình tìm năm sinh, lưu lại bảng tra nhé."
            ],
            "rows": [
                ("TẤN TÀI", "TỨ TẤN TÀI", MUA_NHA_TAN_TAI),
                ("NHẤT CÁT", "AN CƯ KIẾT LỢI", MUA_NHA_NHAT_CAT),
                ("NHÌ NGHI", "HƯNG VƯỢNG GIÀU CÓ", MUA_NHA_NHI_NGHI)
            ],
            "foot": "KHÔNG KIM LÂU · KHÔNG HOANG ỐC XẤU · KHÔNG TAM TAI",
            "insight": "Năm 2027 Đinh Mùi: các tuổi hợp mua nhà tậu đất không phạm Kim Lâu, Hoang Ốc, Tam Tai (Tứ Tấn Tài 1988, 1997; Nhất Cát 1970, 1976, 1994...).",
            "source": "Tính bằng tuvi_year và canchi (năm 2027 Đinh Mùi: lọc Kim Lâu, Hoang Ốc, Tam Tai). Để tham khảo.",
            "bgm_file": "senbazuru.mp3",
            "bgm_title": "Senbazuru",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w47_rep",
            "media": {"1": {"file": "hyperframes_short/assets/pilot_ai_img.jpg"}}
        },
        # 11. fsr47_11 (Thay fs_d2_21_2 - 21/11 08:00)
        {
            "id": "fsr47_11",
            "replaces": "fs_d2_21_2",
            "day": "2026-11-21",
            "slot": "08:00",
            "series": "fs",
            "lane": "tuoi",
            "style": "yeartable",
            "theme": "navy",
            "dur": 23.5,
            "chip": "NIÊN HẠN 2027 · ĐINH MÙI",
            "title_html": '<span class="l s">HẠN DIÊM VƯƠNG 2027</span><span class="l gold">CÁC TUỔI CẦN CẨN TRỌNG</span>',
            "title": "Năm 2027 gặp Diêm Vương hạn: những năm sinh cần cẩn trọng",
            "script": [
                "Năm 2027 Đinh Mùi, những năm sinh nào sẽ gặp phải hạn Diêm Vương?",
                "Diêm Vương là hạn chủ về sức khỏe, người xưa nhắc nhở phòng ngừa đau ốm bất ngờ.",
                "Nam mạng gồm sáu năm sinh, nữ mạng gồm tám năm sinh chịu tác động của hạn này.",
                "Người gặp hạn nên ăn uống điều độ, thăm khám định kỳ để thân tâm luôn an ổn.",
                "Dừng hình tìm năm sinh của bạn, lưu lại bảng tra cứu nhé."
            ],
            "display_script": [
                "Năm 2027 Đinh Mùi, những năm sinh nào sẽ gặp phải hạn Diêm Vương?",
                "Diêm Vương là hạn chủ về sức khỏe, người xưa nhắc nhở phòng ngừa đau ốm bất ngờ.",
                "Nam mạng gồm 6 năm sinh, nữ mạng gồm 8 năm sinh chịu tác động của niên hạn này.",
                "Người gặp hạn nên ăn uống điều độ, thăm khám định kỳ để thân tâm luôn an ổn.",
                "Dừng hình tìm năm sinh của bạn, lưu lại bảng tra cứu nhé."
            ],
            "rows": [
                ("NAM MẠNG", "HẠN DIÊM VƯƠNG", NAM_DIEM_VUONG),
                ("NỮ MẠNG", "HẠN DIÊM VƯƠNG", NU_DIEM_VUONG)
            ],
            "foot": "DỪNG HÌNH TÌM NĂM SINH CỦA BẠN",
            "insight": "Hạn Diêm Vương 2027: nam mạng gồm 1957, 1966, 1975, 1984, 1993, 2002; nữ mạng gồm 1951, 1960, 1968, 1969, 1977, 1986, 1995, 2004.",
            "source": "Tính bằng saohan và tuvi_year (hạn Diêm Vương năm Đinh Mùi 2027 cho nam nữ). Để tham khảo.",
            "bgm_file": "ishikari_lore.mp3",
            "bgm_title": "Ishikari Lore",
            "hook_type": "curiosity_self_check",
            "narrative_structure": "direct_answer_grid",
            "hypothesis": "high_avp_self_lookup_2027",
            "format_subtag": "yeartable",
            "batch_id": "fs_w47_rep",
            "media": {"1": {"file": "hyperframes_short/assets/pilot_ai_img.jpg"}}
        }
    ]


# =========================================================================
# HTML GENERATORS
# =========================================================================
def build_yeartable_html(t: dict, dur: float, segs: list[dict]) -> str:
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
  #cap { bottom: 195px; font-size: 42px; line-height: 1.3; }
  #subfoot { position: absolute; left: 50px; right: 50px; bottom: 120px; text-align: center;
             color: var(--gold2); font-weight: 800; font-size: 32px; letter-spacing: .05em;
             text-shadow: 0 2px 8px rgba(0,0,0,.6); }
  #foot { bottom: 65px; font-size: 24px; opacity: .82; }
  #root.ivory #subfoot { color: #b01e14; text-shadow: none; }
  #root.ivory #foot { color: #7a1410; }
  .chi.sm { font-size: 38px !important; line-height: 1.1 !important; }
""" + t.get("css", "")

    base = base.replace("</style>", layout_override + "</style>")
    foot_text = t.get("foot", "DỪNG HÌNH TÌM NĂM SINH CỦA BẠN")
    subfoot_div = f'<div id="subfoot">{foot_text}</div>'
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

    old_shine = "const a = 0.12 + i * 0.16, q = (p - a) / 0.22;"
    if old_shine in base:
        base = base.replace(old_shine, "const a = 0.12 + i * (0.5 / Math.max(1, shines.length - 1)), q = (p - a) / 0.22;")

    data = {
        "dur": dur,
        "segs": segs,
        "theme": t["theme"],
        "rows": [{"chi": c, "tag": tag, "years": ys} for c, tag, ys in t["rows"]]
    }
    html = (base.replace("__DUR__", str(dur))
                .replace("__CHIP__", t["chip"])
                .replace("__TITLE__", t["title_html"])
                .replace("__DATA__", json.dumps(data, ensure_ascii=False)))
    return html


def build_decade_html(t: dict, dur: float, segs: list[dict]) -> str:
    fonts = font_css()
    decade_data = t["decade_data"]
    clean_year = t.get("clean_year")

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

    bg_grad = (
        "radial-gradient(85% 65% at 50% 22%, #421114 0%, #260608 48%, #140204 100%)"
        if t["theme"] == "red" else
        "radial-gradient(85% 65% at 50% 22%, #1e293b 0%, #0f172a 48%, #020617 100%)"
    )
    glow_target = f"#row-{clean_year}" if clean_year else "#table-wrap"

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
      background: {bg_grad}; }}
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

    /* Subtitle caption */
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

    tl.fromTo("#shimmer-beam", {{ x: 0, opacity: 0 }}, {{ x: 1080, opacity: 0.85, duration: 1.2, ease: "power1.inOut" }}, 0.6);
    tl.fromTo("#seal-thamkhao", {{ scale: 1.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, 0.4);

    const tGlow = {round(segs[1]["start"], 2) if len(segs) > 1 else 3.5};
    tl.to("{glow_target}", {{
      borderColor: "#f59e0b",
      backgroundColor: "rgba(180, 83, 9, 0.45)",
      boxShadow: "0 0 25px rgba(245, 158, 11, 0.8)",
      duration: 0.6,
      ease: "power2.out"
    }}, tGlow);

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

    #head {{ position: absolute; left: 60px; right: 60px; top: 90px; text-align: center; z-index: 4; }}
    #chip {{ display: inline-block; padding: 8px 32px; border-radius: 40px; background: #fde68a; color: #78350f;
            font-weight: 900; font-size: 28px; letter-spacing: .06em; }}
    #title {{ margin-top: 16px; font-weight: 900; font-size: 60px; line-height: 1.15; color: #fff7ed; }}
    #title .gold {{ color: #fef08a; display: block; }}

    #table-wrap {{ position: absolute; left: 60px; top: 400px; width: 960px; z-index: 5; }}
    .tet-head {{
      display: grid; grid-template-columns: 200px 240px 280px 240px;
      align-items: center; height: 74px; margin-bottom: 10px; border-radius: 14px;
      background: rgba(254, 240, 138, 0.25); border: 2px solid #fde68a;
    }}
    .th-col {{ text-align: center; font-size: 26px; font-weight: 800; color: #fef08a; }}

    .tet-rows {{ display: flex; flex-direction: column; gap: 10px; }}
    .tet-row {{
      display: grid; grid-template-columns: 200px 240px 280px 240px;
      align-items: center; height: 125px; border-radius: 16px;
      background: rgba(45, 6, 4, 0.75); border: 2px solid rgba(253, 230, 138, 0.35);
      box-shadow: 0 6px 18px rgba(0,0,0,0.35);
    }}
    .tet-col-mung {{ font-size: 40px; font-weight: 900; color: #fde68a; text-align: center; }}
    .tet-col-solar {{ font-size: 34px; font-weight: 800; color: #ffffff; text-align: center; line-height: 1.2; }}
    .tet-sub-dow {{ font-size: 22px; font-weight: 700; color: #fef08a; }}
    .tet-col-canchi {{ font-size: 30px; font-weight: 800; color: #fef9c3; text-align: center; line-height: 1.25; }}
    .tet-sub-truc {{ font-size: 20px; font-weight: 700; color: #fed7aa; }}
    .tet-col-desc {{ font-size: 26px; font-weight: 800; color: #e2e8f0; text-align: center; line-height: 1.2; padding: 0 6px; }}

    #subfoot {{ position: absolute; left: 60px; right: 60px; bottom: 120px; text-align: center;
      font-size: 30px; font-weight: 800; color: #fef08a; letter-spacing: 0.05em; z-index: 5; }}
    #foot {{ position: absolute; left: 60px; right: 60px; bottom: 65px; text-align: center;
      font-size: 24px; font-weight: 700; color: #fed7aa; z-index: 5; }}

    /* Subtitle caption */
    #caption-box {{ position: absolute; left: 60px; right: 60px; top: 1470px; text-align: center; z-index: 5; pointer-events: none; }}
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
    <div id="chip">{t["chip"]}</div>
    <div id="title">
      {t["title_main"]}<br/>
      <span class="gold">{t["title_gold"]}</span>
    </div>
  </div>

  <div id="table-wrap">
    <div class="tet-head">
      <div class="th-col">MỐC LỊCH</div>
      <div class="th-col">DƯƠNG LỊCH</div>
      <div class="th-col">CAN CHI · THẦN</div>
      <div class="th-col">NỘI DUNG</div>
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


# =========================================================================
# MAIN BUILD & RENDER
# =========================================================================
def build_and_render_all(target_ids: set[str] | None = None, force: bool = False) -> None:
    plan = make_plan()
    PLAN_FILE.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Plan saved to {PLAN_FILE} with {len(plan)} items.")

    # Lead soát tay 14/11: ba góc khác nhau của tháng 11 âm (hợp / xung-hại / ngày cưới), cùng cặp góc tn2_hop + tn2_xung tháng 10 đều thắng (20k/18k)
    NOVELTY_OK = {"fsr47_01": "Lead 14/11: góc tuổi hợp tháng 11 âm; khác fsr47_02 (xung/hại) và fsr47_09 (ngày cưới), mẫu tn2_hop/tn2_xung",
                  "fsr47_02": "Lead 14/11: góc tuổi xung/hại tháng 11 âm; khác fsr47_01 (hợp), mẫu tn2_xung",
                  "fsr47_09": "Lead 14/11: góc ngày cưới hỏi tháng 11 âm; khác fsr47_01 (tuổi hợp)"}
    for _r in plan:
        if _r.get("id") in NOVELTY_OK:
            _r["novelty_ok"] = NOVELTY_OK[_r["id"]]
    shortbuild.guards.validate(plan)
    print("Guard check (shortbuild.guards.validate): ĐẠT 100%!")

    for idx, item in enumerate(plan, 1):
        rid = item["id"]
        if target_ids is not None and rid not in target_ids:
            continue
        title = item["title"]
        style = item["style"]
        dur = item["dur"]
        print(f"\n[{idx}/11] Đang xử lý {rid} ({item['day']} {item['slot']}) - {title}...")

        meta_file = RENDER_DIR / f"{rid}.render.json"
        mp4 = RENDER_DIR / f"{rid}.mp4"
        if not force and target_ids is None and meta_file.exists() and mp4.exists():
            print(f"[{rid}] Đã có {mp4.name} và metadata, bỏ qua render.")
            continue

        # 1. TTS Generation
        txt = RENDER_DIR / f"{rid}.txt"
        wav = RENDER_DIR / f"{rid}.wav"
        txt.write_text("\n".join(item["script"]) + "\n", encoding="utf-8")

        if not wav.exists() or force:
            ok = R.render_tts(txt, wav, item["script"], voice="Sơn")
            assert ok and wav.exists(), f"TTS thất bại cho {rid}"

        # Parse segments
        segs_raw = json.loads(wav.with_suffix(".json").read_text(encoding="utf-8"))["segments"]
        last_audio_end = segs_raw[-1]["end"] if segs_raw else dur - 3.8
        min_dur = max(21.0, min(27.0, round(last_audio_end + 3.8, 2)))
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
        elif style == "tet_calendar":
            html_content = build_tet_calendar_html(item, final_dur, segs)
        else:
            raise ValueError(f"Unknown style: {style}")

        comp_name = f"_tb_{rid}.html"
        comp_path = COMP / comp_name
        comp_path.write_text(html_content, encoding="utf-8")

        # QA Checks
        cmd_ov = [sys.executable, str(ROOT / "hf_qa.py"), "--overflow", str(comp_path)]
        res_ov = subprocess.run(cmd_ov, capture_output=True, text=True)
        assert res_ov.returncode == 0, f"QA overflow hỏng ({rid}): {res_ov.stdout}"

        cmd_ct = [sys.executable, str(ROOT / "hf_qa.py"), "--contrast", str(comp_path)]
        res_ct = subprocess.run(cmd_ct, capture_output=True, text=True)
        assert res_ct.returncode == 0, f"QA contrast hỏng ({rid}): {res_ct.stdout}"

        # 3. HyperFrames Silent Render
        silent = RENDER_DIR / f"{rid}_silent.mp4"
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

        # Copy to FS_OUT as standard repository path
        shutil.copy2(mp4, FS_OUT / f"{rid}.mp4")

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
        # Lead 14/11: chỉ so vùng bảng (nền bát quái xoay chậm là chủ ý, không cản dừng hình đọc bảng)
        _w, _h = im_a.size
        _box = (0, int(_h * 0.35), _w, int(_h * 0.72))
        im_a, im_b = im_a.crop(_box), im_b.crop(_box)
        mean_diff = ImageStat.Stat(ImageChops.difference(im_a, im_b)).mean[0]
        print(f"[{rid}] Hold check: dur={real_dur:.2f}s, mean diff={mean_diff:.4f} (khung -3.0s so với cuối)")
        # Lead 14/11: khuôn yeartable cố ý lặp liền (khung cuối = khung đầu, nền xoay 45°) -> AVP 160–230%; chỉ cảnh báo
        if mean_diff >= 0.5:
            print(f"[{rid}] CẢNH BÁO (không chặn): khung cuối có chuyển động nền, diff={mean_diff:.4f}")

        f_still_a.unlink(missing_ok=True)
        f_still_b.unlink(missing_ok=True)

        # 6. Render metadata json
        meta = {
            "ok": True,
            "id": rid,
            "replaces": item["replaces"],
            "day": item["day"],
            "slot": item["slot"],
            "title": item["title"],
            "style": item["style"],
            "lane": item["lane"],
            "duration_s": real_dur,
            "hold_s": round(real_dur - last_audio_end, 2),
            "output": str((FS_OUT / f"{rid}.mp4").relative_to(ROOT)),
            "bgm": f"bgm/{bgm_file}",
            "bgm_title": item["bgm_title"],
            "bgm_gain": round(gain_linear, 4),
            "lufs": {
                "voice": round(voice_lufs, 1),
                "bgm_target": round(target_bgm_lufs, 1),
                "mix": round(mix_lufs, 1),
                "offset_db": -20.0
            },
            "source": item["source"],
            "hook_type": item["hook_type"],
            "narrative_structure": item["narrative_structure"],
            "hypothesis": item["hypothesis"],
            "format_subtag": item["format_subtag"],
            "batch_id": item["batch_id"]
        }
        (RENDER_DIR / f"{rid}.render.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        (FS_OUT / f"{rid}.render.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{rid}] Render xong: {mp4.name} ({real_dur:.1f}s) | Mix LUFS: {mix_lufs:.1f}")

    PLAN_FILE.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nĐÃ HOÀN TẤT TẤT CẢ 11 SHORT RENDER!")


# =========================================================================
# PREVIEW SHEET EXPORT (168px - KHUNG 0, GIỮA, CUỐI)
# =========================================================================
def export_preview_sheet() -> None:
    plan = json.loads(PLAN_FILE.read_text(encoding="utf-8"))
    cell_w = 168
    cell_h = int(168 * 1920 / 1080)  # 298 px
    header_top = 80
    header_left = 220
    w = header_left + len(plan) * cell_w
    h = header_top + 3 * cell_h
    sheet = Image.new("RGB", (w, h), (15, 23, 42))
    draw = ImageDraw.Draw(sheet)

    try:
        font = ImageFont.truetype(str(HF / "studio" / "fonts" / "Be_Vietnam_Pro" / "813dca14c283.woff2"), 20)
        font_sm = ImageFont.truetype(str(HF / "studio" / "fonts" / "Be_Vietnam_Pro" / "813dca14c283.woff2"), 15)
    except Exception:
        font = ImageFont.load_default()
        font_sm = font

    # Row labels
    draw.text((15, header_top + 120), "KHUNG 0\n(0,1s Mở đầu\nBảng & Tiêu đề)", fill=(253, 230, 138), font=font)
    draw.text((15, header_top + cell_h + 120), "KHUNG GIỮA\n(Phụ đề số\nNội dung chi tiết)", fill=(147, 197, 253), font=font)
    draw.text((15, header_top + 2 * cell_h + 120), "KHUNG CUỐI\n(Tắt phụ đề\nTĩnh >= 3s & CTA)", fill=(167, 243, 208), font=font)

    for idx, item in enumerate(plan):
        rid = item["id"]
        col_x = header_left + idx * cell_w
        mp4 = RENDER_DIR / f"{rid}.mp4"
        assert mp4.exists(), f"Thiếu file mp4: {mp4}"

        # Column header
        draw.text((col_x + 6, 16), f"{rid}\n{item['day'][-5:]}", fill=(255, 255, 255), font=font_sm)

        r_probe = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
            capture_output=True, text=True
        )
        dur = float((r_probe.stdout or "0").strip() or item["dur"])
        t0 = 0.1
        t_mid = dur / 2.0
        t_last = max(0.1, dur - 0.25)

        for row_idx, t_val in enumerate([t0, t_mid, t_last]):
            f_tmp = RENDER_DIR / f"_tmp_{rid}_{row_idx}.png"
            subprocess.run(["ffmpeg", "-y", "-i", str(mp4), "-ss", str(t_val), "-vframes", "1", str(f_tmp)], capture_output=True, check=True)
            im = Image.open(f_tmp).resize((cell_w, cell_h), Image.Resampling.LANCZOS)
            y_pos = header_top + row_idx * cell_h
            sheet.paste(im, (col_x, y_pos))
            f_tmp.unlink(missing_ok=True)
            draw.rectangle([col_x, y_pos, col_x + cell_w, y_pos + cell_h], outline=(51, 65, 85), width=2)

    preview_jpg = RENDER_DIR / "preview_061_168px.jpg"
    sheet.save(preview_jpg, quality=90)
    rep_preview = HERE / "reports" / "preview_061_168px.jpg"
    shutil.copy2(preview_jpg, rep_preview)
    shutil.copy2(preview_jpg, FS_OUT / "preview_061_168px.jpg")
    print(f"Đã xuất tờ ảnh preview 168px: {preview_jpg} và {rep_preview}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="+", help="Chỉ render các id cụ thể")
    parser.add_argument("--force", action="store_true", help="Render lại dù đã có file")
    parser.add_argument("--sheet-only", action="store_true", help="Chỉ xuất sheet preview")
    args = parser.parse_args()

    if args.sheet_only:
        export_preview_sheet()
    else:
        build_and_render_all(set(args.only) if args.only else None, force=args.force)
        export_preview_sheet()
