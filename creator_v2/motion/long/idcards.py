"""Chọn kiểu thẻ tất định; không thay hay xóa nội dung cảnh."""
from collections import Counter
import hashlib
import re

STYLES = ("clip_file", "lower_third", "callout", "news_clip", "telegram", "polaroid", "index_card", "fingerprint", "passport", "verdict", "wanted", "envelope", "edict_scroll", "seal_slip", "museum_label", "case_divider", "terminal", "spec_sheet", "receipt", "app_card")
CONVICTION = {"fingerprint", "wanted", "verdict"}
IMAGE_STYLES = {"lower_third", "callout", "polaroid", "museum_label"}
CHANNELS = {
    "CL": set(STYLES[:16]),
    "MIM": {"lower_third", "callout", "polaroid", "index_card", "envelope", "museum_label", "terminal", "spec_sheet", "app_card"},
    "CK": {"lower_third", "callout", "receipt", "app_card"},
}
HINTS = {
    "person": {"clip_file", "lower_third", "callout", "polaroid", "index_card", "passport", "fingerprint", "wanted"},
    "document": {"news_clip", "telegram", "index_card", "envelope", "edict_scroll", "seal_slip", "case_divider", "verdict"},
    "money": {"receipt", "app_card"}, "tech": {"terminal", "spec_sheet", "app_card"},
    "place": {"lower_third", "callout", "museum_label", "polaroid"},
}

def year(value):
    m = re.search(r"(?<!\d)(1[0-9]{3}|20[0-9]{2})(?!\d)", str(value or ""))
    return int(m.group(1)) if m else None

def candidates(spec, scene):
    channel = str(spec.get("channel") or "CL").upper()
    pool = CHANNELS.get(channel, CHANNELS["CL"]).copy()
    if not scene.get("img"):
        pool -= IMAGE_STYLES
    y = year(spec.get("era")) or year(scene.get("date"))
    if not y or not 1850 <= y <= 1990: pool.discard("news_clip")
    if not y or not 1870 <= y <= 1950: pool.discard("telegram")
    era = str(spec.get("era") or "").casefold()
    china = any(term in era for term in ("china", "chinese", "trung hoa", "trung qu\u1ed1c"))
    ancient = bool(y and y < 1900) or any(term in era for term in ("ancient", "imperial", "c\u1ed5", "phong ki\u1ebfn"))
    if not (china and ancient): pool -= {"edict_scroll", "seal_slip"}
    if not y or y < 1850: pool.discard("passport")
    if y and y < 1900: pool.discard("polaroid")
    if y and y < 1950: pool -= {"terminal", "app_card"}
    # Chỉ bằng chứng kết án được khai riêng mới cho dùng ba kiểu nhạy cảm.
    if not (scene.get("convicted") is True and str(scene.get("conviction_source") or "").startswith(("https://", "http://"))):
        pool -= CONVICTION
    return sorted(pool)

def assign(topic, spec, chapters):
    """Gắn style trên bản sao chapters trong bộ nhớ; style khai tay được giữ."""
    if not spec.get("idcards"): return Counter()
    scenes = [s for _, ch in chapters for s in ch.get("scenes", [])]
    counts = Counter(s.get("style") for s in scenes if s.get("type") == "file" and s.get("style"))
    recent = []
    for index, scene in enumerate(scenes):
        if scene.get("type") != "file": continue
        style = scene.get("style")
        if not style:
            pool = candidates(spec, scene)
            available = [x for x in pool if x not in recent[-6:]] or pool
            if not available: raise ValueError("Không có kiểu thẻ phù hợp cho cảnh " + str(index))
            hint = HINTS.get(scene.get("hint"), set())
            def score(x):
                tie = hashlib.sha256(f"{topic}:{index}:{x}".encode("utf-8")).digest()
                return counts[x], x not in hint if hint else False, tie
            style = min(available, key=score)
            scene["style"] = style
            counts[style] += 1
        recent.append(style)
    return counts

def problems(chapters):
    scenes = [s for _, ch in chapters for s in ch.get("scenes", [])]
    cards = [(i, s) for i, s in enumerate(scenes) if s.get("type") == "file"]
    if not scenes: return []
    out = []
    if len(cards) / len(scenes) > .12:
        out.append(f"họ thẻ {len(cards)}/{len(scenes)} cảnh > 12%")
    counts = Counter(s.get("style") for _, s in cards)
    for style, count in sorted(counts.items(), key=lambda pair: str(pair[0])):
        if not style or style not in STYLES:
            out.append(f"kiểu thẻ không hợp lệ: {style!r}")
        if count / len(scenes) > .04:
            out.append(f"kiểu {style}: {count}/{len(scenes)} cảnh > 4%")
    for n, (i, scene) in enumerate(cards):
        if scene.get("style") in IMAGE_STYLES and not scene.get("img"):
            out.append(f"cảnh {i+1}: kiểu {scene.get('style')} cần img")
        if n and i - cards[n-1][0] < 5:
            out.append(f"thẻ tại cảnh {cards[n-1][0]+1} và {i+1} chưa cách 4 cảnh")
        if scene.get("style") in [s.get("style") for _, s in cards[max(0,n-6):n]]:
            out.append(f"kiểu {scene.get('style')} lặp trong 6 thẻ tại cảnh {i+1}")
        if scene.get("style") in CONVICTION and not (scene.get("convicted") is True and str(scene.get("conviction_source") or "").startswith(("https://", "http://"))):
            out.append(f"cảnh {i+1}: kiểu {scene.get('style')} cần bằng chứng kết án")
    return out
