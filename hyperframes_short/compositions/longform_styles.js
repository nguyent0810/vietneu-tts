/* ===== BỘ STYLE BỔ SUNG CHO KHO CẢNH VIDEO DÀI (issue #258, phương án B) =====
   Sáu cảnh "điểm nhấn" lấy Ý TƯỞNG thị giác từ một catalog animation ngoài (mộc bản,
   cắt giấy, một nét vẽ, phim 16 mm, bản vẽ kỹ thuật, ký hoạ chì). Toàn bộ mã ở đây
   viết mới (clean-room): không dùng mã, hằng số, bảng màu hay asset của repo ngoài.

   Nạp SAU longform.js. Chỉ THÊM khoá mới vào window.HF_LONG.visuals; không đụng
   cảnh cũ, không đổi bộ chọn pick(); plan không gọi tên thì không có gì thay đổi.
   Opt-in: plan ghi `"visuals": {"<câu>": {"type": "woodcut", ...}}`.

   Luật tất định (motion-scene-dev): mọi chuyển động trên timeline đã pause; ngẫu nhiên
   bằng HF.rng(HF.hashSeed(...)) theo số câu; trạng thái liên tục (hạt phim, bút) =
   MỘT tween tiến trình + onUpdate tính từ t. Không Date, không Math.random. */
