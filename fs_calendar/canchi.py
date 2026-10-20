"""Can chi, nạp âm, quan hệ với Thái Tuế -- tính bằng bảng chuẩn, KHÔNG gõ tay từng năm.

Bảng nạp âm lục thập hoa giáp (30 cặp, mỗi cặp hai năm liền nhau). Kiểm chứng:
1984 Giáp Tý = Hải Trung Kim, 2026 Bính Ngọ / 2027 Đinh Mùi = Thiên Hà Thủy.
"""
CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
NAP_AM = ["Hải Trung Kim", "Lư Trung Hỏa", "Đại Lâm Mộc", "Lộ Bàng Thổ", "Kiếm Phong Kim", "Sơn Đầu Hỏa",
          "Giản Hạ Thủy", "Thành Đầu Thổ", "Bạch Lạp Kim", "Dương Liễu Mộc", "Tuyền Trung Thủy", "Ốc Thượng Thổ",
          "Tích Lịch Hỏa", "Tùng Bách Mộc", "Trường Lưu Thủy", "Sa Trung Kim", "Sơn Hạ Hỏa", "Bình Địa Mộc",
          "Bích Thượng Thổ", "Kim Bạch Kim", "Phú Đăng Hỏa", "Thiên Hà Thủy", "Đại Trạch Thổ", "Thoa Xuyến Kim",
          "Tang Đố Mộc", "Đại Khê Thủy", "Sa Trung Thổ", "Thiên Thượng Hỏa", "Thạch Lựu Mộc", "Đại Hải Thủy"]
NGHIA = {"Hải Trung Kim": "vàng trong biển", "Lư Trung Hỏa": "lửa trong lò", "Đại Lâm Mộc": "gỗ rừng lớn",
         "Lộ Bàng Thổ": "đất ven đường", "Kiếm Phong Kim": "vàng mũi kiếm", "Sơn Đầu Hỏa": "lửa trên núi",
         "Giản Hạ Thủy": "nước dưới khe", "Thành Đầu Thổ": "đất trên thành", "Bạch Lạp Kim": "vàng chân đèn",
         "Dương Liễu Mộc": "gỗ cây dương liễu", "Tuyền Trung Thủy": "nước trong suối", "Ốc Thượng Thổ": "đất trên mái nhà",
         "Tích Lịch Hỏa": "lửa sấm sét", "Tùng Bách Mộc": "gỗ tùng bách", "Trường Lưu Thủy": "nước chảy dài",
         "Sa Trung Kim": "vàng trong cát", "Sơn Hạ Hỏa": "lửa dưới núi", "Bình Địa Mộc": "gỗ đồng bằng",
         "Bích Thượng Thổ": "đất trên vách", "Kim Bạch Kim": "vàng pha bạc", "Phú Đăng Hỏa": "lửa ngọn đèn",
         "Thiên Hà Thủy": "nước trên sông trời", "Đại Trạch Thổ": "đất đầm lớn", "Thoa Xuyến Kim": "vàng trang sức",
         "Tang Đố Mộc": "gỗ cây dâu", "Đại Khê Thủy": "nước khe lớn", "Sa Trung Thổ": "đất trong cát",
         "Thiên Thượng Hỏa": "lửa trên trời", "Thạch Lựu Mộc": "gỗ cây thạch lựu", "Đại Hải Thủy": "nước biển lớn"}
HANH_CHI = {"Tý": "Thủy", "Sửu": "Thổ", "Dần": "Mộc", "Mão": "Mộc", "Thìn": "Thổ", "Tỵ": "Hỏa",
            "Ngọ": "Hỏa", "Mùi": "Thổ", "Thân": "Kim", "Dậu": "Kim", "Tuất": "Thổ", "Hợi": "Thủy"}
TAM_HOP = [("Thân", "Tý", "Thìn"), ("Tỵ", "Dậu", "Sửu"), ("Dần", "Ngọ", "Tuất"), ("Hợi", "Mão", "Mùi")]
LUC_HOP = [("Tý", "Sửu"), ("Dần", "Hợi"), ("Mão", "Tuất"), ("Thìn", "Dậu"), ("Tỵ", "Thân"), ("Ngọ", "Mùi")]
LUC_XUNG = [("Tý", "Ngọ"), ("Sửu", "Mùi"), ("Dần", "Thân"), ("Mão", "Dậu"), ("Thìn", "Tuất"), ("Tỵ", "Hợi")]
LUC_HAI = [("Tý", "Mùi"), ("Sửu", "Ngọ"), ("Dần", "Tỵ"), ("Mão", "Thìn"), ("Thân", "Hợi"), ("Dậu", "Tuất")]
LUC_PHA = [("Tý", "Dậu"), ("Mão", "Ngọ"), ("Thân", "Tỵ"), ("Dần", "Hợi"), ("Thìn", "Sửu"), ("Tuất", "Mùi")]
TAM_HINH = [("Dần", "Tỵ", "Thân"), ("Sửu", "Tuất", "Mùi")]
YEAR, YEAR_CHI = 2027, "Mùi"
YEAR_HANH = "Thủy"  # nạp âm Thiên Hà Thủy
SINH = {"Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim", "Kim": "Thủy", "Thủy": "Mộc"}
KHAC = {"Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim", "Kim": "Mộc"}


