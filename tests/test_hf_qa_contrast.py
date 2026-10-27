"""Cổng tương phản chữ cho short (hf_qa.gate_contrast).

25/10 (tn2_nha) và 26/10 (r27_hop2004): theme `ivory` của review_yeartable.html làm dòng #subfoot màu vàng chìm trên nền
ngà (tỉ lệ 1.44, chuẩn AA là 4.5). Cổng tràn chữ không đo tương phản nên lọt hai lô liền.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import hf_qa  # noqa: E402

TEMPLATE = ROOT / "hyperframes_short" / "compositions" / "review_yeartable.html"


def test_doc_ten_font_tu_loi_lint():
    rep = {"lint": {"findings": [{"code": "font_family_without_font_face", "severity": "error",
                                  "message": "Font families used without @font-face declaration: noto serif cjk sc, songti sc. These are not in the auto-resolved font list"}]}}
    assert hf_qa._missing_fonts(rep) == ["noto serif cjk sc", "songti sc"]


def test_gop_theo_selector_lay_ti_le_thap_nhat():
    f = {"severity": "error", "code": "contrast_aa_failure", "selector": "#subfoot", "text": "2027: NỮ GIÁP THÂN"}
    rep = {"contrast": {"samples": [3.4, 10.3], "findings": [{**f, "ratio": 1.6, "time": 3.4}, {**f, "ratio": 1.44, "time": 10.3},
                                                               {"severity": "info", "selector": "#foot", "ratio": 4.0}]}}
    lines = hf_qa.contrast_lines(rep)
    assert len(lines) == 1 and "#subfoot" in lines[0] and "1.44" in lines[0] and "3.4, 10.3" in lines[0]


def test_khong_do_duoc_khong_tinh_la_dat(monkeypatch):
    monkeypatch.setattr(hf_qa, "contrast_check", lambda *a, **k: {"contrast": {"samples": [], "findings": []},
                                                                    "lint": {"findings": []}})
    with pytest.raises(RuntimeError, match="0 mẫu"):
        hf_qa.gate_contrast(Path("x.html"))


# ---- chạy thật hyperframes check (cần Node 22 qua nvm) ----

def _node22() -> bool:
    if not shutil.which("bash"):
        return False
    r = subprocess.run(["/bin/bash", "-lc", 'export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh" >/dev/null 2>&1 && nvm which 22'],
                       capture_output=True, text=True)
    return r.returncode == 0


needs_node22 = pytest.mark.skipif(not _node22(), reason="cần Node 22 qua nvm cho hyperframes check")

SUBFOOT_CSS = ("#subfoot { position: absolute; left: 50px; right: 50px; bottom: 120px; text-align: center; color: var(--gold2);"
               " font-weight: 800; font-size: 30px; letter-spacing: .05em; text-shadow: 0 2px 8px rgba(0,0,0,.6); }")


def _comp(tmp_path: Path, name: str, theme: str, extra_css: str = "") -> Path:
    data = {"dur": 6, "theme": theme, "segs": [{"start": 0.3, "end": 5.5, "text": "Sinh năm hai nghìn lẻ bốn, hợp tuổi nào?"}],
            "rows": [{"chi": "TÝ", "tag": "TAM HỢP", "years": [1996, 2008]}, {"chi": "THÌN", "tag": "TAM HỢP", "years": [2000, 2012]}]}
    html = TEMPLATE.read_text(encoding="utf-8").replace("</style>", SUBFOOT_CSS + extra_css + "</style>")
    html = html.replace('<div id="foot">', '<div id="subfoot">2027: NỮ GIÁP THÂN CƯỚI PHẠM KIM LÂU TỬ</div>\n  <div id="foot">')
    html = (html.replace("__DUR__", "6").replace("__CHIP__", "GIÁP THÂN · 2004")
            .replace("__TITLE__", '<span class="l s">SINH NĂM 2004</span><span class="l gold">HỢP TUỔI NÀO?</span>')
            .replace("__DATA__", json.dumps(data, ensure_ascii=False)))
    p = tmp_path / f"{name}.html"
    p.write_text(html, encoding="utf-8")
    return p


@needs_node22
def test_e2e_nen_nga_bi_chan(tmp_path):
    issues = hf_qa.gate_contrast(_comp(tmp_path, "ctr_ivory", "ivory"))
    assert any("#subfoot" in ln for ln in issues), issues


@needs_node22
def test_e2e_nen_do_dat(tmp_path):
    assert hf_qa.gate_contrast(_comp(tmp_path, "ctr_red", "red")) == []


@needs_node22
def test_e2e_font_du_phong_khong_chan_phep_do(tmp_path):
    # thẻ tượng BUD có font dự phòng Noto Serif CJK SC không khai @font-face -> lint lỗi, check bỏ phần đo nếu không vá
    css = ' #title { font-family: "Be Vietnam Pro", "Noto Serif CJK SC", serif; }'
    assert hf_qa.gate_contrast(_comp(tmp_path, "ctr_font", "red", css)) == []
