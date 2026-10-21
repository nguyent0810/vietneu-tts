/* EVIDENCE / TEXTURE devices */
// Chữ khổng lồ làm cửa sổ: fill = "rain" (mưa vẽ bằng code), "image" (ảnh, có xử lý màu), "stripes".
HFS.device("window", {
  meta: { purpose: "statement", framing: "center-hero", axis: "in-glyph", circle: 0, energy: "M" },
  css: `.wn-lab{position:absolute;left:108px;top:330px;font-size:32px;color:var(--accent)}
        .wn-sub{position:absolute;left:100px;right:110px;top:1240px;font-size:64px}`,
  cssW: `.wn-lab{position:absolute;left:150px;top:150px;font-size:28px;color:var(--accent)}
        .wn-sub{position:absolute;left:150px;right:150px;top:700px;font-size:56px;text-align:center}`,
  build(c, s, st, i) {
    c.el("div", "wn-lab mono", c.esc(s.lab || ""), st);
    const W = c.L.W, H = c.L.H, id = "wclip" + i, fs = s.size || (c.L.wide ? 400 : 420), y = s.y || (c.L.wide ? 600 : 1080);
    const svg = c.sv("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, style: "position:absolute;left:0;top:0" }, st);
    const defs = c.sv("defs", {}, svg), cp = c.sv("clipPath", { id }, defs);
    const txt = (parent, extra) => { const t = c.sv("text", Object.assign({ x: W / 2, y, "text-anchor": "middle", "font-family": "var(--font-body)", "font-weight": 900,
      "font-size": fs, "letter-spacing": -8, style: "font-family:var(--font-body)" }, extra), parent); t.textContent = s.word; return t; };
    txt(cp, {});
    const g = c.sv("g", { "clip-path": `url(#${id})` }, svg);
    // Vùng tô phải phủ cả dấu chồng chữ hoa tiếng Việt (Ề, Ổ, À… nhô tới ~1.3em trên chân chữ); .95em làm dấu chỉ còn viền rỗng (tv04 "VÀNG", 21/10/2026).
    const top = y - fs * 1.35, hgt = fs * 1.65, drops = [], r = c.rng("win" + i);
    if (s.fill === "image" && s.img) {
      c.sv("image", { href: s.img, x: 0, y: top - 80, width: W, height: hgt + 160, preserveAspectRatio: "xMidYMid slice", style: s.imgStyle || "filter:contrast(1.25) saturate(.8)" }, g);
    } else {
      c.sv("rect", { x: 0, y: top, width: W, height: hgt, style: "fill:var(--ink)" }, g);
      if (s.fill !== "solid") for (let k = 0; k < 70; k++) drops.push({ r: c.sv("rect", { width: 4, height: 60 + r() * 70, rx: 2, style: "fill:var(--ground)", opacity: .35 + r() * .5 }, g), x: r() * W, v: 1100 + r() * 800, p: r() });
    }
    txt(svg, { fill: "none", style: "font-family:var(--font-body);stroke:var(--ink)", "stroke-width": 3 });
    const sub = c.el("div", "wn-sub heavy", null, st);
    return { g, drops, top, hgt, W, y, sw: c.words(sub, s.sub || "") };
  },
  enter(c, h, t0, s) {
    c.tl.fromTo(h.g, { scale: 1.06, transformOrigin: `${h.W / 2}px ${h.y - 80}px` }, { scale: 1, duration: c.S(.6), ease: "expo.out", immediateRender: false }, t0);
    if (h.sw.length) { const ts = c.t(s.subAt, t0 + 1); c.waterfall(h.sw, c.spread(ts, ts + .35, h.sw.length)); }
    if (h.drops.length) { const pr = { t: 0 }, span = c.dur - t0;
      c.tl.fromTo(pr, { t: 0 }, { t: span, duration: span, ease: "none", immediateRender: false, onUpdate: () => {
        h.drops.forEach((d) => { const yy = h.top + ((d.p * h.hgt + pr.t * d.v) % h.hgt) - 60; d.r.setAttribute("x", d.x - (yy - h.top) * .12); d.r.setAttribute("y", yy); }); } }, t0); }
  },
});
