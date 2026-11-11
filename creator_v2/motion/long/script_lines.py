"""Kịch bản đã duyệt (data/long/<topic>/script.md) -> "lines" của từng chNN.json (giữ nguyên mọi khoá khác: hud, bgm, scenes…).

    python motion/long/script_lines.py <topic> [--allow-repeat-line]

Quy ước script.md: "## CHnn · Tên chương"; mỗi dòng một câu; "‖" cuối dòng = nghỉ dài; "**[DIỄN Ý]**" = trích diễn ý; "[TRÍCH DỊCH]" = văn bản thật đã dịch;
"»" = phần sau là LỜI TRÍCH (đọc giọng trích, xem build_long.QUOTE_VOICE). Dòng "a: » b" tách thành 2 câu.
Dừng ở "## Ghi chú". Câu -> chuỗi, hoặc {"t", "p": nghỉ, "q": 1 (lời trích), "diy": 1}.

Cổng toàn vẹn (retro 2 mục 16): chạy factory.integrity.check trên LỜI ĐỌC của cả kịch bản TRƯỚC khi ghi chNN.json — câu lặp
nguyên văn ("Anh ta nghi ngờ." ×2 ở MIM #3) hay markup sót thì dừng, không để tới bước Bundle (sau khi đã render final).
Câu lặp CỐ Ý (điệp khúc kiểu "Từ địa ngục.") -> --allow-repeat-line; markup sót thì không có cờ bỏ qua.
Cuối câu được phép có một dấu cảnh `{loại: nội dung}` (sau cả `‖`). Dấu bị gỡ khỏi lời đọc
và nằm ở `marks` của chương: `{"i": chỉ số câu, "raw": "date: 29.07.1967"}`.
"""
import json
import re
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LONG_PAUSE = 1.0
FLOW_SOURCE_TERMS = ("được kể lại", "lời kể", "tài liệu", "nguồn", "ta chỉ có thể",
                     "không chắc", "theo hồ sơ", "người kể")
FLOW_META_TERMS = ("ta phải", "ta giữ", "ta chỉ có thể", "chúng ta phải", "phải nói chậm")
FLOW_META_PATTERN = re.compile(r"(?<!\w)(?<!anh )(?<!ông )(?<!bà )(?<!cô )(?<!người )"
                               r"(?:" + "|".join(map(re.escape, FLOW_META_TERMS)) + r")(?!\w)")
FLOW_YEAR = re.compile(r"(?<!\d)(?:1\d{3}|20\d{2})(?!\d)")
_MARK = re.compile(r"\s*\{([^{}]+)\}\s*$")


def _split_mark(s: str):
    m = _MARK.search(s)
    if not m:
        return s, None
    return s[:m.start()].rstrip(), m.group(1).strip()


def spoken_text(chs) -> str:
    """Lời sẽ đọc của cả kịch bản, mỗi câu một dòng (ranh giới câu chắc chắn, kể cả câu không có dấu chấm)."""
    return "\n".join((x if isinstance(x, str) else x["t"]) for c in chs for x in c["lines"])


# Câu lộ trình rập khuôn (retro 1 mục 14 / retro 2 mục 1: lặp ở A1, C1, D1, MIM #2 — RETENTION.md "Lời hứa lộ trình").
# Luật viết đã có; đây là chốt chặn bằng máy cho đúng cụm người xem đã nhận ra.
CLICHES = [re.compile(r"trả lời (ba|3) câu hỏi", re.I)]


# Các cụm sản xuất không thuộc lời kể; ranh giới từ tránh khớp bên trong từ khác.
# Chỉ các thuật ngữ CHẮC CHẮN là ghi chú sản xuất. Không đưa "kịch bản" (CK: "kịch bản giá tăng"), "trên màn hình"
# (MIM/CK kể về điện thoại, máy tính), "render", "agent" (MIM nói về AI agent): đã thử trên mọi Long và bắt nhầm (06/11).
META_TERMS = (
    "lời đọc", "brief", "mô-típ", "motif", "infobox", "prompt", "factcheck", "tts",
    "kịch bản này", "trên hình", "plan đã",
)
META_PATTERNS = {term: re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.I)
                 for term in META_TERMS}
