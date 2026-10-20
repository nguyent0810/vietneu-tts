/* Thiệp cưới. Nền đỏ đặt bằng post_css của spec; chữ chỉ dùng token. */
HFS.device("thiep_cuoi", {
  meta: { purpose: "statement", framing: "card-on-field", axis: "static", circle: 0, energy: "L" },
  css: `.tc-card{position:absolute;border:2px solid var(--accent);box-shadow:inset 0 0 0 10px var(--ground), inset 0 0 0 12px var(--accent)}
        .tc-han{position:absolute;text-align:center;font-family:var(--font-cjk);line-height:1;color:var(--ghost-accent);font-weight:700}
        .tc-eye{position:absolute;left:110px;right:150px;text-align:center;font-family:var(--font-mono);font-weight:800;
          font-size:26px;letter-spacing:.16em;color:var(--accent)}
        .tc-sub{position:absolute;left:110px;right:150px;text-align:center;font-size:40px;font-weight:800;color:var(--ink)}
        .tc-day{position:absolute;text-align:center;line-height:.9;letter-spacing:-.03em;color:var(--accent);white-space:nowrap;font-weight:800}
        .tc-day.mute{color:var(--ink);letter-spacing:0}
        .tc-am{position:absolute;font-weight:800;line-height:1.15;color:var(--ink)}
        .tc-meta{position:absolute;font-weight:700;line-height:1.2;color:var(--ink-soft)}
        .tc-note{position:absolute;left:120px;right:160px;text-align:center;font-size:34px;font-weight:800;color:var(--ink)}
        .tc-svg{position:absolute;left:0;top:0}`,
  cssW: `.tc-card{position:absolute;left:360px;top:90px;width:1200px;height:760px;border:2px solid var(--accent)}
        .tc-day{position:absolute;font-size:72px;color:var(--accent)}
        .tc-eye{position:absolute;left:400px;right:400px;text-align:center;color:var(--accent)}
        .tc-sub{position:absolute;left:400px;right:400px;text-align:center}`,
  build(c, s, st) {
    const wide = !!(c.L && c.L.wide);
    const wrap = c.el("div", "tc", null, st);
    wrap.setAttribute("data-layout-allow-overlap", "");
    const han = c.el("div", "tc-han", c.esc(s.han || "囍"), wrap);
    han.setAttribute("data-layout-ignore", "");
    han.style.left = "0";
    han.style.right = "0";
    han.style.top = wide ? "180px" : "560px";
    han.style.fontSize = wide ? "420px" : "560px";
    const frieze = c.el("div", "tc-han", c.esc("囍     囍     囍"), wrap);
    frieze.setAttribute("data-layout-ignore", "");
    frieze.style.left = wide ? "400px" : "120px";
    frieze.style.right = wide ? "400px" : "160px";
    frieze.style.top = wide ? "100px" : "268px";
    frieze.style.fontSize = wide ? "64px" : "72px";
    const card = c.el("div", "tc-card", null, wrap);
    if (!wide) {
      card.style.left = "64px";
      card.style.top = "300px";
      card.style.width = "952px";
      card.style.height = "1120px";
    }
    const eye = c.el("div", "tc-eye", c.esc(s.eyebrow || ""), wrap);
    eye.style.top = wide ? "120px" : "340px";
    const sub = c.el("div", "tc-sub", c.esc(s.sub || ""), wrap);
    sub.style.top = wide ? "160px" : "388px";
    const svg = c.sv("svg", {
      class: "tc-svg", width: wide ? 1920 : 1080, height: wide ? 1080 : 1920,
      viewBox: wide ? "0 0 1920 1080" : "0 0 1080 1920",
    }, wrap);
    const rule = c.sv("path", {
      d: wide ? "M520 210 H1400" : "M220 452 H860",
      fill: "none", stroke: "var(--accent)", "stroke-width": 3, "stroke-linecap": "round",
    }, svg);
    const rows = s.rows || [];
    const y0 = wide ? 240 : 490;
    const rh = wide ? 150 : 250;
    rows.forEach((r, i) => {
      const y = y0 + i * rh;
      const mute = !!r.mute;
      const day = c.el("div", "tc-day disp" + (mute ? " mute" : ""), c.esc(r.day || ""), wrap);
      day.style.left = mute ? (wide ? "400px" : "120px") : (wide ? "420px" : "100px");
      day.style.width = mute ? (wide ? "1120px" : "840px") : (wide ? "280px" : "340px");
      day.style.top = (y + (mute ? 20 : 8)) + "px";
      day.style.fontSize = (mute ? (wide ? 40 : 56) : (wide ? 72 : (String(r.day || "").length > 2 ? 100 : 132))) + "px";
      const am = c.el("div", "tc-am", c.esc(r.am || ""), wrap);
      am.style.left = mute ? (wide ? "420px" : "140px") : (wide ? "720px" : "450px");
      am.style.right = wide ? "220px" : "120px";
      am.style.top = (y + (mute ? 108 : 36)) + "px";
      am.style.fontSize = (wide ? 28 : (mute ? 42 : 40)) + "px";
      if (mute) am.style.textAlign = "center";
      if (r.meta) {
        const meta = c.el("div", "tc-meta", c.esc(r.meta), wrap);
        meta.style.left = wide ? "720px" : "450px";
        meta.style.right = wide ? "220px" : "120px";
        meta.style.top = (y + (wide ? 78 : 96)) + "px";
        meta.style.fontSize = (wide ? 24 : 32) + "px";
      }
    });
    const note = c.el("div", "tc-note", c.esc(s.note || ""), wrap);
    note.style.top = wide ? "760px" : "1288px";
    return { rule };
  },
  enter(c, h, t0) {
    if (h.rule) c.draw(h.rule, Math.max(0, t0 + 0.25), 0.55);
  },
});
