"""Đối chiếu ĐỘC LẬP lô hoàng đạo (không import amlich/canchi/ngaytot/hoangdao_daily).

Dùng: python3 -I output/cl_staging/grok/tools/hoangdao_indep_check.py <plan_hd_week_*.json>

Tính lại bằng công thức riêng: can chi ngày (JDN), ngày/tháng âm (trăng mới Meeus ch.49,
giờ VN), tháng tiết (kinh độ Mặt Trời, Meeus ch.25 rút gọn), thần trực nhật theo tháng âm,
trực theo tháng tiết, xung/tam hợp/lục hợp, Tam Nương / Nguyệt kỵ / Dương Công.
Rồi so với insight + lời đọc trong plan, và kiểm lời đọc không tự mâu thuẫn
(ngày có Tam Nương/Nguyệt kỵ/Dương Công hoặc hắc đạo mà vẫn "hợp cưới/đính hôn").
Neo tháng âm: 1/9 Bính Ngọ = 10/10/2026; 2026–2027 không có tháng nhuận. Ngoài khoảng đó: báo lỗi.
"""
import datetime as dt
import json
import math
import sys
from pathlib import Path

CAN = "Giáp Ất Bính Đinh Mậu Kỷ Canh Tân Nhâm Quý".split()
CHI = "Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi".split()
THAN = ["Thanh Long", "Minh Đường", "Thiên Hình", "Chu Tước", "Kim Quỹ", "Kim Đường",
        "Bạch Hổ", "Ngọc Đường", "Thiên Lao", "Nguyên Vũ", "Tư Mệnh", "Câu Trần"]
HD = {0, 1, 4, 5, 7, 10}
TRUC = "Kiến Trừ Mãn Bình Định Chấp Phá Nguy Thành Thu Khai Bế".split()
# Thanh Long khởi ở chi nào theo chi tháng âm
TL_START = {2: 0, 8: 0, 3: 2, 9: 2, 4: 4, 10: 4, 5: 6, 11: 6, 0: 8, 6: 8, 1: 10, 7: 10}
TAM_NUONG = {3, 7, 13, 18, 22, 27}
NGUYET_KY = {5, 14, 23}
DUONG_CONG = {1: {13}, 2: {11}, 3: {9}, 4: {7}, 5: {5}, 6: {3}, 7: {8, 29}, 8: {27},
              9: {25}, 10: {23}, 11: {21}, 12: {19}}
ANCHOR = (dt.date(2026, 10, 10), 9)   # 1/9 âm Bính Ngọ
VALID = (dt.date(2026, 10, 10), dt.date(2027, 12, 31))
NO_WEDDING_FROM = dt.date(2026, 11, 5)
MAJOR_WORDS = ("cưới", "đính hôn", "khai trương", "làm nhà", "nhập trạch")


def jdn(d):
    return d.toordinal() + 1721425


def newmoon_jd(k):
    T = k / 1236.85
    jde = 2451550.09766 + 29.530588861 * k + 0.00015437 * T * T
    M = math.radians(2.5534 + 29.10535670 * k)
    Mp = math.radians(201.5643 + 385.81693528 * k)
    F = math.radians(160.7108 + 390.67050284 * k)
    Om = math.radians(124.7746 - 1.56375588 * k)
    E = 1 - 0.002516 * T
    jde += (-0.40720 * math.sin(Mp) + 0.17241 * E * math.sin(M) + 0.01608 * math.sin(2 * Mp)
            + 0.01039 * math.sin(2 * F) + 0.00739 * E * math.sin(Mp - M) - 0.00514 * E * math.sin(Mp + M)
            + 0.00208 * E * E * math.sin(2 * M) - 0.00111 * math.sin(Mp - 2 * F)
            - 0.00057 * math.sin(Mp + 2 * F) + 0.00056 * E * math.sin(2 * Mp + M)
            - 0.00042 * math.sin(3 * Mp) + 0.00042 * E * math.sin(M + 2 * F)
            + 0.00038 * E * math.sin(M - 2 * F) - 0.00024 * E * math.sin(2 * Mp - M)
            - 0.00017 * math.sin(Om))
    return jde - 69 / 86400


def vn_date(jd):
    return dt.date.fromordinal(int(math.floor(jd + 0.5 + 7 / 24)) - 1721425)


