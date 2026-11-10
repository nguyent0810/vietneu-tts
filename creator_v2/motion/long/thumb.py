"""Render thumbnail từ mẫu HTML: motion/long/thumbs/<topic>_tN.html -> output/long/<topic>/tN.jpg (1280x720, < 2 MB)
+ tN_small.jpg (320x180) và tN_tiny.jpg (168x94) để soi ở cỡ mobile và cỡ feed.

    python motion/long/thumb.py <topic> [t1 t2 ...] [--allow-thumb] [--lint-only]

Sau khi dựng, in các dòng `THUMB LINT:` và thoát mã 1 nếu có lỗi (CTR thumbnail 0,x-1,x%, 09/11/2026):
  (a) chữ lớn (.big, `.tile b`, [data-fit]) > 7 từ là cảnh báo, > 10 từ là lỗi;
  (b) chữ .big sau khi FIT co lại nhỏ hơn 72 px ở khung 1920 là lỗi (không đọc được ở cỡ điện thoại);
  (c) ảnh phẳng, bạc màu: độ lệch chuẩn độ sáng toàn ảnh < 40 là lỗi;
  (d) không có <img> chủ thể: cảnh báo (không chặn thumbnail cũ);
  (e) chữ nhỏ hơn 44 px trên khung 1280, hoặc chữ rơi vào badge thời lượng góc dưới-phải: lỗi.
`--allow-thumb` bỏ qua lỗi có chủ đích (vẫn in). `--lint-only` chỉ soát mẫu HTML + tN.jpg đã có, không dựng lại.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "motion"), str(ROOT)]

import build_long as BL  # noqa: E402


# Chữ thumbnail tràn mép (MIM #5 t1/t2 09/10/2026: "CHƯA BẤM Đ…", "1 TRIỆU ĐO…" bị cắt): template ghi cỡ chữ cố định + nowrap.
# Chặn bằng máy: mọi phần tử chữ (.big, .pill, .tag hoặc data-fit; .pill thêm sau khi D2 t1 tràn nhãn 09/10) tự thu nhỏ (tối đa còn 40% cỡ gốc) tới khi nằm trong khung an toàn 40 px.
# Chạy lúc nạp và lại khi webfont nạp xong (số đo font dự phòng khác font thật). Tất định: chỉ đo DOM.
# Vẫn soát bằng mắt ở tN_small.jpg (cỡ điện thoại).
FIT = """<script>(function(){const M=40,W=1920,H=1080;const fit=function(){
document.querySelectorAll('.big,.pill,.tag,[data-fit]').forEach(function(e){if(!e.dataset.f0)e.dataset.f0=parseFloat(getComputedStyle(e).fontSize);
const f0=+e.dataset.f0;let f=f0;e.style.fontSize=f+'px';let r=e.getBoundingClientRect();
while((r.right>W-M||r.left<M||r.bottom>H-M)&&f>f0*0.4){f*=0.97;e.style.fontSize=f+'px';r=e.getBoundingClientRect();}e.dataset.fs=Math.round(f);});};
fit();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(fit);})();</script>
"""


# ---------------- lint thumbnail ----------------
WORDS_WARN, WORDS_ERROR = 7, 10     # tổng số từ của chữ lớn
MIN_BIG_PX = 72                     # cỡ chữ .big tối thiểu sau khi FIT, ở khung 1920
MIN_LUMA_STD = 40                   # độ lệch chuẩn độ sáng tối thiểu của cả ảnh (0-255)
EM_WIDTH = 0.65                     # ước chiều rộng một ký tự (đơn vị em) của Be Vietnam Pro 900 in hoa
SAFE_MARGIN, FRAME_W = 40, 1920     # khớp FIT: chữ phải nằm trong khung an toàn 40 px
TINY = (168, 94)                    # cỡ feed / cột đề xuất
# Ngưỡng đo trên khung xuất 1280×720, rồi nhân theo khung thật của mẫu (thường 1920×1080).
MIN_TEXT_REF = 44
BADGE_REF = (1060, 620)
REF_FRAME = (1280, 720)


class _BigText(HTMLParser):
    """Gom chữ của phần tử ngoài cùng khớp `.big`, `.tile b` hoặc `[data-fit]` (bỏ thẻ)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.depth_hit, self.cur, self.items = [], None, None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        in_tile = any(t[1] for t in self.stack)
        hit = "big" in classes or "data-fit" in a or (tag == "b" and in_tile)
        if tag not in ("br", "img", "meta", "link", "input", "hr"):
            self.stack.append((tag, "tile" in classes or in_tile, hit and self.depth_hit is None, a))
        if hit and self.depth_hit is None and tag not in ("br", "img"):
            self.depth_hit, self.cur = len(self.stack), {"tag": tag, "attrs": a, "text": ""}

    def handle_endtag(self, tag):
        if not self.stack:
            return
        if self.depth_hit == len(self.stack) and self.cur is not None:
            self.items.append(self.cur)
            self.depth_hit, self.cur = None, None
        self.stack.pop()

    def handle_data(self, data):
        if self.cur is not None:
            self.cur["text"] += data


