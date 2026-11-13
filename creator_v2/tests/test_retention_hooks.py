from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'motion' / 'stier'), str(ROOT / 'motion'), str(ROOT)]
import build as b


def test_hooks_structure_and_legacy(tmp_path):
    r3 = {'rules': 3}
    assert b.retention_hook_lint(dict(r3), 'new', tmp_path)[0]
    assert b.retention_hook_lint({**r3, 'hooks': ['một']}, 'new', tmp_path)[0]
    assert b.retention_hook_lint({**r3, 'hooks': ['một hai ba bốn năm sáu bảy tám chín mười', 'hai']}, 'new', tmp_path)[0]
    errors, notes = b.retention_hook_lint({**r3, 'hooks': ['Bạn mất tiền', 'Tiền của bạn']}, 'new', tmp_path)
    assert not errors and len(notes) == 2
    p = tmp_path / 'data' / 'long' / '_legacy_topics.json'
    p.parent.mkdir(parents=True)
    p.write_text('["old"]', encoding='utf-8')
    assert b.retention_hook_lint(dict(r3), 'old', tmp_path) == ([], [])


def test_specs_before_rules_3_are_not_blocked(tmp_path):
    # Spec Short đã viết trước #337 (rules 2) không bị chặn hồi tố.
    errors, notes = b.retention_hook_lint({'rules': 2}, 'ck-cu', tmp_path)
    assert errors == [] and notes
    assert b.retention_hook_lint({}, 'ck-cu', tmp_path)[0] == []
