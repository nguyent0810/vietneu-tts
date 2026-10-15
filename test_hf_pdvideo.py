"""hf_pdvideo: tham chiếu, cửa giấy phép, đoạn cắt, dòng ghi công + nhánh media "pdvideo" của bridge. Không gọi mạng."""
import ast
import shutil
import sys
import types
from pathlib import Path

import pytest

import hf_pdvideo as P

ROOT = Path(__file__).resolve().parent


def test_parse_ref_ba_nguon():
    assert P.parse_ref("commons:File:On_board_of_the_Tonkin.webm") == ("commons", "File:On board of the Tonkin.webm", None)
    assert P.parse_ref("commons:Scènes de rue - AI12911.webm") == ("commons", "File:Scènes de rue - AI12911.webm", None)
    assert P.parse_ref("ia:Tin-Minh-1918") == ("ia", "Tin-Minh-1918", None)
    assert P.parse_ref("ia:Tin-Minh-1918/01 Prologue 1918.mp4") == ("ia", "Tin-Minh-1918", "01 Prologue 1918.mp4")
    assert P.parse_ref("nasa:MAF_20230801_SupermoonTL") == ("nasa", "MAF_20230801_SupermoonTL", None)
    assert P.parse_ref("nasa:Artemis II at the pad Full Snow Moon 02012026")[0] == "nasa"


@pytest.mark.parametrize("bad", ["", "File:X.webm", "youtube:abc", "commons:File:Anh.jpg", "ia:bad id!", "commons:"])
def test_parse_ref_sai_dang_bi_chan(bad):
    with pytest.raises(ValueError):
        P.parse_ref(bad)


@pytest.mark.parametrize("url,label", [
    ("http://creativecommons.org/publicdomain/zero/1.0/", "CC0 1.0"),
    ("https://creativecommons.org/publicdomain/mark/1.0/", "Public Domain Mark 1.0"),
    ("http://creativecommons.org/licenses/by/3.0/", "CC BY 3.0"),
    ("https://creativecommons.org/licenses/by-sa/4.0/", "CC BY-SA 4.0"),
    ("http://creativecommons.org/licenses/by-nc/3.0/", ""),
    ("http://creativecommons.org/licenses/by-nd/4.0/", ""),
    ("http://creativecommons.org/licenses/by-nc-sa/2.0/", ""),
    ("", ""),
    ("https://example.org/terms", ""),
])
def test_licenseurl_ia_chi_nhan_pd_cc0_by_bysa(url, label):
    assert P.license_from_url(url) == label
    if label:
        assert P.ok_license(label)


def test_ok_license_dung_chung_cua_anh():
    for good in ("Public domain", "CC0", "CC BY-SA 4.0", "CC BY 3.0", "Public Domain Mark 1.0"):
        assert P.ok_license(good), good
    for bad in ("", "CC BY-NC 2.0", "CC BY-ND 4.0", "Fair use", "All rights reserved"):
        assert not P.ok_license(bad), bad


def test_ia_khong_tin_giay_phep_nguoi_tai_tu_khai():
    # "A Better Tomorrow" 1986 gắn CC BY 4.0 bởi người tải lên -> loại
    lic, why = P.ia_verdict({"identifier": "a-better-tomorrow", "licenseurl": "http://creativecommons.org/licenses/by/4.0/",
                             "collection": ["opensource_movies"], "year": "2026"})
    assert lic == "" and "tự khai" in why
    # PDM nhưng phim 1993 -> loại
    assert P.ia_verdict({"identifier": "x", "licenseurl": "http://creativecommons.org/publicdomain/mark/1.0/",
                         "collection": ["community"], "date": "1993"})[0] == ""
    # PDM + phát hành 1918 -> nhận (hết bảo hộ ở Mỹ)
    lic, why = P.ia_verdict({"identifier": "Tin-Minh-1918", "licenseurl": "https://creativecommons.org/publicdomain/mark/1.0/",
                             "collection": ["silent_films"], "date": "1918-12-30"})
    assert lic == "Public Domain Mark 1.0" and "1918" in why
    # Prelinger không licenseurl -> nhận; FedFlix/NARA -> nhận; NC -> loại kể cả trong bộ tin cậy
    assert P.ia_verdict({"identifier": "In_Siamese_Society", "collection": ["prelinger"]})[0].startswith("Public domain")
    assert P.ia_verdict({"identifier": "gov.archives.arc.12867", "collection": ["FedFlix", "usgovfilms"],
                         "licenseurl": "http://creativecommons.org/publicdomain/zero/1.0/"})[0] == "CC0 1.0"
    assert P.ia_verdict({"identifier": "p", "collection": ["prelinger"],
                         "licenseurl": "http://creativecommons.org/licenses/by-nc/3.0/"})[0] == ""
    assert P.ia_verdict({"identifier": "p", "collection": ["prelinger"], "rights": "All rights reserved"})[0] == ""


