"""Bảng tra `lookup` (12/11): không có `find` thì không dựng ô lật số (trống số đứng yên 1 2 3 4 vô nghĩa)
và bảng giãn hết bề ngang; dòng đầu hiện sớm để khỏi có nền trống > 0,3 s (cổng O9)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "hyperframes_short/compositions/longform.js").read_text(encoding="utf-8")
CSS = (ROOT / "hyperframes_short/compositions/longform.css").read_text(encoding="utf-8")
LK = JS[JS.index("visuals.lookup = {"): JS.index("visuals.annot = {")]


def test_khong_find_thi_khong_dung_o_lat_so():
    i = LK.index("if ((v.find || []).length) {")
    assert i < LK.index('el("div", "lk-flap")')
    else_part = LK[LK.index("} else {", i): LK.index("let chip = null;")]
    assert 'st.classList.add("lk-nofl")' in else_part
    assert LK.count('el("div", "lk-chip")') == 1  # thẻ DỪNG VIDEO dựng chung cho cả hai nhánh


def test_enter_chiu_duoc_khi_khong_co_o_lat_so():
    assert 'S.st.querySelector(".lk-flap")' in LK
    assert re.search(r"if \(flapEl\) tl\.fromTo\(flapEl", LK)


def test_bang_gian_het_be_ngang_khi_khong_co_o_lat_so():
    assert re.search(r"\.lf-lk\.lk-nofl \.lk-tab \{ width: 1600px; \}", CSS)


def test_dong_dau_hien_som():
    m = re.search(r"t0 \+ (\.\d+) \+ k \* rstep", LK)
    assert m and float(m.group(1)) <= 0.1
    assert re.search(r"tl\.fromTo\(S\.box, \{ opacity: \.4", LK)


def test_co_find_thi_van_dung_o_lat_so_nhu_cu():
    tail = LK[LK.index('el("div", "lk-flap")'):]
    assert "lk-digits" in tail and "lk-drum" in tail and "(v.find || []).forEach" in LK


def test_buoc_dong_tong_khong_qua_1_2s():
    assert "Math.min(.18, 1.2 / Math.max(1, S.R.length))" in LK


def test_the_dung_video_khong_bi_bang_rong_de():
    assert re.search(r"\.lf-lk\.lk-nofl \.lk-chip \{ left: auto; right: 160px; top: 70px; \}", CSS)
