from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'motion' / 'stier'), str(ROOT / 'motion'), str(ROOT)]
import build as b


def test_hooks_structure_and_legacy(tmp_path):
    assert b.retention_hook_lint({}, 'new', tmp_path)[0]
    assert b.retention_hook_lint({'hooks': ['một']}, 'new', tmp_path)[0]
    assert b.retention_hook_lint({'hooks': ['một hai ba bốn năm sáu bảy tám chín mười', 'hai']}, 'new', tmp_path)[0]
    errors, notes = b.retention_hook_lint({'hooks': ['Bạn mất tiền', 'Tiền của bạn']}, 'new', tmp_path)
    assert not errors and len(notes) == 2
    p = tmp_path / 'data' / 'long' / '_legacy_topics.json'
    p.parent.mkdir(parents=True)
    p.write_text('["old"]', encoding='utf-8')
    assert b.retention_hook_lint({}, 'old', tmp_path) == ([], [])
