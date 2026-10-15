/* TIME devices */
// Lịch bloc xé: trang lật (rotationX) theo mốc, trang cuối giữ lại + dấu son. Ẩn trang bằng autoAlpha (an toàn khi tua ngược).
HFS.device("calendar", {
  meta: { purpose: "time", framing: "card-on-field", axis: "3D", circle: 0, energy: "M" },
  css: `.cl-stage{position:absolute;left:0;top:250px;width:1080px;height:1220px;perspective:1500px}
        .cl-page{position:absolute;left:150px;top:90px;width:780px;height:1010px;background:var(--card, #FBF8F2);box-shadow:0 30px 60px rgba(0,0,0,.18);
                 transform-origin:50% 0;backface-visibility:hidden;border:2px solid var(--line)}
        .cl-head{position:absolute;left:0;right:0;top:0;height:150px;background:var(--accent);color:var(--on-accent,#fff);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:56px}
        .cl-day{position:absolute;left:0;right:0;top:170px;text-align:center;font-size:460px;line-height:1;color:var(--accent);transform:rotate(-4deg)}
        .cl-wd{position:absolute;left:0;right:0;top:680px;text-align:center;font-size:56px;font-weight:900}
        .cl-lun{position:absolute;left:40px;right:40px;top:780px;text-align:center;font-size:32px;color:var(--soft-text,#6B6156);border-top:2px solid var(--line);padding-top:24px}
        .cl-ring{position:absolute;top:-26px;width:30px;height:60px;border-radius:16px;background:var(--ink)}`,
  cssW: `.cl-stage{position:absolute;left:0;top:0;width:1920px;height:1080px;perspective:1500px}
        .cl-page{position:absolute;left:250px;top:140px;width:600px;height:690px;background:var(--card, #FBF8F2);box-shadow:0 30px 60px rgba(0,0,0,.18);
                 transform-origin:50% 0;backface-visibility:hidden;border:2px solid var(--line)}
        .cl-head{position:absolute;left:0;right:0;top:0;height:110px;background:var(--accent);color:var(--on-accent,#fff);display:flex;align-items:center;justify-content:center;font-weight:900;font-size:44px}
        .cl-day{position:absolute;left:0;right:0;top:120px;text-align:center;font-size:300px;line-height:1;color:var(--accent);transform:rotate(-4deg)}
        .cl-wd{position:absolute;left:0;right:0;top:450px;text-align:center;font-size:44px;font-weight:900}
        .cl-lun{position:absolute;left:30px;right:30px;top:530px;text-align:center;font-size:26px;color:var(--soft-text,#6B6156);border-top:2px solid var(--line);padding-top:20px}
        .cl-ring{position:absolute;top:-24px;width:26px;height:52px;border-radius:14px;background:var(--ink)}
        .cl-side{position:absolute;left:980px;right:150px;top:190px;font-size:76px;line-height:1.16}`,
  build(c, s, st) {
    const stage = c.el("div", "cl-stage", null, st), pages = []; stage.setAttribute("data-layout-allow-overlap", "");
    s.pages.slice().reverse().forEach((p) => { const pg = c.el("div", "cl-page", null, stage);
      c.el("div", "cl-head", c.esc(p.head), pg); c.el("div", "cl-day disp", c.esc(p.day), pg); c.el("div", "cl-wd", c.esc(p.wd || ""), pg); c.el("div", "cl-lun mono", c.esc(p.lun || ""), pg);
      (c.L.wide ? [140, 434] : [180, 570]).forEach((x) => { c.el("div", "cl-ring", null, pg).style.left = x + "px"; }); pages.unshift(pg); });
    const sx = s.stampX || (c.L.wide ? 990 : 300), sy = s.stampY || (c.L.wide ? 600 : 1180);
    const seal = c.el("div", "seal", c.esc(s.stamp || ""), st); seal.style.left = sx + "px"; seal.style.top = sy + "px";
    const side = c.L.wide && s.side ? c.el("div", "cl-side heavy", null, st) : null;     // khổ ngang: lời giải bên phải lịch
    return { stage, pages, seal, sx, sy, sw: side ? c.words(side, s.side) : null };
  },
  enter(c, h, t0, s) {
    c.tl.fromTo(h.stage, { y: 120 }, { y: 0, duration: c.S(.5), ease: c.E.entry, immediateRender: false }, t0);
    (s.flips || []).forEach((f, k) => { const tf = c.t(f, t0 + 1 + k);
      c.tl.fromTo(h.pages[k], { rotationX: 0, y: 0 }, { rotationX: 112, y: -40, duration: .5, ease: "power2.in", immediateRender: false }, tf - .15);
      c.tl.set(h.pages[k], { autoAlpha: 0 }, tf + .36); });
    if (s.stamp) { const ts = c.t(s.stampAt, t0 + 2); c.stamp(h.seal, ts, -7); c.burst(h.stage.parentNode, c.L.wide ? h.sx + 150 : 540, h.sy + 50, ts + .05, "cal" + t0); }
    if (h.sw) { const tw = c.t(s.sideAt, t0 + .6); c.waterfall(h.sw, c.spread(tw, tw + .4, h.sw.length)); }
  },
});

