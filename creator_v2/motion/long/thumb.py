"""Render thumbnail từ mẫu HTML: motion/long/thumbs/<topic>_tN.html -> output/long/<topic>/tN.jpg (1280x720, < 2 MB)
+ tN_small.jpg (320x180) để soi ở cỡ mobile.

    python motion/long/thumb.py <topic> [t1 t2 ...] [--allow-thumb] [--lint-only]

Sau khi dựng, in các dòng `THUMB LINT:` và thoát mã 1 nếu có lỗi (CTR thumbnail 0,x-1,x%, 09/11/2026):
  (a) chữ lớn (.big, `.tile b`, [data-fit]) > 7 từ là cảnh báo, > 10 từ là lỗi;
  (b) chữ .big sau khi FIT co lại nhỏ hơn 72 px ở khung 1920 là lỗi (không đọc được ở cỡ điện thoại);
  (c) ảnh phẳng, bạc màu: độ lệch chuẩn độ sáng toàn ảnh < 40 là lỗi.
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
        for name, w, q in ((f"{t}.jpg", 1280, 2), (f"{t}_small.jpg", 320, 3)):
            subprocess.run([BL.FFMPEG, "-v", "error", "-y", "-i", str(mp4), "-frames:v", "1", "-vf", f"scale={w}:-2:flags=lanczos",
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
