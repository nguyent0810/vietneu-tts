import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_new_production_scripts_help():
    scripts = [
        "tools/publish/upload_long.py", "tools/publish/upload_bud.py",
        "tools/publish/upload_fs.py", "tools/publish/playlist_apply.py",
        "tools/long/asset_gate.py", "tools/long/pano_stitch.py",
        "tools/long/pano_prep.py", "tools/long/thumb_cb.py",
        "tools/agents/worker_status.py", "tools/review_due.py",
        "tools/long/month_tuoi_map.py", "tools/long/script_fact_check.py",
        "tools/long/pace_precheck.py", "tools/long/qa_sheet.py",
    ]
    for script in scripts:
        result = subprocess.run([sys.executable, str(ROOT / script), "--help"], cwd=ROOT,
                                text=True, capture_output=True, timeout=20)
        assert result.returncode == 0, f"{script}: {result.stderr}"
        assert "usage:" in result.stdout.lower(), script


def test_script_fact_check_catches_wrong_canchi_and_ignores_negation(tmp_path):
    facts = tmp_path / "facts"
    facts.mkdir()
    (facts / "example_facts.json").write_text(json.dumps({
        "days": [{"duong": "2026-12-09", "am": "1/11", "ngay": "Đinh Tỵ", "than": "Nguyên Vũ"}],
        "birth_years": [{"nam_sinh": 1960, "nap_am": "Bích Thượng Thổ", "cac_nam": [{"nam": 2026, "kim_lau": "Thân", "hoang_oc": "Nhất Cát", "sao_nam": "Thái Bạch", "sao_nu": "Thái Âm"}]}]
    }), encoding="utf-8")
    from tools.long.script_fact_check import check_text
    assert any("CAN CHI sai" in error for error in check_text("Ngày 9 tháng 12 là Giáp Tý, Nguyên Vũ.", facts))
    assert check_text("Năm 1960 không phạm Kim Lâu Thân.", facts) == []
    positive = check_text("Kim Lâu Thân năm 1960.", facts)
    assert not any("NẠP ÂM" in error for error in positive)  # không phân loại thành nạp âm


def test_month_map_clamps_table_before_visual_and_chapter():
    from tools.long.month_tuoi_map import clamp_visual_spans
    visual = {10: {"type": "lookup", "until": 20}, 14: {"type": "word", "until": 18}}
    result = clamp_visual_spans(visual, heads=[17], n=24)
    assert result[10]["until"] == 13
    assert result[14]["until"] == 16
