"""Read-only ticket 151 sample measurement; local plans only, no APIs/rendering."""
from __future__ import annotations
import argparse
import copy
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import hf_batch_render as HBR
from tools import visual_mix as VM
from tools.long_text_rotation import inventory
from tools.long_media_mix import enrich_stock


def audit(path):
    data = json.loads(path.read_text())
    rows = data if isinstance(data, list) else data.get('videos', [data])
    out = []
    for row in rows:
        if row.get('series') not in {'fs', 'bud'}:
            continue
        timing = 'ước 185 tiếng/phút + .5s nghỉ; không pixel audit'
        segs = None
        manifest = path.parent / 'out' / (row['id'] + '.json')
        if manifest.is_file():
            from tools.visual_mix_audit import Audit
            probe = Audit(path.parent, '2026-11-25', 1)
            _, data, mismatches = probe.manifest(row, path.parent / 'out')
            if not mismatches:
                segs = data['segments']
                timing = 'TTS segments đối chiếu đúng script; không pixel audit'
        counts, _ = inventory(row)
        out.append({'id': row['id'], 'file': str(path), 'mtime': path.stat().st_mtime,
                    'day': row.get('day'), 'timing': timing,
                    'metrics': VM.measure(HBR.visual_mix_scenes(row, segs)), 'text_effects': dict(counts)})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data-root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    folder = args.data_root / 'output/cl_staging/long'
    canonical = [p for p in folder.glob('plan*.json') if '.' not in p.stem]
    candidates = []
    for p in canonical:
        for record in audit(p):
            candidates.append((p.stat().st_mtime, p, record['id']))
    chosen, seen = [folder / 'plan_L_fs_484_L03.json'], {'L_fs_484_L03'}
    for _, p, ident in sorted(candidates, key=lambda x: (x[0], x[2]), reverse=True):
        if ident in seen:
            continue
        chosen.append(p)
        seen.add(ident)
        if len(chosen) == 4:
            break
    result = {'selection': 'L03 + 3 canonical FS/BUD plans with newest filesystem mtime; scheduled dates may be future',
              'samples': [item for p in chosen for item in audit(p)]}
    path = folder / 'plan_L_fs_d25_1965.json'
    data = json.loads(path.read_text()); original = data[0] if isinstance(data, list) else data
    from library.tools.plan_enrich import line_spans
    trial = copy.deepcopy(original)
    enrich_stock(trial, 'fs', line_spans(trial)[0], project_root=args.data_root)
    added = set(trial.get('media', {})) - set(original.get('media', {}))
    result['1965'] = {'new_stock_sentences': sorted(added, key=int),
                       'ai_images_replaced': trial['media_mix_report']['ai_images_saved'],
                       'reason': '151b: only documented character-free stills; protected media preserved',
                       'report': trial.get('media_mix_report')}
    # Rebuild-stage counterfactual only, not an edited production plan.
    fresh = copy.deepcopy(original); fresh['media'] = {}
    enrich_stock(fresh, 'fs', line_spans(fresh)[0], project_root=args.data_root)
    result['1965']['before_media_assignment'] = fresh.get('media_mix_report')
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    for item in result['samples']:
        print(item['id'], {k: round(v['share']*100,2) for k,v in item['metrics']['by_source'].items()}, item['text_effects'])
    print('1965', result['1965'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
