"""Nguồn The Met trong hf_museum: HTTP giả, không gọi mạng."""
import io
import json
import sys
import urllib.error
from pathlib import Path

import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hf_museum  # noqa: E402


class _Resp:
    def __init__(self, body: bytes):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


def _jpeg() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (4, 4), (12, 34, 56)).save(buf, format="JPEG")
    return buf.getvalue()


def _obj(oid, *, pd=True, image=True, title="Standing Buddha", date="ca. 3rd century",
         culture="Pakistan (ancient region of Gandhara)", credit="Bequest of X"):
    return {
        "objectID": oid,
        "isPublicDomain": pd,
        "primaryImage": f"https://images.example/{oid}.jpg" if image else "",
        "primaryImageSmall": f"https://images.example/{oid}-s.jpg" if image else "",
        "title": title,
        "objectDate": date,
        "culture": culture,
        "creditLine": credit,
    }


def _install(monkeypatch, handler):
    seen = []

    def urlopen(req, timeout=60):
        url = req.full_url
        seen.append(url)
        body = handler(url)
        if isinstance(body, Exception):
            raise body
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        return _Resp(body)

    monkeypatch.setattr(hf_museum.urllib.request, "urlopen", urlopen)
    monkeypatch.setattr(hf_museum.time, "sleep", lambda *_a, **_k: None)
    return seen


def test_met_search_dung_v11_va_chi_giu_cc0_co_anh(monkeypatch):
    catalog = {
        10: _obj(10, pd=False, title="Ban quyen"),
        11: _obj(11, image=False, title="Khong anh"),
        12: _obj(12, title="Standing Buddha"),
        13: _obj(13, title="Seated Buddha"),
    }

    def handler(url):
        assert "/public/collection/v1/search" not in url
        if "/v1.1/search" in url:
            assert "hasImages=true" in url
            assert "q=gandhara%20buddha%20relief" in url
            assert "limit=6" in url
            return {"total": 4, "objectIDs": [10, 11, 12, 13]}
        oid = int(url.rstrip("/").rsplit("/", 1)[-1])
        assert url.startswith(hf_museum.MET_OBJECT)
        return catalog[oid]

    seen = _install(monkeypatch, handler)
    out = hf_museum._met_search("gandhara buddha relief", 2)
    assert [c["ref"] for c in out] == ["met:12", "met:13"]
    assert out[0]["date"] == "ca. 3rd century"
    assert out[0]["place"].startswith("Pakistan")
    assert out[0]["img"] == "https://images.example/12.jpg"
    assert out[0]["credit"] == "The Met, Bequest of X (CC0)"
    assert any("/v1.1/search" in u for u in seen)
    assert all("/public/collection/v1/search" not in u for u in seen)


def test_met_search_bo_qua_hien_vat_loi_va_objectids_rong(monkeypatch):
    def handler(url):
        if "/v1.1/search" in url:
            return {"total": 2, "objectIDs": [1, 2]}
        if url.endswith("/1"):
            raise urllib.error.URLError("mat mang")
        return _obj(2, title="Head of Buddha")

    _install(monkeypatch, handler)
    out = hf_museum._met_search("buddha", 8)
    assert [c["ref"] for c in out] == ["met:2"]

    def empty(url):
        assert "/v1.1/search" in url
        return {"total": 0, "objectIDs": None}

    _install(monkeypatch, empty)
    assert hf_museum._met_search("khong co", 8) == []


def test_fetch_met_cc0_roi_dung_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(hf_museum, "CACHE", tmp_path)
    jpeg = _jpeg()

    def handler(url):
        if url.endswith("/38820"):
            return _obj(38820)
        if url == "https://images.example/38820.jpg":
            return jpeg
        raise AssertionError(url)

    seen = _install(monkeypatch, handler)
    path, credit = hf_museum.fetch("met:38820")
    assert path == tmp_path / "met_38820.jpg"
    assert path.stat().st_size > 0
    assert credit == "Standing Buddha — The Met, Bequest of X (CC0)"
    saved = json.loads((tmp_path / "met_38820.json").read_text(encoding="utf-8"))
    assert saved["img"] == "https://images.example/38820.jpg"
    seen.clear()
    path2, credit2 = hf_museum.fetch("met:38820")
    assert path2 == path and credit2 == credit and seen == []


def test_fetch_met_khong_phai_cc0_thi_chan(monkeypatch, tmp_path):
    monkeypatch.setattr(hf_museum, "CACHE", tmp_path)

    def handler(url):
        assert url.endswith("/9")
        return _obj(9, pd=False, title="Still in copyright")

    seen = _install(monkeypatch, handler)
    with pytest.raises(ValueError, match="không phải phạm vi công cộng"):
        hf_museum.fetch("met:9")
    assert seen == [hf_museum.MET_OBJECT + "9"]
    assert list(tmp_path.iterdir()) == []


def test_search_met_hong_khong_lam_mat_aic(monkeypatch, capsys):
    def handler(url):
        if "collectionapi.metmuseum.org" in url:
            raise urllib.error.HTTPError(url, 503, "unavailable", {}, None)
        if "api.artic.edu" in url:
            return {"data": [{
                "id": 16568, "title": "Buddha", "image_id": "abc",
                "is_public_domain": True, "date_display": "100",
                "place_of_origin": "Gandhara", "credit_line": "gift",
            }, {
                "id": 2, "title": "An", "image_id": "",
                "is_public_domain": False, "date_display": "",
                "place_of_origin": "", "credit_line": "",
            }]}
        raise AssertionError(url)

    _install(monkeypatch, handler)
    out = hf_museum.search("buddha", limit=4, sources=("aic", "met"))
    assert [c["ref"] for c in out] == ["aic:16568"]
    err = capsys.readouterr().err
    assert "met lỗi" in err
    assert "aic lỗi" not in err