def big_texts(html: str) -> list[dict]:
    html = re.sub(r"<(script|style)\b.*?</\1>", "", html, flags=re.S | re.I)
    p = _BigText()
    p.feed(html)
    return p.items


def _css_size(html: str, cls: str) -> float | None:
    m = re.search(r"\." + re.escape(cls) + r"\s*\{[^}]*?font-size:\s*([\d.]+)px", html)
    return float(m.group(1)) if m else None


def fitted_size(html: str, item: dict) -> float | None:
    """Cỡ chữ sau FIT, tính từ mẫu: cỡ gốc (inline hoặc .big{}) co 0,97 mỗi bước tới khi ước chiều rộng
    (ký tự x EM_WIDTH x cỡ) nằm trong khung an toàn; sàn 40% cỡ gốc như script FIT."""
    style = item["attrs"].get("style") or ""
    m = re.search(r"font-size:\s*([\d.]+)px", style)
    f0 = float(m.group(1)) if m else _css_size(html, "big")
    if f0 is None:
        return None
    left = re.search(r"(?<![-\w])left:\s*(-?[\d.]+)px", style)
    left = float(left.group(1)) if left else 0.0
    text = " ".join(item["text"].split())
    f = f0
    while f > f0 * 0.4 and left + len(text) * EM_WIDTH * f > FRAME_W - SAFE_MARGIN:
        f *= 0.97
    return f


def lint_html(html: str) -> tuple[list[str], list[str]]:
    """(a) số từ chữ lớn, (b) cỡ chữ .big sau FIT. Trả (cảnh báo, lỗi)."""
    warns, errs = [], []
    items = big_texts(html)
    words = sum(len(i["text"].split()) for i in items)
    if words > WORDS_ERROR:
        errs.append(f"chữ lớn {words} từ (> {WORDS_ERROR}): rút còn 3-5 từ để đọc được ở cỡ điện thoại")
    elif words > WORDS_WARN:
        warns.append(f"chữ lớn {words} từ (> {WORDS_WARN}): nên rút gọn")
    for i in items:
        if "big" not in (i["attrs"].get("class") or "").split():
            continue
        size = i["attrs"].get("data-fs")
        size = float(size) if size else fitted_size(html, i)
        if size is not None and size < MIN_BIG_PX:
            errs.append(f"chữ {' '.join(i['text'].split())!r} chỉ {size:.0f}px sau FIT (< {MIN_BIG_PX}px): rút chữ hoặc tách dòng")
    return warns, errs


def _frame_size(html: str) -> tuple[float, float]:
    width = re.search(r'data-width="([\d.]+)"', html)
    height = re.search(r'data-height="([\d.]+)"', html)
    return (float(width.group(1)) if width else 1920.0, float(height.group(1)) if height else 1080.0)


