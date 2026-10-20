"""Cung phi Bát trạch + quan hệ tuổi dùng chung cho video FS (F4, F5, F6...) -- tính bằng công thức, không gõ tay.

Cung phi (Lạc thư): sinh 1900-1999: nam = 10 - tổng, nữ = 5 + tổng; từ 2000: nam = 9 - tổng, nữ = 6 + tổng; 0 -> Ly; 5 -> nam Khôn, nữ Cấn.
Bảng du niên đối chiếu wiki.batdongsan + vatphamphongthuy, kiểm đối xứng (xem F4).
"""
try:
    from . import canchi as K
except ImportError:
    import canchi as K

GUA = {1: "Khảm", 2: "Khôn", 3: "Chấn", 4: "Tốn", 6: "Càn", 7: "Đoài", 8: "Cấn", 9: "Ly"}
DONG = ["Khảm", "Ly", "Chấn", "Tốn"]
TAY = ["Càn", "Khôn", "Cấn", "Đoài"]
STAR_ORDER = ["Sinh Khí", "Thiên Y", "Diên Niên", "Phục Vị", "Tuyệt Mệnh", "Ngũ Quỷ", "Lục Sát", "Họa Hại"]
GOOD = STAR_ORDER[:4]
_ST = {
    "Khảm": ["Đông Nam", "Đông", "Nam", "Bắc", "Tây Nam", "Đông Bắc", "Tây Bắc", "Tây"],
    "Ly": ["Đông", "Đông Nam", "Bắc", "Nam", "Tây Bắc", "Tây", "Tây Nam", "Đông Bắc"],
    "Chấn": ["Nam", "Bắc", "Đông Nam", "Đông", "Tây", "Tây Bắc", "Đông Bắc", "Tây Nam"],
    "Tốn": ["Bắc", "Nam", "Đông", "Đông Nam", "Đông Bắc", "Tây Nam", "Tây", "Tây Bắc"],
    "Càn": ["Tây", "Đông Bắc", "Tây Nam", "Tây Bắc", "Nam", "Đông", "Bắc", "Đông Nam"],
    "Khôn": ["Đông Bắc", "Tây", "Tây Bắc", "Tây Nam", "Bắc", "Đông Nam", "Nam", "Đông"],
    "Cấn": ["Tây Nam", "Tây Bắc", "Tây", "Đông Bắc", "Đông Nam", "Bắc", "Đông", "Nam"],
    "Đoài": ["Tây Bắc", "Tây Nam", "Đông Bắc", "Tây", "Đông", "Nam", "Đông Nam", "Bắc"],
}
STARS = {c: dict(zip(STAR_ORDER, d)) for c, d in _ST.items()}
HOME = {"Khảm": "Bắc", "Ly": "Nam", "Chấn": "Đông", "Tốn": "Đông Nam", "Càn": "Tây Bắc", "Khôn": "Tây Nam", "Cấn": "Đông Bắc", "Đoài": "Tây"}
GUA_OF_DIR = {v: k for k, v in HOME.items()}
for _a in STARS:
    assert STARS[_a]["Phục Vị"] == HOME[_a]
    for _s, _d in STARS[_a].items():
        assert STARS[GUA_OF_DIR[_d]][_s] == HOME[_a]


def digits(y):
    n = y % 100
    while n > 9:
        n = n // 10 + n % 10
    return n


def cung(y, nam=True):
    a = digits(y)
    n = (10 - a if nam else 5 + a) if y < 2000 else (9 - a if nam else 6 + a)
    while n > 9:
        n = n // 10 + n % 10
    if n == 0:
        n = 9
    if n == 5:
        return "Khôn" if nam else "Cấn"
    return GUA[n]


def grp(c):
    return "Đông tứ" if c in DONG else "Tây tứ"


def pair_star(a, b):
    return {d: s_ for s_, d in STARS[a].items()}[HOME[b]]


def _same(pairs, a, b):
    return tuple(sorted((a, b))) in {tuple(sorted(p)) for p in pairs}


def chi_rel(a, b):
    if a != b and any(a in g and b in g for g in K.TAM_HOP):
        return "tam hợp"
    if _same(K.LUC_HOP, a, b):
        return "lục hợp"
    if _same(K.LUC_XUNG, a, b):
        return "lục xung"
    if _same(K.LUC_HAI, a, b):
        return "lục hại"
    if a != b and any(a in g and b in g for g in K.TAM_HINH):
        return "tam hình"
    if _same(K.LUC_PHA, a, b):
        return "lục phá"
    return "bình thường"


def chi(y):
    return K.can_chi(y)[1]


def cc(y):
    return " ".join(K.can_chi(y))


assert cung(1978) == "Tốn" and cung(1978, False) == "Khôn" and cung(2000) == "Ly" and cung(2000, False) == "Càn"
assert cung(2027) == "Ly" and cung(2027, False) == "Càn"
assert chi_rel("Mùi", "Sửu") == "lục xung" and chi_rel("Mùi", "Tuất") == "tam hình" and chi_rel("Mùi", "Mão") == "tam hợp"
