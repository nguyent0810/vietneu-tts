"""Non-rendering composition helpers and the existing HyperFrames bridge call."""

import subprocess
import base64
import io
import json
from pathlib import Path

from PIL import Image, ImageEnhance


def image_data(image_path: Path) -> str:
    """Encode the production crop/brightness adjusted image as WEBP data URL."""
    image = Image.open(image_path).convert("RGB")
    scale = 1920 / image.height
    image = image.resize((round(image.width * scale), 1920), Image.LANCZOS)
    left = (image.width - 1080) // 2
    image = image.crop((left, 0, left + 1080, 1920))
    image = ImageEnhance.Brightness(image).enhance(0.95)
    buf = io.BytesIO()
    image.save(buf, "WEBP", quality=82)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def bud_html(row, times, duration, image_path, *, font_css, candidate_b=False):
    """Build one BUD 138g composition from row data and resolved timing/media."""
    from .css import BASE_CSS
    from .guards import validate

    row = dict(row)
    img = image_data(Path(image_path))
    accent, ink = row["acc"]
    cards = row["cards"]
    card_html = "".join(f'<div class="card" id="c{i}">{card}</div>' for i, card in enumerate(cards) if card)
    shown = [i for i, card in enumerate(cards) if card]
    commands = []
    for i in shown:
        nxt = next((j for j in range(i + 1, len(cards)) if cards[j]), len(times) - 1)
        commands.append(f'show("#c{i}", T[{i}]); hide("#c{i}", T[{nxt}]);')
    title_suffix = "_b" if candidate_b else ""
    head = row["head_b"] if candidate_b else row["head"]
    html = f'''<!doctype html><html lang="vi"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" /><title>{row['id']}{title_suffix}</title>
<style>{font_css}{BASE_CSS}
#root {{ background: #0a0807; }}
#photo {{ left: 0; top: 0; width: 1080px; height: 1920px; z-index: 1; transform-origin: 540px 700px; }}
#photo img {{ width: 100%; height: 100%; display: block; }}
#shade {{ left: 0; top: 0; width: 1080px; height: 1920px; z-index: 2;
  background: linear-gradient(180deg, rgba(10,8,7,0.9) 0px, rgba(10,8,7,0.75) 250px, rgba(10,8,7,0) 440px),
    linear-gradient(0deg, rgba(8,6,5,0.96) 0px, rgba(8,6,5,0.9) 330px, rgba(8,6,5,0.62) 560px, rgba(8,6,5,0) 800px); }}
#chip {{ background: {accent}; color: {ink}; }}
.warm {{ color: {accent}; }}
.card {{ top: 1250px; }}
#footer {{ top: 1745px; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{duration:.2f}" data-width="1080" data-height="1920">
  <div id="photo" class="abs"><img src="{img}" alt="" /></div>
  <div id="shade" class="abs"></div>
  <div id="header"><div id="chip">{row['chip']}</div><div id="title">{head}</div></div>
  {card_html}
  <div id="footer"><div id="src">{row['srcline']}</div></div>
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }}); window.__timelines.main = tl;
const T = {json.dumps(times)};
const show = (id, at) => tl.fromTo(id, {{opacity: 0, y: 26}}, {{opacity: 1, y: 0, duration: 0.6, ease: "expo.out"}}, at);
const hide = (id, at) => tl.to(id, {{opacity: 0, y: -18, duration: 0.45, ease: "power1.in"}}, at - 0.45);
tl.fromTo("#photo", {{scale: 1.0}}, {{scale: 1.05, duration: T[T.length - 1] + 1, ease: "none"}}, 0);
{' '.join(commands)}
</script></body></html>'''
    validate([row], html)
    return html


def render(composition: Path, output: Path, *, hyperframes_dir: Path, fps=30, quality="looks"):
    """Render an already-written HTML composition using HyperFrames CLI."""
    composition, output, hyperframes_dir = map(Path, (composition, output, hyperframes_dir))
    return subprocess.run([
        "npx", "--yes", "hyperframes@0.8.75", "render", ".", "-c",
        str(composition), "--output", str(output), "--quality", quality,
        "--fps", str(fps), "--quiet",
    ], cwd=hyperframes_dir, check=True)
