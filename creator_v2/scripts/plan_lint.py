"""Kiểm phương án tiêu đề mục 5 plan Long, không truy cập mạng hay ghi data."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def title_options(plan):
    heading = re.search(r'^##\s+5\s*[.)·:-]\s*([^\n]*)', plan, re.M | re.I)
    if not heading:
        return []
    rest = plan[heading.end():]
    next_section = re.search(r'^##\s+', rest, re.M)
    section = rest[:next_section.start()] if next_section else rest
    if not re.search(r'tiêu đề', heading.group(1), re.I):
        subsection = re.search(r'^###\s+[^\n]*tiêu đề[^\n]*', section, re.M | re.I)
        if not subsection:
            return []
        section = section[subsection.end():]
        end = re.search(r'^###\s+', section, re.M)
        section = section[:end.start()] if end else section
    else:
        end = re.search(r'^###\s+[^\n]*thumbnail', section, re.M | re.I)
        if end:
            section = section[:end.start()]
    titles = []
    for line in section.splitlines():
        m = re.match(r'^\s*(?:[-*]|\d+[.)])\s+(.+)', line)
        if not m:
            continue
        value = m.group(1).strip()
        quoted = re.search(r'`([^`]+)`|[“"]([^”"]+)[”"]', value)
        if quoted:
            value = next(x for x in quoted.groups() if x is not None)
        else:
            value = re.split(r'\s+[—–]\s+|\s+\(\d+\s+ký tự', value)[0].strip('* ')
        if value:
            titles.append(value)
    return titles


def check(plan, channel):
    titles = title_options(plan)
    errors = []
    if len(titles) < 3:
        errors.append(f"Mục 5 cần ít nhất 3 phương án tiêu đề; tìm thấy {len(titles)}")
    for title in titles:
        if len(title) > 60:
            errors.append(f"Tiêu đề {len(title)} ký tự (>60): {title}")
    if len(titles) >= 3 and channel.lower() == 'ck':
        money = r'(?:\d|một|hai|ba|bốn|năm|mười|trăm|nghìn|ngàn|triệu|tỷ|tỉ)'
        unit = r'(?:đồng|triệu|tỷ|tỉ|nghìn|ngàn|tiền)'
        time = r'(?:ngày|tuần|tháng|năm|giờ|phút)'
        if not any(re.search(money, t, re.I) and re.search(unit, t, re.I) and re.search(time, t, re.I) for t in titles):
            errors.append('CK cần một tiêu đề khoản tiền + mốc thời gian')
        if not any(re.search(r'\b(?:mất|lỗ|rủi ro|phí|thuế|hòa vốn|lãi|lợi|tiết kiệm|bao nhiêu|bảo vệ|tránh|nhận|được)\b', t, re.I) for t in titles):
            errors.append('CK cần một tiêu đề rủi ro hoặc lợi ích cho người xem')
    if len(titles) >= 3 and channel.lower() == 'mim':
        risk = r'\b(?:bạn|của bạn|người dùng)\b.*\b(?:mất|rủi ro|lộ|bị|nguy cơ|sai|lừa|theo dõi)\b'
        year = r'\b(?:1[89]\d{2}|20\d{2})\b'
        for title in titles:
            if not (re.search(risk, title, re.I) or (re.search(year, title) and len(title.split()) >= 4)):
                errors.append(f'MIM cần người + năm + bước ngoặt hoặc rủi ro người xem: {title}')
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic')
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', args.topic):
        parser.error('topic không hợp lệ')
    root = args.root
    registry = root / 'data' / 'long' / '_legacy_topics.json'
    if registry.exists() and args.topic in json.loads(registry.read_text(encoding='utf-8')):
        print('LEGACY: giữ nguyên kết quả cổng cũ')
        return 0
    try:
        plan = (root / 'data' / 'long' / args.topic / 'plan.md').read_text(encoding='utf-8')
    except OSError as exc:
        print(f'Không kiểm được: {exc}')
        return 2
    channel = 'ck' if args.topic.startswith('ck-') else 'mim' if args.topic.startswith('mim-') else 'cl'
    errors = check(plan, channel)
    for error in errors:
        print('LỖI:', error)
    if not errors:
        print('OK; người duyệt xác nhận ý nghĩa tiêu đề')
    return int(bool(errors))


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(ROOT))
    from factory.console import utf8_console
    utf8_console()
    raise SystemExit(main())
