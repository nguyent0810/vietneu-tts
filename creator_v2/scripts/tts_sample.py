"""Đọc thử từng câu, chỉ ghi vào output/long/<topic>/tts_test."""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'motion' / 'long'))
import script_lines
from scripts.prose_to_script import parse_chapters
from factory import speak


def pause_seconds(line):
    text = line if isinstance(line, str) else line['t']
    text = text.rstrip().rstrip('"”’»\')]}').rstrip()
    base = {'?': .6, '!': .5, '…': .7, '.': .55}.get(text[-1:] , .55)
    # parse chuyển ‖ thành p=1.0; nghỉ tiêu đề 0.8 không phải ‖.
    return base + (.6 if isinstance(line, dict) and line.get('p') == script_lines.LONG_PAUSE else 0)


def synthesize_chapter(chapter, engine, voice):
    import numpy as np
    chunks = []
    for line in chapter['lines']:
        text = line if isinstance(line, str) else line['t']
        audio = np.asarray(engine.infer(text, voice=voice), dtype=np.float32)
        if audio.ndim != 1 or not audio.size or not np.isfinite(audio).all():
            raise ValueError('Engine trả âm thanh rỗng, không hữu hạn hoặc không phải mono')
        chunks.extend((audio, np.zeros(round(pause_seconds(line) * speak.SAMPLE_RATE), dtype=np.float32)))
    if not chunks:
        raise ValueError('Chương rỗng')
    return np.concatenate(chunks)


def main():
    from factory.console import utf8_console
    utf8_console()
    ap = argparse.ArgumentParser()
    ap.add_argument('topic')
    ap.add_argument('script', type=Path)
    ap.add_argument('chapters', nargs='+')
    ap.add_argument('--voice')
    args = ap.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.topic):
        ap.error('topic không hợp lệ')
    if any(not re.fullmatch(r'CH[0-9]{2}', name, re.I) for name in args.chapters):
        ap.error('tên chương phải có dạng CHNN')
    spec = json.loads((ROOT / 'data' / 'long' / args.topic / 'spec.json').read_text(encoding='utf-8'))
    import build_long
    profile = build_long._channels()[spec['channel']]
    voice = args.voice or profile['voice']
    fx = profile.get('voice_fx', build_long.VOICE_FX) if spec.get('master', True) else ''
    chs = {c['name']: c for c in parse_chapters(args.script.read_text(encoding='utf-8'))}
    names = [name.lower() for name in args.chapters]
    missing = [n for n in names if n not in chs]
    if missing:
        raise SystemExit('Không có chương: ' + ', '.join(missing))
    import soundfile as sf
    engine = speak._load_engine()
    dest = ROOT / 'output' / 'long' / args.topic / 'tts_test'
    dest.mkdir(parents=True, exist_ok=True)
    for name in names:
        audio = synthesize_chapter(chs[name], engine, voice)
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / 'voice.wav'
            sf.write(str(wav), audio, speak.SAMPLE_RATE)
            target = dest / (name.upper() + '.mp3')
            filters = ','.join(x for x in (fx, 'loudnorm=I=-16:TP=-1.5:LRA=11') if x)
            subprocess.run([build_long.FFMPEG, '-v', 'error', '-y', '-i', str(wav), '-af', filters,
                            '-ar', '48000', '-codec:a', 'libmp3lame', str(target)], check=True)
        print(target)


if __name__ == '__main__':
    main()
