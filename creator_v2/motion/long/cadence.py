"""Measure declared visual changes, without rendering or claiming visual QA.

Each scene start counts once. Timed rows, pins, routes, timeline points and
other item sequences with explicit build_long.plan timing count once per
unique instant strictly inside the scene; simultaneous events count once.
Continuous pans/zooms and split images shown together do not count as cuts.
A b-roll scene takes precedence; image metadata decides A/B/C/AI, otherwise
an unverified image is UNKNOWN. Non-image scenes are D. Durations are assigned
to one group per scene; mixed image scenes with ambiguous provenance are UNKNOWN.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GROUPS = ('A', 'B', 'C', 'AI', 'D', 'broll', 'UNKNOWN')
SERIES = {'ledger': ('rows', .6, .5), 'file': ('rows', .9, .5),
          'timeline': ('items', .3, .5), 'map': ('pins', .5, .35),
          'bars': ('items', .4, .35), 'org': ('nodes', .3, .3),
          'kinetic': ('items', .2, .4), 'board': ('pins', .3, .45),
          'memorial': ('names', .8, .7), 'sticker': ('items', .4, .7),
          'pizzini': ('notes', .5, 1.2), 'dots': ('groups', 1.8, 1.2)}

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def text(line):
    return line.get('t', '') if isinstance(line, dict) else line

def estimated_lines(ch, duration=150.0):
    lines = ch.get('lines', [])
    weights = [max(1, len(text(x).split())) for x in lines]
    total = sum(weights) or 1
    current = 0.0
    result = []
    for line, weight in zip(lines, weights):
        end = current + duration * weight / total
        result.append({'text': text(line), 'start': current, 'end': end})
        current = end
    return result

def anchor(value, lines):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        index = int(value)
        if value != index or index < 0 or index >= len(lines):
            raise ValueError('invalid line anchor: %r' % value)
        return float(lines[index]['start'])
    if isinstance(value, list) and value:
        index = int(value[0]); line = lines[index]
        if len(value) < 2:
            return float(line['start'])
        words = line['text'].split()
        needle = str(value[1]).casefold()
        matches = [i for i, word in enumerate(words) if needle in word.casefold()]
        if not matches:
            raise ValueError('word anchor not found: %r' % value)
        return line['start'] + (line['end'] - line['start']) * matches[0] / max(len(words), 1)
    raise ValueError('invalid anchor: %r' % (value,))

def refs(scene):
    found = []
    for key in ('img', 'bg'):
        if isinstance(scene.get(key), str) and scene[key]:
            found.append(scene[key])
    for key in ('a', 'b'):
        value = scene.get(key)
        if isinstance(value, dict) and isinstance(value.get('img'), str):
            found.append(value['img'])
    return found

def classify(scene, img_dir, images):
    if scene.get('vid') or scene.get('type') == 'broll':
        return 'broll'
    image_refs = refs(scene)
    if not image_refs:
        return 'D'
    groups = set()
    for ref in image_refs:
        meta_path = img_dir / (ref + '.json')
        meta = read(meta_path) if meta_path.is_file() else {}
        spec = images.get(ref, {})
        spec = spec if isinstance(spec, dict) else {}
        ai = bool(meta.get('ai_generated') or meta.get('asset_id') or spec.get('ai_generated') or spec.get('asset_id') or scene.get('ai_generated') or scene.get('asset_id'))
        if ai:
            tags = ' '.join(str(x) for x in (meta.get('tag', ''), meta.get('tags', ''), spec.get('tag', ''), spec.get('tags', ''), scene.get('tag', ''))).lower()
            group = 'B' if 'tai_dung' in tags else 'C' if 'khai_niem' in tags else 'AI'
        elif meta_path.is_file() and meta and any(meta.get(k) for k in ('source', 'url', 'src', 'file', 'title', 'author', 'license')):
            group = 'A'
        else:
            group = 'UNKNOWN'
        groups.add(group)
    return next(iter(groups)) if len(groups) == 1 else 'UNKNOWN'

def subevents(scene, start, end, lines, planned=False):
    events = []
    def add(value, default):
        if value is None:
            t = default
        elif planned and isinstance(value, (int, float)):
            t = float(value)
        else:
            t = anchor(value, lines)
        if start < t < end:
            events.append(round(t, 6))
    typ = scene.get('type')
    series = []
    if typ in SERIES:
        series.append(SERIES[typ])
    if typ == 'board': series.append(('links', .6, .45))
    if typ == 'map': series.append(('routes', None, 0))
    if scene.get('kin') and typ != 'kinetic': series.append(('kin', .2, .4))
    if typ == 'print' and isinstance(scene.get('side'), dict):
        for i, item in enumerate(scene['side'].get('lines', [])):
            if isinstance(item, dict): add(item.get('at'), start + .8 + .6 * i)
    for key, offset, step in series:
        for i, item in enumerate(scene.get(key) or []):
            if not isinstance(item, dict): continue
            if offset is None and 'at' not in item: continue
            add(item.get('at'), start + (offset or 0) + step * i)
    return sorted(set(events))

def measure_chapter(name, ch, output, images):
    timing_path = output / name / 'timing.json'
    data_path = output / name / 'data.js'
    planned = None
    if data_path.is_file():
        raw = data_path.read_text(encoding='utf-8')
        try:
            planned = json.loads(raw.split('=', 1)[1].strip().rstrip(';'))
        except (ValueError, IndexError):
            planned = None
    if planned and planned.get('scenes') and all(isinstance(s.get('t0'), (int, float)) and isinstance(s.get('t1'), (int, float)) for s in planned['scenes']):
        scenes = planned['scenes']
        lines = read(timing_path).get('segments', []) if timing_path.is_file() else []
        duration = max(s['t1'] for s in scenes)
        source = 'data.js (planned scene timing)'
        is_planned = True
    else:
        scenes = ch.get('scenes') or []
        if timing_path.is_file():
            timing = read(timing_path); lines = timing['segments']; duration = float(timing['duration'])
            source = 'timing.json (word anchors interpolated)'
        else:
            duration = 150.0
            lines = estimated_lines(ch, duration)
            source = 'estimated 150 s/chapter (build_long fallback; word-weighted anchors)'
        starts = [0.0] + [anchor(s['at'], lines) for s in scenes[1:]] if scenes else []
        scenes = [dict(s, t0=start, t1=(starts[i+1] if i+1 < len(starts) else duration)) for i, (s, start) in enumerate(zip(scenes, starts))]
        is_planned = False
    counts = 0; longest = {'seconds': 0.0, 'scene': None}; seconds = dict.fromkeys(GROUPS, 0.0)
    for i, s in enumerate(scenes):
        start, end = float(s['t0']), float(s['t1'])
        if end <= start: raise ValueError('%s scene %d has non-positive duration' % (name, i))
        seconds[classify(s, output / 'img', images)] += end-start
        points = [start] + subevents(s, start, end, lines, is_planned) + [end]
        counts += len(points)-1
        gap = max(b-a for a, b in zip(points, points[1:]))
        if gap > longest['seconds']: longest = {'seconds': gap, 'scene': '%s#%d (%s)' % (name, i, s.get('type', '?'))}
    measured = sum(seconds.values())
    avg = measured / counts if counts else None
    return {'chapter': name, 'duration_source': source, 'duration_s': measured, 'changes': counts,
            'seconds_per_change': avg, 'longest_gap': longest,
            'group_seconds': seconds, 'group_percent': {k: 100*v/measured if measured else 0 for k,v in seconds.items()},
            'warning': bool((avg is not None and avg > 5) or longest['seconds'] > 8)}

def analyse(topic_dir, output):
    paths = sorted(topic_dir.glob('ch*.json'))
    if not paths: raise ValueError('no ch*.json in %s' % topic_dir)
    spec_path = topic_dir / 'spec.json'
    spec = read(spec_path) if spec_path.is_file() else {}
    chapters = [measure_chapter(p.stem, read(p), output, spec.get('imgs') or {}) for p in paths]
    seconds = {k: sum(ch['group_seconds'][k] for ch in chapters) for k in GROUPS}
    duration = sum(seconds.values()); changes = sum(ch['changes'] for ch in chapters)
    longest = max((ch['longest_gap'] for ch in chapters), key=lambda x:x['seconds'])
    total = {'duration_s': duration, 'changes': changes, 'seconds_per_change': duration/changes if changes else None,
             'longest_gap': longest, 'group_seconds': seconds,
             'group_percent': {k: 100*v/duration if duration else 0 for k,v in seconds.items()},
             'warning': any(ch['warning'] for ch in chapters)}
    return {'topic': topic_dir.name, 'chapters': chapters, 'total': total}

def main():
    sys.path.insert(0, str(ROOT))
    from factory.console import utf8_console
    utf8_console()  # console Windows cp1252 không in được tiếng Việt
    parser = argparse.ArgumentParser(); parser.add_argument('topic'); parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    if Path(args.topic).name != args.topic or args.topic in ('.', '..'):
        parser.error('topic must be a directory name')
    try: result = analyse(ROOT / 'data' / 'long' / args.topic, ROOT / 'output' / 'long' / args.topic)
    except (ValueError, OSError, KeyError, IndexError, TypeError) as exc:
        print('Error: %s' % exc, file=sys.stderr); return 1
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    for item in result['chapters'] + [dict(result['total'], chapter='TOTAL')]:
        avg = item['seconds_per_change']
        print('%s: %d changes, %s s/change, max %.2f s (%s)%s' % (item['chapter'], item['changes'], ('%.2f' % avg if avg is not None else 'n/a'), item['longest_gap']['seconds'], item['longest_gap']['scene'], ' | C\u1ea2NH B\u00c1O' if item['warning'] else ''))
        print('  ' + ', '.join('%s %.1f%%' % (k, v) for k,v in item['group_percent'].items()))
        if 'duration_source' in item: print('  ' + item['duration_source'])
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
