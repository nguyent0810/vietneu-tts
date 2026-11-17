"""Chuyển văn xuôi thành script V2, giữ nguyên lời kể."""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "motion" / "long"))
import script_lines

CHAPTER = re.compile(r"^## CH\d\d · .+$")
# Append the root as in motion/long/floor.py (#076), preserving V2 imports.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.append(str(_REPO_ROOT))
from tools.prose_split import PDSplitter, split_sentences


def convert(md):
    lines = md.splitlines(keepends=True)
    out, paragraph = [], []
    in_chapter = False
    splitter = PDSplitter()

    def flush():
        if not paragraph:
            return
        text = ' '.join(x.strip() for x in paragraph)
        paragraph.clear()
        for sent, pd in splitter.feed(text):
            out.append(sent + (' {pd}' if pd else '') + '\n')

    for raw in lines:
        s = raw.strip()
        if CHAPTER.match(s):
            flush()
            if splitter.pd:
                raise ValueError('Marker PD chưa đóng trước chương mới')
            in_chapter = True
            out.append(raw)
        elif in_chapter and s.startswith('## '):
            flush()
            if splitter.pd:
                raise ValueError('Marker PD chưa đóng trước phần cuối')
            in_chapter = False
            out.append(raw)
        elif not in_chapter:
            out.append(raw)
        elif not s or s == '---':
            flush()
            out.append(raw)
        elif s.startswith('»'):
            flush()
            paragraph.append(raw)
            flush()
        else:
            paragraph.append(raw)
    flush()
    splitter.finish()
    return ''.join(out)


def parse_chapters(md):
    # Parser V2 dừng ở Ghi chú; những tiêu đề cuối khác cũng không phải lời đọc.
    lines = md.splitlines(keepends=True)
    started = False
    for index, line in enumerate(lines):
        if CHAPTER.match(line.strip()):
            started = True
        elif started and line.strip().startswith('## '):
            return script_lines.parse(''.join(lines[:index]))
    return script_lines.parse(md)


def main():
    from factory.console import utf8_console
    utf8_console()
    ap = argparse.ArgumentParser()
    ap.add_argument('input', type=Path)
    ap.add_argument('output', type=Path)
    args = ap.parse_args()
    result = convert(args.input.read_text(encoding='utf-8'))
    args.output.write_text(result, encoding='utf-8')
    chs = parse_chapters(result)
    if not chs:
        raise SystemExit('Không tìm thấy chương CHNN')
    errors = script_lines.gate(chs)
    longest = ('', 0)
    count = 0
    for ch in chs:
        texts = [x if isinstance(x, str) else x['t'] for x in ch['lines']]
        count += len(texts)
        print(f"{ch['name']}: {len(texts)} câu, {sum(len(t.split()) for t in texts)} tiếng")
        for t in texts:
            if len(t.split()) > longest[1]:
                longest = (t, len(t.split()))
    print(f"Tổng: {count} câu; câu dài nhất {longest[1]} tiếng: {longest[0]}")
    for error in errors:
        print('LỖI:', error)
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
