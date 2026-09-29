/* ===== VIDEO DÀI: bố cục ảnh, sơ đồ dữ liệu, thẻ chương =====
   Nạp SAU engine.js và TRƯỚC HF.build(). engine.js gọi vào window.HF_LONG khi
   một câu có `visual` (sơ đồ), `media.layout` (bố cục ảnh khác ô mặc định của
   style), hoặc `chapter_no` (câu tiêu đề chương của video dài).

   Nguyên tắc (skill hyperframes-animation / faceless-explainer):
   - Không một bố cục cho cả video -- mỗi cảnh một việc, luân phiên bố cục.
   - Thứ gì trên sơ đồ cũng hiện ĐÚNG LÚC giọng đọc nhắc tới (bước `at` = số
     thứ tự câu, `word` = từ trong câu đó), không đổ hết ra ở giây đầu.
   - Mọi chuyển động nằm trên timeline GSAP đã pause -- tất định khi seek.
   - Sơ đồ vẽ từ dữ liệu plan (tên chi, quan hệ, ngũ hành) mà plan đã đối chiếu
     tay; file này không tự suy ra quan hệ nào. */
(function () {
  const NS = "http://www.w3.org/2000/svg";
  const el = (t, c, x) => HF.el(t, c, x);
  function sv(tag, attrs, parent) {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs || {}) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  const CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"];
  const REL = {  // màu + nhãn mặc định của từng quan hệ
    xung: ["--lf-xung", "LỤC XUNG"], tamhinh: ["--lf-hinh", "TAM HÌNH"], tamhop: ["--lf-hop", "TAM HỢP"],
    luchop: ["--lf-luchop", "LỤC HỢP"], hai: ["--lf-hai", "LỤC HẠI"], pha: ["--lf-hinh", "LỤC PHÁ"],
    focus: ["--accent", ""],
  };
  const ELEM = ["Hỏa", "Thổ", "Kim", "Thủy", "Mộc"];  // theo chiều kim đồng hồ = vòng tương sinh
  const ELEM_COLOR = { "Mộc": "#5fae5a", "Hỏa": "#e05a47", "Thổ": "#d0a44c", "Kim": "#e6e1d3", "Thủy": "#4c86e0" };
  const ELEM_INK = { "Mộc": "#0b1130", "Hỏa": "#0b1130", "Thổ": "#0b1130", "Kim": "#0b1130", "Thủy": "#f3f6ff" };
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim() || "#d4a93a";
  const clean = (s) => (s || "").replace(/\*\*/g, "").trim();

  // Thời điểm của một bước: đầu câu `at` (+ lệch), hoặc lúc giọng đọc tới `word`.
  function when(ctx, step, fallback) {
    const L = step && step.at ? ctx.LINES[step.at - 1] : null;
    if (!L) return fallback;
    if (step.word) {
      const key = step.word.toLowerCase();
      const w = (L.words || []).find((x) => clean(x.w).toLowerCase().includes(key));
      if (w) return w.t;
    }
    return L.start + (step.offset != null ? step.offset : 0.3);
  }
  function drawOn(tl, path, at, dur, ease) {
    const len = path.getTotalLength ? path.getTotalLength() : 1000;
    path.style.strokeDasharray = `${len}`;
    tl.fromTo(path, { strokeDashoffset: len }, { strokeDashoffset: 0, duration: dur, ease: ease || "power2.inOut" }, at);
  }
  /* ---------- Bộ chọn đa dạng (kho hiệu ứng) ----------
     Mỗi họ hiệu ứng (chuyển cảnh, thẻ chương, bố cục, lối vào sơ đồ...) có
     nhiều biến thể. pick() lấy biến thể ÍT DÙNG NHẤT trong video, không bao
     giờ trùng lần ngay trước, hoà thì bốc bằng rng hạt giống theo nội dung
     video -- cùng video render lại ra y hệt, video khác ra tổ hợp khác. */
  let R = () => 0.5, USED = {};
  function begin(LINES) {
    const sig = (LINES || []).slice(0, 3).map((l) => (l.words || []).map((w) => w.w).join(" ")).join("|");
    R = HF.rng(HF.hashSeed(sig + "|" + (LINES || []).length));
    USED = {};
  }
  function pick(family, options) {
    const u = USED[family] || (USED[family] = { c: {}, last: null });
    let pool = options.filter((o) => o !== u.last);
    if (!pool.length) pool = options.slice();
    const lo = Math.min(...pool.map((o) => u.c[o] || 0));
    const cand = pool.filter((o) => (u.c[o] || 0) === lo);
    const ch = cand[Math.floor(R() * cand.length) % cand.length];
    u.c[ch] = (u.c[ch] || 0) + 1; u.last = ch;
    return ch;
  }
  // Biến thể do plan chỉ định (spec.variant) thắng; không có thì để kho chọn.
  const variantOf = (family, spec, options) =>
    (spec && spec.variant && options.includes(spec.variant)) ? spec.variant : pick(family, options);

  function title(parent, text, left, top) {
    if (!text) return null;
    const t = el("div", "lf-title", text);
    t.style.left = left + "px"; t.style.top = top + "px";
    parent.appendChild(t);
    return t;
  }

  /* ---------------- Bố cục ảnh ---------------- */
  const layouts = {
    // Ảnh tràn khung, tối dần xuống đáy để phụ đề đọc được.
    full: {
      // Chữ khoá của câu (cụm **đánh dấu**) bật lên góc trên, đúng lúc được đọc.
      build(inner, ln) {
        inner.appendChild(el("div", "lf-full-shade"));
        const hot = (ln.key_parts || []).filter((p) => p.hot).map((p) => p.t).join(" ");
        if (hot && hot.length <= 34) {
          const c = el("div", "lf-callout");
          c.appendChild(el("div", "bar"));
          const t = el("div", "tx");
          hot.split(/\s+/).forEach((w) => t.appendChild(el("span", "", w)));
          c.appendChild(t); inner.appendChild(c);
        }
      },
      enter(tl, inner, ln) {
        const c = inner.querySelector(".lf-callout"); if (!c) return;
        const first = (ln.key_parts || []).find((p) => p.hot);
        const w = first && (ln.words || []).find((x) => x.hot);
        const t = w ? w.t : ln.start + .4;
        tl.fromTo(c.querySelector(".bar"), { scaleY: 0, transformOrigin: "50% 100%" }, { scaleY: 1, duration: .35, ease: "power3.out" }, t - .1);
        tl.fromTo(c.querySelectorAll(".tx span"), { x: 60, opacity: 0 },
          { x: 0, opacity: 1, duration: .45, ease: "power4.out", stagger: .05 }, t);
      },
      enterCont(tl, inner, ln) { this.enter(tl, inner, ln); },
    },
    // Ảnh bên trái, chữ bên phải -- gương của split.
    split_r: {
      build(inner, ln) {
        const w = el("div", "lf-split lf-split-right card-box");
        const key = el("div", "lf-split-key", (ln.key_parts || []).map((p) => p.t).join(" "));
        if (key.textContent.length > 26) key.classList.add("long");
        w.appendChild(key); w.appendChild(el("div", "lf-split-rule"));
        inner.appendChild(w);
      },
      enter(tl, inner, ln) {
        tl.fromTo(inner.querySelector(".lf-split-key"), { x: 90, opacity: 0 }, { x: 0, opacity: 1, duration: .6, ease: "power4.out" }, ln.start + .15);
        tl.fromTo(inner.querySelector(".lf-split-rule"), { width: 0 }, { width: 200, duration: .7, ease: "power2.out" }, ln.start + .35);
      },
      enterCont(tl, inner, ln) { this.enter(tl, inner, ln); },
      motion(tl, clip, ln, mEnd) {
        tl.fromTo(clip, { rotationY: 10, scale: 1, transformPerspective: 1900 },
          { rotationY: 3, scale: 1.04, duration: Math.max(1, mEnd - ln.start), ease: "sine.inOut" }, ln.start);
        return true;
      },
    },
    // Ảnh in có viền trắng, rơi xuống bàn nghiêng một chút rồi trôi chậm.
    polaroid: {
      build() {},
      motion(tl, clip, ln, mEnd) {
        const s = ln.sentence_id % 2 ? 1 : -1;
        tl.fromTo(clip, { y: -120, rotation: -9 * s, scale: 1.08 }, { y: 0, rotation: -3 * s, scale: 1, duration: .9, ease: "back.out(1.4)" }, ln.start);
        tl.to(clip, { rotation: -1.5 * s, y: -10, duration: Math.max(1, mEnd - ln.start - .9), ease: "sine.inOut" }, ln.start + .9);
        return true;
      },
    },
    // Ảnh là một tấm thẻ nghiêng trong không gian 3D, xoay chậm suốt khoảng giữ.
    card3d: {
      build() {},
      motion(tl, clip, ln, mEnd) {
        const s = ln.sentence_id % 2 ? 1 : -1;
        tl.fromTo(clip, { rotationY: -16 * s, rotationX: 7, scale: .93, transformPerspective: 1900 },
          { rotationY: -4 * s, rotationX: 2, scale: 1, duration: Math.max(1, mEnd - ln.start), ease: "sine.inOut" }, ln.start);
        return true;
      },
    },
    // Ảnh bên phải, ý chính của câu bên trái -- mỗi câu nối tiếp thay chữ.
    split: {
      build(inner, ln) {
        const w = el("div", "lf-split card-box");
        const key = el("div", "lf-split-key", (ln.key_parts || []).map((p) => p.t).join(" "));
        if (key.textContent.length > 26) key.classList.add("long");
        w.appendChild(key);
        w.appendChild(el("div", "lf-split-rule"));
        inner.appendChild(w);
      },
      enter(tl, inner, ln) {
        tl.fromTo(inner.querySelector(".lf-split-key"), { x: -90, opacity: 0 },
          { x: 0, opacity: 1, duration: .6, ease: "power4.out" }, ln.start + .15);
        tl.fromTo(inner.querySelector(".lf-split-rule"), { width: 0 }, { width: 200, duration: .7, ease: "power2.out" }, ln.start + .35);
      },
      enterCont(tl, inner, ln) { this.enter(tl, inner, ln); },
      motion(tl, clip, ln, mEnd) {
        tl.fromTo(clip, { rotationY: -10, scale: 1, transformPerspective: 1900 },
          { rotationY: -3, scale: 1.04, duration: Math.max(1, mEnd - ln.start), ease: "sine.inOut" }, ln.start);
        return true;
      },
    },
  };

  /* ---------------- Thẻ chương (5 biến thể) ---------------- */
  const CHAPTER_VARIANTS = ["zoom", "slam", "split", "roll", "depth"];
  const chapter = {
    build(inner, ln) {
      ln._chap = variantOf("chapter", ln, CHAPTER_VARIANTS);
      const w = el("div", "lf-chap lf-chap-" + ln._chap);
      const no = String(ln.chapter_no).padStart(2, "0");
      w.appendChild(el("div", "lf-chap-ghost", no));
      const lab = el("div", "lf-chap-no");
      if (ln._chap === "roll") {  // số chương lăn như đồng hồ cơ
        lab.appendChild(document.createTextNode("PHẦN "));
        const col = el("span", "lf-roll");
        const strip = el("span", "lf-roll-strip");
        for (let d = 0; d <= Number(no); d++) strip.appendChild(el("span", "", String(d).padStart(2, "0")));
        col.appendChild(strip); lab.appendChild(col);
      } else lab.textContent = "PHẦN " + no;
      w.appendChild(lab);
      const t = clean((ln.key_parts || []).map((p) => p.t).join(" ")).replace(/[.:;,]$/, "");
      const tt = el("div", "lf-chap-title");
      if (t.length > 34) tt.classList.add("long");
      if (ln._chap === "slam") t.split(/\s+/).forEach((wd) => { const sp = el("span", "lf-word", wd); tt.appendChild(sp); });
      else tt.textContent = t;
      if (ln._chap === "depth") {  // chữ nổi khối: 6 lớp lùi sau, lớp trước cùng
        const stack = el("div", "lf-depth");
        for (let k = 6; k >= 1; k--) { const b = el("div", "lf-chap-title lf-depth-back", t); if (t.length > 34) b.classList.add("long");
          b.style.transform = `translate(${k * 3}px, ${k * 4}px)`; b.style.opacity = String(0.5 - k * 0.06); stack.appendChild(b); }
        stack.appendChild(tt); w.appendChild(stack);
      } else w.appendChild(tt);
      if (ln._chap === "split") { w.appendChild(el("div", "lf-bar lf-bar-a")); w.appendChild(el("div", "lf-bar lf-bar-b")); }
      w.appendChild(el("div", "lf-chap-rule"));
      inner.appendChild(w);
      inner._lf = { t };
    },
    enter(tl, inner, ln) {
      const t0 = ln.start, span = Math.max(1.5, ln.end - ln.start), v = ln._chap;
      const q = (c) => inner.querySelector(c);
      tl.fromTo(q(".lf-chap-ghost"), { scale: .82, opacity: 0 }, { scale: 1.08, opacity: .5, duration: span + .6, ease: "power1.out" }, t0);
      tl.fromTo(q(".lf-chap-no"), { x: -60, opacity: 0 }, { x: 0, opacity: 1, duration: .6, ease: "power4.out" }, t0 + .1);
      const title = inner.querySelector(".lf-depth > .lf-chap-title:last-child") || q(".lf-chap-title");
      if (v === "zoom") {  // zoom-through: chữ lao từ sau ra, nhoè 10px (cut-catalog)
        tl.fromTo(title, { opacity: 0, scale: .75, rotationX: 26, filter: "blur(10px)", transformPerspective: 1200 },
          { opacity: 1, scale: 1, rotationX: 0, filter: "blur(0px)", duration: .95, ease: "expo.out" }, t0 + .05);
      } else if (v === "slam") {  // từng chữ đập xuống, khung rung nhẹ ở chữ cuối
        const ws = inner.querySelectorAll(".lf-word");
        tl.fromTo(ws, { opacity: 0, scale: 1.9, filter: "blur(8px)" },
          { opacity: 1, scale: 1, filter: "blur(0px)", duration: .32, ease: "power4.out", stagger: .1 }, t0 + .05);
        tl.fromTo(q(".lf-chap"), { x: 0 }, { x: 7, duration: .05, yoyo: true, repeat: 3, ease: "none" }, t0 + .05 + ws.length * .1);
      } else if (v === "split") {  // hai thanh vàng tách ra, chữ lộ giữa
        tl.fromTo(title, { clipPath: "inset(50% 0% 50% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: .75, ease: "power3.inOut" }, t0 + .15);
        tl.fromTo(q(".lf-bar-a"), { y: 0, opacity: 1 }, { y: -95, opacity: .0, duration: .9, ease: "power3.inOut" }, t0 + .15);
        tl.fromTo(q(".lf-bar-b"), { y: 0, opacity: 1 }, { y: 95, opacity: .0, duration: .9, ease: "power3.inOut" }, t0 + .15);
      } else if (v === "roll") {  // số lăn, rồi tiêu đề gõ ra từng chữ
        const n = Number(ln.chapter_no) || 1;
        tl.fromTo(q(".lf-roll-strip"), { yPercent: 0 }, { yPercent: -100 * n / (n + 1), duration: .8, ease: "power3.out" }, t0 + .1);
        const L = (inner._lf.t || "").length || 1;
        tl.fromTo(title, { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: Math.min(1.4, L * .035),
          ease: `steps(${L})` }, t0 + .5);
      } else {  // depth: khối chữ xoay vào từ bên, các lớp sau dày dần
        tl.fromTo(q(".lf-depth"), { rotationY: -38, opacity: 0, transformPerspective: 1400 },
          { rotationY: 0, opacity: 1, duration: 1.0, ease: "power3.out" }, t0 + .05);
      }
      tl.fromTo(q(".lf-chap-rule"), { width: 0 }, { width: 360, duration: .8, ease: "power2.out" }, t0 + .45);
    },
  };

  /* ---------------- Sơ đồ ---------------- */
  const visuals = {
    // Vòng 12 con giáp, Tý ở đỉnh như mặt đồng hồ; quan hệ vẽ lần lượt theo lời.
    wheel: {
      build(inner, ln) {
        const v = ln.visual, S = { steps: [] };
        const st = el("div", "lf-stage"); inner.appendChild(st);
        const wrap = el("div", "lf-wheel"); st.appendChild(wrap);
        const svg = sv("svg", { viewBox: "-500 -500 1000 1000" }, wrap);
        const deco = sv("g", {}, svg);
        sv("circle", { r: 462, fill: "none", stroke: "var(--lf-line)", "stroke-width": 3 }, deco);
        for (let k = 0; k < 72; k++) {
          const a = (k / 72) * Math.PI * 2, r1 = 462, r2 = k % 6 ? 448 : 432;
          sv("line", { x1: Math.cos(a) * r1, y1: Math.sin(a) * r1, x2: Math.cos(a) * r2, y2: Math.sin(a) * r2,
            stroke: "var(--lf-line)", "stroke-width": k % 6 ? 1.5 : 3 }, deco);
        }
        sv("circle", { r: 250, fill: "none", stroke: "var(--lf-line)", "stroke-width": 1.5, "stroke-dasharray": "6 12" }, deco);
        const relG = sv("g", {}, svg);
        const pos = {};
        CHI.forEach((c, k) => {
          const a = (-90 + k * 30) * Math.PI / 180;
          pos[c] = [Math.cos(a) * 360, Math.sin(a) * 360];
        });
        const nodes = {};
        CHI.forEach((c) => {
          const g = sv("g", { transform: `translate(${pos[c][0]},${pos[c][1]})` }, svg);
          const inG = sv("g", {}, g);
          const circ = sv("circle", { r: 66, class: "node-c" }, inG);
          const txt = sv("text", { class: "node-t" }, inG); txt.textContent = c;
          nodes[c] = { g: inG, circ, txt };
        });
        (v.steps || []).forEach((step) => {
          const color = css((REL[step.rel] || REL.focus)[0]);
          const pts = (step.chi || []).map((c) => pos[c]).filter(Boolean);
          let path = null;
          if (step.rel !== "focus" && pts.length >= 2) {
            const d = "M" + pts.map((p) => p.join(",")).join(" L") + (pts.length > 2 ? " Z" : "");
            path = sv("path", { d, class: "rel", stroke: color }, relG);
          }
          S.steps.push({ step, color, path });
        });
        S.wrap = wrap; S.deco = deco; S.nodes = nodes; S.st = st;
        S.title = title(st, v.title || "VÒNG 12 CON GIÁP", 1090, 96);
        const legend = el("div", "lf-legend"); st.appendChild(legend);
        let row = 0;
        S.steps.forEach((s) => {
          const label = s.step.label || (REL[s.step.rel] || REL.focus)[1];
          if (!label) return;
          const chip = el("div", "lf-chip");
          chip.style.top = (row++ * 128) + "px";
          const bar = el("div", "bar"); bar.style.background = s.color;
          const box = el("div", "");
          const t1 = el("div", "t1", label); t1.style.color = s.color;
          box.appendChild(t1); box.appendChild(el("div", "t2", (s.step.chi || []).join(" – ")));
          chip.appendChild(bar); chip.appendChild(box);
          legend.appendChild(chip); s.chip = chip;
        });
        inner._lf = S;
      },
      enter(tl, inner, ln, ctx) {
        const S = inner._lf, v = ln.visual, t0 = ln.start, span = Math.max(2, ctx.until - t0);
        const nodeGs = Object.values(S.nodes).map((n) => n.g);
        const how = variantOf("wheel", v, ["tilt", "assemble", "spin"]);
        if (how === "tilt") {  // mặt đồng hồ nằm ngửa trong không gian 3D rồi dựng lên
          tl.fromTo(S.wrap, { rotationX: 62, rotationZ: -24, scale: .72, opacity: 0, transformPerspective: 1600 },
            { rotationX: 0, rotationZ: 0, scale: 1, opacity: 1, duration: 1.5, ease: "power3.out" }, t0);
          tl.fromTo(nodeGs, { scale: 0, transformOrigin: "50% 50%" },
            { scale: 1, duration: .6, ease: "back.out(2.2)", stagger: .045 }, t0 + .35);
        } else if (how === "assemble") {  // mười hai chi bay từ tâm ra đúng vị trí trên vòng
          tl.fromTo(S.wrap, { opacity: 0 }, { opacity: 1, duration: .4 }, t0);
          CHI.forEach((c, k) => {
            const a = (-90 + k * 30) * Math.PI / 180;
            tl.fromTo(S.nodes[c].g, { x: -Math.cos(a) * 360, y: -Math.sin(a) * 360, scale: .3 },
              { x: 0, y: 0, scale: 1, duration: .8, ease: "expo.out" }, t0 + .15 + k * .05);
          });
          tl.fromTo(S.deco, { scale: .6, svgOrigin: "0 0", opacity: 0 }, { scale: 1, opacity: 1, duration: 1.2, ease: "power3.out" }, t0 + .1);
        } else {  // spin: cả vòng xoay vào như bánh la bàn, dừng có đà
          tl.fromTo(S.wrap, { rotation: -150, scale: .55, opacity: 0 },
            { rotation: 0, scale: 1, opacity: 1, duration: 1.4, ease: "back.out(1.3)" }, t0);
          tl.fromTo(nodeGs, { scale: 0, transformOrigin: "50% 50%" },
            { scale: 1, duration: .5, ease: "back.out(2.4)", stagger: { each: .035, from: "random" } }, t0 + .6);
        }
        tl.fromTo(S.deco, { rotation: 0, svgOrigin: "0 0" }, { rotation: 14, duration: span, ease: "none" }, t0);
        tl.fromTo(S.st, { scale: 1 }, { scale: 1.035, duration: span, ease: "none" }, t0);
        if (S.title) tl.fromTo(S.title, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: .6 }, t0 + .5);
        if (v.focus && S.nodes[v.focus]) {
          const n = S.nodes[v.focus];
          tl.to(n.circ, { fill: css("--accent"), duration: .5 }, t0 + 1.1);
          tl.to(n.txt, { fill: "#0b1130", duration: .5 }, t0 + 1.1);
          tl.to(n.g, { scale: 1.16, duration: .45, ease: "back.out(3)" }, t0 + 1.1);
        }
        let prev = [];
        S.steps.forEach((s, k) => {
          const t = when(ctx, s.step, t0 + 1.4 + k * 1.2);
          prev.forEach((p) => {
            if (p.path) tl.to(p.path, { opacity: .28, duration: .45 }, t);
            if (p.chip) tl.to(p.chip, { opacity: .45, duration: .45 }, t);
          });
          if (s.path) drawOn(tl, s.path, t, 1.0);
          (s.step.chi || []).forEach((c) => {
            const n = S.nodes[c]; if (!n) return;
            tl.to(n.circ, { fill: s.color, stroke: s.color, duration: .4 }, t + .2);
            tl.to(n.txt, { fill: "#0b1130", duration: .4 }, t + .2);
            tl.fromTo(n.g, { scale: 1 }, { scale: 1.2, duration: .35, ease: "back.out(3)", yoyo: true, repeat: 1 }, t + .2);
          });
          if (s.chip) tl.fromTo(s.chip, { x: 80, opacity: 0 }, { x: 0, opacity: 1, duration: .55, ease: "power4.out" }, t + .1);
          prev.push(s);
        });
      },
    },

    // Ngũ hành: vòng tương sinh + sao tương khắc; mỗi bước là một thẻ năm sinh
    // lật 3D bên trái và mũi tên quan hệ vẽ ra bên phải.
    elements: {
      build(inner, ln) {
        const v = ln.visual, S = { steps: [] };
        const st = el("div", "lf-stage"); inner.appendChild(st);
        const wrap = el("div", "lf-elem"); st.appendChild(wrap);
        const svg = sv("svg", { viewBox: "-420 -420 840 840" }, wrap);
        const pos = {};
        ELEM.forEach((e, k) => {
          const a = (-90 + k * 72) * Math.PI / 180;
          pos[e] = { x: Math.cos(a) * 300, y: Math.sin(a) * 300, a: -90 + k * 72 };
        });
        const base = sv("g", {}, svg);
        S.ring = sv("circle", { r: 300, class: "base", "stroke-dasharray": "4 10" }, base);
        const star = ELEM.map((e, k) => pos[ELEM[(k * 2) % 5]]);
        S.star = sv("path", { d: "M" + star.map((p) => `${p.x},${p.y}`).join(" L") + " Z", class: "base", opacity: .45 }, base);
        const arrows = sv("g", {}, svg);
        const nodes = {};
        ELEM.forEach((e) => {
          const g = sv("g", { transform: `translate(${pos[e].x},${pos[e].y})` }, svg);
          const inG = sv("g", {}, g);
          sv("circle", { r: 86, fill: ELEM_COLOR[e], opacity: .95 }, inG);
          const t = sv("text", { class: "el-t", fill: ELEM_INK[e] }, inG); t.textContent = e;
          nodes[e] = inG;
        });
        if (v.year && pos[v.year.element]) {
          const p = pos[v.year.element];
          S.halo = sv("circle", { cx: p.x, cy: p.y, r: 112, fill: "none", stroke: css("--accent"),
            "stroke-width": 5, "stroke-dasharray": "14 12" }, svg);
          const lab = el("div", "lf-yearlabel", v.year.label || "");
          lab.style.left = (1010 + 420 + p.x - 150) + "px"; lab.style.top = (40 + 420 + p.y + 130) + "px";
          st.appendChild(lab); S.yearLabel = lab;
        }
        (v.steps || []).forEach((step) => {
          const a = pos[step.from], b = pos[step.to];
          const color = ELEM_COLOR[step.from] || css("--accent");
          let path = null, head = null;
          if (step.kind === "hoa" && a) {
            path = sv("circle", { cx: a.x, cy: a.y, r: 118, fill: "none", stroke: color, "stroke-width": 10 }, arrows);
          } else if (a && b) {
            let p1, p2, dir;
            if (step.kind === "sinh") {  // cung tròn theo vòng sinh, chừa chỗ cho hai nút
              const a1 = (a.a + 19) * Math.PI / 180, a2 = (a.a + 72 - 19) * Math.PI / 180;
              p1 = [Math.cos(a1) * 300, Math.sin(a1) * 300]; p2 = [Math.cos(a2) * 300, Math.sin(a2) * 300];
              path = sv("path", { d: `M${p1} A300 300 0 0 1 ${p2}`, class: "arrow", stroke: color }, arrows);
              dir = (a.a + 72 - 19 + 90);
            } else {  // tương khắc: dây cung thẳng
              const dx = b.x - a.x, dy = b.y - a.y, L = Math.hypot(dx, dy), u = [dx / L, dy / L];
              p1 = [a.x + u[0] * 100, a.y + u[1] * 100]; p2 = [b.x - u[0] * 108, b.y - u[1] * 108];
              path = sv("path", { d: `M${p1} L${p2}`, class: "arrow", stroke: color }, arrows);
              dir = Math.atan2(dy, dx) * 180 / Math.PI;
            }
            head = sv("path", { d: "M-2,-16 L26,0 L-2,16 Z", fill: color,
              transform: `translate(${p2[0]},${p2[1]}) rotate(${dir})` }, arrows);
          }
          const card = el("div", "lf-card");
          const c = step.card || {};
          card.appendChild(el("div", "yr", c.yr || ""));
          card.appendChild(el("div", "sub", c.sub || ""));
          card.appendChild(el("div", "note", c.note || ""));
          if (step.pill) { const pl = el("div", "pill", step.pill); pl.style.background = color; card.appendChild(pl); }
          st.appendChild(card);
          S.steps.push({ step, path, head, card, color });
        });
        S.wrap = wrap; S.nodes = nodes; S.st = st;
        S.title = title(st, v.title || "NGŨ HÀNH NẠP ÂM", 150, 124);
        inner._lf = S;
      },
      enter(tl, inner, ln, ctx) {
        const S = inner._lf, t0 = ln.start, span = Math.max(2, ctx.until - t0);
        if (variantOf("elements", ln.visual, ["swing", "rise"]) === "swing") {
          tl.fromTo(S.wrap, { rotationY: -40, scale: .8, opacity: 0, transformPerspective: 1700 },
            { rotationY: 0, scale: 1, opacity: 1, duration: 1.3, ease: "power3.out" }, t0);
        } else {  // ngũ hành trồi lên từ đáy khung, nghiêng về phía người xem
          tl.fromTo(S.wrap, { y: 260, rotationX: 40, opacity: 0, transformPerspective: 1700 },
            { y: 0, rotationX: 0, opacity: 1, duration: 1.2, ease: "expo.out" }, t0);
        }
        tl.fromTo(Object.values(S.nodes), { scale: 0, transformOrigin: "50% 50%" },
          { scale: 1, duration: .6, ease: "back.out(2)", stagger: .08 }, t0 + .3);
        drawOn(tl, S.ring, t0 + .4, 1.2); drawOn(tl, S.star, t0 + .9, 1.4);
        if (S.halo) tl.fromTo(S.halo, { rotation: 0, svgOrigin: `${S.halo.getAttribute("cx")} ${S.halo.getAttribute("cy")}`, opacity: 0 },
          { rotation: 90, opacity: 1, duration: span, ease: "none" }, t0 + .8);
        if (S.yearLabel) tl.fromTo(S.yearLabel, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: .5 }, t0 + 1.0);
        if (S.title) tl.fromTo(S.title, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: .6 }, t0 + .4);
        S.steps.forEach((s) => gsap.set(s.card, { opacity: 0 }));
        let prev = null, prevYr = null;
        S.steps.forEach((s, k) => {
          const t = when(ctx, s.step, t0 + 1.5 + k * 1.5);
          if (prev) {
            tl.to(prev.card, { rotationY: 70, opacity: 0, duration: .4, ease: "power2.in", transformPerspective: 1400 }, t - .1);
            if (prev.path) tl.to([prev.path, prev.head].filter(Boolean), { opacity: 0, duration: .4 }, t);
          }
          tl.fromTo(s.card, { rotationY: -80, opacity: 0, transformPerspective: 1400 },
            { rotationY: 0, opacity: 1, duration: .75, ease: "power3.out" }, t + .15);
          const yrEl = s.card.querySelector(".yr"), target = parseInt(s.step.card && s.step.card.yr, 10);
          if (!isNaN(target)) {  // đếm số năm tới giá trị thật
            const o = { v: prevYr != null ? prevYr : target - 24 };
            tl.to(o, { v: target, duration: .9, ease: "power2.out",
              onUpdate: () => { yrEl.textContent = String(Math.round(o.v)); } }, t + .15);
            prevYr = target;
          }
          if (s.path) drawOn(tl, s.path, t + .35, .9);
          if (s.head) tl.fromTo(s.head, { opacity: 0, scale: 0, transformOrigin: "50% 50%" },
            { opacity: 1, scale: 1, duration: .3, ease: "back.out(3)" }, t + 1.15);
          [s.step.from, s.step.to].forEach((e) => {
            if (S.nodes[e]) tl.fromTo(S.nodes[e], { scale: 1 }, { scale: 1.16, duration: .35, yoyo: true, repeat: 1, ease: "back.out(3)" }, t + .5);
          });
          prev = s;
        });
      },
    },

    // Hàng thẻ năm sinh lật vào đúng lúc giọng đọc nói tới năm đó.
    years: {
      build(inner, ln) {
        const row = el("div", "lf-years");
        const cards = (ln.visual.items || []).map((it) => {
          const c = el("div", "lf-ycard");
          c.appendChild(el("div", "yr", it.yr || ""));
          if (it.sub) c.appendChild(el("div", "sub", it.sub));
          if (it.note) c.appendChild(el("div", "note", it.note));
          row.appendChild(c);
          return c;
        });
        if (cards.length > 3) row.classList.add("many");
        inner.appendChild(row);
        inner._lf = { cards };
      },
      enter(tl, inner, ln, ctx) {
        const S = inner._lf, items = ln.visual.items || [];
        const how = variantOf("years", ln.visual, ["flip", "deal", "count"]);
        let last = ln.start;
        S.cards.forEach((c, k) => {
          const it = items[k];
          const t = when(ctx, { at: it.at || ln.sentence_id, word: it.word || it.yr }, ln.start + .3 + k * .45);
          const at = Math.max(ln.start, t - .15);
          last = Math.max(last, t);
          if (how === "flip") {  // lật 3D đúng lúc nghe năm đó
            tl.fromTo(c, { rotationY: -95, opacity: 0, y: 40, transformPerspective: 1400 },
              { rotationY: 0, opacity: 1, y: 0, duration: .8, ease: "power3.out" }, at);
          } else if (how === "deal") {  // chia bài: bay ra từ một xấp ở giữa đáy khung
            tl.fromTo(c, { x: (S.cards.length / 2 - k - .5) * 330, y: 360, rotation: -14 + k * 7, opacity: 0 },
              { x: 0, y: 0, rotation: 0, opacity: 1, duration: .75, ease: "power3.out" }, at);
          } else {  // đếm: thẻ nở ra, con số chạy tới năm thật
            tl.fromTo(c, { scale: .6, opacity: 0 }, { scale: 1, opacity: 1, duration: .5, ease: "back.out(2)" }, at);
            const yrEl = c.querySelector(".yr"), target = parseInt(it.yr, 10);
            if (!isNaN(target)) {
              const o = { v: target - 36 };
              tl.to(o, { v: target, duration: .9, ease: "power3.out", onUpdate: () => { yrEl.textContent = String(Math.round(o.v)); } }, at);
            }
          }
        });
        const idle = Math.max(1, ctx.until - last - .9);
        S.cards.forEach((c, k) => tl.to(c, { y: k % 2 ? 10 : -10, duration: idle, ease: "sine.inOut" }, last + .9));
      },
    },

    // Danh sách đánh số: từng mục bật vào theo câu, mục cũ lùi mờ.
    list: {
      build(inner, ln) {
        const st = el("div", "lf-stage"); inner.appendChild(st);
        const box = el("div", "lf-list"); st.appendChild(box);
        const items = ln.visual.items || [];
        const H = Math.min(130, Math.floor((640 - 22 * (items.length - 1)) / Math.max(1, items.length)));
        const rows = items.map((it, k) => {
          const r = el("div", "lf-item");
          const off = Math.max(0, (640 - (items.length * (H + 22) - 22)) / 2);
          r.style.top = (off + k * (H + 22)) + "px"; r.style.height = H + "px";
          r.appendChild(el("div", "no", String(k + 1)));
          r.appendChild(el("div", "tx", it.text || ""));
          box.appendChild(r);
          return r;
        });
        inner._lf = { rows, title: title(st, ln.visual.title, 260, 124) };
      },
      enter(tl, inner, ln, ctx) {
        const S = inner._lf, items = ln.visual.items || [];
        if (S.title) tl.fromTo(S.title, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .5 }, ln.start + .1);
        const how = variantOf("list", ln.visual, ["cascade", "stack", "spotlight"]);
        if (how === "spotlight")  // cả danh sách hiện mờ sẵn, câu nào nói tới thì mục đó sáng lên
          tl.fromTo(S.rows, { opacity: 0, y: 20 }, { opacity: .32, y: 0, duration: .6, stagger: .08, ease: "power2.out" }, ln.start + .2);
        else S.rows.forEach((r) => gsap.set(r, { opacity: 0 }));
        S.rows.forEach((r, k) => {
          const t = when(ctx, items[k], ln.start + .4 + k * .8);
          if (k) tl.to(S.rows.slice(0, k), { opacity: how === "spotlight" ? .32 : .45, scale: 1, duration: .4 }, t);
          if (how === "cascade") {
            tl.fromTo(r, { x: -120, rotationY: -22, opacity: 0, transformPerspective: 1400 },
              { x: 0, rotationY: 0, opacity: 1, duration: .7, ease: "power4.out" }, t);
          } else if (how === "stack") {  // bật lên từ đáy như lò xo
            tl.fromTo(r, { y: 220, opacity: 0, scale: .9 }, { y: 0, opacity: 1, scale: 1, duration: .6, ease: "back.out(1.8)" }, t);
          } else {
            tl.to(r, { opacity: 1, scale: 1.04, duration: .45, ease: "power2.out" }, t);
          }
          tl.fromTo(r.querySelector(".no"), { scale: 0 }, { scale: 1, duration: .45, ease: "back.out(2.6)" }, t + .12);
        });
      },
    },
  };

  // Dòng thời gian: các mốc năm trên một trục, một điểm sáng chạy tới từng mốc
  // đúng lúc được đọc (spatial-pan-stations, rút gọn một khung).
  visuals.timeline = {
    build(inner, ln) {
      const v = ln.visual, items = v.items || [];
      const st = el("div", "lf-stage"); inner.appendChild(st);
      const box = el("div", "lf-tl"); st.appendChild(box);
      box.appendChild(el("div", "lf-tl-axis"));
      const dot = el("div", "lf-tl-dot"); box.appendChild(dot);
      const W = 1500, gap = items.length > 1 ? W / (items.length - 1) : 0;
      const marks = items.map((it, k) => {
        const m = el("div", "lf-tl-mark" + (it.now ? " now" : ""));
        m.style.left = (k * gap) + "px";
        const up = k % 2 === 0;
        m.appendChild(el("div", "pin"));
        const lab = el("div", "lab " + (up ? "up" : "down"));
        lab.appendChild(el("div", "yr", it.yr || ""));
        if (it.label) lab.appendChild(el("div", "sub", it.label));
        m.appendChild(lab); box.appendChild(m);
        return m;
      });
      inner._lf = { box, dot, marks, gap, title: title(st, v.title, 210, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, items = ln.visual.items || [];
      if (S.title) tl.fromTo(S.title, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .5 }, ln.start + .1);
      tl.fromTo(S.box.querySelector(".lf-tl-axis"), { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: 1.0, ease: "power3.inOut" }, ln.start);
      tl.fromTo(S.dot, { opacity: 0, x: 0 }, { opacity: 1, duration: .3 }, ln.start + .5);
      S.marks.forEach((m, k) => {
        const t = when(ctx, { at: items[k].at || ln.sentence_id, word: items[k].word || items[k].yr }, ln.start + .6 + k * .6);
        tl.to(S.dot, { x: k * S.gap, duration: .55, ease: "power3.inOut" }, t - .3);
        tl.fromTo(m.querySelector(".pin"), { scaleY: 0 }, { scaleY: 1, duration: .35, ease: "back.out(2)" }, t);
        tl.fromTo(m.querySelector(".lab"), { opacity: 0, y: m.querySelector(".up") ? 30 : -30 },
          { opacity: 1, y: 0, duration: .5, ease: "power3.out" }, t + .05);
      });
    },
  };

  // So sánh hai vế: hai thẻ mở như cuốn sách (split-tilt-cards).
  visuals.compare = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-cmp"); inner.appendChild(st);
      const mk = (side, d) => {
        const c = el("div", "lf-cmp-card " + side);
        if (d.eyebrow) c.appendChild(el("div", "eb", d.eyebrow));
        c.appendChild(el("div", "hd", d.title || ""));
        if (d.body) c.appendChild(el("div", "bd", d.body));
        if (d.badge) c.appendChild(el("div", "badge", d.badge));
        st.appendChild(c); return c;
      };
      inner._lf = { L: mk("left", v.left || {}), Rt: mk("right", v.right || {}), title: title(st, v.title, 210, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, v = ln.visual;
      if (S.title) tl.fromTo(S.title, { opacity: 0 }, { opacity: 1, duration: .5 }, ln.start + .1);
      const tL = when(ctx, v.left, ln.start + .2), tR = when(ctx, v.right, ln.start + 1.2);
      tl.fromTo(S.L, { x: -260, rotationY: 34, opacity: 0, transformPerspective: 1600 },
        { x: 0, rotationY: 12, opacity: 1, duration: .8, ease: "power3.out" }, tL);
      tl.fromTo(S.Rt, { x: 260, rotationY: -34, opacity: 0, transformPerspective: 1600 },
        { x: 0, rotationY: -12, opacity: 1, duration: .8, ease: "power3.out" }, tR);
      [S.L, S.Rt].forEach((c, k) => {
        const b = c.querySelector(".badge");
        if (b) tl.fromTo(b, { scale: 0 }, { scale: 1, duration: .45, ease: "back.out(3)" }, (k ? tR : tL) + .7);
      });
      tl.to(S.L, { y: -8, duration: Math.max(1, ctx.until - tR - 1), ease: "sine.inOut" }, tR + .9);
      tl.to(S.Rt, { y: 8, duration: Math.max(1, ctx.until - tR - 1), ease: "sine.inOut" }, tR + .9);
    },
  };

  // Một con số lớn đếm lên cùng vòng tiến độ (dataviz-countup).
  visuals.stat = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-stat"); inner.appendChild(st);
      const svg = sv("svg", { viewBox: "-260 -260 520 520", class: "ring" }, st);
      sv("circle", { r: 230, class: "track" }, svg);
      const arc = sv("circle", { r: 230, class: "arc", transform: "rotate(-90)" }, svg);
      const num = el("div", "num", String(v.value));
      const lab = el("div", "lab", v.label || "");
      st.appendChild(num); st.appendChild(lab);
      if (v.suffix) num.setAttribute("data-suffix", v.suffix);
      inner._lf = { arc, num, lab };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, v = ln.visual, t = when(ctx, v, ln.start + .3);
      drawOn(tl, S.arc, t, 1.4, "power2.out");
      const o = { v: 0 }, target = Number(v.value) || 0, suf = v.suffix || "";
      tl.to(o, { v: target, duration: 1.4, ease: "power2.out", onUpdate: () => { S.num.textContent = Math.round(o.v) + suf; } }, t);
      tl.fromTo(S.num, { scale: .7, opacity: 0 }, { scale: 1, opacity: 1, duration: .6, ease: "back.out(2)" }, t);
      tl.fromTo(S.lab, { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: .5, ease: "power3.out" }, t + .5);
    },
  };

  /* ---------- Chuyển cảnh (6 biến thể) ----------
     Luật chọn: vào thẻ chương = đổi phần -> zoom-through / iris (cut-catalog:
     state change). Cảnh cũ có ảnh bên dưới -> chỉ dùng loại kéo ảnh đi cùng
     (blur trên ảnh sẽ đè filter màu của kênh). Còn lại chọn trong cả kho. */
  function transition(tl, oldS, newS, T, ctx) {
    const kinds = ctx.toChapter ? ["zoom", "iris"]
      : ctx.oldClip ? ["blurfade", "push", "pushup"]
      : ["blurfade", "push", "pushup", "zoom", "wipe", "iris"];
    const k = pick("transition", kinds);
    const clip = ctx.oldClip;
    if (k === "push" || k === "pushup") {  // cut-the-curve: hai bên cùng hướng, cắt ở đỉnh tốc độ
      const ax = k === "push" ? "x" : "y", d = 230;
      tl.to(oldS, { [ax]: -d, duration: .34, ease: "power4.in" }, T);
      if (clip) tl.to(clip, { [ax]: -d, duration: .34, ease: "power4.in" }, T);
      tl.to(oldS, { opacity: 0, duration: .22, ease: "power1.in" }, T + .1);
      tl.fromTo(newS, { [ax]: d, opacity: 0 }, { [ax]: 0, opacity: 1, duration: .42, ease: "power4.out" }, T + .32);
    } else if (k === "zoom") {  // zoom-through: cả khung lao về phía người xem
      tl.to(oldS, { scale: 1.2, filter: "blur(18px)", duration: .22, ease: "power3.in" }, T);
      tl.to(oldS, { opacity: 0, duration: .22, ease: "none" }, T);
      tl.fromTo(newS, { opacity: 0, scale: .75, filter: "blur(18px)" },
        { opacity: 1, scale: 1, filter: "blur(0px)", duration: .55, ease: "expo.out" }, T + .22);
    } else if (k === "wipe") {  // quét ngang, mép vàng dẫn đường
      tl.fromTo(newS, { opacity: 1, clipPath: "inset(0% 0% 0% 100%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: .6, ease: "power3.inOut" }, T);
      tl.to(oldS, { opacity: 0, duration: .2 }, T + .55);
    } else if (k === "iris") {  // mở từ tâm như ống kính
      tl.fromTo(newS, { opacity: 1, clipPath: "circle(0% at 50% 45%)" }, { clipPath: "circle(78% at 50% 45%)", duration: .7, ease: "power2.inOut" }, T);
      tl.to(oldS, { opacity: 0, duration: .2 }, T + .6);
    } else {
      return false;  // blurfade: để style tự chuyển (mỗi style một chất riêng)
    }
    return true;
  }

  window.HF_LONG = { layouts, visuals, chapter, begin, pick, transition };
})();
