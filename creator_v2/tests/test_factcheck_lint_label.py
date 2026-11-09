import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "motion" / "long"))
import factcheck_lint as F  # noqa: E402

FC = '| CH05 | x | TRÍCH DỊCH · nguyên văn: "Pour prix de mes faveurs" — https://fr.wikipedia.org/wiki/Mata_Hari |'


def test_display_label_alone_is_not_a_quote():
    art = "» Câu trích một. [TRÍCH DỊCH]\nTRÍCH DỊCH\n"
    assert F.translation_issues(art, FC) == []


def test_missing_source_still_flagged():
    art = "» Câu một. [TRÍCH DỊCH]\n» Câu hai. [TRÍCH DỊCH]\nTRÍCH DỊCH\n"
    assert F.translation_issues(art, FC)
