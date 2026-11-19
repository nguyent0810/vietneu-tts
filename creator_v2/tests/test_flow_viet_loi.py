import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import flow_viet_loi as F  # noqa: E402


def test_tidy_closes_second_pd_tag():
    assert F.tidy("[PD]Một cảnh.[PD] Câu thường.") == "[PD]Một cảnh.[/PD] Câu thường."


def test_tidy_keeps_balanced_tags():
    s = "[PD]A.[/PD] B. [PD]C.[/PD]"
    assert F.tidy(s) == s


def test_tidy_strips_italic_and_bold_but_not_words():
    assert F.tidy("tàu *La Meuron* và **đậm** của snake_case") == "tàu La Meuron và đậm của snake_case"


def test_save_versions_and_tidies(tmp_path, monkeypatch):
    monkeypatch.setattr(F, "INBOX", tmp_path)
    a = F.save("CL", "x", "full", "## CH00 · A\n\n*B*.\r\n")
    b = F.save("CL", "x", "full", "## CH00 · A\n")
    assert a.read_text(encoding="utf-8") == "## CH00 · A\n\nB.\n"
    assert b.name.endswith("_full_v2.md")
