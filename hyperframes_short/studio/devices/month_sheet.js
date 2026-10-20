/* Tờ lịch tháng. Lưới chiếm tới sát dải phụ đề; vòng chỉ khoanh số dương. */
HFS.device("month_sheet", {
  meta: { purpose: "time", framing: "grid", axis: "draw", circle: 0, energy: "M" },
  css: `.ms-title{position:absolute;left:36px;right:36px;text-align:center;font-size:68px;line-height:1;color:var(--accent)}
        .ms-note{position:absolute;left:48px;right:48px;text-align:center;font-size:28px;font-weight:700;color:var(--ink-soft)}
        .ms-w{position:absolute;text-align:center;font-family:var(--font-mono);font-weight:800;font-size:26px;letter-spacing:.04em;color:var(--ink)}
        .ms-w.sun{color:var(--accent)}
        .ms-c{position:absolute;overflow:hidden;background:var(--card);box-shadow:inset 0 -2px 0 var(--line)}
        .ms-d{position:absolute;left:0;right:0;text-align:center;line-height:.86;letter-spacing:-.04em;font-weight:800;color:var(--ink);white-space:nowrap}
        .ms-c.good .ms-d{color:var(--accent)}
        .ms-a{position:absolute;left:2px;right:2px;text-align:center;font-weight:800;line-height:1.05;color:var(--accent);white-space:nowrap}
        .ms-band{position:absolute;left:36px;right:36px;background:var(--card);border:3px solid var(--accent);box-shadow:0 8px 0 var(--line)}
        .ms-lab{position:absolute;left:16px;right:16px;text-align:center;font-family:var(--font-mono);font-weight:800;letter-spacing:.14em;color:var(--accent)}
        .ms-sl{position:absolute;left:20px;right:20px;text-align:center;font-weight:800;line-height:1.15;color:var(--ink)}
        .ms-svg{position:absolute;left:0;top:0}`,
  cssW: `.ms-title{position:absolute;left:160px;right:160px;text-align:center;font-size:48px;color:var(--accent)}
        .ms-note{position:absolute;left:160px;right:160px;text-align:center;font-size:22px}
        .ms-sl{position:absolute;left:180px;right:180px;text-align:center;font-size:26px;font-weight:800}
        .ms-band{position:absolute;left:160px;right:160px;border:3px solid var(--accent);background:var(--card)}`,
  build(c, s, st) {
    const wide = !!(c.L && c.L.wide);
    const wrap = c.el("div", "ms", null, st);
    wrap.setAttribute("data-layout-allow-overlap", "");
    const weeks = s.weeks || [];
    const lines = s.strip || [];
    const n = Math.max(1, weeks.length);
    const nLines = Math.max(1, lines.length);
    const W = wide ? 1920 : 1080;
    const gridTop = wide ? 210 : 396;
    const bottom = wide ? 820 : 1484;
    const lineH = wide ? 34 : 42;
    const labelH = wide ? 28 : 36;
    const bandH = Math.max(wide ? 120 : 156, labelH + nLines * lineH + (wide ? 16 : 22));
    const gridBot = bottom - bandH - (wide ? 8 : 10);
    const gapY = 4;
    const ch = Math.floor((gridBot - gridTop - gapY * (n - 1)) / n);
    const lft = wide ? 170 : 20;
    const right = wide ? 170 : 28;
    const gapX = 4;
    const cols = 7;
    const cw = (W - lft - right - gapX * (cols - 1)) / cols;
    const numSize = Math.min(wide ? 64 : 116, Math.floor(ch * 0.62), Math.floor(cw * 0.78));
    const amSize = Math.max(16, Math.min(wide ? 18 : 24, Math.floor(ch * 0.15)));

    const title = c.el("div", "ms-title disp", c.esc(s.title || ""), wrap);
    title.style.top = (wide ? 86 : 246) + "px";
    const note = c.el("div", "ms-note", c.esc(s.note || ""), wrap);
    note.style.top = (wide ? 142 : 322) + "px";
    (s.wd || []).forEach((w, col) => {
      const e = c.el("div", "ms-w" + (col === 0 ? " sun" : ""), c.esc(w), wrap);
      e.style.left = (lft + col * (cw + gapX)) + "px";
      e.style.width = cw + "px";
      e.style.top = (gridTop - (wide ? 28 : 34)) + "px";
    });

    const pos = {};
    weeks.forEach((week, r) => {
      week.forEach((cell, col) => {
        const x = lft + col * (cw + gapX);
        const y = gridTop + r * (ch + gapY);
        const box = c.el("div", "ms-c" + (cell && cell.good ? " good" : ""), null, wrap);
        box.style.left = x + "px";
        box.style.top = y + "px";
        box.style.width = cw + "px";
        box.style.height = ch + "px";
        if (!cell) return;
        const num = c.el("div", "ms-d disp", c.esc(String(cell.d)), box);
        const numTop = 4;
        num.style.top = numTop + "px";
        num.style.fontSize = numSize + "px";
        const amTop = ch - amSize - 6;
        const am = c.el("div", "ms-a", c.esc(cell.am), box);
        am.style.top = amTop + "px";
        am.style.fontSize = amSize + "px";
        const cy = y + numTop + numSize * 0.42;
        const stroke = 6;
        const ryMax = (y + amTop - 18) - cy - stroke / 2;
        const ry = Math.max(16, Math.min(ryMax / 1.02, numSize * 0.4));
        const rx = Math.min(cw / 2 - 8, numSize * 0.7);
        pos[cell.d] = { x: x + cw / 2, y: cy, rx: rx, ry: ry };
      });
    });

    const svg = c.sv("svg", { class: "ms-svg", width: W, height: wide ? 1080 : 1920, viewBox: "0 0 " + W + " " + (wide ? 1080 : 1920) }, wrap);
    svg.setAttribute("data-layout-allow-overlap", "");
    const circles = (s.goods || []).map((g, i) => {
      const p = pos[g.day];
      if (!p) return null;
      return c.sv("path", {
        d: msOval(p.x, p.y, p.rx, p.ry, i),
        fill: "none", stroke: "var(--accent)", "stroke-width": 6,
        "stroke-linecap": "round", "stroke-linejoin": "round",
      }, svg);
    });

    const band = c.el("div", "ms-band", null, wrap);
    band.style.top = (gridBot + 8) + "px";
    band.style.height = (bottom - gridBot - 8) + "px";
    const lab = c.el("div", "ms-lab", c.esc(s.stripLab || "TRỰC VÀ TUỔI XUNG"), band);
    lab.style.top = "12px";
    lab.style.fontSize = (wide ? 16 : 24) + "px";
    const innerTop = labelH;
    const slot = Math.max(lineH, Math.floor(((bottom - gridBot - 8) - innerTop - 12) / nLines));
    lines.forEach((line, i) => {
      const e = c.el("div", "ms-sl", c.esc(line), band);
      e.style.top = (innerTop + i * slot) + "px";
      e.style.fontSize = Math.min(wide ? 26 : 40, slot - 4) + "px";
    });
    return { circles };
  },
  enter(c, h, t0, s) {
    (s.goods || []).forEach((g, i) => {
      if (h.circles[i]) c.draw(h.circles[i], Math.max(0, c.t(g.at, t0 + 0.8 + i * 1.4)), 0.7);
    });
  },
});

function msOval(cx, cy, rx, ry, key) {
  const n = 28;
  let d = "";
  for (let i = 0; i <= n; i++) {
    const a = -Math.PI / 2 + (i / n) * Math.PI * 2;
    const wob = 1 + (((i * 3 + key * 2) % 5) - 2) * 0.016;
    const x = cx + Math.cos(a) * rx * wob;
    const y = cy + Math.sin(a) * ry * (1 + (((i + key) % 3) - 1) * 0.01);
    d += (i ? " L" : "M") + x.toFixed(1) + " " + y.toFixed(1);
  }
  return d;
}
