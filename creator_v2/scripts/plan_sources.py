"""Kiểm URL và đếm file Commons trong plan Long; kết quả không thay thế factcheck."""
import argparse
from datetime import date
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, unquote, urlencode, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

USER_AGENT = "creator-plan-check/1.0"
URL_RE = re.compile(r"https?://[^\s<>`\"'|]+")
NUMBER_RE = re.compile(r"(?<![\w])\d+(?:[.,]\d+)*(?![\w])")
ERROR_RE = re.compile(r"trang\s+báo\s+lỗi|không\s+tìm\s+thấy|\b404\b|page\s+not\s+found|\bnot\s+found\b", re.I)
BLOCK_RE = re.compile(r"<!-- plan-sources:start -->.*?<!-- plan-sources:end -->\s*", re.S)
API = "https://commons.wikimedia.org/w/api.php"


def fetch(url):
    """Tách mạng để kiểm thử với dữ liệu giả."""
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=20) as response:
        return response.read().decode(response.headers.get_content_charset() or 'utf-8', errors='replace')


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def page_text(body):
    parser = TextExtractor()
    parser.feed(body)
    return ' '.join(parser.parts)


def normalized_number(number):
    return re.sub(r'[.,]', '', number)


def extract_sources(plan):
    """Giữ mọi lần xuất hiện; không tự kiểm tra các bảng kết quả cũ."""
    sources = {}
    for line in BLOCK_RE.sub('', plan).splitlines():
        matches = list(URL_RE.finditer(line))
        if not matches:
            continue
        without_urls = URL_RE.sub('', line)
        numbers = set(NUMBER_RE.findall(without_urls))
        for match in matches:
            url = match.group().rstrip('.,;:!?)]}')
            sources.setdefault(url, set()).update(numbers)
    return sources


def check_url(url, numbers):
    try:
        content = page_text(fetch(url))
    except HTTPError as exc:
        return ('CHAN' if exc.code in (403, 429) else f'HTTP {exc.code}'), []
    except (URLError, OSError, TimeoutError, ValueError) as exc:
        return 'KHONG_MO_DUOC', [str(exc)]
    if ERROR_RE.search(content):
        return 'TRANG_LOI', []
    found = {normalized_number(n) for n in NUMBER_RE.findall(content)}
    missing = sorted((n for n in numbers if normalized_number(n) not in found), key=str)
    return ('KHONG_CHUA_SO', missing) if missing else ('OK', [])


def commons_category(url):
    parsed = urlsplit(url)
    if parsed.hostname is None or parsed.hostname.lower() != 'commons.wikimedia.org':
        return None
    path = unquote(parsed.path)
    title = path.removeprefix('/wiki/') if path.startswith('/wiki/') else parse_qs(parsed.query).get('title', [''])[0]
    return title.replace('_', ' ') if title.lower().startswith('category:') else None


def category_members(category):
    continuation = {}
    members = []
    while True:
        params = {'action': 'query', 'format': 'json', 'list': 'categorymembers',
                  'cmtitle': category, 'cmtype': 'file|subcat', 'cmlimit': 'max', **continuation}
        data = json.loads(fetch(API + '?' + urlencode(params)))
        if 'error' in data:
            raise ValueError(str(data['error']))
        members.extend(data['query']['categorymembers'])
        continuation = data.get('continue')
        if not continuation:
            return members


def count_commons(category):
    members = category_members(category)
    files = {m['pageid'] for m in members if m['ns'] == 6}
    for subcategory in {m['title'] for m in members if m['ns'] == 14}:
        files.update(m['pageid'] for m in category_members(subcategory) if m['ns'] == 6)
    return len(files)


def run(plan):
    rows = []
    for url, numbers in extract_sources(plan).items():
        status, details = check_url(url, numbers)
        category = commons_category(url)
        count = '—'
        if category:
            try:
                count = str(count_commons(category))
            except (HTTPError, URLError, OSError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as exc:
                count = 'KHONG_DEM_DUOC'
                details.append(f'Commons: {exc}')
        rows.append((url, status, count, details))
    return rows


def render(rows):
    lines = [f'## Kiểm nguồn tự động ({date.today().isoformat()})', '',
             '> Kết quả hỗ trợ rà soát, không chứng minh nội dung đúng; CHAN và KHONG_MO_DUOC chưa được xác minh.', '',
             '| URL | Trạng thái | Số file Commons (gồm một cấp con) | Chi tiết |',
             '|---|---|---:|---|']
    for url, status, count, details in rows:
        detail = ', '.join(details).replace('|', '\\|').replace('\n', ' ')
        lines.append(f'| {url.replace("|", "%7C")} | {status} | {count} | {detail} |')
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('topic')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', args.topic):
        parser.error('topic không hợp lệ')
    path = ROOT / 'data' / 'long' / args.topic / 'plan.md'
    plan = path.read_text(encoding='utf-8')
    rows = run(plan)
    report = render(rows)
    print(report, end='')
    if args.write:
        path.write_text('<!-- plan-sources:start -->\n' + report + '<!-- plan-sources:end -->\n\n' + plan, encoding='utf-8')
    return int(any(status in ('TRANG_LOI', 'KHONG_CHUA_SO', 'KHONG_MO_DUOC')
                   or (status.startswith('HTTP ') and int(status[5:]) >= 400)
                   or count == 'KHONG_DEM_DUOC' for _, status, count, _ in rows))


if __name__ == '__main__':
    from factory.console import utf8_console
    utf8_console()
    raise SystemExit(main())