def sun_lon(jd):
    T = (jd - 2451545.0) / 36525
    L0 = 280.46646 + 36000.76983 * T
    M = math.radians(357.52911 + 35999.05029 * T)
    C = (1.914602 - 0.004817 * T) * math.sin(M) + 0.019993 * math.sin(2 * M) + 0.000289 * math.sin(3 * M)
    om = math.radians(125.04 - 1934.136 * T)
    return (L0 + C - 0.00569 - 0.00478 * math.sin(om)) % 360


NEWMOONS = sorted(vn_date(newmoon_jd(k)) for k in range(320, 350))


def lunar(d):
    starts = [x for x in NEWMOONS if x >= ANCHOR[0]]
    i = max(k for k, s in enumerate(starts) if s <= d)
    return (d - starts[i]).days + 1, (ANCHOR[1] - 1 + i) % 12 + 1


def tiet_chi(d):
    # Ngày giao tiết đã thuộc tiết mới (trực lặp lại hôm trước), nên tính ở CUỐI ngày giờ VN.
    # Đối chiếu xemlicham/ngaydep: 07/11/2026 (Lập đông 16:47) trực Khai. Dần bắt đầu ở Lập xuân 315°.
    jd = jdn(d) + 0.5 - 7 / 24 - 1e-6
    return (int(((sun_lon(jd) - 315) % 360) // 30) + 2) % 12


def main(path):
    p = Path(path)
    if not p.is_file():
        for parent in (Path("output/cl_staging/grok"), Path("output/cl_staging/fs")):
            cand = parent / path
            if cand.is_file():
                p = cand
                break
    plan = json.load(open(p, encoding="utf-8"))
    ok = True
    for p in plan:
        d = dt.date(int(p["id"][3:7]), int(p["id"][7:9]), int(p["id"][9:11]))
        if not VALID[0] <= d <= VALID[1]:
            sys.exit(f"{d}: ngoài khoảng neo tháng âm {VALID}, cần cập nhật ANCHOR")
        j = jdn(d)
        can, chi = (j + 9) % 10, (j + 1) % 12
        ld, lm = lunar(d)
        # Thần trực nhật theo THÁNG ÂM (xemlicham/ngaydep: 07/11/2026 = Kim Đường hoàng đạo), không theo tiết.
        than_i = (chi - TL_START[(lm + 1) % 12]) % 12
        than = THAN[than_i]
        truc = TRUC[(chi - tiet_chi(d)) % 12]
        xung = CHI[(chi + 6) % 12]
        hop = [CHI[(chi + 4) % 12], CHI[(chi + 8) % 12], CHI[(1 - chi) % 12]]
        flags = [n for n, s in (("Tam Nương", TAM_NUONG), ("Nguyệt kỵ", NGUYET_KY),
                                ("Dương Công", DUONG_CONG[lm])) if ld in s]
        s1 = p["script"][0]
        txt = " ".join(p["script"]) + " " + p["insight"]
        nen = s1.split("hợp ", 1)[1] if "hợp " in s1 else ""
        checks = {
            "can chi": f"{CAN[can]} {CHI[chi]}" in p["insight"],
            "âm": f"({ld}/{lm} âm" in p["insight"],   # có thể kèm ", rằm"
            "thần": than in p["insight"],
            "hoàng/hắc": ("hoàng đạo" if than_i in HD else "hắc đạo") in s1,
            "trực": f"trực {truc}" in s1,
            "xung": f"Tuổi {xung} xung" in p["script"][1],
            "hợp": all(h in p["script"][2] for h in hop),
            "cờ ngày": all(f in txt for f in flags)
            and not any(f in txt for f in {"Tam Nương", "Nguyệt kỵ", "Dương Công"} - set(flags)),
            "Nên≠Tránh": not ((flags or than_i not in HD) and any(w in nen for w in MAJOR_WORDS)),
            # Người dùng 20/10/2026: short hằng ngày không khuyên cưới hỏi (để làn ngày tốt theo việc lo).
            "không cưới": d < NO_WEDDING_FROM or not any(w in nen for w in ("cưới", "đính hôn")),
        }
        bad = [k for k, v in checks.items() if not v]
        ok &= not bad
        print(d, f"{ld}/{lm}", CAN[can], CHI[chi], than, truc, "xung", xung, "hợp", hop, flags,
              "OK" if not bad else f"LỆCH {bad}")
    print("TỔNG:", f"KHỚP {len(plan)}/{len(plan)}" if ok else "CÓ LỆCH")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
