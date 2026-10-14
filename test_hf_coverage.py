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


# ---- sổ tách theo kênh -----------------------------------------------------
def test_so_theo_kenh_khong_xoa_id_kenh_khac(tmp_path, monkeypatch):
    """Quét kênh Phong Thuỷ từng xoá sạch video riêng tư của kênh Phật giáo
    khỏi sổ chung. Giờ mỗi kênh chỉ ghi phần của mình."""
    monkeypatch.setattr(cov, "PROJECT_ROOT", tmp_path)
    cov.save_index({"BUD1", "BUD2"}, channel="UC_BUD")
    cov.save_index({"FS1"}, channel="UC_FS")
    assert cov.load_index(channel="UC_BUD") == {"BUD1", "BUD2"}
    assert cov.load_index(channel="UC_FS") == {"FS1"}


def test_so_phang_cu_thanh_be_chung(tmp_path, monkeypatch):
    monkeypatch.setattr(cov, "PROJECT_ROOT", tmp_path)
    cov.save_index({"A", "B", "C"})              # định dạng cũ: danh sách phẳng
    assert cov.load_index(channel="UC_X") == {"A", "B", "C"}
    cov.save_index({"A"}, channel="UC_X")        # kênh X nhận A là của mình
    assert cov.load_index(channel="UC_X") == {"A", "B", "C"}
    assert cov.own_channel_index(cov.INDEX_PATH, "UC_X") == {"A"}
    assert cov.load_index(channel="UC_Y") == {"B", "C"}   # A đã rời bể chung


def test_chi_dem_video_cua_kenh_dang_xet():
    rows = [{"id": "1", "channel": "UC_FS", "when": "2026-09-28T01:00:00Z"},
            {"id": "2", "channel": "UC_BUD", "when": "2026-09-28T03:30:00Z"},
            {"id": "3", "channel": "UC_FS", "when": "2026-09-28T08:00:00Z"}]
    assert [r["id"] for r in cov.rows_of_channel(rows, "UC_FS")] == ["1", "3"]


def test_khung_da_co_video():
    rows = [{"id": "1", "when": "2026-10-01T04:30:00Z", "privacy": "private", "scheduled": True},
            {"id": "2", "when": "2026-10-01T08:00:00Z", "privacy": "public", "scheduled": False},
            {"id": "3", "when": "2026-09-01T02:00:00Z", "privacy": "private", "scheduled": False}]
    # video riêng tư đã huỷ hẹn không chiếm khung
    assert cov.slots_taken(rows) == {"2026-10-01T04:30", "2026-10-01T08:00"}


def _fake_search(pages):
    calls = []

    def _get(cred, url, params):
        i = int(params.get("pageToken") or 0)
        calls.append(i)
        nxt = str(i + 1) if i + 1 < len(pages) else None
        return {"items": [{"id": {"videoId": v}} for v in pages[i]], "nextPageToken": nxt}
    return _get, calls


def test_do_sau_dung_som_khi_hai_trang_lien_da_biet(monkeypatch):
    # Mỗi trang search.list là một lượt trong hạn mức 100 lượt/ngày.
    pages = [["new1", "a"], ["b", "c"], ["d", "e"], ["f"], ["g"]]
    _get, calls = _fake_search(pages)
    monkeypatch.setattr(cov, "_api", lambda: (_get, None, None, None))
    got = cov.discover_ids_deep("x", known={"a", "b", "c", "d", "e", "f", "g"})
    assert "new1" in got and calls == [0, 1, 2]


def test_do_sau_khong_co_so_thi_quet_tron(monkeypatch):
    pages = [["a"], ["b"], ["c"], ["d"]]
    _get, calls = _fake_search(pages)
    monkeypatch.setattr(cov, "_api", lambda: (_get, None, None, None))
    assert cov.discover_ids_deep("x") == {"a", "b", "c", "d"} and calls == [0, 1, 2, 3]


def test_do_sau_trang_co_id_moi_thi_dem_lai(monkeypatch):
    # Một trang đã biết rồi một trang có ID lạ: bộ đếm về 0, quét tiếp.
    pages = [["a"], ["new"], ["b"], ["c"], ["d"]]
    _get, calls = _fake_search(pages)
    monkeypatch.setattr(cov, "_api", lambda: (_get, None, None, None))
    got = cov.discover_ids_deep("x", known={"a", "b", "c", "d"})
    assert "new" in got and calls == [0, 1, 2, 3]
