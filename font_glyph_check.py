"""
Kiểm tra 1 font file có đủ glyph tiếng Việt hay không, bằng công cụ
(`fontTools.ttLib`, đọc trực tiếp bảng `cmap`) -- KHÔNG suy đoán từ tên
font hay danh tiếng. Nhiều font Google Fonts phổ biến (kể cả các font
"đa ngôn ngữ") từng thiếu 1 phần dải tổ hợp dấu tiếng Việt dù trông có vẻ
hỗ trợ đầy đủ -- nên bắt buộc xác minh trước khi đưa vào danh sách font
dùng được cho typography/phụ đề.

Dải Unicode bắt buộc cho tiếng Việt:
  U+0102-0103  Ă ă
  U+0110-0111  Đ đ
  U+0128-0129  Ĩ ĩ
  U+0168-0169  Ũ ũ
  U+01A0-01A1  Ơ ơ
  U+01AF-01B0  Ư ư
  U+1EA0-1EF9  Toàn bộ khối tổ hợp phụ âm/nguyên âm có dấu tiếng Việt --
               dải QUAN TRỌNG NHẤT, chứa phần lớn ký tự có dấu thực tế
               dùng trong văn bản (vd ệ, ắ, ờ, ậ...).
"""
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

REQUIRED_RANGES = [
    (0x0102, 0x0103, "Ă/ă"),
    (0x0110, 0x0111, "Đ/đ"),
    (0x0128, 0x0129, "Ĩ/ĩ"),
    (0x0168, 0x0169, "Ũ/ũ"),
    (0x01A0, 0x01A1, "Ơ/ơ"),
    (0x01AF, 0x01B0, "Ư/ư"),
    (0x1EA0, 0x1EF9, "khối tổ hợp dấu tiếng Việt (ệ, ắ, ờ, ậ...)"),
]


class GlyphCheckResult:
    def __init__(self, font_path: Path, passed: bool, missing: list[tuple[int, str]], total_checked: int):
        self.font_path = font_path
        self.passed = passed
        self.missing = missing  # [(codepoint, range_label)]
        self.total_checked = total_checked

    def __repr__(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return f"<GlyphCheckResult {self.font_path.name}: {status}, {len(self.missing)}/{self.total_checked} thiếu>"


def check_font_glyphs(font_path: str | Path) -> GlyphCheckResult:
    font_path = Path(font_path)
    font = TTFont(str(font_path), lazy=True)
    cmap = font.getBestCmap()  # dict {codepoint: glyph_name}

    missing = []
    total = 0
    for start, end, label in REQUIRED_RANGES:
        for cp in range(start, end + 1):
            total += 1
            if cp not in cmap:
                missing.append((cp, label))

    font.close()
    return GlyphCheckResult(font_path, passed=(len(missing) == 0), missing=missing, total_checked=total)


def check_fonts_directory(fonts_dir: str | Path) -> dict[str, GlyphCheckResult]:
    """Kiểm tra mọi file .ttf/.otf trong thư mục, trả về {tên_file: kết quả}."""
    fonts_dir = Path(fonts_dir)
    results = {}
    for font_file in sorted(list(fonts_dir.glob("*.ttf")) + list(fonts_dir.glob("*.otf"))):
        try:
            results[font_file.name] = check_font_glyphs(font_file)
        except Exception as exc:
            print(f"CẢNH BÁO: không đọc được font {font_file.name} ({exc}) -- coi như FAIL.", file=sys.stderr)
            results[font_file.name] = GlyphCheckResult(font_file, passed=False, missing=[], total_checked=0)
    return results


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts-dir", required=True)
    args = ap.parse_args()

    results = check_fonts_directory(args.fonts_dir)
    passed_fonts = []
    for name, result in results.items():
        if result.passed:
            print(f"PASS  {name}  ({result.total_checked} codepoint tiếng Việt bắt buộc, đủ cả)")
            passed_fonts.append(name)
        else:
            missing_labels = sorted(set(label for _cp, label in result.missing))
            print(f"FAIL  {name}  thiếu {len(result.missing)}/{result.total_checked} codepoint -- dải thiếu: {', '.join(missing_labels)}")

    print(f"\nFont dùng được cho tiếng Việt: {passed_fonts}")
    return 0 if passed_fonts else 1


if __name__ == "__main__":
    sys.exit(main())
