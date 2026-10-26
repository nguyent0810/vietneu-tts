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
