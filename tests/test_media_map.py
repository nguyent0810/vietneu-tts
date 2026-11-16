"""tools/long/media_map — mỗi ca thử là một lần render Long bị cổng chặn ở pilot 15/11/2026."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "long"))

import media_map as M  # noqa: E402

P = lambda n: f"output/cl_staging/grokbot/x/out/{n}.png"  # noqa: E731
IMGS = [f"img{i}" for i in range(10)]


def _script(n=80, heads=(30, 60)):
    return [("**Chương %d**" % i) if i in heads else f"Câu số {i} kể chuyện." for i in range(1, n + 1)]


def test_dong_1_co_may_quay_object():
    m = M.assign(_script(), open_img="img0", path_of=P, kw_img=[("kể", "img1")])
    assert isinstance(m["1"]["cine"], dict) and m["1"]["cine"]["cam"] in M.CAMS


def test_khong_trung_anh_va_khung_cat_trong_chuong():
    s = _script(120, heads=(100,))
    m = M.assign(s, open_img="img0", path_of=P, kw_img=[("kể", "img1")], pick={})
    assert M.duplicates(s, m) == []


def test_40_giay_dau_du_8_hinh_khac_nhau():
    s = _script()
    starts = M.line_starts(s)
    m = M.assign(s, open_img="img0", path_of=P, starts=starts, kw_img=[(f"số {i}\\b", f"img{i % 10}") for i in range(1, 80)] + [("kể", "img1")])
    early = {m[str(i)]["path"] for i in range(1, len(s) + 1) if str(i) in m and starts[i - 1] < M.EARLY_S}
    assert len(early) >= M.EARLY_MIN_DISTINCT


def test_cau_trong_so_do_khong_anh_cau_sau_so_do_co_anh():
    s = _script(120)
    vis = {"70": {"type": "compare", "until": 72}, "75": {"type": "wheel", "until": 75}}
    m = M.assign(s, open_img="img0", path_of=P, visuals=vis, kw_img=[("kể", "img1")])
    assert not {"70", "71", "72", "75"} & set(m)
    assert "73" in m and "76" in m


def test_bang_chon_theo_nghia_uu_tien_hon_tu_khoa():
    s = _script(10, heads=())
    m = M.assign(s, open_img="img0", path_of=P, pick={"4": "img7"}, kw_img=[("kể", "img1")])
    assert m["4"]["path"].endswith("img7.png")


def test_120_giay_dau_bo_the_chu_nen_trong_va_rut_the_khac():
    s = _script()
    starts = M.line_starts(s)
    v = M.clean_visuals({"5": {"type": "quote"}, "8": {"type": "compare", "until": 14}, "79": {"type": "quote"}}, starts)
    assert "5" not in v and v["8"]["until"] == 8 and "79" in v


def test_anh_dung_khung_full_tranh_khung_nho_in_chu_cut():
    m = M.assign(_script(), open_img="img0", path_of=P, kw_img=[("kể", "img1")])
    assert all(x.get("layout") == "full" for k, x in m.items() if k != "1")


def test_dong_phong_dung_co_nhan_va_luon_co_anh_rieng():
    s = _script(120, heads=())
    m = M.assign(s, open_img="img0", path_of=P, kw_img=[("kể", "img1")], pd={101, 102})
    assert m["101"]["label"] == "PHỎNG DỰNG" and m["102"]["label"] == "PHỎNG DỰNG"
    assert m["101"]["credit"].strip() == "" and not any(v.get("label") for k, v in m.items() if int(k) not in {101, 102})