def _style_px(style: str, name: str) -> float | None:
    match = re.search(rf"(?<![\w-]){name}\s*:\s*(-?[\d.]+)px", style or "")
    return float(match.group(1)) if match else None


def _css_rules(html: str) -> list[tuple[str, str]]:
    rules = []
    for block in re.findall(r"<style[^>]*>(.*?)</style>", html, flags=re.S | re.I):
        for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", block):
            for one in selector.split(","):
                one = " ".join(one.split())
                if one and not one.startswith("@"):
                    rules.append((one, body))
    return rules


def _simple_match(selector: str, tag: str, classes: list[str]) -> bool:
    if selector.startswith(".") and selector[1:] in classes:
        return True
    if selector == tag:
        return True
    if "." in selector:
        element, class_name = selector.split(".", 1)
        return (element == "" or element == tag) and class_name in classes
    return False


def _selector_match(selector: str, tag: str, classes: list[str], parents: list[tuple[str, list[str]]]) -> bool:
    parts = selector.split()
    if not parts or not _simple_match(parts[-1], tag, classes):
        return False
    index = len(parents) - 1
    for part in reversed(parts[:-1]):
        found = False
        while index >= 0:
            parent_tag, parent_classes = parents[index][0], parents[index][1]
            index -= 1
            if _simple_match(part, parent_tag, parent_classes):
                found = True
                break
        if not found:
            return False
    return True


def _specificity(selector: str) -> int:
    return sum(10 if part.startswith(".") or "." in part else 1 for part in selector.split())


def _declared(style: str, rules, tag, classes, parents, prop: str) -> str | None:
    inline = re.search(rf"(?<![\w-]){prop}\s*:\s*([^;]+)", style or "")
    if inline:
        return inline.group(1).strip()
    best, score = None, -1
    for index, (selector, body) in enumerate(rules):
        if not _selector_match(selector, tag, classes, parents):
            continue
        found = re.search(rf"(?<![\w-]){prop}\s*:\s*([^;]+)", body)
        if not found:
            continue
        spec = _specificity(selector) * 1000 + index
        if spec >= score:
            score, best = spec, found.group(1).strip()
    return best


def _px_value(value: str | None) -> float | None:
    if not value:
        return None
    match = re.search(r"-?[\d.]+", value)
    return float(match.group(0)) if match and value.rstrip().endswith("px") else None


class _TextElements(HTMLParser):
    """Phần tử có chữ trực tiếp. Bỏ script/style/svg."""

    _VOID = {"br", "img", "meta", "link", "input", "hr", "source", "area", "base", "col", "embed", "wbr"}
    _SKIP = {"script", "style", "svg"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.items, self.skip = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self._VOID:
            return
        if tag in self._SKIP or self.skip:
            self.skip += 1
            self.stack.append({"skip": True, "tag": tag})
            return
        attrs = dict(attrs)
        self.stack.append({"skip": False, "tag": tag, "class": (attrs.get("class") or "").split(),
                           "style": attrs.get("style") or "", "text": ""})

    def handle_startendtag(self, tag, attrs):
        if tag in self._VOID or tag in self._SKIP:
            return
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in self._VOID:
            return
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].get("tag") == tag:
                element = self.stack.pop(index)
                del self.stack[index:]
                if element.get("skip"):
                    self.skip = max(0, self.skip - 1)
                elif " ".join(element.get("text", "").split()):
                    element["parents"] = [(item["tag"], item["class"], item.get("style") or "") for item in self.stack if not item.get("skip")]
                    self.items.append(element)
                return

    def handle_data(self, data):
        if self.stack and not self.stack[-1].get("skip"):
            self.stack[-1]["text"] += data


