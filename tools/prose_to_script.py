"""Long prose.md -> one complete sentence per TTS line, without rewriting.

Usage: .venv/bin/python tools/prose_to_script.py prose.md script.txt
Only ## headings become chapter cards; a # document title is not narration.
Sources and visual directions belong in separate notes.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import long_script_lint as lint
from tools.prose_split import split_sentences
from tools.long_plan_build import is_heading


def convert(md):
    out, paragraph = [], []

    def flush():
        if paragraph:
            out.extend(split_sentences(' '.join(paragraph)))
            paragraph.clear()

    for raw in md.splitlines():
        line = raw.strip()
        if line.startswith('## '):
            flush()
            out.append('**' + line[3:].strip() + '**')
        elif line.startswith('# ') or not line or line == '---':
            flush()
        else:
            paragraph.append(line)
    flush()
    return '\n'.join(out) + ('\n' if out else '')


def chapter_ranges(script):
    """Zero-based CH00… ranges, including spoken chapter cards.

    An unheaded opening is CH00. A first-line heading starts CH00 directly.
    """
    starts = [i for i, text in enumerate(script) if is_heading(text)]
    if script and (not starts or starts[0] != 0):
        starts.insert(0, 0)
    return list(zip(starts, starts[1:] + [len(script)]))


def statistics(script):
    out = []
    for number, (start, end) in enumerate(chapter_ranges(script)):
        lines = [t for t in script[start:end] if not is_heading(t)]
        counts = [lint.syllables(t) for t in lines]
        out.append(f'CH{number:02d}: {len(lines)} câu, {sum(counts)} tiếng đọc, '
                   f'câu dài nhất {max(counts, default=0)} tiếng đọc')
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path)
    ap.add_argument('output', type=Path)
    args = ap.parse_args(argv)
    result = convert(args.input.read_text(encoding='utf-8'))
    args.output.write_text(result, encoding='utf-8')
    script = result.splitlines()
    for line in statistics(script):
        print(line)
    report = lint.lint({'id': args.output.stem, 'script': script})
    print(lint.render_text(report))
    return int(any(level == lint.ERROR for level, *_ in report['issues']))


if __name__ == '__main__':
    raise SystemExit(main())
