"""Đếm độ phủ — test cho đúng lý do script cũ phải bị thay.

Bản cũ đếm bằng cách duyệt playlist, và đã cho số sai hai lần trong một buổi:
đếm lặp (một video hai lần) và bỏ sót (video có thật không được đếm). Các
test dưới đây chốt cả hai hành vi chống lại chuyện đó.
"""
import json

import hf_coverage as cov


def test_dem_theo_ngay_khong_bi_lap():
    """Cùng một video xuất hiện hai lần trong danh sách nguồn thì chỉ được
    tính một lần -- vì đầu vào đã là tập ID duy nhất, không phải trang."""
    rows = [{"id": "a", "when": "2026-10-02T00:00:00Z"},
            {"id": "b", "when": "2026-10-02T04:30:00Z"},
            {"id": "c", "when": "2026-10-03T00:00:00Z"}]
    counts = cov.count_by_day(rows)
    assert counts["2026-10-02"] == 2
    assert counts["2026-10-03"] == 1


def test_playlist_coi_la_dung_yen_khi_hai_luot_giong_nhau():
    assert not cov.discovery_stabilised([{"a", "b"}])
    assert not cov.discovery_stabilised([{"a", "b"}, {"a", "b", "c"}])
    assert cov.discovery_stabilised([{"a", "b"}, {"a", "b", "c"}, {"a", "b", "c"}])


def test_so_da_dang_luon_duoc_hop_vao(tmp_path, monkeypatch):
    """Video ta tự đăng KHÔNG BAO GIỜ được phép sót, kể cả khi playlist
    đang xê dịch và không trả về chúng."""
    d = tmp_path / "output" / "cl_staging" / "dot_thu_nghiem"
    d.mkdir(parents=True)
    (d / "uploaded.json").write_text(json.dumps({"x1": "VID_A", "x2": "VID_B"}), encoding="utf-8")
    monkeypatch.setattr(cov, "PROJECT_ROOT", tmp_path)
    ids = cov.ledger_ids()
    assert set(ids) == {"VID_A", "VID_B"}
    assert ids["VID_A"] == "dot_thu_nghiem"


def test_so_hong_khong_lam_sap_viec_dem(tmp_path, monkeypatch):
    d = tmp_path / "output" / "cl_staging" / "hong"
    d.mkdir(parents=True)
    (d / "uploaded.json").write_text("{ không phải json", encoding="utf-8")
    monkeypatch.setattr(cov, "PROJECT_ROOT", tmp_path)
    assert cov.ledger_ids() == {}


def test_so_id_ben_vung_ghi_va_doc_lai(tmp_path, monkeypatch):
    monkeypatch.setattr(cov, "PROJECT_ROOT", tmp_path)
    assert cov.load_index() == set()
    cov.save_index({"B", "A", "C"})
    assert cov.load_index() == {"A", "B", "C"}


def test_so_id_hong_thi_coi_nhu_rong(tmp_path, monkeypatch):
    monkeypatch.setattr(cov, "PROJECT_ROOT", tmp_path)
    p = tmp_path / "output" / ".video_index.json"
    p.parent.mkdir(parents=True)
    p.write_text("không phải json", encoding="utf-8")
    assert cov.load_index() == set()


def test_so_chi_giu_id_con_song(tmp_path, monkeypatch):
    """Video bị xoá thật phải rời khỏi sổ, nếu không nó sống mãi trong số đếm."""
    monkeypatch.setattr(cov, "PROJECT_ROOT", tmp_path)
    cov.save_index({"CON", "DA_XOA"})
    alive = {"CON"}
    cov.save_index(alive)
    assert cov.load_index() == {"CON"}
