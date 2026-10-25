"""Lấy lại dữ liệu thô các mẫu prompt-motion.com (tiêu đề, thẻ, prompt, mô tả, khung, link video) vào items_raw.json.

Chỉ đọc trang công khai, nghỉ 0,5 s giữa hai trang, không tải video. Chạy bằng python có chứng chỉ SSL (.venv):
    .venv/bin/python .claude/skills/motion-library/references/prompt_motion/cap_nhat.py /tmp/pm_raw
Mục đã có trong items_raw.json được bỏ qua; mục mới cần phân loại theo khoá của catalog.json rồi chạy build_catalog.py.
"""
import re, json, html, time, sys, urllib.request
from pathlib import Path
D = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
out = D / "items_raw.json"
sm = urllib.request.urlopen(urllib.request.Request("https://prompt-motion.com/sitemap.xml", headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read().decode()
SKIP = re.compile(r"/(templates|customize|blog|tags)(/|$)")
urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", sm) if re.fullmatch(r"https://prompt-motion\.com/[^/]+", u) and not SKIP.search(u)]
done = {r["url"]: r for r in json.load(open(out))} if out.exists() else {}
def rsc(s):
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', s, re.S)
    return "".join(json.loads('"' + c + '"') for c in chunks)
def jstr(t, key, start=0):
    i = t.find(f'"{key}":"', start)
    if i < 0: return None, -1
    j = i + len(key) + 4; buf = []; esc = False
    while j < len(t):
        c = t[j]
        if esc: buf.append("\\" + c); esc = False
        elif c == "\\": esc = True
        elif c == '"': break
        else: buf.append(c)
        j += 1
    try: return json.loads('"' + "".join(buf) + '"'), i
    except Exception: return "".join(buf), i
def resolve(t, v):
    if not isinstance(v, str) or not re.fullmatch(r"\$[0-9a-f]+", v): return None if v == "$undefined" else v
    m = re.search(r"(?:^|\n)" + v[1:] + r":T([0-9a-f]+),", t)
    if not m: return v
    b = t[m.end():].encode("utf-8")[: int(m.group(1), 16)]
    return b.decode("utf-8", "replace")
for n, u in enumerate(urls):
    if u in done: continue
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        s = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception as e:
        print("LOI", u, e); continue
    t = rsc(s)
    rec = {"url": u, "slug": u.rsplit("/", 1)[1]}
    m = re.search(r'<title>(.*?)</title>', s); rec["title"] = html.unescape(m.group(1)).replace(" · Prompt Motion", "") if m else None
    m = re.search(r'"tags":\[(.*?)\]\}', t); rec["tags"] = json.loads("[" + m.group(1) + "]") if m else []
    p, i = jstr(t, "prompt"); rec["prompt"] = resolve(t, p)
    tr = re.search(r'"translation":\{"slug":"[^"]*","language":"([^"]*)","prompt":', t)
    if tr:
        rec["lang"] = tr.group(1); pe, _ = jstr(t, "prompt", tr.start()); rec["prompt_en"] = resolve(t, pe)
    note, _ = jstr(t, "note"); rec["note"] = resolve(t, note)
    m = re.search(r'<meta name="description" content="(.*?)"', s); rec["desc"] = html.unescape(m.group(1)) if m else None
    m = re.search(r'https://media\.prompt-motion\.com/[^"\\]*?\.mp4', s); rec["video"] = m.group(0) if m else None
    m = re.search(r'"width":(\d{3,4}),"height":(\d{3,4})', t); rec["wh"] = [int(m.group(1)), int(m.group(2))] if m else None
    m = re.search(r'https://(?:x|twitter)\.com/([^/"]+)/status/\d+', t); rec["author"] = m.group(1) if m else None
    rec["skill_cmd"] = sorted(set(re.findall(r'npx skills add [^"\\<]{3,120}', t)))[:3]
    done[u] = rec
    if n % 10 == 0:
        json.dump(list(done.values()), open(out, "w"), ensure_ascii=False, indent=1); print(n, rec["title"], flush=True)
    time.sleep(0.5)
json.dump(list(done.values()), open(out, "w"), ensure_ascii=False, indent=1)
print("XONG", len(done))
