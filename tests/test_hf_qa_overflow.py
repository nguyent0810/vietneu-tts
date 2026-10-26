"""Cổng tràn chữ cho short (hf_qa.gate_overflow).

25/10, lô TN2: tiêu đề vàng "DÂN GIAN HAY KIÊNG" ở 96 px vượt mép phải, và lưới năm 5 cột 52 px tràn khi
.tag nowrap làm cột nhãn nở. Cả hai chỉ lộ ra ở khung tĩnh; `hyperframes check` xếp chúng mức info/warning
nên HF_QA=strict không chặn.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import hf_qa  # noqa: E402

TEMPLATE = ROOT / "hyperframes_short" / "compositions" / "review_yeartable.html"


def _report(*layout, contrast=()):
    return {"ok": True, "layout": {"findings": list(layout)}, "contrast": {"findings": list(contrast)}}


def test_tran_muc_info_van_bi_chan():
    rep = _report({"severity": "info", "code": "canvas_overflow", "selector": "span.l.gold", "text": "DÂN GIAN HAY KIÊNG",
                   "time": 1.1, "overflow": {"right": 25.5}})
    lines = hf_qa.overflow_lines(rep)
    assert len(lines) == 1 and "span.l.gold" in lines[0] and "26px" in lines[0]


def test_gop_cung_cho_tran_qua_nhieu_mau():
    f = {"severity": "warning", "code": "container_overflow", "selector": "div.years", "text": ""}
    rep = _report({**f, "time": 1.0, "overflow": {"right": 100}}, {**f, "time": 3.0, "overflow": {"right": 120}})
    lines = hf_qa.overflow_lines(rep)
    assert len(lines) == 1 and "120px" in lines[0] and "1.0, 3.0" in lines[0]


def test_bo_qua_ma_khac_va_muc_khac():
    rep = _report({"severity": "warning", "code": "text_not_painted", "selector": "div.x"},
                  contrast=[{"severity": "error", "code": "contrast_overflow", "selector": "p"}])
    assert hf_qa.overflow_lines(rep) == []


def test_khong_lay_duoc_mau_khong_duoc_tinh_la_dat(monkeypatch):
    # 26/10: bản đầu dùng `check`, lint lỗi font làm bước layout bị bỏ (0 mẫu) -> cổng từng "đạt" im lặng
    monkeypatch.setattr(hf_qa, "inspect_layout", lambda *a, **k: {"ok": True, "layout": {"findings": [], "samples": 0}})
    with pytest.raises(RuntimeError, match="0 mẫu"):
        hf_qa.gate_overflow(Path("x.html"))


def test_vet_sang_yeartable_duoc_danh_dau_tran_co_chu_dich():
    html = TEMPLATE.read_text(encoding="utf-8")
    shines = re.findall(r'<div class="shine"[^>]*>', html)
    assert shines and all("data-layout-allow-overflow" in s for s in shines), shines


# ---- chạy thật hyperframes check (cần Node 22 qua nvm, ~6 giây mỗi bài) ----

def _node22() -> bool:
    if not shutil.which("bash"):
        return False
    r = subprocess.run(["/bin/bash", "-lc", 'export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1 && nvm which 22'],
                       capture_output=True, text=True)
    return r.returncode == 0


needs_node22 = pytest.mark.skipif(not _node22(), reason="cần Node 22 qua nvm cho hyperframes check")

ROWS = [("TỴ", "XUNG THÁNG HỢI", [1953, 1965, 1977, 1989, 2001]),
        ("THÂN", "HẠI", [1956, 1968, 1980, 1992, 2004]),
        ("HỢI", "TỰ HÌNH", [1959, 1971, 1983, 1995, 2007])]
TITLE_OK = '<span class="l s">THÁNG 10 ÂM</span><span class="l gold">TUỔI NÀO XUNG?</span>'
CSS_5COT_TRAN = ".tag { white-space: nowrap; } .years, .years.col4 { grid-template-columns: repeat(5, 1fr) !important; } .big .y { font-size: 52px !important; }"
CSS_5COT_VUA = (".tag { white-space: normal !important; } .years, .years.col4 { grid-template-columns: repeat(5, 1fr) !important; } "
                ".lab { flex: 0 0 230px !important; min-width: 0; } .big .chi { font-size: 72px !important; } "
                ".big .y { font-size: 42px !important; letter-spacing: 0 !important; } .years .y { min-width: 0; }")


def _comp(tmp_path: Path, name: str, title_html: str, css: str = "") -> Path:
    data = {"dur": 6, "theme": "navy", "segs": [{"start": 0.3, "end": 5.5, "text": "Tháng mười âm là tháng Hợi."}],
            "rows": [{"chi": c, "tag": t, "years": ys} for c, t, ys in ROWS]}
    html = TEMPLATE.read_text(encoding="utf-8").replace("</style>", css + "</style>")
    html = (html.replace("__DUR__", "6").replace("__CHIP__", "THÁNG 10 ÂM").replace("__TITLE__", title_html)
            .replace("__DATA__", json.dumps(data, ensure_ascii=False)))
    p = tmp_path / f"{name}.html"
    p.write_text(html, encoding="utf-8")
    return p


@needs_node22
def test_e2e_bat_tieu_de_vang_tran(tmp_path):
    p = _comp(tmp_path, "ovf_title", '<span class="l s">THÁNG 10 ÂM CÓ 9 NGÀY</span><span class="l gold">DÂN GIAN HAY KIÊNG</span>', CSS_5COT_VUA)
    issues = hf_qa.gate_overflow(p, samples=3)
    assert any("span.l.gold" in ln for ln in issues), issues


@needs_node22
def test_e2e_bat_luoi_5_cot_tran(tmp_path):
    issues = hf_qa.gate_overflow(_comp(tmp_path, "ovf_grid", TITLE_OK, CSS_5COT_TRAN), samples=3)
    assert any("span.y" in ln or "div.years" in ln for ln in issues), issues


@needs_node22
def test_e2e_ban_da_sua_dat(tmp_path):
    assert hf_qa.gate_overflow(_comp(tmp_path, "ovf_ok", TITLE_OK, CSS_5COT_VUA), samples=3) == []