META_STRUCTURE = re.compile(
    r"(?<!\w)(?:(?:sẽ\s+)?(?:quay lại|đóng|mở)\s+ở\s+chương\s+"
    r"(?:\d+|[\w]+)|vòng\s+thứ\s+(?:\d+|[\w]+)\s+đóng|"
    r"cảnh\s+ấy\s+ta\s+không\s+dựng)(?!\w)", re.I)
SOURCE_PATTERN = re.compile(
    r"(?<!\w)(?:wikipedia|bách khoa|bài tiếng việt|bài tiếng anh|cùng trang)(?!\w)", re.I)


def _meta_leak(text: str) -> bool:
    for term, pattern in META_PATTERNS.items():
        if pattern.search(text):
            return True
    return bool(META_STRUCTURE.search(text))



def flow_warnings(chs) -> list[tuple[str, str, int, str]]:
    """Cảnh báo mạch kể; chỉ số câu bắt đầu từ 0 như các neo cảnh."""
    out = []
    for chapter_index, c in enumerate(chs):
        lines = [x if isinstance(x, str) else x["t"] for x in c["lines"]]
        lowered = [line.casefold() for line in lines]
        source_indices = [i for i, line in enumerate(lowered)
                          if any(term in line for term in FLOW_SOURCE_TERMS)]
        # Gom các cửa sổ tám câu chồng nhau, tránh báo lặp cùng một đoạn.
        groups = []
        for start in range(max(1, len(lines) - 7)):
            hits = [i for i in source_indices if start <= i < start + 8]
            if len(hits) >= 3:
                if groups and start <= groups[-1][1]:
                    groups[-1] = (groups[-1][0], max(groups[-1][1], hits[-1]))
                else:
                    groups.append((hits[0], hits[-1]))
        for first, last in groups:
            out.append(("RAO_NGUON", c["name"], first, f"câu {first}–{last}"))
        start = None
        for i in range(len(lines) + 1):
            short = i < len(lines) and len(lines[i].split()) < 9
            if short and start is None:
                start = i
            elif not short and start is not None:
                if i - start >= 5:
                    out.append(("NHIP_DEU", c["name"], start, f"câu {start}–{i - 1}"))
                start = None
        for i, line in enumerate(lowered):
            if FLOW_META_PATTERN.search(line):
                out.append(("META_NGUOI_KE", c["name"], i, lines[i]))
        if c["name"].lower() == "ch00" or chapter_index == len(chs) - 1:
            continue
        title_year = FLOW_YEAR.search(c.get("title", ""))
        first_year = title_year or next((m for line in lines if (m := FLOW_YEAR.search(line))), None)
        if first_year:
            baseline = int(first_year.group())
            for i, line in enumerate(lines[:-3]):
                for match in FLOW_YEAR.finditer(line):
                    if int(match.group()) > baseline + 10:
                        out.append(("NHAY_MOC", c["name"], i,
                                    f"{match.group()} sau mốc {baseline} hơn 10 năm"))
    return out