def test_doan_cat_toi_da_20_giay_va_khong_qua_cuoi_phim():
    assert P.clip_window(12, 15) == (12.0, 15.0)
    assert P.clip_window(-3, 60) == (0.0, P.MAX_DUR)
    assert P.clip_window(50, 15, total=55.2) == (50.0, 5.2)
    with pytest.raises(ValueError):
        P.clip_window(0, 0)
    with pytest.raises(ValueError):
        P.clip_window(60, 10, total=55)


def test_ghi_cong_va_ten_cache():
    m = {"src": "ia", "title": "Chang: A Drama of the Wilderness", "author": "Merian C. Cooper", "license": "Public Domain Mark 1.0"}
    assert P.credit_line(m) == "Chang: A Drama of the Wilderness — Merian C. Cooper, Public Domain Mark 1.0, Internet Archive"
    assert P.credit_line({"src": "nasa", "title": "Full Moon", "license": "Public domain (NASA)"}) == \
        "Full Moon — Public domain (NASA), NASA"
    mp4, js = P.cache_paths("commons:File:Scènes de rue - AI12911.webm", 12.0, 15.0, "cover")
    assert mp4.parent == P.CACHE and mp4.suffix == ".mp4" and js.suffix == ".json"
    assert "/" not in mp4.name and mp4.name.endswith("_12_15_cover.mp4")


def test_vf_dung_khung_1920x1080():
    for fit in P.FITS:
        vf = P.vf_for(fit)
        assert "1920" in vf and "1080" in vf and vf.endswith("format=yuv420p")
    with pytest.raises(ValueError, match="fit lạ"):
        P.fetch("commons:File:X.webm", fit="stretch")


# ---------------- bridge ----------------
def _bridge(tmp_path, fake_fetch):
    tree = ast.parse((ROOT / "hyperframes_bridge.py").read_text(encoding="utf-8"))
    names = {"resolve_media", "_short_credit", "HyperFramesError", "FORBIDDEN_TREATMENT"}
    keep = [n for n in tree.body
            if (isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names)
            or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") in names for t in n.targets))]
    ns: dict = {"__name__": "bridge", "Path": Path, "shutil": shutil, "HF_ASSETS": tmp_path / "assets"}
    exec(compile(ast.Module(body=keep, type_ignores=[]), "bridge", "exec"), ns)
    return ns


@pytest.fixture
def fake_pdvideo(tmp_path, monkeypatch):
    calls = []
    clip = tmp_path / "cache.mp4"
    clip.write_bytes(b"\x00" * 64)

    def fetch(ref, start=0, dur=15, fit="cover"):
        calls.append((ref, start, dur, fit))
        if "bad" in ref:
            raise ValueError(f"{ref}: giấy phép 'CC BY-NC 2.0' không dùng được")
        return clip, "Scènes de rue — Busy Léon, CC0, Wikimedia Commons"

    monkeypatch.setitem(sys.modules, "hf_pdvideo", types.SimpleNamespace(fetch=fetch))
    return calls


def test_bridge_pdvideo_tra_mp4_ref_ghi_cong(tmp_path, fake_pdvideo):
    ns = _bridge(tmp_path, None)
    spec = {"kind": "pdvideo", "ref": "commons:File:Scènes de rue - AI12911.webm", "start": 12, "dur": 15,
            "fit": "blur", "label": "TƯ LIỆU 1921"}
    local, q, credit, grade = ns["resolve_media"](spec, 7, "L_bud_1", "BUD", "landscape")
    assert local.name == "L_bud_1_s7.mp4" and local.is_file()
    assert q == spec["ref"] and credit.startswith("Scènes de rue") and grade == ""
    assert fake_pdvideo == [(spec["ref"], 12, 15, "blur")]
    assert ns["_short_credit"](credit, "pdvideo") == "Busy Léon, CC0 · Wikimedia Commons"


def test_bridge_pdvideo_giay_phep_hong_thanh_loi_cau(tmp_path, fake_pdvideo):
    ns = _bridge(tmp_path, None)
    with pytest.raises(ns["HyperFramesError"], match="câu 3"):
        ns["resolve_media"]({"kind": "pdvideo", "ref": "ia:bad"}, 3, "x", "BUD")
