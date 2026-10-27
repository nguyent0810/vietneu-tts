import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'library/tools/inventory.py'
spec = importlib.util.spec_from_file_location('inventory', MODULE)
inv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inv)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.tax = [
            {'id': 'timeline', 'name_vi': 'Dòng thời gian', 'group': 'canh', 'keywords': ['timeline', 'dòng thời gian']},
            {'id': 'chua_phan_loai', 'name_vi': 'Chưa phân loại', 'group': 'khac', 'keywords': []},
        ]

    def test_tagging_keyword_and_unclassified(self):
        rows = [inv.record('fixture', '1', 'Timeline demo', 'animated timeline'),
                inv.record('fixture', '2', 'No clue', 'a totally unrelated passage')]
        got = inv.tag_records(rows, self.tax)
        self.assertEqual(got[0]['techniques'], ['timeline'])
        self.assertEqual(got[1]['techniques'], ['chua_phan_loai'])

    def test_exact_dedup_by_post_and_normalized_text(self):
        rows = [inv.record('one', 'a', 'A title', 'same text', 'https://twitter.com/foo/status/123456789012'),
                inv.record('two', 'b', 'Other title', 'different', 'https://x.com/foo/status/123456789012'),
                inv.record('one', 'c', 'Hello, WORLD!', 'Text!!!'),
                inv.record('two', 'd', 'hello world', 'text')]
        out = inv.exact_dedup(rows)
        self.assertEqual(len(out), 2)

    def test_near_dedup_jaccard(self):
        base = 'A timeline explains the history of events in chronological order and shows dates.'
        rows = [inv.record('a', '1', 'History timeline', base),
                inv.record('b', '2', 'History timeline', base.replace('shows dates', 'shows the dates')),
                inv.record('c', '3', 'Completely different', 'A recipe for soup with vegetables.')]
        out1 = inv.near_dedup(rows, .8)
        out2 = inv.near_dedup(rows, .8)
        self.assertEqual([r['uid'] for r in out1], [r['uid'] for r in out2])
        self.assertEqual(len(out1), 2)

    def test_adapter_extension_uses_common_record_shape(self):
        # A new source only needs a thin adapter returning shared records.
        def adapt_new_source(data):
            return [inv.record('new_source', x['id'], x['title'], x['prompt'], x.get('url',''), x.get('tags', [])) for x in data]
        rows = adapt_new_source([{'id':'x1','title':'Diagram','prompt':'Node edge graph','tags':['diagram']}])
        self.assertEqual(rows[0]['source'], 'new_source')
        self.assertEqual(set(rows[0]), {'uid','source','source_id','url','post_id','title','text','labels','tools','format','engine_asset'})

    def test_same_input_serializes_identically(self):
        rows = [inv.record('b','2','timeline','timeline chart'), inv.record('a','1','map','animated map')]
        tax = self.tax + [{'id':'map','name_vi':'Bản đồ','group':'canh','keywords':['map']}]
        first = [json.dumps(x, sort_keys=True, ensure_ascii=False) for x in inv.near_dedup(inv.exact_dedup(inv.tag_records(rows,tax)),.8)]
        second = [json.dumps(x, sort_keys=True, ensure_ascii=False) for x in inv.near_dedup(inv.exact_dedup(inv.tag_records(rows,tax)),.8)]
        self.assertEqual(first, second)

    def test_label_map_and_canvas_context(self):
        from unittest.mock import patch
        with patch.object(inv, 'load_map', return_value={'fixture': {'motion graphics ui': ['ui_mockup']}}):
            row = inv.record('fixture', 'x', 'Canvas', 'A canvas element appears in a page.', labels=['motion graphics ui'])
            tagged = inv.tag_records([row], self.tax + [
                {'id':'canvas_drawing','name_vi':'Canvas','group':'style','keywords':['canvas drawing','canvas']},
                {'id':'ui_mockup','name_vi':'UI','group':'template','keywords':[]},
            ])[0]
        self.assertIn('ui_mockup', tagged['techniques'])
        self.assertNotIn('canvas_drawing', tagged['techniques'])

    def test_empty_short_text_is_insufficient(self):
        row = inv.record('fixture', 'empty', '', '')
        self.assertEqual(inv.tag_records([row], self.tax)[0]['techniques'], ['thieu_du_lieu'])

    def test_engine_has_three_availability_states(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            asset = root / 'asset.html'; asset.write_text('effect')
            usage = root / 'render.html'; usage.write_text('asset.html asset.html')
            with patch.object(inv, 'ROOT', root), patch.object(inv, 'USAGE_ROOT', root), patch.object(inv, 'load_map', return_value={'asset.html':['timeline']}):
                inv.engine_status.cache_clear()
                self.assertEqual(inv.engine_status('missing')['status'], 'chua_co')
                self.assertEqual(inv.engine_status('timeline')['status'], 'co_san')
                # Usage scanning is restricted to project output roots.
                (root/'hyperframes_short/compositions').mkdir(parents=True)
                (root/'hyperframes_short/compositions/_render.html').write_text('asset.html')
                inv.engine_status.cache_clear()
                self.assertEqual(inv.engine_status('timeline')['status'], 'dung_that')

    def test_usage_root_scans_render_html_and_plan(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'asset.html').write_text('template')
            (root/'output/cl_staging').mkdir(parents=True)
            (root/'output/cl_staging/_r_example.html').write_text('asset.html')
            (root/'output/cl_staging/plan_example.json').write_text('{"style":"look"}')
            with patch.object(inv, 'ROOT', root), patch.object(inv, 'USAGE_ROOT', root), patch.object(inv, 'load_map', return_value={'asset.html':['timeline'], 'bridge_style:look':['timeline']}):
                inv.engine_status.cache_clear()
                found = inv.engine_status('timeline')['evidence']
                self.assertEqual(inv.engine_status('timeline')['status'], 'dung_that')
                self.assertTrue(any(x['path'].endswith('_r_example.html') for x in found))

    def test_stoplist_is_loaded_for_residual_vocabulary(self):
        words = inv.load_map('stopwords.json')['words']
        self.assertTrue({'prompt', 'stated', 'inputs', 'result', 'evidence', 'verification', 'repository', 'preview'}.issubset(set(words)))


if __name__ == '__main__':
    unittest.main()