def gate(chs, allow_repeat: bool = False) -> list[str]:
    """Lỗi CHẶN của factory.integrity trên toàn kịch bản (rỗng = qua). allow_repeat: câu lặp chỉ còn là cảnh báo.
    Kèm cụm lộ trình rập khuôn (CLICHES) — không có cờ bỏ qua: đổi hình thức lộ trình (RETENTION.md)."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from factory import integrity
    out = [f"ROADMAP_CLICHE [{c['name']}] «{t}»" for c in chs for x in c["lines"]
           for t in [x if isinstance(x, str) else x["t"]] if any(p.search(t) for p in CLICHES)]
    for c in chs:
        lines = [x if isinstance(x, str) else x["t"] for x in c["lines"]]
        out.extend(f"META_LEAK [{c['name']}] «{t}»" for t in lines if _meta_leak(t))
        source_count = sum(len(SOURCE_PATTERN.findall(t)) for t in lines)
        if source_count > 1:
            warnings.warn(f"SOURCE_DENSITY [{c['name']}] {source_count} lần", stacklevel=2)
    for code, chapter, index, note in flow_warnings(chs):
        warnings.warn(f"{code} [{chapter}] câu {index}: {note}", stacklevel=2)
    for f in integrity.check(spoken_text(chs)):
        if f.blocking and not (allow_repeat and f.code == "INT_REPEATED_SENTENCE"):
            where = next((c["name"] for c in chs for x in c["lines"] if f.span.strip() in (x if isinstance(x, str) else x["t"])), "?")
            out.append(f"{f.code} [{where}] «{f.span.strip()}»")
    return out


def parse(md: str):
    chs, cur = [], None
    for raw in md.split("\n"):
        s = raw.strip()
        if s.startswith("## Ghi chú"):
            break
        m = re.match(r"^## (CH\d\d) · (.+)$", s)
        if m:
            cur = {"name": m.group(1).lower(), "title": m.group(2), "lines": [], "marks": []}
            chs.append(cur)
            continue
        if not cur or not s or s == "---" or s.startswith("#"):
            continue
        # Nhãn có hoặc không có ** (ripper ch12 ghi "[DIỄN Ý]" trần -> lọt vào lời đọc, TTS đọc thành tiếng).
        diy = bool(re.search(r"\**\[DIỄN Ý\]\**", s))
        tr = "[TRÍCH DỊCH]" in s            # văn bản thật dịch sang tiếng Việt (nhãn TRÍCH DỊCH trên cảnh quote)
        s = re.sub(r"\**\[DIỄN Ý\]\**", "", s).replace("[TRÍCH DỊCH]", "").strip()
        s, mark = _split_mark(s)
        if not s:
            continue
        pause = s.endswith("‖")
        s = s.rstrip("‖").strip()
        parts = [p.strip() for p in s.split("»")]
        out = []
        if s.startswith("HỎI:"):           # câu hỏi của người xem, đọc bằng giọng "người hỏi" (kênh có CHAN["ask"])
            out.append({"t": s[4:].strip(), "ask": 1})
        elif len(parts) == 2:
            if parts[0]:
                out.append({"t": parts[0]})
            q = parts[1][:1].upper() + parts[1][1:]
            out.append({"t": q, "q": 1, **({"diy": 1} if diy else {}), **({"tr": 1} if tr else {})})
        else:
            out.append({"t": s, **({"diy": 1} if diy else {})})
        if pause:
            out[-1]["p"] = LONG_PAUSE
        cur["lines"] += out
        if mark:
            cur["marks"].append({"i": len(cur["lines"]) - 1, "raw": mark})
    for c in chs:
        x0 = c["lines"][0]
        if c["name"] != "ch00" and set(x0) == {"t"}:     # "Chương N. Tên." -> nghỉ để màn tên chương thở
            x0["p"] = 0.8
        c["lines"] = [x["t"] if set(x) == {"t"} else x for x in c["lines"]]
    return chs


if __name__ == "__main__":
    import pathlib, sys  # noqa: E401
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
    from factory.console import utf8_console  # noqa: E402
    utf8_console()  # console Windows cp1252 không in được tiếng Việt (retro 2 mục 7)
    topic = sys.argv[1]
    sd = ROOT / "data" / "long" / topic
    chs = parse((sd / "script.md").read_text(encoding="utf-8"))
    bad = gate(chs, allow_repeat="--allow-repeat-line" in sys.argv)
    if bad:      # dừng TRƯỚC khi ghi chNN.json -> không có gì để TTS đọc nhầm
        raise SystemExit("integrity: kịch bản chưa qua cổng (sửa script.md rồi chạy lại):\n  " + "\n  ".join(bad)
                         + "\n(câu lặp cố ý: thêm --allow-repeat-line)")
    tot = 0
    for c in chs:
        f = sd / f"{c['name']}.json"
        d = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        d["title"] = c["title"]
        d["lines"] = c["lines"]
        d.setdefault("scenes", [])
        f.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        syl = sum(len((x if isinstance(x, str) else x["t"]).split()) for x in c["lines"])
        tot += syl
        print(f"{c['name']}: {len(c['lines'])} câu, {syl} âm tiết, ~{syl / 200:.1f} phút  {c['title']}")
    print(f"TỔNG {sum(len(c['lines']) for c in chs)} câu, {tot} âm tiết")
