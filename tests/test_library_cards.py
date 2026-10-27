import importlib.util, json, tempfile, unittest
from pathlib import Path
MODULE=Path(__file__).resolve().parents[1]/'library/tools/cards.py'
spec=importlib.util.spec_from_file_location('cards',MODULE); cards=importlib.util.module_from_spec(spec); spec.loader.exec_module(cards)

class CardsTests(unittest.TestCase):
 def test_regeneration_preserves_editor_fields_and_body(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td); inv=root/'inventory'; out=root/'cards'; inv.mkdir()
   (inv/'techniques.json').write_text(json.dumps({'techniques':[{'id':'demo','group':'template','name_vi':'Tên mới','count':4,'source_count':2,'sources':['a','b'],'built':'co_san','built_evidence':[],'examples':[]}]}))
   (inv/'taxonomy.json').write_text(json.dumps([{'id':'demo','group':'template','name_vi':'Tên mới','alias':[]}]))
   p=out/'template/demo.md'; p.parent.mkdir(parents=True)
   p.write_text('---\n'+json.dumps({'id':'demo','ten':'Tên Lead','pham_vi':['cl'],'hop_ngach':['x'],'cam_ngach':[],'so_muc':1})+'\n---\n\n## Mô tả\n\nNội dung do người viết.\n')
   old_inv,old_cards=cards.INV,cards.CARDS; cards.INV,cards.CARDS=inv,out
   try:
    cards.generate(); d,body=cards.read_card(p)
    self.assertEqual(d['ten'],'Tên Lead'); self.assertEqual(d['pham_vi'],['cl']); self.assertEqual(d['hop_ngach'],['x'])
    self.assertEqual(d['so_muc'],4); self.assertEqual(d['so_nguon'],2); self.assertEqual(d['da_dung'],'co_san')
    self.assertIn('Nội dung do người viết.',body)
   finally: cards.INV,cards.CARDS=old_inv,old_cards

if __name__=='__main__': unittest.main()


def test_chay_lai_ra_dung_tung_byte(tmp_path, monkeypatch):
    """Lead 26/10: regex đọc thẻ nuốt dòng trống đầu thân -> lần ghi 2 khác lần 1. Thân phải được chuẩn hoá."""
    import importlib, json, sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "library/tools"))
    cards = importlib.import_module("cards")
    inv = tmp_path / "inventory"; inv.mkdir()
    (inv / "taxonomy.json").write_text(json.dumps([{"id": "giay_cat", "name_vi": "Giấy cắt", "group": "style"}]), encoding="utf-8")
    (inv / "techniques.json").write_text(json.dumps({"techniques": [{"id": "giay_cat", "count": 3, "source_count": 2,
                                                                    "sources": ["a", "b"], "built": "chua_co"}]}), encoding="utf-8")
    monkeypatch.setattr(cards, "INV", inv); monkeypatch.setattr(cards, "CARDS", tmp_path / "cards")
    outs = []
    for _ in range(3):
        cards.generate()
        outs.append((tmp_path / "cards/canh/giay_cat.md").read_bytes())
    assert outs[0] == outs[1] == outs[2]


def test_pick_loai_tru_chuoi_bao_ve(tmp_path, monkeypatch):
    """ADR 0018 mục 7: chuỗi thắng (Chú Đại Bi) nằm trong khuôn 'thua' vẫn phải bị loại trừ khỏi nơi áp thư viện."""
    import importlib, sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "library/tools"))
    lib = importlib.import_module("lib")
    prof = {"bud": {"khuon": [{"ten": "niem", "trang_thai": "thua", "dinh_dang": "short", "nguon": "x"},
                              {"ten": "tuong", "trang_thai": "thang", "dinh_dang": "short", "nguon": "x"}],
                    "bao_ve": [{"ten": "Chú Đại Bi", "khuon": "niem", "ly_do": "thắng"}]}, "fs": {"khuon": []}}
    monkeypatch.setattr(lib, "sync_channels", lambda u: prof)
    monkeypatch.setattr(lib, "_experiments", lambda u, c: [])
    monkeypatch.setattr(lib, "ranked", lambda c, n: [])
    res = lib.picks("bud", str(tmp_path))
    names = [p["ten"] for p in res["noi_duoc_ap"]]
    assert "tuong" not in names                       # khuôn thắng không bao giờ được gợi ý
    niem = next(p for p in res["noi_duoc_ap"] if p["ten"] == "niem")
    assert niem["loai_tru"] and "Chú Đại Bi" in niem["loai_tru"][0]


def _lib():
    import importlib, sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "library/tools"))
    return importlib.import_module("lib")


