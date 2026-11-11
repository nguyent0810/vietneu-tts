"""Deterministic, in-memory enhancement of planned Long scenes."""
from collections import Counter
import hashlib
import json

IMAGE_TYPES = {"photo", "print", "split"}
CAMS = ("push_in", "pan", "pull_out", "tilt_up", "dolly")
TRANSITIONS = ("dip_black", "whip", "flash_white")


class Director:
    def __init__(self, topic, total_duration=0, existing_panos=0, pano_duration=0):
        self.seed = int(hashlib.sha256(topic.encode('utf-8')).hexdigest()[:8], 16)
        self.index = 0
        self.image_index = 0
        self.cam_index = self.seed % len(CAMS)
        self.last_cam = None
        self.last_image_cam = None
        self.panos = existing_panos
        self.pano_duration = pano_duration
        self.total_duration = total_duration

    def apply(self, scenes, imgs, offset=0, context='', ambience=()):
        context = (context + ' ' + json.dumps(ambience, ensure_ascii=False)).lower()
        for s in scenes:
            typ = s.get('type')
            if typ in IMAGE_TYPES:
                n = self.image_index
                self.image_index += 1
                meta = imgs.get(s.get('img'), {})
                stops = s.get('stops')
                duration = s.get('t1', 0) - s.get('t0', 0)
                # Conversion requires explicit anchors, valid timing and a compatible photo.
                if (typ == 'photo' and not any(k in s for k in ('frame', 'layout', 'focus', 'circles', 'kin', 'zoom', 'reveal', 'move'))
                    and isinstance(meta, dict) and meta.get('h', 0) and meta.get('w', 0) / meta['h'] >= 2
                    and isinstance(stops, list) and len(stops) >= 2 and 8 <= duration <= 20
                    and self.panos < 6 and self.total_duration and self.pano_duration + duration <= self.total_duration * .25
                    and all(isinstance(x.get('at'), (int, float)) and isinstance(x.get('x'), (int, float)) and 0 <= x['x'] <= 1 for x in stops)
                    and all(a['at'] < b['at'] and abs(b['x']-a['x']) * (1080 * meta['w']/meta['h'] - 1920) <= 180 * (b['at']-a['at']) for a,b in zip(stops, stops[1:]))):
                    s['type'] = typ = 'pano'
                    self.panos += 1
                    self.pano_duration += duration
                if typ == 'photo' and offset + s.get('t0', 0) < 120 and 'frame' not in s and 'layout' not in s:
                    s['frame'] = False
                if 'cam' not in s and n % 3 != 2:
                    choices = ('push_in', 'pull_out') if typ == 'pano' else CAMS
                    cam = choices[self.cam_index % len(choices)]
                    for step in range(len(choices)):
                        candidate = choices[(self.cam_index + step) % len(choices)]
                        if candidate != self.last_cam and candidate != self.last_image_cam:
                            cam = candidate
                            break
                    s['cam'] = cam
                    self.cam_index += 1
                if s.get('cam'):
                    self.last_cam = s['cam']
                    self.last_image_cam = s['cam']
                if 'fx' not in s and n % 7 == self.seed % 7:
                    local = context + ' ' + json.dumps(s, ensure_ascii=False).lower()
                    fx = next((effect for words, effect in [
                        (('mưa', 'rain'), 'rain'), (('nến', 'candle'), 'candle_flicker'),
                        (('tuyết', 'snow'), 'snow_ash'), (('lửa', 'cháy', 'fire'), 'embers'),
                        (('sương', 'mist', 'fog'), 'mist_drift'), (('nắng', 'sunlight'), 'god_rays')]
                        if any(word in local for word in words)), 'dust')
                    s['fx'] = fx
                if 'transition_in' not in s and 'tr' not in s:
                    s['transition_in'] = TRANSITIONS[(self.index + self.seed) % len(TRANSITIONS)]
            elif typ in {'kinetic', 'slam', 'question'} and s.get('bg') and 'cam' not in s:
                s['cam'] = 'pan' if self.last_cam == 'push_in' else 'push_in' if self.last_cam == 'pan' else ('push_in', 'pan')[(self.index + self.seed) % 2]
                self.last_cam = s['cam']
            elif s.get('cam'):
                self.last_cam = s['cam']
            self.index += 1
        return scenes


def distribution(scenes):
    images = [s for s in scenes if s.get('type') in IMAGE_TYPES | {'pano'}]
    cams = Counter(s['cam'] for s in images if s.get('cam'))
    seq = [s['cam'] for s in images if s.get('cam')]
    run = longest = 0
    last = None
    for cam in seq:
        run = run + 1 if cam == last else 1
        longest = max(run, longest)
        last = cam
    return {'images': len(images), 'cams': dict(cams), 'cam_pct': 100 * sum(cams.values()) / max(1, len(images)),
            'fx_pct': 100 * sum(bool(s.get('fx')) for s in images) / max(1, len(images)),
            'pano_pct': 100 * sum(s.get('type') == 'pano' for s in scenes) / max(1, len(scenes)), 'longest_run': longest}
