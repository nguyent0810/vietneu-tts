"""Chống trùng chủ đề (chuyển thể từ Youtube_Creator_V2): bắt trùng thật, không bắt khuôn khác năm."""
import hf_novelty as N


def test_catches_real_duplicates():
    assert N.similar("Vì sao tượng Phật có dái tai dài?", "Vì sao tượng Phật có đôi tai dài?")
    assert N.similar("Bếp đối diện bồn rửa có sao không?", "Vì sao phong thủy kỵ bếp đối diện bồn rửa?")


def test_same_template_different_year_is_not_duplicate():
    assert not N.similar("Sinh năm 1990 Canh Ngọ hợp màu gì?", "Sinh năm 1995 Ất Hợi: mệnh gì, hợp màu gì?")


def test_unrelated_titles():
    assert not N.similar("Vì sao đi quanh tháp phải theo chiều kim đồng hồ?", "Bảo tháp trong chùa để làm gì?")
