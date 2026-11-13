"""Bộ dữ liệu FS cho một con giáp trong một tháng âm lịch bất kỳ."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from fs_calendar import amlich as A
from fs_calendar import batrach as BT
from fs_calendar import canchi as K
from fs_calendar import ngaytot as NT
from fs_calendar import tuvi_year as TY

ANCHORS = ("mùng 1 âm", "rằm âm", "Đông chí", "Hạ chí", "Noel 24/12", "Noel 25/12",
           "31/12", "01/01", "14/02")


def _solar_term_day(year: int, degree: int) -> dt.date:
    """Tìm ngày VN mà kinh độ Mặt Trời vượt mốc; giữ cách tính của ngaytot."""
    start = A.jd_from_date(1, 1, year) - 2
    end = A.jd_from_date(31, 12, year) + 2
    prev, jd = NT.lon_deg(start), start
    while jd < end:
        jd += 1 / 24
        cur = NT.lon_deg(jd)
        if prev <= degree < cur or (prev > cur and (prev <= degree or degree < cur)):
            lo, hi = jd - 1 / 24, jd
            for _ in range(24):
                mid = (lo + hi) / 2
                lm, hm = NT.lon_deg(lo), NT.lon_deg(mid)
                if (lm <= degree < hm) or (lm > hm and (lm <= degree or degree < hm)):
                    hi = mid
                else:
                    lo = mid
            # Ngày dương theo giờ Việt Nam (UTC+7) của khoảnh khắc Mặt Trời qua 270°/90°.
            # Đông chí 2026: 21/12 20:45 UT = 22/12 03:45 giờ VN.
            return NT.ict_date(hi)
        prev = cur
    raise ValueError(f"Không tìm thấy mốc {degree}° năm {year}")


def facts(chi: str, lunar_year: int, lunar_month: int, years: tuple[int, int] = (1950, 2010)) -> dict:
    if chi not in K.CHI:
        raise ValueError(f"chi không hợp lệ: {chi}")
    if not 1 <= lunar_month <= 12:
        raise ValueError("lunar_month phải từ 1 đến 12")
    lo, hi = years
    if lo > hi:
        raise ValueError("years phải là (năm đầu, năm cuối)")
    start_tuple = A.lunar2solar(1, lunar_month, lunar_year, 0)
    start = dt.date(*reversed(start_tuple))
    month_entry = next((r for r in A.month_lengths(lunar_year) if r[0] == lunar_month and not r[1]), None)
    if month_entry is None:
        raise ValueError(f"không tìm thấy tháng âm {lunar_month}/{lunar_year}")
    days = [NT.fact(start + dt.timedelta(days=i)) for i in range(month_entry[3])]
    end = days[-1]["date"]
    month_chi = days[0]["tiet_thang"]
    year_chi = K.CHI[(lunar_year - 4) % 12]
    compatible = set(K.tam_hop_of(chi)) | {K.luc_hop_of(chi)}
    rows = []
    for f in days:
        relation = BT.chi_rel(chi, f["chi"])
        rows.append({"duong": f["duong"], "am": f["am"], "ngay": f["ngay"], "chi": f["chi"],
                     "than": f["than"], "xung": f["xung"] == chi, "hoang": f["hoang"],
                     "dan": list(f["dan"]), "hop": ("tam hợp" if f["chi"] in K.tam_hop_of(chi) else "lục hợp")
                     if f["chi"] in compatible and f["chi"] != chi else None,
                     "quan_he": relation})
    xung_days = [r for r in rows if r["xung"]]
    good_days = [r for r in rows if r["hop"] and r["hoang"]]
    best_days = [r for r in good_days if not r["dan"]]

    candidates: dict[str, dt.date] = {}
    for f in days:
        if f["ld"] in (1, 15):
            candidates["mùng 1 âm" if f["ld"] == 1 else "rằm âm"] = f["date"]
    for y in range(start.year, end.year + 1):
        for name, deg in (("Đông chí", 270), ("Hạ chí", 90)):
            d = _solar_term_day(y, deg)
            if start <= d <= end:
                candidates[name] = d
    for name, month, day in (("Noel 24/12", 12, 24), ("Noel 25/12", 12, 25),
                             ("31/12", 12, 31), ("01/01", 1, 1), ("14/02", 2, 14)):
        for y in range(start.year, end.year + 1):
            try:
                d = dt.date(y, month, day)
            except ValueError:
                continue
            if start <= d <= end:
                candidates[name] = d
    anchors = []
    for name in ANCHORS:
        if name not in candidates:
            continue
        f = NT.fact(candidates[name])
        rel = BT.chi_rel(chi, f["chi"])
        anchors.append({"name": name, "duong": f["duong"], "am": f["am"], "ngay": f["ngay"],
                        "chi_ngay": f["chi"], "quan_he": rel,
                        "xung": rel == "lục xung", "hop": rel in ("tam hợp", "lục hợp")})

    birth_years = []
    for birth_year in range(lo, hi + 1):
        can, birth_chi = K.can_chi(birth_year)
        if birth_chi != chi:
            continue
        p = TY.profile(birth_year, start=lunar_year, n_years=2)
        birth_years.append({"nam_sinh": birth_year, "can_chi": f"{can} {birth_chi}",
                            "nap_am": K.nap_am(birth_year), "tuong": p["tuong"],
                            "cac_nam": [TY.year_row(birth_year, y) for y in (lunar_year, lunar_year + 1)],
                            "tam_tai_nam_hien_tai_va_sau": [y for y in (lunar_year, lunar_year + 1)
                                if K.CHI[(y - 4) % 12] in TY.tam_tai_years(chi)]})
    return {"chi": chi, "lunar_year": lunar_year, "lunar_month": lunar_month,
            "chi_thang": month_chi, "khoang_duong": {"start": start.isoformat(), "end": end.isoformat()},
            "quan_he_thang": BT.chi_rel(chi, month_chi), "chi_nam": year_chi,
            "quan_he_nam": BT.chi_rel(chi, year_chi), "days": rows,
            "xung_days": xung_days, "good_days": good_days, "best_days": best_days,
            "anchors": anchors, "birth_years": birth_years}


def visuals(data: dict) -> dict:
    """Bốn khối lookup/list dùng bởi marker_visuals của long_plan_build."""
    return {
        "BẢNG NĂM SINH": {"type": "lookup", "title": f"NĂM SINH TUỔI {data['chi']}",
            "cols": ["NĂM", "CAN CHI", "NẠP ÂM", "TƯỢNG", "SAO/HẠN", "KIM LÂU · HOANG ỐC · TAM TAI"],
            "rows": [{"cells": [str(r["nam_sinh"]), r["can_chi"], r["nap_am"], r["tuong"],
                f"Nam {r['cac_nam'][0]['sao_nam']} · Nữ {r['cac_nam'][0]['sao_nu']}",
                f"{r['cac_nam'][0]['kim_lau'] or 'không'} · {r['cac_nam'][0]['hoang_oc']} · "
                f"{'có' if r['tam_tai_nam_hien_tai_va_sau'] else 'không'}"]} for r in data["birth_years"]]},
        "NGÀY XUNG": {"type": "list", "title": "NGÀY XUNG", "items": [
            {"text": f"{r['duong']} · {r['ngay']}"} for r in data["xung_days"]]},
        "NGÀY TỐT": {"type": "list", "title": "NGÀY TỐT · THAM KHẢO", "items": [
            {"text": f"{r['duong']} · {r['ngay']} · {r['hop']}"} for r in data["best_days"]]},
        "NGÀY NEO": {"type": "list", "title": "NGÀY NEO", "items": [
            {"text": f"{r['duong']} · {r['name']} · {r['quan_he']}"} for r in data["anchors"]]},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chi", choices=K.CHI)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    data = facts(args.chi, args.year, args.month)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"t{args.month}_{args.chi}"
    (args.out_dir / f"{stem}_facts.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.out_dir / f"{stem}_tables.json").write_text(json.dumps(visuals(data), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
