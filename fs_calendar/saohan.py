"""Sao (Cửu Diệu) và hạn (8 vận hạn) theo tuổi âm + giới tính -- dữ liệu đối chiếu 3 nguồn (01/10/2026).

Sao: quy tắc chu kỳ 9 năm, khởi ở 10 tuổi âm -- nam từ La Hầu, nữ từ Kế Đô. Kiểm khớp 91/91 năm
sinh của bảng 2026 tuoiam.com và 71/71 năm của hoatieu.vn (quantrimang.com sai 4 dòng tuổi Sửu, bỏ).
Hạn: bảng tra theo tuổi âm (han_by_age.json), rút từ tuoiam.com, trùng khớp hoatieu.vn.
Gốc Cửu Diệu = Navagraha (thiên văn Ấn Độ): 7 thiên thể thấy bằng mắt + 2 điểm giao nhật/nguyệt thực.
"""
import json
from pathlib import Path

SAO_NAM = ["La Hầu", "Thổ Tú", "Thủy Diệu", "Thái Bạch", "Thái Dương", "Vân Hớn", "Kế Đô", "Thái Âm", "Mộc Đức"]
SAO_NU = ["Kế Đô", "Vân Hớn", "Mộc Đức", "Thái Âm", "Thổ Tú", "La Hầu", "Thái Dương", "Thái Bạch", "Thủy Diệu"]
HAN = json.loads((Path(__file__).with_name("han_by_age.json")).read_text(encoding="utf-8"))
THIEN_THE = {"Thái Dương": "Mặt Trời", "Thái Âm": "Mặt Trăng", "Mộc Đức": "sao Mộc", "Thái Bạch": "sao Kim", "Thủy Diệu": "sao Thủy",
             "Vân Hớn": "sao Hỏa", "Thổ Tú": "sao Thổ", "La Hầu": "điểm giao bắc (Rahu)", "Kế Đô": "điểm giao nam (Ketu)"}
SANSKRIT = {"Thái Dương": "Surya", "Thái Âm": "Chandra", "Mộc Đức": "Brihaspati", "Thái Bạch": "Shukra", "Thủy Diệu": "Budha",
            "Vân Hớn": "Mangala", "Thổ Tú": "Shani", "La Hầu": "Rahu", "Kế Đô": "Ketu"}
NHOM = {"Thái Dương": "cát", "Thái Âm": "cát", "Mộc Đức": "cát", "La Hầu": "hung", "Kế Đô": "hung", "Thái Bạch": "hung",
        "Thổ Tú": "trung", "Thủy Diệu": "trung", "Vân Hớn": "trung"}


def tuoi(year: int, at: int = 2027) -> int:
    return at - year + 1


def sao(year: int, nam: bool, at: int = 2027) -> str:
    a = tuoi(year, at)
    return (SAO_NAM if nam else SAO_NU)[(a - 10) % 9]


def han(year: int, nam: bool, at: int = 2027) -> str:
    return HAN[str(tuoi(year, at))]["nam_han" if nam else "nu_han"]


def years_of_sao(name: str, nam: bool, lo: int = 1955, hi: int = 2014, at: int = 2027) -> list[int]:
    return [y for y in range(lo, hi + 1) if sao(y, nam, at) == name]


if __name__ == "__main__":
    # mốc kiểm từ bảng 2026 (tuoiam/hoatieu): 1972 nam La Hầu–Tam Kheo, nữ Kế Đô–Thiên Tinh; 1984 nam Kế Đô–Địa Võng
    assert (sao(1972, True, 2026), han(1972, True, 2026), sao(1972, False, 2026), han(1972, False, 2026)) == ("La Hầu", "Tam Kheo", "Kế Đô", "Thiên Tinh")
    assert (sao(1984, True, 2026), han(1984, True, 2026)) == ("Kế Đô", "Địa Võng")
    assert (sao(2009, True, 2026), han(2009, False, 2026)) == ("Mộc Đức", "Toán Tận")
    for s in SAO_NAM:
        print(f"{s:10s} {NHOM[s]:5s} nam {years_of_sao(s, True)}  nữ {years_of_sao(s, False)}")
