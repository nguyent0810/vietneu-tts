import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("fs_month_tuoi", ROOT / "tools/fs_month_tuoi.py")
fs_month_tuoi = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(fs_month_tuoi)


def test_month_11_2026_calendar_and_relationship_facts():
    ng = fs_month_tuoi.facts("Ngọ", 2026, 11)
    assert ng["chi_thang"] == "Tý"
    assert ng["khoang_duong"] == {"start": "2026-12-09", "end": "2027-01-07"}
    assert {r["duong"] for r in ng["xung_days"]} == {"2026-12-16", "2026-12-28"}
    assert {r["duong"] for r in ng["best_days"]} == {"2027-01-07"}
    assert {r["duong"] for r in fs_month_tuoi.facts("Mão", 2026, 11)["best_days"]} == {"2027-01-07"}
    assert len(fs_month_tuoi.facts("Thìn", 2026, 11)["good_days"]) == 7


def test_anchor_and_thanh_long_facts():
    tuat = fs_month_tuoi.facts("Tuất", 2026, 11)
    assert next(a for a in tuat["anchors"] if a["name"] == "01/01")["xung"]
    # Đông chí 2026 = 21/12 20:45 UT = 22/12 giờ VN, ngày Canh Ngọ: xung Tý, không xung Hợi.
    ty = fs_month_tuoi.facts("Tý", 2026, 11)
    dong_chi = next(a for a in ty["anchors"] if a["name"] == "Đông chí")
    assert dong_chi["duong"] == "2026-12-22" and dong_chi["xung"]
    hoi = fs_month_tuoi.facts("Hợi", 2026, 11)
    assert not next(a for a in hoi["anchors"] if a["name"] == "Đông chí")["xung"]
    dan = fs_month_tuoi.facts("Dần", 2026, 11)
    for day in ("2026-12-12", "2026-12-24"):
        row = next(d for d in dan["days"] if d["duong"] == day)
        assert row["xung"] and row["than"] == "Thanh Long"


def test_chi_rel_same_and_tu_hinh():
    from fs_calendar.batrach import chi_rel
    assert chi_rel("Ngọ", "Ngọ") == "đồng chi"
    assert chi_rel("Tý", "Mão") == "tương hình"
    assert chi_rel("Tý", "Ngọ") == "lục xung"


def test_visuals_have_four_engine_blocks_and_variable_rows():
    data = fs_month_tuoi.facts("Ngọ", 2026, 11)
    visual = fs_month_tuoi.visuals(data)
    assert set(visual) == {"BẢNG NĂM SINH", "NGÀY XUNG", "NGÀY TỐT", "NGÀY NEO"}
    assert visual["BẢNG NĂM SINH"]["type"] == "lookup"
    assert len(visual["BẢNG NĂM SINH"]["rows"]) == len(data["birth_years"])
    assert all(visual[name]["type"] == "list" for name in ("NGÀY XUNG", "NGÀY TỐT", "NGÀY NEO"))


def test_build_new_attaches_tables_deterministically(tmp_path):
    spec = importlib.util.spec_from_file_location("long_plan_build_month", ROOT / "tools/long_plan_build.py")
    builder = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(builder)
    script = tmp_path / "script.txt"
    script.write_text("\n".join(["**Mở đầu**", "[BẢNG NĂM SINH] Bảng.", "[NGÀY XUNG] Xung.",
                                   "[NGÀY TỐT] Tốt.", "[NGÀY NEO] Neo."]), encoding="utf-8")
    base = tmp_path / "base.json"
    base.write_text(json.dumps([{"style": "laban_long", "series": "fs", "lane": "long", "tts": {}, "sound": {}}]), encoding="utf-8")
    tables = tmp_path / "tables.json"
    tables.write_text(json.dumps(fs_month_tuoi.visuals(fs_month_tuoi.facts("Ngọ", 2026, 11)), ensure_ascii=False), encoding="utf-8")
    out1, out2 = tmp_path / "one.json", tmp_path / "two.json"
    builder.build_new(script, "fs_month_fixture", "fs", base, out1, tables=tables)
    builder.build_new(script, "fs_month_fixture", "fs", base, out2, tables=tables)
    assert out1.read_bytes() == out2.read_bytes()
    visuals = json.loads(out1.read_text(encoding="utf-8"))[0]["visuals"]
    assert [visuals[str(i)]["type"] for i in range(2, 6)] == ["lookup", "list", "list", "list"]


def test_cli_writes_facts_and_tables(tmp_path):
    import os
    import subprocess
    import sys
    root = Path(__file__).resolve().parents[1]
    r = subprocess.run([sys.executable, str(root / "tools" / "fs_month_tuoi.py"), "Ngọ", "--year", "2026", "--month", "11",
                        "--out-dir", str(tmp_path)], cwd=root, capture_output=True, text=True,
                       env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"})
    assert r.returncode == 0, r.stderr[-800:]
    assert (tmp_path / "t11_Ngọ_facts.json").exists() and (tmp_path / "t11_Ngọ_tables.json").exists()
