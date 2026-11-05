"""Đánh dấu một video dài đã QA xong: ghi sha256 của final.mp4 vào output/long/<topic>/qa_ok.
publish_long từ chối nếu final.mp4 đổi sau khi đánh dấu (retro 15/10/2026).

    python scripts/qa_mark.py <topic> [<topic> ...]
"""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory.console import utf8_console

utf8_console()

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "motion" / "long"))
import long_output  # noqa: E402


def mark(topics, root=ROOT):
    for t in topics:
        od = root / "output" / "long" / t
        bad = long_output.final_problems(od)    # GH-170: không QA/đánh dấu một final của lượt hỏng, đang chạy hay lệch chương
        if bad:
            raise SystemExit(f"{t}: final không hợp lệ: " + "; ".join(bad))
        h = hashlib.sha256((od / "final.mp4").read_bytes()).hexdigest()
        (od / "qa_ok").write_text(h + "\n", encoding="utf-8")
        print(f"{t}: qa_ok {h[:12]}")


if __name__ == "__main__":
    mark(sys.argv[1:])
