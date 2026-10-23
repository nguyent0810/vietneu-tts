"""SPEC chống "mùi AI" cho engine Long (hyperframes_short/compositions/longform.js), 23/10/2026.

Nguồn: skill hyperframes-animation (gsap-easing-and-stagger.md: back/elastic/bounce là register hiếm, không phải mặc định)
và hyperframes-creative (motion-principles.md). Báo cáo đo: output/cl_staging/hf_art_audit_2026-10-23.md.
"""
import re
from pathlib import Path

COMP = Path(__file__).resolve().parents[1] / "hyperframes_short" / "compositions"
JS = (COMP / "longform.js").read_text(encoding="utf-8")
CSS = (COMP / "longform.css").read_text(encoding="utf-8")


def test_khong_ease_nay():
    # Kim la bàn được dùng elastic (vật lý thật); thẻ, con dấu, nút sơ đồ thì không nảy.
    assert not re.findall(r'"back\.(?:out|in|inOut)', JS)
    assert not re.findall(r'"bounce\.', JS)


def test_tieu_de_chuong_khong_rung_sau_khi_hien():
    assert not re.search(r'q\("\.lf-chap"\),\s*\{\s*x:\s*0\s*\},\s*\{\s*x:', JS)


def test_chu_khoa_khong_phong_sau_khi_hien():
    assert not re.search(r'contains\("acc"\)\)\s*tl\.to\(wd,\s*\{\s*scale:', JS)


def test_khong_rung_ngang_sau_khi_hien():
    # Mẫu rung: x vài px, duration rất ngắn, yoyo lặp nhiều lần.
    assert not re.search(r'\{\s*x:\s*\d+,\s*duration:\s*\.0\d,\s*yoyo:\s*true', JS)


def test_nam_bon_chu_so_khong_cham_nghin():
    # 23/10: thẻ stat hiện "1.863", "1.535" vì chỉ coi là năm khi nhãn có chữ NĂM.
    m = re.search(r"const plain = (.+?);", JS)
    assert m and "target >= 1000" in m.group(1) and "target <= 2100" in m.group(1)


def test_so_dem_tabular_nums():
    assert "tabular-nums" in CSS and ".lf-stat .num" in CSS


def _kc_grim(keys):
    """Chạy đúng KC_GRIM + kcGrim trích từ longform.js bằng node."""
    import json
    import shutil
    import subprocess

    import pytest
    if not shutil.which("node"):
        pytest.skip("không có node")
    src = re.search(r"  const KC_GRIM = .+?\n  const kcGrim = .+?\n.+?\};\n", JS, re.S)
    assert src, "không tìm thấy KC_GRIM/kcGrim"
    code = src.group(0) + f"console.log(JSON.stringify({json.dumps(keys, ensure_ascii=False)}.map(kcGrim)));"
    return json.loads(subprocess.run(["node", "-e", code], capture_output=True, text=True, check=True).stdout)


def test_dau_cat_khong_dong_canh_chu_nghia_xau():
    # 23/10: Long thử Cao Biền hiện 吉 ("tốt lành") cạnh "BỊ GIẾT", "TRỊ TỘI", "ỐM VÌ KHAI QUẬT".
    xau = ["BỊ GIẾT", "TRỊ TỘI", "ỐM VÌ KHAI QUẬT", "Bỏ chạy!", "yểm long mạch", "TAI HOẠ", "phản thần"]
    tot = ["LONG MẠCH", "THĂNG LONG", "TỬ VI TRỌN ĐỜI", "SAO HẠN", "BẢN ĐỒ GIAO CHỈ", "NGŨ HÀNH"]
    assert _kc_grim(xau) == [True] * len(xau)
    assert _kc_grim(tot) == [False] * len(tot)


def test_dau_cat_bi_chan_boi_kcgrim():
    assert re.search(r'kcGrim\(key\) \? "記" : "吉"', JS)
    assert JS.count('"吉"') == 1