def _glyph_box(item: dict, font: float, frame: tuple[float, float], rules) -> tuple[float, float, float, float] | None:
    style = item["style"]
    parents = item["parents"]
    left = _style_px(style, "left")
    top = _style_px(style, "top")
    right = _style_px(style, "right")
    bottom = _style_px(style, "bottom")
    align = (_declared(style, rules, item["tag"], item["class"], parents, "text-align") or "").lower()
    line_height = _px_value(_declared(style, rules, item["tag"], item["class"], parents, "line-height") or "")
    if line_height is None:
        raw = _declared(style, rules, item["tag"], item["class"], parents, "line-height")
        match = re.search(r"^[\d.]+$", raw or "")
        line_height = float(match.group(0)) if match else 1.15
        height = font * line_height
    else:
        height = line_height
    text = " ".join(item["text"].split())
    width = max(1, len(text)) * EM_WIDTH * font
    centered = "translateX(-50%" in style or "translate(-50%" in style
    frame_w, frame_h = frame
    if (left is None and right is None) or (top is None and bottom is None):
        return _ancestor_box(parents, frame)
    if left is not None and right is not None:
        box_left, box_right = left, frame_w - right
        inner = max(0.0, box_right - box_left)
        if align == "center" or centered:
            x0 = box_left + max(0.0, (inner - width) / 2)
        elif align == "right":
            x0 = box_right - width
        else:
            x0 = box_left
    elif right is not None:
        x1 = frame_w - right
        x0 = (x1 - width / 2) if centered else (x1 - width)
    else:
        x0 = (left - width / 2) if centered else left
    if top is not None:
        y0 = top
    else:
        y0 = frame_h - bottom - height
    return (x0, y0, x0 + width, y0 + height)


def _ancestor_box(parents, frame) -> tuple[float, float, float, float] | None:
    """Chữ không tự định vị thì nằm trong hộp tổ tiên. Hộp gần bằng cả khung thì bỏ (không đoán được chỗ chữ)."""
    frame_w, frame_h = frame
    for parent in reversed(parents):
        style = parent[2] if len(parent) > 2 else ""
        left, top = _style_px(style, "left"), _style_px(style, "top")
        width, height = _style_px(style, "width"), _style_px(style, "height")
        if None in (left, top, width, height):
            continue
        if width > frame_w * 0.9 and height > frame_h * 0.9:
            continue
        return (left, top, left + width, top + height)
    return None


def text_elements(html: str) -> list[dict]:
    html_body = re.sub(r"<(script|style)\b.*?</\1>", "", html, flags=re.S | re.I)
    parser = _TextElements()
    parser.feed(html_body)
    rules = _css_rules(html)
    frame = _frame_size(html)
    items = []
    for element in parser.items:
        parents = element["parents"]
        font = _px_value(_declared(element["style"], rules, element["tag"], element["class"], parents, "font-size"))
        element["font"] = font
        element["box"] = _glyph_box(element, font or MIN_TEXT_REF, frame, rules)
        element["frame"] = frame
        items.append(element)
    return items


def _hits_badge(box, frame) -> bool:
    if box is None:
        return False
    frame_w, frame_h = frame
    badge_x = BADGE_REF[0] * frame_w / REF_FRAME[0]
    badge_y = BADGE_REF[1] * frame_h / REF_FRAME[1]
    x0, y0, x1, y1 = box
    return x1 > badge_x and y1 > badge_y and x0 < frame_w and y0 < frame_h


def lint_feed(html: str) -> tuple[list[str], list[str]]:
    """(d) thiếu <img> là cảnh báo. (e) chữ < 44px khung 1280, hoặc chữ trong badge thời lượng, là lỗi."""
    warns, errs = [], []
    if not re.search(r"<img\b", html, re.I):
        warns.append("không có <img> chủ thể")
    frame = _frame_size(html)
    min_px = MIN_TEXT_REF * frame[0] / REF_FRAME[0]
    for element in text_elements(html):
        text = " ".join(element["text"].split())
        font = element.get("font")
        if font is not None and font < min_px:
            errs.append(f"chữ {text!r} cỡ {font:.0f}px nhỏ hơn 44px khung 1280 (ngưỡng {min_px:.0f}px trên khung {frame[0]:.0f})")
        if _hits_badge(element.get("box"), frame):
            errs.append(f"chữ {text!r} nằm trong vùng badge thời lượng")
    return warns, errs


