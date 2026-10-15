/* QUOTE / CLOSE devices */
// Trích dẫn (kinh, sách): mode "karaoke" -- cả câu hiện mờ, từ đang đọc sáng lên (một driver tuyến tính);
// mode "rise" -- từng từ trồi khỏi đường che. Nguồn (vd "Tương Ưng Bộ 56.11") trượt vào cuối.
HFS.device("quote", {
  meta: { purpose: "quote", framing: "center-hero", axis: "in-glyph", circle: 0, energy: "C" },
  css: `.qt-mark{position:absolute;left:84px;top:300px;font-family:var(--font-quote, var(--font-display));font-size:260px;line-height:1;color:var(--accent);opacity:.9}
        .qt{position:absolute;left:100px;right:110px;top:520px;font-family:var(--font-quote, var(--font-display));font-style:var(--quote-style, italic);
            font-weight:var(--quote-weight, 500);font-size:86px;line-height:1.26;color:var(--ink)}
        .qt-src{position:absolute;left:100px;top:1300px;font-size:30px;color:var(--accent)}
        .qt-rule{position:absolute;left:100px;top:1270px;width:220px;height:3px;background:var(--accent);transform-origin:0 50%}`,
  cssW: `.qt-mark{position:absolute;left:150px;top:110px;font-family:var(--font-quote, var(--font-display));font-size:220px;line-height:1;color:var(--accent);opacity:.9}
        .qt{position:absolute;left:290px;right:220px;top:200px;font-family:var(--font-quote, var(--font-display));font-style:var(--quote-style, italic);
            font-weight:var(--quote-weight, 500);font-size:68px;line-height:1.3;color:var(--ink)}
        .qt-src{position:absolute;left:290px;top:760px;font-size:28px;color:var(--accent)}
        .qt-rule{position:absolute;left:290px;top:735px;width:220px;height:3px;background:var(--accent);transform-origin:0 50%}`,
  build(c, s, st) {
    c.el("div", "qt-mark", "“", st);
    const q = c.el("div", "qt", null, st), ws = c.words(q, s.text, { mask: s.mode === "rise" });
    const rule = c.el("div", "qt-rule", null, st), src = c.el("div", "qt-src mono", c.esc(s.source || ""), st);
    return { ws, rule, src };
  },
  enter(c, h, t0, s) {
    const times = s.wordTimes || c.spread(t0 + .2, t0 + 2, h.ws.length);
    if (s.mode === "rise") h.ws.forEach((w, i) => { c.tl.set(w.inn, { yPercent: 115 }, 0); c.tl.to(w.inn, { yPercent: 0, duration: c.S(.5), ease: "power3.out" }, Math.max(0, times[i] - .05)); });
    else {   // karaoke: một driver tuyến tính, attack .15 / release .35 / nền .3
      h.ws.forEach((w) => c.tl.set(w.inn, { opacity: .3 }, 0));
      const d = { t: t0 }, end = (s.until != null ? s.untilT : null) || (times[times.length - 1] + 1.2);
      c.tl.fromTo(d, { t: t0 }, { t: end, duration: Math.max(.1, end - t0), ease: "none", immediateRender: false, onUpdate: () => {
        h.ws.forEach((w, i) => { const s0 = times[i], dt = d.t - s0; const k = dt < 0 ? 0 : dt < .15 ? dt / .15 : dt < .5 ? 1 - (dt - .15) / .35 * .25 : .75;
          w.inn.style.opacity = (.3 + .7 * k).toFixed(3); }); } }, t0); }
    const ts = c.t(s.sourceAt, t0 + 2);
    c.tl.set(h.rule, { scaleX: 0 }, 0); c.tl.to(h.rule, { scaleX: 1, duration: c.S(.5), ease: c.E.draw }, ts);
    c.reveal(h.src, ts + .15, { x: -40, y: 0, d: .4 });
  },
});

// Câu hỏi kết: từng từ trồi khỏi đường che (mask có đệm dấu), gạch chân cụm cuối; khung tĩnh >= 1.5s.
HFS.device("close", {
  meta: { purpose: "close", framing: "edge-band", axis: "mask", circle: 0, energy: "C" },
  css: `.cs-q{position:absolute;left:100px;right:110px;top:560px;font-size:118px;line-height:1.2}`,
  cssW: `.cs-q{position:absolute;left:220px;right:220px;top:280px;font-size:100px;line-height:1.2;text-align:center}`,
  build(c, s, st) { const q = c.el("div", "cs-q heavy", null, st); return { ws: c.words(q, s.q, { mask: true }) }; },
  enter(c, h, t0, s) {
    h.ws.forEach((w, i) => { c.tl.set(w.inn, { yPercent: 115 }, 0); c.tl.to(w.inn, { yPercent: 0, duration: c.S(.5), ease: "power3.out" }, t0 + .1 + i * .07); });
    const k = s.markWord != null ? s.markWord : h.ws.length - 1;
    h.ws.slice(Math.max(0, k - (s.markSpan || 1) + 1), k + 1).forEach((w) => c.underline(w.wd, t0 + .9, { cls: "u-line u-accent" }));
  },
});
