"""Soát kịch bản video dài (30-90 phút) BUD / FS TRƯỚC khi tốn TTS + render.

Bạn đồng hành của skill `.claude/skills/long-script/`: mỗi luật ở đây khớp một luật trong SKILL.md và được rút từ
đường giữ chân thật của kênh (xem `references/evidence.md`). Thuần Python, không mạng, chỉ đọc.

Không lặp lại `hf_batch_render.retention_issues`: hàm đó vẫn là cổng của runner và được gọi nguyên vẹn ở đây
(mục "runner"). Lint đo thêm những thứ runner không đo: phân bố độ dài, liệt kê, câu mở lặp, từ lặp, câu trừu tượng
liền nhau, vòng mở / trả, re-hook 25-50-75%, 90 giây đầu, độ dài chương, câu kết chương, lời gọi đăng ký, bẫy TTS.
Đoạn "không ngắt nhịp" dùng ĐÚNG định nghĩa của retention_issues (test đảm bảo hai bên ra cùng một con số).

Usage:
    python long_script_lint.py output/cl_staging/long/plan_long_w41.json --only L_bud_05
    python long_script_lint.py plan.json --only L_fs_06 --json
    python long_script_lint.py nhap.txt              # bản nháp: mỗi dòng một dòng kịch bản, **tiêu đề chương**
    python long_script_lint.py plan.json --only X --kind night   # Đêm nghe: bỏ luật móc mạnh
    python long_script_lint.py plan.json --only X --strict       # mã thoát 1 nếu có LỖI

Thời gian: nếu có `out/<id>.json` (segments TTS thật, cùng số dòng) cạnh file plan thì dùng giây thật; không thì ước
theo 185 tiếng/phút (mặc định của retention_issues; đo 30 bản trụ 10/2026: 179-189 tiếng/phút kể cả nghỉ).
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import statistics
import sys
from pathlib import Path

import hf_batch_render as HBR

RATE = 185 / 60  # tiếng/giây -- mặc định của hf_batch_render.retention_issues

ERROR, WARN, INFO = "LỖI", "CẢNH BÁO", "GỢI Ý"

# ---------------------------------------------------------------- tách câu, đếm tiếng


def is_heading(line: str) -> bool:
    """Tiêu đề chương = câu in đậm TRỌN câu (giống hf_batch_render.chapter_spans)."""
    s = line.strip()
    return s.startswith("**") and s.endswith("**") and s.count("**") == 2


def plain(line: str) -> str:
    return line.replace("**", "").strip()


def sentences(text: str) -> list[str]:
    """Tách câu y như retention_issues: theo . ! ?"""
    return [x.strip() for x in re.findall(r"[^.!?]+[.!?]?", text) if x.strip()]


_DIG = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]


def _three(n: int, full: bool) -> list[str]:
    h, t, u = n // 100, n // 10 % 10, n % 10
    out = []
    if full or h:
        out += [_DIG[h], "trăm"]
    if t == 0:
        if u and (full or h):
            out += ["lẻ", _DIG[u]]
        elif u:
            out.append(_DIG[u])
    elif t == 1:
        out.append("mười")
        if u:
            out.append("lăm" if u == 5 else _DIG[u])
    else:
        out += [_DIG[t], "mươi"]
        if u:
            out.append({1: "mốt", 4: "tư", 5: "lăm"}.get(u, _DIG[u]))
    return out


def read_int(n: int) -> str:
    """Cách đọc tiếng Việt của một số nguyên (đủ để đếm tiếng và gợi ý cách viết)."""
    if n == 0:
        return "không"
    words, groups = [], []
    while n:
        groups.append(n % 1000)
        n //= 1000
    units = ["", "nghìn", "triệu", "tỷ"]
    for i in range(len(groups) - 1, -1, -1):
        g = groups[i]
        if not g:
            continue
        words += _three(g, full=i < len(groups) - 1)
        if units[i % 4]:
            words.append(units[i % 4])
    return " ".join(words)


def _num_syllables(tok: str) -> int:
    t = tok.strip(".,;:!?()\"'“”‘’…%")
    if "," in t and re.fullmatch(r"\d+,\d+", t):  # số thập phân kiểu Việt: 1,5
        a, b = t.split(",")
        return len(read_int(int(a)).split()) + 1 + len(b)
    digits = re.sub(r"[.,]", "", t)
    if digits.isdigit() and len(digits) <= 12:
        return len(read_int(int(digits)).split())
    return max(1, len(re.findall(r"\d", t)))


def syllables(text: str) -> int:
    """Số tiếng KHI ĐỌC: chữ số được đọc ra (1983 = 7 tiếng). Runner đếm token (1983 = 1) -> lint chặt hơn."""
    n = 0
    for tok in plain(text).split():
        if re.search(r"\d", tok):
            n += _num_syllables(tok)
        else:
            n += max(1, len([p for p in tok.split("-") if p.strip(".,;:!?\"'“”…()")]))
    return n


def tokens(text: str) -> int:
    """Số token (cách retention_issues và tốc độ 185/phút được đo)."""
    return len(plain(text).split())


# ---------------------------------------------------------------- phân loại câu (heuristic)

PERSON = (r"ông|bà|anh|chị|cô|cậu|chàng|nàng|vua|hoàng hậu|thái tử|công chúa|vị sư|nhà sư|sư|thầy|người thị giả|ngài|"
          r"bồ tát|đức phật|thương nhân|người lái buôn|cậu bé|cô bé|mẹ|cha|vợ|chồng|con trai|con gái|lão|người mẹ|người cha|"
          r"hắn|ma vương|người ấy|anh ấy|chị ấy|ông ấy|bà ấy|cô ấy")
NARRATIVE = re.compile(r"(?i)\b(kể rằng|ngày xưa|thuở|một hôm|một ngày|một đêm|một buổi|đêm ấy|đêm đó|sáng hôm|khi ấy|lúc ấy|"
                       r"hôm ấy|năm ấy|bấy giờ|tương truyền|chuyện kể)\b")
SENSORY = re.compile(r"(?i)\b(tay|chân|mắt|mặt|tóc|vai|lưng|da|xương|máu|nước mắt|giọng|tiếng|nhà|cửa|cửa sổ|bàn thờ|bàn|ghế|"
                     r"bát|chén|mâm|cơm|áo|nón|đèn|nến|nhang|hương|hoa|lọ|gương|giường|bếp|tiền|vàng|bạc|gậy|bình bát|"
                     r"cây|lá|sông|núi|đá|đường|chợ|chùa|tháp|am|ngựa|voi|xe|thuyền|mưa|gió|nắng|đêm|bình minh|hoàng hôn|"
                     r"trăng|sao trời|ngôi sao|lửa|khói|lạnh|nóng|cát|sa mạc|biển|rừng|khóc|cười|quỳ|cúi|ôm|cầm|mở|đóng|ngồi|"
                     r"nằm|đứng|chạy|ăn|uống|thở|run|đói|khát|mùi|thơm|tối|sáng|giờ Tý|ngày|tháng|gươm|kiếm|bùn|cỏ|hạt|rơm|"
                     r"mái|sân|giếng|ruộng|lúa|gạo|muối|sữa)\b")
NUMWORD = re.compile(r"(?i)\b(mười|mươi|trăm|nghìn|ngàn|triệu|tỷ|hai|ba|bốn|sáu|bảy|tám|chín)\b")
ABSTRACT = re.compile(r"(?i)\b(nghĩa là|tức là|được xem là|được hiểu là|được gọi là|gọi là|có nghĩa|bản chất|khái niệm|"
                      r"nguyên lý|nguyên tắc|quy luật|ý nghĩa|năng lượng|tâm thức|nhận thức|giáo lý|triết lý|vô thường|vô ngã|"
                      r"duyên khởi|nhân duyên|nghiệp|phiền não|chánh niệm|trí tuệ|từ bi|giải thoát|khổ đau|tham|sân|si|"
                      r"ngũ hành|tương sinh|tương khắc|âm dương|can chi|thiên can|địa chi|nạp âm|lục hợp|tam hợp|lục hại|"
                      r"lục xung|thái tuế|cát|hung|vận|khí|mệnh|tinh thần|hệ thống|quan hệ|yếu tố|khía cạnh|phương diện|"
                      r"điều quan trọng|nói cách khác|về mặt|thực chất|bởi lẽ|vì vậy|do đó|nhìn chung)\b")
META = re.compile(r"(?i)\b(video này|trong video|cuối video|đầu video|giữa video|phần cuối|đăng ký|bình luận|chia sẻ video|"
                  r"xem đến cuối|xem tiếp|kênh)\b")
CTA = re.compile(r"(?i)\b(đăng ký kênh|bấm đăng ký|nhấn đăng ký|bật chuông|để lại bình luận|viết .{0,30} bình luận)\b")
SUMMARY_END = re.compile(r"(?i)^(tóm lại|nói tóm lại|tóm gọn|như vậy|vậy là|tổng kết)\b")
DEFINITION_HEAD = re.compile(r"(?i)(là gì|chìa khóa|trước hết|khái niệm|nguồn gốc|đến từ đâu|cơ bản|hiểu đúng về|giải thích)")
OPEN_LOOP = re.compile(r"(?i)(ở cuối video|cuối video|lát nữa|chút nữa|phần sau|chương sau|chặng sau|"
                       r"(ta|mình|chúng ta)( cũng)? sẽ (thấy|gặp|quay lại|trở lại|biết|kể|nói|tìm|trả lời|đi|leo)|"
                       r"sẽ (kể|nói rõ|trả lời|giải thích)|câu hỏi thứ (nhất|hai|ba)|ba câu hỏi|phải chăng|"
                       r"hãy (giữ|nhớ) (câu hỏi|hình ảnh|chi tiết)|bí mật|điều bất ngờ|còn một điều|chưa phải (là )?tất cả|"
                       r"nhưng đó chưa phải|để sau|vẫn chưa ai|chưa ai biết)")
PAYOFF = re.compile(r"(?i)(còn nhớ|nhớ (câu hỏi|chuyện|cảnh|hình ảnh|chi tiết|lời|đêm|người)|(hãy|giờ|ta|mình|cùng) (quay|trở) lại|"
                    r"quay lại (với|câu hỏi)|câu trả lời (là|nằm|đây|đã|cho|đầu tiên)|đã có câu trả lời|"
                    r"giờ (thì )?(ta|mình|bạn) (đã )?(hiểu|biết|có thể)|"
                    r"như đã hứa|lời đáp|đó (chính )?là lý do|đây là câu trả lời|điều đã hứa|như đầu video|ở đầu video)")
FOREIGN = re.compile(r"[āīūṅñṭḍṇḷṃṁśṣ]", re.I)
# Đo bằng vieneu_utils.phonemize_text 14/10/2026: "năm 1-3 lần" -> "năm ngày một tháng ba lần"; "DN 16" -> "đi-en";
# "Sāriputta", "Jāṇussoṇi", "Vedehikā" -> âm tiếng Anh vỡ; ngoặc đơn bị bỏ mà không ngắt hơi. "3/4" -> "ba trên bốn",
# "1.068" / "2.500" / "1,5" / "12/7/2025" / "23:00" / "VIII" đọc đúng.
TTS_DATE = re.compile(r"\d\s*[-–]\s*\d")
TTS_ACRO = re.compile(r"\b(?![IVXLC]+\b)[A-ZĐ]{2,}\b")
TTS_RISK = re.compile(r"(%|&|\(|\)|\.\.\.|…|\bv\.v\b|\d\s*/\s*\d)")
CHI = HBR.CHI_NAME

STOP = set("""là và của có không một những các cho với được này ấy đó thì mà người ta mình bạn ở trong đã sẽ đang cũng như
lại rồi nhưng khi để từ theo vì nên ra vào đến đi nào gì cái chỉ rất nhiều hơn thể còn nữa vẫn đều ai sao thế vậy hay hoặc
bị phải làm nói biết điều chúng mỗi cùng đây kia nó họ ngài ông bà anh chị cô con hai ba bốn năm sáu bảy tám chín mười
trên dưới sau trước giữa lúc thật một_""".split())


def kind_of(sent: str) -> str:
    """question | meta | story | concrete | abstract | neutral."""
    s = plain(sent)
    if s.endswith("?"):
        return "question"
    if META.search(s):
        return "meta"
    body = s[1:] if s else s
    proper = re.search(r"(?<![.!?:]\s)(?<!^)\b[A-ZĐÂĂÊÔƠƯÁÀẢÃẠ][\wÀ-ỹ]+", body)
    has_num = bool(re.search(r"\d", s) or NUMWORD.search(s))
    sensory = bool(SENSORY.search(s))
    person = bool(re.search(rf"(?i)\b({PERSON})\b", s))
    if (NARRATIVE.search(s) or (person and (sensory or ":" in s))) and not ABSTRACT.search(s):
        return "story"
    if has_num or sensory or proper or ":" in s:
        return "concrete"
    if ABSTRACT.search(s):
        return "abstract"
    return "neutral"


# ---------------------------------------------------------------- nạp kịch bản + thời gian


def load_row(path: Path, only: str | None) -> dict:
    if path.suffix == ".txt":
        lines = [x.rstrip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        return {"id": path.stem, "script": lines}
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]
    rows = [r for r in data if not only or r.get("id") == only]
    if not rows:
        raise SystemExit(f"không thấy id {only!r} trong {path} (có: {[r.get('id') for r in data]})")
    if len(rows) > 1:
        raise SystemExit(f"{path} có {len(rows)} mục -- chọn một bằng --only ({[r.get('id') for r in rows]})")
    return rows[0]


def timeline(row: dict, plan_path: Path | None = None, rate: float = RATE) -> tuple[list[tuple[float, float]], str]:
    """[(giây đầu, giây cuối)] cho từng dòng. Giây thật nếu có out/<id>.json khớp số dòng."""
    script = row.get("script") or []
    if plan_path is not None:
        seg_file = plan_path.parent / "out" / f"{row.get('id')}.json"
        if seg_file.exists():
            try:
                segs = json.loads(seg_file.read_text(encoding="utf-8")).get("segments") or []
            except (OSError, ValueError):
                segs = []
            if len(segs) == len(script):
                return [(s["start"], s["end"]) for s in segs], f"giây thật ({seg_file.name})"
    out, t = [], 0.0
    for line in script:
        d = tokens(line) / rate
        out.append((t, t + d))
        t += d
    return out, f"ước {rate * 60:.0f} tiếng/phút"


# ---------------------------------------------------------------- các phép đo


def beat_stretches(row: dict, rate: float = RATE) -> list[tuple[float, int, int]]:
    """Mọi đoạn liền không ngắt nhịp: [(giây, dòng đầu, dòng cuối)], giảm dần.
    ĐÚNG định nghĩa của hf_batch_render.retention_issues: ngắt = câu hỏi, chữ số, câu nói <= 6 tiếng, visual
    quote/ask/stamp; tiêu đề chương đặt lại về 0; giây = token / rate."""
    vis = row.get("visuals") or {}
    out, cur, start = [], 0.0, None
    for i, line in enumerate(row.get("script") or [], 1):
        if line.startswith("**") and line.endswith("**"):
            if cur:
                out.append((cur, start, i - 1))
            cur, start = 0.0, None
            continue
        t = line.replace("**", "")
        ss = [x.strip() for x in re.findall(r"[^.!?]+[.!?]?", t) if x.strip()]
        hit = ("?" in t or re.search(r"\d", t) or any(len(x.split()) <= 6 for x in ss)
               or (vis.get(str(i)) or {}).get("type") in ("quote", "ask", "stamp"))
        if hit:
            if cur:
                out.append((cur, start, i - 1))
            cur, start = 0.0, None
        else:
            start = start or i
            cur += len(t.split()) / rate
    if cur:
        out.append((cur, start, len(row.get("script") or [])))
    return sorted(out, reverse=True)


def list_issues(sent: str) -> str | None:
    """Liệt kê >= 4 mục SONG SONG trong một câu nói: chuỗi >= 4 cụm liền nhau (ngăn bởi dấu phẩy / và / hay / hoặc), mỗi cụm
    là tên riêng (<= 4 tiếng), con số, hoặc cụm ngắn <= 3 tiếng. Đồng vị kiểu "một người già, lưng còng, tóc bạc" không tính."""
    s = plain(sent).rstrip(".!?")
    s = s.rsplit(":", 1)[-1]  # "Ba thứ: A, B, C" -> chỉ phần sau dấu hai chấm
    items = [x.strip() for x in re.split(r",|\s+và\s+|\s+hay\s+|\s+hoặc\s+", s) if x.strip()]
    items = [re.sub(r"(?i)^(và|cả|rồi|hay|hoặc)\s+", "", x) for x in items]

    def kind(x: str) -> str | None:
        w = x.split()
        if re.fullmatch(r"\d[\d.]*", w[-1]) and len(w) <= 3:
            return "con số"
        if x[:1].isupper() and len(w) <= 4 and all(t[:1].isupper() for t in w):
            return "tên riêng"
        if len(w) <= 3:
            return "mục"
        return None

    best, run, kinds = 0, 0, collections.Counter()
    for k, x in enumerate(items):
        kd = kind(x) if k else (kind(x) if len(x.split()) <= 3 else None)
        run = run + 1 if kd else 0
        if kd:
            kinds[kd] += 1
        if run > best:
            best = run
    if best < 4:
        return None
    top = kinds.most_common(1)[0][0]
    return f"{best} {top}"


def opener(sent: str) -> str:
    w = re.sub(r"[^\wÀ-ỹ\s]", "", plain(sent).lower()).split()
    return " ".join(w[:2])


def bigrams(text: str) -> list[str]:
    w = [x for x in re.sub(r"[^\wÀ-ỹ\s]", " ", plain(text)).split()]
    out = []
    for a, b in zip(w, w[1:]):
        if a.lower() in STOP or b.lower() in STOP or a.isdigit() or b.isdigit():
            continue
        out.append(f"{a} {b}")
    return out


def pct(xs: list[int], q: float) -> int:
    if not xs:
        return 0
    s = sorted(xs)
    return s[min(len(s) - 1, int(q * len(s)))]


def lint(row: dict, plan_path: Path | None = None, kind: str = "standard", rate: float = RATE) -> dict:
    script = list(row.get("script") or [])
    if not any(x.strip() for x in script):
        raise SystemExit(f"{row.get('id')}: kịch bản rỗng")
    times, time_src = timeline(row, plan_path, rate)
    total = times[-1][1] if times else 0.0
    issues: list[tuple[str, str, str]] = []  # (mức, mã, nội dung)

    def add(level, code, msg):
        issues.append((level, code, msg))

    # câu nói (không tính tiêu đề)
    sents = []  # (dòng, câu, tiếng đọc, loại, giây đầu dòng)
    for i, line in enumerate(script, 1):
        if is_heading(line):
            continue
        for s in sentences(plain(line)):
            sents.append((i, s, syllables(s), kind_of(s), times[i - 1][0]))
    n = len(sents) or 1
    syl_s = [x[2] for x in sents]
    syl_l = [syllables(x) for x in script if not is_heading(x)]

    # 1. độ dài câu / dòng
    buckets = collections.Counter()
    for v in syl_s:
        buckets["<=6" if v <= 6 else "7-11" if v <= 11 else "12-18" if v <= 18 else "19-25" if v <= 25
                else "26-35" if v <= 35 else ">35"] += 1
    long_s = [(i, v, s) for i, s, v, _, _ in sents if v > 35]
    for i, v, s in long_s:
        add(ERROR, "cau_dai", f"dòng {i}: câu {v} tiếng đọc (> 35) -- tách ở dấu hai chấm / 'mà là': {s[:70]}")
    long_l = [i for i, x in enumerate(script, 1) if not is_heading(x) and syllables(x) > 35]
    short_share = buckets["<=6"] / n
    if kind != "night" and short_share < 1 / 8:
        add(WARN, "it_cau_ngan", f"câu <= 6 tiếng chỉ {buckets['<=6']}/{n} ({short_share:.0%}) -- cần >= 1/8, tốt nhất 1/6-1/4 "
            "(câu đỉnh sau khoảnh khắc, phán định ĐÚNG/SAI)")

    # 2. đoạn không ngắt nhịp (định nghĩa runner)
    stretches = beat_stretches(row, rate)
    limit = 120 if kind == "night" else 90
    for sec, a, b in stretches[:5]:
        if sec > limit:
            add(WARN, "khong_ngat_nhip", f"dòng {a}-{b}: ~{sec:.0f} giây liền không câu hỏi/con số/câu ngắn -- chèn một nhịp")
        elif sec > 60:
            add(INFO, "khong_ngat_nhip", f"dòng {a}-{b}: ~{sec:.0f} giây không ngắt nhịp (ổn nhưng sát ngưỡng)")

    # 3. chương
    heads = [i for i, x in enumerate(script, 1) if is_heading(x)]
    bounds = ([1] if not heads or heads[0] != 1 else []) + heads
    chapters = []
    for k, a in enumerate(bounds):
        b = (bounds[k + 1] - 1) if k + 1 < len(bounds) else len(script)
        t0, t1 = times[a - 1][0], times[b - 1][1]
        title = plain(script[a - 1]) if is_heading(script[a - 1]) else "(mở đầu)"
        chapters.append({"dòng": [a, b], "giây": [round(t0), round(t1)], "phút": round((t1 - t0) / 60, 1), "tiêu đề": title})
    for c in chapters[1:-1]:
        if c["phút"] > 8.5:
            add(WARN, "chuong_dai", f"chương '{c['tiêu đề'][:40]}' {c['phút']} phút (> 8) -- tách hoặc chèn re-hook giữa chương")
    for c in chapters:
        a, b = c["dòng"]
        body = [s for s in sents if a <= s[0] <= b]
        if body and c is not chapters[-1] and SUMMARY_END.search(body[-1][1]):
            add(WARN, "ket_chuong_tom_tat", f"dòng {body[-1][0]}: kết chương bằng tóm tắt ('{body[-1][1][:40]}') -- kết bằng câu cầu nối")
    mids = [c["phút"] for c in chapters[1:-1]]
    if len(mids) >= 4 and statistics.median(mids) < 2:
        add(INFO, "chuong_ngan", f"trung vị chương {statistics.median(mids)} phút (< 2): thẻ chương dày cắt mạch kể -- cân nhắc "
            "gộp thành chương 3-8 phút, giữ tiêu đề phụ trên màn hình")
    if heads and total > 600 and len(heads) < total / 60 / 8:
        add(WARN, "it_chuong", f"{len(heads)} chương cho {total / 60:.0f} phút -- mỗi chương 3-8 phút")

    # 4. liệt kê
    for i, s, *_ in sents:
        why = list_issues(s)
        if why:
            add(WARN, "liet_ke", f"dòng {i}: liệt kê {why} trong một câu -- đọc tối đa 3, phần còn lại lên màn hình: {s[:60]}")
    for msg in HBR.crowded_chi_lines([plain(x) for x in script]):
        add(ERROR, "nhieu_chi", f"{msg} -- >= 4 tên chi trong một dòng, TTS đọc lồng (runner chặn)")
    if row.get("series") == "fs":
        for msg in HBR.zodiac_naming_errors(script):
            add(ERROR, "ten_con_vat", f"{msg} -- FS gọi con giáp bằng tên chi (runner chặn)")

    # 5. câu mở lặp
    ops = [opener(s) for _, s, *_ in sents]
    cnt = collections.Counter(o for o in ops if o)
    rep_open = [(o, c) for o, c in cnt.most_common(8) if c >= max(4, int(0.02 * n) + 1)]
    for o, c in rep_open[:4]:
        add(INFO, "mo_cau_lap", f"{c} câu mở bằng '{o}'")
    for k in range(len(ops) - 2):
        if ops[k] and ops[k] == ops[k + 1] == ops[k + 2] and (k == 0 or ops[k - 1] != ops[k]):
            add(INFO, "mo_cau_lap", f"dòng {sents[k][0]}: ba câu liền mở bằng '{ops[k]}' (điệp có chủ ý thì giữ, tối đa 3)")

    # 6. từ lặp (cục bộ: cùng cụm 2 tiếng thường >= 3 lần trong 5 dòng)
    grams = [bigrams(x) if not is_heading(x) else [] for x in script]
    seen_local = set()
    for k in range(len(script)):
        win = collections.Counter(g for j in range(k, min(k + 5, len(script))) for g in grams[j])
        for g, c in win.items():
            if c >= 3 and g[0].islower() and g not in seen_local:
                seen_local.add(g)
                add(INFO, "tu_lap", f"dòng {k + 1}-{min(k + 5, len(script))}: '{g}' lặp {c} lần trong 5 dòng")
    top_grams = collections.Counter(g for gs in grams for g in gs).most_common(10)

    # 7. trừu tượng / cụ thể
    kinds = collections.Counter(x[3] for x in sents)
    concrete = kinds["story"] + kinds["concrete"]
    abstract = kinds["abstract"]
    run, best, best_at = 0, 0, 0
    for i, s, v, k, t in sents:
        run = run + 1 if k in ("abstract", "neutral") else 0
        if run > best:
            best, best_at = run, i
    if best >= 5:
        add(WARN, "truu_tuong_lien", f"{best} câu liền không cụ thể (tới dòng {best_at}) -- chèn ví dụ, con số, cảnh, câu hỏi")
    if abstract / n > 0.25:
        add(WARN, "truu_tuong", f"câu trừu tượng {abstract}/{n} ({abstract / n:.0%}) > 25%")

    # 8. vòng mở / trả + re-hook
    opens = [(i, t) for i, s, v, k, t in sents if OPEN_LOOP.search(s)]
    pays = [(i, t) for i, s, v, k, t in sents if PAYOFF.search(s)]
    if kind != "night" and total > 600:
        if len(opens) < 3:
            add(WARN, "it_vong_mo", f"chỉ {len(opens)} câu mở vòng (cần >= 3: 'lát nữa', 'ở cuối video', 'ta sẽ quay lại'...)")
        if opens and not pays:
            add(WARN, "khong_tra_vong", "có mở vòng nhưng không câu trả vòng nào ('còn nhớ...', 'quay lại với...', 'câu trả lời là...')")
        for mark in (0.25, 0.5, 0.75):
            lo, hi = total * (mark - 0.05), total * (mark + 0.05)
            near = [i for i, s, v, k, t in sents if lo <= t <= hi and (k == "question" or OPEN_LOOP.search(s) or PAYOFF.search(s))]
            if not near:
                add(WARN, "thieu_rehook", f"không có re-hook (câu hỏi / mở / trả vòng) quanh {int(mark * 100)}% "
                    f"({lo / 60:.0f}-{hi / 60:.0f} phút)")

    # 9. 90 giây đầu
    first = [x for x in sents if x[4] < 90]
    if kind != "night" and first:
        if first[0][3] not in ("story", "concrete"):
            add(WARN, "mo_dau_khong_cu_the", f"câu 1 không cụ thể ({first[0][3]}): {first[0][1][:60]}")
        if len(first) > 1 and first[1][3] not in ("story", "concrete", "question") and first[1][2] > 6:
            add(WARN, "cau2_khong_cu_the", f"câu 2 không cụ thể ({first[1][3]}): {first[1][1][:60]}")
        metas = [x for x in first if x[3] == "meta"]
        if metas and metas[0][4] < 25:
            add(WARN, "meta_som", f"dòng {metas[0][0]}: nói về video ở giây {metas[0][4]:.0f} (< 25) -- cảnh trước, lộ trình sau")
        if len(metas) > 2:
            add(WARN, "meta_nhieu", f"{len(metas)} câu nói về video/kênh trong 90 giây đầu (> 2): lộ trình gói trong 1-2 câu")
        abs_run, worst = 0, 0
        for x in sents:
            if x[4] >= 120:
                break
            abs_run = abs_run + 1 if x[3] == "abstract" else 0
            worst = max(worst, abs_run)
        if worst >= 3:
            add(WARN, "ly_thuyet_som", f"{worst} câu trừu tượng liền trong 2 phút đầu -- lý thuyết trước khi trả")
        for c in chapters[1:3]:
            if c["giây"][0] < 240 and DEFINITION_HEAD.search(c["tiêu đề"]):
                add(WARN, "chuong_dinh_nghia_som", f"chương '{c['tiêu đề']}' ở giây {c['giây'][0]}: chương định nghĩa ngay sau "
                    "mở đầu là chỗ rơi thứ hai ở F6/F1/F3 -- nhét định nghĩa vào câu trả lời, <= 2 câu")
        q = next((k for k, x in enumerate(first) if x[3] == "question"), None)
        if q is not None and not any(x[3] in ("concrete", "story") for x in first[q + 1:]):
            add(WARN, "chua_tra_som", "câu hỏi mở đầu chưa được trả một phần nào trong 90 giây đầu")
        payload = next((c for c in chapters[1:] if not DEFINITION_HEAD.search(c["tiêu đề"])), None)
        if payload and payload["giây"][0] > 150:
            add(WARN, "noi_dung_muon", f"chương nội dung đầu tiên ('{payload['tiêu đề'][:40]}') bắt đầu ở giây "
                f"{payload['giây'][0]} (> 150)")

    # 10. lời gọi đăng ký
    ctas = [(i, t) for i, s, v, k, t in sents if CTA.search(s)]
    for i, t in ctas:
        if total and t < total * 0.85 and t > 60:
            add(INFO, "cta_giua", f"dòng {i}: lời gọi đăng ký ở {t / total:.0%} -- đặt sau lần trả vòng cuối")
    if len(ctas) > 3:
        add(WARN, "cta_nhieu", f"{len(ctas)} câu gọi đăng ký/bình luận (> 3)")

    # 11. bẫy TTS
    for i, line in enumerate(script, 1):
        p = plain(line)
        if FOREIGN.search(p):
            add(WARN, "tts_dau_la", f"dòng {i}: dấu Pali/Sanskrit ({FOREIGN.search(p).group()}) -- viết phiên âm Việt: {p[:50]}")
        if TTS_DATE.search(p):
            add(WARN, "tts_gach_noi", f"dòng {i}: '{TTS_DATE.search(p).group()}' bị đọc thành ngày tháng ('1-3' -> 'ngày một "
                f"tháng ba') -- viết 'từ một đến ba': {p[:50]}")
        if TTS_ACRO.search(p):
            add(WARN, "tts_viet_tat", f"dòng {i}: viết tắt '{TTS_ACRO.search(p).group()}' đọc kiểu tiếng Anh ('DN 16' -> 'đi-en') "
                f"-- lời đọc ghi 'Trường Bộ, kinh số mười sáu', mã kinh để trên màn hình: {p[:50]}")
        m = TTS_RISK.search(p)
        if m:
            add(INFO, "tts_ky_hieu", f"dòng {i}: '{m.group()}' -- viết bằng chữ như khi đọc: {p[:50]}")
        if p.count(":") >= 2 and re.search(r"(?i)\b(hỏi|thưa|đáp|nói|bảo)\b.*:.*\b(hỏi|thưa|đáp|nói|bảo)\b.*:", p):
            add(INFO, "hai_luot_thoai", f"dòng {i}: hai lượt thoại trong một dòng -- tách dòng để có nghỉ giữa hai người")

    runner = HBR.retention_issues(row)
    stats = {
        "id": row.get("id"), "thời gian": time_src, "phút": round(total / 60, 1), "dòng": len(script), "câu nói": len(sents),
        "tiếng (đọc)": sum(syl_s),
        "tiếng/câu": {"p10": pct(syl_s, .1), "trung vị": int(statistics.median(syl_s)) if syl_s else 0,
                      "p90": pct(syl_s, .9), "max": max(syl_s or [0])},
        "tiếng/dòng": {"trung vị": int(statistics.median(syl_l)) if syl_l else 0, "p90": pct(syl_l, .9),
                       "max": max(syl_l or [0]), "dòng > 35": len(long_l)},
        "phân bố câu": {k: buckets[k] for k in ("<=6", "7-11", "12-18", "19-25", "26-35", ">35")},
        "câu ngắn <= 6": f"{buckets['<=6']}/{n} ({short_share:.0%})",
        "đoạn không ngắt dài nhất": (f"~{stretches[0][0]:.0f} giây (dòng {stretches[0][1]}-{stretches[0][2]})"
                                     if stretches else "0"),
        "loại câu": dict(kinds.most_common()),
        "cụ thể : trừu tượng": f"{concrete} : {abstract} ({concrete / n:.0%} : {abstract / n:.0%})",
        "mở vòng / trả vòng": f"{len(opens)} / {len(pays)}",
        "mở vòng ở (%)": [round(t / total * 100) for _, t in opens] if total else [],
        "trả vòng ở (%)": [round(t / total * 100) for _, t in pays] if total else [],
        "chương": chapters,
        "cụm 2 tiếng nhiều nhất": top_grams,
        "câu mở hay dùng": cnt.most_common(5),
    }
    return {"stats": stats, "issues": issues, "runner": runner}


def render_text(rep: dict) -> str:
    s, out = rep["stats"], []
    out.append(f"== {s['id']} · {s['phút']} phút · {s['dòng']} dòng · {s['câu nói']} câu · {s['tiếng (đọc)']} tiếng · {s['thời gian']}")
    out.append(f"tiếng/câu {s['tiếng/câu']}  tiếng/dòng {s['tiếng/dòng']}")
    out.append(f"phân bố câu {s['phân bố câu']}  · câu ngắn {s['câu ngắn <= 6']}")
    out.append(f"đoạn không ngắt dài nhất {s['đoạn không ngắt dài nhất']} · cụ thể:trừu tượng {s['cụ thể : trừu tượng']}")
    out.append(f"loại câu {s['loại câu']}")
    out.append(f"mở/trả vòng {s['mở vòng / trả vòng']} · mở ở % {s['mở vòng ở (%)']} · trả ở % {s['trả vòng ở (%)']}")
    out.append("chương:")
    for c in s["chương"]:
        out.append(f"  {c['giây'][0] // 60:>3}:{c['giây'][0] % 60:02d}  {c['phút']:>4} phút  dòng {c['dòng'][0]}-{c['dòng'][1]}  {c['tiêu đề'][:60]}")
    out.append(f"cụm lặp nhiều nhất: {', '.join(f'{g} ×{c}' for g, c in s['cụm 2 tiếng nhiều nhất'][:6])}")
    out.append(f"câu mở hay dùng: {', '.join(f'{o} ×{c}' for o, c in s['câu mở hay dùng'])}")
    out.append("runner (hf_batch_render.retention_issues): " + ("; ".join(rep["runner"]) or "đạt"))
    order = {ERROR: 0, WARN: 1, INFO: 2}
    by = collections.Counter(lv for lv, *_ in rep["issues"])
    out.append(f"-- {by[ERROR]} lỗi, {by[WARN]} cảnh báo, {by[INFO]} gợi ý")
    for lv, code, msg in sorted(rep["issues"], key=lambda x: order[x[0]]):
        out.append(f"[{lv}] {code}: {msg}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("path", type=Path, help="plan_long_wNN.json, một row JSON, hoặc bản nháp .txt")
    ap.add_argument("--only", help="id trong file plan (bắt buộc nếu file có nhiều mục)")
    ap.add_argument("--kind", choices=["standard", "night"], default="standard",
                    help="night = Đêm nghe lời Phật dạy: bỏ luật móc/re-hook/90 giây đầu, nới đoạn không ngắt lên 120 giây")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="mã thoát 1 nếu có LỖI")
    ap.add_argument("--max-info", type=int, default=25, help="số GỢI Ý tối đa in ra (text)")
    a = ap.parse_args(argv)
    row = load_row(a.path, a.only)
    rep = lint(row, a.path, a.kind)
    if a.json:
        print(json.dumps(rep, ensure_ascii=False, indent=1))
    else:
        infos = [x for x in rep["issues"] if x[0] == INFO]
        if len(infos) > a.max_info:
            drop = set(map(id, infos[a.max_info:]))
            rep = {**rep, "issues": [x for x in rep["issues"] if id(x) not in drop]
                   + [(INFO, "...", f"còn {len(infos) - a.max_info} gợi ý (--max-info hoặc --json để xem hết)")]}
        print(render_text(rep))
    return 1 if a.strict and any(lv == ERROR for lv, *_ in rep["issues"]) else 0


if __name__ == "__main__":
    sys.exit(main())
