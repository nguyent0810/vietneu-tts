from scripts import plan_lint as pl


def test_ck_titles_and_length():
    plan = "## 5. Tiêu đề và Thumbnail\n### 3 phương án tiêu đề\n1. `100 triệu sau 5 năm`\n2. `Bạn mất bao nhiêu phí?`\n3. `Tiền của bạn đi đâu?`\n### Thumbnail\n- `Không phải tiêu đề`\n## 6. Khác\n"
    assert pl.check(plan, 'ck') == []
    assert len(pl.title_options(plan)) == 3
    assert any('60' in e for e in pl.check(plan.replace('Tiền của bạn đi đâu?', 'x' * 61), 'ck'))
    assert any('mốc thời gian' in e for e in pl.check(plan.replace('100 triệu sau 5 năm', 'Mở tài khoản'), 'ck'))


def test_missing_wrong_section_and_mim():
    assert pl.check('## 5. Dàn ý\n1. `Không phải tiêu đề`', 'cl')
    good = '## 5. Tiêu đề\n1. `Alan Turing 1950 thay đổi máy tính`\n2. `Bạn bị lộ dữ liệu`\n3. `Ada Lovelace 1843 viết thuật toán`'
    assert pl.check(good, 'mim') == []
    assert pl.check(good.replace('Bạn bị lộ dữ liệu', 'Máy tính biết nghĩ'), 'mim')


def test_legacy_short_circuits(tmp_path, capsys):
    p = tmp_path / 'data' / 'long' / '_legacy_topics.json'
    p.parent.mkdir(parents=True)
    p.write_text('["old"]', encoding='utf-8')
    assert pl.main(['old', '--root', str(tmp_path)]) == 0
    assert 'LEGACY' in capsys.readouterr().out
