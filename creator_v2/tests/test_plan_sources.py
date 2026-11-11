import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

import pytest

from scripts import plan_sources as sources

SAMPLE = Path('docs/pm/tickets/GH-291-sample-plan.md')


def test_sample_plan_error_page_and_missing_number(monkeypatch):
    plan = SAMPLE.read_text(encoding='utf-8')
    lines = plan.splitlines()
    line = next(line for line in lines if 'tapchikinhtetaichinh.vn/' in line)
    plan = line + ' 14.384.902'
    def fetch(url):
        if 'tapchikinhtetaichinh.vn/' in url:
            return '<html><title>Trang báo lỗi</title></html>'
        return '<html><body>Không có số được dẫn.</body></html>'
    monkeypatch.setattr(sources, 'fetch', fetch)
    rows = sources.run(plan)
    assert rows[0][1] == 'TRANG_LOI'
    assert rows[1][1] == 'KHONG_CHUA_SO'
    assert '14.384.902' in rows[1][3]


@pytest.mark.parametrize(('code', 'expected'), [(403, 'CHAN'), (429, 'CHAN'), (404, 'HTTP 404'), (500, 'HTTP 500')])
def test_http_status(monkeypatch, code, expected):
    def fetch(url):
        raise HTTPError(url, code, 'error', None, None)
    monkeypatch.setattr(sources, 'fetch', fetch)
    assert sources.check_url('https://example.test', set())[0] == expected


def test_visible_numbers_and_unavailable(monkeypatch):
    monkeypatch.setattr(sources, 'fetch', lambda url: '<script>14.384.902</script><p>14,384,902</p>')
    assert sources.check_url('https://example.test', {'14.384.902'})[0] == 'OK'
    monkeypatch.setattr(sources, 'fetch', lambda url: '<script>14.384.902</script><p>Khác</p>')
    assert sources.check_url('https://example.test', {'14.384.902'})[0] == 'KHONG_CHUA_SO'
    def offline(url):
        raise URLError('offline')
    monkeypatch.setattr(sources, 'fetch', offline)
    assert sources.check_url('https://example.test', set())[0] == 'KHONG_MO_DUOC'


def test_commons_counts_paginated_unique_files_and_one_child_level(monkeypatch):
    calls = []
    def fetch(url):
        if not url.startswith(sources.API):
            return '<p>Ảnh tư liệu</p>'
        params = parse_qs(urlsplit(url).query)
        calls.append(params)
        title = params['cmtitle'][0]
        if title == 'Category:Example' and 'cmcontinue' not in params:
            data = {'query': {'categorymembers': [{'pageid': 1, 'ns': 6}, {'title': 'Category:Child', 'ns': 14}]},
                    'continue': {'continue': '-||', 'cmcontinue': 'next'}}
        elif title == 'Category:Example':
            data = {'query': {'categorymembers': [{'pageid': 2, 'ns': 6}]}}
        else:
            data = {'query': {'categorymembers': [{'pageid': 2, 'ns': 6}, {'pageid': 3, 'ns': 6},
                                                    {'title': 'Category:Grandchild', 'ns': 14}]}}
        return json.dumps(data)
    monkeypatch.setattr(sources, 'fetch', fetch)
    rows = sources.run('Ảnh: https://commons.wikimedia.org/wiki/Category:Example')
    assert rows[0][1:3] == ('OK', '3')
    assert [c['cmtitle'][0] for c in calls] == ['Category:Example', 'Category:Example', 'Category:Child']
    assert all(c['cmtype'] == ['file|subcat'] for c in calls)


def test_write_and_exit_code_preserve_and_do_not_recheck_report(tmp_path, monkeypatch, capsys):
    topic = tmp_path / 'data' / 'long' / 'demo'
    topic.mkdir(parents=True)
    plan = '# Plan\n- 14.384.902: https://example.test/article\n'
    path = topic / 'plan.md'
    path.write_text(plan, encoding='utf-8')
    monkeypatch.setattr(sources, 'ROOT', tmp_path)
    monkeypatch.setattr(sources, 'fetch', lambda url: '<p>Thiếu số</p>')
    assert sources.main(['demo', '--write']) == 1
    assert path.read_text(encoding='utf-8').endswith(plan)
    assert sources.main(['demo', '--write']) == 1
    result = path.read_text(encoding='utf-8')
    assert result.count('<!-- plan-sources:start -->') == 2
    assert result.endswith(plan)
    assert len(sources.extract_sources(result)) == 1
    assert 'KHONG_CHUA_SO' in capsys.readouterr().out


def test_request_user_agent_and_timeout(monkeypatch):
    class Response:
        headers = type('Headers', (), {'get_content_charset': lambda self: 'utf-8'})()
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return b'content'
    def fake_urlopen(request, timeout):
        assert request.get_header('User-agent') == 'creator-plan-check/1.0'
        assert timeout == 20
        return Response()
    monkeypatch.setattr(sources, 'urlopen', fake_urlopen)
    assert sources.fetch('https://example.test') == 'content'
