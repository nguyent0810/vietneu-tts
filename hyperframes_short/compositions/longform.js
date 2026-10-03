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
  const esc = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  // Short dọc (1080x1920) chỉ mượn các cảnh chữ/minh hoạ; chuyển cảnh + không khí
  // giữ của riêng style short (đã chỉnh cho nhịp 30 giây).
  const PORTRAIT = document.documentElement.getAttribute("data-resolution") === "portrait";

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
      if (ln._chap === "slam" || ln._chap === "roll") t.split(/\s+/).forEach((wd) => { const sp = el("span", "lf-word", wd); tt.appendChild(sp); });
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
        // Gõ theo TỪNG TỪ: xén ngang cả khối làm tiêu đề hai dòng lộ ra theo cột,
        // giữa chừng thấy mảnh chữ vô nghĩa ("NĂM ĐINI").
        const ws = inner.querySelectorAll(".lf-word");
        tl.fromTo(ws, { opacity: 0 }, { opacity: 1, duration: .01, stagger: Math.min(.14, 1.2 / Math.max(1, ws.length)) }, t0 + .5);
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
          // Phải xong TRƯỚC lần làm sáng đầu tiên (đầu câu + .3s): tween mờ kết
          // thúc sau sẽ ghi đè mục đang được đọc về lại mờ.
          tl.fromTo(S.rows, { opacity: 0, y: 20 }, { opacity: .32, y: 0, duration: .24, stagger: .02, ease: "power2.out" }, ln.start);
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
          if (how !== "spotlight")  // spotlight: số thứ tự có sẵn, cả danh sách đọc được ngay
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
      // Khung dọc: trục DỌC, mốc xếp từ trên xuống, số lớn bên phải trục.
      if (PORTRAIT) box.classList.add("vert");
      const W = PORTRAIT ? 780 : 1500, gap = items.length > 1 ? W / (items.length - 1) : 0;
      const marks = items.map((it, k) => {
        const m = el("div", "lf-tl-mark" + (it.now ? " now" : ""));
        if (PORTRAIT) m.style.top = (k * gap) + "px"; else m.style.left = (k * gap) + "px";
        const up = PORTRAIT ? true : k % 2 === 0;
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
      const vert = S.box.classList.contains("vert");
      tl.fromTo(S.box.querySelector(".lf-tl-axis"), vert ? { scaleY: 0, transformOrigin: "50% 0%" } : { scaleX: 0, transformOrigin: "0% 50%" },
        vert ? { scaleY: 1, duration: 1.0, ease: "power3.inOut" } : { scaleX: 1, duration: 1.0, ease: "power3.inOut" }, ln.start);
      tl.fromTo(S.dot, { opacity: 0, x: 0 }, { opacity: 1, duration: .3 }, ln.start + .5);
      S.marks.forEach((m, k) => {
        const t = when(ctx, { at: items[k].at || ln.sentence_id, word: items[k].word || items[k].yr }, ln.start + .6 + k * .6);
        tl.to(S.dot, vert ? { y: k * S.gap, duration: .55, ease: "power3.inOut" } : { x: k * S.gap, duration: .55, ease: "power3.inOut" }, t - .3);
        tl.fromTo(m.querySelector(".pin"), vert ? { scaleX: 0 } : { scaleY: 0 }, vert ? { scaleX: 1, duration: .35, ease: "back.out(2)" } : { scaleY: 1, duration: .35, ease: "back.out(2)" }, t);
        tl.fromTo(m.querySelector(".lab"), vert ? { opacity: 0, x: 40 } : { opacity: 0, y: m.querySelector(".up") ? 30 : -30 },
          { opacity: 1, x: 0, y: 0, duration: .5, ease: "power3.out" }, t + .05);
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
      // Đếm từ đầu câu và CHẠM đích đúng lúc giọng đọc tới con số -- chờ tới lúc đọc
      // mới bắt đầu thì vòng trống ~2 giây (hook short mất khung đầu).
      const S = inner._lf, v = ln.visual, land = when(ctx, v, ln.start + .3);
      const t = ln.start + .1, cnt = Math.max(1.4, land + .5 - t);
      drawOn(tl, S.arc, t, cnt, "power2.out");
      const o = { v: 0 }, target = Number(v.value) || 0, suf = v.suffix || "";
      const plain = v.plain || /NĂM/i.test(v.label || "");
      tl.to(o, { v: target, duration: cnt, ease: "power2.out", onUpdate: () => { const n = String(Math.round(o.v)); S.num.textContent = (plain ? n : n.replace(/\B(?=(\d{3})+(?!\d))/g, ".")) + suf; } }, t);  // 20.000 kiểu Việt; năm 1885 thì không chấm
      tl.fromTo(S.num, { scale: .7, opacity: 0 }, { scale: 1, opacity: 1, duration: .6, ease: "back.out(2)" }, t);
      tl.fromTo(S.lab, { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: .5, ease: "power3.out" }, land);
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
    const fgClip = clip && clip.dataset.fg ? document.getElementById(clip.dataset.fg) : null;  // lớp chủ thể 2.5D
    if (k === "push" || k === "pushup") {  // cut-the-curve: hai bên cùng hướng, cắt ở đỉnh tốc độ
      const ax = k === "push" ? "x" : "y", d = 230;
      tl.to(oldS, { [ax]: -d, duration: .34, ease: "power4.in" }, T);
      if (clip) tl.to(clip, { [ax]: -d, duration: .34, ease: "power4.in" }, T);
      if (fgClip) tl.to(fgClip, { [ax]: -d, duration: .34, ease: "power4.in" }, T);
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

  /* ================= PHASE A (29/09/2026) =================
     Xu hướng motion 2026 cho video tài liệu/giải thích: nét vẽ tay "on twos"
     (Vox / Johnny Harris), kính lỏng, hạt chuyển động theo thuật toán, vệt
     sáng analog, chữ động theo lời. Tất cả tất định: rng hạt giống, không
     Math.random, mọi chuyển động nằm trên timeline đã pause. */
  const theme = () => (css("--lf-theme") || "night").replace(/["']/g, "");
  // "On twos": nét vẽ tay nhảy theo nấc 12 hình/giây trong video 30 hình/giây --
  // trông như được đặt tay lên khung, không trượt mượt như máy.
  const twos = (dur) => `steps(${Math.max(2, Math.round(dur * 12))})`;
  function jitter(seed) { const r = HF.rng(HF.hashSeed(String(seed))); return () => r() - 0.5; }
  // Vòng tròn vẽ tay: hơi méo, vẽ quá một chút (1.12 vòng) như bút lướt.
  function sketchLoop(cx, cy, rx, ry, seed) {
    const j = jitter(seed), N = 30, pts = [];
    for (let k = 0; k <= N; k++) {
      const a = -Math.PI * 0.62 + (k / N) * Math.PI * 2 * 1.12, w = 1 + j() * 0.09;
      pts.push(`${(cx + Math.cos(a) * rx * w).toFixed(1)},${(cy + Math.sin(a) * ry * w).toFixed(1)}`);
    }
    return "M" + pts.join(" L");
  }
  function sketchUnder(x1, x2, y, seed) {
    const j = jitter(seed), mid = (x1 + x2) / 2;
    return `M${x1},${y + j() * 6} Q${mid},${y + 10 + j() * 8} ${x2},${y - 4 + j() * 6}`;
  }
  // Nét vẽ tay / dạ quang là PHẦN TỬ CON của thứ nó đánh dấu, đặt bằng CSS
  // inset + SVG toạ độ chuẩn hoá 0..100: không đo toạ độ lúc dựng. Đo lúc dựng
  // từng lệch vì font (Lora) nạp xong SAU khi dựng -> chữ đổi bề rộng, dải dạ
  // quang nằm lệch sang chữ khác.
  function sketchOn(target, cls, d) {
    const s = sv("svg", { class: "lf-sketch " + cls, viewBox: "0 0 100 100", preserveAspectRatio: "none" });
    const p = sv("path", { d, class: "lf-ink", "vector-effect": "non-scaling-stroke" }, s);
    target.appendChild(s);
    return p;
  }
  // Vẽ ra bằng cách LỘ dần (không dùng stroke-dash): với non-scaling-stroke,
  // dash tính theo pixel nên pathLength=1 hết tác dụng -> nét thành chấm 1px.
  // Gạch chân: quét trái -> phải. Vòng tròn: mặt nạ hình nón quay một vòng.
  function drawSketch(tl, p, at, dur) {
    const s = p.ownerSVGElement;
    if (s.classList.contains("loop"))
      tl.fromTo(s, { "--sweep": "0deg" }, { "--sweep": "400deg", duration: dur, ease: twos(dur) }, at);
    else
      tl.fromTo(s, { clipPath: "inset(-20% 100% -20% 0%)" }, { clipPath: "inset(-20% 0% -20% 0%)", duration: dur, ease: twos(dur) }, at);
  }
  // Bút dạ quang (Vox): dải màu nghiêng quét qua SAU chữ.
  function marker(target, color) {
    const m = el("div", "lf-marker");
    if (color) m.style.background = color;
    target.insertBefore(m, target.firstChild);
    return m;
  }
  function sweep(tl, m, at, dur) {
    tl.fromTo(m, { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: dur || .5, ease: twos(dur || .5) }, at);
  }
  // Vệt sáng kính: dải trắng mờ trượt chéo qua tấm panel một lần khi nó vào.
  function sheen(tl, panel, at) {
    if (!panel) return;
    const wrap = el("div", "lf-sheen-wrap"), g = el("div", "lf-sheen");
    wrap.appendChild(g); panel.appendChild(wrap);
    tl.fromTo(g, { xPercent: -160 }, { xPercent: 260, duration: 1.1, ease: "power2.inOut" }, at);
  }

  // ---- 1) Trích dẫn: trang sách xưa / chữ động / kính ----
  visuals.quote = {
    build(inner, ln) {
      const v = ln.visual, how = v.variant === "type" ? "type" : variantOf("quote", v, ["page", "kinetic", "glass"]);
      ln._q = how;
      const st = el("div", "lf-stage lf-q lf-q-" + how); inner.appendChild(st);
      const card = el("div", "lf-q-card"); st.appendChild(card);
      if (how === "page") { card.appendChild(el("div", "tape a")); card.appendChild(el("div", "tape b")); }
      const body = el("div", "lf-q-text"); card.appendChild(body);
      // Chữ lấy đúng câu đang đọc (bỏ dấu **), cụm đánh dấu là cụm được tô.
      let words = (ln.words || []).map((w) => ({ t: clean(w.w), hot: !!w.hot, at: w.t }));
      // "Trong kinh X, Đức Phật dạy: <lời kinh>" -> thẻ chỉ mang lời kinh (nguồn đã ghi
      // ở dòng dưới thẻ). Phần dẫn ngắn thì giữ nguyên cả câu.
      const colon = words.findIndex((w) => /:$/.test(w.t));
      if (v.source && colon >= 0 && words.length - colon > 3) {
        words = words.slice(colon + 1);
        words[0] = { ...words[0], t: words[0].t.charAt(0).toUpperCase() + words[0].t.slice(1) };
      }
      // class "qw", KHÔNG "w": .w là chữ phụ đề trong base.css (trắng, gạch chân)
      const spans = words.map((w) => { const sp = el("span", "qw" + (w.hot ? " hot" : "")); sp.appendChild(document.createTextNode(w.t)); body.appendChild(sp); return sp; });
      if (v.source) card.appendChild(el("div", "lf-q-src", "— " + v.source));
      inner._lf = { st, card, spans, words, markers: [] };
      if (how === "page")  // bút dạ quang dưới từng từ được đánh dấu
        spans.forEach((sp, k) => { if (words[k].hot) inner._lf.markers.push({ m: marker(sp), at: words[k].at }); });
    },
    enter(tl, inner, ln) {
      const S = inner._lf, how = ln._q, t0 = ln.start;
      if (how === "page") {  // tờ giấy rơi xuống, nghiêng, nhảy nấc như ảnh chụp từng khung
        tl.fromTo(S.card, { y: -220, rotation: -9, opacity: 0 }, { y: 0, rotation: -2.2, opacity: 1, duration: .6, ease: twos(.6) }, t0);
        tl.fromTo(S.card.querySelectorAll(".tape"), { scale: 0 }, { scale: 1, duration: .25, ease: twos(.25), stagger: .1 }, t0 + .55);
        tl.fromTo(S.spans, { opacity: 0 }, { opacity: 1, duration: .3, stagger: .015 }, t0 + .3);
        S.markers.forEach((mk) => sweep(tl, mk.m, mk.at, .3));
        tl.to(S.card, { rotation: -1.4, duration: Math.max(1, ln.end - t0 - 1), ease: twos(Math.max(1, ln.end - t0 - 1)) }, t0 + 1);
      } else if (how === "kinetic") {  // từng từ hiện đúng lúc được đọc
        S.spans.forEach((sp, k) => {
          const hot = S.words[k].hot;
          tl.fromTo(sp, { opacity: 0, y: 30, scale: hot ? 1.5 : 1 },
            { opacity: 1, y: 0, scale: 1, duration: hot ? .4 : .28, ease: hot ? "back.out(2.5)" : "power3.out" }, S.words[k].at - .05);
        });
      } else if (how === "type") {  // máy chữ (S-tier): từng ký tự gõ ra đều, xong trước cuối câu
        tl.fromTo(S.card, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: .45, ease: "power3.out" }, t0);
        const chars = [];
        S.spans.forEach((sp) => { const txt = sp.textContent; sp.textContent = "";
          Array.from(txt).forEach((c) => { const e = el("span", "tc", c); sp.appendChild(e); chars.push(e); }); });
        const a = t0 + .45, b = Math.max(a + .8, ln.end - .5), step = (b - a) / Math.max(1, chars.length);
        chars.forEach((c, k) => tl.fromTo(c, { opacity: 0 }, { opacity: 1, duration: .01 }, a + k * step));
      } else {  // glass: tấm kính trồi lên, vệt sáng lướt qua, chữ hiện theo cụm
        tl.fromTo(S.card, { y: 60, opacity: 0, scale: .96 }, { y: 0, opacity: 1, scale: 1, duration: .8, ease: "expo.out" }, t0);
        sheen(tl, S.card, t0 + .5);
        S.spans.forEach((sp, k) => tl.fromTo(sp, { opacity: .18 }, { opacity: 1, duration: .25 }, S.words[k].at - .05));
      }
    },
  };

  // ---- 2) Bố cục "ghim bảng": ảnh dán băng keo, rơi xuống từng nấc ----
  layouts.pinned = {
    build(inner, ln) {
      const s = ln.sentence_id % 2 ? 1 : -1;
      const g = el("div", "lf-pin"); g.style.transform = `rotate(${-2.4 * s}deg)`;
      g.appendChild(el("div", "tape a")); g.appendChild(el("div", "tape b"));
      inner.appendChild(g);
    },
    enter(tl, inner, ln) {
      const g = inner.querySelector(".lf-pin"); if (!g) return;
      tl.fromTo(g, { y: -160 }, { y: 0, duration: .5, ease: twos(.5) }, ln.start);
      tl.fromTo(g.querySelectorAll(".tape"), { scale: 0 }, { scale: 1, duration: .2, ease: twos(.2), stagger: .08 }, ln.start + .45);
    },
    enterCont() {},
    motion(tl, clip, ln, mEnd) {
      const s = ln.sentence_id % 2 ? 1 : -1;
      gsap.set(clip, { rotation: -2.4 * s });
      tl.fromTo(clip, { y: -160 }, { y: 0, duration: .5, ease: twos(.5) }, ln.start);
      tl.fromTo(clip, { scale: 1 }, { scale: 1.035, duration: Math.max(1, mEnd - ln.start), ease: "none" }, ln.start);
      return true;
    },
  };

  /* ================= PHASE B ================= */
  // ---- 2.5D: nền trôi chậm, chủ thể (tách bằng Vision) đẩy nhanh hơn ----
  layouts.depth = {
    build(inner) { inner.appendChild(el("div", "lf-full-shade")); },
    motion(tl, clip, ln, mEnd) {
      const fg = clip.dataset.fg ? document.getElementById(clip.dataset.fg) : null;
      const d = Math.max(1, mEnd - ln.start), s = ln.sentence_id % 2 ? 1 : -1;
      // Chênh tốc độ giữa hai lớp là thứ tạo chiều sâu: nền 1.06 -> 1.11,
      // chủ thể 1.07 -> 1.20 và dạt ngang gấp gần ba lần.
      tl.fromTo(clip, { scale: 1.06, x: 0 }, { scale: 1.11, x: -18 * s, duration: d, ease: "none" }, ln.start);
      if (fg) {
        tl.fromTo(fg, { opacity: 0 }, { opacity: 1, duration: .55, ease: "sine.out" }, ln.start);
        tl.to(fg, { opacity: 0, duration: .45, ease: "sine.in" }, Math.max(ln.start + .6, mEnd - .45));
        tl.fromTo(fg, { scale: 1.07, x: 0, y: 0 }, { scale: 1.2, x: -48 * s, y: -10, duration: d, ease: "none" }, ln.start);
      }
      return true;
    },
  };

  // ---- Bản đồ (vector lane): biên giới vẽ ra, ghim rơi đúng lúc được nhắc,
  // tuyến nối các ghim. Toạ độ đã nướng sẵn trong spec._geo (hf_geo.py). ----
  visuals.map = {
    build(inner, ln) {
      const v = ln.visual, G = v._geo || { countries: [], pins: [] };
      const st = el("div", "lf-stage lf-map"); inner.appendChild(st);
      const svg = sv("svg", { viewBox: "0 0 1920 1080", class: "lf-map-svg" }, st);
      const world = sv("g", { class: "world" }, svg);
      const S = { st, world, borders: [], fills: [], labels: [], pins: [], routes: [] };
      G.countries.forEach((c) => {
        const f = sv("path", { d: c.d, class: c.focus ? "cty focus" : "cty ctx" }, world);
        if (c.focus) { S.fills.push(f); S.borders.push(sv("path", { d: c.d, class: "border" }, world)); }
        if (c.label && c.lx > 0) {
          const t = sv("text", { x: c.lx, y: c.ly, class: "cty-label" }, world); t.textContent = c.label; S.labels.push(t);
        }
      });
      const routeG = sv("g", {}, world);
      G.pins.forEach((p, k) => {
        if (v.route && k > 0) {  // cung cong nhẹ giữa hai ghim liền nhau
          const a = G.pins[k - 1], mx = (a.x + p.x) / 2, my = (a.y + p.y) / 2 - Math.hypot(p.x - a.x, p.y - a.y) * .18;
          S.routes[k] = sv("path", { d: `M${a.x},${a.y} Q${mx},${my} ${p.x},${p.y}`, class: "route" }, routeG);
        }
        const g = sv("g", { transform: `translate(${p.x},${p.y})` }, world);
        const inG = sv("g", {}, g);
        const ring = sv("circle", { r: 12, class: "pulse" }, inG);
        sv("circle", { r: 11, class: "pin" }, inG);
        const card = el("div", "lf-pin-card " + (p.side || (k % 2 ? "left" : "right")));
        card.style.left = p.x + "px"; card.style.top = p.y + "px";
        card.appendChild(el("div", "nm", p.name || ""));
        if (p.sub) card.appendChild(el("div", "sb", p.sub));
        st.appendChild(card);
        S.pins.push({ g: inG, ring, card, p });
      });
      S.title = title(st, v.title, 150, 124);
      inner._lf = S;
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, t0 = ln.start, span = Math.max(2, ctx.until - t0);
      // Thu phóng CẢ sân khấu (bản đồ SVG + thẻ tên HTML) -- thu riêng SVG thì thẻ
      // tên trôi lệch khỏi ghim tới ~40px ở mép khung.
      tl.fromTo(S.world, { opacity: 0 }, { opacity: 1, duration: 1.1, ease: "power2.out" }, t0);
      tl.fromTo(S.st, { scale: .95 }, { scale: 1.04, duration: span, ease: "sine.out" }, t0);
      S.borders.forEach((b, k) => drawOn(tl, b, t0 + .3 + k * .25, 1.6, "power2.inOut"));
      tl.fromTo(S.fills, { opacity: 0 }, { opacity: 1, duration: .8, stagger: .2 }, t0 + 1.2);
      if (S.labels.length) tl.fromTo(S.labels, { opacity: 0 }, { opacity: 1, duration: .5, stagger: .1 }, t0 + 1.5);
      if (S.title) tl.fromTo(S.title, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .5 }, t0 + .2);
      S.pins.forEach((P, k) => {
        const t = when(ctx, P.p, t0 + 1.6 + k * 1.2);
        if (S.routes[k]) drawOn(tl, S.routes[k], t - .7, .8, "power2.inOut");
        tl.fromTo(P.g, { y: -60, opacity: 0 }, { y: 0, opacity: 1, duration: .5, ease: "back.out(2.4)" }, t);
        tl.fromTo(P.ring, { attr: { r: 12 }, opacity: .9 }, { attr: { r: 46 }, opacity: 0, duration: 1.1, ease: "power2.out", repeat: 1 }, t + .3);
        // Thẻ tên đặt bằng transform translate(-50%) -> chỉ tween opacity; tween x
        // sẽ ghi đè transform, thẻ nhảy khỏi ghim (skill maps: centered overlays).
        tl.fromTo(P.card, { opacity: 0 }, { opacity: 1, duration: .45, ease: "power2.out" }, t + .2);
        tl.fromTo(P.card.querySelector(".nm"), { x: P.card.classList.contains("left") ? 24 : -24 },
          { x: 0, duration: .5, ease: "power3.out" }, t + .2);
      });
    },
  };

  // ---- 3) Kính lỏng trên ảnh tràn khung: thẻ chữ khoá bằng kính thay chữ trần ----
  const fullBase = layouts.full;
  layouts.full = {
    build(inner, ln) {
      ln._fullSkin = ln._fullSkin || pick("fullskin", ["text", "glass"]);
      fullBase.build(inner, ln);
      const c = inner.querySelector(".lf-callout");
      if (c && ln._fullSkin === "glass") c.classList.add("lf-glass");
    },
    enter(tl, inner, ln) {
      fullBase.enter(tl, inner, ln);
      const c = inner.querySelector(".lf-callout.lf-glass");
      if (c) {  // tấm kính vào CÙNG lúc chữ khoá được đọc, không để kính rỗng chờ chữ
        const w = (ln.words || []).find((x) => x.hot), t = (w ? w.t : ln.start + .4) - .15;
        tl.fromTo(c, { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: .4, ease: "power3.out" }, t);
        sheen(tl, c, t + .4);
      }
    },
    enterCont(tl, inner, ln) { this.enter(tl, inner, ln); },
  };

  // ---- 4) Bút dạ quang / nét vẽ tay gắn vào các sơ đồ có sẵn ----
  // Gắn thêm vào một sơ đồ có sẵn: `measure` chạy NGAY SAU khi dựng (lúc chưa có
  // tween nào dịch/nghiêng phần tử -- đo vị trí mới đúng), `extra` chạy sau lối vào.
  const withInk = (base, extra, measure) => ({
    build(inner, ln, i, ctx) { base.build(inner, ln, i, ctx); if (measure) measure(inner, ln); },
    enter(tl, inner, ln, ctx) { base.enter(tl, inner, ln, ctx); extra(tl, inner, ln, ctx); },
  });
  // Danh sách: mục đang đọc được tô dạ quang.
  visuals.list = withInk(visuals.list, (tl, inner, ln, ctx) => {
    const items = ln.visual.items || [];
    (inner._marks || []).forEach((m, k) => sweep(tl, m, when(ctx, items[k], ln.start + .4 + k * .8) + .25, .45));
  }, (inner) => {
    inner._marks = inner._lf.rows.map((r) => marker(r.querySelector(".tx"), "var(--lf-marker)"));
  });
  // Thẻ năm: vòng tròn vẽ tay quanh năm được `mark` (hoặc thẻ cuối nếu không đánh dấu).
  visuals.years = withInk(visuals.years, (tl, inner, ln, ctx) => {
    const items = ln.visual.items || [], k = inner._circleAt, p = inner._circle;
    if (!p) return;
    const t = when(ctx, { at: items[k].at || ln.sentence_id, word: items[k].word || items[k].yr }, ln.start + 1) + .6;
    drawSketch(tl, p, t, .6);
  }, (inner, ln) => {
    const items = ln.visual.items || [];
    let k = items.findIndex((it) => it.mark);
    if (k < 0) k = items.length - 1;
    const card = inner._lf.cards[k]; if (!card) return;
    // Vòng vẽ tay là con của con số -> đi theo thẻ khi thẻ lật/bay vào.
    inner._circle = sketchOn(card.querySelector(".yr"), "loop", sketchLoop(50, 50, 47, 45, ln.sentence_id));
    inner._circleAt = k;
  });

  // ---- 5) Thẻ chương thêm biến thể "ink": gạch chân vẽ tay + chữ nhảy nấc ----
  CHAPTER_VARIANTS.push("ink");
  const chapBase = { build: chapter.build, enter: chapter.enter };
  chapter.build = function (inner, ln) {
    chapBase.build(inner, ln);
    // hạt bung ra khi thẻ chương vào (particle-burst)
    const b = el("div", "lf-burst");
    const r = HF.rng(HF.hashSeed("burst" + ln.sentence_id));
    for (let k = 0; k < 26; k++) {
      const d = el("i", ""); const a = (k / 26) * Math.PI * 2 + r() * .3, dist = 220 + r() * 360;
      d.dataset.x = String(Math.cos(a) * dist); d.dataset.y = String(Math.sin(a) * dist * .6);
      d.style.width = d.style.height = (3 + r() * 6).toFixed(1) + "px"; b.appendChild(d);
    }
    inner.querySelector(".lf-chap").appendChild(b);
    if (ln._chap === "ink") {
      inner._ink = sketchOn(inner.querySelector(".lf-chap-title"), "under", sketchUnder(2, 98, 45, ln.sentence_id));
      inner.querySelector(".lf-chap-rule").style.display = "none";
    }
  };
  chapter.enter = function (tl, inner, ln) {
    if (ln._chap === "ink") {
      const t0 = ln.start, q = (c) => inner.querySelector(c);
      tl.fromTo(q(".lf-chap-ghost"), { opacity: 0 }, { opacity: .5, duration: .6 }, t0);
      tl.fromTo(q(".lf-chap-no"), { opacity: 0 }, { opacity: 1, duration: .3, ease: twos(.3) }, t0 + .1);
      tl.fromTo(q(".lf-chap-title"), { opacity: 0, y: 40, rotation: -2 }, { opacity: 1, y: 0, rotation: 0, duration: .5, ease: twos(.5) }, t0 + .1);
      drawSketch(tl, inner._ink, t0 + .6, .5);
    } else chapBase.enter(tl, inner, ln);
    // set + to chứ không fromTo: fromTo vẽ trạng thái đầu ngay lúc dựng, hạt sẽ
    // lơ lửng giữa khung từ giây 0.
    const ps = inner.querySelectorAll(".lf-burst i"), tb = ln.start + .1;
    tl.set(ps, { x: 0, y: 0, opacity: 1, scale: 1 }, tb);
    tl.to(ps, { x: (k, e) => Number(e.dataset.x), y: (k, e) => Number(e.dataset.y), scale: .3,
      duration: 1.4, ease: "expo.out" }, tb);
    tl.to(ps, { opacity: 0, duration: 1.1, ease: "power2.in" }, tb + .3);
  };

  // Vệt sáng kính khi panel của sơ đồ vào (thẻ ngũ hành, thẻ so sánh, chip vòng con giáp).
  ["elements", "compare", "wheel"].forEach((k) => {
    visuals[k] = withInk(visuals[k], (tl, inner, ln) => {
      const S = inner._lf;
      const panels = k === "elements" ? S.steps.map((s) => s.card) : k === "compare" ? [S.L, S.Rt] : S.steps.map((s) => s.chip).filter(Boolean);
      panels.forEach((p, i) => sheen(tl, p, ln.start + 1 + i * .4));
    });
  });

  // ---- 6) Không khí: hạt bay + vệt sáng analog theo chủ đề style ----
  function ambient(tl, DUR, ctx) {
    const root = ctx.root, stage = document.getElementById("stage");
    const layer = el("div", "lf-ambient"); root.insertBefore(layer, stage);
    const night = theme() === "night", r = HF.rng(HF.hashSeed("ambient|" + Math.round(DUR)));
    const N = night ? 34 : 12, parts = [];
    for (let k = 0; k < N; k++) {
      const p = el("i", night ? "mote" : "petal");
      const size = night ? 2 + r() * 5 : 14 + r() * 12;
      p.style.width = size + "px"; p.style.height = (night ? size : size * .62) + "px";
      p.style.left = (r() * 1920).toFixed(0) + "px";
      layer.appendChild(p);
      parts.push({ p, period: night ? 14 + r() * 16 : 11 + r() * 9, phase: r(), sway: (night ? 22 : 90) * (.5 + r()),
        spin: night ? 0 : 180 + r() * 240, peak: night ? .2 + r() * .5 : .55 });
    }
    // Một tween tiến trình duy nhất: vị trí mỗi hạt là hàm của t -> tất định khi
    // seek bất kỳ, không cần đặt tween ở thời điểm âm.
    const clock = { t: 0 }, y0 = night ? 1120 : -60, y1 = night ? -60 : 1140;
    const place = () => parts.forEach((q) => {
      const f = ((clock.t / q.period) + q.phase) % 1;
      q.p.style.transform = `translate(${(Math.sin(f * Math.PI * 4) * q.sway).toFixed(1)}px, ${(y0 + (y1 - y0) * f).toFixed(1)}px) rotate(${(f * q.spin).toFixed(0)}deg)`;
      q.p.style.opacity = (q.peak * Math.sin(f * Math.PI)).toFixed(3);
    });
    place();
    tl.to(clock, { t: DUR, duration: DUR, ease: "none", onUpdate: place }, 0);
    // Vệt sáng ấm quét qua mỗi lần sang chương (analog light leak).
    const leak = el("div", "lf-leak " + (night ? "night" : "paper")); root.insertBefore(leak, stage);
    (ctx.LINES || []).forEach((ln) => {
      if (!ln.chapter_no) return;
      const t = Math.max(0, ln.start - .4);
      tl.set(leak, { xPercent: -120, opacity: 0 }, t);
      tl.to(leak, { xPercent: 130, duration: 2.6, ease: "sine.inOut" }, t);
      tl.to(leak, { opacity: night ? .35 : .55, duration: 1.3, ease: "sine.out" }, t);
      tl.to(leak, { opacity: 0, duration: 1.3, ease: "sine.in" }, t + 1.3);
    });
  }

  /* ================= PHASE C (29/09/2026) =================
     Theo quy trình motion graphic "thuần code" (không footage): chữ động theo
     NGHĨA của từ, minh hoạ SVG tự vẽ nét, nền shader WebGL cho thẻ kết. */

  // ---- C2: chữ lớn với hiệu ứng theo nghĩa ----
  const FX_LEXICON = [
    ["dissolve", ["vô thường", "buông", "tan ", "qua đi", "biến mất", "không còn"]],
    ["rays", ["tỉnh thức", "bình an", "giác ngộ", "thành đạo", "ánh sáng", "thuận", "an lạc", "tỏa sáng"]],
    ["split", ["xung", "chia", "đối diện", "tách", "hai cực"]],
    ["crack", ["phá", "hại", "vỡ", "gián đoạn", "nứt", "hình "]],
    ["ripple", ["nước", "thủy", "sóng", "sông", "suối", "biển"]],
    ["wave", ["khổ", "buồn", "khóc", "lo ", "đau", "hận thù"]],
    ["flicker", ["lửa", "hỏa", "giận", "nóng"]],
    ["grow", ["mộc", "cây", "sinh ra", "lớn lên", "nảy mầm", "bắt đầu"]],
  ];
  function fxFor(text) {
    const t = " " + text.toLowerCase() + " ";
    for (const [fx, keys] of FX_LEXICON) if (keys.some((k) => t.includes(k))) return fx;
    return "slam";
  }
  const glyphs = (s) => Array.from((s || "").normalize("NFC"));

  visuals.word = {
    build(inner, ln) {
      const v = ln.visual;
      const hot = (ln.words || []).filter((w) => w.hot).map((w) => clean(w.w).replace(/[.,:;!?]+$/, "")).join(" ");
      const text = (v.text || hot || clean((ln.key_parts || []).map((p) => p.t).join(" "))).toUpperCase();
      const fx = v.fx || fxFor(text);
      ln._fx = fx;
      const st = el("div", "lf-stage lf-word-stage lf-fx-" + fx); inner.appendChild(st);
      if (fx === "rays") {
        const s = sv("svg", { class: "lf-rays", viewBox: "-500 -500 1000 1000" }, st);
        for (let k = 0; k < 24; k++) {
          const a = (k / 24) * Math.PI * 2, w = k % 2 ? 0.035 : 0.06;
          sv("path", { d: `M0,0 L${Math.cos(a - w) * 520},${Math.sin(a - w) * 520} L${Math.cos(a + w) * 520},${Math.sin(a + w) * 520} Z` }, s);
        }
      }
      if (fx === "ripple") {
        const s = sv("svg", { width: 0, height: 0, style: "position:absolute" }, st);
        const f = sv("filter", { id: "lfRipple" + ln.sentence_id, x: "-20%", y: "-40%", width: "140%", height: "180%" }, s);
        sv("feTurbulence", { type: "fractalNoise", baseFrequency: "0.012 0.06", numOctaves: "2", seed: "3", result: "n" }, f);
        sv("feDisplacementMap", { in: "SourceGraphic", in2: "n", scale: "0", xChannelSelector: "R", yChannelSelector: "G" }, f);
      }
      const box = el("div", "lf-bigword");
      if (fx === "split" || fx === "crack") {  // hai bản chồng khít, mỗi bản giữ một nửa
        box.appendChild(el("div", "half top", text)); box.appendChild(el("div", "half bot", text));
        if (fx === "crack") {
          const s = sv("svg", { class: "lf-crack", viewBox: "0 0 100 40", preserveAspectRatio: "none" }, box);
          const j = jitter(ln.sentence_id); let d = "M0,20";
          for (let x = 8; x <= 100; x += 8) d += ` L${x},${(20 + j() * 14).toFixed(1)}`;
          sv("path", { d, "vector-effect": "non-scaling-stroke" }, s);
        }
      } else {
        // Ký tự gom theo TỪ (không ngắt giữa từ): mỗi ký tự là một inline-block
        // nên trình duyệt được phép xuống dòng giữa hai ký tự bất kỳ -- ra
        // "NƯỚC CHỈ ĐANG BỊ KHU / ẤY" (L_bud_04 bản đầu).
        text.split(/\s+/).forEach((word, wi) => {
          if (wi) box.appendChild(document.createTextNode(" "));
          const wd = el("span", "wd");
          glyphs(word).forEach((g) => wd.appendChild(el("span", "ch", g)));
          box.appendChild(wd);
        });
      }
      if (fx === "ripple") box.style.filter = `url(#lfRipple${ln.sentence_id})`;
      st.appendChild(box);
      if (text.length > 14) box.classList.add("long");
      if (text.length > 22) box.classList.add("xlong");
      inner._lf = { st, box, text, fx };
    },
    enter(tl, inner, ln) {
      const S = inner._lf, fx = S.fx, t0 = ln.start + .1, span = Math.max(1.5, ln.end - ln.start);
      const chs = S.box.querySelectorAll(".ch");
      const r = HF.rng(HF.hashSeed("fx" + ln.sentence_id));
      if (fx === "split" || fx === "crack") {
        const top = S.box.querySelector(".top"), bot = S.box.querySelector(".bot");
        tl.fromTo(S.box, { opacity: 0, scale: 1.25 }, { opacity: 1, scale: 1, duration: .45, ease: "power4.out" }, t0);
        if (fx === "split") {
          tl.to(top, { y: -46, x: -18, duration: .7, ease: "expo.out" }, t0 + .6);
          tl.to(bot, { y: 46, x: 18, duration: .7, ease: "expo.out" }, t0 + .6);
        } else {
          const p = S.box.querySelector(".lf-crack path");
          tl.fromTo(S.box.querySelector(".lf-crack"), { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: .35, ease: twos(.35) }, t0 + .5);
          tl.to(top, { y: -8, x: -10, rotation: -1.5, duration: .18, ease: "power4.out" }, t0 + .85);
          tl.to(bot, { y: 10, x: 12, rotation: 1.2, duration: .18, ease: "power4.out" }, t0 + .85);
          tl.fromTo(S.st, { x: 0 }, { x: 8, duration: .04, yoyo: true, repeat: 5, ease: "none" }, t0 + .85);
        }
      } else if (fx === "dissolve") {  // hiện rồi tan: từng chữ bay lên, nhoè, mờ
        tl.fromTo(chs, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: .5, stagger: .04, ease: "power3.out" }, t0);
        const at = t0 + Math.min(span * .55, 2.2);
        chs.forEach((c) => tl.to(c, { y: -(60 + r() * 140), x: (r() - .5) * 120, rotation: (r() - .5) * 60, opacity: 0,
          filter: "blur(6px)", duration: 1.4 + r() * .6, ease: "power2.in" }, at + r() * .5));
      } else if (fx === "rays") {
        tl.fromTo(chs, { opacity: 0, filter: "blur(10px)" }, { opacity: 1, filter: "blur(0px)", duration: .6, stagger: .03 }, t0);
        const rays = S.st.querySelector(".lf-rays");
        tl.fromTo(rays, { opacity: 0, scale: .6, rotation: 0 }, { opacity: 1, scale: 1, duration: 1.2, ease: "power2.out" }, t0 + .3);
        tl.to(rays, { rotation: 25, duration: span + .5, ease: "none" }, t0 + .3);
        tl.fromTo(S.box, { textShadow: "0 0 0px rgba(255,220,140,0)" }, { textShadow: "0 0 60px rgba(255,220,140,.9)", duration: 1 }, t0 + .4);
      } else if (fx === "ripple") {
        const dm = S.st.querySelector("feDisplacementMap"), tb = S.st.querySelector("feTurbulence");
        tl.fromTo(chs, { opacity: 0 }, { opacity: 1, duration: .5, stagger: .03 }, t0);
        tl.fromTo(dm, { attr: { scale: 60 } }, { attr: { scale: 6 }, duration: 1.4, ease: "power2.out" }, t0);
        tl.fromTo(tb, { attr: { baseFrequency: "0.012 0.06" } }, { attr: { baseFrequency: "0.02 0.09" }, duration: span, ease: "sine.inOut" }, t0);
      } else if (fx === "wave") {
        tl.fromTo(chs, { opacity: 0 }, { opacity: 1, duration: .4, stagger: .03 }, t0);
        chs.forEach((c, k) => tl.fromTo(c, { y: 0 }, { y: 16, duration: .5, ease: "sine.inOut", yoyo: true,
          repeat: Math.max(1, Math.floor(span / .5)), delay: 0 }, t0 + .3 + k * .06));
      } else if (fx === "flicker") {  // lửa: sáng tối chập chờn theo chuỗi tất định
        tl.fromTo(chs, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .35, stagger: .03 }, t0);
        let t = t0 + .5;
        while (t < t0 + span) { const d = .06 + r() * .12;
          tl.to(S.box, { opacity: .55 + r() * .45, textShadow: `0 0 ${20 + r() * 50}px rgba(255,120,40,.9)`, duration: d, ease: "none" }, t); t += d; }
      } else if (fx === "grow") {  // chữ nhú lên từ mặt đất
        tl.fromTo(chs, { scaleY: 0, transformOrigin: "50% 100%", opacity: 0 }, { scaleY: 1, opacity: 1, duration: .6, stagger: .07, ease: "back.out(2)" }, t0);
      } else {
        tl.fromTo(chs, { opacity: 0, scale: 1.8, filter: "blur(8px)" }, { opacity: 1, scale: 1, filter: "blur(0px)", duration: .32, stagger: .05, ease: "power4.out" }, t0);
      }
    },
  };

  // ---- C3: minh hoạ SVG tự vẽ nét ----
  const ILLUS = {
    // Con đường một điểm tụ, máy quay dolly tiến về chân trời.
    road(s) {
      const g = sv("g", {}, s), hz = 380;
      sv("path", { d: `M0,${hz} L1920,${hz}`, class: "il-line thin" }, g);
      [[-900, 0], [900, 0], [-420, 0], [420, 0]].forEach(([x]) => sv("path", { d: `M${960 + x * 1.6},1080 L960,${hz}`, class: "il-line" + (Math.abs(x) < 500 ? " thin" : "") }, g));
      const dash = sv("path", { d: `M960,1080 L960,${hz}`, class: "il-dash" }, g);
      [[300, 250, 120], [1560, 240, 140], [620, 300, 70], [1320, 305, 60]].forEach(([x, w, h]) =>
        sv("path", { d: `M${x - w / 2},${hz} L${x},${hz - h} L${x + w / 2},${hz}`, class: "il-line thin" }, g));
      const sun = sv("circle", { cx: 960, cy: hz - 10, r: 70, class: "il-sun" }, g);
      return { g, dash, sun, cam: g };
    },
    // Núi nhiều lớp, mặt trời lên kèm tia sáng.
    sunrise(s) {
      const g = sv("g", {}, s);
      const sun = sv("circle", { cx: 960, cy: 700, r: 110, class: "il-sun" }, g);
      const rays = sv("g", { class: "il-rays" }, g);
      for (let k = 0; k < 16; k++) { const a = Math.PI + (k / 15) * Math.PI;
        sv("path", { d: `M${960 + Math.cos(a) * 150},${700 + Math.sin(a) * 150} L${960 + Math.cos(a) * 260},${700 + Math.sin(a) * 260}`, class: "il-line thin" }, rays); }
      const far = sv("path", { d: "M0,760 L240,600 L420,690 L640,540 L900,720 L1150,560 L1380,700 L1600,590 L1920,720 L1920,1080 L0,1080 Z", class: "il-fill far" }, g);
      const near = sv("path", { d: "M0,860 L300,740 L560,830 L820,700 L1100,860 L1400,730 L1700,850 L1920,780 L1920,1080 L0,1080 Z", class: "il-fill near" }, g);
      return { g, sun, rays, far, near, cam: g };
    },
    // Hoa sen nở trên mặt nước, gợn sóng lan ra.
    lotus(s) {
      const g = sv("g", { transform: "translate(960,620)" }, s);
      const ripples = [1, 2, 3].map((k) => sv("ellipse", { cx: 0, cy: 150, rx: 120 * k, ry: 26 * k, class: "il-line thin" }, g));
      const petals = [];
      [[-70, 1.0], [-35, 1.08], [0, 1.15], [35, 1.08], [70, 1.0], [-110, .85], [110, .85]].forEach(([a, k]) => {
        const p = sv("path", { d: `M0,120 C${-60 * k},40 ${-40 * k},${-120 * k} 0,${-190 * k} C${40 * k},${-120 * k} ${60 * k},40 0,120 Z`,
          class: "il-line petal", transform: `rotate(${a} 0 120)` }, g);
        petals.push(p);
      });
      return { g, petals, ripples, cam: g };
    },
    // Trăng khuyết, mây trôi, sao nhấp nháy.
    moon(s) {
      const g = sv("g", {}, s);
      const moon = sv("path", { d: "M1040,260 A150,150 0 1 0 1040,560 A118,118 0 1 1 1040,260 Z", class: "il-line il-moon" }, g);
      const clouds = [[520, 520, 1], [1320, 640, 1.3], [880, 780, .9]].map(([x, y, k]) =>
        sv("path", { d: `M${x - 180 * k},${y} q${40 * k},-60 ${100 * k},-30 q${40 * k},-70 ${120 * k},-20 q${60 * k},-30 ${90 * k},20 q${50 * k},10 ${50 * k},30 Z`, class: "il-line thin" }, g));
      const r = HF.rng(HF.hashSeed("stars"));
      const stars = Array.from({ length: 26 }, () => sv("circle", { cx: r() * 1920, cy: r() * 520, r: 1.5 + r() * 2.5, class: "il-star" }, g));
      return { g, moon, clouds, stars, cam: g };
    },
    // Ngôi nhà nét vẽ, cửa chính, la bàn hướng (phong thuỷ nhà ở).
    house(s) {
      const g = sv("g", { transform: "translate(960,560)" }, s);
      const parts = [
        "M-300,120 L-300,-60 L0,-260 L300,-60 L300,120 Z", "M-360,-40 L0,-300 L360,-40",
        "M-60,120 L-60,-20 L60,-20 L60,120", "M-230,0 L-130,0 L-130,70 L-230,70 Z", "M130,0 L230,0 L230,70 L130,70 Z",
        "M-420,120 L420,120"].map((d) => sv("path", { d, class: "il-line" }, g));
      const comp = sv("g", { transform: "translate(470,-190)" }, g);
      sv("circle", { r: 90, class: "il-line thin" }, comp);
      const needle = sv("path", { d: "M0,-78 L14,0 L0,78 L-14,0 Z", class: "il-fill needle" }, comp);
      [["B", 0, -112], ["N", 0, 128], ["Đ", 118, 10], ["T", -118, 10]].forEach(([t, x, y]) => {
        const e = sv("text", { x, y, class: "il-label" }, comp); e.textContent = t; });
      return { g, parts, comp, needle, cam: g };
    },
  };
  visuals.illus = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-illus"); inner.appendChild(st);
      const s = sv("svg", { viewBox: "0 0 1920 1080", class: "lf-illus-svg", preserveAspectRatio: PORTRAIT ? "xMidYMid slice" : "xMidYMid meet" }, st);
      const make = ILLUS[v.scene] || ILLUS.sunrise;
      inner._lf = { st, s, scene: v.scene in ILLUS ? v.scene : "sunrise", P: make(s), title: title(st, v.title, 150, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, P = S.P, t0 = ln.start, span = Math.max(2, ctx.until - t0);
      const draw = (els, at, dur, each) => [].concat(els).forEach((p, k) => drawOn(tl, p, at + k * (each || 0), dur, "power2.inOut"));
      if (S.title) tl.fromTo(S.title, { opacity: 0 }, { opacity: 1, duration: .5 }, t0 + .2);
      if (S.scene === "road") {
        draw(Array.from(P.g.querySelectorAll(".il-line")), t0, 1.2, .08);
        tl.fromTo(P.sun, { attr: { cy: 470 }, opacity: 0 }, { attr: { cy: 300 }, opacity: 1, duration: span, ease: "sine.out" }, t0 + .6);
        tl.fromTo(P.dash, { strokeDashoffset: 0 }, { strokeDashoffset: -600, duration: span, ease: "none" }, t0);
        tl.fromTo(P.cam, { scale: 1, svgOrigin: "960 380" }, { scale: 1.35, duration: span, ease: "power1.in" }, t0 + .8);  // dolly
      } else if (S.scene === "sunrise") {
        tl.fromTo(P.far, { y: 60, opacity: 0 }, { y: 0, opacity: 1, duration: 1.2, ease: "power3.out" }, t0);
        tl.fromTo(P.near, { y: 120, opacity: 0 }, { y: 0, opacity: 1, duration: 1.2, ease: "power3.out" }, t0 + .2);
        tl.fromTo(P.sun, { attr: { cy: 900 } }, { attr: { cy: 560 }, duration: span, ease: "sine.out" }, t0 + .3);
        tl.fromTo(P.rays, { opacity: 0, y: 340 }, { opacity: 1, y: 0, duration: span, ease: "sine.out" }, t0 + .3);
        draw(Array.from(P.rays.children), t0 + 1.2, .6, .05);
        tl.fromTo(P.near, { x: 0 }, { x: -40, duration: span, ease: "none", immediateRender: false }, t0 + 1.4);   // parallax
        tl.fromTo(P.far, { x: 0 }, { x: -14, duration: span, ease: "none", immediateRender: false }, t0 + 1.4);
      } else if (S.scene === "lotus") {
        draw(P.ripples, t0, 1.0, .2);
        P.petals.forEach((p, k) => { drawOn(tl, p, t0 + .5 + k * .12, .9, "power2.inOut");
          tl.fromTo(p, { scale: .2, svgOrigin: "0 120" }, { scale: 1, duration: 1.1, ease: "back.out(1.6)" }, t0 + .5 + k * .12); });
        P.ripples.forEach((rp, k) => tl.to(rp, { scale: 1.12, opacity: .3, svgOrigin: "0 150", duration: 2, yoyo: true, repeat: Math.ceil(span / 4), ease: "sine.inOut" }, t0 + 1 + k * .5));
      } else if (S.scene === "moon") {
        drawOn(tl, P.moon, t0, 1.4, "power2.inOut");
        tl.fromTo(P.moon, { fillOpacity: 0 }, { fillOpacity: 1, duration: 1 }, t0 + 1.2);
        P.clouds.forEach((c, k) => { drawOn(tl, c, t0 + .4 + k * .2, 1.0);
          tl.to(c, { x: (k % 2 ? -1 : 1) * 90, duration: span, ease: "none" }, t0 + .4); });
        P.stars.forEach((st, k) => tl.fromTo(st, { opacity: 0 }, { opacity: 1, duration: .6, yoyo: true, repeat: Math.ceil(span / 1.2), ease: "sine.inOut" }, t0 + .2 + (k % 7) * .17));
      } else if (S.scene === "house") {
        draw(P.parts, t0, .9, .18);
        tl.fromTo(P.comp, { opacity: 0, scale: .6, svgOrigin: "0 0" }, { opacity: 1, scale: 1, duration: .6, ease: "back.out(2)" }, t0 + 1.2);
        tl.fromTo(P.needle, { rotation: -140, svgOrigin: "0 0" }, { rotation: 0, duration: 1.6, ease: "elastic.out(1, .5)" }, t0 + 1.4);
      }
      tl.fromTo(S.st, { scale: 1 }, { scale: 1.04, duration: span, ease: "none" }, t0);
    },
  };

  // ---- C4: thẻ kết nền shader WebGL (mây/mực chuyển động) ----
  // Thời gian shader lấy từ timeline (tween tiến trình), vẽ lại trong onUpdate:
  // seek tới đâu vẽ đúng khung đó. Không có WebGL -> nền gradient tĩnh.
  visuals.endcard = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-end"); inner.appendChild(st);
      const cv = el("canvas", "lf-end-gl"); cv.width = 960; cv.height = 540; st.appendChild(cv);
      const night = theme() === "night";
      const gl = cv.getContext("webgl", { preserveDrawingBuffer: true, antialias: false });
      let draw = null;
      if (gl) {
        const vs = "attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}";
        const fs = `precision mediump float;uniform float t;uniform vec2 r;
          float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
          float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
            return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}
          float fbm(vec2 p){float v=0.,a=.5;for(int k=0;k<5;k++){v+=a*n(p);p*=2.03;a*=.5;}return v;}
          void main(){vec2 uv=gl_FragCoord.xy/r;vec2 q=uv*vec2(3.2,1.8);
            float c=fbm(q+vec2(t*.06,t*.02)+fbm(q*1.6-vec2(t*.04,0.)));
            vec3 a=${night ? "vec3(.03,.05,.14)" : "vec3(.94,.91,.84)"}, b=${night ? "vec3(.55,.42,.16)" : "vec3(.62,.30,.20)"};
            gl_FragColor=vec4(mix(a,b,smoothstep(.45,.95,c)*${night ? ".85" : ".55"}),1.);}`;
        const sh = (type, src) => { const s2 = gl.createShader(type); gl.shaderSource(s2, src); gl.compileShader(s2); return s2; };
        const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, fs));
        gl.linkProgram(pr);
        if (gl.getProgramParameter(pr, gl.LINK_STATUS)) {
          gl.useProgram(pr);
          const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b);
          gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
          const loc = gl.getAttribLocation(pr, "p"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
          const ut = gl.getUniformLocation(pr, "t"); gl.uniform2f(gl.getUniformLocation(pr, "r"), cv.width, cv.height);
          draw = (tt) => { gl.uniform1f(ut, tt); gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4); };
          draw(0);
        }
      }
      if (!draw) cv.classList.add("nogl");
      const box = el("div", "lf-end-box");
      box.appendChild(el("div", "lf-end-main", v.text || "Đăng ký kênh"));
      if (v.sub) box.appendChild(el("div", "lf-end-sub", v.sub));
      st.appendChild(box);
      inner._lf = { st, cv, draw, box };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, t0 = ln.start, span = Math.max(2, ctx.until - t0);
      tl.fromTo(S.cv, { opacity: 0 }, { opacity: 1, duration: 1.0 }, t0);
      if (S.draw) { const clock = { t: 0 }; tl.to(clock, { t: span * 1.0 + 1, duration: span + 1, ease: "none", onUpdate: () => S.draw(clock.t) }, t0); }
      tl.fromTo(S.box.children, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: .7, stagger: .25, ease: "expo.out" }, t0 + .4);
      sheen(tl, S.box, t0 + 1.1);
    },
  };

  /* ================= PHASE D: mượn từ hồ sơ S-tier (Youtube_Creator_V2) =================
     Ảnh tư liệu Commons + máy quay lia (doc), ảnh có vòng khoanh đỏ vẽ tay (photo),
     đồng hồ 12 canh giờ (clock), câu hỏi trong lặng (ask). Âm thanh của các cảnh
     này do hf_sfx.py đặt theo cùng mốc (when). */
  const FRAME = () => (PORTRAIT ? { W: 1080, H: 1920 } : { W: 1920, H: 1080 });

  // doc: moves [{at, word, x, y, z, d}] -- x,y = điểm ảnh (0..1) đặt vào tâm khung, z = độ phóng.
  visuals.doc = {
    build(inner, ln) {
      const v = ln.visual, F = FRAME(), st = el("div", "lf-stage lf-doc"); inner.appendChild(st);
      const img = el("div", "lf-doc-img " + (v.tone || "sepia")); st.appendChild(img);
      const k = Math.max(F.W / v.w, F.H / v.h), w = v.w * k, h = v.h * k;
      Object.assign(img.style, { width: w + "px", height: h + "px", backgroundImage: `url(${v.src})` });
      st.appendChild(el("div", "lf-doc-veil"));
      const tag = v.tag ? el("div", "lf-doc-tag", v.tag) : null;
      if (tag) st.appendChild(tag);
      inner._lf = { img, w, h, F, tag };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, v = ln.visual, moves = v.moves && v.moves.length ? v.moves : [{ x: .5, y: .5, z: 1 }];
      const pos = (m) => {
        const z = Math.max(1, m.z || 1);
        let x = S.F.W / 2 - (m.x == null ? .5 : m.x) * S.w * z, y = S.F.H / 2 - (m.y == null ? .5 : m.y) * S.h * z;
        x = Math.min(0, Math.max(S.F.W - S.w * z, x)); y = Math.min(0, Math.max(S.F.H - S.h * z, y));
        return { x, y, scale: z };
      };
      tl.set(S.img, { transformOrigin: "0 0", ...pos(moves[0]) }, 0);
      tl.fromTo(S.img, { opacity: 0 }, { opacity: 1, duration: .35 }, ln.start);
      let prev = ln.start;
      moves.slice(1).forEach((m) => {
        const t = when(ctx, m, prev + 1.2), d = m.d || 1.6;
        tl.to(S.img, { ...pos(m), duration: d, ease: "power2.inOut" }, t - .2);
        prev = t;
      });
      if (S.tag) tl.fromTo(S.tag, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .5, ease: "power3.out" },
        when(ctx, v.tag_at || {}, ln.start + .6));
      // Kết vòng lặp (V.loop): cảnh đầu quay lại khung mở màn ở những khung cuối.
      const DUR = Number(ctx.V && ctx.V.duration) || 0;
      if (ctx.V && ctx.V.loop && ln.sentence_id === 1 && DUR)
        tl.to(S.img, { ...pos(moves[0]), duration: .4, ease: "power2.out" }, DUR - .45);
    },
  };

  // photo: ảnh in viền trắng hơi nghiêng + vòng khoanh đỏ vẽ tay. circles [{x,y,r,at,word}] theo tỉ lệ ảnh.
  visuals.photo = {
    build(inner, ln) {
      const v = ln.visual, F = FRAME(), st = el("div", "lf-stage lf-photo"); inner.appendChild(st);
      const maxW = F.W - 160, maxH = PORTRAIT ? 1000 : 820;
      const k = Math.min(maxW / v.w, maxH / v.h), w = Math.round(v.w * k), h = Math.round(v.h * k);
      const card = el("div", "lf-photo-card"); st.appendChild(card);
      Object.assign(card.style, { width: w + "px", height: h + "px", marginLeft: (-w / 2) + "px",
        top: (PORTRAIT ? 330 + (1000 - h) / 2 : 90) + "px" });
      const img = el("div", "lf-photo-img " + (v.tone || "color")); card.appendChild(img);
      img.style.backgroundImage = `url(${v.src})`;
      const marks = (v.circles || []).map((c, n) => {
        const box = el("div", "lf-photo-mark"); card.appendChild(box);
        const r = (c.r || .12) * Math.min(w, h);
        Object.assign(box.style, { left: (c.x * w - r) + "px", top: (c.y * h - r) + "px", width: 2 * r + "px", height: 2 * r + "px" });
        const p = sketchOn(box, "loop", sketchLoop(50, 50, 46, 46, (ln.sentence_id * 7 + n)));
        return { p, c, box };
      });
      const lab = v.label ? el("div", "lf-photo-label", v.label) : null;
      if (lab) { st.appendChild(lab); lab.style.top = (PORTRAIT ? 330 + (1000 + h) / 2 + 40 : 950) + "px"; }
      inner._lf = { card, marks, lab, n: ln.sentence_id };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, rot = S.n % 2 ? -2.2 : 2.0;
      tl.fromTo(S.card, { y: -180, rotation: rot * 3, opacity: 0 }, { y: 0, rotation: rot, opacity: 1, duration: .55, ease: twos(.55) }, ln.start);
      tl.to(S.card, { scale: 1.04, duration: Math.max(1, ctx.until - ln.start), ease: "none" }, ln.start + .5);
      S.marks.forEach((m) => drawSketch(tl, m.p, when(ctx, m.c, ln.start + .8), .45));
      if (S.lab) tl.fromTo(S.lab, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: .45 },
        S.marks.length ? when(ctx, S.marks[0].c, ln.start + .8) + .3 : ln.start + .6);
    },
  };

  // clock: 12 canh giờ trên mặt 24 giờ. steps [{at, word, chi}] -> tô cung giờ + kim chỉ + thẻ.
  const CANH = { "Tý": "23:00 – 01:00", "Sửu": "01:00 – 03:00", "Dần": "03:00 – 05:00", "Mão": "05:00 – 07:00",
    "Thìn": "07:00 – 09:00", "Tỵ": "09:00 – 11:00", "Ngọ": "11:00 – 13:00", "Mùi": "13:00 – 15:00",
    "Thân": "15:00 – 17:00", "Dậu": "17:00 – 19:00", "Tuất": "19:00 – 21:00", "Hợi": "21:00 – 23:00" };
  visuals.clock = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-clock"); inner.appendChild(st);
      const wrap = el("div", "lf-clock-wrap"); st.appendChild(wrap);
      const svg = sv("svg", { viewBox: "-500 -500 1000 1000" }, wrap);
      const ring = sv("circle", { r: 470, class: "ring" }, svg);
      const arc = (a0, a1, r0, r1) => {
        const P = (a, r) => [Math.cos(a) * r, Math.sin(a) * r].map((x) => x.toFixed(1)).join(",");
        return `M${P(a0, r1)} A${r1},${r1} 0 0 1 ${P(a1, r1)} L${P(a1, r0)} A${r0},${r0} 0 0 0 ${P(a0, r0)} Z`;
      };
      const sectors = {}, labels = [];
      CHI.forEach((c, k) => {   // Tý ở đỉnh (0 giờ), mỗi chi một cung 30°
        const mid = (k * 30 - 90) * Math.PI / 180, a0 = mid - Math.PI / 12, a1 = mid + Math.PI / 12;
        sectors[c] = sv("path", { d: arc(a0 + .01, a1 - .01, 250, 440), class: "sec" }, svg);
        const t = sv("text", { x: (Math.cos(mid) * 345).toFixed(1), y: (Math.sin(mid) * 345).toFixed(1), class: "chi" }, svg);
        t.textContent = c; labels.push(t);
      });
      const ticks = sv("g", {}, svg);
      for (let h = 0; h < 24; h++) {
        const a = (h * 15 - 90) * Math.PI / 180, r2 = h % 2 ? 458 : 450;
        sv("line", { x1: Math.cos(a) * 470, y1: Math.sin(a) * 470, x2: Math.cos(a) * r2, y2: Math.sin(a) * r2, class: "tk" }, ticks);
        if (h % 6 === 0) { const n = sv("text", { x: Math.cos(a) * 205, y: Math.sin(a) * 205, class: "hr" }, svg); n.textContent = String(h); }
      }
      const hand = sv("g", { class: "hand" }, svg);
      sv("line", { x1: 0, y1: 30, x2: 0, y2: -230, class: "hand-l" }, hand);
      sv("circle", { r: 16, class: "hub" }, svg);
      const chips = (v.steps || []).map((s) => {
        const c = el("div", "lf-clock-chip"); st.appendChild(c);
        c.innerHTML = `<b>GIỜ ${esc(String(s.chi || "").toUpperCase())}</b><span>${CANH[s.chi] || ""}</span>`;
        return c;
      });
      const tt = title(st, v.title, 60, 330);
      inner._lf = { wrap, ring, sectors, labels, ticks, hand, chips, tt };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, v = ln.visual, t0 = ln.start;
      if (S.tt) tl.fromTo(S.tt, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .5 }, t0 + .1);
      drawOn(tl, S.ring, t0, 1.0, "power2.inOut");
      tl.fromTo(Object.values(S.sectors), { opacity: 0, scale: .6, svgOrigin: "0 0" },
        { opacity: 1, scale: 1, duration: .5, ease: "back.out(1.6)", stagger: .06 }, t0 + .2);
      tl.fromTo(S.labels, { opacity: 0 }, { opacity: 1, duration: .3, stagger: .06 }, t0 + .45);
      tl.fromTo(S.ticks, { opacity: 0 }, { opacity: 1, duration: .6 }, t0 + .3);
      tl.set(S.hand, { rotation: 0, svgOrigin: "0 0" }, 0);
      let prev = null;
      (v.steps || []).forEach((st, k) => {
        const t = when(ctx, st, t0 + 1.2 + k * 1.2), sec = S.sectors[st.chi];
        if (!sec) return;
        const deg = CHI.indexOf(st.chi) * 30;
        tl.to(S.hand, { rotation: deg, svgOrigin: "0 0", duration: .7, ease: "back.out(1.4)" }, t - .15);
        if (prev) tl.to(prev, { fill: "var(--lf-clock-sec)", duration: .3 }, t);
        tl.to(sec, { fill: css("--accent"), duration: .35 }, t);
        tl.fromTo(sec, { scale: 1, svgOrigin: "0 0" }, { scale: 1.06, svgOrigin: "0 0", duration: .3, yoyo: true, repeat: 1 }, t);
        if (k) tl.to(S.chips[k - 1], { opacity: 0, duration: .2 }, t);
        tl.fromTo(S.chips[k], { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: .4, ease: "power3.out" }, t + .05);
        prev = sec;
      });
      tl.to(S.wrap, { rotation: 0, scale: 1.03, duration: Math.max(1, ctx.until - t0), ease: "none" }, t0);
    },
  };

  // ask: câu hỏi trong LẶNG -- chữ lớn, không phụ đề, không tiếng (hf_sfx + mux tắt nhạc nền).
  visuals.ask = {
    build(inner, ln) {
      const st = el("div", "lf-stage lf-ask"); inner.appendChild(st);
      const text = (ln.visual.text || clean((ln.words || []).map((w) => w.w).join(" ")));
      const q = el("div", "lf-ask-q"); st.appendChild(q);
      const words = text.split(/\s+/).map((w) => { const s = el("span", "aw", w); q.appendChild(s); q.appendChild(document.createTextNode(" ")); return s; });
      inner._lf = { words };
    },
    enter(tl, inner, ln) {
      const S = inner._lf, words = ln.words || [];
      // Cả câu hỏi hiện NGAY đầu cảnh (người xem đọc trong lặng); chữ đang được đọc sáng lên.
      S.words.forEach((s, k) => {
        tl.fromTo(s, { opacity: 0, y: 26, filter: "blur(6px)" }, { opacity: .55, y: 0, filter: "blur(0px)", duration: .45, ease: "power3.out" }, ln.start + .05 + k * .06);
        if (words[k]) tl.to(s, { opacity: 1, duration: .2 }, words[k].t - .03);
      });
    },
  };

  /* ================= E: cảnh VẼ thay tư liệu (video dài 30+ phút) =================
     Khi không có ảnh thật đúng nghĩa: rối bóng (shadow), gieo quẻ (hexagram),
     ô Lạc Thư (luoshu), dấu chân trên bản đồ. Mọi cảnh dựng lại gắn nhãn MINH HOẠ. */
  const NIGHT = () => theme() !== "paper";
  function shadowDefs(svg, id) {
    const defs = sv("defs", {}, svg);
    const g = sv("radialGradient", { id: "shg" + id, cx: "50%", cy: "42%", r: "75%" }, defs);
    const stops = NIGHT()
      ? [["0%", "#f2c274", .95], ["38%", "#b8742e", .85], ["72%", "#3a220f", 1], ["100%", "#0b0a12", 1]]
      : [["0%", "#fbf1d8", 1], ["45%", "#f1e0b8", 1], ["80%", "#dcc596", 1], ["100%", "#c9ad7a", 1]];
    stops.forEach(([o, c, a]) => sv("stop", { offset: o, "stop-color": c, "stop-opacity": a }, g));
    const f = sv("filter", { id: "shb" + id, x: "-5%", y: "-5%", width: "110%", height: "110%" }, defs);
    sv("feGaussianBlur", { stdDeviation: 1.6 }, f);
    return { grad: `url(#shg${id})`, blur: `url(#shb${id})` };
  }
  const INK = () => (NIGHT() ? "#090705" : "#22180f");
  const SHADOW = {
    // Gốc bồ-đề đêm trăng: người ngồi thiền nhìn từ phía sau (không vẽ mặt -- như nghệ
    // thuật Phật giáo sơ kỳ Sanchi/Bharhut chỉ dùng biểu tượng).
    bodhi(g, P) {
      const ink = INK();
      P.moon = sv("circle", { cx: 1500, cy: 230, r: 74, fill: NIGHT() ? "#fff3d6" : "#fffaf0", opacity: .85 }, g);
      P.far = sv("path", { d: "M0,650 C220,560 380,610 560,580 C760,540 900,620 1100,590 C1320,555 1500,610 1700,575 C1800,560 1880,590 1920,600 L1920,1080 L0,1080 Z",
        fill: ink, opacity: .38 }, g);
      P.river = sv("g", {}, g);
      sv("rect", { x: 0, y: 700, width: 1920, height: 60, fill: ink, opacity: .55 }, P.river);
      P.shimmer = [0, 1, 2].map((k) => sv("path", { d: `M0,${712 + k * 16} L1920,${712 + k * 16}`, stroke: NIGHT() ? "#f6d7a0" : "#fff7e6",
        "stroke-width": 2.5, "stroke-dasharray": "60 140", opacity: .55, fill: "none" }, P.river));
      P.ground = sv("path", { d: "M0,760 C400,748 900,770 1300,756 C1600,746 1800,760 1920,756 L1920,800 L0,800 Z", fill: ink }, g);
      const tree = sv("g", {}, g); P.tree = tree;
      sv("path", { d: "M640,780 C650,700 630,620 600,560 C580,520 560,470 520,430 L540,420 C580,455 610,500 630,540 C640,470 655,420 700,370 L716,384 C680,430 668,490 672,560 C700,500 760,460 820,440 L826,458 C770,480 712,530 694,600 C690,660 700,720 712,780 Z", fill: ink }, tree);
      const r = HF.rng(HF.hashSeed("bodhi"));
      P.canopy = sv("g", {}, tree);
      for (let k = 0; k < 46; k++) {
        const a = r() * Math.PI * 2, d = Math.sqrt(r()) * 1;
        sv("circle", { cx: 640 + Math.cos(a) * 330 * d, cy: 330 + Math.sin(a) * 170 * d, r: 55 + r() * 60, fill: ink }, P.canopy);
      }
      P.leaves = [];
      for (let k = 0; k < 34; k++) {   // lá bồ-đề hình tim, đuôi nhọn, lắc nhẹ ở rìa tán
        const a = (k / 34) * Math.PI * 2, x = 640 + Math.cos(a) * 400, y = 330 + Math.sin(a) * 215;
        if (y > 470) continue;
        const lf = sv("path", { d: "M0,0 C-16,-10 -22,-30 -10,-40 C-4,-44 0,-40 0,-34 C0,-40 4,-44 10,-40 C22,-30 16,-10 0,0 L0,14 Z",
          fill: ink, transform: `translate(${x},${y}) rotate(${(a * 180) / Math.PI + 90}) scale(${1 + r() * .5})` }, P.canopy);
        P.leaves.push(lf);
      }
      P.figure = sv("path", { d: "M790,778 C790,742 812,712 838,702 C828,692 824,680 826,666 C828,646 842,634 858,634 C874,634 888,646 890,666 C892,680 888,692 878,702 C904,712 926,742 926,778 Z", fill: ink }, g);
      P.stars = Array.from({ length: 14 }, () => sv("circle", { cx: 900 + r() * 1000, cy: 60 + r() * 300, r: 1.6 + r() * 1.8, fill: "#fff6dc", opacity: 0 }, g));
    },
    // Đêm rời cung: sân trong (màn sáng) bên trái, cung điện mờ ở xa, tường thành + cổng
    // hai cánh ở tiền cảnh bên phải. Ngựa vẽ TRƯỚC tường -> đi qua cổng thì bị tường che,
    // chỉ lộ trong khung cổng (bóng đen trên bóng đen thì hoà làm một, không thấy ngựa).
    departure(g, P) {
      const ink = INK();
      P.moon = sv("circle", { cx: 980, cy: 200, r: 62, fill: NIGHT() ? "#fff3d6" : "#fffaf0", opacity: .85 }, g);
      const pal = sv("g", { opacity: .42 }, g); P.far = pal;
      sv("path", { d: "M40,790 L40,560 C40,470 90,440 130,400 C170,440 220,470 220,560 L220,790 Z M120,400 L130,360 L140,400 Z", fill: ink }, pal);
      sv("path", { d: "M240,790 L240,600 C240,540 280,520 310,500 C340,520 380,540 380,600 L380,790 Z", fill: ink }, pal);
      sv("path", { d: "M400,790 L400,620 L420,620 C450,580 560,580 590,620 L610,620 L610,790 Z", fill: ink }, pal);
      for (let k = 0; k < 3; k++) sv("rect", { x: 100 + k * 160, y: 660, width: 26, height: 50, rx: 13, fill: NIGHT() ? "#f2c274" : "#fff6dc", opacity: .8 }, pal);
      P.ground = sv("rect", { x: 0, y: 788, width: 1920, height: 30, fill: ink }, g);
      const hr = sv("g", { transform: "translate(200,790)" }, g); P.horse = hr;
      const body = sv("g", {}, hr); P.hbody = body;
      sv("path", { d: "M-150,-150 C-150,-185 -110,-200 -40,-198 C20,-196 70,-200 95,-215 C110,-250 120,-285 150,-300 L178,-292 L200,-270 L192,-258 L168,-262 C160,-240 150,-215 140,-195 C130,-170 120,-150 100,-140 C40,-128 -60,-128 -120,-135 Z", fill: ink }, body);
      sv("path", { d: "M-150,-170 C-185,-165 -205,-140 -215,-100 L-206,-98 C-195,-128 -178,-148 -150,-152 Z", fill: ink }, body);
      sv("path", { d: "M-20,-198 C-30,-235 -10,-265 10,-280 C14,-300 30,-312 40,-300 C48,-292 44,-280 36,-276 C46,-262 48,-238 36,-210 L60,-205 C66,-188 40,-190 20,-196 Z", fill: ink }, body);
      sv("path", { d: "M12,-292 L22,-322 L32,-292 Z", fill: ink }, body);
      P.legs = [[-120, 0], [-95, 1], [70, 1], [95, 0]].map(([x, ph]) => {
        const l = sv("path", { d: `M${x - 12},-142 L${x - 8},-70 L${x - 12},0 L${x + 8},0 L${x + 10},-70 L${x + 12},-142 Z`, fill: ink }, body);
        return { l, x, ph };
      });
      const wall = sv("g", {}, g); P.palace = wall;
      sv("path", { d: "M1300,790 L1300,440 L1340,440 L1340,410 L1380,410 L1380,440 L1680,440 L1680,410 L1720,410 L1720,440 L1780,440 L1780,410 L1820,410 L1820,440 L1920,440 L1920,790 L1640,790 L1640,560 C1640,520 1600,500 1530,500 C1460,500 1420,520 1420,560 L1420,790 Z", fill: ink }, wall);
      sv("path", { d: "M1380,446 L1380,410 C1380,330 1440,300 1530,260 C1620,300 1680,330 1680,410 L1680,446 Z", fill: ink }, wall);
      P.doorL = sv("rect", { x: 1420, y: 520, width: 110, height: 270, fill: ink }, g);
      P.doorR = sv("rect", { x: 1530, y: 520, width: 110, height: 270, fill: ink }, g);
    },
    // Rừng đêm (Trung Bộ 86): một người đi thong thả phía trước, một người chạy hết sức phía sau
    // mà không đuổi kịp. Không vẽ vũ khí, không vẽ mặt -- chỉ bóng dáng.
    forest(g, P) {
      const ink = INK(), r = HF.rng(HF.hashSeed("forest"));
      P.moon = sv("circle", { cx: 1450, cy: 190, r: 58, fill: NIGHT() ? "#fff3d6" : "#fffaf0", opacity: .8 }, g);
      P.far = sv("g", { opacity: .35 }, g);
      for (let k = 0; k < 16; k++) { const x = k * 130 + r() * 60, w = 18 + r() * 16;
        sv("path", { d: `M${x},790 L${x + 4},0 L${x + w},0 L${x + w - 4},790 Z`, fill: ink }, P.far); }
      sv("path", { d: "M0,0 L1920,0 L1920,90 C1600,150 1300,70 1000,130 C700,180 400,90 0,140 Z", fill: ink }, P.far);
      P.trees = sv("g", {}, g);
      [[60, 46], [420, 38], [880, 30], [1340, 42], [1760, 52]].forEach(([x, w]) => {
        sv("path", { d: `M${x},800 C${x + 6},500 ${x - 8},250 ${x + 4},-20 L${x + w},-20 C${x + w - 10},250 ${x + w + 6},520 ${x + w + 4},800 Z`, fill: ink }, P.trees);
        sv("path", { d: `M${x + w / 2},${300 + r() * 120} C${x + w + 60},${260 + r() * 60} ${x + w + 120},${240 + r() * 40} ${x + w + 170},${230 + r() * 40} L${x + w + 172},${244 + r() * 30} C${x + w + 110},${262} ${x + w + 50},${300} ${x + w / 2},${330 + r() * 100} Z`, fill: ink }, P.trees);
      });
      P.ground = sv("path", { d: "M0,790 C500,770 1100,800 1920,780 L1920,830 L0,830 Z", fill: ink }, g);
      const mk = sv("g", { transform: "translate(1060,790)" }, g); P.monk = sv("g", {}, mk);
      sv("circle", { cx: 0, cy: -178, r: 19, fill: ink }, P.monk);
      sv("path", { d: "M-24,-150 C-30,-120 -34,-60 -40,0 L34,0 C30,-60 26,-120 22,-150 C10,-160 -12,-160 -24,-150 Z", fill: ink }, P.monk);
      sv("path", { d: "M18,-140 C34,-110 40,-90 36,-70 L28,-68 C28,-90 22,-108 10,-130 Z", fill: ink }, P.monk);
      const ch = sv("g", { transform: "translate(380,790)" }, g); P.chaser = sv("g", {}, ch);
      sv("circle", { cx: 6, cy: -182, r: 18, fill: ink }, P.chaser);
      sv("path", { d: "M-16,-160 C-6,-166 20,-166 28,-156 L40,-90 L-6,-86 Z", fill: ink }, P.chaser);
      P.clegs = [[-4, 1], [24, -1]].map(([x, s]) => sv("path", { d: `M${x - 8},-90 L${x + 8},-90 L${x + 6},0 L${x - 6},0 Z`, fill: ink }, P.chaser));
      P.carms = [[0, 1], [26, -1]].map(([x]) => sv("path", { d: `M${x - 5},-152 L${x + 5},-152 L${x + 4},-100 L${x - 4},-100 Z`, fill: ink }, P.chaser));
    },
    // Ngọn đèn dầu (Trường Bộ 16: "hãy tự mình là ngọn đèn cho chính mình"): bấc bắt lửa, rồi
    // nhiều ngọn đèn nhỏ sáng dần ở xa.
    lamp(g, P) {
      const ink = INK();
      P.far = sv("rect", { x: 0, y: 862, width: 1920, height: 14, fill: ink, opacity: .9 }, g);   // mép bàn mỏng: vùng phụ đề bên dưới vẫn sáng
      P.lamp = sv("g", {}, sv("g", { transform: "translate(860,822)" }, g));   // nhóm trong để tween y không đè translate
      sv("path", { d: "M-170,-60 C-150,10 150,10 170,-60 C120,-40 -120,-40 -170,-60 Z", fill: ink }, P.lamp);
      sv("path", { d: "M150,-58 C190,-90 230,-92 250,-80 C220,-74 190,-66 168,-50 Z", fill: ink }, P.lamp);
      sv("path", { d: "M-40,-2 L40,-2 L60,40 L-60,40 Z", fill: ink }, P.lamp);
      P.wick = sv("path", { d: "M232,-82 L240,-104", stroke: ink, "stroke-width": 6, "stroke-linecap": "round" }, P.lamp);
      P.flame = sv("path", { d: "M240,-104 C214,-140 226,-190 240,-230 C254,-190 268,-140 240,-104 Z", fill: NIGHT() ? "#ffcf73" : "#e2661f", opacity: 0 }, P.lamp);
      P.core = sv("path", { d: "M240,-108 C230,-128 234,-152 240,-170 C246,-152 250,-128 240,-108 Z", fill: NIGHT() ? "#fff6dc" : "#ffc04d", opacity: 0 }, P.lamp);
      const r = HF.rng(HF.hashSeed("lamps"));
      P.small = Array.from({ length: 26 }, (_, k) => {
        const x = 80 + r() * 1760, y = 560 + r() * 160, s = .22 + r() * .26;
        const gg = sv("g", { transform: `translate(${x},${y}) scale(${s})`, opacity: 0 }, g);
        sv("path", { d: "M0,-104 C-26,-140 -14,-190 0,-230 C14,-190 26,-140 0,-104 Z", fill: NIGHT() ? "#ffcf73" : "#e2661f" }, gg);
        return gg;
      });
    },
    // Rùa thần nổi lên từ sông Lạc, trên mai có chín nhóm chấm (Lạc Thư).
    turtle(g, P) {
      const ink = INK();
      P.moon = sv("circle", { cx: 1560, cy: 200, r: 60, fill: NIGHT() ? "#fff3d6" : "#fffaf0", opacity: .7 }, g);
      P.far = sv("path", { d: "M0,600 C200,520 420,560 640,530 C860,500 1100,560 1320,520 C1560,480 1760,540 1920,520 L1920,1080 L0,1080 Z", fill: ink, opacity: .3 }, g);
      const t = sv("g", {}, sv("g", { transform: "translate(960,560)" }, g)); P.tt = t;
      sv("path", { d: "M-290,-30 C-360,-80 -400,-60 -410,-20 C-380,-10 -330,-6 -290,10 Z M290,-30 C360,-80 400,-60 410,-20 C380,-10 330,-6 290,10 Z M-250,90 C-320,130 -340,170 -320,190 C-290,170 -250,140 -220,110 Z M250,90 C320,130 340,170 320,190 C290,170 250,140 220,110 Z M-40,-170 C-50,-230 -20,-262 0,-262 C20,-262 50,-230 40,-170 Z", fill: ink }, t);
      sv("ellipse", { cx: 0, cy: 0, rx: 300, ry: 185, fill: ink }, t);
      const ring = NIGHT() ? "#f2c274" : "#f6e3b8";
      sv("ellipse", { cx: 0, cy: 0, rx: 262, ry: 154, fill: "none", stroke: ring, "stroke-width": 2, opacity: .35 }, t);
      const LS = [[4, 9, 2], [3, 5, 7], [8, 1, 6]];
      P.dots = [];
      LS.forEach((row, ry) => row.forEach((n, rx) => {
        const cx = (rx - 1) * 150, cy = (ry - 1) * 92;
        for (let k = 0; k < n; k++) {
          const a = (k / n) * Math.PI * 2 - Math.PI / 2, rr = n === 1 ? 0 : 12 + n * 2.2;
          const d = sv("circle", { cx: cx + Math.cos(a) * rr, cy: cy + Math.sin(a) * rr * .8, r: 7,
            fill: n % 2 ? "#fff3d6" : "none", stroke: "#fff3d6", "stroke-width": 2.4, opacity: 0 }, t);
          P.dots.push({ d, n, cell: ry * 3 + rx });
        }
      }));
      P.waves = [0, 1, 2, 3].map((k) => sv("path", {
        d: Array.from({ length: 26 }, (_, i) => `${i ? "L" : "M"}${i * 90 - 120},${720 + k * 34 + (i % 2 ? -12 : 12)}`).join(" ") + ` L2300,1080 L-120,1080 Z`,
        fill: ink, opacity: .55 + k * .12 }, g));
    },
  };
  visuals.shadow = {
    build(inner, ln, i) {
      const v = ln.visual, st = el("div", "lf-stage lf-shadow"); inner.appendChild(st);
      const svg = sv("svg", { viewBox: "0 0 1920 1080", class: "lf-shadow-svg", preserveAspectRatio: "xMidYMid slice" }, st);
      const D = shadowDefs(svg, ln.sentence_id);
      const screen = sv("rect", { x: -40, y: -40, width: 2000, height: 1160, fill: D.grad }, svg);
      const g = sv("g", { filter: D.blur, transform: v.scene === "bodhi" || !(v.scene in SHADOW) ? "translate(0,55)" : "" }, svg);
      const P = {};
      (SHADOW[v.scene] || SHADOW.bodhi)(g, P);
      const tag = el("div", "lf-shadow-tag", esc(v.tag || "MINH HOẠ")); st.appendChild(tag);
      inner._lf = { st, svg, screen, g, P, tag, scene: v.scene in SHADOW ? v.scene : "bodhi" };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, P = S.P, v = ln.visual, t0 = ln.start, span = Math.max(2, ctx.until - t0);
      tl.fromTo(S.screen, { opacity: 0 }, { opacity: 1, duration: 1.0, ease: "power2.out" }, t0 - .2);
      // Đèn sau màn rối: chập chờn nhẹ, tất định theo hạt giống.
      const r = HF.rng(HF.hashSeed("flick" + ln.sentence_id));
      for (let t = t0 + 1; t < t0 + span; t += .35 + r() * .5) tl.to(S.screen, { opacity: .86 + r() * .14, duration: .18, ease: "sine.inOut" }, t);
      tl.fromTo(S.tag, { opacity: 0 }, { opacity: .8, duration: .5 }, t0 + .6);
      tl.fromTo(S.st, { scale: 1 }, { scale: 1.06, duration: span, ease: "none", transformOrigin: "50% 60%" }, t0);
      const step = (k, fb) => when(ctx, (v.steps || [])[k], fb);
      if (P.moon) tl.fromTo(P.moon, { opacity: 0, y: 40 }, { opacity: .85, y: 0, duration: 2, ease: "sine.out" }, t0);
      if (P.far) tl.fromTo(P.far, { opacity: 0, x: 0 }, { opacity: P.far.getAttribute("opacity"), x: -30, duration: span, ease: "none" }, t0);
      if (S.scene === "bodhi") {
        tl.fromTo([P.ground, P.river], { opacity: 0 }, { opacity: 1, duration: .8 }, t0);
        P.shimmer.forEach((s, k) => tl.fromTo(s, { strokeDashoffset: 0 }, { strokeDashoffset: -400 - k * 80, duration: span, ease: "none" }, t0));
        tl.fromTo(P.tree, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 1.4, ease: "power2.out" }, t0 + .3);
        P.leaves.forEach((lf, k) => tl.to(lf, { rotation: (k % 2 ? 6 : -6), svgOrigin: lf.getAttribute("transform").match(/translate\(([^)]+)\)/)[1].replace(",", " "),
          duration: 1.6 + (k % 5) * .2, yoyo: true, repeat: Math.ceil(span / 1.6), ease: "sine.inOut" }, t0 + .4 + (k % 7) * .1));
        tl.fromTo(P.figure, { opacity: 0 }, { opacity: 1, duration: 1.6, ease: "power1.inOut" }, t0 + 1.4);
        P.stars.forEach((s, k) => tl.to(s, { opacity: .8, duration: .8, yoyo: true, repeat: Math.ceil(span / 1.6), ease: "sine.inOut" }, t0 + .8 + k * .23));
      } else if (S.scene === "departure") {
        tl.fromTo([P.palace, P.ground, P.doorL, P.doorR], { opacity: 0 }, { opacity: 1, duration: .9 }, t0);
        const open = step(0, t0 + span * .45);
        // Ngựa bước chậm qua sân tới trước cổng, cổng mở (bản lề hai bên), rồi phi qua cổng.
        tl.fromTo(P.horse, { x: 60, opacity: 0 }, { x: 1000, opacity: 1, duration: Math.max(1, open - t0 - .2), ease: "sine.inOut" }, t0 + .2);
        tl.to(P.doorL, { scaleX: .06, svgOrigin: "1420 655", duration: 1.2, ease: "power2.inOut" }, open);
        tl.to(P.doorR, { scaleX: .06, svgOrigin: "1640 655", duration: 1.2, ease: "power2.inOut" }, open);
        const go = open + 1.0, out = Math.max(go + 1.2, t0 + span - .2);
        tl.to(P.horse, { x: 2300, duration: out - go, ease: "power1.in" }, go);
        const gait = (from, to, per) => { for (let t = from, k = 0; t < to; t += per, k++) {
          P.legs.forEach((L) => tl.to(L.l, { rotation: ((k + L.ph) % 2 ? 1 : -1) * (per < .3 ? 24 : 12), svgOrigin: `${L.x} -140`, duration: per, ease: "sine.inOut" }, t));
          tl.to(P.hbody, { y: (k % 2) * (per < .3 ? -14 : -5), duration: per, ease: "sine.inOut" }, t); } };
        gait(t0 + .2, open, .42);
        gait(go, out, .2);
      } else if (S.scene === "forest") {
        tl.fromTo([P.trees, P.ground], { opacity: 0 }, { opacity: 1, duration: 1.0 }, t0);
        const stop = step(0, t0 + span * .6);
        // Người đi trước bước đều; người phía sau chạy (nhún nhanh) nhưng khoảng cách KHÔNG đổi.
        tl.fromTo(P.monk.parentNode, { x: 1060, y: 790 }, { x: 1320, y: 790, duration: Math.max(1, stop - t0), ease: "none" }, t0);
        tl.fromTo(P.chaser.parentNode, { x: 380, y: 790 }, { x: 640, y: 790, duration: Math.max(1, stop - t0), ease: "none" }, t0);
        for (let t = t0, k = 0; t < stop; t += .5, k++) tl.to(P.monk, { y: k % 2 ? -3 : 0, duration: .5, ease: "sine.inOut" }, t);
        for (let t = t0, k = 0; t < stop; t += .18, k++) {
          tl.to(P.chaser, { y: k % 2 ? -10 : 0, rotation: 12, svgOrigin: "0 0", duration: .18, ease: "sine.inOut" }, t);
          P.clegs.forEach((l, j) => tl.to(l, { rotation: ((k + j) % 2 ? 1 : -1) * 28, svgOrigin: `${j ? 24 : -4} -90`, duration: .18 }, t));
        }
        tl.to(P.chaser, { rotation: 0, y: 0, duration: .5, ease: "power2.out" }, stop);
        P.clegs.forEach((l) => tl.to(l, { rotation: 0, duration: .4 }, stop));
      } else if (S.scene === "lamp") {
        tl.fromTo(P.lamp, { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 1.4, ease: "power2.out" }, t0);
        const lit = step(0, t0 + 1.5), many = step(1, lit + span * .5);
        tl.fromTo(P.flame, { opacity: 0, scale: .2, svgOrigin: "240 -104" }, { opacity: 1, scale: 1, duration: .8, ease: "back.out(2)" }, lit);
        tl.to(P.core, { opacity: 1, duration: .6 }, lit + .2);
        for (let t = lit + 1, k = 0; t < t0 + span; t += .4, k++) tl.to(P.flame, { scaleY: k % 2 ? .92 : 1.05, scaleX: k % 2 ? 1.04 : .97, svgOrigin: "240 -104", duration: .4, ease: "sine.inOut" }, t);
        P.small.forEach((m, k) => tl.to(m, { opacity: .9, duration: .6 }, many + k * .12));
      } else if (S.scene === "turtle") {
        P.waves.forEach((w, k) => tl.fromTo(w, { x: 0 }, { x: k % 2 ? -180 : -90, duration: span, ease: "none" }, t0));
        tl.fromTo(P.tt, { y: 300, scale: .55, opacity: 0, svgOrigin: "0 0" }, { y: 0, scale: 1, opacity: 1, duration: 3.2, ease: "power2.out" }, t0 + .4);
        const dt = step(0, t0 + span * .55);
        P.dots.forEach((d, k) => tl.fromTo(d.d, { opacity: 0, scale: 0, svgOrigin: `${d.d.getAttribute("cx")} ${d.d.getAttribute("cy")}` },
          { opacity: 1, scale: 1, duration: .35, ease: "back.out(2.4)" }, dt + d.cell * .22 + (k % 9) * .02));
      }
    },
  };

  // ---- Gieo quẻ: ba đồng xu (đồng tiền lỗ vuông), mỗi lần gieo thêm một hào, từ dưới lên ----
  visuals.hexagram = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-hex"); inner.appendChild(st);
      const svg = sv("svg", { viewBox: "0 0 1920 1080", class: "lf-hex-svg" }, st);
      const coin = (cx, cy) => {
        const o = sv("g", { transform: `translate(${cx},${cy})` }, svg), g = sv("g", {}, o), f = sv("g", {}, g);
        sv("circle", { r: 78, class: "coin" }, f);
        sv("circle", { r: 64, class: "coin-rim" }, f);
        sv("rect", { x: -18, y: -18, width: 36, height: 36, class: "coin-hole" }, f);
        const chu = sv("g", { class: "coin-chu" }, f);
        [[0, -42], [0, 42], [-42, 0], [42, 0]].forEach(([x, y]) => sv("path", { d: `M${x - 9},${y - 8} L${x + 9},${y - 8} M${x},${y - 12} L${x},${y + 10} M${x - 8},${y + 2} L${x + 8},${y + 10}`, class: "coin-glyph" }, chu));
        const val = sv("text", { x: 0, y: 132, class: "coin-val" }, g);
        return { g, f, chu, val };
      };
      const coins = [360, 560, 760].map((x) => coin(x, 470));
      const sum = el("div", "lf-hex-sum"); st.appendChild(sum);
      const X0 = 1150, W = 440, base = 790, gap = 92;
      const slots = (v.lines || []).map((yang, k) => {
        const y = base - k * gap, g = sv("g", {}, svg);
        sv("rect", { x: X0, y: y - 19, width: W, height: 38, rx: 4, class: "hex-ghost" }, g);
        const bars = yang ? [sv("rect", { x: X0, y: y - 19, width: W, height: 38, rx: 4, class: "hex-bar" }, g)]
          : [sv("rect", { x: X0, y: y - 19, width: W * .42, height: 38, rx: 4, class: "hex-bar" }, g),
             sv("rect", { x: X0 + W * .58, y: y - 19, width: W * .42, height: 38, rx: 4, class: "hex-bar" }, g)];
        const lab = sv("text", { x: X0 - 34, y: y + 10, class: "hex-lab" }, g); lab.textContent = `HÀO ${k + 1}`;
        return { bars, lab, y, yang };
      });
      const name = el("div", "lf-hex-name"); name.innerHTML = `<b>${esc(v.name || "")}</b><span>${esc(v.sub || "")}</span>`; st.appendChild(name);
      inner._lf = { st, coins, sum, slots, name, X0, W };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, v = ln.visual, t0 = ln.start, steps = v.steps || [];
      tl.fromTo(S.coins.map((c) => c.g), { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: .6, stagger: .1, ease: "power3.out" }, t0);
      tl.fromTo(S.slots.map((s) => s.lab), { opacity: 0 }, { opacity: .55, duration: .4, stagger: .05 }, t0 + .3);
      S.slots.forEach((s) => s.bars.forEach((b) => gsap.set(b, { scaleX: 0, transformOrigin: "50% 50%" })));
      let last = t0;
      S.slots.forEach((s, k) => {
        const t = Math.max(last + 1.0, when(ctx, steps[k], last + 1.4)); last = t;
        // 1 mặt chữ (3) + 2 mặt trơn (2+2) = 7 lẻ -> dương; 2 chữ + 1 trơn = 8 chẵn -> âm.
        const heads = s.yang ? [k % 3] : [k % 3, (k + 1) % 3];
        S.coins.forEach((c, j) => {
          const up = j * .06;
          tl.to(c.g, { y: -230 - j * 30, duration: .38, ease: "power2.out" }, t + up);
          tl.to(c.g, { y: 0, duration: .34, ease: "bounce.out" }, t + .38 + up);
          tl.fromTo(c.f, { scaleX: 1 }, { scaleX: -1, duration: .12, repeat: 5, yoyo: true, ease: "none" }, t + up);
          tl.set(c.chu, { opacity: heads.includes(j) ? 1 : 0 }, t + .5);
          tl.set(c.val, { textContent: heads.includes(j) ? "3" : "2" }, t + .74);
          tl.fromTo(c.val, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: .25 }, t + .74 + up);
        });
        const total = heads.length * 3 + (3 - heads.length) * 2;
        tl.set(S.sum, { innerHTML: `<b>${total}</b><span>${total % 2 ? "LẺ · DƯƠNG" : "CHẴN · ÂM"}</span>` }, t + .9);
        tl.fromTo(S.sum, { opacity: 0, scale: .7 }, { opacity: 1, scale: 1, duration: .3, ease: "back.out(2)" }, t + .9);
        tl.to(s.bars, { scaleX: 1, duration: .45, ease: "power3.out", stagger: .06 }, t + 1.0);
        tl.to(s.lab, { opacity: 1, duration: .3 }, t + 1.0);
        tl.to(S.coins.map((c) => c.val), { opacity: 0, duration: .25 }, t + 1.6);
        tl.to(S.sum, { opacity: 0, duration: .25 }, t + 1.6);
      });
      const rv = when(ctx, v.reveal, last + 1.6);
      tl.fromTo(S.name, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .6, ease: "power3.out" }, Math.max(rv, last + 1.5));
      tl.to(S.slots.flatMap((s) => s.bars), { opacity: .45, duration: .35, yoyo: true, repeat: 3, ease: "sine.inOut" }, Math.max(rv, last + 1.5));
    },
  };

  // ---- Ô Lạc Thư 3x3: chấm -> số -> hàng/cột/chéo cùng ra 15 -> tâm Thổ -> phương vị ----
  const LUOSHU = [[4, 9, 2], [3, 5, 7], [8, 1, 6]];
  visuals.luoshu = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-ls"); inner.appendChild(st);
      const svg = sv("svg", { viewBox: "0 0 1920 1080", class: "lf-ls-svg" }, st);
      const C = 205, X = 960 - 1.5 * C, Y = 165;
      const hl = sv("g", {}, svg);
      const grid = [0, 1, 2, 3].flatMap((k) => [
        sv("path", { d: `M${X},${Y + k * C} L${X + 3 * C},${Y + k * C}`, class: "ls-grid" }, svg),
        sv("path", { d: `M${X + k * C},${Y} L${X + k * C},${Y + 3 * C}`, class: "ls-grid" }, svg)]);
      const cells = [];
      LUOSHU.forEach((row, ry) => row.forEach((n, rx) => {
        const cx = X + rx * C + C / 2, cy = Y + ry * C + C / 2, g = sv("g", {}, svg);
        const dots = Array.from({ length: n }, (_, k) => {
          const a = (k / n) * Math.PI * 2 - Math.PI / 2, rr = n === 1 ? 0 : 22 + n * 4;
          return sv("circle", { cx: cx + Math.cos(a) * rr, cy: cy + Math.sin(a) * rr, r: 11, class: n % 2 ? "ls-yang" : "ls-yin" }, g);
        });
        const num = sv("text", { x: cx, y: cy + 40, class: "ls-num" }, g); num.textContent = n;
        cells.push({ g, dots, num, cx, cy, n });
      }));
      const band = (x, y, w, h) => sv("rect", { x, y, width: w, height: h, rx: 14, class: "ls-band" }, hl);
      const rows = [0, 1, 2].map((k) => ({ b: band(X - 10, Y + k * C + 10, 3 * C + 20, C - 20), lx: X + 3 * C + 50, ly: Y + k * C + C / 2 + 22, a: "start" }));
      const cols = [0, 1, 2].map((k) => ({ b: band(X + k * C + 10, Y - 10, C - 20, 3 * C + 20), lx: X + k * C + C / 2, ly: Y - 30, a: "middle" }));
      const diags = [sv("path", { d: `M${X},${Y} L${X + 3 * C},${Y + 3 * C}`, class: "ls-diag" }, svg), sv("path", { d: `M${X + 3 * C},${Y} L${X},${Y + 3 * C}`, class: "ls-diag" }, svg)];
      const lab = (x, y, a, t, cls) => { const e = sv("text", { x, y, class: cls || "ls-sum", "text-anchor": a }, svg); e.textContent = t; return e; };
      rows.forEach((r) => { r.t = lab(r.lx, r.ly, r.a, "= 15"); });
      cols.forEach((c) => { c.t = lab(c.lx, c.ly, c.a, "15"); });
      const dl = [lab(X - 40, Y - 26, "end", "15"), lab(X + 3 * C + 40, Y - 26, "start", "15")];
      const tho = lab(960, Y + 1.5 * C + 82, "middle", "THỔ", "ls-tho");
      const dirs = [[960, Y - 70, "NAM"], [960, Y + 3 * C + 60, "BẮC"], [X - 90, Y + 1.5 * C + 12, "ĐÔNG"], [X + 3 * C + 90, Y + 1.5 * C + 12, "TÂY"]]
        .map(([x, y, t]) => lab(x, y, "middle", t, "ls-dir"));
      inner._lf = { st, grid, cells, rows, cols, diags, dl, tho, dirs, title: title(st, v.title, 150, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, v = ln.visual, t0 = ln.start;
      if (S.title) tl.fromTo(S.title, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .5 }, t0 + .1);
      S.grid.forEach((p, k) => drawOn(tl, p, t0 + k * .06, .7));
      S.cells.forEach((c, k) => tl.fromTo(c.dots, { opacity: 0, scale: 0, svgOrigin: `${c.cx} ${c.cy}` }, { opacity: 1, scale: 1, duration: .35, stagger: .03, ease: "back.out(2)" }, t0 + .5 + k * .16));
      const hide = [...S.rows.flatMap((r) => [r.b, r.t]), ...S.cols.flatMap((c) => [c.b, c.t]), ...S.diags, ...S.dl, S.tho, ...S.dirs, ...S.cells.map((c) => c.num)];
      gsap.set(hide, { opacity: 0 });
      const st = {}; (v.steps || []).forEach((s) => { st[s.do] = s; });
      const T = (k, fb) => when(ctx, st[k], fb);
      const tn = T("numbers", t0 + 3);
      S.cells.forEach((c, k) => {
        const t = tn + k * .18;
        tl.to(c.dots, { opacity: 0, scale: .2, svgOrigin: `${c.cx} ${c.cy}`, duration: .25 }, t);
        tl.fromTo(c.num, { opacity: 0, scale: .4, svgOrigin: `${c.cx} ${c.cy}` }, { opacity: 1, scale: 1, duration: .35, ease: "back.out(2.2)" }, t + .12);
      });
      const flash = (els, t, each) => els.forEach((e, k) => {
        tl.fromTo(e.b, { opacity: 0 }, { opacity: 1, duration: .25 }, t + k * each);
        tl.to(e.b, { opacity: 0, duration: .35 }, t + k * each + .55);
        tl.fromTo(e.t, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: .3 }, t + k * each + .1);
      });
      if (st.rows) flash(S.rows, T("rows"), .45);
      if (st.cols) flash(S.cols, T("cols"), .45);
      if (st.diags) {
        const t = T("diags");
        S.diags.forEach((d, k) => { tl.set(d, { opacity: 1 }, t + k * .5); drawOn(tl, d, t + k * .5, .5); tl.fromTo(S.dl[k], { opacity: 0 }, { opacity: 1, duration: .3 }, t + k * .5 + .4); });
      }
      if (st.center) {
        const t = T("center"), c = S.cells[4];
        tl.to([...S.rows.map((r) => r.t), ...S.cols.map((c2) => c2.t), ...S.diags, ...S.dl], { opacity: .18, duration: .4 }, t);
        tl.fromTo(c.num, { scale: 1, svgOrigin: `${c.cx} ${c.cy}` }, { scale: 1.35, duration: .5, ease: "back.out(2)" }, t);
        tl.to(c.num, { fill: css("--accent"), duration: .3 }, t);
        tl.fromTo(S.tho, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: .4 }, t + .3);
      }
      if (st.dirs) {
        const t = T("dirs");
        tl.to([...S.rows.map((r) => r.t), ...S.cols.map((c2) => c2.t), ...S.diags, ...S.dl], { opacity: 0, duration: .4 }, t - .2);
        tl.fromTo(S.dirs, { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: .4, stagger: .15, ease: "back.out(2)" }, t);
      }
    },
  };

  // ---- Bảng kê: nhiều dòng hiện dần theo lời (bảng tổng hợp 12 tuổi, đối chiếu) ----
  visuals.ledger = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-ledger"); inner.appendChild(st);
      const box = el("div", "lf-led"); st.appendChild(box);
      const cols = v.cols || [];
      const W = v.widths || cols.map(() => 1);
      const grid = W.map((w) => w + "fr").join(" ");
      const all = v.rows || [];
      // Bảng dài (> 8 dòng, vd 12 con giáp): chia hai cột cạnh nhau -> dòng cao, chữ to đọc được trên điện thoại.
      const two = all.length > 8, per = two ? Math.ceil(all.length / 2) : all.length;
      const parts = two ? [el("div", "lf-led-col"), el("div", "lf-led-col")] : [box];
      if (two) { box.classList.add("two"); parts.forEach((c) => box.appendChild(c)); }
      parts.forEach((pc) => {
        if (!cols.length) return;
        const h = el("div", "lf-led-row head"); h.style.gridTemplateColumns = grid;
        cols.forEach((c) => h.appendChild(el("div", "c", esc(c)))); pc.appendChild(h);
      });
      const rows = all.map((r, i) => {
        const e = el("div", "lf-led-row" + (r.hot ? " hot" : "")); e.style.gridTemplateColumns = grid;
        (r.cells || []).forEach((c, k) => e.appendChild(el("div", "c" + (k ? "" : " k"), esc(c))));
        parts[two ? Math.floor(i / per) : 0].appendChild(e); return e;
      });
      const rh = Math.min(66, Math.floor(640 / Math.max(1, per + 1)));
      box.style.setProperty("--rh", rh + "px");
      inner._lf = { box, rows, title: title(st, v.title, 150, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, v = ln.visual, rows = v.rows || [];
      if (S.title) tl.fromTo(S.title, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .5 }, ln.start + .1);
      const heads = S.box.querySelectorAll(".head");
      if (heads.length) tl.fromTo(heads, { opacity: 0, y: -10 }, { opacity: 1, y: 0, duration: .4 }, ln.start + .2);
      S.rows.forEach((r, k) => {
        const t = when(ctx, rows[k], ln.start + .5 + k * .25);
        tl.fromTo(r, { opacity: 0, x: -40 }, { opacity: 1, x: 0, duration: .4, ease: "power3.out" }, t);
        tl.fromTo(r, { backgroundColor: "rgba(255,255,255,0)" }, { backgroundColor: "var(--lf-led-flash)", duration: .25, yoyo: true, repeat: 1 }, t + .1);
      });
    },
  };

  // ---- Thở cùng người xem: vòng tròn nở khi hít vào, thu lại khi thở ra ----
  visuals.breath = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-breath"); inner.appendChild(st);
      const svg = sv("svg", { viewBox: "0 0 1920 1080", class: "lf-breath-svg" }, st);
      const halo = sv("circle", { cx: 960, cy: 470, r: 150, class: "br-halo" }, svg);
      const ring = sv("circle", { cx: 960, cy: 470, r: 150, class: "br-ring" }, svg);
      const lab = el("div", "lf-breath-lab", ""); st.appendChild(lab);
      inner._lf = { halo, ring, lab, title: title(st, v.title, 150, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lf, v = ln.visual, inh = v.inhale || 4, exh = v.exhale || 5;
      if (S.title) tl.fromTo(S.title, { opacity: 0 }, { opacity: 1, duration: .6 }, ln.start + .1);
      tl.fromTo(S.ring, { opacity: 0 }, { opacity: 1, duration: .8 }, ln.start);
      tl.fromTo(S.halo, { opacity: 0 }, { opacity: .1, duration: .8 }, ln.start);
      let t = when(ctx, v, ln.start + .6);
      const end = ctx.until - .4;
      while (t + inh + exh <= end + .5) {
        tl.set(S.lab, { textContent: "HÍT VÀO" }, t);
        tl.fromTo(S.lab, { opacity: 0 }, { opacity: 1, duration: .5 }, t);
        tl.to([S.ring, S.halo], { attr: { r: 300 }, duration: inh, ease: "sine.inOut" }, t);
        tl.set(S.lab, { textContent: "THỞ RA" }, t + inh);
        tl.fromTo(S.lab, { opacity: .3 }, { opacity: 1, duration: .5 }, t + inh);
        tl.to([S.ring, S.halo], { attr: { r: 150 }, duration: exh, ease: "sine.inOut" }, t + inh);
        t += inh + exh;
      }
    },
  };

  /* ================= F: SS-tier (plan "kinetic": true) =================
     Đo trên F1/B1 (01/10/2026): ~45% thời lượng là chữ khoá đứng yên trên nền trơn và
     sơ đồ lặp khuôn. Ở đây: thẻ chữ động 5 biến thể có bộ chọn chống lặp, cảnh "bảo tàng"
     (máy quay tiến vào từng chi tiết hiện vật, có nhãn chỉ dẫn), mở chương riêng mỗi kênh. */
  function blobs(st, n) {   // nền luôn chuyển động nhẹ: các quầng màu lớn trôi chậm
    const out = [];
    for (let k = 0; k < n; k++) { const b = el("div", "kc-blob kc-blob" + k); st.appendChild(b); out.push(b); }
    return out;
  }
  function driftBlobs(tl, bs, t0, span) {
    bs.forEach((b, k) => tl.fromTo(b, { x: (k ? 120 : -160), y: (k ? -60 : 40), scale: 1 },
      { x: (k ? -140 : 180), y: (k ? 50 : -40), scale: 1.25, duration: Math.max(2, span + 1), ease: "sine.inOut" }, t0 - .4));
  }
  const KC_VARIANTS = () => (NIGHT() ? ["stamp", "cascade", "placard", "lens", "gold"] : ["brush", "cascade", "placard", "lens", "stamp"]);
  const keycard = {
    build(inner, ln, i, ctx) {
      const hot = (ln.key_parts || []).filter((p) => p.hot).map((p) => p.t).join(" ");
      const key = clean(hot || (ln.key_parts || []).map((p) => p.t).join(" ")).replace(/[.:;,!?]+$/, "");
      ln._kc = pick("keycard", KC_VARIANTS());
      const st = el("div", "lf-stage kc kc-" + ln._kc); inner.appendChild(st);
      const bs = blobs(st, 2);
      const box = el("div", "kc-box"); st.appendChild(box);
      const t = el("div", "kc-key" + (key.length > 26 ? " long" : "") + (key.length > 40 ? " xlong" : "")); box.appendChild(t);
      const words = key.toUpperCase().split(/\s+/).map((w) => { const s = el("span", "kc-w", esc(w)); t.appendChild(s); t.appendChild(document.createTextNode(" ")); return s; });
      const S = { st, bs, box, t, words, key };
      if (ln._kc === "brush" || ln._kc === "gold") {
        const svg = sv("svg", { class: "kc-stroke", viewBox: "0 0 1000 120", preserveAspectRatio: "none" }, box);
        const r = HF.rng(HF.hashSeed("brush" + ln.sentence_id));
        let d = "M10,70"; for (let x = 60; x <= 990; x += 70) d += ` L${x},${60 + (r() - .5) * 18}`;
        S.stroke = sv("path", { d, class: "kc-stroke-p" }, svg);
      }
      if (ln._kc === "placard") {
        const chap = ctx && ctx.LINES ? ctx.LINES.slice(0, i).reverse().find((l) => l.chapter_no) : null;
        S.eye = el("div", "kc-eye", chap ? `PHẦN ${String(chap.chapter_no).padStart(2, "0")} · ${esc(clean((chap.key_parts || []).map((p) => p.t).join(" ")).toUpperCase())}` : "");
        box.insertBefore(S.eye, t);
        S.frame = sv("svg", { class: "kc-frame", viewBox: "0 0 1000 300", preserveAspectRatio: "none" }, box);
        S.rects = [sv("rect", { x: 4, y: 4, width: 992, height: 292, class: "kc-fr" }, S.frame), sv("rect", { x: 16, y: 16, width: 968, height: 268, class: "kc-fr thin" }, S.frame)];
      }
      if (ln._kc === "stamp") {
        S.seal = el("div", "kc-seal"); box.appendChild(S.seal);
        // FS (la bàn đêm, sơn mài, Đông Hồ): chữ 吉; BUD (giấy mực, trăng thiền, than hồng): bánh xe pháp
        if (skin() === "dongho" || (NIGHT() && skin() !== "moon" && skin() !== "ember")) S.seal.appendChild(el("span", "", "吉"));
        else {   // bánh xe pháp 8 nan (biểu tượng Phật giáo sơ kỳ), không dùng chữ Hán
          const w = sv("svg", { viewBox: "-50 -50 100 100", class: "kc-wheel" }, S.seal);
          sv("circle", { r: 34, class: "kw" }, w); sv("circle", { r: 9, class: "kw" }, w);
          for (let k = 0; k < 8; k++) { const A = k * Math.PI / 4; sv("line", { x1: Math.cos(A) * 9, y1: Math.sin(A) * 9, x2: Math.cos(A) * 34, y2: Math.sin(A) * 34, class: "kw" }, w);
            sv("circle", { cx: Math.cos(A) * 42, cy: Math.sin(A) * 42, r: 4, class: "kwd" }, w); }
        }
      }
      if (ln._kc === "lens") { S.glow = el("div", "kc-glow"); st.insertBefore(S.glow, box); }
      inner._kc = S;
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._kc, t0 = ln.start, span = Math.max(1.6, (ctx && ctx.until ? ctx.until : ln.end) - t0), v = ln._kc;
      driftBlobs(tl, S.bs, t0, span);
      tl.fromTo(S.box, { scale: 1 }, { scale: 1.045, duration: span + .5, ease: "none" }, t0);   // máy quay đẩy nhẹ, không đứng yên
      const hotWords = (ln.words || []).filter((w) => w.hot);
      if (v === "cascade") {   // mỗi chữ khoá rơi xuống ĐÚNG lúc được đọc
        S.words.forEach((w, k) => { const at = hotWords[k] ? hotWords[k].t - .05 : t0 + .15 + k * .14;
          tl.fromTo(w, { opacity: 0, y: -60, rotationX: 70, transformPerspective: 900 }, { opacity: 1, y: 0, rotationX: 0, duration: .45, ease: "back.out(2)" }, at); });
      } else if (v === "brush" || v === "gold") {   // nét cọ quét ngang, chữ lộ theo nét
        const len = S.stroke.getTotalLength ? S.stroke.getTotalLength() : 1000;
        S.stroke.style.strokeDasharray = `${len}`;
        tl.fromTo(S.stroke, { strokeDashoffset: len }, { strokeDashoffset: 0, duration: .7, ease: "power2.inOut" }, t0 + .05);
        tl.fromTo(S.t, { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: .75, ease: "power2.inOut" }, t0 + .15);
        if (v === "gold") sheen(tl, S.t, t0 + .9);
      } else if (v === "placard") {   // biển chú thích bảo tàng: khung tự vẽ, nhãn chương, chữ hiện
        S.rects.forEach((r, k) => drawOn(tl, r, t0 + k * .15, .9, "power2.inOut"));
        tl.fromTo(S.eye, { opacity: 0, letterSpacing: "0.6em" }, { opacity: 1, letterSpacing: "0.3em", duration: .8, ease: "power3.out" }, t0 + .2);
        tl.fromTo(S.t, { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: .6, ease: "power3.out" }, t0 + .45);
      } else if (v === "lens") {      // chữ siết dần từ rộng về chuẩn, quầng sáng lướt sau
        tl.fromTo(S.t, { opacity: 0, letterSpacing: "0.5em", filter: "blur(8px)" }, { opacity: 1, letterSpacing: "0.02em", filter: "blur(0px)", duration: 1.2, ease: "expo.out" }, t0);
        tl.fromTo(S.glow, { x: -500, opacity: 0 }, { x: 500, opacity: .9, duration: span + .5, ease: "sine.inOut" }, t0);
      } else {                        // stamp: chữ hiện, ấn son/ấn vàng đập xuống bên cạnh
        tl.fromTo(S.t, { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: .5, ease: "power3.out" }, t0 + .05);
        tl.fromTo(S.seal, { opacity: 0, scale: 2.2, rotation: -18 }, { opacity: 1, scale: 1, rotation: -6, duration: .35, ease: "power4.in" }, t0 + .55);
        tl.fromTo(S.box, { x: 0 }, { x: 5, duration: .05, yoyo: true, repeat: 3, ease: "none" }, t0 + .9);
      }
    },
  };

  // ---- Cảnh "bảo tàng": hiện vật + máy quay tiến vào từng chi tiết + nhãn chỉ dẫn ----
  // notes: [{at, word, x, y, label, sub}] -- x,y là toạ độ trên ảnh (0..1). Máy quay đưa chi tiết
  // vào giữa khung (phóng z), chấm + vòng sáng + đường dẫn + nhãn hiện đúng lúc lời kể nhắc tới.
  visuals.museum = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-mus"); inner.appendChild(st);
      const F = { W: 1920, H: 1080 };
      const cam = el("div", "mus-cam"); st.appendChild(cam);
      // contain = thấy TRỌN hiện vật (ảnh dọc mặc định contain -- cover sẽ cắt mất đầu tượng); cover = phủ kín khung.
      const contain = v.fit === "contain" || (v.fit !== "cover" && v.h > v.w);
      const k = contain ? Math.min(F.W / v.w, F.H / v.h) * .92 : Math.max(F.W / v.w, F.H / v.h), w = v.w * k, h = v.h * k;
      const img = el("div", "mus-img"); Object.assign(img.style, { width: w + "px", height: h + "px", backgroundImage: `url(${v.src})` });
      cam.appendChild(img);
      const vig = el("div", "mus-vig"); st.appendChild(vig);
      st.appendChild(el("div", "mus-veil"));   // phụ đề đọc được trên đá tối (nền giấy: dải sáng; nền đêm: dải tối)
      const layer = el("div", "mus-notes"); st.appendChild(layer);
      const notes = (v.notes || []).map((n, j) => {
        const g = el("div", "mus-note " + (n.side || (j % 2 ? "left" : "right")));
        g.appendChild(el("div", "dot")); g.appendChild(el("div", "ring")); g.appendChild(el("div", "lead"));
        const lab = el("div", "lab"); lab.appendChild(el("b", "", esc(n.label || ""))); if (n.sub) lab.appendChild(el("span", "", esc(n.sub)));
        g.appendChild(lab); layer.appendChild(g); return { g, n };
      });
      const plate = el("div", "mus-plate"); plate.innerHTML = `<b>${esc(v.title || "")}</b><span>${esc(v.tag || "")}</span>`; st.appendChild(plate);
      inner._mus = { st, cam, img, vig, notes, plate, w, h, F };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._mus, v = ln.visual, t0 = ln.start, span = Math.max(3, ctx.until - t0);
      const camAt = (x, y, z) => ({ x: S.F.W / 2 - x * S.w * z, y: S.F.H / 2 - y * S.h * z, scale: z });
      tl.set(S.cam, { transformOrigin: "0 0" }, 0);
      const z0 = 1.0;
      tl.fromTo(S.cam, camAt(.5, .5, z0 * 1.08), { ...camAt(.5, .5, z0), duration: 2.2, ease: "power2.out" }, t0 - .2);
      tl.fromTo(S.img, { opacity: 0, filter: "brightness(.6)" }, { opacity: 1, filter: "brightness(1)", duration: 1.2 }, t0 - .2);
      tl.fromTo(S.plate, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .6 }, t0 + .6);
      let prev = t0 + 1.2;
      S.notes.forEach((N, j) => {
        const n = N.n, t = Math.max(prev + .6, when(ctx, n, prev + 2)), z = n.z || 1.7;
        tl.to(S.cam, { ...camAt(n.x, n.y, z), duration: 1.1, ease: "power3.inOut" }, t - .7);
        tl.to(S.vig, { opacity: 1, duration: .6 }, t - .5);
        if (j) tl.to(S.notes[j - 1].g, { opacity: 0, duration: .3 }, t - .7);
        tl.fromTo(N.g.querySelector(".dot"), { scale: 0 }, { scale: 1, duration: .3, ease: "back.out(3)" }, t + .35);
        tl.fromTo(N.g.querySelector(".ring"), { scale: .3, opacity: .9 }, { scale: 2.6, opacity: 0, duration: 1.1, ease: "power2.out", repeat: 1 }, t + .4);
        tl.fromTo(N.g.querySelector(".lead"), { scaleX: 0 }, { scaleX: 1, duration: .4, ease: "power2.out" }, t + .5);
        tl.fromTo(N.g.querySelector(".lab"), { opacity: 0, x: N.g.classList.contains("left") ? 30 : -30 }, { opacity: 1, x: 0, duration: .45, ease: "power3.out" }, t + .75);
        tl.set(N.g, { opacity: 1 }, t + .3);
        prev = t;
      });
      // về toàn cảnh trước khi rời cảnh (khép vòng, người xem thấy lại cả hiện vật)
      const out = ctx.until - 1.6;
      if (S.notes.length && out > prev + 1.5) {
        tl.to(S.notes[S.notes.length - 1].g, { opacity: 0, duration: .3 }, out - .2);
        tl.to(S.vig, { opacity: 0, duration: .8 }, out);
        tl.to(S.cam, { ...camAt(.5, .5, z0), duration: 1.4, ease: "power2.inOut" }, out);
      }
    },
  };

  // ---- Nạp âm từng năm sinh: ảnh minh hoạ ĐÚNG nghĩa mệnh (đất trên vách, cây dâu, sấm sét...) + thẻ ----
  visuals.napam = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-np"); inner.appendChild(st);
      const k = Math.max(1920 / v.w, 1080 / v.h), w = v.w * k, h = v.h * k;
      const img = el("div", "np-img"); Object.assign(img.style, { width: w + "px", height: h + "px", left: (1920 - w) / 2 + "px", top: (1080 - h) / 2 + "px", backgroundImage: `url(${v.src})` });
      st.appendChild(img); st.appendChild(el("div", "np-shade"));
      const card = el("div", "np-card"); st.appendChild(card);
      const yr = el("div", "np-yr", esc(v.yr || "")), cc = el("div", "np-cc", esc(v.cc || ""));
      const na = el("div", "np-na", esc(v.na || "")), ng = el("div", "np-ng", esc(v.nghia || ""));
      const pill = el("div", "np-pill"); pill.style.setProperty("--el", ELEM_COLOR[v.el] || css("--accent"));
      pill.innerHTML = `<i></i>${esc(v.pill || "")}`;
      [yr, cc, na, ng, pill].forEach((x) => card.appendChild(x));
      inner._np = { img, yr, cc, na, ng, pill };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._np, v = ln.visual, t0 = ln.start, span = Math.max(3, ctx.until - t0);
      tl.fromTo(S.img, { scale: 1.12, x: 40 }, { scale: 1.0, x: -40, duration: span + .6, ease: "none" }, t0 - .3);
      tl.fromTo(S.yr, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: .55, ease: "power3.out" }, t0 + .1);
      tl.fromTo(S.cc, { opacity: 0, x: -20 }, { opacity: 1, x: 0, duration: .45 }, t0 + .35);
      tl.fromTo(S.na, { opacity: 0, clipPath: "inset(0% 100% 0% 0%)" }, { opacity: 1, clipPath: "inset(0% 0% 0% 0%)", duration: .7, ease: "power2.inOut" }, when(ctx, { at: ln.sentence_id, word: (v.na || "").split(" ")[0] }, t0 + .9));
      tl.fromTo(S.ng, { opacity: 0 }, { opacity: 1, duration: .5 }, when(ctx, { at: ln.sentence_id, word: "tức" }, t0 + 1.6));
      tl.fromTo(S.pill, { opacity: 0, scale: .7 }, { opacity: 1, scale: 1, duration: .4, ease: "back.out(2.2)" }, when(ctx, v.pill_at || {}, t0 + 2.6));
    },
  };

  // ---- Cửu Diệu: 9 thiên thể theo nhóm cát / hung / trung, sáng lên đúng lúc được nhắc ----
  const CD = [["Thái Dương", "MẶT TRỜI", "cát"], ["Thái Âm", "MẶT TRĂNG", "cát"], ["Mộc Đức", "SAO MỘC", "cát"],
              ["Thủy Diệu", "SAO THỦY", "trung"], ["Vân Hớn", "SAO HỎA", "trung"], ["Thổ Tú", "SAO THỔ", "trung"],
              ["Thái Bạch", "SAO KIM", "hung"], ["La Hầu", "ĐIỂM GIAO BẮC", "hung"], ["Kế Đô", "ĐIỂM GIAO NAM", "hung"]];
  const CD_COLOR = { "cát": "#e6b84a", "trung": "#6fa8e6", "hung": "#e0533d" };
  visuals.cuudieu = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-cd"); inner.appendChild(st);
      const svg = sv("svg", { viewBox: "-960 -540 1920 1080", class: "cd-svg" }, st);
      const orbit = sv("g", {}, svg);
      sv("circle", { cx: -180, cy: -40, r: 330, class: "cd-orbit" }, orbit);
      sv("circle", { cx: -180, cy: -40, r: 26, class: "cd-earth" }, orbit);
      const nodes = {};
      CD.forEach(([name, body, grp], k) => {
        const A = -Math.PI / 2 + k * (2 * Math.PI / 9), x = -180 + Math.cos(A) * 330, y = -40 + Math.sin(A) * 330;
        const g = sv("g", { transform: `translate(${x},${y})` }, orbit), inG = sv("g", {}, g);
        const halo = sv("circle", { r: 58, fill: CD_COLOR[grp], opacity: 0 }, inG);
        const dot = sv("circle", { r: name === "La Hầu" || name === "Kế Đô" ? 30 : 34, class: "cd-dot " + (name === "La Hầu" || name === "Kế Đô" ? "node" : ""), style: `--c:${CD_COLOR[grp]}` }, inG);
        const lab = sv("text", { x: 0, y: Math.sin(A) > .3 ? 76 : -52, class: "cd-lab" }, inG); lab.textContent = name;
        nodes[name] = { inG, halo, dot, lab, x, y, grp, body };
      });
      const chip = el("div", "cd-chip"); st.appendChild(chip);
      const legend = el("div", "cd-legend");
      legend.innerHTML = Object.entries(CD_COLOR).map(([g, c]) => `<span><i style="background:${c}"></i>${g === "cát" ? "CÁT TINH" : g === "hung" ? "HUNG TINH" : "TRUNG TÍNH"}</span>`).join("");
      st.appendChild(legend);
      inner._cd = { orbit, nodes, chip, legend, title: title(st, v.title, 150, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._cd, v = ln.visual, t0 = ln.start, span = Math.max(3, ctx.until - t0);
      if (S.title) tl.fromTo(S.title, { opacity: 0 }, { opacity: 1, duration: .5 }, t0 + .1);
      tl.fromTo(S.orbit, { rotation: -25, svgOrigin: "-180 -40", opacity: 0 }, { rotation: 0, svgOrigin: "-180 -40", opacity: 1, duration: 1.6, ease: "power3.out" }, t0);
      Object.values(S.nodes).forEach((N, k) => tl.fromTo(N.inG, { scale: 0, svgOrigin: "0 0" }, { scale: 1, svgOrigin: "0 0", duration: .45, ease: "back.out(2.4)" }, t0 + .3 + k * .09));
      tl.fromTo(S.legend, { opacity: 0 }, { opacity: 1, duration: .5 }, t0 + 1.2);
      let lit = [];
      (v.steps || []).forEach((st, k) => {
        const t = when(ctx, st, t0 + 1.5 + k * 1.2);
        const names = st.group ? CD.filter((c) => c[2] === st.group).map((c) => c[0]) : [st.star];
        lit.forEach((N) => tl.to([N.halo], { opacity: 0, duration: .3 }, t - .1));
        lit = names.map((n) => S.nodes[n]).filter(Boolean);
        lit.forEach((N) => { tl.to(N.halo, { opacity: .35, duration: .35 }, t); tl.fromTo(N.inG, { scale: 1 }, { scale: 1.25, svgOrigin: "0 0", duration: .35, yoyo: true, repeat: 1 }, t); });
        const N0 = lit[0];
        if (N0) {
          const txt = st.group ? `<b>${st.group === "cát" ? "3 CÁT TINH" : st.group === "hung" ? "3 HUNG TINH" : "3 SAO TRUNG TÍNH"}</b><span>${esc(st.label || "")}</span>`
            : `<b>${esc(st.star)}</b><span>${esc(st.label || N0.body)}</span>`;
          tl.set(S.chip, { innerHTML: txt, borderColor: CD_COLOR[N0.grp] }, t);
          tl.fromTo(S.chip, { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: .4, ease: "power3.out" }, t);
        }
      });
      tl.to(S.orbit, { rotation: 8, svgOrigin: "-180 -40", duration: span, ease: "none" }, t0 + 1.6);
    },
  };

  // ---- Nhật thực: Mặt Trăng trượt qua che Mặt Trời (La Hầu / Kế Đô "nuốt" Mặt Trời, Mặt Trăng) ----
  visuals.eclipse = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-ecl"); inner.appendChild(st);
      const svg = sv("svg", { viewBox: "-960 -540 1920 1080", class: "ecl-svg" }, st);
      const defs = sv("defs", {}, svg);
      const gr = sv("radialGradient", { id: "cor" + ln.sentence_id }, defs);
      [["0%", "#fff6d8", 1], ["55%", "#ffd27a", .55], ["100%", "#ff9a3c", 0]].forEach(([o, c, a]) => sv("stop", { offset: o, "stop-color": c, "stop-opacity": a }, gr));
      const corona = sv("circle", { cx: 0, cy: -60, r: 330, fill: `url(#cor${ln.sentence_id})`, opacity: 0 }, svg);
      const sun = sv("circle", { cx: 0, cy: -60, r: 170, class: "ecl-sun" }, svg);
      const moon = sv("circle", { cx: -760, cy: -60, r: 176, class: "ecl-moon" }, svg);
      const cap = el("div", "ecl-cap", esc(v.label || "")); st.appendChild(cap);
      inner._ecl = { corona, sun, moon, cap };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._ecl, v = ln.visual, t0 = ln.start, span = Math.max(3, ctx.until - t0);
      const full = when(ctx, (v.steps || [])[0], t0 + span * .55);
      tl.fromTo(S.sun, { opacity: 0, scale: .8, svgOrigin: "0 -60" }, { opacity: 1, scale: 1, svgOrigin: "0 -60", duration: .9 }, t0);
      tl.fromTo(S.moon, { attr: { cx: -760 } }, { attr: { cx: 0 }, duration: Math.max(1.2, full - t0 - .2), ease: "power1.inOut" }, t0 + .2);
      tl.to(S.sun, { opacity: .15, duration: .5 }, full - .3);
      tl.fromTo(S.corona, { opacity: 0, scale: .6, svgOrigin: "0 -60" }, { opacity: 1, scale: 1.1, svgOrigin: "0 -60", duration: 1.2, ease: "power2.out" }, full - .2);
      tl.fromTo(S.cap, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .6 }, full + .2);
      tl.to(S.moon, { attr: { cx: 120 }, duration: Math.max(1, t0 + span - full - .5), ease: "none" }, full + .8);
    },
  };

  // ---- Mở chương đặc trưng: mực loang (nền giấy · Phật giáo) / la bàn 3D (nền đêm · Phong Thuỷ) ----
  const TRIGRAM = [[1, 1, 1], [0, 1, 1], [1, 0, 1], [0, 0, 1], [1, 1, 0], [0, 1, 0], [1, 0, 0], [0, 0, 0]];
  let signatureChapter = {
    build(inner, ln) {
      const t = clean((ln.key_parts || []).map((p) => p.t).join(" ")).replace(/[.:;,]$/, "");
      const no = String(ln.chapter_no).padStart(2, "0");
      const st = el("div", "lf-stage sig " + (NIGHT() ? "sig-luopan" : "sig-ink")); inner.appendChild(st);
      const svg = sv("svg", { class: "sig-svg", viewBox: "-960 -540 1920 1080" }, st);
      const S = { st, svg };
      if (NIGHT()) {
        const g = sv("g", { class: "lp" }, svg); S.lp = g;
        S.rings = [0, 1, 2].map((k) => sv("g", {}, g));
        sv("circle", { r: 430, class: "lp-ring" }, S.rings[0]);
        for (let a = 0; a < 72; a++) { const r1 = 430, r2 = a % 3 ? 416 : 400, A = a * Math.PI / 36;
          sv("line", { x1: Math.cos(A) * r1, y1: Math.sin(A) * r1, x2: Math.cos(A) * r2, y2: Math.sin(A) * r2, class: "lp-tick" }, S.rings[0]); }
        TRIGRAM.forEach((tg, k) => { const A = k * Math.PI / 4 - Math.PI / 2, cx = Math.cos(A) * 350, cy = Math.sin(A) * 350;
          const gg = sv("g", { transform: `translate(${cx},${cy}) rotate(${k * 45})` }, S.rings[0]);
          tg.forEach((yang, j) => { const y = (j - 1) * 16;
            if (yang) sv("rect", { x: -26, y: y - 4, width: 52, height: 8, class: "lp-bar" }, gg);
            else { sv("rect", { x: -26, y: y - 4, width: 22, height: 8, class: "lp-bar" }, gg); sv("rect", { x: 4, y: y - 4, width: 22, height: 8, class: "lp-bar" }, gg); } }); });
        sv("circle", { r: 300, class: "lp-ring" }, S.rings[1]);
        CHI.forEach((c, k) => { const A = k * Math.PI / 6 - Math.PI / 2;
          const tx = sv("text", { x: Math.cos(A) * 255, y: Math.sin(A) * 255 + 10, class: "lp-chi" }, S.rings[1]); tx.textContent = c; });
        sv("circle", { r: 205, class: "lp-ring thin" }, S.rings[2]);
        for (let k = 0; k < 8; k++) { const A = k * Math.PI / 4; sv("line", { x1: Math.cos(A) * 120, y1: Math.sin(A) * 120, x2: Math.cos(A) * 205, y2: Math.sin(A) * 205, class: "lp-tick" }, S.rings[2]); }
        S.needle = sv("path", { d: "M0,-150 L12,0 L0,150 L-12,0 Z", class: "lp-needle" }, g);
      } else {
        const defs = sv("defs", {}, svg);
        const f = sv("filter", { id: "ink" + ln.sentence_id, x: "-30%", y: "-30%", width: "160%", height: "160%" }, defs);
        sv("feTurbulence", { type: "fractalNoise", baseFrequency: ".012", numOctaves: 3, seed: ln.sentence_id % 97, result: "n" }, f);
        sv("feDisplacementMap", { in: "SourceGraphic", in2: "n", scale: 140 }, f);
        S.blot = sv("circle", { r: 520, class: "ink-blot", filter: `url(#ink${ln.sentence_id})` }, svg);
        S.ripples = [1, 2, 3].map(() => sv("circle", { r: 120, class: "ink-ripple" }, svg));
      }
      const cap = el("div", "sig-cap"); cap.appendChild(el("div", "sig-no", "PHẦN " + no)); cap.appendChild(el("div", "sig-title" + (t.length > 30 ? " long" : ""), esc(t)));
      st.appendChild(cap); S.cap = cap;
      inner._sig = S;
    },
    enter(tl, inner, ln) {
      const S = inner._sig, t0 = ln.start, span = Math.max(1.8, ln.end - t0);
      if (S.lp) {
        tl.fromTo(S.lp, { rotationX: 62, scale: .7, opacity: 0, transformPerspective: 1600, transformOrigin: "50% 50%" },
          { rotationX: 0, scale: 1, opacity: 1, duration: 1.6, ease: "power3.out" }, t0 - .3);
        S.rings.forEach((r, k) => tl.fromTo(r, { rotation: (k % 2 ? -1 : 1) * (150 + k * 40), svgOrigin: "0 0" },
          { rotation: 0, svgOrigin: "0 0", duration: 1.9, ease: "expo.out" }, t0 - .3));
        tl.fromTo(S.needle, { rotation: -200, svgOrigin: "0 0" }, { rotation: (ln.chapter_no * 30) % 360, svgOrigin: "0 0", duration: 2.2, ease: "elastic.out(1,.45)" }, t0);
        tl.to(S.lp, { opacity: .32, duration: .6 }, t0 + 1.5);
      } else {
        tl.fromTo(S.blot, { scale: .02, svgOrigin: "0 0", opacity: .95 }, { scale: 1, svgOrigin: "0 0", opacity: .92, duration: 1.4, ease: "power3.out" }, t0 - .25);
        S.ripples.forEach((r, k) => tl.fromTo(r, { scale: .3, opacity: .7, svgOrigin: "0 0" }, { scale: 6 + k, opacity: 0, svgOrigin: "0 0", duration: 2.2, ease: "power2.out" }, t0 + k * .25));
        tl.to(S.blot, { scale: 1.06, duration: span, ease: "none" }, t0 + 1.2);
      }
      tl.fromTo(S.cap.querySelector(".sig-no"), { opacity: 0, letterSpacing: "0.8em" }, { opacity: 1, letterSpacing: "0.32em", duration: .9, ease: "power3.out" }, t0 + .4);
      tl.fromTo(S.cap.querySelector(".sig-title"), { opacity: 0, y: 26, filter: "blur(10px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.0, ease: "expo.out" }, t0 + .6);
    },
  };

  // ---- Dấu chân dọc tuyến bản đồ (hành hương): hiện dần theo nét tuyến ----
  const mapBase = visuals.map;
  visuals.map = {
    build(inner, ln, i, ctx) {
      mapBase.build(inner, ln, i, ctx);
      const S = inner._lf;
      S.steps = [];
      if (!ln.visual.footsteps) return;
      S.routes.forEach((p, k) => {
        if (!p) return;
        const len = p.getTotalLength(), n = Math.max(4, Math.floor(len / 30)), out = [];
        for (let j = 1; j < n; j++) {
          const a = p.getPointAtLength((j / n) * len), b = p.getPointAtLength(Math.min(len, (j / n) * len + 2));
          const ang = Math.atan2(b.y - a.y, b.x - a.x), side = j % 2 ? 1 : -1;
          const x = a.x + Math.cos(ang + Math.PI / 2) * 7 * side, y = a.y + Math.sin(ang + Math.PI / 2) * 7 * side;
          out.push(sv("ellipse", { cx: x, cy: y, rx: 5.5, ry: 3.2, class: "foot", transform: `rotate(${(ang * 180) / Math.PI} ${x} ${y})` }, p.parentNode));
        }
        p.classList.add("faint");
        S.steps[k] = out;
      });
    },
    enter(tl, inner, ln, ctx) {
      mapBase.enter(tl, inner, ln, ctx);
      const S = inner._lf;
      S.pins.forEach((P, k) => {
        const fs = S.steps[k];
        if (!fs) return;
        const t = when(ctx, P.p, ln.start + 1.6 + k * 1.2);
        tl.fromTo(fs, { opacity: 0 }, { opacity: 1, duration: .08, stagger: Math.min(.06, 1.2 / fs.length) }, t - 1.3);
      });
    },
  };


  /* ================= G: v3 (02/10/2026) -- nâng cấp cho F3/B3 =================
     Xu hướng motion 2026 cho kênh tài liệu: chất thủ công (nét vẽ tay "on twos", giấy,
     bút dạ Vox), hiện vật 2.5D (nét phác -> ảnh thật, hai lớp trôi lệch, vệt sáng xiên),
     bảng tra có "tìm năm sinh của bạn" (bảng lật số + vòng bút khoanh), thẻ giữ chân giữa video.
     Không đo toạ độ chữ lúc dựng (font nạp sau) -- nét đánh dấu là phần tử con của chữ. */
  const HAND = "'Patrick Hand', 'Be Vietnam Pro', cursive";
  const lerp = (a, b, t) => a + (b - a) * t;

  // ---- Bảng tra: bảng lật số tìm đúng năm sinh, vòng bút khoanh dòng, thẻ "dừng video" ----
  visuals.lookup = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-lk"); inner.appendChild(st);
      const box = el("div", "lk-tab"); st.appendChild(box);
      const cols = v.cols || [], W = v.widths || cols.map(() => 1), grid = W.map((w) => w + "fr").join(" ");
      const rows = v.rows || [];
      const rh = Math.min(74, Math.floor(600 / Math.max(1, rows.length + 1)));
      box.style.setProperty("--rh", rh + "px");
      const head = el("div", "lk-row head"); head.style.gridTemplateColumns = grid;
      cols.forEach((c) => head.appendChild(el("div", "c", esc(c)))); box.appendChild(head);
      const R = rows.map((r) => {
        const e = el("div", "lk-row"); e.style.gridTemplateColumns = grid;
        (r.cells || []).forEach((c, k) => {
          const cell = el("div", "c" + (k ? "" : " k"));
          const s = String(c);
          cell.appendChild(el("span", (/^(Không|—|-)$/i.test(s) ? "ok" : (r.bad || []).includes(k) ? "bad" : (r.good || []).includes(k) ? "good" : ""), esc(s)));
          e.appendChild(cell);
        });
        box.appendChild(e); return e;
      });
      // bảng lật số (split-flap): mỗi ô một trống số 0..9 cuộn tới chữ số đích
      const flap = el("div", "lk-flap"); st.appendChild(flap);
      flap.appendChild(el("div", "lk-flap-k", esc(v.flap_label || "NĂM SINH")));
      const digits = el("div", "lk-digits"); flap.appendChild(digits);
      const ND = Math.max(1, ...rows.map((r) => String((r.cells || [])[0] || "").replace(/\D/g, "").length));
      const drums = Array.from({ length: Math.min(4, ND) }, () => {
        const cell = el("div", "lk-d"), drum = el("div", "lk-drum");
        for (let n = 0; n < 20; n++) drum.appendChild(el("div", "n", String(n % 10)));
        cell.appendChild(drum); cell.appendChild(el("div", "lk-hinge")); digits.appendChild(cell); return drum;
      });
      const sub = el("div", "lk-sub"); flap.appendChild(sub);
      const note = el("div", "lk-note"); note.style.fontFamily = HAND; flap.appendChild(note);
      let chip = null;
      if (v.pause) {
        const [l1, l2] = String(v.pause.text || "DỪNG VIDEO · TÌM NĂM SINH CỦA BẠN").split(" · ");
        chip = el("div", "lk-chip"); chip.innerHTML = `<i class="pz"></i><b>${esc(l1)}<small>${esc(l2 || "")}</small></b><em>3</em>`;
        st.appendChild(chip);
      }
      // vòng bút khoanh: phần tử con của từng dòng (không đo toạ độ)
      const loops = (v.find || []).map((f, j) => sketchOn(R[f.row], "loop lk-loop", sketchLoop(50, 50, 49, 46, (ln.sentence_id || 1) * 7 + j)));
      inner._lk = { st, box, head, R, drums, sub, note, chip, loops, title: title(st, v.title, 150, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._lk, v = ln.visual, t0 = ln.start, rows = v.rows || [];
      if (S.title) tl.fromTo(S.title, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .5 }, t0 + .1);
      tl.fromTo(S.box, { opacity: 0, y: 30, rotationX: 18, transformPerspective: 1400 }, { opacity: 1, y: 0, rotationX: 0, duration: .8, ease: "power3.out" }, t0);
      tl.fromTo(S.head, { opacity: 0 }, { opacity: 1, duration: .4 }, t0 + .3);
      S.R.forEach((r, k) => tl.fromTo(r, { opacity: 0, x: -36 }, { opacity: 1, x: 0, duration: .35, ease: "power3.out" }, when(ctx, rows[k], t0 + .45 + k * .18)));
      tl.fromTo(S.st.querySelector(".lk-flap"), { opacity: 0, x: 60 }, { opacity: 1, x: 0, duration: .7, ease: "power3.out" }, t0 + .5);
      // trống số quay chầm chậm khi chưa tìm (đợi người xem)
      S.drums.forEach((d, k) => tl.fromTo(d, { yPercent: 0 }, { yPercent: -5 * (k + 1), duration: 1.2, ease: "power2.inOut" }, t0 + .7));
      let prev = null;
      (v.find || []).forEach((f, j) => {
        const t = when(ctx, f, t0 + 2 + j * 4), row = S.R[f.row], cells = (rows[f.row] || {}).cells || [];
        const yr = String(cells[0] || "").replace(/\D/g, "").padStart(S.drums.length, "0").slice(-S.drums.length);
        S.drums.forEach((d, k) => {
          const target = 10 + Number(yr[k]);   // lần cuộn thứ hai của dải 0..9 -> luôn cuộn xuôi
          tl.to(d, { yPercent: -(target / 20) * 100, duration: .9 + k * .18, ease: `steps(${8 + k * 3})` }, t - .4);
        });
        tl.set(S.sub, { textContent: [cells[1], cells[2]].filter(Boolean).join(" · ") }, t + .4);
        tl.fromTo(S.sub, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: .35 }, t + .45);
        if (f.note) {
          tl.set(S.note, { textContent: "→ " + f.note }, t + .9);
          tl.fromTo(S.note, { opacity: 0, clipPath: "inset(0% 100% 0% 0%)" }, { opacity: 1, clipPath: "inset(0% 0% 0% 0%)", duration: .7, ease: twos(.7) }, t + .95);
        }
        if (prev) { tl.to(prev.r, { scale: 1, boxShadow: "0 0 0 rgba(0,0,0,0)", duration: .3 }, t - .3); tl.to(prev.l.ownerSVGElement, { opacity: 0, duration: .25 }, t - .3); }
        tl.to(S.R.filter((r) => r !== row), { opacity: .38, duration: .35 }, t - .2);
        tl.to(row, { opacity: 1, scale: 1.045, boxShadow: "0 18px 40px rgba(0,0,0,.28)", zIndex: 3, duration: .4, ease: "back.out(2)" }, t - .2);
        tl.set(S.loops[j].ownerSVGElement, { opacity: 1 }, t);
        drawSketch(tl, S.loops[j], t + .1, .75);
        prev = { r: row, l: S.loops[j] };
      });
      if (S.chip) {
        const tp = when(ctx, v.pause, ctx.until - 4);
        tl.fromTo(S.chip, { opacity: 0, y: -20, scale: .9 }, { opacity: 1, y: 0, scale: 1, duration: .45, ease: "back.out(2)" }, tp);
        if (prev) tl.to(S.R, { opacity: 1, duration: .4 }, tp);
        const em = S.chip.querySelector("em");
        [3, 2, 1].forEach((n, k) => { tl.set(em, { textContent: String(n) }, tp + .2 + k); tl.fromTo(em, { scale: 1.5, opacity: .3 }, { scale: 1, opacity: 1, duration: .35 }, tp + .2 + k); });
        tl.fromTo(S.chip.querySelector(".pz"), { opacity: 1 }, { opacity: .35, duration: .5, yoyo: true, repeat: 5 }, tp + .2);
      }
    },
  };

  // ---- Trang kinh kiểu Vox: bút dạ quét sau chữ, vòng bút, gạch chân, ghi chú viết tay ----
  visuals.annot = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-an"); inner.appendChild(st);
      const desk = el("div", "an-desk"); st.appendChild(desk);
      const page = el("div", "an-page"); desk.appendChild(page);
      page.appendChild(el("div", "an-grain"));
      if (v.title) page.appendChild(el("div", "an-src", esc(v.title)));
      const lines = v.lines || [], marks = v.marks || [];
      const M = [];
      const LH = 74, top0 = 120;
      lines.forEach((text, li) => {
        const row = el("div", "an-line"); row.style.top = (top0 + li * LH) + "px"; page.appendChild(row);
        let rest = String(text);
        const mine = marks.map((m, j) => ({ m, j })).filter((x) => (x.m.line || 0) === li && rest.includes(x.m.phrase));
        mine.sort((a, b) => rest.indexOf(a.m.phrase) - rest.indexOf(b.m.phrase));
        mine.forEach(({ m, j }) => {
          const i0 = rest.indexOf(m.phrase);
          if (i0 > 0) row.appendChild(document.createTextNode(rest.slice(0, i0)));
          const span = el("span", "an-mk", esc(m.phrase)); row.appendChild(span);
          let ink = null;
          if ((m.kind || "hl") === "hl") ink = marker(span);
          else if (m.kind === "loop") ink = sketchOn(span, "loop", sketchLoop(50, 50, 48, 44, li * 13 + j));
          else ink = sketchOn(span, "under", sketchUnder(0, 100, 50, li * 17 + j));
          let note = null;
          if (m.note) {
            note = el("div", "an-note"); note.style.fontFamily = HAND;
            const ar = sv("svg", { class: "an-arrow", viewBox: "0 0 100 100", preserveAspectRatio: "none" }, note);
            sv("path", { d: "M96,30 C70,10 40,70 6,52 M6,52 L22,38 M6,52 L24,66", class: "lf-ink" }, ar);
            note.appendChild(el("span", "", esc(m.note)));
            span.appendChild(note);
          }
          M[j] = { span, ink, note, kind: m.kind || "hl", line: li };
          rest = rest.slice(i0 + m.phrase.length);
        });
        if (rest) row.appendChild(document.createTextNode(rest));
      });
      page.style.height = (top0 + lines.length * LH + 90) + "px";
      inner._an = { st, desk, page, M, LH, top0, n: lines.length };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._an, v = ln.visual, t0 = ln.start, marks = v.marks || [];
      tl.fromTo(S.page, { opacity: 0, y: 80, rotation: -4 }, { opacity: 1, y: 0, rotation: -1.2, duration: 1.0, ease: "power3.out" }, t0 - .2);
      tl.fromTo(S.page.querySelectorAll(".an-line"), { opacity: 0 }, { opacity: 1, duration: .3, stagger: .12 }, t0 + .3);
      tl.fromTo(S.desk, { scale: 1 }, { scale: 1.04, duration: Math.max(2, ctx.until - t0), ease: "none" }, t0);
      const pageH = S.top0 + S.n * S.LH + 90;
      marks.forEach((m, j) => {
        const M = S.M[j]; if (!M) return;
        const t = when(ctx, m, t0 + 1.2 + j * 1.6);
        // máy quay nghiêng về dòng đang đánh dấu (toạ độ dòng biết trước: top0 + li*LH)
        const yLine = S.top0 + M.line * S.LH + 30, dy = (pageH / 2 - yLine) * .35;
        tl.to(S.page, { y: dy, scale: 1.08, duration: .9, ease: "power2.inOut" }, t - .6);
        if (M.kind === "hl") sweep(tl, M.ink, t, .55);
        else { tl.set(M.ink.ownerSVGElement, { opacity: 1 }, t); drawSketch(tl, M.ink, t, .6); }
        tl.to(M.span, { color: "var(--an-hot)", duration: .3 }, t + .1);
        if (M.note) {
          tl.fromTo(M.note.querySelector(".an-arrow"), { clipPath: "inset(0% 0% 0% 100%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: .45, ease: twos(.45) }, t + .5);
          tl.fromTo(M.note.querySelector("span"), { opacity: 0, clipPath: "inset(0% 100% 0% 0%)" }, { opacity: 1, clipPath: "inset(0% 0% 0% 0%)", duration: .7, ease: twos(.7) }, t + .8);
        }
      });
      tl.to(S.page, { y: 0, scale: 1, duration: 1.2, ease: "power2.inOut" }, Math.max(t0 + 2, ctx.until - 1.6));
    },
  };

  // ---- Hiện vật 2.5D: nét viền tự vẽ -> nét phác -> ảnh thật; hai lớp trôi lệch; vệt sáng xiên ----
  visuals.relic = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-rl"); inner.appendChild(st);
      const k = Math.min(1920 / v.w, 960 / v.h) * .9, w = v.w * k, h = v.h * k;
      const cam = el("div", "rl-cam"); st.appendChild(cam);
      const box = el("div", "rl-box"); Object.assign(box.style, { width: w + "px", height: h + "px", left: (1920 - w) / 2 + "px", top: (1000 - h) / 2 - 10 + "px" });
      cam.appendChild(box);
      const bg = el("div", "rl-bg"); bg.style.backgroundImage = `url(${v.bg})`; box.appendChild(bg);
      const sk = el("div", "rl-sk"); const ink = el("div", "rl-ink");
      ink.style.webkitMaskImage = ink.style.maskImage = `url(${v.sketch})`; sk.appendChild(ink); box.appendChild(sk);
      const svg = sv("svg", { class: "rl-line", viewBox: `0 0 ${w} ${h}` }, box);
      const paths = (v.outline || []).map((poly) => sv("path", {
        d: "M" + poly.map(([x, y]) => `${(x * w).toFixed(1)},${(y * h).toFixed(1)}`).join(" L") + " Z", class: "rl-path" }, svg));
      const fg = el("div", "rl-fg"); fg.style.backgroundImage = `url(${v.fg})`; box.appendChild(fg);
      const lightWrap = el("div", "rl-lightwrap"); lightWrap.style.webkitMaskImage = lightWrap.style.maskImage = `url(${v.fg})`;
      const light = el("div", "rl-light"); lightWrap.appendChild(light); box.appendChild(lightWrap);
      st.appendChild(el("div", "rl-veil"));
      const layer = el("div", "rl-notes"); box.appendChild(layer);
      const notes = (v.notes || []).map((n, j) => {
        const g = el("div", "mus-note rl-note " + (n.side || (j % 2 ? "left" : "right")));
        Object.assign(g.style, { left: n.x * w + "px", top: n.y * h + "px" });
        g.appendChild(el("div", "dot")); g.appendChild(el("div", "ring")); g.appendChild(el("div", "lead"));
        const lab = el("div", "lab"); lab.appendChild(el("b", "", esc(n.label || ""))); if (n.sub) lab.appendChild(el("span", "", esc(n.sub)));
        g.appendChild(lab); layer.appendChild(g); return { g, n };
      });
      const plate = el("div", "mus-plate rl-plate"); plate.innerHTML = `<b>${esc(v.title || "")}</b><span>${esc(v.tag || "")}</span>`; st.appendChild(plate);
      inner._rl = { st, cam, box, bg, sk, ink, paths, fg, light, notes, plate, w, h, bx: (1920 - w) / 2, by: (1000 - h) / 2 - 10 };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._rl, t0 = ln.start, until = ctx.until, span = Math.max(4, until - t0);
      // 1) nét viền tự vẽ (nhảy nấc như tay vẽ)
      S.paths.forEach((p, k) => {
        const len = p.getTotalLength ? p.getTotalLength() : 4000;
        tl.set(p, { strokeDasharray: len, strokeDashoffset: len }, 0);
        tl.to(p, { strokeDashoffset: 0, duration: 1.5, ease: twos(1.5) }, t0 - .1 + k * .25);
      });
      // 2) nét phác lộ dần từ trên xuống (bút đi theo)
      tl.fromTo(S.sk, { clipPath: "inset(0% 0% 100% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 1.5, ease: twos(1.5) }, t0 + .5);
      // 3) ảnh thật hiện lên: nền trước, hiện vật sau; nét phác và viền lui xuống
      const tr = t0 + 2.1;
      tl.fromTo(S.bg, { opacity: 0 }, { opacity: 1, duration: 1.0 }, tr);
      tl.fromTo(S.fg, { opacity: 0, filter: "brightness(1.6) saturate(.2)" }, { opacity: 1, filter: "brightness(1) saturate(1)", duration: 1.2, ease: "power2.out" }, tr + .25);
      tl.to(S.sk, { opacity: 0, duration: .9 }, tr + .6);
      tl.to(S.paths, { opacity: 0, duration: 1.0 }, tr + .9);
      tl.fromTo(S.plate, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .6 }, tr + .8);
      // 4) chiều sâu: nền trôi chậm/ngược, hiện vật trôi nhanh hơn + đổ bóng
      tl.fromTo(S.bg, { x: 0, scale: 1.04 }, { x: -26, scale: 1.1, duration: span - 1.5, ease: "none" }, tr);
      tl.fromTo(S.fg, { x: 0, scale: 1 }, { x: 22, scale: 1.05, duration: span - 1.5, ease: "none" }, tr);
      // 5) vệt sáng xiên lướt qua bề mặt (chỉ trên hiện vật -- mặt nạ hình hiện vật)
      tl.fromTo(S.light, { xPercent: -140 }, { xPercent: 240, duration: 2.4, ease: "power1.inOut" }, tr + 1.2);
      // 6) chỉ dẫn: máy quay tiến vào từng điểm
      let prev = tr + 1.4;
      S.notes.forEach((N, j) => {
        const n = N.n, t = Math.max(prev + .8, when(ctx, n, prev + 2)), z = n.z || 1.6;
        const px = S.bx + n.x * S.w, py = S.by + n.y * S.h;
        tl.to(S.cam, { x: 960 - px * z, y: 500 - py * z, scale: z, transformOrigin: "0 0", duration: 1.1, ease: "power3.inOut" }, t - .7);
        if (j) tl.to(S.notes[j - 1].g, { opacity: 0, duration: .3 }, t - .7);
        tl.set(N.g, { opacity: 1 }, t + .3);
        tl.fromTo(N.g.querySelector(".dot"), { scale: 0 }, { scale: 1, duration: .3, ease: "back.out(3)" }, t + .35);
        tl.fromTo(N.g.querySelector(".ring"), { scale: .3, opacity: .9 }, { scale: 2.6, opacity: 0, duration: 1.1, repeat: 1 }, t + .4);
        tl.fromTo(N.g.querySelector(".lead"), { scaleX: 0 }, { scaleX: 1, duration: .4 }, t + .5);
        tl.fromTo(N.g.querySelector(".lab"), { opacity: 0, x: N.g.classList.contains("left") ? 30 : -30 }, { opacity: 1, x: 0, duration: .45, ease: "power3.out" }, t + .75);
        prev = t;
      });
      if (S.notes.length && until - 1.6 > prev + 1.5) {
        tl.to(S.notes[S.notes.length - 1].g, { opacity: 0, duration: .3 }, until - 1.8);
        tl.to(S.cam, { x: 0, y: 0, scale: 1, duration: 1.3, ease: "power2.inOut" }, until - 1.6);
      }
    },
  };

  // ---- Vòng 12 chi: tam hợp vẽ dần, nhóm cần nói sáng lên, cung Tam Tai ba năm ----
  const CHI_ELEM = { "Thân": "Thủy", "Tý": "Thủy", "Thìn": "Thủy", "Tỵ": "Kim", "Dậu": "Kim", "Sửu": "Kim",
                     "Dần": "Hỏa", "Ngọ": "Hỏa", "Tuất": "Hỏa", "Hợi": "Mộc", "Mão": "Mộc", "Mùi": "Mộc" };
  visuals.chiwheel = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-cw"); inner.appendChild(st);
      const svg = sv("svg", { class: "cw-svg", viewBox: "0 0 1920 1080" }, st);
      const C = { x: 700, y: 492, r: 270 };
      const pos = (c, r) => { const k = CHI.indexOf(c), A = k * Math.PI / 6 - Math.PI / 2; return [C.x + Math.cos(A) * (r || C.r), C.y + Math.sin(A) * (r || C.r)]; };
      const ring = sv("circle", { cx: C.x, cy: C.y, r: C.r, class: "cw-ring" }, svg);
      const ring2 = sv("circle", { cx: C.x, cy: C.y, r: C.r + 62, class: "cw-ring thin" }, svg);
      const tris = (v.groups || []).map((g) => {
        const col = ELEM_COLOR[CHI_ELEM[g[0]]] || css("--accent");
        return sv("path", { d: "M" + g.map((c) => pos(c).map((n) => n.toFixed(1)).join(",")).join(" L") + " Z", class: "cw-tri", stroke: col, fill: col }, svg);
      });
      const arcG = sv("g", { class: "cw-arc" }, svg);
      let arcPath = null, arcLabs = [];
      if (v.arc) {
        const a = v.arc, k0 = CHI.indexOf(a.from), n = a.n || 3, R = C.r + 62;
        const A0 = (k0 - .45) * Math.PI / 6 - Math.PI / 2, A1 = (k0 + n - 1 + .45) * Math.PI / 6 - Math.PI / 2;
        arcPath = sv("path", { d: `M${C.x + Math.cos(A0) * R},${C.y + Math.sin(A0) * R} A${R},${R} 0 0 1 ${C.x + Math.cos(A1) * R},${C.y + Math.sin(A1) * R}`, class: "cw-arcpath" }, arcG);
        arcLabs = (a.labels || []).map((t, j) => {
          const [x, y] = pos(CHI[(k0 + j) % 12], R + 46);
          const tx = sv("text", { x, y: y + 10, class: "cw-yr" + (j === n - 1 ? " last" : "") }, arcG); tx.textContent = t; return tx;
        });
      }
      const nodes = CHI.map((c) => {
        const [x, y] = pos(c), g = sv("g", { class: "cw-node" }, svg);
        sv("circle", { cx: x, cy: y, r: 42, class: "cw-dot" }, g);
        const tx = sv("text", { x, y: y + 13, class: "cw-chi" }, g); tx.textContent = c;
        return { c, g };
      });
      const legend = el("div", "cw-legend"); st.appendChild(legend);
      const items = (v.groups || []).map((g, j) => {
        const it = el("div", "cw-it"); it.style.setProperty("--el", ELEM_COLOR[CHI_ELEM[g[0]]] || css("--accent"));
        it.innerHTML = `<i></i><b>${esc(g.join(" · "))}</b><span>${esc((v.group_labels || [])[j] || "")}</span>`;
        legend.appendChild(it); return it;
      });
      const cap = v.arc && v.arc.label ? el("div", "cw-cap", esc(v.arc.label)) : null; if (cap) st.appendChild(cap);
      inner._cw = { svg, ring, ring2, tris, nodes, items, arcPath, arcLabs, cap, title: title(st, v.title, 150, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._cw, v = ln.visual, t0 = ln.start, steps = v.steps || [];
      if (S.title) tl.fromTo(S.title, { opacity: 0 }, { opacity: 1, duration: .5 }, t0 + .1);
      tl.fromTo([S.ring, S.ring2], { opacity: 0, scale: .85, svgOrigin: "700 492" }, { opacity: 1, scale: 1, svgOrigin: "700 492", duration: 1, ease: "power3.out" }, t0);
      tl.fromTo(S.nodes.map((n) => n.g), { opacity: 0, scale: .4, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: .35, stagger: .05, ease: "back.out(2)" }, t0 + .3);
      const gstep = (j) => steps.find((s) => s.group === j);
      S.tris.forEach((p, j) => {
        const t = when(ctx, gstep(j), t0 + 1.4 + j * .9);
        const len = p.getTotalLength ? p.getTotalLength() : 2000;
        tl.set(p, { strokeDasharray: len, strokeDashoffset: len, fillOpacity: 0 }, 0);
        tl.to(p, { strokeDashoffset: 0, duration: .8, ease: twos(.8) }, t);
        tl.to(p, { fillOpacity: .12, duration: .5 }, t + .7);
        tl.fromTo(S.items[j], { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: .45, ease: "power3.out" }, t + .2);
      });
      const fs = steps.find((s) => s.focus);
      if (fs && v.focus) {
        const t = when(ctx, fs, t0 + 5);
        const fi = (v.groups || []).findIndex((g) => g.join() === v.focus.join());
        S.tris.forEach((p, j) => tl.to(p, j === fi ? { fillOpacity: .32, strokeWidth: 9, duration: .5 } : { opacity: .18, duration: .5 }, t));
        S.items.forEach((it, j) => tl.to(it, j === fi ? { scale: 1.06, duration: .4 } : { opacity: .3, duration: .4 }, t));
        S.nodes.forEach((n) => tl.to(n.g, v.focus.includes(n.c) ? { scale: 1.18, duration: .4, ease: "back.out(2)" } : { opacity: .35, duration: .4 }, t));
      }
      const as = steps.find((s) => s.arc);
      if (as && S.arcPath) {
        const t = when(ctx, as, t0 + 7);
        const len = S.arcPath.getTotalLength ? S.arcPath.getTotalLength() : 1200;
        tl.set(S.arcPath, { strokeDasharray: len, strokeDashoffset: len }, 0);
        tl.to(S.arcPath, { strokeDashoffset: 0, duration: 1.0, ease: twos(1) }, t);
        S.arcLabs.forEach((tx, j) => tl.fromTo(tx, { opacity: 0, scale: .6, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: .35, ease: "back.out(2.4)" }, t + .3 + j * .35));
        if (S.arcLabs.length) tl.to(S.arcLabs[S.arcLabs.length - 1], { scale: 1.25, duration: .45, yoyo: true, repeat: 3, transformOrigin: "50% 50%" }, t + 1.6);
        if (S.cap) tl.fromTo(S.cap, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .5 }, t + .8);
      }
    },
  };

  // ---- Biểu đồ tròn nét cọ (chia phần): từng múi vẽ ra đúng lúc được nhắc ----
  visuals.pie = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-pie"); inner.appendChild(st);
      const svg = sv("svg", { class: "pie-svg", viewBox: "0 0 1920 1080" }, st);
      const defs = sv("defs", {}, svg);
      const f = sv("filter", { id: "brush" + ln.sentence_id, x: "-10%", y: "-10%", width: "120%", height: "120%" }, defs);
      sv("feTurbulence", { type: "fractalNoise", baseFrequency: ".035", numOctaves: 2, seed: ln.sentence_id % 53, result: "n" }, f);
      sv("feDisplacementMap", { in: "SourceGraphic", in2: "n", scale: 16 }, f);
      const C = { x: 640, y: 530, r: 250 }, parts = v.parts || [], tot = parts.reduce((s, p) => s + (p.value || 0), 0) || 1;
      sv("circle", { cx: C.x, cy: C.y, r: C.r, class: "pie-track" }, svg);
      let acc = 0;
      const pal = NIGHT() ? ["#e6b84a", "#6fa8e6", "#e0533d", "#5fae5a"] : ["#8c2f22", "#3f5d4a", "#b07a2a", "#4a4238"];
      const segs = parts.map((p, k) => {
        const a0 = acc / tot, a1 = (acc + p.value) / tot; acc += p.value;
        const A0 = a0 * Math.PI * 2 - Math.PI / 2 + .02, A1 = a1 * Math.PI * 2 - Math.PI / 2 - .02, big = (a1 - a0) > .5 ? 1 : 0;
        const d = `M${C.x + Math.cos(A0) * C.r},${C.y + Math.sin(A0) * C.r} A${C.r},${C.r} 0 ${big} 1 ${C.x + Math.cos(A1) * C.r},${C.y + Math.sin(A1) * C.r}`;
        const col = p.color || pal[k % pal.length];
        const path = sv("path", { d, class: "pie-seg", stroke: col, filter: `url(#brush${ln.sentence_id})` }, svg);
        const Am = (A0 + A1) / 2, lx = C.x + Math.cos(Am) * (C.r + 120), ly = C.y + Math.sin(Am) * (C.r + 120);
        const pct = sv("text", { x: C.x + Math.cos(Am) * C.r, y: C.y + Math.sin(Am) * C.r + 14, class: "pie-pct" }, svg); pct.textContent = Math.round(p.value / tot * 100) + "%";
        return { path, col, pct, lx, ly };
      });
      const center = el("div", "pie-center"); center.innerHTML = `<b>${esc((v.center || {}).t || "")}</b><span>${esc((v.center || {}).sub || "")}</span>`; st.appendChild(center);
      const legend = el("div", "pie-legend"); st.appendChild(legend);
      const items = parts.map((p, k) => {
        const it = el("div", "pie-it"); it.style.setProperty("--c", segs[k].col);
        it.innerHTML = `<em>${Math.round(p.value / tot * 4 * 10) / 10 === Math.round(p.value / tot * 4) ? Math.round(p.value / tot * 4) + "/4" : Math.round(p.value / tot * 100) + "%"}</em><b>${esc(p.label)}</b><span>${esc(p.sub || "")}</span>`;
        legend.appendChild(it); return it;
      });
      inner._pie = { segs, items, center, title: title(st, v.title, 150, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._pie, v = ln.visual, t0 = ln.start, parts = v.parts || [];
      if (S.title) tl.fromTo(S.title, { opacity: 0 }, { opacity: 1, duration: .5 }, t0 + .1);
      tl.fromTo(S.center, { opacity: 0, scale: .8 }, { opacity: 1, scale: 1, duration: .6, ease: "back.out(2)" }, t0 + .3);
      S.segs.forEach((s, k) => {
        const t = when(ctx, parts[k], t0 + .8 + k * 1.2);
        const len = s.path.getTotalLength ? s.path.getTotalLength() : 800;
        tl.set(s.path, { strokeDasharray: len, strokeDashoffset: len }, 0);
        tl.to(s.path, { strokeDashoffset: 0, duration: .9, ease: twos(.9) }, t);
        tl.fromTo(s.pct, { opacity: 0, scale: .5, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: .35, ease: "back.out(2.4)" }, t + .7);
        tl.fromTo(S.items[k], { opacity: 0, x: 50 }, { opacity: 1, x: 0, duration: .45, ease: "power3.out" }, t + .2);
      });
    },
  };

  // ---- Sáu phương (giả 3D): mặt đất elip bốn phương + trục trên/dưới ----
  const DIR_POS = { east: [1500, 540, 1], west: [420, 540, 1], north: [960, 396, .78], south: [960, 690, 1.1], up: [960, 178, .95], down: [960, 806, .9] };
  visuals.compass = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-cp"); inner.appendChild(st);
      const svg = sv("svg", { class: "cp-svg", viewBox: "0 0 1920 1080" }, st);
      const g0 = sv("g", { class: "cp-world" }, svg);
      const ground = sv("ellipse", { cx: 960, cy: 540, rx: 560, ry: 160, class: "cp-ground" }, g0);
      const ticks = [];
      for (let a = 0; a < 48; a++) { const A = a * Math.PI / 24, x1 = 960 + Math.cos(A) * 560, y1 = 540 + Math.sin(A) * 160, x2 = 960 + Math.cos(A) * (a % 4 ? 540 : 520), y2 = 540 + Math.sin(A) * (a % 4 ? 154 : 148);
        ticks.push(sv("line", { x1, y1, x2, y2, class: "cp-tick" }, g0)); }
      const axis = sv("line", { x1: 960, y1: 218, x2: 960, y2: 770, class: "cp-axis" }, g0);
      const center = sv("g", { class: "cp-center" }, g0);
      sv("circle", { cx: 960, cy: 540, r: 58, class: "cp-cdot" }, center);
      const ct = sv("text", { x: 960, y: 554, class: "cp-ctext" }, center); ct.textContent = v.center || "BẠN";
      const nodes = (v.dirs || []).map((d) => {
        const [x, y, s] = DIR_POS[d.dir] || [960, 600, 1];
        const spoke = sv("line", { x1: 960, y1: 540, x2: x, y2: y, class: "cp-spoke" }, g0);
        const g = sv("g", { class: "cp-node", transform: `translate(${x},${y}) scale(${s})` }, g0), inG = sv("g", {}, g);
        sv("circle", { r: 40, class: "cp-ndot" }, inG);
        const rip = sv("circle", { r: 40, class: "cp-rip" }, inG);
        const below = d.dir === "down" || d.dir === "south", side = d.dir === "east" ? 1 : d.dir === "west" ? -1 : 0;
        const lx = side ? side * 66 : 0, ly = side ? 12 : below ? 12 : -64, anchor = side > 0 ? "start" : side < 0 ? "end" : "middle";
        const t1 = sv("text", { x: below ? 66 : lx, y: below ? 2 : ly, class: "cp-lab", "text-anchor": below ? "start" : anchor }, inG); t1.textContent = d.label;
        const t2 = sv("text", { x: below ? 66 : lx, y: (below ? 2 : ly) + 40, class: "cp-sub", "text-anchor": below ? "start" : anchor }, inG); t2.textContent = d.sub || "";
        return { d, spoke, g: inG, rip };
      });
      inner._cp = { g0, ground, ticks, axis, center, nodes, title: title(st, v.title, 150, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._cp, v = ln.visual, t0 = ln.start, span = Math.max(3, ctx.until - t0);
      if (S.title) tl.fromTo(S.title, { opacity: 0 }, { opacity: 1, duration: .5 }, t0 + .1);
      const len = 2 * Math.PI * Math.sqrt((560 * 560 + 160 * 160) / 2);
      tl.set(S.ground, { strokeDasharray: len, strokeDashoffset: len }, 0);
      tl.to(S.ground, { strokeDashoffset: 0, duration: 1.2, ease: twos(1.2) }, t0);
      tl.fromTo(S.ticks, { opacity: 0 }, { opacity: 1, duration: .05, stagger: .015 }, t0 + .4);
      tl.fromTo(S.axis, { opacity: 0, scaleY: 0, svgOrigin: "960 540" }, { opacity: 1, scaleY: 1, svgOrigin: "960 540", duration: .8, ease: "power3.out" }, t0 + .6);
      tl.fromTo(S.center, { opacity: 0, scale: .4, svgOrigin: "960 540" }, { opacity: 1, scale: 1, svgOrigin: "960 540", duration: .5, ease: "back.out(2.4)" }, t0 + .8);
      tl.fromTo(S.g0, { scale: 1, svgOrigin: "960 560" }, { scale: 1.04, svgOrigin: "960 560", duration: span, ease: "none" }, t0);
      S.nodes.forEach((N, k) => {
        const t = when(ctx, N.d, t0 + 1.4 + k * .9);
        tl.fromTo(N.spoke, { opacity: 0 }, { opacity: 1, duration: .4 }, t - .1);
        tl.fromTo(N.g, { opacity: 0, scale: .3, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: .45, ease: "back.out(2.2)" }, t);
        tl.fromTo(N.rip, { scale: 1, opacity: .8, transformOrigin: "50% 50%" }, { scale: 2.6, opacity: 0, duration: 1.0, ease: "power2.out" }, t + .1);
      });
    },
  };

  // ---- Thẻ giữ chân giữa video: "phần tiếp theo" + câu hỏi treo + xương sống chương ----
  visuals.teaser = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-tz"); inner.appendChild(st);
      st.appendChild(el("div", "tz-k", esc(v.kicker || "PHẦN TIẾP THEO")));
      const nx = el("div", "tz-next"); st.appendChild(nx);
      const words = String(v.next || "").split(/\s+/).map((w) => { const s = el("span", "tz-w", esc(w)); nx.appendChild(s); nx.appendChild(document.createTextNode(" ")); return s; });
      const q = el("div", "tz-q", esc(v.q || "")); st.appendChild(q);
      const sp = el("div", "tz-spine"); st.appendChild(sp);
      const line = el("div", "tz-line"); sp.appendChild(line);
      const N = Math.max(2, v.total || 10), cur = Math.min(N, v.chap || 1);
      const dots = [];
      for (let k = 1; k <= N; k++) {
        const d = el("div", "tz-dot" + (k < cur ? " past" : k === cur ? " cur" : k === cur + 1 ? " next" : ""));
        d.style.left = ((k - 1) / (N - 1) * 100) + "%"; sp.appendChild(d); dots.push(d);
      }
      const lab = el("div", "tz-lab", `ĐANG Ở PHẦN ${cur}/${N}`); lab.style.left = ((cur - 1) / (N - 1) * 100) + "%"; sp.appendChild(lab);
      inner._tz = { st, words, q, line, dots, lab, cur };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._tz, t0 = ln.start;
      tl.fromTo(S.st.querySelector(".tz-k"), { opacity: 0, letterSpacing: "0.9em" }, { opacity: 1, letterSpacing: "0.34em", duration: .8, ease: "power3.out" }, t0);
      tl.fromTo(S.words, { opacity: 0, y: 50, rotationX: -70, transformPerspective: 900 }, { opacity: 1, y: 0, rotationX: 0, duration: .55, stagger: .08, ease: "back.out(1.6)" }, t0 + .25);
      tl.fromTo(S.line, { scaleX: 0, transformOrigin: "0% 50%" }, { scaleX: 1, duration: .9, ease: "power2.inOut" }, t0 + .4);
      tl.fromTo(S.dots, { scale: 0 }, { scale: 1, duration: .25, stagger: .05, ease: "back.out(2)" }, t0 + .5);
      tl.fromTo(S.lab, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: .4 }, t0 + 1.1);
      const nxt = S.dots[S.cur];
      if (nxt) tl.fromTo(nxt, { boxShadow: "0 0 0 0 var(--accent)" }, { boxShadow: "0 0 0 18px rgba(0,0,0,0)", duration: .9, repeat: 3, ease: "power2.out" }, t0 + 1.2);
      tl.fromTo(S.q, { opacity: 0, y: 16, filter: "blur(8px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: .8, ease: "expo.out" }, when(ctx, ln.visual.q_at || {}, t0 + 1.4));
    },
  };


  /* ================= H: v4 (02/10/2026) -- kể chuyện đa dạng, không liệt kê 1-2-3 =================
     Phản hồi người dùng: v3 hay nhưng motif lặp (liệt kê, nền xanh). Bộ cảnh này đi cùng các
     cách kể mới: GIẢI MÃ (bảng ghim manh mối), ĐÚNG/SAI (dấu mộc), HÀNH TRÌNH (đối thoại, gió),
     cùng hai skin mới (sơn mài, trăng thiền) chọn qua biến CSS --lf-skin. */
  const skin = () => (css("--lf-skin") || "").replace(/["'\s]/g, "");

  // ---- Bảng ghim manh mối (GIẢI MÃ): thẻ ghim lên bảng, dây đỏ nối dần, lời giải bật ra ở giữa ----
  const CLUE_SLOTS = [[340, 310], [900, 260], [1480, 320], [470, 660], [1350, 670], [1700, 500]];
  visuals.clues = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-cl"); inner.appendChild(st);
      st.appendChild(el("div", "cl-board"));
      const svg = sv("svg", { class: "cl-strings", viewBox: "0 0 1920 1080" }, st);
      const j = jitter((ln.sentence_id || 1) * 31);
      const cards = (v.cards || []).slice(0, 6).map((c, k) => {
        const [x, y] = CLUE_SLOTS[k];
        const card = el("div", "cl-card" + (c.img ? " photo" : ""));
        Object.assign(card.style, { left: x - 200 + "px", top: y - 105 + "px" });
        card.style.setProperty("--rot", (j() * 9).toFixed(1) + "deg");
        if (c.img) { const ph = el("div", "cl-ph"); ph.style.backgroundImage = `url(${c.img})`; card.appendChild(ph); }
        const tx = el("div", "cl-tx", esc(c.text)); tx.style.fontFamily = HAND; card.appendChild(tx);
        if (c.sub) card.appendChild(el("div", "cl-sub", esc(c.sub)));
        card.appendChild(el("div", "cl-pin"));
        st.appendChild(card);
        return { card, x, y };
      });
      const lines = (v.links || []).map((L) => {
        const A = cards[L.a], B = cards[L.b]; if (!A || !B) return null;
        const mx = (A.x + B.x) / 2, my = (A.y + B.y) / 2 + 40;
        return sv("path", { d: `M${A.x},${A.y - 80} Q${mx},${my} ${B.x},${B.y - 80}`, class: "cl-str" }, svg);
      });
      let ans = null;
      if (v.answer) {
        ans = el("div", "cl-ans"); ans.innerHTML = `<b>${esc(v.answer.text)}</b><span>${esc(v.answer.sub || "")}</span>`; st.appendChild(ans);
        (v.answer.from || []).forEach((k) => { const A = cards[k]; if (A) lines.push(sv("path", { d: `M${A.x},${A.y - 80} L960,470`, class: "cl-str ans" }, svg)); });
      }
      inner._cl = { cards, lines, ans, title: title(st, v.title, 150, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._cl, v = ln.visual, t0 = ln.start;
      if (S.title) tl.fromTo(S.title, { opacity: 0 }, { opacity: 1, duration: .5 }, t0 + .1);
      S.cards.forEach((C, k) => {
        const t = when(ctx, (v.cards || [])[k], t0 + .4 + k * 1.2);
        tl.fromTo(C.card, { opacity: 0, y: -60, rotation: "+=14", scale: 1.15 }, { opacity: 1, y: 0, rotation: "-=14", scale: 1, duration: .45, ease: "back.out(1.6)" }, t);
        tl.fromTo(C.card.querySelector(".cl-pin"), { scale: 0 }, { scale: 1, duration: .25, ease: "back.out(3)" }, t + .35);
      });
      S.lines.forEach((p, k) => {
        if (!p) return;
        const L = (v.links || [])[k];
        const len = p.getTotalLength ? p.getTotalLength() : 600;
        tl.set(p, { strokeDasharray: len, strokeDashoffset: len }, 0);
        const t = L ? when(ctx, L, t0 + 2 + k) : when(ctx, v.answer, ctx.until - 2.5) - .4;
        tl.to(p, { strokeDashoffset: 0, duration: .7, ease: twos(.7) }, t);
      });
      if (S.ans) {
        const t = when(ctx, v.answer, ctx.until - 2.5);
        tl.to(S.cards.map((c) => c.card), { opacity: .55, duration: .4 }, t);
        tl.fromTo(S.ans, { opacity: 0, scale: .4, rotation: -8 }, { opacity: 1, scale: 1, rotation: -2, duration: .55, ease: "back.out(2)" }, t + .2);
      }
    },
  };

  // ---- Dấu mộc ĐÚNG / SAI / CÒN TÙY: niềm tin phổ biến bị "đóng dấu", lý do hiện sau ----
  const STAMP = { dung: ["ĐÚNG", "ok"], sai: ["SAI", "no"], tuy: ["CÒN TÙY", "mid"] };
  visuals.stamp = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-sp"); inner.appendChild(st);
      const card = el("div", "sp-card"); st.appendChild(card);
      card.appendChild(el("div", "sp-k", esc(v.kicker || "NIỀM TIN PHỔ BIẾN")));
      card.appendChild(el("div", "sp-claim", "“" + esc(v.claim || "") + "”"));
      const [txt, cls] = STAMP[v.verdict] || STAMP.tuy;
      const stamp = el("div", "sp-stamp " + cls, txt); st.appendChild(stamp);
      const note = el("div", "sp-note"); note.innerHTML = esc(v.note || ""); st.appendChild(note);
      inner._sp = { card, stamp, note };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._sp, v = ln.visual, t0 = ln.start;
      tl.fromTo(S.card, { opacity: 0, y: 40, rotation: -2 }, { opacity: 1, y: 0, rotation: -1, duration: .7, ease: "power3.out" }, t0);
      tl.fromTo(S.card.querySelector(".sp-claim"), { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 1.2, ease: "power1.inOut" }, t0 + .3);
      const t = when(ctx, v, t0 + 2.2);
      tl.fromTo(S.stamp, { opacity: 0, scale: 2.6, rotation: -24 }, { opacity: 1, scale: 1, rotation: -12, duration: .22, ease: "power4.in" }, t);
      tl.fromTo(S.card, { x: 0 }, { x: 8, duration: .05, yoyo: true, repeat: 5 }, t + .22);
      tl.fromTo(S.note, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .6, ease: "power3.out" }, when(ctx, v.note_at || {}, t + .9));
    },
  };

  // ---- Cuộn thư pháp: cuộn mở từ giữa ra, chữ hiện từng dòng, ấn son cuối ----
  visuals.scroll = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-sc"); inner.appendChild(st);
      const roll = el("div", "sc-roll"); st.appendChild(roll);
      // chiều cao cuộn theo số dòng (2 dòng không để trống cả cuộn), canh giữa vùng trên phụ đề
      const H = Math.min(820, 300 + (v.lines || []).length * 70 + (v.source ? 50 : 0));
      Object.assign(roll.style, { height: H + "px", top: Math.max(60, 470 - H / 2) + "px" });
      const paper = el("div", "sc-paper"); roll.appendChild(paper);
      const rodT = el("div", "sc-rod top"), rodB = el("div", "sc-rod bot"); roll.appendChild(rodT); roll.appendChild(rodB);
      const L = (v.lines || []).map((t) => { const d = el("div", "sc-line", esc(t)); paper.appendChild(d); return d; });
      if (v.source) paper.appendChild(el("div", "sc-src", esc(v.source)));
      const seal = el("div", "sc-seal", esc(v.seal || "法")); paper.appendChild(seal);
      inner._sc = { roll, paper, rodT, rodB, L, seal, H };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._sc, v = ln.visual, t0 = ln.start, span = Math.max(3, ctx.until - t0);
      tl.fromTo(S.paper, { clipPath: "inset(50% 0% 50% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 1.3, ease: "power2.inOut" }, t0 - .1);
      tl.fromTo(S.rodT, { y: S.H / 2 - 20 }, { y: 0, duration: 1.3, ease: "power2.inOut" }, t0 - .1);
      tl.fromTo(S.rodB, { y: -(S.H / 2 - 20) }, { y: 0, duration: 1.3, ease: "power2.inOut" }, t0 - .1);
      const each = Math.max(.6, Math.min(2.2, (span - 2.5) / Math.max(1, S.L.length)));
      S.L.forEach((d, k) => tl.fromTo(d, { opacity: 0, y: 14, filter: "blur(6px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: .7 },
        when(ctx, (v.steps || [])[k], t0 + 1.2 + k * each)));
      tl.fromTo(S.seal, { opacity: 0, scale: 1.8, rotation: 8 }, { opacity: .95, scale: 1, rotation: 0, duration: .25, ease: "power4.in" }, ctx.until - 1.4);
      tl.fromTo(S.roll, { scale: 1 }, { scale: 1.03, duration: span, ease: "none" }, t0);
    },
  };

  // ---- Đối thoại hai nhân vật (câu chuyện minh hoạ): bong bóng hiện dần, ba chấm "đang nói" trước ----
  function avatar(parent, side, name, sub) {
    const a = el("div", "dl-av " + side);
    const s = sv("svg", { viewBox: "0 0 120 120", class: "dl-face" }, a);
    sv("circle", { cx: 60, cy: 44, r: 24, class: "dl-head" }, s);
    sv("path", { d: "M18,118 C22,84 98,84 102,118 Z", class: "dl-body" }, s);
    a.appendChild(el("b", "", esc(name || ""))); if (sub) a.appendChild(el("span", "", esc(sub)));
    parent.appendChild(a); return a;
  }
  visuals.dialog = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-dl"); inner.appendChild(st);
      const L = avatar(st, "left", (v.left || {}).name, (v.left || {}).sub), R = avatar(st, "right", (v.right || {}).name, (v.right || {}).sub);
      const col = el("div", "dl-col"); st.appendChild(col);
      const bubbles = (v.turns || []).map((t) => {
        const b = el("div", "dl-b " + (t.who === "right" ? "right" : "left"));
        const dots = el("div", "dl-dots"); dots.innerHTML = "<i></i><i></i><i></i>"; b.appendChild(dots);   // el() gán textContent -> hiện nguyên thẻ
        b.appendChild(el("div", "dl-tx", esc(t.text)));
        col.appendChild(b); return b;
      });
      if (v.note) st.appendChild(el("div", "dl-note", esc(v.note)));
      inner._dl = { L, R, bubbles, title: title(st, v.title, 150, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._dl, v = ln.visual, t0 = ln.start, turns = v.turns || [];
      if (S.title) tl.fromTo(S.title, { opacity: 0 }, { opacity: 1, duration: .5 }, t0 + .1);
      tl.fromTo([S.L, S.R], { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: .6, stagger: .15, ease: "power3.out" }, t0);
      const ROW = 150;
      S.bubbles.forEach((b, k) => {
        const t = when(ctx, turns[k], t0 + .8 + k * 2.5);
        const av = turns[k].who === "right" ? S.R : S.L;
        tl.set(b, { y: k * ROW }, 0);
        tl.fromTo(b, { opacity: 0, scale: .6 }, { opacity: 1, scale: 1, duration: .3, ease: "back.out(2)" }, t - .5);
        tl.fromTo(b.querySelector(".dl-dots"), { opacity: 1 }, { opacity: 0, duration: .15 }, t - .05);
        tl.fromTo(b.querySelector(".dl-tx"), { opacity: 0 }, { opacity: 1, duration: .3 }, t);
        tl.fromTo(av, { scale: 1 }, { scale: 1.08, duration: .25, yoyo: true, repeat: 1, ease: "sine.inOut" }, t);
        if (k >= 3) {   // giữ tối đa 3 bong bóng: cả cột trượt lên
          tl.to(S.bubbles.slice(0, k + 1), { y: `-=${ROW}`, duration: .45, ease: "power2.inOut" }, t - .55);
          tl.to(S.bubbles[k - 3], { opacity: 0, duration: .3 }, t - .55);
        }
      });
    },
  };

  // ---- Tám ngọn gió: lá bay theo từng cơn gió, cặp chữ đối nhau sáng lên quanh ngọn đèn đứng yên ----
  visuals.wind = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-wd"); inner.appendChild(st);
      const svg = sv("svg", { class: "wd-svg", viewBox: "0 0 1920 1080" }, st);
      const r = HF.rng(HF.hashSeed("wind|" + ln.sentence_id));
      const leaves = [];
      for (let k = 0; k < 46; k++) {
        const g = sv("g", { transform: `translate(${(r() * 2200 - 140).toFixed(0)},${(120 + r() * 760).toFixed(0)})` }, svg), inG = sv("g", {}, g);
        sv("path", { d: "M0,-14 C10,-6 10,6 0,14 C-10,6 -10,-6 0,-14 Z", class: "wd-leaf", transform: `rotate(${(r() * 360).toFixed(0)}) scale(${(.6 + r() * .9).toFixed(2)})` }, inG);
        leaves.push({ g: inG, k });
      }
      const C = { x: 960, y: 500 }, R = 290, pairs = v.pairs || [];
      const ringC = sv("circle", { cx: C.x, cy: C.y, r: R, class: "wd-ring" }, svg);
      const lamp = sv("g", { class: "wd-lamp", transform: `translate(${C.x},${C.y}) scale(1.7) translate(${-C.x},${-C.y})` }, svg);
      sv("path", { d: `M${C.x - 46},${C.y + 40} Q${C.x},${C.y + 74} ${C.x + 46},${C.y + 40} Z`, class: "wd-bowl" }, lamp);
      const flame = sv("path", { d: `M${C.x},${C.y - 40} C${C.x + 18},${C.y - 6} ${C.x + 14},${C.y + 30} ${C.x},${C.y + 34} C${C.x - 14},${C.y + 30} ${C.x - 18},${C.y - 6} ${C.x},${C.y - 40} Z`, class: "wd-flame" }, lamp);
      const halo = sv("circle", { cx: C.x, cy: C.y, r: 90, class: "wd-halo" }, svg);
      const words = [];
      pairs.forEach((p, k) => {
        [0, 1].forEach((s) => {
          const A = (k / pairs.length) * Math.PI + s * Math.PI - Math.PI / 2 + (pairs.length > 2 ? 0 : 0);
          const x = C.x + Math.cos(A) * (R + 170), y = C.y + Math.sin(A) * (R + 10) + 14;   // elip dẹt: chữ không chạm mép trên/phụ đề
          const t = sv("text", { x, y, class: "wd-w" + (s ? " neg" : "") }, svg); t.textContent = p[s]; words.push({ t, k });
        });
      });
      inner._wd = { leaves, ringC, flame, halo, words, title: title(st, v.title, 150, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._wd, v = ln.visual, t0 = ln.start, span = Math.max(3, ctx.until - t0);
      if (S.title) tl.fromTo(S.title, { opacity: 0 }, { opacity: 1, duration: .5 }, t0 + .1);
      tl.fromTo(S.ringC, { opacity: 0, scale: .8, svgOrigin: "960 500" }, { opacity: 1, scale: 1, svgOrigin: "960 500", duration: 1, ease: "power3.out" }, t0);
      tl.fromTo(S.halo, { opacity: .15, scale: .9, svgOrigin: "960 500" }, { opacity: .35, scale: 1.08, svgOrigin: "960 500", duration: 2.2, yoyo: true, repeat: Math.floor(span / 2.2), ease: "sine.inOut" }, t0);
      // lá trôi nhẹ suốt cảnh
      S.leaves.forEach((L, i) => tl.fromTo(L.g, { x: 0, y: 0, rotation: 0 }, { x: 160 + (i % 7) * 40, y: (i % 2 ? -1 : 1) * (30 + (i % 5) * 12), rotation: 90 + (i % 5) * 40,
        svgOrigin: "0 0", duration: span, ease: "none" }, t0));
      (v.steps || []).forEach((stp, j) => {
        const t = when(ctx, stp, t0 + 1.4 + j * 2.4);
        // cơn gió: lá vụt qua, ngọn lửa nghiêng rồi đứng lại
        S.leaves.forEach((L, i) => { if (i % 3 === j % 3) tl.to(L.g, { x: "+=520", y: "-=60", rotation: "+=220", svgOrigin: "0 0", duration: 1.1, ease: "power2.out" }, t - .3 + (i % 5) * .04); });
        tl.to(S.flame, { skewX: -14, svgOrigin: "960 534", duration: .35, yoyo: true, repeat: 1, ease: "sine.inOut" }, t - .2);
        S.words.filter((w) => w.k === stp.pair).forEach((w, s) => {
          tl.fromTo(w.t, { opacity: 0, x: -120, filter: "blur(8px)" }, { opacity: 1, x: 0, filter: "blur(0px)", duration: .6, ease: "power3.out" }, t + s * .45);
        });
      });
    },
  };

  // ---- La bàn bát trạch: 8 hướng + quái, tô nhóm Đông tứ / Tây tứ, đánh dấu cung phi ----
  const BAGUA = [["Bắc", "Khảm", "dong"], ["Đông Bắc", "Cấn", "tay"], ["Đông", "Chấn", "dong"], ["Đông Nam", "Tốn", "dong"],
                 ["Nam", "Ly", "dong"], ["Tây Nam", "Khôn", "tay"], ["Tây", "Đoài", "tay"], ["Tây Bắc", "Càn", "tay"]];
  const STAR_GOOD = new Set(["Sinh Khí", "Thiên Y", "Diên Niên", "Phục Vị"]);
  visuals.bagua = {
    build(inner, ln) {
      const v = ln.visual, st = el("div", "lf-stage lf-bg8"); inner.appendChild(st);
      const svg = sv("svg", { class: "bg8-svg", viewBox: "0 0 1920 1080" }, st);
      const C = { x: 700, y: 490 }, R1 = 150, R2 = 360;
      const secs = BAGUA.map(([dir, gua, grp], k) => {
        const a0 = (k - .5) * Math.PI / 4 - Math.PI / 2, a1 = (k + .5) * Math.PI / 4 - Math.PI / 2;
        const p = (r, a) => `${(C.x + Math.cos(a) * r).toFixed(1)},${(C.y + Math.sin(a) * r).toFixed(1)}`;
        const path = sv("path", { d: `M${p(R1, a0)} L${p(R2, a0)} L${p(R2, a1)} L${p(R1, a1)} Z`, class: "bg8-sec " + grp }, svg);
        const am = k * Math.PI / 4 - Math.PI / 2;
        const g1 = sv("text", { x: C.x + Math.cos(am) * 255, y: C.y + Math.sin(am) * 255 + 4, class: "bg8-gua" }, svg); g1.textContent = gua;
        const d1 = sv("text", { x: C.x + Math.cos(am) * 412, y: C.y + Math.sin(am) * 412 + 10, class: "bg8-dir" }, svg); d1.textContent = dir;
        // sao du niên của hướng này (theo cung người xem): tên + tốt/xấu, hiện ở bước "stars"
        let star = null;
        const sname = (v.stars || {})[dir];
        if (sname) { star = sv("text", { x: C.x + Math.cos(am) * 255, y: C.y + Math.sin(am) * 255 + 38, class: "bg8-star " + (STAR_GOOD.has(sname) ? "good" : "bad") }, svg); star.textContent = sname; }
        return { path, grp, gua, am, dir, star };
      });
      sv("circle", { cx: C.x, cy: C.y, r: R1, class: "bg8-core" }, svg);
      const ctext = sv("text", { x: C.x, y: C.y + 12, class: "bg8-ct" }, svg); ctext.textContent = v.center || "NHÀ";
      const legend = el("div", "bg8-leg"); st.appendChild(legend);
      const items = ["dong", "tay"].map((g) => {
        const it = el("div", "bg8-it " + g); const names = BAGUA.filter((b) => b[2] === g);
        it.innerHTML = `<b>${g === "dong" ? "ĐÔNG TỨ TRẠCH" : "TÂY TỨ TRẠCH"}</b><span>${names.map((b) => b[0]).join(" · ")}</span><em>${names.map((b) => b[1]).join(" · ")}</em>`;
        legend.appendChild(it); return it;
      });
      let marker = null;
      if (v.marker) {
        const s = secs.find((x) => x.gua === v.marker.cung);
        if (s) { marker = sv("g", { class: "bg8-mk" }, svg);
          const mx = C.x + Math.cos(s.am) * 255, my = C.y + Math.sin(s.am) * 255;
          sv("circle", { cx: mx, cy: my, r: 58, class: "bg8-mkc" }, marker);
          const lbl = el("div", "bg8-mkl"); lbl.innerHTML = `<b>${esc(v.marker.label || "")}</b><span>CUNG ${esc(v.marker.cung.toUpperCase())}</span>`; st.appendChild(lbl);
          marker._lbl = lbl; }
      }
      inner._bg = { secs, items, marker, svg, title: title(st, v.title, 150, 124) };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._bg, v = ln.visual, t0 = ln.start;
      if (S.title) tl.fromTo(S.title, { opacity: 0 }, { opacity: 1, duration: .5 }, t0 + .1);
      tl.fromTo(S.svg, { rotation: -60, opacity: 0, transformOrigin: "36.5% 45.4%" }, { rotation: 0, opacity: 1, duration: 1.4, ease: "expo.out" }, t0 - .2);
      (v.steps || []).forEach((stp, j) => {
        const t = when(ctx, stp, t0 + 1.5 + j * 2);
        if (stp.show === "dong" || stp.show === "tay") {
          tl.to(S.secs.filter((s) => s.grp === stp.show).map((s) => s.path), { fillOpacity: .55, duration: .5, stagger: .12 }, t);
          tl.to(S.secs.filter((s) => s.grp !== stp.show).map((s) => s.path), { fillOpacity: .06, duration: .4 }, t);
          tl.fromTo(S.items[stp.show === "dong" ? 0 : 1], { opacity: 0, x: 40 }, { opacity: 1, x: 0, duration: .5 }, t + .2);
        } else if (stp.show === "stars" || stp.show === "good" || stp.show === "bad") {
          const want = (sec) => sec.star && (stp.show === "stars" || (stp.show === "good") === STAR_GOOD.has(sec.star.textContent));
          const on = S.secs.filter(want);
          tl.to(S.secs.map((x) => x.path), { fillOpacity: .08, duration: .3 }, t);
          on.forEach((x, i) => {
            tl.set(x.path, { fill: STAR_GOOD.has(x.star.textContent) ? css("--bg8-dong") : "#c0392b" }, t + i * .18);
            tl.to(x.path, { fillOpacity: .55, duration: .4 }, t + i * .18);
            tl.fromTo(x.star, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: .35 }, t + i * .18);
          });
        } else if (stp.show === "marker" && S.marker) {
          tl.fromTo(S.marker, { opacity: 0, scale: .3, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: .45, ease: "back.out(2.4)" }, t);
          tl.fromTo(S.marker._lbl, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: .5 }, t + .3);
        }
      });
    },
  };

  // ---- Mở chương theo skin: cửa sơn mài mở ra (lacquer) / trăng lên qua sương (moon) ----
  const sigBase = signatureChapter;
  signatureChapter = {
    build(inner, ln, i, ctx) {
      const sk = skin();
      if (!["lacquer", "moon", "dongho", "ember"].includes(sk)) return sigBase.build(inner, ln, i, ctx);
      const t = clean((ln.key_parts || []).map((p) => p.t).join(" ") || "");
      const st = el("div", "lf-stage sig sig-" + sk); inner.appendChild(st);
      const S = { st, sk };
      if (sk === "lacquer") {
        S.inside = el("div", "sl-inside"); st.appendChild(S.inside);
        S.L = el("div", "sl-door left"); S.R = el("div", "sl-door right"); st.appendChild(S.L); st.appendChild(S.R);
        [S.L, S.R].forEach((d) => { for (let k = 0; k < 3; k++) d.appendChild(el("div", "sl-stud")); d.appendChild(el("div", "sl-ring")); });
      } else if (sk === "dongho") {
        // bản khắc gỗ ép xuống tờ giấy điệp rồi nhấc lên: tên chương còn lại như vừa in
        S.block = el("div", "sd-block"); st.appendChild(S.block);
        S.flowers = [0, 1, 2, 3].map((k) => { const f = el("div", "sd-flower f" + k); st.appendChild(f); return f; });
      } else if (sk === "ember") {
        // hòn than đỏ rực nguội dần thành ánh trắng; tàn lửa bắn lên
        S.coal = el("div", "se-coal"); st.appendChild(S.coal);
        S.sp = [0, 1, 2, 3, 4, 5, 6, 7].map((k) => { const d = el("div", "se-sp"); d.style.left = (956 + (k - 3.5) * 34) + "px"; st.appendChild(d); return d; });
      } else {
        S.moon = el("div", "sm-moon"); st.appendChild(S.moon);
        S.mist = [0, 1, 2].map((k) => { const m = el("div", "sm-mist m" + k); st.appendChild(m); return m; });
      }
      const cap = el("div", "sig-cap"); cap.appendChild(el("div", "sig-no", "PHẦN " + String(ln.chapter_no).padStart(2, "0"))); cap.appendChild(el("div", "sig-title" + (t.length > 30 ? " long" : ""), esc(t)));
      st.appendChild(cap); S.cap = cap;
      inner._sig2 = S;
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._sig2;
      if (!S) return sigBase.enter(tl, inner, ln, ctx);
      const t0 = ln.start, span = Math.max(1.8, ln.end - t0);
      if (S.sk === "lacquer") {
        tl.fromTo(S.L, { rotationY: 0, transformPerspective: 1800, transformOrigin: "0% 50%" }, { rotationY: -96, duration: 1.6, ease: "power3.inOut" }, t0 + .2);
        tl.fromTo(S.R, { rotationY: 0, transformPerspective: 1800, transformOrigin: "100% 50%" }, { rotationY: 96, duration: 1.6, ease: "power3.inOut" }, t0 + .2);
        tl.fromTo(S.inside, { opacity: .4, scale: 1.1 }, { opacity: 1, scale: 1, duration: 2, ease: "power2.out" }, t0 + .3);
      } else if (S.sk === "dongho") {
        tl.fromTo(S.block, { y: -1100 }, { y: 0, duration: .55, ease: "power3.in" }, t0);
        tl.to(S.block, { y: -1100, duration: .8, ease: "power2.inOut" }, t0 + .75);
        S.flowers.forEach((f, k) => tl.fromTo(f, { scale: 0, rotation: -45 }, { scale: 1, rotation: 0, duration: .5, ease: "back.out(2)" }, t0 + .9 + k * .1));
      } else if (S.sk === "ember") {
        tl.fromTo(S.coal, { scale: .4, opacity: 0, background: "radial-gradient(circle at 45% 40%, #fff1c9 0%, #ff8a3d 45%, #8a1e0c 100%)" },
          { scale: 1, opacity: 1, duration: .9, ease: "power2.out" }, t0 - .1);
        tl.to(S.coal, { background: "radial-gradient(circle at 45% 40%, #ffffff 0%, #f6e7d6 45%, #8a6a58 100%)", opacity: .5, duration: Math.min(3, span), ease: "sine.inOut" }, t0 + .9);
        S.sp.forEach((d, k) => tl.fromTo(d, { y: 0, x: 0, opacity: .95 }, { y: -320 - (k % 3) * 90, x: (k - 3.5) * 22, opacity: 0, duration: 1.6, ease: "power2.out" }, t0 + .2 + k * .06));
      } else {
        tl.fromTo(S.moon, { y: 260, opacity: 0 }, { y: 0, opacity: 1, duration: 2.2, ease: "power2.out" }, t0 - .2);
        // trăng nền của skin tạm lặn khi trăng mở chương mọc (không để hai mặt trăng cùng lúc)
        if (document.getElementById("moon")) { tl.to("#moon", { opacity: 0, duration: .4 }, t0 - .3); tl.to("#moon", { opacity: .55, duration: 1.2 }, ln.end + 1.6); }
        S.mist.forEach((m, k) => tl.fromTo(m, { x: k % 2 ? 200 : -200, opacity: 0 }, { x: k % 2 ? -160 : 160, opacity: .8, duration: span + 1.5, ease: "none" }, t0 - .3));
      }
      tl.fromTo(S.cap.querySelector(".sig-no"), { opacity: 0, letterSpacing: "0.8em" }, { opacity: 1, letterSpacing: "0.32em", duration: .9, ease: "power3.out" }, t0 + .7);
      tl.fromTo(S.cap.querySelector(".sig-title"), { opacity: 0, y: 26, filter: "blur(10px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 1.0, ease: "expo.out" }, t0 + .9);
    },
  };

  window.HF_LONG = PORTRAIT
    ? { layouts: {}, visuals, chapter, begin, pick, transition: null, ambient: null }
    : { layouts, visuals, chapter, begin, pick, transition, ambient, keycard, signatureChapter };
})();
