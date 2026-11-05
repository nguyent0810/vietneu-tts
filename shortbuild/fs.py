"""Production FS year-table and month-sheet HTML formatters, migrated from FS legacy."""
from __future__ import annotations
import json
from pathlib import Path

def yeartable_html(t: dict, dur: float, segs: list[dict], *, template_path: Path, fonts: str) -> str:
    """Yeartable 9.5-11.5s based on review_yeartable.html with proven layout fixes."""
    base = template_path.read_text(encoding="utf-8")
    
    theme_amber = (
        'amber: { b1: "#d97706", b2: "#b45309", b3: "#78350f", b4: "#451a03", '
        'r1: "rgba(120,53,15,.94)", r2: "rgba(69,26,3,.94)", gold: "#fde68a", gold2: "#fef08a", '
        'chip: "#fffbeb", chipfg: "#78350f", chiptop: "#fde68a", chiptopfg: "#78350f" },'
    )
    if "amber:" not in base:
        base = base.replace("const THEMES = {", f"const THEMES = {{\n    {theme_amber}")

    layout_override = """
  #head { top: 90px; }
  #title .gold { font-size: 72px !important; }
  #rows { top: 430px; bottom: 310px; gap: 14px; }
  .row, #rows.big .row { padding: 12px 18px; }
  .years.col4 { grid-template-columns: repeat(4, 1fr) !important; gap: 8px 10px !important; }
  .years.col4 .y, #rows.big .years.col4 .y { font-size: 52px !important; padding: 6px 0 !important; border-radius: 14px !important; white-space: nowrap !important; }
  #cap { bottom: 195px; font-size: 44px; }
  #subfoot { position: absolute; left: 50px; right: 50px; bottom: 120px; text-align: center;
             color: var(--gold2); font-weight: 800; font-size: 32px; letter-spacing: .05em;
             text-shadow: 0 2px 8px rgba(0,0,0,.6); }
  #foot { bottom: 65px; font-size: 24px; opacity: .82; }
  #root.ivory #subfoot { color: #b01e14; text-shadow: none; }
  #root.ivory #foot { color: #7a1410; }
  .chi.sm { font-size: 38px !important; line-height: 1.1 !important; }
"""
    base = base.replace("</style>", layout_override + "</style>")
    subfoot_div = '<div id="subfoot">DỪNG HÌNH TÌM NĂM SINH CỦA BẠN</div>'
    base = base.replace('<div id="foot">', f"{subfoot_div}\n  <div id=\"foot\">")

    old_big = 'if ((DATA.rows || []).length && DATA.rows.length <= 3) rows.classList.add("big");'
    new_big = (
        'const maxYears = Math.max(...(DATA.rows || []).map(r => (r.years || []).length), 0);\n'
        '  if ((DATA.rows || []).length && DATA.rows.length <= 3 && maxYears < 7) rows.classList.add("big");'
    )
    base = base.replace(old_big, new_big)

    old_row_gen = '<div class="years">${r.years.map((y) => `<span class="y">${y}</span>`).join("")}</div>'
    new_row_gen = (
        '<div class="years${r.years && r.years.length >= 7 ? " col4" : ""}">'
        '${r.years.map((y) => `<span class="y">${y}</span>`).join("")}</div>'
    )
    base = base.replace(old_row_gen, new_row_gen)

    # SS-tier hold frame fix: freeze all animations in the last >= 3.0s
    old_onupdate = """  tl.to(st, { t: DUR, duration: DUR, ease: "none", onUpdate: () => {
    const t = st.t, p = t / DUR;           // p: 0 -> 1, khung cuối = khung đầu (lặp liền)
    svg.style.transform = `rotate(${p * 45}deg)`;   // 45 độ = một quẻ -> trùng khung đầu
    document.getElementById("glow").style.opacity = 0.85 + 0.15 * Math.sin(p * Math.PI * 2);
    SP.forEach((o) => { o.d.style.opacity = 0.25 + 0.6 * (0.5 + 0.5 * Math.sin(o.ph + p * Math.PI * 2 * Math.round(o.sp * 2))); });  // số vòng nguyên -> lặp liền
    // dải sáng quét từng hàng trong 75% đầu, rồi nghỉ
    // vệt cuối xong trước 85% thời lượng (bảng 6 hàng từng kẹt ở khung cuối)
    shines.forEach((el, i) => { const a = 0.12 + i * (0.5 / Math.max(1, shines.length - 1)), q = (p - a) / 0.22; el.style.transform = `translateX(${-260 + Math.min(Math.max(q, 0), 1) * 1300}px)`; el.style.opacity = q > 0 && q < 1 ? 1 : 0; });
    // viên năm sinh sáng lần lượt (nhịp nhẹ)
    ys.forEach((el, i) => { const q = Math.sin((p * ys.length * 0.5 - i * 0.5) * Math.PI); el.style.transform = `scale(${1 + Math.max(q, 0) * 0.035})`; });
    // phụ đề: câu đang đọc
    const cur = DATA.segs.find((sg) => t >= sg.start - 0.05 && t < sg.end + 0.25);
    if (cur) {
      if (cap.dataset.s !== cur.text) { cap.dataset.s = cur.text; cap.innerHTML = words.filter((w) => w.s === cur).map((w) => `<span class="cw" data-t="${w.t}">${w.w}</span>`).join(" "); }
      cap.querySelectorAll(".cw").forEach((e) => e.classList.toggle("on", +e.dataset.t <= t + 0.02));
      cap.style.opacity = 1;
    } else { cap.style.opacity = 0; }
  } });"""

    new_onupdate = """  const tStop = (DATA.segs && DATA.segs.length) ? DATA.segs[DATA.segs.length - 1].end : Math.max(1.0, DUR - 3.2);
  tl.to(st, { t: DUR, duration: DUR, ease: "none", onUpdate: () => {
    const t = st.t;
    const p = Math.min(1.0, t / tStop);
    svg.style.transform = `rotate(${p * 45}deg)`;
    document.getElementById("glow").style.opacity = 0.85 + 0.15 * Math.sin(p * Math.PI * 2);
    SP.forEach((o) => { o.d.style.opacity = 0.25 + 0.6 * (0.5 + 0.5 * Math.sin(o.ph + p * Math.PI * 2 * Math.round(o.sp * 2))); });
    shines.forEach((el, i) => { const a = 0.12 + i * (0.5 / Math.max(1, shines.length - 1)), q = (p - a) / 0.22; el.style.transform = `translateX(${-260 + Math.min(Math.max(q, 0), 1) * 1300}px)`; el.style.opacity = q > 0 && q < 1 ? 1 : 0; });
    ys.forEach((el, i) => { const q = Math.sin((p * ys.length * 0.5 - i * 0.5) * Math.PI); el.style.transform = `scale(${1 + Math.max(q, 0) * 0.035})`; });

    const cur = t < tStop ? DATA.segs.find((sg) => t >= sg.start - 0.05 && t < sg.end) : null;
    if (cur) {
      if (cap.dataset.s !== cur.text) { cap.dataset.s = cur.text; cap.innerHTML = words.filter((w) => w.s === cur).map((w) => `<span class="cw" data-t="${w.t}">${w.w}</span>`).join(" "); }
      cap.querySelectorAll(".cw").forEach((e) => e.classList.toggle("on", +e.dataset.t <= t + 0.02));
      cap.style.opacity = 1;
    } else { cap.style.opacity = 0; }
  } });"""

    base = base.replace(old_onupdate, new_onupdate)

    # Replace local fonts
    base = base.replace(
        '<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@500;700;800;900&display=swap" rel="stylesheet" />',
        f"<style>\n{fonts}\n</style>"
    )

    data = {
        "dur": dur,
        "theme": t.get("theme", "red"),
        "segs": segs,
        "rows": [{"chi": c, "tag": tag, "years": ys} for c, tag, ys in t["rows"]]
    }

    title_val = t.get("title_html") or t["title"]
    html = (
        base.replace("__DUR__", str(dur))
        .replace("__CHIP__", t["chip"])
        .replace("__TITLE__", title_val)
        .replace("__DATA__", json.dumps(data, ensure_ascii=False))
    )
    return html