_PROF = {"bud": {"khuon": [{"ten": "niem", "trang_thai": "thua", "dinh_dang": "short", "nguon": "x"},
                           {"ten": "phap", "trang_thai": "thua", "dinh_dang": "short", "nguon": "x"},
                           {"ten": "tuong", "trang_thai": "thang", "dinh_dang": "short", "nguon": "x"}],
                 "bao_ve": [{"ten": "Chú Đại Bi", "khuon": "niem", "ly_do": "thắng", "tu_khoa": ["Đại Bi"]}]},
         "fs": {"khuon": []}}


def _write_exp(root, cells):
    d = root / "output/cl_staging/experiments"; d.mkdir(parents=True)
    (d / "tn_x.json").write_text(json.dumps({"tn": cells}, ensure_ascii=False), encoding="utf8")


def test_pick_loai_o_thu_chua_chuoi_bao_ve(tmp_path, monkeypatch):
    """Vòng chấm 26/10: Codex chọn ô tn_2026-10 có TN4 = chuỗi Chú Đại Bi. pick phải tách từng ô và loại ô đó."""
    lib = _lib()
    _write_exp(tmp_path, [{"ma": "TN4", "kenh": "bud", "lam": "Phần 3–7 Chú Đại Bi"},
                          {"ma": "TN9", "kenh": "bud", "lam": "thử chữ trồi ở khuôn phap"},
                          {"ma": "TN2", "kenh": "fs", "lam": "bảng tháng 10"}])
    monkeypatch.setattr(lib, "sync_channels", lambda u: _PROF)
    monkeypatch.setattr(lib, "ranked", lambda c, n: [])
    res = lib.picks("bud", str(tmp_path))
    names = [p["ten"] for p in res["noi_duoc_ap"]]
    assert "TN9" in names and "TN4" not in names and "TN2" not in names
    assert [x["ten"] for x in res["o_thu_bi_loai"]] == ["TN4"]
    assert "niem" in names          # khuôn thua vẫn được áp; chỉ chuỗi bên trong bị cấm


def test_register_cell_tu_choi_khuon_thang_va_ma_trung(tmp_path, monkeypatch):
    import pytest
    lib = _lib()
    _write_exp(tmp_path, [{"ma": "TN4", "kenh": "bud", "lam": "Chú Đại Bi"}])
    monkeypatch.setattr(lib, "sync_channels", lambda u: _PROF)
    with pytest.raises(SystemExit, match="đang thắng"):
        lib.register_cell("bud", "LIB1", "tuong", "text_reveal", "x", str(tmp_path))
    with pytest.raises(SystemExit, match="đã có"):
        lib.register_cell("bud", "TN4", "phap", "text_reveal", "x", str(tmp_path))
    with pytest.raises(SystemExit, match="chuỗi bảo vệ"):
        lib.register_cell("bud", "LIB2", "niem", "text_reveal", "series Đại Bi phần 8", str(tmp_path))
    lib.register_cell("bud", "LIB1", "phap", "text_reveal", "chữ trồi kéo AVP khuôn phap", str(tmp_path))
    saved = json.loads((tmp_path / "output/cl_staging/experiments/lib_bud.json").read_text(encoding="utf8"))
    assert saved["tn"][0]["ma"] == "LIB1"
    assert "LIB1" in [p["ten"] for p in lib.picks("bud", str(tmp_path))["noi_duoc_ap"]]


def test_kenh_ngoai_tu_khai_ho_so(tmp_path, monkeypatch):
    """Kênh khác (vd MIMCK) chỉ cần thả một hồ sơ vào channels/: rank/pick/register-cell chạy được, dạng thắng vẫn bị loại."""
    import shutil
    lib = _lib()
    ch = tmp_path / "channels"; ch.mkdir()
    for f in ("fs.yaml", "bud.yaml"):
        shutil.copy(lib.CHANNELS / f, ch / f)
    prof = {"kenh": "mimck", "khuon": [{"ten": "a", "dinh_dang": "short", "trang_thai": "thang", "nguon": "x"},
                                     {"ten": "b", "dinh_dang": "short", "trang_thai": "thua", "nguon": "x"}],
            "bao_ve": [], "do_hop_mac_dinh": 1, "do_hop": {"glitch": 0}, "thu_muc_thu_nghiem": "exp"}
    (ch / "mimck.yaml").write_text(json.dumps(prof, ensure_ascii=False), encoding="utf8")
    (ch / "_mau.yaml").write_text("{}", encoding="utf8")
    monkeypatch.setattr(lib, "CHANNELS", ch)
    assert "mimck" in lib.channel_names() and "_mau" not in lib.channel_names()
    rows = lib.ranked("mimck", 200)
    assert rows and "glitch" not in [r["id"] for r in rows]          # ghi đè 0 thì loại
    assert any(r["ly_do"].endswith("dung_that") for r in rows)       # đã dùng ở FS/BUD vẫn là mới với kênh ngoài
    usage = tmp_path / "repo_mimck"; usage.mkdir()
    res = lib.picks("mimck", str(usage))
    assert [p["ten"] for p in res["noi_duoc_ap"]] == ["b"]            # khuôn thắng không được gợi ý
    lib.register_cell("mimck", "M1", "b", rows[0]["id"], "thử", str(usage))
    assert (usage / "exp/lib_mimck.json").is_file()
    assert json.loads((ch / "fs.yaml").read_text())["khuon"]          # checkout ngoài không xoá khuôn FS đã commit


