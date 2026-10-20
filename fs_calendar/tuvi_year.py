"""Hồ sơ "tử vi trọn đời" của MỘT năm sinh -- toàn bộ số liệu tính bằng code từ các bảng đã đối chiếu
(canchi.py, saohan.py, batrach.py, luật Kim Lâu / Hoang Ốc / Tam Tai của build_F3.py). Dùng cho series FS
"Tử vi trọn đời theo năm sinh" (15/10/2026): mỗi tập một năm sinh, kịch bản đọc số từ đây, không gõ tay.

    python tuvi_year.py 1983            # in hồ sơ
    python tuvi_year.py 1983 --json     # JSON cho build_FTxx.py
"""
from __future__ import annotations

import json
import sys

try:
    from . import batrach as BT
    from . import canchi as K
    from . import saohan as SH
except ImportError:
    import batrach as BT
    import canchi as K
    import saohan as SH

TAM_TAI = {("Thân", "Tý", "Thìn"): ("Dần", "Mão", "Thìn"), ("Tỵ", "Dậu", "Sửu"): ("Hợi", "Tý", "Sửu"),
           ("Dần", "Ngọ", "Tuất"): ("Thân", "Dậu", "Tuất"), ("Hợi", "Mão", "Mùi"): ("Tỵ", "Ngọ", "Mùi")}
KIM_LAU = {1: "Kim Lâu Thân", 3: "Kim Lâu Thê", 6: "Kim Lâu Tử", 8: "Kim Lâu Lục Súc"}
HOANG_OC = ["Nhất Cát", "Nhì Nghi", "Tam Địa Sát", "Tứ Tấn Tài", "Ngũ Thọ Tử", "Lục Hoang Ốc"]
HO_XAU = {"Tam Địa Sát", "Ngũ Thọ Tử", "Lục Hoang Ốc"}
# Hành sinh/khắc (để nói "mệnh năm nay với mệnh mình")
SINH, KHAC = K.SINH, K.KHAC


def chi_of(y: int) -> str:
    return K.can_chi(y)[1]


def tuoi(y: int, at: int) -> int:
    return at - y + 1


def hoang_oc(a: int) -> str:
    return HOANG_OC[(a // 10 - 1 + a % 10) % 6]


def tam_tai_years(chi: str) -> tuple[str, ...]:
    return TAM_TAI[next(g for g in TAM_TAI if chi in g)]


def hanh_rel(me: str, other: str) -> str:
    """Quan hệ ngũ hành: mệnh mình (me) với mệnh khác (other)."""
    if me == other:
        return "bình hòa"
    if SINH[other] == me:
        return "được sinh"      # other sinh cho mình
    if SINH[me] == other:
        return "sinh ra"        # mình sinh cho other (hao)
    if KHAC[other] == me:
        return "bị khắc"
    return "khắc ra"


def year_row(y: int, at: int) -> dict:
    a = tuoi(y, at)
    ychi = K.CHI[(at - 4) % 12]
    chi = chi_of(y)
    na_year = K.nap_am(at)
    return {"nam": at, "can_chi": " ".join(K.can_chi(at)), "tuoi": a,
            "sao_nam": SH.sao(y, True, at), "sao_nu": SH.sao(y, False, at),
            "han_nam": SH.han(y, True, at), "han_nu": SH.han(y, False, at),
            "kim_lau": KIM_LAU.get(a % 9), "hoang_oc": hoang_oc(a), "hoang_oc_xau": hoang_oc(a) in HO_XAU,
            "tam_tai": ychi in tam_tai_years(chi), "quan_he_chi": BT.chi_rel(chi, ychi) if chi != ychi else "năm tuổi",
            "nap_am_nam": na_year, "hanh_rel": hanh_rel(K.hanh(K.nap_am(y)), K.hanh(na_year))}


def profile(y: int, start: int = 2027, n_years: int = 12) -> dict:
    can, chi = K.can_chi(y)
    na = K.nap_am(y)
    h = K.hanh(na)
    cn, cf = BT.cung(y, True), BT.cung(y, False)
    dirs = {k: dict(BT.STARS[c]) for k, c in (("nam", cn), ("nu", cf))}
    rel = {}
    for k in K.CHI:
        if k != chi:
            r = BT.chi_rel(chi, k)
            if r != "bình thường":
                rel.setdefault(r, []).append(k)
    near = [x for x in range(y - 12, y + 13) if x != y]
    partners = [{"nam": x, "can_chi": " ".join(K.can_chi(x)), "nap_am": K.nap_am(x), "quan_he_chi": BT.chi_rel(chi, chi_of(x)),
                 "hanh_rel": hanh_rel(h, K.hanh(K.nap_am(x)))} for x in near]
    milestones = {a: y + a - 1 for a in (49, 53, 61, 70)}
    return {"nam_sinh": y, "can": can, "chi": chi, "can_chi": f"{can} {chi}", "nap_am": na, "nghia": K.NGHIA[na], "hanh": h,
            "hanh_chi": K.HANH_CHI[chi], "cung_nam": cn, "cung_nu": cf, "nhom_nam": BT.grp(cn), "nhom_nu": BT.grp(cf),
            "huong": dirs, "tam_hop": list(K.tam_hop_of(chi)), "luc_hop": K.luc_hop_of(chi), "quan_he": rel,
            "tam_tai_nam": [k for k in tam_tai_years(chi)], "ban_doi": partners,
            "cac_nam": [year_row(y, s) for s in range(start, start + n_years)],
            "moc_tuoi": {str(a): yy for a, yy in milestones.items()}}


if __name__ == "__main__":
    yy = int(sys.argv[1])
    p = profile(yy)
    if "--json" in sys.argv:
        print(json.dumps(p, ensure_ascii=False, indent=1))
        sys.exit()
    print(f"{p['nam_sinh']} {p['can_chi']} · {p['nap_am']} ({p['nghia']}) · hành {p['hanh']}")
    print(f"cung nam {p['cung_nam']} ({p['nhom_nam']}) · cung nữ {p['cung_nu']} ({p['nhom_nu']})")
    for g in ("nam", "nu"):
        print(" ", g, {k: v for k, v in p["huong"][g].items()})
    print("tam hợp", p["tam_hop"], "lục hợp", p["luc_hop"], "quan hệ", p["quan_he"], "tam tai năm", p["tam_tai_nam"])
    for r in p["cac_nam"]:
        print(f"  {r['nam']} {r['can_chi']:9s} {r['tuoi']:>2} tuổi | nam {r['sao_nam']:10s} {r['han_nam']:12s} | nữ {r['sao_nu']:10s} {r['han_nu']:12s} | "
              f"{r['kim_lau'] or '-':16s} | {r['hoang_oc']:13s} | {'TAM TAI' if r['tam_tai'] else '-':7s} | {r['quan_he_chi']} | mệnh {r['hanh_rel']}")
    print("mốc", p["moc_tuoi"])