// Trục thời gian dọc: đường xương sống vẽ xuống, mốc năm bật theo lời, nhãn trượt luân phiên hai bên.
HFS.device("time_spine", {
  meta: { purpose: "time", framing: "world-camera", axis: "draw", circle: 0, energy: "M" },
  css: `.ts-kick{position:absolute;left:108px;top:300px;font-size:30px;color:var(--accent)}
        .ts-item{position:absolute;width:400px}.ts-item.l{left:100px;text-align:right}.ts-item.r{left:580px}
        .ts-yr{font-size:84px;line-height:1;color:var(--accent)}.ts-lab{font-size:40px;font-weight:800;line-height:1.2;margin-top:6px}
        .ts-dot{position:absolute;left:525px;width:30px;height:30px;border-radius:50%;background:var(--accent);border:6px solid var(--ground)}`,
  cssW: `.ts-kick{position:absolute;left:150px;top:150px;font-size:28px;color:var(--accent)}
        .ts-item{position:absolute;width:400px;text-align:center}
        .ts-yr{font-size:104px;line-height:1;color:var(--accent);white-space:nowrap}.ts-lab{font-size:42px;font-weight:800;line-height:1.2;margin-top:6px}
        .ts-dot{position:absolute;width:30px;height:30px;border-radius:50%;background:var(--accent);border:6px solid var(--ground)}`,
  build(c, s, st) {
    if (s.kick) c.el("div", "ts-kick mono", c.esc(s.kick), st);
    const n = s.items.length;
    if (c.L.wide) {      // khổ ngang: xương sống nằm ngang y=470, nhãn luân phiên trên/dưới
      const gx = Math.min(460, 1400 / Math.max(1, n - 1)), x0 = 960 - gx * (n - 1) / 2, Y = 470;
      const svg = c.sv("svg", { width: 1920, height: 1080, style: "position:absolute;left:0;top:0" }, st);
      const spine = c.sv("path", { d: `M${x0 - 60},${Y} L${x0 + gx * (n - 1) + 80},${Y}`, style: "stroke:var(--ink);fill:none", "stroke-width": 6 }, svg);
      const items = s.items.map((it, i) => { const x = x0 + gx * i, side = i % 2 ? "r" : "l";
        const d = c.el("div", "ts-dot", null, st); d.style.left = (x - 15) + "px"; d.style.top = (Y - 15) + "px";
        const b = c.el("div", "ts-item", `<div class="ts-yr disp">${c.esc(it.yr)}</div><div class="ts-lab">${c.esc(it.label)}</div>`, st);
        b.style.left = (x - 200) + "px";
        if (side === "l") b.style.bottom = (1080 - Y + 40) + "px"; else b.style.top = (Y + 44) + "px";   // trên trục: neo đáy
        if (String(it.yr).length > 5) b.querySelector(".ts-yr").style.fontSize = "68px";
        return { d, b, side }; });
      return { spine, items, wide: true };
    }
    const y0 = 420, gap = Math.min(250, 980 / Math.max(1, n - 1));
    const svg = c.sv("svg", { width: 1080, height: 1920, style: "position:absolute;left:0;top:0" }, st);
    const spine = c.sv("path", { d: `M540,${y0 - 30} L540,${y0 + gap * (n - 1) + 60}`, style: "stroke:var(--ink);fill:none", "stroke-width": 6 }, svg);
    const items = s.items.map((it, i) => { const y = y0 + gap * i, side = i % 2 ? "r" : "l";
      const d = c.el("div", "ts-dot", null, st); d.style.top = (y - 15) + "px";
      const b = c.el("div", "ts-item " + side, `<div class="ts-yr disp">${c.esc(it.yr)}</div><div class="ts-lab">${c.esc(it.label)}</div>`, st); b.style.top = (y - 46) + "px";
      return { d, b, side }; });
    return { spine, items };
  },
  enter(c, h, t0, s) {
    const last = c.t(s.items[s.items.length - 1].at, t0 + 2);
    c.draw(h.spine, t0 + .1, Math.max(.6, last - t0), "none");
    h.items.forEach((it, i) => { const t = c.t(s.items[i].at, t0 + .3 + i * .6);
      c.tl.set(it.d, { autoAlpha: 0 }, 0); c.tl.set(it.d, { autoAlpha: 1 }, t);
      c.tl.fromTo(it.d, { scale: .3 }, { scale: 1, duration: .3, ease: c.E.entry, immediateRender: false }, t);
      c.reveal(it.b, t + .05, h.wide ? { x: 0, y: it.side === "l" ? -40 : 40, d: .4 } : { x: it.side === "l" ? -60 : 60, y: 0, d: .4 }); });
  },
});
