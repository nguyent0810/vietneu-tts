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
ABBR = {"tp", "st", "m", "mr", "mrs", "ms", "dr", "pgs", "ts", "gs"}
CLOSERS = '"”’»\')]}‖'


def split_sentences(text):
    """Giữ dấu chấm trong số, tên và các viết tắt thường gặp."""
    out, start, i = [], 0, 0
    while i < len(text):
        c = text[i]
        if c not in '.!?…':
            i += 1
            continue
        if c == '.':
            if i + 1 < len(text) and not text[i + 1].isspace() and text[i + 1] not in CLOSERS:
                i += 1
                continue
            m = re.search(r"([\w]+)$", text[:i], re.UNICODE)
            word = m.group(1) if m else ''
            if word.casefold() in ABBR or (len(word) == 1 and word.isalpha()):
                i += 1
                continue
        end = i + 1
        while end < len(text) and text[end] in '.!?…' + CLOSERS:
            end += 1
        # Nhãn lời trích và nghỉ dài thuộc câu trước.
        suffix = re.match(r'\s*(?:\[TRÍCH DỊCH\])?(?:\s*‖)?', text[end:])
        if suffix and suffix.group().strip():
            end += suffix.end()
        if end == len(text) or text[end].isspace():
            out.append(text[start:end].strip())
            start = end
        i = end
    if text[start:].strip():
        out.append(text[start:].strip())
    return out


def convert(md):
    lines = md.splitlines(keepends=True)
    out, paragraph = [], []
    in_chapter = False
    pd = False

    def flush():
        nonlocal pd
        if not paragraph:
            return
        text = ' '.join(x.strip() for x in paragraph)
        paragraph.clear()
        # Marker phải nằm tại ranh giới câu.
        tokens = re.split(r'(\[/?PD\])', text)
        buffer = ''
        for token in tokens:
            if token in ('[PD]', '[/PD]'):
                if buffer.strip():
                    if token == '[PD]' and not buffer.rstrip().endswith(tuple('.!?…' + CLOSERS)):
                        raise ValueError('Marker PD phải nằm ở ranh giới câu')
                    if token == '[/PD]' and not buffer.rstrip().endswith(tuple('.!?…' + CLOSERS)):
                        raise ValueError('Marker PD phải nằm ở ranh giới câu')
                    for sent in split_sentences(buffer):
                        out.append(sent + (' {pd}' if pd else '') + '\n')
                    buffer = ''
                if (token == '[PD]') == pd:
                    raise ValueError('Marker PD lồng nhau hoặc đóng khi chưa mở')
                pd = token == '[PD]'
            else:
                buffer += token
        if buffer.strip():
            for sent in split_sentences(buffer):
                out.append(sent + (' {pd}' if pd else '') + '\n')

    for raw in lines:
        s = raw.strip()
        if CHAPTER.match(s):
            flush()
            if pd:
                raise ValueError('Marker PD chưa đóng trước chương mới')
            in_chapter = True
            out.append(raw)
        elif in_chapter and s.startswith('## '):
            flush()
            if pd:
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
    if pd:
        raise ValueError('Marker PD chưa đóng')
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
