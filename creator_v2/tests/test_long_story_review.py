import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import long_story_review as review


def response(status='SUCCESS', text='Bản review'):
    return json.dumps({'event': 'result', 'result': {'status': status, 'response': text}}, ensure_ascii=False)


def test_prompt_template_context_and_factcheck_limit(tmp_path):
    template = tmp_path / 'prompt.md'
    template.write_text('```text\nNguyên văn prompt.\n```\n', encoding='utf-8')
    chs = [{'name': 'ch01', 'title': 'Trước', 'lines': ['Câu trước.']},
           {'name': 'ch02', 'title': 'Giữa', 'lines': [{'t': 'Lời một.'}, 'Lời hai.']},
           {'name': 'ch03', 'title': 'Sau', 'lines': ['Câu sau.']}]
    prompt = review.make_prompt(chs, 1, 'x' * 12000 + 'SENTINEL', template)
    assert prompt.startswith('Nguyên văn prompt.\n')
    assert all(s in prompt for s in ('CH02 · Giữa', 'Câu trước.', 'Câu sau.', '0. Lời một.',
                                      '1. Lời hai.', 'Review', 'Bản viết lại', 'Cần xác minh'))
    assert 'x' * 12000 in prompt and 'SENTINEL' not in prompt


def test_fallback_from_local_to_grok(monkeypatch):
    calls = []
    def run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        if cmd[0] == 'ssh':
            return SimpleNamespace(returncode=1, stdout='', stderr='')
        if cmd[0] == 'agy':
            return SimpleNamespace(returncode=0, stdout=response(text='  '), stderr='')
        return SimpleNamespace(returncode=0, stdout='Review Grok', stderr='')
    monkeypatch.setattr(review.subprocess, 'run', run)
    assert review.review('Xin chào', 'local') == ('grok', 'Review Grok')
    assert [call[0][0] for call in calls] == ['agy', 'grok']
    for _, kwargs in calls[:1]:
        payload = json.loads(kwargs['input'])
        assert payload == {'event': 'user', 'message': {'role': 'user', 'content': review.NO_SHELL + '\n\nXin chào'}}
        assert kwargs['input'].count('\n') == 1
    assert calls[1][1]['input'] == 'Xin chào'


def test_last_result_from_local(monkeypatch):
    calls = []
    def run(cmd, **kwargs):
        calls.append(cmd)
        if cmd[0] == 'ssh':
            raise OSError('offline')
        return SimpleNamespace(returncode=0, stdout=response(text='cũ') + '\n' + response(text='mới'), stderr='')
    monkeypatch.setattr(review.subprocess, 'run', run)
    assert review.review('prompt', 'local') == ('local', 'mới')
    assert len(calls) == 1


def test_dry_run_never_calls_agent_and_real_review_metadata(tmp_path, monkeypatch):
    root = tmp_path
    directory = root / 'data' / 'long' / 'demo'
    directory.mkdir(parents=True)
    (directory / 'script.md').write_text('## CH01 · Tên\nMột câu.\n', encoding='utf-8')
    (directory / 'factcheck.md').write_text('Tư liệu', encoding='utf-8')
    monkeypatch.setattr(review, 'ROOT', root)
    monkeypatch.setattr(review.subprocess, 'run', lambda *a, **k: pytest.fail('agent called'))
    review.main(['demo', 'ch01', '--dry-run'])
    assert 'Một câu.' in (directory / 'story_review' / 'ch01.prompt.md').read_text(encoding='utf-8')
    monkeypatch.setattr(review, 'review', lambda *a: ('local', 'Review kết quả'))
    review.main(['demo', 'ch01'])
    text = (directory / 'story_review' / 'ch01.md').read_text(encoding='utf-8')
    assert text.startswith('Agent: local\nModel: gemini-4-argon-high\nNgày: ')
    assert 'Review kết quả' in text


@pytest.mark.parametrize('agent', ['c', 'local'])
@pytest.mark.parametrize('status', ['SUCCESS', 'ERROR'])
def test_ask_no_shell_and_denied_actions(monkeypatch, agent, status):
    calls = []
    def run(cmd, **kwargs):
        calls.append(json.loads(kwargs['input']))
        event = {'event': 'result', 'result': {'status': status, 'response': '',
                                                 'denied_actions': [{'action': 'run_command'}]}}
        return SimpleNamespace(returncode=0, stdout=json.dumps(event), stderr='')
    monkeypatch.setattr(review.subprocess, 'run', run)
    with pytest.raises(RuntimeError, match='run_command'):
        review.ask(agent, 'Kiểm nguồn')
    assert calls[0]['message']['content'] == review.NO_SHELL + '\n\nKiểm nguồn'


def test_review_reports_denied_action_when_fallbacks_fail(monkeypatch):
    def fail(agent, prompt):
        raise RuntimeError('bị từ chối action: run_command')
    monkeypatch.setattr(review, 'run_agent', fail)
    with pytest.raises(RuntimeError, match='run_command'):
        review.review('Tra nguồn', 'local')
