import unittest
from pathlib import Path
from unittest.mock import patch
from motion.long import cadence

class CadenceTests(unittest.TestCase):
    def setUp(self):
        self.out = Path('fake-output')
        self.files = {}
        self.is_file = patch.object(Path, 'is_file', lambda path: str(path) in self.files)
        self.read = patch.object(cadence, 'read', lambda path: self.files[str(path)])
        self.is_file.start(); self.read.start()
        self.addCleanup(self.is_file.stop); self.addCleanup(self.read.stop)
    def metadata(self, name, data):
        self.files[str(self.out / 'img' / (name + '.json'))] = data
    def timing(self):
        self.files[str(self.out / 'ch00' / 'timing.json')] = {'duration': 12, 'segments': [
            {'text': 'one two', 'start': 0, 'end': 5}, {'text': 'three four', 'start': 6, 'end': 11}]}
    def test_scene_count_and_real_timing(self):
        self.timing()
        result = cadence.measure_chapter('ch00', {'scenes': [{'type': 'chapter'}, {'type': 'question', 'at': 1}]}, self.out, {})
        self.assertEqual(result['changes'], 2)
        self.assertEqual(result['duration_s'], 12)
        self.assertTrue(result['warning'])
        self.assertIn('timing.json', result['duration_source'])
    def test_timed_steps_and_simultaneous_events(self):
        self.timing()
        ch = {'scenes': [{'type': 'ledger', 'rows': [{}, {}, {}]},
                         {'type': 'map', 'at': 1, 'pins': [{'at': [1, 'four']}], 'routes': [{'at': [1, 'four']}]}]}
        result = cadence.measure_chapter('ch00', ch, self.out, {})
        self.assertEqual(result['changes'], 6)
        self.assertAlmostEqual(result['longest_gap']['seconds'], 4.4)
    def test_groups_and_unknown(self):
        self.metadata('real', {'file': 'source'})
        self.metadata('ai', {'ai_generated': True})
        self.metadata('rebuild', {'asset_id': 'id', 'tags': ['tai_dung']})
        for scene, expected in [({'img': 'real'}, 'A'), ({'img': 'ai'}, 'AI'), ({'img': 'rebuild'}, 'B'),
                                ({'img': 'missing'}, 'UNKNOWN'), ({'type': 'map'}, 'D'), ({'vid': '123', 'img': 'real'}, 'broll')]:
            self.assertEqual(cadence.classify(scene, self.out/'img', {}), expected)
    def test_150_second_fallback(self):
        result = cadence.measure_chapter('ch00', {'lines': ['one', 'two'], 'scenes': [{'type': 'chapter'}, {'type': 'question', 'at': 1}]}, self.out, {})
        self.assertEqual(result['duration_s'], 150)
        self.assertIn('estimated', result['duration_source'])
    def test_planned_timing(self):
        self.timing()
        path = self.out / 'ch00' / 'data.js'
        self.files[str(path)] = True
        with patch.object(Path, 'read_text', return_value='CASE = {"scenes":[{"type":"ledger","t0":0,"t1":10,"rows":[{"at":2},{"at":7}]}]};'):
            result = cadence.measure_chapter('ch00', {'scenes': []}, self.out, {})
        self.assertEqual(result['changes'], 3)
        self.assertEqual(result['duration_s'], 10)
        self.assertIn('data.js', result['duration_source'])

if __name__ == '__main__': unittest.main()