def test_pick_goi_y_theo_ly_do_thua(tmp_path, monkeypatch):
    """Phản hồi MIMCK 26/10: mỗi khuôn phải nhận gợi ý chữa đúng lý do thua; không có thì báo thiếu, không gợi ý bừa."""
    lib = _lib()
    ch = tmp_path / "channels"; ch.mkdir()
    prof = {"kenh": "x", "do_hop_mac_dinh": 1, "bao_ve": [], "khuon": [
        {"ten": "ctr_thua", "dinh_dang": "long", "trang_thai": "thua", "nguon": "x", "ly_do_thua": ["ctr"]},
        {"ten": "hinh_thua", "dinh_dang": "short", "trang_thai": "thua", "nguon": "x", "ly_do_thua": ["hinh"]},
        {"ten": "chua_khai", "dinh_dang": "short", "trang_thai": "ngang", "nguon": "x"}]}
    (ch / "x.yaml").write_text(json.dumps(prof, ensure_ascii=False), encoding="utf8")
    monkeypatch.setattr(lib, "CHANNELS", ch)
    monkeypatch.setattr(lib, "sync_channels", lambda u: (_ for _ in ()).throw(AssertionError("kênh ngoài không được sync")))
    pool = [{"id": f"h{i}", "ten": f"h{i}", "chua_duoc": ["hinh"], "diem": 1.0, "ly_do": ""} for i in range(4)]
    monkeypatch.setattr(lib, "ranked", lambda c, n: pool)   # kho chỉ có thẻ hình: khuôn thua vì ctr phải báo thiếu
    res = {p["ten"]: p for p in lib.picks("x", str(tmp_path))["noi_duoc_ap"]}
    assert res["ctr_thua"]["goi_y"] == [] and "chưa có" in res["ctr_thua"]["thieu"]
    assert res["hinh_thua"]["goi_y"] and all("hinh" in r["chua_duoc"] for r in res["hinh_thua"]["goi_y"])
    assert res["chua_khai"]["goi_y"] and "ly_do_thua" in res["chua_khai"]["canh_bao"]


def test_the_chu_de_hook_thumbnail_vao_duoc_pick():
    """Thẻ ngoài hình (Muse 26/10) có chua_duoc thì rank xét tới; FS/BUD không bị gợi ý lại thẻ đã dùng thật."""
    lib = _lib()
    ids = {r["id"]: r for r in lib.ranked("bud", 10**6)}
    assert "thumb_ab_test_watch_time" in ids and "ctr" in ids["thumb_ab_test_watch_time"]["chua_duoc"]
    assert "thumb_tuy_chinh" not in ids          # dung_that ở FS/BUD


def test_pick_loc_theo_dinh_dang(tmp_path, monkeypatch):
    """Khuôn short không nhận thẻ chỉ dành cho long (vd thumbnail), 26/10."""
    lib = _lib()
    ch = tmp_path / "channels"; ch.mkdir()
    prof = {"kenh": "x", "do_hop_mac_dinh": 1, "bao_ve": [], "khuon": [
        {"ten": "s", "dinh_dang": "short", "trang_thai": "thua", "nguon": "x", "ly_do_thua": ["ctr", "hook"]},
        {"ten": "l", "dinh_dang": "long", "trang_thai": "thua", "nguon": "x", "ly_do_thua": ["ctr"]}]}
    (ch / "x.yaml").write_text(json.dumps(prof, ensure_ascii=False), encoding="utf8")
    monkeypatch.setattr(lib, "CHANNELS", ch)
    res = {p["ten"]: p for p in lib.picks("x", str(tmp_path))["noi_duoc_ap"]}
    assert res["s"]["goi_y"] and all(set(r["dinh_dang"]) & {"short", "ca_hai"} for r in res["s"]["goi_y"])
    assert any(r["id"].startswith("thumb_") for r in res["l"]["goi_y"])


def test_check_chan_duong_dan_tro_ra_ngoai_repo():
    """CI PR #38 đỏ 27/10: thẻ statue_cards có nguon_su_that '../../../../Users/...' (chỉ đúng trên máy Lead)."""
    lib = _lib()
    d = {"nguon_su_that": ["../../../../Users/x/output/a.py", "/abs/b.py"]}
    errs = [e for e in lib.validate({**d}, {"required": [], "properties": {}}) if "gốc repo" in e]
    assert len(errs) == 2
