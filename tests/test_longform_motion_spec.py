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
