"""Audition plan chapters with hf_voice, isolated from production outputs/cache.

.venv/bin/python tools/tts_sample.py plan.json --only ID --chapters 0 1
CH00 is the opening (or first chapter card); cards are spoken as in production.
"""
import argparse
import copy
import re
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.prose_to_script import chapter_ranges

DEST = ROOT / 'output' / 'cl_staging' / 'long' / 'tts_test'


def chapter_tts(spec, start, end):
    """Rebase all line-indexed voice settings; leave the plan untouched."""
    result = copy.deepcopy(spec)
    result.pop('_line_fingerprints', None)
    for key in ('pauses', 'tempos'):
        if key in spec:
            result[key] = {str(int(k) - start): v for k, v in spec[key].items()
                           if start < int(k) <= end}
    if spec.get('voices') is not None:
        result['voices'] = spec['voices'][start:end]
    if spec.get('alt'):
        result['alt']['lines'] = [int(k) - start for k in spec['alt'].get('lines', [])
                                  if start < int(k) <= end]
    if spec.get('seed') is not None:
        result['seed'] = int(spec['seed']) + start * 10
    return result


@contextmanager
def isolated_cache(voice, cache):
    import hf_asr_check
    previous = voice.CACHE
    previous_asr = hf_asr_check.CACHE
    voice.CACHE = cache
    hf_asr_check.CACHE = cache.parent / 'asr_cache'
    try:
        yield
    finally:
        voice.CACHE = previous
        hf_asr_check.CACHE = previous_asr


def sample(row, chapters, *, voice=None, dest=None, run=None):
    if voice is None:
        import hf_voice as voice
    run = run or subprocess.run
    ident = row['id']
    if not re.fullmatch(r'[A-Za-z0-9_-]+', ident):
        raise ValueError('id không hợp lệ')
    script = row['script']
    ranges = chapter_ranges(script)
    if not chapters or any(n < 0 or n >= len(ranges) for n in chapters):
        raise ValueError(f'Chương không tồn tại; có {len(ranges)} chương (từ CH00)')
    tts = copy.deepcopy(row['tts'])
    if 'voices' in row and 'voices' not in tts:
        tts['voices'] = row['voices']
    if not tts.get('voice'):
        raise ValueError('Plan thiếu tts.voice')
    target_dir = (dest or DEST) / ident
    target_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for number in dict.fromkeys(chapters):
        start, end = ranges[number]
        work = target_dir / '_work' / f'CH{number:02d}'
        work.mkdir(parents=True, exist_ok=True)
        wav = work / 'voice.wav'
        with isolated_cache(voice, work / 'cache'):
            manifest = voice.synth(script[start:end], chapter_tts(tts, start, end), wav)
        if manifest.get('n_failed_qa', 0):
            raise ValueError(f'CH{number:02d}: TTS QA lỗi; xem {wav.with_suffix(".json")}')
        target = target_dir / f'CH{number:02d}.mp3'
        run(['ffmpeg', '-v', 'error', '-y', '-i', str(wav), '-af',
             'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', '48000',
             '-codec:a', 'libmp3lame', str(target)], check=True)
        outputs.append(target)
        print(target)
    return outputs


def main(argv=None):
    import long_script_lint
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('plan', type=Path)
    ap.add_argument('--only', required=True)
    ap.add_argument('--chapters', type=int, nargs='+', required=True)
    args = ap.parse_args(argv)
    row = long_script_lint.load_row(args.plan, args.only)
    sample(row, args.chapters)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
