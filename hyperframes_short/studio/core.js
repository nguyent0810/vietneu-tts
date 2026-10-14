/* HFS -- HyperFrames Shorts Studio core (engine 1.0, 14/10/2026).
 * Một video = một composition, MỘT timeline paused ("main"). Mỗi cảnh là <section class="clip scene" data-start data-duration>
 * do builder Python viết sẵn -> runtime HyperFrames tự quản ẩn/hiện (không tween visibility trên .clip).
 * Thiết bị (device) = module: build(ctx, spec, stage) -> handle; enter(ctx, handle, t0). Mọi mốc thời gian đã được builder
 * phân giải ra GIÂY (anchor -> số). Màu/chữ chỉ qua biến CSS của theme; JS đọc token một lần (ctx.T).
 * Luật: fromTo có from tường minh; không Math.random/Date; không repeat:-1; blur chữ <= 10px rồi về "none";
 * một bảng ease trung tâm (ctx.E) -> ngân sách nảy (overshoot) kiểm soát được.
 */
window.HFS = (function () {
  "use strict";
  const DEV = {};
  const NS = "http://www.w3.org/2000/svg";
  const device = (name, def) => { DEV[name] = def;
    if (def.css) { const st = document.createElement("style"); st.textContent = def.css; document.head.appendChild(st); } };

  // ---------- tiện ích ----------
  const el = (tag, cls, html, parent) => { const e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; if (parent) parent.appendChild(e); return e; };
  const sv = (tag, a, parent) => { const e = document.createElementNS(NS, tag); for (const k in a) e.setAttribute(k, a[k]); if (parent) parent.appendChild(e); return e; };
  function hash(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  function rng(key) { let a = hash(String(key)) || 1; return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  const nfc = (s) => String(s).normalize("NFC");
  const esc = (s) => nfc(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  // "**từ**" = nhấn (màu accent). Trả [{w, hot}]
  function tokens(text) { const out = []; let hot = false;
    nfc(text).split(/\s+/).filter(Boolean).forEach((tok) => { let t = tok; if (t.startsWith("**")) { hot = true; t = t.slice(2); }
      const end = t.endsWith("**") || /\*\*[.,:;!?]$/.test(t); t = t.replace(/\*\*/g, ""); out.push({ w: t, hot }); if (end) hot = false; });
    return out; }

  function run(DATA) {
    const root = document.getElementById("root");
    const tl = gsap.timeline({ paused: true });
    const cs = getComputedStyle(root);
    const tok = (n, d) => (cs.getPropertyValue("--" + n).trim() || d);
    const T = { ground: tok("ground", "#F3EEE5"), ground2: tok("ground2", "#EAE2D4"), ink: tok("ink", "#1C1410"), soft: tok("ink-soft", "#5A4A40"),
                accent: tok("accent", "#C32F27"), accent2: tok("accent2", "#780116"), glow: tok("glow", "#E2A93B"), mute: tok("mute", "#8A7F72"),
                on2: tok("on-accent2", "#F3EEE5"), line: tok("line", "rgba(28,20,16,.18)") };
    const M = Object.assign({ entry: "expo.out", exit: "power3.in", move: "power2.inOut", calm: "sine.inOut", draw: "power2.out",
                              accent: "back.out(1.5)", speed: 1, overshoot: 1, blur: 10 }, DATA.motion || {});
    const S = (d) => d * M.speed;                    // theme chậm (BUD) -> speed > 1
    let overshootLeft = M.overshoot;
    const E = { entry: M.entry, exit: M.exit, move: M.move, calm: M.calm, draw: M.draw,
                pop: () => (overshootLeft-- > 0 ? M.accent : M.entry) };   // nảy chỉ khi còn ngân sách
    const diag = (window.__hfsDiag = { engine: DATA.engine, errors: [] });
    const fail = (code, d) => { diag.errors.push([code, d]); console.error("HFS", code, d); };

    // ---------- ctx cho device ----------
    const ctx = { tl, T, E, S, M, el, sv, tokens, esc, rng, dur: DATA.dur, lines: DATA.lines, fail,
      t: (x, def) => (typeof x === "number" ? x : (def != null ? def : (fail("anchor", x), 0))),
      // chữ theo từ; mask = khung che có đệm dấu tiếng Việt
      words(box, text, { mask = false } = {}) {
        return tokens(text).map((x, i) => { if (i) box.appendChild(document.createTextNode(" "));
          const wd = el("span", "wd" + (mask ? " mask" : ""), null, box), inn = el("span", "in" + (x.hot ? " hot" : ""), null, wd);
          inn.textContent = x.w; return { wd, inn, w: x.w }; }); },
      // hiện nhị phân theo mốc, từ cuối đi xa hơn (waterfall)
      waterfall(items, times, { y = 46, axis = "y" } = {}) {
        items.forEach((it, i) => { const last = i === items.length - 1, d = S(last ? .2 : .15), off = last ? y * 1.5 : y, t = Math.max(0, times[i]);
          tl.set(it.inn, { opacity: 0 }, 0); tl.set(it.inn, { opacity: 1 }, t);
          tl.fromTo(it.inn, { [axis]: off }, { [axis]: 0, duration: d, ease: "power4.out", immediateRender: false }, t); }); },
      spread: (t0, t1, n) => Array.from({ length: n }, (_, i) => t0 + (t1 - t0) * (n > 1 ? i / (n - 1) : 0)),
      // hiện một khối tại mốc (nhị phân + trượt ngắn)
      reveal(node, t, { y = 30, x = 0, d = .3, ease } = {}) { t = Math.max(0, t);
        tl.set(node, { autoAlpha: 0 }, 0); tl.set(node, { autoAlpha: 1 }, t);
        tl.fromTo(node, { x, y }, { x: 0, y: 0, duration: S(d), ease: ease || E.entry, immediateRender: false }, t); },
      // vạch/gạch chân: phần tử tuyệt đối trong cha, scaleX 0->1 (không đo layout)
      underline(node, t, { cls = "u-line", d = .5 } = {}) { const u = el("span", cls, null, node); tl.set(u, { scaleX: 0 }, 0);
        tl.to(u, { scaleX: 1, duration: S(d), ease: E.draw }, Math.max(0, t)); return u; },
      draw(path, t, d = .5, ease) { const len = path.getTotalLength ? (path.getTotalLength() || 800) : 800;
        path.setAttribute("stroke-dasharray", len); tl.set(path, { attr: { "stroke-dashoffset": len }, autoAlpha: 1 }, 0);
        tl.to(path, { attr: { "stroke-dashoffset": 0 }, duration: S(d), ease: ease || E.draw }, Math.max(0, t)); },
      stamp(node, t, rot = -6) { t = Math.max(0, t); tl.set(node, { autoAlpha: 0 }, 0); tl.set(node, { autoAlpha: 1 }, t);
        tl.fromTo(node, { scale: 1.7, rotation: rot - 6 }, { scale: 1, rotation: rot, duration: .28, ease: "power4.out", immediateRender: false }, t); },
      burst(parent, cx, cy, t, key, n = 12) { const r = rng(key);
        for (let k = 0; k < n; k++) { const d = el("i", "dot", null, parent); d.style.left = cx + "px"; d.style.top = cy + "px";
          const a = (k / n) * Math.PI * 2 + r() * .4, R = 90 + r() * 90; tl.set(d, { autoAlpha: 0 }, 0);
          tl.fromTo(d, { x: 0, y: 0, autoAlpha: 1, scale: 1 }, { x: Math.cos(a) * R, y: Math.sin(a) * R, autoAlpha: 0, scale: .4, duration: .55, ease: "power3.out", immediateRender: false }, Math.max(0, t)); } },
      count(node, from, to, t, d = 1.2, fmt) { const st = { v: from }; const f = fmt || ((v) => String(Math.round(v)));
        node.textContent = f(from); tl.fromTo(st, { v: from }, { v: to, duration: S(d), ease: "power3.out", immediateRender: false, onUpdate: () => (node.textContent = f(st.v)) }, Math.max(0, t)); },
    };

    // ---------- chuyển cảnh (seam) trên .stage; clip tự ẩn/hiện ----------
    const SEAM = {
      curve(a, b, t) { tl.fromTo(a, { y: 0, opacity: 1 }, { y: -230, opacity: 0, duration: .3, ease: "power4.in", immediateRender: false }, t - .3);
                       tl.fromTo(b, { y: 230, opacity: .35 }, { y: 0, opacity: 1, duration: .34, ease: "power4.out", immediateRender: false }, t); },
      side(a, b, t) { tl.fromTo(a, { x: 0, opacity: 1 }, { x: -230, opacity: 0, duration: .3, ease: "power4.in", immediateRender: false }, t - .3);
                      tl.fromTo(b, { x: 230, opacity: .35 }, { x: 0, opacity: 1, duration: .34, ease: "power4.out", immediateRender: false }, t); },
      zoom(a, b, t, inv) { const bl = `blur(${M.blur}px)`;
        tl.fromTo(a, { scale: 1, filter: "blur(0px)", opacity: 1 }, { scale: inv ? .8 : 1.2, filter: bl, opacity: .15, duration: .2, ease: "power3.in", immediateRender: false }, t - .2);
        tl.fromTo(b, { scale: inv ? 1.25 : .75, filter: bl, opacity: .15 }, { scale: 1, filter: "blur(0px)", opacity: 1, duration: .5, ease: "expo.out", immediateRender: false }, t);
        tl.set(b, { filter: "none" }, t + .5); },
      inv(a, b, t) { SEAM.zoom(a, b, t, true); },
      blur(a, b, t) { tl.fromTo(a, { opacity: 1, filter: "blur(0px)", scale: 1 }, { opacity: 0, filter: "blur(12px)", scale: 1.03, duration: S(.4), ease: "power1.in", immediateRender: false }, t - S(.4));
                      tl.fromTo(b, { opacity: 0, filter: "blur(12px)", scale: .97 }, { opacity: 1, filter: "blur(0px)", scale: 1, duration: S(.55), ease: "power2.out", immediateRender: false }, t);
                      tl.set(b, { filter: "none" }, t + S(.55)); },
      hard() {},
    };

    // ---------- dựng cảnh ----------
    const scenes = DATA.scenes.map((s, i) => {
      const sec = document.getElementById("s" + i), stage = sec.querySelector(".stage");
      const def = DEV[s.device]; if (!def) { fail("device", s.device); return null; }
      const h = def.build(ctx, s, stage, i) || {};
      return { s, sec, stage, def, h, t0: +sec.dataset.start };
    });
    scenes.forEach((sc, i) => { if (!sc) return;
      if (i) { const k = sc.s.seam || DATA.seam || "curve"; (SEAM[k] || SEAM.curve)(scenes[i - 1].stage, sc.stage, sc.t0); }
      sc.def.enter && sc.def.enter(ctx, sc.h, sc.t0, sc.s); });

    // ---------- chữ nền mờ + thanh tiến độ ----------
    const ghost = document.getElementById("ghost");
    if (ghost) scenes.forEach((sc) => sc && tl.set(ghost, { textContent: sc.s.ghost || "" }, sc.t0));
    const bar = document.getElementById("topbar"); if (bar) tl.fromTo(bar, { scaleX: 0 }, { scaleX: 1, duration: DATA.dur, ease: "none" }, 0);
    const kick = document.getElementById("kick"); if (kick) kick.textContent = DATA.kicker || "";

    // ---------- phụ đề: nhóm dựng sẵn, bật/tắt bằng set (thấy được bởi check) ----------
    const cap = document.getElementById("cap");
    if (cap && DATA.captions !== false) DATA.lines.forEach((ln, li) => {
      const ws = ln.words, n = DATA.capGroup || 5;
      for (let k = 0; k < ws.length; k += n) {
        const g = ws.slice(k, k + n), t0 = g[0].t, t1 = k + n >= ws.length ? ln.end + .1 : ws[k + n].t;
        const grp = el("div", "cg", null, cap);
        g.forEach((x, j) => { if (j) grp.appendChild(document.createTextNode(" ")); const w = el("span", "cw", null, grp); w.textContent = x.w.replace(/\*\*/g, "");
          tl.set(w, { attr: { class: "cw on now" } }, x.t); tl.set(w, { attr: { class: "cw on" } }, x.t + Math.max(.12, x.d || .25)); });
        tl.set(grp, { autoAlpha: 0 }, 0); tl.set(grp, { autoAlpha: 1 }, Math.max(0, t0 - .05)); tl.set(grp, { autoAlpha: 0 }, t1);
      }
    });

    window.__timelines["main"] = tl;
    tl.seek(0);
    return tl;
  }
  return { device, run, hash, rng };
})();
