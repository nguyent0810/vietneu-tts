/* HOOK devices -- khung 0 phải đủ nghĩa (câu trả lời đã hiện), phát triển theo mốc giọng sau đó. */
HFS.device("hook_poster", {
  meta: { purpose: "hook", framing: "edge-band", axis: "static", circle: 0, energy: "H" },
  css: `.hp-num{position:absolute;left:96px;top:300px;font-size:380px;line-height:1;color:var(--accent);transform:rotate(-6deg);transform-origin:0 100%;
          text-shadow:6px 6px 0 var(--accent2),12px 12px 0 var(--shadow, rgba(0,0,0,.15));white-space:nowrap}
        .hp-kick{position:absolute;left:108px;top:760px;font-size:32px;color:var(--ink)}
        .hp-big{position:absolute;left:100px;right:110px;top:810px;font-size:150px;color:var(--accent)}`,
  cssW: `.hp-num{position:absolute;left:130px;top:150px;font-size:360px;line-height:1;color:var(--accent);transform:rotate(-6deg);transform-origin:0 100%;
          text-shadow:6px 6px 0 var(--accent2),12px 12px 0 var(--shadow, rgba(0,0,0,.15));white-space:nowrap}
        .hp-kick{position:absolute;left:150px;top:572px;font-size:30px;color:var(--ink)}
        .hp-big{position:absolute;left:142px;right:150px;top:618px;font-size:150px;color:var(--accent)}`,
  build(c, s, st) {
    st.setAttribute("data-layout-allow-overlap", "");          // số nghiêng đè lên dòng dưới là chủ ý (poster)
    c.el("div", "hp-num disp", c.esc(s.num || ""), st);
    c.el("div", "hp-kick mono", c.esc(s.kick || ""), st);
    const big = c.el("div", "hp-big heavy", null, st);
    if (c.L.wide) { const n = String(s.big || "").replace(/\*\*/g, "").length;   // khổ ngang: giữ 1 dòng trên dải phụ đề
      big.style.fontSize = (n > 30 ? 84 : n > 22 ? 104 : n > 16 ? 124 : 150) + "px"; }
    const fx = s.fx || [], ws = c.words(big, s.big);
    // fx "ink": vết mực loang SAU số + chữ lớn (chữ vẫn đọc được ở khung 0 -- luật hook)
    const ink = fx.includes("ink") ? (c.L.wide ? { x: 80, y: 90, w: 1500, h: 760 } : { x: 40, y: 240, w: 1000, h: 900 }) : null;
    return { ws, num: st.querySelector(".hp-num"), ink, fx };
  },
  enter(c, h, t0, s) { const k = s.markWord != null ? s.markWord : h.ws.length - 1, tm = c.t(s.markAt, t0 + 1.2);
    if (h.ink) c.ink(h.num.parentNode, t0, Object.assign({ key: "hp" + (s.big || "") }, h.ink));
    c.underline(h.ws[k].wd, tm);
    // fx "shimmer": vệt sáng quét chữ khoá (**…**) + số, ngay sau gạch chân
    if (h.fx.includes("shimmer")) c.shimmer(h.ws.filter((w) => w.inn.classList.contains("hot")).map((w) => w.inn).concat([h.num]), tm + c.S(.35)); },
});

/* nhiều nhóm chữ đập vào theo mốc, mỗi nhóm một trục khác nhau (Z-slam -> X-snap -> Y-rise); nhóm 1 hiện sẵn ở khung 0 */
HFS.device("hook_slam", {
  meta: { purpose: "hook", framing: "edge-band", axis: "Z", circle: 0, energy: "H" },
  css: `.hs-wrap{position:absolute;left:100px;right:110px;top:330px;display:flex;flex-direction:column;gap:26px}
        .hs-g{position:relative;font-size:128px;line-height:1.14;color:var(--ink)} .hs-g.big{font-size:176px;color:var(--accent)}
        .hs-kick{position:absolute;left:108px;top:270px;font-size:30px;color:var(--accent)}`,
  cssW: `.hs-wrap{position:absolute;left:150px;right:150px;top:200px;display:flex;flex-direction:column;gap:18px}
        .hs-g{position:relative;font-size:96px;line-height:1.14;color:var(--ink)} .hs-g.big{font-size:150px;color:var(--accent)}
        .hs-kick{position:absolute;left:152px;top:150px;font-size:28px;color:var(--accent)}`,
  build(c, s, st) {
    if (s.kick) c.el("div", "hs-kick mono", c.esc(s.kick), st);
    const w = c.el("div", "hs-wrap", null, st);
    return { gs: s.groups.map((g) => { const d = c.el("div", "hs-g heavy" + (g.big ? " big disp" : ""), null, w); c.words(d, g.text); return d; }) };
  },
  enter(c, h, t0, s) {
    const moves = [{ scale: 1.5, filter: `blur(${c.M.blur}px)` }, { x: -320 }, { y: 90, rotation: 4 }];
    if (s.allAtStart) { h.gs.forEach((g, i) => { if (!i) return; const t = c.t(s.groups[i].at, t0 + i);
        c.tl.fromTo(g, { scale: 1.12 }, { scale: 1, duration: c.S(.45), ease: c.E.entry, immediateRender: false }, t); });
      c.underline(h.gs[h.gs.length - 1], c.t(s.markAt, t0 + 2)); return; }
    h.gs.forEach((g, i) => { if (i === 0) return;        // nhóm 1 đứng sẵn ở khung 0
      const t = c.t(s.groups[i].at, t0 + i), mv = moves[i % moves.length];
      c.tl.set(g, { autoAlpha: 0 }, 0); c.tl.set(g, { autoAlpha: 1 }, t);
      c.tl.fromTo(g, Object.assign({ x: 0, y: 0, scale: 1, rotation: 0, filter: "blur(0px)" }, mv),
        { x: 0, y: 0, scale: 1, rotation: 0, filter: "blur(0px)", duration: c.S(.5), ease: c.E.entry, immediateRender: false }, t);
      c.tl.set(g, { filter: "none" }, t + c.S(.5)); });
    const last = h.gs[h.gs.length - 1];
    c.underline(last, c.t(s.markAt, t0 + 2));
  },
});