def month_sheet_html(t: dict, dur: float, segs: list[dict], *, fonts: str, days: list[dict], offset: int, month_label: str, total_days: str, good_days: str) -> str:
    """December 2026 month sheet calendar with full AA contrast and 0 overflow."""

    # 01/12/2026 is Tuesday (Thứ Ba).
    # Lưới 7 cột Thứ Hai -> Chủ Nhật.
    # Monday is empty cell (offset = 1)
    cells_html = ['<div class="cal-cell empty"></div>'] * offset

    for d_item in days:
        d = d_item["solar_day"]
        l_str = d_item["lunar_str"]
        c_type = d_item["cell_type"]

        corner_html = '<div class="corner-red" data-layout-allow-overflow></div>' if c_type == "gold-tn" else ''
        cell_str = f"""
      <div class="cal-cell {c_type}" id="day-cell-{d}">
        {corner_html}
        <div class="day-solar">{d}</div>
        <div class="day-lunar">{l_str}</div>
      </div>"""
        cells_html.append(cell_str)

    # Fill remaining cells to complete 5 full weeks (35 cells)
    while len(cells_html) < 35:
        cells_html.append('<div class="cal-cell empty"></div>')

    grid_content = "\n".join(cells_html)
    segs_json = json.dumps(segs, ensure_ascii=False)

    html = f"""<!doctype html>
<html lang="vi" data-needs-fit="1">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<style>
{fonts}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; padding: 0; width: 1080px; height: 1920px; overflow: hidden;
      background: #070b14; font-family: "Be Vietnam Pro", sans-serif; }}
    #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden;
      background: radial-gradient(90% 70% at 50% 18%, #142036 0%, #0a111f 45%, #050810 100%); }}
    #grain {{ position: absolute; inset: 0; width: 1080px; height: 1920px; opacity: 0.22;
      pointer-events: none; mix-blend-mode: overlay; z-index: 20; }}
    #mountains {{ position: absolute; left: 0; bottom: 0; width: 1080px; height: 220px; pointer-events: none; z-index: 1; }}

    /* Header */
    #kicker {{ position: absolute; left: 60px; top: 118px; width: 870px; text-align: center;
      font-family: "JetBrains Mono", monospace; font-weight: 500; font-size: 24px;
      letter-spacing: 0.16em; color: #e7c56a; z-index: 4; }}
    #title {{ position: absolute; left: 60px; top: 165px; width: 870px; text-align: center;
      font-weight: 900; font-size: 54px; line-height: 1.18; letter-spacing: -0.01em; color: #f8fafc; z-index: 4; }}
    #title .gold {{ color: #fde68a; display: block; }}
    #subchip {{ position: absolute; left: 60px; top: 345px; width: 870px; display: flex; align-items: center; justify-content: center; z-index: 4; }}
    .chip-tag {{ display: inline-block; padding: 7px 28px; border-radius: 20px;
      background: rgba(231,197,106,0.12); border: 1.5px solid rgba(231,197,106,0.45);
      font-weight: 700; font-size: 22px; color: #fde68a; }}

    /* Shimmer Beam */
    #shimmer-wrap {{ position: absolute; inset: 0; overflow: hidden; pointer-events: none; z-index: 6; }}
    #shimmer-beam {{ position: absolute; top: 0; left: -140px; width: 120px; height: 100%;
      background: linear-gradient(90deg, transparent, rgba(255,255,255,0.7), transparent);
      transform: skewX(-20deg); opacity: 0; }}

    /* Month Sheet Grid */
    #calendar-wrap {{ position: absolute; left: 64px; top: 430px; width: 872px; z-index: 5; }}
    .weekday-row {{ display: grid; grid-template-columns: repeat(7, 1fr); column-gap: 8px; margin-bottom: 8px; }}
    .wd {{ text-align: center; font-family: "JetBrains Mono", monospace; font-size: 24px; font-weight: 800; color: #e7c56a; }}
    .wd.sun {{ color: #f87171; }}

    .month-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); grid-template-rows: repeat(5, 156px); gap: 8px; }}
    .cal-cell {{ position: relative; border-radius: 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; overflow: hidden; }}
    .cal-cell.empty {{ background: rgba(15, 23, 42, 0.25); border: 1px dashed rgba(100, 116, 139, 0.15); }}

    /* Day typography */
    .day-solar {{ font-size: 64px; font-weight: 900; line-height: 1; margin-top: 4px; }}
    .day-lunar {{ font-size: 30px; font-weight: 700; line-height: 1; margin-top: 6px; }}

    /* Cell Types with High Contrast */
    .cal-cell.gold-good {{
      background: linear-gradient(145deg, rgba(234, 179, 8, 0.32) 0%, rgba(161, 98, 7, 0.45) 100%);
      border: 2px solid rgba(253, 224, 71, 0.95);
      box-shadow: inset 0 0 14px rgba(234, 179, 8, 0.25);
    }}
    .cal-cell.gold-good .day-solar {{ color: #fef08a; }}
    .cal-cell.gold-good .day-lunar {{ color: #fef9c3; }}

    .cal-cell.gold-tn {{
      background: linear-gradient(145deg, rgba(234, 179, 8, 0.32) 0%, rgba(161, 98, 7, 0.45) 100%);
      border: 2px solid rgba(253, 224, 71, 0.95);
      box-shadow: inset 0 0 14px rgba(234, 179, 8, 0.25);
    }}
    .cal-cell.gold-tn .day-solar {{ color: #fef08a; }}
    .cal-cell.gold-tn .day-lunar {{ color: #fef9c3; }}
    .corner-red {{
      position: absolute; top: 0; right: 0; width: 0; height: 0;
      border-style: solid; border-width: 0 34px 34px 0;
      border-color: transparent #ef4444 transparent transparent;
      z-index: 3;
    }}

    .cal-cell.red-bad {{
      background: linear-gradient(145deg, rgba(220, 38, 38, 0.35) 0%, rgba(153, 27, 27, 0.50) 100%);
      border: 2px solid rgba(248, 113, 113, 0.95);
      box-shadow: inset 0 0 14px rgba(239, 68, 68, 0.30);
    }}
    .cal-cell.red-bad .day-solar {{ color: #ffffff; }}
    .cal-cell.red-bad .day-lunar {{ color: #fca5a5; }}

    .cal-cell.neutral-cell {{
      background: rgba(15, 23, 42, 0.55);
      border: 1.5px solid rgba(148, 163, 184, 0.30);
    }}
    .cal-cell.neutral-cell .day-solar {{ color: #f1f5f9; }}
    .cal-cell.neutral-cell .day-lunar {{ color: #cbd5e1; }}

    /* Legend & Subfoot */
    #legend {{ position: absolute; left: 64px; top: 1334px; width: 872px; text-align: center;
      font-size: 24px; font-weight: 700; color: #fde68a; letter-spacing: 0.02em; z-index: 5; }}
    #subfoot {{ position: absolute; left: 64px; top: 1386px; width: 872px; text-align: center;
      font-size: 26px; font-weight: 800; color: #e2e8f0; letter-spacing: 0.08em; z-index: 5; }}

    /* Seal Tham Khao */
    #seal-thamkhao {{ position: absolute; left: 64px; top: 110px; width: 78px; height: 78px; z-index: 10;
      border: 3px solid #b91c1c; border-radius: 8px; background: rgba(185, 28, 28, 0.40);
      display: flex; align-items: center; justify-content: center; transform: rotate(-8deg); }}
    .seal-text {{ font-family: "Be Vietnam Pro", sans-serif; font-weight: 900; font-size: 15px;
      line-height: 1.15; color: #fecaca; text-align: center; letter-spacing: 0.05em; }}

    /* Subtitle caption */
    #caption-box {{ position: absolute; left: 60px; right: 60px; top: 1490px; text-align: center; z-index: 5; pointer-events: none; }}
    .cap-line {{ font-size: 40px; font-weight: 800; line-height: 1.32; color: #ffffff; text-shadow: 0 3px 8px rgba(0,0,0,0.85); }}
    .cw {{ opacity: 0.38; color: #ffffff; transition: color 0.1s ease, opacity 0.1s ease; }}
    .cw.on {{ opacity: 1; color: #fde68a; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
  <div id="grain" data-layout-allow-overflow></div>
  <svg id="mountains" viewBox="0 0 1080 220" fill="none" xmlns="http://www.w3.org/2000/svg" data-layout-allow-overflow>
    <path d="M0 140 Q 270 40 540 130 T 1080 120 L 1080 220 L 0 220 Z" fill="#050810" opacity="0.9"/>
  </svg>

  <div id="shimmer-wrap"><div id="shimmer-beam" data-layout-allow-overflow></div></div>
  <div id="seal-thamkhao"><div class="seal-text">THAM<br>KHẢO</div></div>

  <div id="kicker">LỊCH VẠN NIÊN · {month_label}</div>
  <div id="title">
    {month_label.replace('/', ' NĂM ')}<br/>
    <span class="gold">LỊCH NGÀY HOÀNG ĐẠO</span>
  </div>

  <div id="subchip">
    <div class="chip-tag">{total_days} NGÀY HOÀNG ĐẠO · {good_days} NGÀY THUẬN LỢI</div>
  </div>

  <div id="calendar-wrap">
    <div class="weekday-row">
      <div class="wd">T2</div>
      <div class="wd">T3</div>
      <div class="wd">T4</div>
      <div class="wd">T5</div>
      <div class="wd">T6</div>
      <div class="wd">T7</div>
      <div class="wd sun">CN</div>
    </div>
    <div class="month-grid">
{grid_content}
    </div>
  </div>

  <div id="legend">
    Vàng: hoàng đạo · Góc đỏ: trùng Tam Nương · Đỏ: ngày kỵ · Tham khảo
  </div>
  <div id="subfoot">DỪNG HÌNH LƯU LẠI LỊCH CẢ THÁNG NHÉ</div>
  <div id="caption-box"></div>
</div>

<script>
  (function() {{
    const segs = {segs_json};
    const tStop = (segs && segs.length) ? segs[segs.length - 1].end : Math.max(1.0, {dur} - 3.2);
    const capBox = document.getElementById("caption-box");

    const words = [];
    segs.forEach((sg) => {{
      const ws = sg.text.split(/\\s+/).filter(Boolean);
      ws.forEach((w, idx) => {{
        const tWord = sg.start + (sg.end - sg.start) * idx / Math.max(1, ws.length);
        words.push({{ w, t: Math.round(tWord * 100) / 100, s: sg }});
      }});
    }});

    const tl = gsap.timeline({{ paused: true }});
    window.__timelines = {{ main: tl }};

    tl.fromTo("#shimmer-beam", {{ x: 0, opacity: 0 }}, {{ x: 1080, opacity: 0.85, duration: 1.2, ease: "power1.inOut" }}, 0.6);
    tl.fromTo("#seal-thamkhao", {{ scale: 1.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.4, ease: "back.out(2)" }}, 0.4);

    const st = {{ t: 0 }};
    tl.to(st, {{
      t: {dur},
      duration: {dur},
      ease: "none",
      onUpdate: () => {{
        const curT = st.t;
        const cur = curT < tStop ? segs.find((sg) => curT >= sg.start - 0.05 && curT < sg.end) : null;
        if (cur) {{
          if (capBox.dataset.s !== cur.text) {{
            capBox.dataset.s = cur.text;
            capBox.innerHTML = '<div class="cap-line">' +
              words.filter((w) => w.s === cur).map((w) => `<span class="cw" data-t="${{w.t}}">${{w.w}}</span>`).join(" ") +
              '</div>';
          }}
          capBox.querySelectorAll(".cw").forEach((el) => {{
            el.classList.toggle("on", +el.dataset.t <= curT + 0.02);
          }});
          capBox.style.opacity = "1";
        }} else {{
          capBox.style.opacity = "0";
        }}
      }}
    }}, 0);
  }})();
</script>
</body>
</html>"""
    return html