def lint_image(path: Path) -> list[str]:
    """(c) ảnh phẳng, bạc màu: độ lệch chuẩn độ sáng toàn ảnh < MIN_LUMA_STD."""
    from PIL import Image, ImageStat
    with Image.open(path) as im:
        std = ImageStat.Stat(im.convert("L")).stddev[0]
    if std < MIN_LUMA_STD:
        return [f"ảnh phẳng, thiếu tương phản (độ lệch chuẩn độ sáng {std:.0f} < {MIN_LUMA_STD}): đậm nền hoặc sáng chữ"]
    return []


def lint(name: str, html: str, jpg: Path | None) -> tuple[list[str], list[str]]:
    warns, errs = lint_html(html)
    feed_warns, feed_errs = lint_feed(html)
    warns += feed_warns
    errs += feed_errs
    if jpg is not None and jpg.exists():
        errs += lint_image(jpg)
    for w in warns:
        print(f"THUMB LINT: CẢNH BÁO {name}: {w}", flush=True)
    for e in errs:
        print(f"THUMB LINT: LỖI {name}: {e}", flush=True)
    if not warns and not errs:
        print(f"THUMB LINT: {name}: OK", flush=True)
    return warns, errs


def main(topic: str, only: list[str], allow: bool = False, lint_only: bool = False) -> int:
    failed = []
    od = ROOT / "output" / "long" / topic
    for src in sorted((HERE / "thumbs").glob(f"{topic}_t*.html")):
        t = src.stem.rsplit("_", 1)[1]
        if only and t not in only:
            continue
        if lint_only:
            if lint(src.stem, src.read_text(encoding="utf-8"), od / f"{t}.jpg")[1]:
                failed.append(src.stem)
            continue
        comp = BL.HF / "compositions" / "long" / f"_{topic}_{t}.html"
        html = src.read_text(encoding="utf-8")
        assert "</body>" in html, f"{src.name}: thiếu </body>"
        comp.write_text(html.replace("</body>", FIT + "</body>", 1), encoding="utf-8")
        mp4 = od / f"_{t}.mp4"
        from factory.render_lock import render_lock      # một render một lúc trên cả máy
        with render_lock(f"thumb {topic} {t}"):
            r = subprocess.run(["npx.cmd", "-y", "-p", "node@22", "-p", "hyperframes@0.8.75", "hyperframes", "render", ".", "-c",
                                f"compositions/long/{comp.name}", "-o", str(mp4), "--fps", "30", "--quiet", "--crf", "12"],
                               cwd=BL.HF, capture_output=True, text=True, encoding="utf-8", errors="replace")
        comp.unlink(missing_ok=True)
        if r.returncode != 0 or not mp4.exists():
            raise SystemExit(f"{t}: render hỏng\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
        for name, vf, q in ((f"{t}.jpg", "scale=1280:-2:flags=lanczos", 2),
                            (f"{t}_small.jpg", "scale=320:-2:flags=lanczos", 3),
                            (f"{t}_tiny.jpg", f"scale={TINY[0]}:{TINY[1]}:flags=lanczos", 4)):
            subprocess.run([BL.FFMPEG, "-v", "error", "-y", "-i", str(mp4), "-frames:v", "1", "-vf", vf,
                            "-q:v", str(q), str(od / name)], check=True)
        mp4.unlink()
        print(od / f"{t}.jpg")
        if lint(src.stem, html, od / f"{t}.jpg")[1]:
            failed.append(src.stem)
    if failed and not allow:
        print(f"THUMB LINT: {len(failed)} thumbnail lỗi ({', '.join(failed)}); sửa mẫu hoặc chạy lại với --allow-thumb nếu cố ý", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from factory.console import utf8_console  # noqa: E402
    utf8_console()  # console Windows cp1252 không in được tiếng Việt (retro 2 mục 7)
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    raise SystemExit(main(argv[0], argv[1:], "--allow-thumb" in sys.argv, "--lint-only" in sys.argv))