def can_chi(y: int) -> tuple[str, str]:
    return CAN[(y - 4) % 10], CHI[(y - 4) % 12]


def nap_am(y: int) -> str:
    return NAP_AM[((y - 4) % 60) // 2]


def hanh(na: str) -> str:
    return na.split()[-1]


def rel_with_year(h: str) -> str:
    """Quan hệ mệnh năm sinh (h) với mệnh năm 2027 (Thủy)."""
    if h == YEAR_HANH:
        return "hoa"
    if SINH[YEAR_HANH] == h:
        return "duoc_sinh"      # Thủy sinh Mộc: năm sinh cho mình
    if SINH[h] == YEAR_HANH:
        return "sinh_ra"        # Kim sinh Thủy: mình sinh cho năm
    if KHAC[YEAR_HANH] == h:
        return "bi_khac"        # Thủy khắc Hỏa
    return "khac_ra"            # Thổ khắc Thủy


def years_of(chi: str, lo: int = 1955, hi: int = 2014) -> list[int]:
    return [y for y in range(lo, hi + 1) if can_chi(y)[1] == chi]


def thai_tue(chi: str) -> list[str]:
    out = []
    if chi == YEAR_CHI:
        out.append("truc")
    if tuple(sorted((chi, YEAR_CHI))) in {tuple(sorted(p)) for p in LUC_XUNG}:
        out.append("xung")
    if any(chi in g and YEAR_CHI in g and chi != YEAR_CHI for g in TAM_HINH):
        out.append("hinh")
    if tuple(sorted((chi, YEAR_CHI))) in {tuple(sorted(p)) for p in LUC_HAI}:
        out.append("hai")
    if tuple(sorted((chi, YEAR_CHI))) in {tuple(sorted(p)) for p in LUC_PHA}:
        out.append("pha")
    if any(chi in g and YEAR_CHI in g and chi != YEAR_CHI for g in TAM_HOP):
        out.append("tamhop")
    if tuple(sorted((chi, YEAR_CHI))) in {tuple(sorted(p)) for p in LUC_HOP}:
        out.append("luchop")
    return out


def tam_hop_of(chi):
    return next(g for g in TAM_HOP if chi in g)


def luc_hop_of(chi):
    return next(b if a == chi else a for a, b in LUC_HOP if chi in (a, b))


if __name__ == "__main__":
    assert can_chi(1984) == ("Giáp", "Tý") and nap_am(1984) == "Hải Trung Kim"
    assert can_chi(2027) == ("Đinh", "Mùi") and nap_am(2027) == nap_am(2026) == "Thiên Hà Thủy"
    assert nap_am(1958) == "Bình Địa Mộc" and nap_am(1994) == "Sơn Đầu Hỏa" and nap_am(1972) == "Tang Đố Mộc"
    assert thai_tue("Tuất") == ["hinh", "pha"] and thai_tue("Sửu") == ["xung", "hinh"] and thai_tue("Tý") == ["hai"]
    for c in CHI:
        ys = years_of(c)
        print(f"{c:5s}", thai_tue(c), [(y, "".join(can_chi(y)), nap_am(y), rel_with_year(hanh(nap_am(y)))) for y in ys])

# Ảnh minh hoạ ĐÚNG nghĩa từng mệnh nạp âm (truy vấn ảnh stock tiếng Anh) -- cảnh `napam`.
NAP_QUERY = {
    "Hải Trung Kim": "golden light underwater ocean", "Lư Trung Hỏa": "fire burning in clay stove",
    "Đại Lâm Mộc": "ancient giant forest trees", "Lộ Bàng Thổ": "dirt road countryside", "Kiếm Phong Kim": "steel sword blade close up",
    "Sơn Đầu Hỏa": "wildfire on mountain ridge", "Giản Hạ Thủy": "mountain stream between rocks", "Thành Đầu Thổ": "ancient citadel brick wall",
    "Bạch Lạp Kim": "brass candlestick candle", "Dương Liễu Mộc": "willow tree by lake", "Tuyền Trung Thủy": "spring water flowing from rocks",
    "Ốc Thượng Thổ": "old clay roof tiles", "Tích Lịch Hỏa": "lightning strike night sky", "Tùng Bách Mộc": "pine trees on mountain",
    "Trường Lưu Thủy": "long winding river aerial", "Sa Trung Kim": "gold flakes in river sand", "Sơn Hạ Hỏa": "campfire at foot of mountain",
    "Bình Địa Mộc": "trees on flat green plain", "Bích Thượng Thổ": "old earthen wall texture", "Kim Bạch Kim": "silver and gold metal",
    "Phú Đăng Hỏa": "oil lamp flame dark", "Thiên Hà Thủy": "milky way night sky", "Đại Trạch Thổ": "wetland marsh landscape",
    "Thoa Xuyến Kim": "gold bracelet jewelry", "Tang Đố Mộc": "mulberry tree leaves", "Đại Khê Thủy": "river rapids rocks",
    "Sa Trung Thổ": "sand dunes desert", "Thiên Thượng Hỏa": "sun shining in sky", "Thạch Lựu Mộc": "pomegranate tree fruit",
    "Đại Hải Thủy": "vast ocean waves",
}
assert set(NAP_QUERY) == set(NAP_AM)
