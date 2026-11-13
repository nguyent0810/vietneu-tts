"""Tên tượng 60 hoa giáp (canchi.TUONG) và chỗ nó đi vào profile năm sinh (tuvi_year.profile)."""
from fs_calendar import canchi as K
from fs_calendar import tuvi_year as TY

CON = {"Tý": ("Thử",), "Sửu": ("Ngưu",), "Dần": ("Hổ",), "Mão": ("Thố",), "Thìn": ("Long",), "Tỵ": ("Xà",),
       "Ngọ": ("Mã",), "Mùi": ("Dương",), "Thân": ("Hầu",), "Dậu": ("Kê",), "Tuất": ("Cẩu", "Khuyển"), "Hợi": ("Trư",)}


def test_du_60_ten_khong_trung_can_chi():
    assert len(K.TUONG) == 60
    assert len({ten for ten, _ in K.TUONG}) == 60
    for i, (ten, nghia) in enumerate(K.TUONG):
        chi = K.CHI[i % 12]
        assert ten.split()[-1] in CON[chi], (i, ten, chi)
        assert " Chi " in ten and nghia


def test_moc_da_doi_chieu():
    assert K.tuong(1983) == ("Lâm Hạ Chi Trư", "lợn trong rừng")
    assert K.tuong(1988)[0] == "Thanh Ôn Chi Long"
    assert K.tuong(1984)[0] == "Ốc Thượng Chi Thử"
    assert K.tuong(2027)[0] == "Thất Quần Chi Dương"
    assert K.tuong(1964)[0] == "Phục Đầm Chi Long"
    assert K.tuong(1923) == K.tuong(1983)  # chu kỳ 60


def test_profile_co_tuong():
    p = TY.profile(1983)
    assert p["tuong"] == "Lâm Hạ Chi Trư" and p["tuong_nghia"] == "lợn trong rừng"