(function () {
  const LONG = window.HF_LONG;
  if (!LONG || !LONG.visuals || !window.HF) return;
  const VIS = LONG.visuals;
  const NS = "http://www.w3.org/2000/svg";
  const el = (t, c, x) => HF.el(t, c, x);
  function sv(tag, attrs, parent) {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs || {}) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  const PORTRAIT = document.documentElement.getAttribute("data-resolution") === "portrait";
  const W = PORTRAIT ? 1080 : 1920, H = PORTRAIT ? 1920 : 1080;
  const rng = (s) => HF.rng(HF.hashSeed(String(s)));
  const clean = (s) => (s || "").replace(/\*\*/g, "").trim();
  const esc = (t) => String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const theme = () => (css("--lf-theme") || "night").replace(/["']/g, "");
  const f1 = (n) => Number(n).toFixed(1);
  // Thời điểm một bước: giống longform.when (đầu câu `at` + lệch, hoặc lúc đọc tới `word`).
  function when(ctx, step, fallback) {
    const L = step && step.at && ctx && ctx.LINES ? ctx.LINES[step.at - 1] : null;
    if (!L) return fallback;
    if (step.word) {
      const key = step.word.toLowerCase();
      const w = (L.words || []).find((x) => clean(x.w).toLowerCase().includes(key));
      if (w) return w.t;
    }
    return L.start + (step.offset != null ? step.offset : 0.3);
  }
  const stepAt = (ctx, v, k, fb) => when(ctx, (v.steps || [])[k], fb);
  // "On twos" của kho: nét tay nhảy 12 nấc/giây.
  const twos = (dur) => `steps(${Math.max(2, Math.round(dur * 12))})`;
  // Camera dùng chung của kho (plan `camera`), gọi lại hàm longform đã xuất.
  function withCamera(def) {
    return {
      build(inner, ln, i, ctx) { def.build.call(def, inner, ln, i, ctx); },
      enter(tl, inner, ln, ctx) {
        def.enter.call(def, tl, inner, ln, ctx);
        const cam = ln.visual && ln.visual.camera;
        if (cam && LONG.camera) LONG.camera(tl, inner, ln, ctx, cam);
      },
    };
  }
  const register = (name, def) => { if (!VIS[name]) VIS[name] = withCamera(def); };
  // Vẽ dần một path bằng stroke-dash (đo độ dài thật; SVG phải có width/height rõ).
  function draw(tl, path, at, dur, ease) {
    const len = path.getTotalLength ? path.getTotalLength() : 1000;
    path.style.strokeDasharray = `${len + 2}`;
    path.style.strokeDashoffset = `${len + 2}`;   // trạng thái dựng: chưa có nét (không hiện sớm từ giây 0)
    tl.fromTo(path, { strokeDashoffset: len + 2 }, { strokeDashoffset: 0, duration: Math.max(.05, dur), ease: ease || "power1.inOut", immediateRender: false }, at);
  }
  // Catmull-Rom (đều) -> Bézier bậc ba: đường cong mượt qua các điểm cho trước.
  function smooth(pts) {
    if (!pts.length) return "";
    let d = `M${f1(pts[0][0])},${f1(pts[0][1])}`;
    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[i - 1] || pts[i], p1 = pts[i], p2 = pts[i + 1], p3 = pts[i + 2] || p2;
      d += ` C${f1(p1[0] + (p2[0] - p0[0]) / 6)},${f1(p1[1] + (p2[1] - p0[1]) / 6)} ${f1(p2[0] - (p3[0] - p1[0]) / 6)},${f1(p2[1] - (p3[1] - p1[1]) / 6)} ${f1(p2[0])},${f1(p2[1])}`;
    }
    return d;
  }
  const poly = (pts, close) => "M" + pts.map((p) => `${f1(p[0])},${f1(p[1])}`).join(" L") + (close ? " Z" : "");
  // Lệch tay có hạt giống: dãy số trong [-a, a].
  const wobble = (seed, a) => { const r = rng(seed); return () => (r() - .5) * 2 * a; };
  // Chữ "A · B": vế A nhỏ, vế B to (quy ước của thẻ chữ trong kho).
  function splitText(t) {
    const s = clean(t || ""), i = s.indexOf("·");
    return i >= 0 ? [s.slice(0, i).trim(), s.slice(i + 1).trim()] : ["", s];
  }
  const ROMAN = [[1000, "M"], [900, "CM"], [500, "D"], [400, "CD"], [100, "C"], [90, "XC"], [50, "L"], [40, "XL"], [10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"]];
  function roman(n) { let s = "", x = Math.max(1, Math.min(3999, Math.round(Number(n) || 0))); for (const [v, c] of ROMAN) while (x >= v) { s += c; x -= v; } return s; }

  /* ================= THƯ VIỆN HÌNH (toạ độ cục bộ, gốc ở chân hình, lên là âm) ================= */
  // Mỗi hình là một ĐƯỜNG GẤP KHÚC LIÊN TỤC, vào từ trái (x âm, y=0) ra bên phải (x dương, y=0)
  // -> dùng được cho "một nét vẽ"; ký hoạ chì / cắt giấy dùng lại cùng dữ liệu.
  function circlePts(cx, cy, r, a0, turns, n) {
    const out = [];
    for (let k = 0; k <= n; k++) { const a = a0 + (k / n) * Math.PI * 2 * turns; out.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); }
    return out;
  }
  const MOTIF = {
    lotus: () => [[-150, 0], [-105, 0], [-125, -70], [-60, -30], [-70, -140], [-20, -45], [0, -165], [20, -45], [70, -140], [60, -30], [125, -70], [105, 0], [150, 0]],
    mountain: () => [[-230, 0], [-150, -130], [-100, -80], [-20, -215], [50, -120], [110, -165], [230, 0]],
    house: () => [[-190, 0], [-170, 0], [-170, -95], [-205, -95], [0, -205], [205, -95], [170, -95], [170, 0], [190, 0]],
    enso: () => [[-170, 0], [-120, -8]].concat(circlePts(0, -118, 112, Math.PI * .58, 1.04, 28), [[120, -8], [170, 0]]),
    pagoda: () => [[-200, 0], [-150, 0], [-150, -60], [-195, -60], [-120, -115], [-120, -165], [-160, -165], [-90, -215], [-90, -255], [-115, -255], [0, -345], [115, -255], [90, -255], [90, -215], [160, -165], [120, -165], [120, -115], [195, -60], [150, -60], [150, 0], [200, 0]],
    boat: () => [[-230, 0], [-200, -8], [-165, -70], [-140, -22], [-10, -22], [-10, -175], [60, -120], [95, -60], [-10, -60], [-10, -22], [140, -22], [165, -70], [200, -8], [230, 0]],
    incense: () => [[-120, 0], [-40, 0], [-40, -120], [-55, -160], [-30, -205], [-55, -250], [-35, -290], [0, -310], [35, -290], [55, -250], [30, -205], [55, -160], [40, -120], [40, 0], [120, 0]],
    meditator: () => [[-180, 0], [-160, -12], [-95, -45], [-55, -50], [-45, -125], [-30, -160]]
      .concat(circlePts(0, -200, 36, Math.PI * .72, .9, 16), [[30, -160], [45, -125], [55, -50], [95, -45], [160, -12], [180, 0]]),
    gate: () => [[-230, 0], [-200, 0], [-200, -170], [-240, -170], [-200, -215], [-120, -215], [-120, -260], [-160, -260], [0, -330], [160, -260], [120, -260], [120, -215], [200, -215], [240, -170], [200, -170], [200, 0], [230, 0]],
    bagua: () => { const o = circlePts(0, -150, 150, Math.PI * .625, 1.0, 8); return [[-200, 0], o[0]].concat(o, [[o[0][0] + 1, o[0][1]], [200, 0]]); },
    tower: () => [[-130, 0], [-90, 0], [-80, -120], [-100, -125], [-70, -210], [-85, -215], [-40, -300], [0, -345], [40, -300], [85, -215], [70, -210], [100, -125], [80, -120], [90, 0], [130, 0]],
    bust: () => [[-170, 0], [-150, -20], [-150, -60], [-95, -100], [-55, -130], [-40, -175], [-50, -215]]
      .concat(circlePts(0, -255, 52, Math.PI * .78, .86, 18), [[50, -215], [40, -175], [55, -130], [95, -100], [150, -60], [150, -20], [170, 0]]),
  };
  const motifPts = (name, fallback) => (MOTIF[name] || MOTIF[fallback || "lotus"])();
  const bboxOf = (pts) => pts.reduce((b, p) => ({ x0: Math.min(b.x0, p[0]), x1: Math.max(b.x1, p[0]), y0: Math.min(b.y0, p[1]), y1: Math.max(b.y1, p[1]) }), { x0: 1e9, x1: -1e9, y0: 1e9, y1: -1e9 });
  const shift = (pts, dx, dy, s) => pts.map((p) => [p[0] * (s || 1) + dx, p[1] * (s || 1) + dy]);

  /* ================= 1) MỘC BẢN — woodcut ================= */
  // Giấy dó ngà, mực nho, son đỏ. Tia đục (nêm thô), đĩa tròn có khía đục, hình giữa đĩa,
  // băng chữ đỏ. Mọi nét vào "on twos"; mực "sôi" bằng cách đổi qua lại 3 bản khắc lệch nhau 8 nhịp/giây.
  function rough(pts, seed, a) { const w = wobble(seed, a); return pts.map((p) => [p[0] + w(), p[1] + w()]); }
  register("woodcut", {
    build(inner, ln) {
      const v = ln.visual, sid = ln.sentence_id;
      const dark = v.tone ? v.tone === "dark" : theme() !== "paper" && v.tone !== "paper";
      const st = el("div", "lf-stage lf-wc" + (dark ? " dark" : "")); inner.appendChild(st);
      st.appendChild(el("div", "wc-paper"));
      const svg = sv("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: "wc-svg" }, st);
      const [small, big] = splitText(v.text);
      const hasText = !!(small || big);
      const cx = hasText && !PORTRAIT ? 640 : W / 2, cy = PORTRAIT ? 700 : 470, R = PORTRAIT ? 250 : 235;
      // Tia nêm quanh đĩa: 3 bản khắc lệch nhau (mực sôi)
      const rays = sv("g", { class: "wc-rays" }, svg);
      const N = 26, variants = [];
      for (let k = 0; k < 3; k++) {
        const w = wobble(`wc-ray|${sid}|${k}`, 6), ds = [];
        for (let i = 0; i < N; i++) {
          const a = (i / N) * Math.PI * 2 + .07, len = (i % 2 ? 1500 : 1700), half = (i % 2 ? .022 : .034);
          const p = [[Math.cos(a - half) * (R + 60) + w(), Math.sin(a - half) * (R + 60) + w()], [Math.cos(a - half * .8) * len + w(), Math.sin(a - half * .8) * len + w()],
                     [Math.cos(a + half * .8) * len + w(), Math.sin(a + half * .8) * len + w()], [Math.cos(a + half) * (R + 60) + w(), Math.sin(a + half) * (R + 60) + w()]];
          ds.push(poly(shift(p, cx, cy), true));
        }
        variants.push(ds);
      }
      const rayEls = variants[0].map((d) => sv("path", { d, class: "wc-ray" }, rays));
      // Đĩa: vành mực dày có khía đục, nền giấy bên trong
      const disc = sv("g", { class: "wc-disc" }, svg);
      sv("path", { d: smooth(rough(circlePts(cx, cy, R, 0, 1, 40), `wc-disc|${sid}`, 3)) + " Z", class: "wc-ring" }, disc);
      sv("path", { d: smooth(rough(circlePts(cx, cy, R - 34, 0, 1, 40), `wc-disc2|${sid}`, 2)) + " Z", class: "wc-ring thin" }, disc);
      const nicks = sv("g", { class: "wc-nicks" }, disc), wn = wobble(`wc-nick|${sid}`, 4);
      for (let i = 0; i < 48; i++) { const a = (i / 48) * Math.PI * 2, r0 = R - 14 + wn(), r1 = R - 30 + wn();
        sv("line", { x1: cx + Math.cos(a) * r0, y1: cy + Math.sin(a) * r0, x2: cx + Math.cos(a + .012) * r1, y2: cy + Math.sin(a + .012) * r1 }, nicks); }
      // Hình giữa đĩa: motif khắc, hoặc con số lớn
      const mid = sv("g", { class: "wc-mid" }, disc);
      let numEl = null;
      if (v.value != null) {
        numEl = sv("text", { x: cx, y: cy + (PORTRAIT ? 70 : 64), class: "wc-num", "text-anchor": "middle" }, mid);
        numEl.textContent = String(v.value);
      } else if (!v.motif || v.motif === "lotus") {
        // Sen khắc: 5 cánh kín (mỗi cánh một nét đục), gân giữa; đế sen là vạch cong
        const w = wobble(`wc-lotus|${sid}`, 3), by = cy + R * .38;
        [-52, -26, 0, 26, 52].forEach((deg, k) => {
          const h = k === 2 ? R * .92 : (k === 1 || k === 3 ? R * .8 : R * .62), a = deg * Math.PI / 180;
          const petal = (u, vv) => [cx + u * Math.cos(a) - vv * Math.sin(a) + w(), by + u * Math.sin(a) + vv * Math.cos(a) + w()];
          const P = (p) => `${f1(p[0])},${f1(p[1])}`;
          const d = `M${P(petal(0, 0))} C${P(petal(-R * .3, -h * .35))} ${P(petal(-R * .22, -h * .85))} ${P(petal(0, -h))} C${P(petal(R * .22, -h * .85))} ${P(petal(R * .3, -h * .35))} ${P(petal(0, 0))} Z`;
          sv("path", { d, class: "wc-motif petal" }, mid);
          sv("path", { d: `M${P(petal(0, -h * .12))} L${P(petal(0, -h * .78))}`, class: "wc-motif vein" }, mid);
        });
        sv("path", { d: smooth([[cx - R * .62, by - 4 + w()], [cx - R * .3, by + 26 + w()], [cx, by + 34 + w()], [cx + R * .3, by + 26 + w()], [cx + R * .62, by - 4 + w()]]), class: "wc-motif" }, mid);
      } else {
        const pts = motifPts(v.motif, "lotus"), bb = bboxOf(pts), s = Math.min((R * 1.25) / (bb.x1 - bb.x0), (R * 1.15) / (bb.y1 - bb.y0));
        sv("path", { d: smooth(shift(rough(pts, `wc-motif|${sid}`, 2), cx, cy + (bb.y1 - bb.y0) * s / 2 - 8, s)), class: "wc-motif" }, mid);
      }
      // Băng chữ đỏ (bong bóng khắc) bên phải / dưới
      let band = null, bandEls = null;
      if (hasText) {
        band = el("div", "wc-band"); st.appendChild(band);
        if (PORTRAIT) Object.assign(band.style, { left: "70px", right: "70px", top: "1080px" });
        else Object.assign(band.style, { left: "980px", width: "800px", top: small ? "330px" : "360px" });
        if (small) band.appendChild(el("div", "wc-small", esc(small)));
        band.appendChild(el("div", "wc-big" + (big.length > 14 ? " long" : ""), esc(big)));
        bandEls = Array.from(band.children);
      }
      inner._wc = { st, rays, rayEls, variants, disc, mid, numEl, band, bandEls, cx, cy };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._wc, v = ln.visual, t0 = ln.start, span = Math.max(2.5, ctx.until - t0);
      const tDisc = t0 + .25, tText = stepAt(ctx, v, 0, t0 + 1.7);
      tl.fromTo(S.rays, { scale: .2, opacity: 0, svgOrigin: `${S.cx} ${S.cy}` }, { scale: 1, opacity: 1, duration: .6, ease: twos(.6), immediateRender: false }, t0 + .05);
      tl.fromTo(S.disc, { scale: .6, opacity: 0, svgOrigin: `${S.cx} ${S.cy}` }, { scale: 1, opacity: 1, duration: .45, ease: twos(.45), immediateRender: false }, tDisc);
      tl.fromTo(S.mid, { opacity: 0 }, { opacity: 1, duration: .3, ease: twos(.3), immediateRender: false }, tDisc + .35);
      if (S.numEl) tl.fromTo(S.numEl, { scale: 1.6, svgOrigin: `${S.cx} ${S.cy}` }, { scale: 1, duration: .35, ease: twos(.35), immediateRender: false }, tDisc + .35);
      if (S.band) {
        tl.fromTo(S.band, { opacity: 0, scale: 1.25, rotation: -4 }, { opacity: 1, scale: 1, rotation: -1.5, duration: .3, ease: twos(.3), immediateRender: false }, tText);
        tl.fromTo(S.bandEls, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: .3, stagger: .12, ease: twos(.3), immediateRender: false }, tText + .1);
      }
      // Mực sôi: đổi bản khắc 8 lần/giây (tất định theo nấc thời gian)
      // Trạng thái lấy HOÀN TOÀN từ giá trị tween (boil.k): seek lùi trước t0 / nhảy mốc -> về bản khắc 0.
      const boil = { k: 0 }, applyBoil = () => { const vi = S.variants[Math.round(boil.k) % 3]; S.rayEls.forEach((p, i) => p.setAttribute("d", vi[i])); };
      tl.set(boil, { k: 0, onUpdate: applyBoil }, t0);
      tl.to(boil, { k: Math.round(span * 8), duration: span, ease: `steps(${Math.max(1, Math.round(span * 8))})`, onUpdate: applyBoil }, t0);
      // Trôi rất chậm cả bản in (giữ cảnh sống)
      tl.fromTo(S.st, { scale: 1 }, { scale: 1.03, duration: span, ease: "none", immediateRender: false }, t0);
    },
  });

  /* ================= 2) CẮT GIẤY DIORAMA — papercut ================= */
  // 5–6 lớp giấy cắt (trời, trăng/mặt trời, núi xa, đồi, công trình, cây, đất gần), mỗi lớp đổ bóng mềm;
  // thị sai trượt chậm theo chiều sâu, nguồn sáng đổi theo giờ (bóng đổi hướng). Thẻ giấy ghi chữ tại mốc.
  const PC_TIME = {
    night: { sky: ["#1b2340", "#2e3a66"], far: "#3e4a7c", mid: "#2f3f63", hill: "#2a4a4a", near: "#1f3b35", bld: "#1a1f36", sun: "#f1e6c8", tag: "#f3ead6", ink: "#1d1a2a", glow: "rgba(255,225,160,.75)" },
    dawn: { sky: ["#f1c9a6", "#e58f7c"], far: "#8e6a98", mid: "#6d5a8a", hill: "#5f8a6d", near: "#3f6b4f", bld: "#3a2f44", sun: "#f6b35a", tag: "#fff6e8", ink: "#3a2a26", glow: "rgba(255,210,140,.6)" },
    day: { sky: ["#bfe0f5", "#e9f4fb"], far: "#8aa6c6", mid: "#6f8fb4", hill: "#7fb37a", near: "#5a9a5c", bld: "#5b4a3c", sun: "#f8d35c", tag: "#ffffff", ink: "#243041", glow: "rgba(255,255,255,.4)" },
    dusk: { sky: ["#3d2a52", "#d9775e"], far: "#6a4a74", mid: "#4f3c64", hill: "#3f5a52", near: "#2b4238", bld: "#2a2030", sun: "#f3a24b", tag: "#fbe9d8", ink: "#2b1f2a", glow: "rgba(255,190,120,.7)" },
  };
  function ridge(seed, y, amp, n, x0, x1) {   // đường chân trời gấp khúc (núi/đồi) có hạt giống
    const r = rng(seed), pts = [[x0, H + 40]];
    for (let k = 0; k <= n; k++) pts.push([x0 + (k / n) * (x1 - x0), y - r() * amp]);
    pts.push([x1, H + 40]);
    return pts;
  }
  const PC_SCENE = {
    pagoda(g, P, sid) {   // chùa + tháp, mái cong, cửa sáng
      const x = W * .36, y = 760;
      sv("path", { d: poly(shift([[-260, 0], [-260, -120], [-300, -130], [-230, -165], [-170, -165], [-170, -230], [-205, -240], [-120, -290], [120, -290], [205, -240], [170, -230], [170, -165], [230, -165], [300, -130], [260, -120], [260, 0]], x, y), true), class: "pc-bld" }, g);
      // Tháp nhiều tầng: các tầng hẹp dần, mỗi tầng có mái vươn, chóp nhọn
      const tx = x + 470, tiers = [[150, 0, 90], [120, -90, 80], [96, -170, 70], [74, -240, 60], [52, -300, 50]];
      tiers.forEach(([hw, ty, th]) => { sv("rect", { x: tx - hw, y: y + ty - th, width: hw * 2, height: th, class: "pc-bld" }, g);
        sv("path", { d: poly([[tx - hw - 26, y + ty - th], [tx + hw + 26, y + ty - th], [tx + hw - 6, y + ty - th - 22], [tx - hw + 6, y + ty - th - 22]], true), class: "pc-bld" }, g); });
      sv("path", { d: poly([[tx - 30, y - 372], [tx + 30, y - 372], [tx, y - 460]], true), class: "pc-bld" }, g);
      P.win = [[-70, -60], [0, -75], [70, -60]].map(([dx, dy]) => sv("rect", { x: x + dx - 22, y: y + dy - 40, width: 44, height: 70, rx: 6, class: "pc-win" }, g));
    },
    mountain(g, P, sid) {  // long mạch: dải núi lớp sát + dòng sông uốn
      const r = rng(`pc-mnt|${sid}`);
      sv("path", { d: poly(ridge(`pc-m1|${sid}`, 640, 220, 7, -80, W + 80), true), class: "pc-bld" }, g);
      const riv = [[W * .55, 1120]]; for (let k = 1; k <= 6; k++) riv.push([W * .55 + (r() - .5) * 420, 1120 - k * 70]);
      P.river = sv("path", { d: smooth(riv), class: "pc-river" }, g);
    },
    citadel(g, P, sid) {  // thành luỹ: tường răng cưa + cổng vòm + lầu
      const x = W * .5, y = 790, pts = [[-620, 0], [-620, -120]];
      for (let k = 0; k < 14; k++) { const bx = -560 + k * 86; pts.push([bx, -120], [bx, -150], [bx + 44, -150], [bx + 44, -120]); }
      pts.push([620, -120], [620, 0]);
      sv("path", { d: poly(shift(pts, x, y), true), class: "pc-bld" }, g);
      sv("path", { d: poly(shift(MOTIF.gate(), x, y + 2, 1.0), true), class: "pc-bld" }, g);
      P.win = [sv("path", { d: `M${x - 60},${y} L${x - 60},${y - 90} A60,60 0 0 1 ${x + 60},${y - 90} L${x + 60},${y} Z`, class: "pc-win" }, g)];
    },
    village(g, P, sid) {  // xóm làng: ba mái nhà, cây đa
      [[-520, 0, .75], [-120, 0, 1], [360, 0, .8]].forEach(([dx, dy, s]) => sv("path", { d: poly(shift(MOTIF.house(), W * .5 + dx, 790 + dy, s), true), class: "pc-bld" }, g));
      P.win = [sv("rect", { x: W * .5 - 150, y: 720, width: 50, height: 60, rx: 5, class: "pc-win" }, g)];
    },
  };
  register("papercut", {
    build(inner, ln) {
      const v = ln.visual, sid = ln.sentence_id, T = PC_TIME[v.time] || PC_TIME.night;
      const st = el("div", "lf-stage lf-pc"); inner.appendChild(st);
      st.style.background = `linear-gradient(180deg, ${T.sky[0]} 0%, ${T.sky[1]} 100%)`;
      const layer = (cls, depth) => { const s = sv("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: "pc-layer " + cls }, st); s.dataset.depth = depth; return s; };
      const P = { layers: [] };
      // Trăng / mặt trời: đĩa giấy có lớp quầng
      const Lsun = layer("sun", .1); P.sun = sv("g", {}, Lsun);
      sv("circle", { cx: W * .72, cy: 300, r: 86, fill: T.sun, class: "pc-sun" }, P.sun);
      if ((v.time || "night") === "night") sv("circle", { cx: W * .72 - 30, cy: 282, r: 74, fill: T.sky[0], opacity: .85 }, P.sun);  // trăng khuyết: che một phần
      P.sunGlow = Lsun; Lsun.style.filter = `drop-shadow(0 0 40px ${T.glow})`;
      // Sao đêm (giấy đục lỗ)
      if ((v.time || "night") === "night") { const r = rng(`pc-star|${sid}`); P.stars = []; for (let k = 0; k < 26; k++) P.stars.push(sv("circle", { cx: r() * W, cy: r() * 420, r: 1.5 + r() * 2.2, fill: "#fff6d8", opacity: .0 }, Lsun)); }
      const Lfar = layer("far", .25); sv("path", { d: poly(ridge(`pc-far|${sid}`, 560, 180, 9, -120, W + 120), true), fill: T.far }, Lfar);
      const Lmid = layer("mid", .45); sv("path", { d: poly(ridge(`pc-mid|${sid}`, 680, 130, 11, -120, W + 120), true), fill: T.mid }, Lmid);
      const Lbld = layer("bld", .6); const g = sv("g", {}, Lbld); Lbld.style.setProperty("--pc-bld", T.bld);
      (PC_SCENE[v.scene] || PC_SCENE.pagoda)(g, P, sid);
      const Lhill = layer("hill", .75); sv("path", { d: poly(ridge(`pc-hill|${sid}`, 820, 70, 13, -140, W + 140), true), fill: T.hill }, Lhill);
      // Cây gần: cụm tam giác / tán tròn cắt giấy
      const Ltree = layer("tree", .9), rt = rng(`pc-tree|${sid}`);
      for (let k = 0; k < 9; k++) { const x = -60 + k * (W + 120) / 8 + (rt() - .5) * 90, h = 120 + rt() * 110, y = 905 + rt() * 30;
        sv("path", { d: poly([[x - h * .42, y], [x - h * .3, y - h * .45], [x - h * .16, y - h * .4], [x, y - h], [x + h * .16, y - h * .4], [x + h * .3, y - h * .45], [x + h * .42, y]], true), fill: T.near }, Ltree); }
      const Lnear = layer("near", 1.0); sv("path", { d: poly(ridge(`pc-near|${sid}`, 985, 36, 17, -160, W + 160), true), fill: T.near }, Lnear);
      P.layers = [Lfar, Lmid, Lbld, Lhill, Ltree, Lnear];
      // Thẻ giấy ghi chữ
      if (v.text) {
        const tag = el("div", "pc-tag"); tag.style.background = T.tag; tag.style.color = T.ink; st.appendChild(tag);
        const [a, b] = splitText(v.text);
        if (a) tag.appendChild(el("div", "pc-tag-small", esc(a)));
        tag.appendChild(el("div", "pc-tag-big" + (b.length > 16 ? " long" : ""), esc(b)));
        if (v.sub) tag.appendChild(el("div", "pc-tag-sub", esc(v.sub)));
        P.tag = tag;
      }
      st.appendChild(el("div", "pc-grain"));
      inner._pc = Object.assign(P, { st, T });
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._pc, v = ln.visual, t0 = ln.start, span = Math.max(3, ctx.until - t0);
      // Dựng cảnh: các lớp trồi lên từ dưới, lớp xa trước
      S.layers.forEach((L, k) => tl.fromTo(L, { y: 90 + k * 20, opacity: 0 }, { y: 0, opacity: 1, duration: .9, ease: "power3.out", immediateRender: false }, t0 + k * .12));
      tl.fromTo(S.sunGlow, { opacity: 0, y: 60 }, { opacity: 1, y: 0, duration: 1.6, ease: "sine.out", immediateRender: false }, t0 + .3);
      // Thị sai: lớp càng gần trượt càng nhiều; nguồn sáng đi lên -> bóng ngắn dần
      S.layers.forEach((L) => { const d = Number(L.dataset.depth); tl.fromTo(L, { x: 0 }, { x: -34 * d, duration: span, ease: "none", immediateRender: false }, t0 + .9);
        tl.fromTo(L, { filter: `drop-shadow(0 ${14 + 26 * d}px ${8 + 10 * d}px rgba(0,0,0,.5))` }, { filter: `drop-shadow(0 ${8 + 14 * d}px ${8 + 10 * d}px rgba(0,0,0,.42))`, duration: span, ease: "none", immediateRender: false }, t0 + .9); });
      tl.fromTo(S.sun, { y: 0 }, { y: -70, duration: span, ease: "sine.out", immediateRender: false }, t0 + .9);
      if (S.stars) S.stars.forEach((s, k) => tl.fromTo(s, { opacity: 0 }, { opacity: .55 + (k % 3) * .15, duration: .8, ease: "sine.out", immediateRender: false }, t0 + 1.0 + (k % 7) * .13));
      if (S.win) { const tw = stepAt(ctx, v, 1, t0 + 2.2); S.win.forEach((w, k) => tl.fromTo(w, { opacity: 0 }, { opacity: 1, duration: .6, ease: "sine.inOut", immediateRender: false }, tw + k * .15)); }
      if (S.river) draw(tl, S.river, t0 + 1.2, 2.4, "power1.inOut");
      if (S.tag) {
        const tt = stepAt(ctx, v, 0, t0 + 1.4);
        tl.fromTo(S.tag, { opacity: 0, y: 30, rotation: -3 }, { opacity: 1, y: 0, rotation: -1.2, duration: .6, ease: "power3.out", immediateRender: false }, tt);
        tl.fromTo(S.tag.children, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: .45, stagger: .1, ease: "power2.out", immediateRender: false }, tt + .15);
      }
      tl.fromTo(S.st, { scale: 1.04 }, { scale: 1, duration: span, ease: "none", immediateRender: false }, t0);
    },
  });

  /* ================= 3) MỘT NÉT VẼ — oneline ================= */
  // Một đường liên tục chạy ngang khung, lần lượt "vẽ" các hình (sen, núi, nhà, vòng thiền...) đúng lúc
  // giọng đọc nhắc tới; nhãn chữ viết tay hiện dưới mỗi hình. Đầu bút = chấm son.
  register("oneline", {
    build(inner, ln) {
      const v = ln.visual, sid = ln.sentence_id;
      const dark = v.tone ? v.tone === "dark" : theme() !== "paper";
      const st = el("div", "lf-stage lf-ol" + (dark ? " dark" : "")); inner.appendChild(st);
      const svg = sv("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: "ol-svg" }, st);
      const items = (v.items || [{ motif: "lotus" }]).slice(0, PORTRAIT ? 3 : 4);
      const base = PORTRAIT ? 1050 : 600, n = items.length;
      const w = wobble(`ol|${sid}`, 5);
      // Toạ độ tâm từng hình: chia đều, chừa lề
      const margin = PORTRAIT ? 120 : 220, gap = (W - margin * 2) / n;
      const pts = [[-40, base + w()]], marks = [];   // marks: chỉ số điểm cuối của mỗi hình
      let x = -40;
      const scale = PORTRAIT ? .6 : Math.min(1, gap / 520);
      items.forEach((it, k) => {
        const cx = margin + gap * (k + .5), m = shift(motifPts(it.motif, "lotus"), cx, base, scale);
        // đoạn nền uốn nhẹ tới hình
        for (let s = 1; s <= 3; s++) pts.push([x + (m[0][0] - x) * (s / 4), base + w() * 1.6]);
        m.forEach((p) => pts.push(p));
        x = m[m.length - 1][0];
        marks.push({ idx: pts.length - 1, cx, w: bboxOf(m) });
      });
      for (let s = 1; s <= 3; s++) pts.push([x + (W + 40 - x) * (s / 4), base + w() * 1.6]);
      pts.push([W + 40, base + w()]);
      const path = sv("path", { d: smooth(pts), class: "ol-path" }, svg);
      const pen = sv("circle", { r: 7, class: "ol-pen", opacity: 0 }, svg);
      // Nhãn viết tay dưới mỗi hình
      const labels = items.map((it, k) => { if (!it.label) return null; const d = el("div", "ol-label", esc(it.label));
        d.style.left = (marks[k].cx - 260) + "px"; d.style.top = (base + 34) + "px"; st.appendChild(d); return d; });
      const title = v.title ? el("div", "ol-title", esc(v.title)) : null; if (title) st.appendChild(title);
      // Độ dài tích luỹ theo đường gấp khúc (đủ chính xác để canh mốc)
      const cum = [0]; for (let i = 1; i < pts.length; i++) cum.push(cum[i - 1] + Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]));
      inner._ol = { st, svg, path, pen, labels, marks, cum, title, items };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._ol, v = ln.visual, t0 = ln.start, span = Math.max(3, ctx.until - t0);
      const total = S.path.getTotalLength(), ratio = total / S.cum[S.cum.length - 1];
      S.path.style.strokeDasharray = `${total + 4}`;
      const prog = { L: 0 };
      const apply = () => { S.path.style.strokeDashoffset = String(total + 4 - prog.L); const p = S.path.getPointAtLength(Math.min(total, prog.L)); S.pen.setAttribute("cx", p.x); S.pen.setAttribute("cy", p.y); };
      apply();                                           // trạng thái dựng: chưa có nét
      tl.set(prog, { L: 0, onUpdate: apply }, t0);        // neo tại t0 (seek lùi / nhảy mốc -> về 0)
      if (S.title) tl.fromTo(S.title, { opacity: 0 }, { opacity: 1, duration: .5, immediateRender: false }, t0 + .2);
      tl.fromTo(S.pen, { opacity: 0 }, { opacity: 1, duration: .25, immediateRender: false }, t0);
      // Mốc: hình k vẽ xong vào thời điểm bước k (mặc định chia đều trong khoảng)
      const n = S.marks.length, ends = [];
      let prevT = t0 + .2;
      S.marks.forEach((m, k) => {
        const fb = t0 + .9 + (span - 2.2) * ((k + 1) / n);
        const tk = Math.max(prevT + .5, when(ctx, S.items[k], when(ctx, (v.steps || [])[k], fb)));
        const Lk = S.cum[m.idx] * ratio;
        tl.to(prog, { L: Lk, duration: tk - prevT, ease: "power1.inOut", onUpdate: apply }, prevT);
        if (S.labels[k]) tl.fromTo(S.labels[k], { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: .5, ease: "power2.out", immediateRender: false }, tk - .15);
        prevT = tk; ends.push(tk);
      });
      // Chạy nốt ra mép phải rồi đầu bút biến mất
      const tEnd = Math.max(prevT + .6, t0 + span - .3);
      tl.to(prog, { L: total, duration: tEnd - prevT, ease: "power1.in", onUpdate: apply }, prevT);
      tl.fromTo(S.pen, { opacity: 1 }, { opacity: 0, duration: .2, immediateRender: false }, tEnd - .2);
      tl.fromTo(S.st, { scale: 1 }, { scale: 1.02, duration: span, ease: "none", immediateRender: false }, t0);
    },
  });

  /* ================= 4) PHIM TƯ LIỆU 16 MM — film16 ================= */
  // Đen trắng: hạt phim (ô nhiễu nướng sẵn, xê dịch 24 nấc/giây), rung cửa phim 1–2 px, vệt xước thưa,
  // viền tối, thẻ tiêu đề khung kép, đếm ngược (tuỳ chọn), chú thích gõ máy. Không loé sáng toàn khung.
  function noiseTile(seed, size) {
    const cv = document.createElement("canvas"); cv.width = cv.height = size;
    const c = cv.getContext("2d"); if (!c) return cv;
    const img = c.createImageData(size, size), r = rng(`f16-noise|${seed}`);
    for (let i = 0; i < img.data.length; i += 4) { const g = 90 + Math.floor(r() * 130); img.data[i] = img.data[i + 1] = img.data[i + 2] = g; img.data[i + 3] = 255; }
    c.putImageData(img, 0, 0);
    return cv;
  }
  register("film16", {
    build(inner, ln) {
      const v = ln.visual, sid = ln.sentence_id;
      const st = el("div", "lf-stage lf-f16"); inner.appendChild(st);
      const frame = el("div", "f16-frame"); st.appendChild(frame);   // lớp bị rung cửa phim
      if (v.src) { const img = el("div", "f16-img"); img.style.backgroundImage = `url(${v.src})`; frame.appendChild(img); inner._f16img = img; }
      else frame.appendChild(el("div", "f16-stagebg"));
      // Thẻ tiêu đề khung kép
      const card = el("div", "f16-card"); frame.appendChild(card);
      if (v.kicker) card.appendChild(el("div", "f16-kicker", esc(v.kicker)));
      if (v.title) card.appendChild(el("div", "f16-title" + (clean(v.title).length > 18 ? " long" : ""), esc(v.title)));
      if (v.sub) card.appendChild(el("div", "f16-sub", esc(v.sub)));
      if (v.year) card.appendChild(el("div", "f16-year", "— " + roman(v.year) + " —"));
      // Chú thích gõ máy (góc trên trái)
      const cap = v.caption ? el("div", "f16-cap", esc(v.caption)) : null; if (cap) frame.appendChild(cap);
      // Đếm ngược
      let leader = null;
      if (v.leader) { leader = el("div", "f16-leader"); leader.appendChild(el("div", "f16-leader-sweep")); leader.appendChild(el("div", "f16-leader-num", String(v.leader_n || 3))); leader.appendChild(el("div", "f16-leader-cross")); st.appendChild(leader); }
      // Vệt xước (các đường dọc mảnh, hiện ngắn)
      const scr = sv("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: "f16-scr" }, st);
      const r = rng(`f16-scr|${sid}`), lines = [];
      for (let k = 0; k < 40; k++) { const x = r() * W; lines.push({ l: sv("line", { x1: x, y1: 0, x2: x + (r() - .5) * 12, y2: H, opacity: 0 }, scr), r1: r(), r2: r() }); }
      const grain = el("canvas", "f16-grain"); grain.width = 960; grain.height = 540; st.appendChild(grain);
      st.appendChild(el("div", "f16-vignette"));
      inner._f16 = { st, frame, card, cap, leader, lines, grain, tile: noiseTile(sid, 192), gc: grain.getContext("2d") };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._f16, v = ln.visual, t0 = ln.start, span = Math.max(3, ctx.until - t0);
      const lead = S.leader ? 2.0 : 0;
      if (S.leader) {
        tl.fromTo(S.leader, { opacity: 1 }, { opacity: 1, duration: lead - .1, immediateRender: false }, t0);
        tl.fromTo(S.leader.querySelector(".f16-leader-sweep"), { "--sweep": "0deg" }, { "--sweep": "360deg", duration: lead - .2, ease: "none", immediateRender: false }, t0);
        tl.set(S.leader, { opacity: 0 }, t0 + lead);
      }
      const tc = t0 + lead + .15;
      if (inner._f16img) { tl.fromTo(inner._f16img, { opacity: 0 }, { opacity: 1, duration: .3, ease: twos(.3), immediateRender: false }, tc);
        tl.fromTo(inner._f16img, { scale: 1.04 }, { scale: 1.12, duration: span, ease: "none", immediateRender: false }, tc); }
      const cardT = v.src ? stepAt(ctx, v, 0, tc + 1.2) : tc;
      if (S.card.children.length) {
        tl.fromTo(S.card, { opacity: 0 }, { opacity: 1, duration: .25, ease: twos(.25), immediateRender: false }, cardT);
        tl.fromTo(S.card.children, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: .3, stagger: .18, ease: twos(.3), immediateRender: false }, cardT + .15);
      }
      if (S.cap) { const tcap = stepAt(ctx, v, v.src ? 1 : 0, cardT + 1.6), nch = S.cap.textContent.length;
        tl.fromTo(S.cap, { clipPath: "inset(0 100% 0 0)", opacity: 1 }, { clipPath: "inset(0 0% 0 0)", duration: Math.min(2.2, nch * .055), ease: `steps(${nch})`, immediateRender: false }, tcap); }
      // Hạt + rung cửa phim: một tween tiến trình, vẽ lại trong onUpdate theo nấc 24/giây
      const clock = { t: 0 }, gc = S.gc, tile = S.tile, tw = 192, cols = Math.ceil(960 / tw) + 1, rows = Math.ceil(540 / tw) + 1;
      const scrOn = S.lines.map((L, k) => ({ L, t: t0 + .4 + L.r1 * span, d: .06 + L.r2 * .14 })).filter((e) => e.t < t0 + span - .2).slice(0, Math.round(span * .9));
      const paint = () => {
        if (!gc) return;
        const f = Math.floor(clock.t * 24), r = rng(`f16-f|${ln.sentence_id}|${f}`);
        const ox = -Math.floor(r() * tw), oy = -Math.floor(r() * tw);
        gc.clearRect(0, 0, 960, 540);
        for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) gc.drawImage(tile, ox + i * tw, oy + j * tw);
        const wy = (r() - .5) * 3, wx = (r() - .5) * 1.4;
        S.frame.style.transform = `translate(${wx.toFixed(2)}px, ${wy.toFixed(2)}px)`;
      };
      paint();                                            // trạng thái dựng = khung 0
      tl.set(clock, { t: 0, onUpdate: paint }, t0);       // seek lùi / nhảy mốc -> hạt + rung về khung 0
      tl.to(clock, { t: span, duration: span, ease: "none", onUpdate: paint }, t0);
      scrOn.forEach((e) => { tl.set(e.L.l, { opacity: .35 + e.d }, e.t); tl.set(e.L.l, { opacity: 0 }, e.t + e.d); });
    },
  });

  /* ================= 5) BẢN VẼ KỸ THUẬT — blueprint ================= */
  // Nền xanh lam, lưới ô, nét trắng vẽ dần, đường kích thước có mũi tên, nhãn có đường dẫn, khung tên
  // góc phải dưới. Dữ liệu từ JSON (items) hoặc preset (scene: house | wall) hoặc bars (biểu đồ).
  function dimPath(x1, y1, x2, y2) {   // đường kích thước: hai vạch chặn + mũi tên hai đầu
    const dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L, nx = -uy, ny = ux, a = 12;
    return `M${f1(x1)},${f1(y1)} L${f1(x2)},${f1(y2)} M${f1(x1 + nx * 14)},${f1(y1 + ny * 14)} L${f1(x1 - nx * 14)},${f1(y1 - ny * 14)} M${f1(x2 + nx * 14)},${f1(y2 + ny * 14)} L${f1(x2 - nx * 14)},${f1(y2 - ny * 14)}` +
      ` M${f1(x1 + ux * a + nx * 5)},${f1(y1 + uy * a + ny * 5)} L${f1(x1)},${f1(y1)} L${f1(x1 + ux * a - nx * 5)},${f1(y1 + uy * a - ny * 5)}` +
      ` M${f1(x2 - ux * a + nx * 5)},${f1(y2 - uy * a + ny * 5)} L${f1(x2)},${f1(y2)} L${f1(x2 - ux * a - nx * 5)},${f1(y2 - uy * a - ny * 5)}`;
  }
  const BP_SCENE = {
    house: () => [   // mặt bằng nhà ba gian, sân trước, hướng
      { kind: "rect", x: 560, y: 300, w: 800, h: 300 }, { kind: "line", x1: 826, y1: 300, x2: 826, y2: 600 }, { kind: "line", x1: 1093, y1: 300, x2: 1093, y2: 600 },
      { kind: "rect", x: 560, y: 640, w: 800, h: 180, dash: true }, { kind: "label", text: "GIAN GIỮA · BÀN THỜ", x: 960, y: 450 },
      { kind: "label", text: "SÂN", x: 960, y: 740 }, { kind: "dim", x1: 560, y1: 250, x2: 1360, y2: 250, text: "3 GIAN" },
      { kind: "dim", x1: 1420, y1: 300, x2: 1420, y2: 600, text: "LÒNG NHÀ" }, { kind: "circle", cx: 300, cy: 420, r: 90 },
      { kind: "line", x1: 300, y1: 330, x2: 300, y2: 510 }, { kind: "line", x1: 210, y1: 420, x2: 390, y2: 420 }, { kind: "label", text: "HƯỚNG NHÀ", x: 300, y: 560, lead: false },
    ],
    wall: () => [   // mặt cắt luỹ đất: nền, thân luỹ, hào
      { kind: "poly", points: [[300, 760], [700, 760], [820, 460], [1000, 460], [1120, 760], [1620, 760]] }, { kind: "line", x1: 200, y1: 760, x2: 1720, y2: 760 },
      { kind: "poly", points: [[1180, 760], [1240, 880], [1440, 880], [1500, 760]], dash: true }, { kind: "label", text: "HÀO", x: 1340, y: 950, lead: false },
      { kind: "dim", x1: 820, y1: 410, x2: 1000, y2: 410, text: "MẶT LUỸ" }, { kind: "dim", x1: 250, y1: 460, x2: 250, y2: 760, text: "CAO" },
      { kind: "dim", x1: 700, y1: 820, x2: 1120, y2: 820, text: "CHÂN LUỸ" }, { kind: "hatch", points: [[700, 760], [820, 460], [1000, 460], [1120, 760]] },
    ],
  };
  function barsToItems(bars, unit) {
    const n = bars.length, x0 = 300, x1 = 1500, base = 780, top = 340, gap = (x1 - x0) / n, bw = Math.min(160, gap * .56);
    const max = Math.max(...bars.map((b) => Number(b.value) || 0)) || 1, items = [{ kind: "line", x1: x0 - 40, y1: base, x2: x1 + 40, y2: base }];
    bars.forEach((b, k) => { const h = (Number(b.value) / max) * (base - top), x = x0 + gap * (k + .5) - bw / 2, y = base - h;
      items.push({ kind: "rect", x, y, w: bw, h, at: b.at, word: b.word, hatch: true }, { kind: "label", text: String(b.label || ""), x: x + bw / 2, y: base + 44, lead: false, at: b.at, word: b.word },
        { kind: "dim", x1: x + bw + 26, y1: y, x2: x + bw + 26, y2: base, text: (b.text || `${b.value}${unit ? " " + unit : ""}`), at: b.at, word: b.word }); });
    return items;
  }
  register("blueprint", {
    build(inner, ln) {
      const v = ln.visual, sid = ln.sentence_id;
      const st = el("div", "lf-stage lf-bp"); inner.appendChild(st);
      st.appendChild(el("div", "bp-grid"));
      const svg = sv("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: "bp-svg" }, st);
      const defs = sv("defs", {}, svg), pat = sv("pattern", { id: `bp-hatch-${sid}`, width: 14, height: 14, patternUnits: "userSpaceOnUse", patternTransform: "rotate(45)" }, defs);
      sv("line", { x1: 0, y1: 0, x2: 0, y2: 14, class: "bp-hatch-line" }, pat);
      const items = v.bars ? barsToItems(v.bars, v.unit) : (v.items || (BP_SCENE[v.scene] || BP_SCENE.house)());
      const drawn = items.map((it) => {
        const g = sv("g", { class: "bp-item", opacity: 0 }, svg); let strokes = [];
        if (it.kind === "rect") { strokes.push(sv("rect", { x: it.x, y: it.y, width: it.w, height: it.h, class: "bp-stroke" + (it.dash ? " dash" : "") }, g));
          if (it.hatch) g.appendChild(sv("rect", { x: it.x, y: it.y, width: it.w, height: it.h, fill: `url(#bp-hatch-${sid})`, class: "bp-fill" })); }
        else if (it.kind === "circle") strokes.push(sv("circle", { cx: it.cx, cy: it.cy, r: it.r, class: "bp-stroke" + (it.dash ? " dash" : "") }, g));
        else if (it.kind === "line") strokes.push(sv("path", { d: `M${it.x1},${it.y1} L${it.x2},${it.y2}`, class: "bp-stroke" + (it.dash ? " dash" : "") }, g));
        else if (it.kind === "poly") strokes.push(sv("path", { d: poly(it.points, it.close), class: "bp-stroke" + (it.dash ? " dash" : "") }, g));
        else if (it.kind === "hatch") g.appendChild(sv("path", { d: poly(it.points, true), fill: `url(#bp-hatch-${sid})`, class: "bp-fill" }));
        else if (it.kind === "dim") { strokes.push(sv("path", { d: dimPath(it.x1, it.y1, it.x2, it.y2), class: "bp-stroke thin" }, g));
          const vert = Math.abs(it.x2 - it.x1) < Math.abs(it.y2 - it.y1), mx = (it.x1 + it.x2) / 2, my = (it.y1 + it.y2) / 2;
          const t = sv("text", { x: vert ? mx + 18 : mx, y: vert ? my : my - 14, class: "bp-text", "text-anchor": vert ? "start" : "middle", "dominant-baseline": vert ? "middle" : "auto" }, g); t.textContent = it.text || ""; }
        else if (it.kind === "label") { const t = sv("text", { x: it.x, y: it.y, class: "bp-text big", "text-anchor": "middle" }, g); t.textContent = it.text || "";
          if (it.lead !== false && it.lx != null) strokes.push(sv("path", { d: `M${it.lx},${it.ly} L${it.x},${it.y + 10}`, class: "bp-stroke thin" }, g)); }
        return { g, strokes, it, texts: Array.from(g.querySelectorAll("text")) };
      });
      // Khung tên
      const tb = el("div", "bp-title"); st.appendChild(tb);
      tb.appendChild(el("div", "bp-tt" + (clean(v.title || "").length > 22 ? " long" : ""), esc(v.title || "BẢN VẼ")));
      const row = el("div", "bp-row"); tb.appendChild(row);
      [["TỶ LỆ", v.scale || "1 : 100"], ["MÃ", v.code || "—"], ["TỜ", v.sheet || "1 / 1"]].forEach(([k, val]) => { const c = el("div", "bp-cell"); c.appendChild(el("span", "k", k)); c.appendChild(el("span", "v", esc(val))); row.appendChild(c); });
      if (v.sub) tb.appendChild(el("div", "bp-sub", esc(v.sub)));
      inner._bp = { st, svg, drawn, tb };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._bp, v = ln.visual, t0 = ln.start, span = Math.max(3, ctx.until - t0);
      tl.fromTo(S.st.querySelector(".bp-grid"), { opacity: 0 }, { opacity: 1, duration: .6, immediateRender: false }, t0);
      tl.fromTo(S.tb, { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: .5, ease: "power2.out", immediateRender: false }, t0 + .3);
      const n = S.drawn.length, each = Math.max(.25, Math.min(1.1, (span - 1.6) / Math.max(1, n)));
      let prev = t0 + .4;
      S.drawn.forEach((d, k) => {
        const tk = d.it.at ? when(ctx, d.it, prev) : prev + (k ? each * .8 : 0);
        tl.set(d.g, { opacity: 1 }, tk);
        // Nét đứt (dash tĩnh trong CSS) không vẽ dần được bằng dash-offset -> hiện dần.
        d.strokes.forEach((p) => p.classList.contains("dash")
          ? tl.fromTo(p, { opacity: 0 }, { opacity: 1, duration: .4, immediateRender: false }, tk)
          : draw(tl, p, tk, Math.min(1.2, each * 1.3), "power1.inOut"));
        d.texts.forEach((t) => tl.fromTo(t, { opacity: 0 }, { opacity: 1, duration: .3, immediateRender: false }, tk + Math.min(.9, each)));
        const fill = d.g.querySelector(".bp-fill"); if (fill) tl.fromTo(fill, { opacity: 0 }, { opacity: 1, duration: .6, ease: "power1.inOut", immediateRender: false }, tk + .4);
        prev = tk;
      });
      tl.fromTo(S.svg, { scale: 1 }, { scale: 1.025, duration: span, ease: "none", immediateRender: false, transformOrigin: "50% 45%" }, t0);
    },
  });

  /* ================= 6) KÝ HOẠ CHÌ — pencil ================= */
  // Giấy ký hoạ: đường dựng hình mờ trước, nét chì vẽ dần (hai lớp: nét phác nhạt + nét chính), tô bóng
  // bằng gạch chéo lộ dần, bóng đổ nhoè. Tiêu đề viết tay có gạch chân; ghi chú có mũi tên tại mốc.
  register("pencil", {
    build(inner, ln) {
      const v = ln.visual, sid = ln.sentence_id;
      // Nền tối (theme night, mặc định) = phấn trên bảng đá; nền sáng = chì trên giấy ký hoạ.
      const dark = v.tone ? v.tone === "dark" : theme() !== "paper";
      const st = el("div", "lf-stage lf-pn" + (dark ? " dark" : "")); inner.appendChild(st);
      st.appendChild(el("div", "pn-paper"));
      const svg = sv("svg", { viewBox: `0 0 ${W} ${H}`, width: W, height: H, class: "pn-svg" }, st);
      const defs = sv("defs", {}, svg);
      const pat = sv("pattern", { id: `pn-hatch-${sid}`, width: 9, height: 9, patternUnits: "userSpaceOnUse", patternTransform: "rotate(-35)" }, defs);
      sv("line", { x1: 0, y1: 0, x2: 0, y2: 9, class: "pn-hatch-line" }, pat);
      const clipId = `pn-clip-${sid}`, clip = sv("clipPath", { id: clipId }, defs), clipRect = sv("rect", { x: 0, y: 0, width: 0, height: H }, clip);  // x đặt lại ngay dưới (theo bbox)
      const pts0 = motifPts(v.scene, "pagoda"), bb0 = bboxOf(pts0);
      const s = Math.min((PORTRAIT ? 760 : 620) / (bb0.y1 - bb0.y0), (PORTRAIT ? 820 : 900) / (bb0.x1 - bb0.x0));
      const cx = PORTRAIT ? W / 2 : (v.title ? 1180 : W / 2), base = PORTRAIT ? 1150 : 840;
      const pts = shift(pts0, cx, base, s), bb = bboxOf(pts);
      // x của clip cố định từ lúc dựng; CHỈ tween width. (Bẫy 10/11: x chỉ có trong `from` của fromTo -> GSAP lấy
      // giá trị hiện tại lúc khởi tạo làm đích, kết quả phụ thuộc thứ tự seek -> mất tất định.)
      clipRect.setAttribute("x", bb.x0 - 10);
      // Đường dựng hình (guide)
      const guide = sv("g", { class: "pn-guide" }, svg);
      [bb.y0, (bb.y0 + bb.y1) / 2, bb.y1].forEach((y) => sv("line", { x1: bb.x0 - 120, y1: y, x2: bb.x1 + 120, y2: y }, guide));
      [bb.x0, cx, bb.x1].forEach((x) => sv("line", { x1: x, y1: bb.y0 - 90, x2: x, y2: bb.y1 + 60 }, guide));
      // Bóng đổ nhoè dưới chân
      const shadow = sv("ellipse", { cx: cx + 40, cy: base + 14, rx: (bb.x1 - bb.x0) * .55, ry: 22, class: "pn-shadow" }, svg);
      // Tô bóng: nửa phải của hình (gạch chéo) lộ dần bằng clip
      const fillG = sv("g", { "clip-path": `url(#${clipId})` }, svg);
      sv("path", { d: poly(pts, true), fill: `url(#pn-hatch-${sid})`, class: "pn-fill" }, fillG);
      // Nét: lớp phác nhạt lệch tay + nét chính
      const w = wobble(`pn|${sid}`, 4);
      const sketch = sv("path", { d: poly(pts.map((p) => [p[0] + w(), p[1] + w()])), class: "pn-stroke faint" }, svg);
      const main = sv("path", { d: poly(pts), class: "pn-stroke" }, svg);
      // Tiêu đề viết tay + gạch chân
      let title = null, under = null;
      if (v.title) { title = el("div", "pn-title" + (clean(v.title).length > 14 ? " long" : "")); title.appendChild(el("span", "", esc(v.title))); st.appendChild(title);
        if (PORTRAIT) Object.assign(title.style, { left: "80px", right: "80px", top: "220px", textAlign: "center" }); else Object.assign(title.style, { left: "140px", top: "250px", width: "560px" });
        const us = sv("svg", { viewBox: "0 0 100 100", preserveAspectRatio: "none", class: "pn-under" }, title);
        under = sv("path", { d: "M2,70 Q50,82 98,66", class: "pn-under-path", "vector-effect": "non-scaling-stroke" }, us); }
      if (v.sub && title) title.appendChild(el("div", "pn-sub", esc(v.sub)));
      // Ghi chú có mũi tên: notes [{text, x, y, at, word}] (x,y = điểm trỏ)
      const notes = (v.notes || []).slice(0, 4).map((nt, k) => {
        const g = sv("g", { class: "pn-note", opacity: 0 }, svg), side = nt.x > cx ? 1 : -1;
        const tx = nt.x + side * 150, ty = nt.y - 80 - k * 10;
        const arrow = sv("path", { d: smooth([[tx, ty + 10], [nt.x + side * 60, (ty + nt.y) / 2 + 20], [nt.x, nt.y]]), class: "pn-stroke thin" }, g);
        const t = sv("text", { x: tx, y: ty - 6, class: "pn-text", "text-anchor": side > 0 ? "start" : "end" }, g); t.textContent = nt.text || "";
        return { g, arrow, t, nt };
      });
      inner._pn = { st, svg, guide, shadow, clipRect, sketch, main, title, under, notes, bb };
    },
    enter(tl, inner, ln, ctx) {
      const S = inner._pn, v = ln.visual, t0 = ln.start, span = Math.max(3, ctx.until - t0);
      tl.fromTo(S.guide, { opacity: 0 }, { opacity: 1, duration: .5, ease: twos(.5), immediateRender: false }, t0 + .1);
      const dDraw = Math.min(3.2, Math.max(1.4, span * .35));
      draw(tl, S.sketch, t0 + .5, dDraw * .9, "power1.inOut");
      draw(tl, S.main, t0 + .8, dDraw, "power1.inOut");
      tl.fromTo(S.clipRect, { attr: { width: 0 } }, { attr: { width: S.bb.x1 - S.bb.x0 + 20 }, duration: 1.4, ease: twos(1.4), immediateRender: false }, t0 + .8 + dDraw * .7);
      tl.fromTo(S.shadow, { opacity: 0 }, { opacity: 1, duration: .8, immediateRender: false }, t0 + .8 + dDraw);
      tl.fromTo(S.guide, { opacity: 1 }, { opacity: .35, duration: .8, immediateRender: false }, t0 + .8 + dDraw);
      if (S.title) { const tt = stepAt(ctx, v, 0, t0 + .6);
        tl.fromTo(S.title, { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: .5, ease: "power2.out", immediateRender: false }, tt);
        tl.fromTo(S.under.ownerSVGElement, { clipPath: "inset(-20% 100% -20% 0%)" }, { clipPath: "inset(-20% 0% -20% 0%)", duration: .5, ease: twos(.5), immediateRender: false }, tt + .4); }
      S.notes.forEach((n, k) => { const tn = when(ctx, n.nt, t0 + 1.2 + dDraw + k * .9);
        tl.set(n.g, { opacity: 1 }, tn); draw(tl, n.arrow, tn, .5, "power1.out"); tl.fromTo(n.t, { opacity: 0 }, { opacity: 1, duration: .3, immediateRender: false }, tn + .35); });
      tl.fromTo(S.st, { scale: 1 }, { scale: 1.03, duration: span, ease: "none", immediateRender: false, transformOrigin: "50% 60%" }, t0);
    },
  });

  // Danh sách để bridge / test đối chiếu (chỉ đọc).
  window.HF_LONG_STYLES = Object.freeze(["woodcut", "papercut", "oneline", "film16", "blueprint", "pencil"]);
})();
