"""review_yeartable.html: chú thích // không được nuốt mã phía sau trên cùng dòng (25/10: vệt sáng làm cả script lỗi cú pháp,
bảng năm sinh không hiện, theme về mặc định)."""
import re
from pathlib import Path

HTML = Path(__file__).resolve().parents[1] / "hyperframes_short" / "compositions" / "review_yeartable.html"


def test_khong_co_ma_sau_chu_thich_dong():
    js = "\n".join(re.findall(r"<script>(.*?)</script>", HTML.read_text(encoding="utf-8"), re.S))
    bad = []
    for n, line in enumerate(js.splitlines(), 1):
        code = re.sub(r"`[^`]*`|\"[^\"]*\"|'[^']*'", "", line)   # bỏ chuỗi để không bắt nhầm // trong URL
        i = code.find("//")
        if i >= 0 and re.search(r"[;{}]\s*$", code[i:]) and re.search(r"\w+\s*[.=(]", code[i:]):
            bad.append((n, line.strip()[:120]))
    assert not bad, bad
