"""Bộ sinh short "Lịch Hoàng Đạo hằng ngày" (khuôn A) — Task 30.

Cách dùng:
    .venv/bin/python tools/hoangdao_daily.py <yyyy-mm-dd>
    .venv/bin/python tools/hoangdao_daily.py 2026-10-22 --render
    .venv/bin/python tools/hoangdao_daily.py --check-all

Mọi số tính bằng code (amlich.py, canchi.py, ngaytot.py).
Không dùng vnlunar cho thần/trực/nạp âm (Rule 5).
Luật con giáp FS: Gọi bằng tên chi (Tý..Hợi), tối đa 3 tên chi mỗi câu.
Giữ nhận diện gia đình bảng (nhãn trên, tiêu đề 2 dòng, chân dừng hình, khung 1080x1920).
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if (HERE.parent / "studio.py").is_file() else Path.cwd()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "output/cl_staging/long"))
sys.path.insert(0, str(ROOT / "output/cl_staging/grok/tools"))

import amlich as A  # noqa: E402
import canchi as C  # noqa: E402
import hf_batch_render as R  # noqa: E402
import ngaytot as N  # noqa: E402

CHI = C.CHI
CAN = C.CAN
THAN = [
    "Thanh Long", "Minh Đường", "Thiên Hình", "Chu Tước", "Kim Quỹ", "Kim Đường",
    "Bạch Hổ", "Ngọc Đường", "Thiên Lao", "Nguyên Vũ", "Tư Mệnh", "Câu Trần"
]
HOANG = {0, 1, 4, 5, 7, 10}
TRUC = ["Kiến", "Trừ", "Mãn", "Bình", "Định", "Chấp", "Phá", "Nguy", "Thành", "Thu", "Khai", "Bế"]
GIO = [
    [0, 1, 3, 6, 8, 9],       # Tý, Ngọ
    [2, 3, 5, 8, 10, 11],     # Sửu, Mùi
    [0, 1, 4, 5, 7, 10],      # Dần, Thân
    [0, 2, 3, 6, 7, 9],       # Mão, Dậu
    [2, 4, 5, 8, 9, 11],      # Thìn, Tuất
    [1, 4, 6, 7, 10, 11]       # Tỵ, Hợi
]
GIO_HOURS_MAP = {
    0: (23, 1), 1: (1, 3), 2: (3, 5), 3: (5, 7), 4: (7, 9), 5: (9, 11),
    6: (11, 13), 7: (13, 15), 8: (15, 17), 9: (17, 19), 10: (19, 21), 11: (21, 23)
}
DOW_VI = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]

SAMPLE_DIR = ROOT / "samples"
RENDER_HD_DIR = ROOT / "output/cl_staging/grok/render_hd"
WEEK_DATES = [
    "2026-10-22",
    "2026-10-23",
    "2026-10-24",
    "2026-10-25",
    "2026-10-26",
    "2026-10-27",
    "2026-10-28",
]


def get_week_dates(start_date: dt.date | str) -> list[str]:
    """Trả về danh sách 7 ngày liên tiếp dạng ISO YYYY-MM-DD từ ngày bắt đầu."""
    if isinstance(start_date, str):
        start_date = dt.date.fromisoformat(start_date)
    return [(start_date + dt.timedelta(days=i)).isoformat() for i in range(7)]


def find_next_available_thursday(render_dir: Path | None = None) -> dt.date:
    """Tìm thứ Năm kế tiếp chưa có lô (chưa render video hoặc chưa có trong plan)."""
    if render_dir is None:
        render_dir = RENDER_HD_DIR

    covered = set()
    if render_dir.is_dir():
        for p in render_dir.glob("hd_*.mp4"):
            stem = p.stem.replace("hd_", "")
            if len(stem) == 8 and stem.isdigit():
                try:
                    covered.add(dt.datetime.strptime(stem, "%Y%m%d").date())
                except ValueError:
                    pass
        for p in render_dir.glob("plan_hd_week*.json"):
            try:
                items = json.loads(p.read_text(encoding="utf-8"))
                for it in items:
                    rid = it.get("id", "").replace("hd_", "")
                    if len(rid) == 8 and rid.isdigit():
                        covered.add(dt.datetime.strptime(rid, "%Y%m%d").date())
            except Exception:
                pass

    today = dt.date.today()
    days_ahead = (3 - today.weekday()) % 7
    cur_thursday = today + dt.timedelta(days=days_ahead)
    if cur_thursday < dt.date(2026, 10, 22):
        cur_thursday = dt.date(2026, 10, 22)

    while cur_thursday in covered:
        cur_thursday += dt.timedelta(days=7)

    return cur_thursday
VERIFIED = ROOT / "output/cl_staging/fs/calendar_facts_verified.json"
COMP = ROOT / "hyperframes_short/compositions"
HF = ROOT / "hyperframes_short"
FS_BGM = "bgm/asian_drums.mp3"
FS_BGM_GAIN = 0.14


def merge_contiguous_hours(indices: list[int]) -> str:
    """Gộp các khung giờ hoàng đạo liền kề thành dải gọn (vd 7–11h)."""
    in_set = set(indices)
    heads = [i for i in indices if (i - 1) % 12 not in in_set]
    if not heads and indices:
        heads = [indices[0]]
    blocks = []
    for h in heads:
        chain = [h]
        curr = h
        while (curr + 1) % 12 in in_set and (curr + 1) % 12 != h:
            curr = (curr + 1) % 12
            chain.append(curr)
        start_h = GIO_HOURS_MAP[chain[0]][0]
        end_h = GIO_HOURS_MAP[chain[-1]][1]
        blocks.append((chain[0], f"{start_h}–{end_h}h"))
    blocks.sort(key=lambda b: b[0] if b[0] != 0 else 12)
    return " · ".join(b[1] for b in blocks)


def day_data(target_date: dt.date | str) -> dict:
    """Hàm chuẩn trích xuất toàn bộ dữ kiện lịch hoàng đạo hằng ngày.

    - NÊN lấy độc quyền từ ngaytot.VIEC.
    - TRÁNH: lọc việc lớn + Tam Nương / Nguyệt kỵ.
    - 12 con giáp chia 4 nhóm: HỢP (xanh), TRÁNH (đỏ), LƯU Ý (vàng), Bình hòa (trầm).
    - Giờ hoàng đạo gộp khung liền.
    - Kịch bản 3 câu đọc (≤ 3 chi/câu).
    """
    if isinstance(target_date, str):
        target_date = dt.date.fromisoformat(target_date)

    ld, lm, ly, leap = A.solar2lunar(target_date.day, target_date.month, target_date.year)
    # Neo can chi ngày: 2026-10-02 = Kỷ Dậu
    i60 = (45 + A.jd_from_date(target_date.day, target_date.month, target_date.year) - A.jd_from_date(2, 10, 2026)) % 60
    can_i, chi_i = i60 % 10, i60 % 12
    mchi, tiet_name, tiet_date = N.tiet_month_chi(target_date)
    # Thần trực nhật tính theo chi tháng âm (tháng 1 = Dần ... tháng 9 = Tuất, tháng 10 = Hợi; tháng nhuận dùng chi tháng chính)
    lunar_mchi = (lm + 1) % 12
    start = (2 * ((lunar_mchi - 2) % 12)) % 12

    dan = []
    if ld in N.TAM_NUONG:
        dan.append("Tam Nương")
    if ld in N.NGUYET_KY:
        dan.append("Nguyệt kỵ")
    if (lm, ld) in N.DUONG_CONG and not leap:
        dan.append("Dương Công")

    truc = TRUC[(chi_i - mchi) % 12]
    than_name = THAN[(chi_i - start) % 12]
    is_hoang = (chi_i - start) % 12 in HOANG

    # 1. Quan hệ can chi 12 con giáp
    xung_chi_i = (chi_i + 6) % 12
    xung_chi = CHI[xung_chi_i]

    # Tam Hợp (2 chi)
    tam_hop = []
    for grp in C.TAM_HOP:
        if CHI[chi_i] in grp:
            tam_hop = [x for x in grp if x != CHI[chi_i]]

    # Lục Hợp (1 chi)
    luc_hop = [b if a == CHI[chi_i] else a for a, b in C.LUC_HOP if a == CHI[chi_i] or b == CHI[chi_i]][0]

    # Lục Hại & Lục Phá (nhóm LƯU Ý màu vàng)
    luc_hai = [b if a == CHI[chi_i] else a for a, b in C.LUC_HAI if a == CHI[chi_i] or b == CHI[chi_i]][0]
    luc_pha = [b if a == CHI[chi_i] else a for a, b in C.LUC_PHA if a == CHI[chi_i] or b == CHI[chi_i]][0]

    zodiac_grid = []
    for i in range(12):
        chi_name = CHI[i]
        if i == xung_chi_i:
            cls = "tranh"
            tag = "XUNG NGÀY"
            reason = "Xung ngày"
        elif chi_name in tam_hop:
            cls = "hop"
            tag = "TAM HỢP"
            reason = "Tam hợp"
        elif chi_name == luc_hop:
            cls = "hop"
            tag = "LỤC HỢP"
            reason = "Lục hợp"
        elif chi_name in (luc_hai, luc_pha):
            cls = "luuy"
            tag = "LƯU Ý"
            reason = "Hại ngày" if chi_name == luc_hai else "Phá ngày"
        else:
            cls = "binh"
            tag = "Bình hòa"
            reason = "Bình thường"
        zodiac_grid.append({
            "chi": chi_name,
            "index": i,
            "cls": cls,
            "tag": tag,
            "reason": reason
        })

    # 2. "Nên" lấy từ bảng VIEC (ngaytot.py). Short hằng ngày không khuyên cưới hỏi / đính hôn,
    # kể cả ngày qua lọc việc lớn — để làn ngày tốt theo việc. Không sửa ngaytot.py.
    viec_hop = N.VIEC.get(truc, ["thu xếp"])

    # 3. "Tránh": nếu ngày không qua lọc việc lớn -> chọn ngày khác; có Tam Nương/Nguyệt kỵ thì ghi tên.
    # passed_major giữ nguyên nghĩa lọc. Dòng NÊN và câu 1 luôn bỏ cưới hỏi, đính hôn.
    passed_major = is_hoang and any(v in viec_hop for v in N.VIEC_OK) and not dan
    cuoi_kws = ("cưới", "đính hôn")
    if passed_major:
        viec_nen = [v for v in viec_hop if not any(w in v.lower() for w in cuoi_kws)]
    else:
        viec_nen = [v for v in viec_hop if v not in N.VIEC_OK and not any(w in v.lower() for w in cuoi_kws)]
    nen_display = ", ".join(v.capitalize() for v in viec_nen) or "Việc thường ngày"
    if not passed_major:
        if dan:
            tranh_display = f"Việc lớn (cưới hỏi, khai trương, làm nhà): chọn ngày khác ({', '.join(dan)})"
        else:
            tranh_display = "Việc lớn (cưới hỏi, khai trương, làm nhà): chọn ngày khác"
    else:
        tranh_display = f"Tuổi {xung_chi} xung ngày: tránh việc lớn"

    # 4. Giờ tốt: gộp khung liền nhau cho gọn (vd 7–11h)
    gio_indices = GIO[chi_i % 6]
    gio_names = [CHI[g] for g in gio_indices]
    gio_display = merge_contiguous_hours(gio_indices)

    # 5. Kịch bản đọc 3 câu, ≤ 3 chi/câu
    hoang_txt = "hoàng đạo" if is_hoang else "hắc đạo"
    hop_str = ("hợp " + ", ".join(viec_nen[:2])) if viec_nen else "hợp việc thường ngày"
    c1 = f"{DOW_VI[target_date.weekday()]} {target_date.day}/{target_date.month} là ngày {hoang_txt}, trực {truc}, {hop_str}."
    for label, blob in (("NÊN", nen_display), ("câu 1", c1)):
        hit = [w for w in ("cưới", "đính hôn") if w in blob.lower()]
        if hit:
            raise AssertionError(f"{target_date} {label} còn {hit}: {blob}")

    if dan:
        dan_str = " và ".join(dan)
        c2 = f"Tuổi {xung_chi} xung ngày, ngày {dan_str} nên tránh việc lớn."
    else:
        c2 = f"Tuổi {xung_chi} xung ngày, nên tránh việc lớn."

    c3 = f"Tuổi {tam_hop[0]}, {tam_hop[1]} và {luc_hop} hợp ngày. Dừng hình tìm tuổi của bạn nhé."
    script = [c1, c2, c3]

    return {
        "date": target_date,
        "duong_str": f"{target_date.day}/{target_date.month}/{target_date.year}",
        "dow_vi": DOW_VI[target_date.weekday()],
        "solar_day": target_date.day,
        "solar_month": target_date.month,
        "solar_year": target_date.year,
        "ld": ld,
        "lm": lm,
        "leap": leap,
        "am_str": f"{ld}/{lm}" + (" nhuận" if leap else ""),
        "can_chi_ngay": f"{CAN[can_i]} {CHI[chi_i]}",
        "chi_ngay": CHI[chi_i],
        "can_ngay": CAN[can_i],
        "than": than_name,
        "is_hoang": is_hoang,
        "hoang_hac_str": "HOÀNG ĐẠO" if is_hoang else "HẮC ĐẠO",
        "truc": truc,
        "dan": dan,
        "tiet_name": tiet_name,
        "tiet_thang": CHI[mchi],
        "xung_chi": xung_chi,
        "tam_hop": tam_hop,
        "luc_hop": luc_hop,
        "luc_hai": luc_hai,
        "luc_pha": luc_pha,
        "zodiac_grid": zodiac_grid,
        "viec_hop": viec_hop,
        "nen_display": nen_display,
        "viec_nen": viec_nen,
        "tranh_display": tranh_display,
        "gio_hoang_dao": gio_names,
        "gio_indices": gio_indices,
        "gio_display": gio_display,
        "script": script
    }


def generate_title(target_date: dt.date, day_idx: int | None = None) -> str:
    """Tạo tiêu đề xoay 4 mẫu, không trùng kênh, câu tự nhiên, đưa Tam Nương/Nguyệt kỵ/Rằm vào tự nhiên."""
    iso = target_date.isoformat()
    # Giữ nguyên tiêu đề đã chốt cho tuần 22–28/10
    if iso == "2026-10-22":
        return "Thứ Năm 22/10 Tam Nương: tuổi nào nên tránh, giờ nào tốt?"
    if iso == "2026-10-23":
        return "Ngày mai 23/10 Nguyệt kỵ: tuổi nào nên tránh, giờ nào tốt?"
    if iso == "2026-10-24":
        return "24/10 Rằm tháng 9: ngày hoàng đạo hay hắc đạo?"
    if iso == "2026-10-25":
        return "Ngày 25/10/2026 tốt hay xấu? Tuổi nào hợp, tuổi nào tránh"
    if iso == "2026-10-26":
        return "Thứ Hai 26/10: tuổi nào nên tránh, giờ nào tốt?"
    if iso == "2026-10-27":
        return "Ngày mai 27/10 là ngày Tam Nương: tuổi nào nên tránh?"
    if iso == "2026-10-28":
        return "28/10 (19/9 âm): ngày hoàng đạo hay hắc đạo?"

    d = target_date.day
    m = target_date.month
    y = target_date.year
    dow = DOW_VI[target_date.weekday()]
    ld, lm, ly, leap = A.solar2lunar(d, m, y)
    am = f"{ld}/{lm}" + (" nhuận" if leap else "")

    is_tam_nuong = ld in N.TAM_NUONG
    is_nguyet_ky = ld in N.NGUYET_KY
    is_duong_cong = (lm, ld) in N.DUONG_CONG and not leap
    is_ram = (ld == 15)
    is_mung1 = (ld == 1)

    # Ngày đặc biệt Tam Nương: tránh "Tam Nương hợp làm gì?"; dùng câu tự nhiên
    if is_tam_nuong:
        return f"Ngày mai {d}/{m} là ngày Tam Nương: tuổi nào nên tránh?"

    if is_ram:
        return f"{d}/{m} Rằm tháng {lm}: ngày hoàng đạo hay hắc đạo?"

    if is_mung1:
        return f"{d}/{m} Mùng 1 tháng {lm}: ngày hoàng đạo hay hắc đạo?"

    idx = day_idx if day_idx is not None else target_date.toordinal() % 4

    if idx == 0:
        return f"Ngày {d}/{m}/{y} tốt hay xấu? Tuổi nào hợp, tuổi nào tránh"
    elif idx == 1:
        if is_nguyet_ky:
            return f"{dow} {d}/{m} Nguyệt kỵ: tuổi nào nên tránh, giờ nào tốt?"
        if is_duong_cong:
            return f"{dow} {d}/{m}: tuổi nào nên tránh, giờ nào tốt?"
        return f"{dow} {d}/{m}: tuổi nào nên tránh, giờ nào tốt?"
    elif idx == 2:
        if is_nguyet_ky:
            return f"Ngày mai {d}/{m} là ngày Nguyệt kỵ: tuổi nào nên tránh?"
        if is_duong_cong:
            return f"Ngày mai {d}/{m} là ngày Dương Công: tuổi nào nên tránh?"
        return f"Ngày mai {d}/{m} hợp làm gì? Tra tuổi của bạn"
    elif idx == 3:
        return f"{d}/{m} ({am} âm): ngày hoàng đạo hay hắc đạo?"
    elif idx == 4:
        return f"Ngày mai {d}/{m} hợp làm gì? Tra tuổi của bạn"
    elif idx == 5:
        return f"{dow} {d}/{m}: tuổi nào nên tránh, giờ nào tốt?"
    else:
        return f"{d}/{m} ({am} âm): ngày hoàng đạo hay hắc đạo?"


def get_week_meta(target_date: dt.date | str, day_idx: int | None = None) -> dict:
    """Tạo tiêu đề xoay 4 mẫu (kèm Tam Nương/Nguyệt kỵ/Rằm), insight chuẩn, và plan row cho ngày."""
    if isinstance(target_date, str):
        target_date = dt.date.fromisoformat(target_date)
    f = day_data(target_date)
    d = target_date.day
    m = target_date.month
    y = target_date.year
    dow = f["dow_vi"]
    am = f["am_str"]
    iso = target_date.isoformat()

    title = generate_title(target_date, day_idx=day_idx)

    hh_txt = "hoàng đạo" if f["is_hoang"] else "hắc đạo"
    hop_viec_txt = ("hợp " + ", ".join(f["viec_nen"][:2])) if f["viec_nen"] else "hợp việc thường ngày"
    if f["dan"]:
        dan_txt = f", ngày {' và '.join(f['dan'])} nên tránh việc lớn"
    elif f["is_hoang"] and f["truc"] in ("Khai", "Thành"):
        # Không ghi "hợp làm việc lớn": cụm đó gồm cưới hỏi. Câu 1 đã liệt kê việc còn lại.
        dan_txt = ""
    else:
        dan_txt = ", việc lớn nên chọn ngày khác"
    hop_chi_txt = f"{f['tam_hop'][0]}, {f['tam_hop'][1]} và {f['luc_hop']}"
    am_note = f"{f['am_str']} âm" + (", rằm" if f["ld"] == 15 else "")
    insight = (
        f"{dow} {d}/{m}/{y} ({am_note}) là ngày {f['can_chi_ngay']}, {hh_txt} {f['than']}, trực {f['truc']}: "
        f"{hop_viec_txt}{dan_txt}. Tuổi {f['xung_chi']} xung ngày. Tuổi {hop_chi_txt} hợp ngày. "
        f"Theo truyền thống, chỉ để tham khảo."
    )
    for label, blob in (("tiêu đề", title), ("insight", insight)):
        hit = [w for w in ("cưới", "đính hôn") if w in blob.lower()]
        if hit:
            raise AssertionError(f"{target_date} {label} còn {hit}: {blob}")

    # LỊCH ĐĂNG = NGÀY D TRỪ 2, slot "23:00" (tức 06:00 VN ngày D−1)
    publish_day = (target_date - dt.timedelta(days=2)).isoformat()
    rid = f"hd_{target_date.strftime('%Y%m%d')}"

    plan_item = {
        "id": rid,
        "day": publish_day,
        "slot": "23:00",
        "style": "daytable",
        "series": "fs",
        "badge": "",
        "title": title,
        "source": "",
        "tags": [
            "ngay hoang dao",
            "xem ngay tot",
            f"{d}/{m}/{y}",
            "lich am",
            "tuoi hop"
        ],
        "tags_vi": [
            "ngày hoàng đạo",
            "xem ngày tốt xấu",
            f"ngày {d}/{m}/{y}",
            "tuổi hợp hôm nay"
        ],
        "insight": insight,
        "script": f["script"],
        "media": {},
        "visuals": {},
        "lane": "hoangdao_daily",
        "hashtags": [
            "#Shorts",
            "#ngayhoangdao",
            "#phongthuy"
        ]
    }
    return {
        "title": title,
        "insight": insight,
        "plan_item": plan_item,
        "facts": f
    }
    return {
        "title": title,
        "insight": insight,
        "plan_item": plan_item,
        "facts": f
    }


def build_composition_html(facts: dict, dur: float, segs: list[dict]) -> str:
    """Dựng HTML composition 1080x1920 (khuôn A) từ review_yeartable.html với motion nâng cấp."""
    tpl = (COMP / "review_yeartable.html").read_text(encoding="utf-8")

    cells_html = []
    for c in facts["zodiac_grid"]:
        stamp = '<div class="stamp-tranh">TRÁNH</div>' if c["cls"] == "tranh" else ""
        cells_html.append(
            f'    <div class="cell {c["cls"]}" data-idx="{c["index"]}">'
            f'<div class="cell-shine"></div>'
            f'{stamp}'
            f'<div class="chi">{c["chi"]}</div>'
            f'<div class="tag">{c["tag"]}</div>'
            f'</div>'
        )
    grid_cells_html = "\n".join(cells_html)

    # 12 khúc giờ con giáp cho thanh 24 giờ
    gio_indices_set = set(facts.get("gio_indices", []))
    gio_segs = []
    for i in range(12):
        is_tot = i in gio_indices_set
        cls_seg = "is-tot" if is_tot else "is-hac"
        gio_segs.append(f'<div class="gio-seg {cls_seg}"><span class="seg-chi">{CHI[i]}</span></div>')
    gio_bar_html = "\n".join(gio_segs)

    custom_css = """
  #head { top: 75px; left: 40px; right: 40px; text-align: center; }
  #chip { font-size: 34px; padding: 10px 30px; }
  #title { font-size: 82px; margin-top: 14px; line-height: 1.05; }
  
  #meta { margin-top: 14px; display: inline-flex; align-items: center; justify-content: center; gap: 12px;
          padding: 8px 24px; border-radius: 40px; background: rgba(0,0,0,0.38); border: 2px solid rgba(255,211,77,0.5); }
  #meta .tag-hd { position: relative; overflow: hidden; background: #ffd34d; color: #5a0805; font-weight: 900; font-size: 24px; padding: 4px 14px; border-radius: 10px; }
  #meta .tag-hd.hd-hac { background: #b91c1c; color: #fef2f2; }
  .tag-hd-shimmer { position: absolute; top: 0; left: 0; width: 60px; height: 100%;
                    background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.75) 50%, rgba(255,255,255,0) 100%);
                    transform: translateX(-100px) skewX(-20deg); pointer-events: none; }
  #meta .info-txt { color: #fff4cf; font-weight: 800; font-size: 26px; }

  #grid12 { position: absolute; left: 45px; right: 45px; top: 435px; height: 740px;
            display: grid; grid-template-columns: repeat(4, 1fr); grid-template-rows: repeat(3, 1fr); gap: 14px; }
  .cell { border-radius: 22px; display: flex; flex-direction: column; align-items: center; justify-content: center;
          position: relative; overflow: hidden; }
  .cell .cell-shine { position: absolute; inset: 0; border-radius: 20px;
                      background: radial-gradient(circle at center, rgba(255,255,255,0.75) 0%, rgba(255,255,255,0) 70%);
                      opacity: 0; pointer-events: none; z-index: 2; }
  .cell .chi { font-size: 74px; font-weight: 900; line-height: 1; z-index: 3; }
  .cell .tag { font-size: 22px; font-weight: 800; padding: 4px 12px; border-radius: 10px; margin-top: 8px; z-index: 3; }

  .cell.hop { background: linear-gradient(145deg, rgba(16, 185, 129, 0.42) 0%, rgba(6, 95, 70, 0.78) 100%);
              border: 3.5px solid #34d399; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.35); }
  .cell.hop .chi { color: #ecfdf5; text-shadow: 0 3px 8px rgba(0,0,0,.4); }
  .cell.hop .tag { background: #34d399; color: #064e3b; }

  .cell.tranh { background: linear-gradient(145deg, rgba(239, 68, 68, 0.5) 0%, rgba(153, 27, 27, 0.85) 100%);
                border: 3.5px solid #f87171; box-shadow: 0 8px 20px rgba(239, 68, 68, 0.4); }
  .cell.tranh .chi { color: #fff1f2; text-shadow: 0 3px 8px rgba(0,0,0,.4); }
  .cell.tranh .tag { background: #f87171; color: #7f1d1d; }

  .stamp-tranh { position: absolute; top: 12px; right: 10px; padding: 3px 10px;
                 border: 3px solid #ff4d4d; border-radius: 8px; color: #fff; background: #dc2626;
                 font-size: 22px; font-weight: 900; letter-spacing: .05em;
                 transform: scale(1) rotate(-12deg); opacity: 0.95;
                 box-shadow: 0 4px 10px rgba(0,0,0,0.5); pointer-events: none; z-index: 4; }

  .cell.luuy { background: linear-gradient(145deg, rgba(234, 179, 8, 0.45) 0%, rgba(161, 98, 7, 0.8) 100%);
               border: 3.5px solid #facc15; box-shadow: 0 8px 20px rgba(234, 179, 8, 0.35); }
  .cell.luuy .chi { color: #fef9c3; text-shadow: 0 3px 8px rgba(0,0,0,.4); }
  .cell.luuy .tag { background: #facc15; color: #713f12; }

  .cell.binh { background: linear-gradient(145deg, rgba(75, 12, 9, 0.85) 0%, rgba(42, 6, 4, 0.95) 100%);
               border: 2px solid rgba(242, 193, 78, 0.3); box-shadow: 0 6px 14px rgba(0,0,0,.25); }
  .cell.binh .chi { color: #fef08a; text-shadow: 0 3px 6px rgba(0,0,0,.4); }
  .cell.binh .tag { background: rgba(254, 240, 138, 0.16); color: #fde68a; }

  #info_box { position: absolute; left: 45px; right: 45px; top: 1195px; height: 305px;
              background: linear-gradient(180deg, rgba(90, 12, 8, 0.94), rgba(58, 8, 5, 0.96));
              border: 3.5px solid #f2c14e; border-radius: 28px; padding: 14px 22px;
              display: flex; flex-direction: column; justify-content: space-between;
              box-shadow: 0 12px 35px rgba(0,0,0,0.45); }
  .info-row { display: flex; align-items: center; gap: 16px; }
  .row-tag { flex: 0 0 140px; text-align: center; padding: 6px 0; border-radius: 12px;
             font-weight: 900; font-size: 26px; letter-spacing: .04em; }
  .row-tag.nen { background: #10b981; color: #022c22; }
  .row-tag.kieng { background: #ef4444; color: #450a0a; }
  .row-tag.gio { background: #f59e0b; color: #451a03; }
  .row-text { font-size: 28px; font-weight: 800; color: #fff; line-height: 1.25; }
  .row-text.gio-txt { font-size: 25px; color: #fef08a; line-height: 1.15; }

  .gio-row { align-items: center; }
  .gio-col { flex: 1; display: flex; flex-direction: column; gap: 6px; justify-content: center; }
  .gio-bar { display: grid; grid-template-columns: repeat(12, 1fr); gap: 4px; width: 100%; height: 38px; }
  .gio-seg { border-radius: 8px; display: flex; align-items: center; justify-content: center;
             font-weight: 900; font-size: 20px; line-height: 1; position: relative; }
  .gio-seg.is-tot { background: linear-gradient(180deg, #f59e0b, #d97706); color: #451a03;
                    border: 2px solid #fde68a; box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4); }
  .gio-seg.is-hac { background: rgba(0, 0, 0, 0.38); color: rgba(254, 240, 138, 0.38);
                    border: 1.5px solid rgba(255, 255, 255, 0.12); }

  #cap { bottom: 170px; font-size: 42px; }
  #subfoot { position: absolute; left: 50px; right: 50px; bottom: 100px; text-align: center;
             color: #ffd34d; font-weight: 900; font-size: 34px; letter-spacing: .06em;
             text-shadow: 0 2px 10px rgba(0,0,0,.7); }
  #foot { bottom: 45px; font-size: 23px; opacity: .85; }
"""
    tpl = tpl.replace("</style>", custom_css + "\n</style>")
    subfoot_div = '<div id="subfoot">DỪNG HÌNH TÌM TUỔI CỦA BẠN</div>'
    tpl = tpl.replace('<div id="foot">', f'{subfoot_div}\n  <div id="foot">')

    grid_and_box_html = f"""
  <div id="grid12">
{grid_cells_html}
  </div>
  <div id="info_box">
    <div class="info-row">
      <div class="row-tag nen">NÊN</div>
      <div class="row-text">{facts['nen_display']}</div>
    </div>
    <div class="info-row">
      <div class="row-tag kieng">TRÁNH</div>
      <div class="row-text">{facts['tranh_display']}</div>
    </div>
    <div class="info-row gio-row">
      <div class="row-tag gio">GIỜ TỐT</div>
      <div class="gio-col">
        <div class="gio-bar">
{gio_bar_html}
        </div>
        <div class="row-text gio-txt">{facts['gio_display']}</div>
      </div>
    </div>
  </div>
"""
    tpl = tpl.replace('<div id="rows"></div>', grid_and_box_html)

    tag_hd_cls = "tag-hd hd-hac" if not facts["is_hoang"] else "tag-hd"
    meta_html = f"""<div id="meta">
      <span class="{tag_hd_cls}">{facts["hoang_hac_str"]}<span class="tag-hd-shimmer"></span></span>
      <span class="info-txt">{facts["am_str"]} ÂM · {facts["can_chi_ngay"].upper()} · {facts["than"].upper()} · TRỰC {facts["truc"].upper()}</span>
    </div>"""
    tpl = tpl.replace("__TITLE__</div>", "__TITLE__</div>\n    " + meta_html)

    custom_script = """
  const DATA = __DATA__;
  const THEMES = {
    red:  { b1: "#d8321f", b2: "#b31b12", b3: "#7d0d08", b4: "#5a0805", r1: "rgba(122,12,8,.92)", r2: "rgba(88,7,4,.92)", gold: "#f2c14e", gold2: "#ffd34d", chip: "#fff6dc", chipfg: "#8a0f09", chiptop: "#ffe39a", chiptopfg: "#7d0d08" }
  };
  const TH = THEMES[DATA.theme || "red"];
  Object.entries(TH).forEach(([k, v]) => document.getElementById("root").style.setProperty("--" + k, v));
  const DUR = DATA.dur;

  // 1. Bagua SVG
  const svg = document.getElementById("bagua"), NS = "http://www.w3.org/2000/svg";
  const mk = (t, a, p) => { const e = document.createElementNS(NS, t); for (const k in a) e.setAttribute(k, a[k]); (p || svg).appendChild(e); return e; };
  mk("circle", { r: 460, fill: "none", stroke: "#ffd34d", "stroke-width": 10 });
  mk("circle", { r: 300, fill: "none", stroke: "#ffd34d", "stroke-width": 6 });
  mk("circle", { r: 150, fill: "none", stroke: "#ffd34d", "stroke-width": 6 });
  const TRI = ["111", "011", "101", "001", "110", "010", "100", "000"];
  TRI.forEach((code, k) => {
    const g = mk("g", { transform: `rotate(${k * 45}) translate(0 -380)` });
    [...code].forEach((b, j) => {
      const y = -36 + j * 36;
      if (b === "1") mk("rect", { x: -90, y, width: 180, height: 22, rx: 6, fill: "#ffd34d" }, g);
      else { mk("rect", { x: -90, y, width: 78, height: 22, rx: 6, fill: "#ffd34d" }, g); mk("rect", { x: 12, y, width: 78, height: 22, rx: 6, fill: "#ffd34d" }, g); }
    });
  });

  // 2. Deterministic Sparks
  let s = 7; const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const sparks = document.getElementById("sparks"), SP = [];
  for (let i = 0; i < 26; i++) {
    const d = document.createElement("div"); d.className = "spark";
    d.style.left = (rnd() * 1040 + 20) + "px"; d.style.top = (rnd() * 1840 + 40) + "px";
    sparks.appendChild(d); SP.push({ d, ph: rnd() * 6.28, sp: .6 + rnd() });
  }

  // 3. Subtitles
  const cap = document.getElementById("cap");
  const words = [];
  DATA.segs.forEach((sg) => {
    const ws = sg.text.split(/\\s+/);
    ws.forEach((w, i) => words.push({ w, t: sg.start + (sg.end - sg.start) * i / ws.length, s: sg }));
  });

  // 4. Element references for animations
  const cells = [...document.querySelectorAll("#grid12 .cell")];
  const hopCells = cells.filter(c => c.classList.contains("hop"));
  const xungCell = cells.find(c => c.classList.contains("tranh"));
  const luuyCells = cells.filter(c => c.classList.contains("luuy"));
  const stampEl = document.querySelector(".stamp-tranh");
  const chipShimmer = document.querySelector(".tag-hd-shimmer");
  const goodSegs = [...document.querySelectorAll(".gio-seg.is-tot")];

  const tl = gsap.timeline({ paused: true });
  const st = { t: 0 };

  tl.to(st, { t: DUR, duration: DUR, ease: "none", onUpdate: () => {
    const t = st.t;
    const p = t / DUR;

    // Ambient 1: Bagua rotation (45 deg = 1 octagram period, loop identical)
    svg.style.transform = `rotate(${p * 45}deg)`;

    // Ambient 2: Glow pulse
    document.getElementById("glow").style.opacity = 0.85 + 0.15 * Math.sin(p * Math.PI * 2);

    // Ambient 3: Sparks
    SP.forEach((o) => {
      o.d.style.opacity = 0.25 + 0.6 * (0.5 + 0.5 * Math.sin(o.ph + p * Math.PI * 2 * Math.round(o.sp * 2)));
    });

    // Effect A: Chip HOÀNG ĐẠO/HẮC ĐẠO slow shimmer (runs 3 full cycles across DUR)
    if (chipShimmer) {
      const shimP = (p * 3) % 1.0;
      const shimX = -100 + shimP * 340;
      chipShimmer.style.transform = `translateX(${shimX}px) skewX(-20deg)`;
    }

    // Effect B: 0.0s - 1.0s: Light sweep across 12 cells in zodiac order
    if (t < 1.0) {
      cells.forEach((cell, idx) => {
        const t_c = idx * (0.92 / 12);
        const dist = Math.abs(t - t_c);
        const shine = cell.querySelector(".cell-shine");
        if (dist < 0.075) {
          const q = 1.0 - dist / 0.075;
          if (shine) shine.style.opacity = q * 0.85;
          cell.style.filter = `brightness(${1 + q * 0.4})`;
        } else {
          if (shine) shine.style.opacity = 0;
          cell.style.filter = "none";
        }
      });
    } else {
      cells.forEach((cell) => {
        const shine = cell.querySelector(".cell-shine");
        if (shine) shine.style.opacity = 0;
        cell.style.filter = "none";
      });
    }

    // Effect C: 0.95s - 1.40s: Light lands on HỢP cells (bright green border, gentle heartbeat pulse)
    if (t >= 0.95 && t <= 1.40) {
      const dt_hop = (t - 0.95) / 0.45;
      const q_hop = Math.sin(dt_hop * Math.PI);
      hopCells.forEach((c) => {
        c.style.transform = `scale(${1 + q_hop * 0.045})`;
        c.style.boxShadow = `0 8px ${20 + q_hop * 16}px rgba(52, 211, 153, ${0.35 + q_hop * 0.55})`;
        c.style.borderColor = q_hop > 0.3 ? "#6ee7b7" : "#34d399";
      });
    } else {
      hopCells.forEach((c) => {
        c.style.transform = "scale(1)";
        c.style.boxShadow = "0 8px 20px rgba(16, 185, 129, 0.35)";
        c.style.borderColor = "#34d399";
      });
    }

    // Effect D: ~1.2s: Ô XUNG stamp "TRÁNH" drops down (stamp slam + shake); ô LƯU Ý vibrates softly
    if (stampEl && xungCell) {
      if (t >= 1.05 && t < 1.18) {
        // Lift up
        const q_lift = (t - 1.05) / 0.13;
        stampEl.style.transform = `scale(${1 + q_lift * 0.55}) rotate(${-12 - q_lift * 3}deg)`;
        stampEl.style.opacity = `${0.95 - q_lift * 0.35}`;
      } else if (t >= 1.18 && t <= 1.25) {
        // Slam down
        const q_slam = (t - 1.18) / 0.07;
        const sc = 1.55 - q_slam * 0.59;
        stampEl.style.transform = `scale(${sc}) rotate(${-15 + q_slam * 3}deg)`;
        stampEl.style.opacity = "1";
      } else if (t > 1.25 && t <= 1.35) {
        // Settle back to 1.0
        const q_set = (t - 1.25) / 0.10;
        stampEl.style.transform = `scale(${0.96 + q_set * 0.04}) rotate(-12deg)`;
        stampEl.style.opacity = "0.95";
      } else {
        stampEl.style.transform = "scale(1) rotate(-12deg)";
        stampEl.style.opacity = "0.95";
      }

      // XUNG cell impact shake (1.24s - 1.44s)
      if (t >= 1.24 && t <= 1.44) {
        const dt_x = (t - 1.24) / 0.20;
        const env_x = 1.0 - dt_x;
        const shake_x = Math.sin(dt_x * Math.PI * 2 * 20) * 5 * env_x;
        xungCell.style.transform = `translateX(${shake_x}px)`;
      } else {
        xungCell.style.transform = "none";
      }

      // LƯU Ý subtle vibration (1.26s - 1.42s)
      if (t >= 1.26 && t <= 1.42) {
        const dt_l = (t - 1.26) / 0.16;
        const env_l = 1.0 - dt_l;
        const shake_l = Math.sin(dt_l * Math.PI * 2 * 16) * 2 * env_l;
        luuyCells.forEach((c) => c.style.transform = `translateX(${shake_l}px)`);
      } else {
        luuyCells.forEach((c) => c.style.transform = "none");
      }
    }

    // Effect E: 1.6s - 2.6s: Dải GIỜ TỐT: 6 khúc giờ tốt sáng lần lượt
    goodSegs.forEach((seg, k) => {
      const t_flare_start = 1.60 + k * 0.14;
      const t_flare_end = t_flare_start + 0.22;
      if (t >= t_flare_start && t <= t_flare_end) {
        const q_f = Math.sin(((t - t_flare_start) / 0.22) * Math.PI);
        seg.style.transform = `scale(${1 + q_f * 0.16})`;
        seg.style.filter = `brightness(${1 + q_f * 0.85})`;
        seg.style.boxShadow = `0 0 ${8 + q_f * 20}px #ffd34d`;
        seg.style.zIndex = "5";
      } else {
        seg.style.transform = "scale(1)";
        seg.style.filter = "none";
        seg.style.boxShadow = "0 2px 8px rgba(245, 158, 11, 0.4)";
        seg.style.zIndex = "1";
      }
    });

    // Subtitles karaoke
    const cur = DATA.segs.find((sg) => t >= sg.start - 0.05 && t < sg.end + 0.25);
    if (cur) {
      if (cap.dataset.s !== cur.text) {
        cap.dataset.s = cur.text;
        cap.innerHTML = words.filter((w) => w.s === cur).map((w) => `<span class="cw" data-t="${w.t}">${w.w}</span>`).join(" ");
      }
      cap.querySelectorAll(".cw").forEach((e) => e.classList.toggle("on", +e.dataset.t <= t + 0.02));
      cap.style.opacity = 1;
    } else {
      cap.style.opacity = 0;
    }
  }});

  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = tl;
  tl.seek(0);
"""

    prefix = tpl[: tpl.rfind("<script>") + len("<script>")]
    suffix = tpl[tpl.rfind("</script>") :]
    tpl = prefix + "\n" + custom_script + "\n" + suffix

    data_payload = {
        "dur": dur,
        "theme": "red",
        "segs": segs
    }

    chip_txt = f"{facts['dow_vi'].upper()} · {facts['duong_str']}"
    title_line1 = f"NGÀY MAI {facts['solar_day']}/{facts['solar_month']}"
    title_line2 = "TUỔI BẠN THẾ NÀO?"
    title_html = f'<span class="l s">{title_line1}</span><span class="l gold">{title_line2}</span>'

    html = (
        tpl.replace("__DUR__", str(dur))
        .replace("__CHIP__", chip_txt)
        .replace("__TITLE__", title_html)
        .replace("__DATA__", json.dumps(data_payload, ensure_ascii=False))
    )
    return html


def extract_qa_sheet(mp4: Path, out_jpg: Path, n_frames: int = 4) -> None:
    r_probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
        capture_output=True, text=True
    )
    dur = float((r_probe.stdout or "0").strip() or 0)
    times = [round(dur * (i + 0.5) / n_frames, 2) for i in range(n_frames)]

    imgs = []
    for t in times:
        cmd = [
            "ffmpeg", "-y", "-ss", str(t), "-i", str(mp4),
            "-vframes", "1", "-vf", "scale=360:640", "-f", "image2pipe", "-vcodec", "mjpeg", "-"
        ]
        p = subprocess.run(cmd, capture_output=True)
        if p.stdout:
            img = Image.open(io.BytesIO(p.stdout)).convert("RGB")
            draw = ImageDraw.Draw(img)
            draw.text((15, 15), f"{t:.1f}s", fill=(255, 255, 255))
            imgs.append(img)

    if not imgs:
        return

    sheet = Image.new("RGB", (360 * len(imgs), 640))
    for i, im in enumerate(imgs):
        sheet.paste(im, (i * 360, 0))
    sheet.save(out_jpg, quality=85)


def export_last_frames(mp4: Path, out_dir: Path, rid: str) -> tuple[Path, Path]:
    r_probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)],
        capture_output=True, text=True
    )
    dur = float((r_probe.stdout or "0").strip() or 0)
    t = max(0.1, dur - 0.25)
    p_1080 = out_dir / f"{rid}_frame_1080.png"
    p_168 = out_dir / f"{rid}_frame_168.png"

    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(t), "-i", str(mp4), "-vframes", "1", str(p_1080)],
        check=True, capture_output=True
    )
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(t), "-i", str(mp4), "-vframes", "1", "-vf", "scale=168:-1", str(p_168)],
        check=True, capture_output=True
    )
    return p_1080, p_168


def render(target_date: dt.date | str, out_dir: Path | str | None = None, prefix: str | None = None) -> dict:
    """Hàm chuẩn render short khuôn A cho ngày chỉ định."""
    if isinstance(target_date, str):
        target_date = dt.date.fromisoformat(target_date)

    if out_dir is None:
        out_dir = SAMPLE_DIR
    out_dir = Path(out_dir).resolve()   # đường dẫn tuyệt đối: lệnh render chạy với cwd = hyperframes_short
    out_dir.mkdir(parents=True, exist_ok=True)

    dtag = target_date.strftime("%Y%m%d")
    rid = prefix if prefix else f"hd_{dtag}"

    facts = day_data(target_date)
    lines = facts["script"]

    txt_path = out_dir / f"{rid}.txt"
    wav_path = out_dir / f"{rid}.wav"
    mp4_path = out_dir / f"{rid}.mp4"

    clean_lines = [l.replace("**", "") for l in lines]
    txt_path.write_text("\n".join(clean_lines) + "\n", encoding="utf-8")

    if not wav_path.is_file():
        ok = R.render_tts(txt_path, wav_path, clean_lines, voice="Sơn")
        if not ok:
            raise RuntimeError(f"TTS giọng Sơn thất bại cho {rid}")

    manifest_p = wav_path.with_suffix(".json")
    manifest = json.loads(manifest_p.read_text(encoding="utf-8"))
    segs = manifest.get("segments") or []
    speech_end = segs[-1]["end"] if segs else 12.0
    dur = round(max(12.0, min(16.0, speech_end + 2.0)), 2)

    html = build_composition_html(facts, dur=dur, segs=segs)
    comp_file = COMP / f"_tb_{rid}.html"
    comp_file.write_text(html, encoding="utf-8")

    silent_mp4 = out_dir / f"{rid}_silent.mp4"
    cmd = (
        f'export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1; nvm use 22 >/dev/null 2>&1; '
        f'cd "{HF}" && npx --yes hyperframes@0.8.75 render . -c compositions/{comp_file.name} --output "{silent_mp4}" --quality looks --fps 30 --quiet'
    )
    p = subprocess.run(["/bin/bash", "-lc", cmd], capture_output=True, text=True, timeout=1800)
    comp_file.unlink(missing_ok=True)

    if p.returncode != 0 or not silent_mp4.exists():
        raise RuntimeError(f"Render HyperFrames thất bại cho {rid}:\n" + (p.stdout + p.stderr)[-2000:])

    bgm_path = ROOT / FS_BGM
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(silent_mp4), "-i", str(wav_path),
            "-stream_loop", "-1", "-i", str(bgm_path),
            "-filter_complex",
            f"[1:a]apad[v];[2:a]volume={FS_BGM_GAIN},afade=t=out:st={dur - 1.2}:d=1.2[m];[v][m]amix=inputs=2:duration=first:normalize=0[a]",
            "-map", "0:v", "-map", "[a]", "-t", str(dur),
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(mp4_path)
        ],
        check=True
    )
    silent_mp4.unlink(missing_ok=True)

    qa_sheet = out_dir / f"{rid}_qa.jpg"
    extract_qa_sheet(mp4_path, qa_sheet)
    f_1080, f_168 = export_last_frames(mp4_path, out_dir, rid)

    render_json_path = mp4_path.with_suffix(".render.json")
    render_json_path.write_text(
        json.dumps({
            "ok": True,
            "output": str(mp4_path.relative_to(ROOT)),
            "duration_s": dur,
            "speech_end_s": speech_end,
            "tail_s": round(dur - speech_end, 2),
            "style": "yeartable_daily_a",
            "voice": "Sơn",
            "bgm": FS_BGM,
            "bgm_gain": FS_BGM_GAIN
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    return {
        "id": rid,
        "mp4": mp4_path,
        "duration": dur,
        "speech_end": speech_end,
        "qa_sheet": qa_sheet,
        "frame_1080": f_1080,
        "frame_168": f_168,
        "facts": facts
    }


def generate_week_sheet(results: list[dict], out_sheet: Path) -> Path:
    """Tạo tờ khung tuần week_sheet.jpg:
    - Khung cuối 7 ngày
    - 3 khung motion ngày đầu tiên (t=0.5s [quét vệt sáng], t=1.25s [dấu TRÁNH], t=2.0s [giờ tốt sáng])
    Tổng 10 khung, xếp lưới 2 hàng x 5 cột (1800x1280).
    """
    out_sheet.parent.mkdir(parents=True, exist_ok=True)
    day0_res = results[0]
    day0_mp4 = day0_res["mp4"]
    f0 = day0_res["facts"]
    d0_lbl = f"{f0['solar_day']}/{f0['solar_month']}"

    motion_times = [
        (0.5, f"{d0_lbl} · 0.5s: Vệt sáng quét 12 ô"),
        (1.25, f"{d0_lbl} · 1.25s: Đóng dấu TRÁNH"),
        (2.0, f"{d0_lbl} · 2.0s: Khúc giờ tốt sáng"),
    ]

    tiles = []
    # 7 khung cuối (7 ngày)
    for r in results:
        f = r["facts"]
        lbl = f"{f['solar_day']}/{f['solar_month']} · Khung cuối ({f['can_chi_ngay']})"
        img = Image.open(r["frame_1080"]).convert("RGB").resize((360, 640), Image.Resampling.LANCZOS)
        tiles.append((img, lbl))

    # 3 khung motion ngày đầu tiên
    for t_sec, lbl in motion_times:
        cmd = [
            "ffmpeg", "-y", "-ss", str(t_sec), "-i", str(day0_mp4),
            "-vframes", "1", "-vf", "scale=360:640", "-f", "image2pipe", "-vcodec", "mjpeg", "-"
        ]
        p = subprocess.run(cmd, capture_output=True)
        if p.stdout:
            img = Image.open(io.BytesIO(p.stdout)).convert("RGB")
            tiles.append((img, lbl))

    # Xếp vào canvas 1800 x 1280 (2 hàng, 5 cột)
    sheet = Image.new("RGB", (360 * 5, 640 * 2), (20, 15, 15))
    draw = ImageDraw.Draw(sheet)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    except Exception:
        font = ImageFont.load_default()

    for idx, (im, label) in enumerate(tiles[:10]):
        col = idx % 5
        row = idx // 5
        x = col * 360
        y = row * 640
        sheet.paste(im, (x, y))

        # Banner nhãn phía trên
        draw.rectangle([(x + 8, y + 10), (x + 352, y + 46)], fill=(15, 15, 15))
        draw.rectangle([(x + 8, y + 10), (x + 352, y + 46)], outline=(242, 193, 78), width=2)
        draw.text((x + 14, y + 16), label, fill=(255, 230, 120), font=font)

    sheet.save(out_sheet, quality=88)
    return out_sheet


def batch_render_week(start_date: dt.date | str | None = None, out_dir: Path | str | None = None) -> list[dict]:
    """Render 7 short hoàng đạo liên tiếp, xuất plan_hd_week_<start>.json và week_sheet.jpg."""
    if out_dir is None:
        out_dir = RENDER_HD_DIR
    out_dir = Path(out_dir).resolve()   # đường dẫn tuyệt đối: lệnh render chạy với cwd = hyperframes_short
    out_dir.mkdir(parents=True, exist_ok=True)

    if start_date is None:
        start_date = find_next_available_thursday(out_dir)
    elif isinstance(start_date, str):
        start_date = dt.date.fromisoformat(start_date)

    week_dates = get_week_dates(start_date)
    start_str = start_date.isoformat()
    end_str = week_dates[-1]

    print("=" * 70)
    print(f"BẮT ĐẦU RENDER LÔ 7 SHORT HOÀNG ĐẠO ({start_str} – {end_str}):")
    print(f"Thư mục xuất: {out_dir}")
    print("=" * 70)

    results = []
    plan_entries = []

    for idx, d_str in enumerate(week_dates):
        t_date = dt.date.fromisoformat(d_str)
        meta = get_week_meta(t_date, day_idx=idx)
        plan_entries.append(meta["plan_item"])

        print(f"\n>>> Đang render ngày {d_str} ({meta['facts']['dow_vi']}) - Tiêu đề: \"{meta['title']}\"")
        r = render(t_date, out_dir=out_dir)
        results.append(r)
        print(f"    [XONG] Video: {r['mp4'].name} ({r['duration']:.2f}s, giọng: {r['speech_end']:.2f}s)")

    # Ghi plan_hd_week_<start>.json và plan_hd_week.json
    plan_path = out_dir / f"plan_hd_week_{start_str}.json"
    plan_content = json.dumps(plan_entries, ensure_ascii=False, indent=2) + "\n"
    plan_path.write_text(plan_content, encoding="utf-8")
    (out_dir / "plan_hd_week.json").write_text(plan_content, encoding="utf-8")
    print(f"\n[OK] Đã ghi plan tuần: {plan_path.relative_to(ROOT)} ({len(plan_entries)} short)")

    # Xuất tờ khung tuần week_sheet_<start>.jpg và week_sheet.jpg
    sheet_path = out_dir / f"week_sheet_{start_str}.jpg"
    generate_week_sheet(results, sheet_path)
    shutil.copy2(sheet_path, out_dir / "week_sheet.jpg")
    print(f"[OK] Đã xuất tờ khung tuần: {sheet_path.relative_to(ROOT)}")

    return results


def self_check() -> int:
    """Tự kiểm 7 ngày verified trong calendar_facts_verified.json."""
    if not VERIFIED.is_file():
        return 0
    ver = json.loads(VERIFIED.read_text(encoding="utf-8"))
    bad = 0
    for iso, exp in ver.items():
        f = day_data(dt.date.fromisoformat(iso))
        exp_gio = [p.split(" (")[0] for p in exp["gio_tot"].split(", ")]
        got = [f["am_str"], f["can_chi_ngay"], f["than"], "hoàng đạo" if f["is_hoang"] else "hắc đạo", f["truc"], f["xung_chi"], f["gio_hoang_dao"]]
        want = [exp["am_lich"], exp["ngay"], exp["than"], exp["hoang_hac"], exp["truc"], exp["xung"], exp_gio]
        if got != want:
            bad += 1
            print(f"LỆCH {iso}: got {got} != want {want}")
    if bad:
        raise SystemExit(f"Tự kiểm verified thất bại: lệch {bad}/{len(ver)}")
    return len(ver)


def print_daily_summary(f: dict) -> None:
    print("\n" + "=" * 65)
    print(f"DỮ KIỆN LỊCH HOÀNG ĐẠO NGÀY {f['duong_str']} ({f['dow_vi']}):")
    print("=" * 65)
    print(f"Âm lịch         : {f['am_str']} (Năm Bính Ngọ)")
    print(f"Can chi ngày    : {f['can_chi_ngay']}")
    print(f"Thần            : {f['than']} ({f['hoang_hac_str']})")
    print(f"Trực            : {f['truc']} (Tháng tiết {f['tiet_thang']}, ngày {f['chi_ngay']})")
    print(f"XUNG ngày       : {f['xung_chi']}")
    print(f"HỢP ngày        : {', '.join(f['tam_hop'])} (Tam hợp), {f['luc_hop']} (Lục hợp)")
    print(f"LƯU Ý           : {f['luc_hai']} (Hại), {f['luc_pha']} (Phá)")
    ky_txt = ", ".join(f["dan"]) if f["dan"] else "Không (bình thường)"
    print(f"Tam Nương/Nguyệt kỵ: {ky_txt}")
    print(f"NÊN             : {f['nen_display']}")
    print(f"TRÁNH           : {f['tranh_display']}")
    print(f"GIỜ TỐT         : {f['gio_display']}")

    print("\n--- 12 CON GIÁP (BẢNG 4x3) ---")
    for row in range(3):
        cells = f["zodiac_grid"][row*4 : (row+1)*4]
        line = " | ".join(f"{c['chi']}: {c['tag']:<8} ({c['reason']})" for c in cells)
        print(f"  Hàng {row+1}: {line}")

    print("\n--- LỜI ĐỌC (3 CÂU, ≤ 3 CHI/CÂU, CHỈ DÙNG TÊN CHI) ---")
    animal_forbidden = {"chuột", "trâu", "hổ", "mèo", "rồng", "rắn", "ngựa", "dê", "khỉ", "gà", "chó", "lợn"}
    for i, line in enumerate(f["script"], 1):
        found = [w for w in line.replace(",", " ").replace(".", " ").split() if w in set(CHI)]
        assert len(found) <= 3, f"Vi phạm luật: > 3 chi trong câu {i}: {found}"
        line_words = {w.strip(".,;:?!\"'").lower() for w in line.split()}
        bad_found = line_words & animal_forbidden
        assert not bad_found, f"Vi phạm luật FS: Dùng từ con vật {bad_found} thay vì tên chi trong câu {i}"
        print(f"  {i}. {line} [{len(found)} chi: {', '.join(found)} - GUARD ĐẠT]")

    # Guard Luật 13: Ngày Tam Nương/Nguyệt kỵ/Dương Công hoặc hắc đạo thì NÊN không được có việc lớn
    major_words = ("cưới", "đính hôn", "khai trương", "làm nhà", "nhập trạch")
    if f["dan"] or not f["is_hoang"]:
        for v in f["viec_nen"]:
            for mw in major_words:
                assert mw not in v.lower(), f"Vi phạm Luật 13: ngày {f['duong_str']} có {f['dan']} hoặc hắc đạo mà NÊN có '{v}'"

    print("=" * 65 + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bộ sinh short Lịch Hoàng Đạo hằng ngày (khuôn A)")
    parser.add_argument("date", nargs="?", default=None, help="Ngày cần tính YYYY-MM-DD")
    parser.add_argument("--start", help="Ngày bắt đầu cho lô tuần YYYY-MM-DD (mặc định thứ Năm kế tiếp chưa có lô)")
    parser.add_argument("--week", action="store_true", help="Render trọn lô 7 ngày tuần vào render_hd")
    parser.add_argument("--sheet", action="store_true", help="Dựng lại week_sheet từ mp4/khung đang có (không render)")
    parser.add_argument("--check-week", action="store_true", help="Kiểm tra facts và guard 7 ngày của lô tuần")
    parser.add_argument("--check", action="store_true", help="Kiểm tra facts và guard 7 ngày của lô tuần")
    parser.add_argument("--check-all", action="store_true", help="Chạy kiểm tra facts cho 22, 23, 24/10/2026")
    parser.add_argument("--render", action="store_true", help="Thực hiện render video MP4 và khung QA")
    parser.add_argument("--out-dir", default=str(RENDER_HD_DIR), help="Thư mục xuất file")
    args = parser.parse_args()

    # 1. Tự kiểm 7 ngày verified
    n_ver = self_check()
    print(f"[OK] Tự kiểm facts verified: {n_ver}/{n_ver} ngày khớp 100%.")

    out_dir = Path(args.out_dir).resolve()
    start_date = None
    if args.start:
        start_date = dt.date.fromisoformat(args.start)

    if args.check or args.check_week:
        if start_date is None:
            start_date = find_next_available_thursday(out_dir)
        week_dates = get_week_dates(start_date)
        print(f"\n>>> KIỂM TRA DỮ LIỆU VÀ GUARD CHO 7 NGÀY TUẦN ({week_dates[0]} – {week_dates[-1]}):")
        for idx, d_str in enumerate(week_dates):
            meta = get_week_meta(d_str, day_idx=idx)
            print(f"\n[TIÊU ĐỀ DỰ KIẾN]: {meta['title']}")
            print(f"[INSIGHT DỰ KIẾN]: {meta['insight']}")
            print(f"[LỊCH ĐĂNG DỰ KIẾN]: {meta['plan_item']['day']} slot {meta['plan_item']['slot']} (D-2)")
            print_daily_summary(meta["facts"])

        sheet_candidates = [
            out_dir / f"week_sheet_{start_date.isoformat()}.jpg",
            out_dir / "week_sheet.jpg"
        ]
        found_sheet = next((s for s in sheet_candidates if s.is_file()), None)
        if found_sheet:
            print(f"[TỜ KHUNG TUẦN]: Đã có tại {found_sheet.relative_to(ROOT)} ({found_sheet.stat().st_size} bytes)")
        else:
            print(f"[TỜ KHUNG TUẦN]: Chưa render cho tuần {start_date.isoformat()}")
        print("TỔNG: KHỚP 7/7")
        return 0

    if args.sheet:
        if start_date is None:
            start_date = find_next_available_thursday(out_dir)
        week_dates = get_week_dates(start_date)
        start_str = start_date.isoformat()
        results = []
        for d_str in week_dates:
            d = dt.date.fromisoformat(d_str)
            rid = f"hd_{d.strftime('%Y%m%d')}"
            mp4_path = out_dir / f"{rid}.mp4"
            if not mp4_path.is_file():
                sys.exit(f"Lỗi: Không tìm thấy video {mp4_path.name} để dựng week_sheet")
            f_1080 = out_dir / f"{rid}_frame_1080.png"
            f_168 = out_dir / f"{rid}_frame_168.png"
            qa_sheet = out_dir / f"{rid}_qa.jpg"
            if not f_1080.is_file():
                f_1080, f_168 = export_last_frames(mp4_path, out_dir, rid)
            f = day_data(d)
            results.append({
                "id": rid,
                "mp4": mp4_path,
                "frame_1080": f_1080,
                "frame_168": f_168,
                "facts": f,
                "qa_sheet": qa_sheet
            })
        sheet_path = out_dir / f"week_sheet_{start_str}.jpg"
        generate_week_sheet(results, sheet_path)
        shutil.copy2(sheet_path, out_dir / "week_sheet.jpg")
        print(f"[OK] Đã dựng lại tờ khung tuần: {sheet_path.relative_to(ROOT)} ({sheet_path.stat().st_size} bytes)")
        return 0

    if args.week:
        batch_render_week(start_date=start_date, out_dir=out_dir)
        return 0

    if args.check_all:
        for d_str in ["2026-10-22", "2026-10-23", "2026-10-24"]:
            f = day_data(d_str)
            print_daily_summary(f)
        return 0

    target_date_str = args.date if args.date else "2026-10-22"
    target_date = dt.date.fromisoformat(target_date_str)
    f = day_data(target_date)
    print_daily_summary(f)

    if args.render:
        print("Đang tiến hành render video...")
        r = render(target_date, out_dir=out_dir)
        print("\n--- KẾT QUẢ RENDER ---")
        print(f"  Video:       {r['mp4'].relative_to(ROOT)}")
        print(f"  Thời lượng:  {r['duration']:.2f}s (giọng đọc: {r['speech_end']:.2f}s, đuôi: {round(r['duration'] - r['speech_end'], 2):.2f}s)")
        print(f"  QA sheet:    {r['qa_sheet'].relative_to(ROOT)}")
        print(f"  Khung 1080:  {r['frame_1080'].relative_to(ROOT)}")
        print(f"  Khung 168:   {r['frame_168'].relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
