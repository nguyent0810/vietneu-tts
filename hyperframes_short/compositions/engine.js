/* Engine dùng chung cho mọi style "cinematic" của kênh Hình Sự.
 *
 * Mỗi style chỉ cần khai báo window.HF_STYLE = { buildScene, transition,
 * ambient } rồi gọi HF.build(). Engine lo phần bất biến giữa các style:
 * đọc biến, dựng scene theo từng câu narration, dựng phụ đề karaoke theo
 * timing THẬT của TTS, gắn audio, đăng ký timeline.
 *
 * Ràng buộc bất biến (xem hyperframes-core/determinism-rules):
 *  - mọi trạng thái hình ảnh phải suy ra được từ thời gian -> không
 *    Date.now/Math.random (dùng PRNG có seed), không repeat:-1.
 *  - scene KHÔNG phải .clip: composition nhiều cảnh có transition thì
 *    GSAP tự quản opacity, framework không được tranh quyền ẩn/hiện.
 *  - luôn fromTo (không from) để trạng thái đầu là tường minh.
 */
window.HF = (function () {
  function rng(seed) {                     // mulberry32 -- ngẫu nhiên nhưng tất định
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function el(tag, cls, txt) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt != null) e.textContent = txt;
    return e;
  }

  function hexA(hex, a) {
    const h = (hex || "#e5484d").replace("#", "");
    const n = parseInt(h.length === 3 ? h.split("").map(c => c + c).join("") : h, 16);
    return `rgba(${(n >> 16) & 255},${(n >> 8) & 255},${n & 255},${a})`;
  }


  /* ---- Đồ hoạ thông tin -------------------------------------------------
   * Nhận SEMANTIC figure theo hf_figure_schema.json ({type, data, ...}) và tự
   * quyết định toàn bộ hình học + chữ định dạng (ADR-0001). Python không tính
   * sẵn gì cả.
   *
   * ADR-0002: ở đây CHỈ được sinh chữ thuần định dạng từ số (2000000 ->
   * "2 TRIỆU"). Mọi nhãn mang khẳng định pháp lý phải đến từ `labels` — chữ
   * người viết đặt tay trong plan. Không bao giờ tự chế ra mệnh đề pháp lý.
   */
  const THRESHOLD_SPLIT = 42;          // % chiều ngang — lựa chọn bố cục, không phải dữ liệu

  function viNumber(n) {
    const rounded = Math.round(n * 10) / 10;
    return Number.isInteger(rounded) ? String(rounded) : String(rounded).replace(".", ",");
  }

  function formatQuantity(value, unit) {
    const u = (unit || "").toLowerCase();
    if (u === "đồng") {
      if (value >= 1e9) return viNumber(value / 1e9) + " TỶ";
      if (value >= 1e6) return viNumber(value / 1e6) + " TRIỆU";
      if (value >= 1e3) return viNumber(value / 1e3) + " NGHÌN";
      return viNumber(value) + " ĐỒNG";
    }
    return viNumber(value) + " " + (unit || "").toUpperCase();
  }

  function buildFigure(fig, labels) {
    const L = labels || {};
    const d = fig.data || {};
    const box = el("div", "fig fig-" + fig.type);

    if (fig.type === "threshold") {
      const q = formatQuantity(d.value, d.unit);
      const at = THRESHOLD_SPLIT + "%";
      const axis = el("div", "axis");
      const lo = el("div", "lo"), hi = el("div", "hi"), mark = el("div", "mark"), pin = el("div", "pin", q);
      lo.style.width = at; hi.style.left = at; mark.style.left = at; pin.style.left = at;
      axis.appendChild(lo); axis.appendChild(hi); axis.appendChild(mark); axis.appendChild(pin);
      box.appendChild(axis);
      const labelRow = el("div", "labels");
      labelRow.appendChild(el("div", "l", L.left || ("Dưới " + q.toLowerCase())));
      labelRow.appendChild(el("div", "r", L.right || ((d.direction === "above" ? "Trên " : "Từ ") + q.toLowerCase())));
      box.appendChild(labelRow);
      if (L.note) box.appendChild(el("div", "note", L.note));

    } else if (fig.type === "range") {
      const a = formatQuantity(d.from.value, d.from.unit);
      const b = formatQuantity(d.to.value, d.to.unit);
      const rail = el("div", "rail");
      rail.appendChild(el("div", "bar"));
      rail.appendChild(el("div", "edge start", a));
      rail.appendChild(el("div", "edge stop", b));
      box.appendChild(rail);
      if (L.note) box.appendChild(el("div", "note", L.note));

    } else if (fig.type === "flow") {
      (d.steps || []).forEach((st, i) => {
        if (i) box.appendChild(el("div", "arrow", "→"));
        const cls = "step" + (st.terminal ? " end" : "") + (st.text.length > 34 ? " long" : "");
        box.appendChild(el("div", cls, st.text));
      });

    } else if (fig.type === "timeline") {
      const points = (d.points || []).slice().sort((a, b) => a.year - b.year);
      const rail = el("div", "rail");
      const line = el("div", "line");
      rail.appendChild(line);
      const span = Math.max(1, points.length - 1);
      points.forEach((pt, i) => {
        const tick = el("div", "tick");
        tick.style.left = (span ? (i / span) * 100 : 50) + "%";
        tick.appendChild(el("div", "dot"));
        tick.appendChild(el("div", "year", String(pt.year)));
        if (pt.text) tick.appendChild(el("div", "what", pt.text));
        rail.appendChild(tick);
      });
      box.appendChild(rail);
      if (L.note) box.appendChild(el("div", "note", L.note));

    } else if (fig.type === "stat") {
      const big = el("div", "big");
      big.dataset.target = String(d.value);
      big.dataset.unit = d.unit || "";
      big.textContent = formatQuantity(0, d.unit);
      box.appendChild(big);
      if (d.of != null) {
        const track = el("div", "track");
        const fill = el("div", "fill");
        fill.style.width = Math.max(0, Math.min(100, (d.value / d.of) * 100)) + "%";
        track.appendChild(fill);
        box.appendChild(track);
      }
      if (L.note) box.appendChild(el("div", "note", L.note));
    }
    return box;
  }

  function animateFigure(tl, box, fig, at) {
    tl.fromTo(box, { opacity: 0, y: 26 }, { opacity: 1, y: 0, duration: .42, ease: "power3.out" }, at);

    if (fig.type === "threshold") {
      tl.fromTo(box.querySelector(".lo"), { scaleX: 0 }, { scaleX: 1, duration: .5, ease: "power2.out" }, at + .1);
      tl.fromTo(box.querySelector(".hi"), { scaleX: 0 }, { scaleX: 1, duration: .6, ease: "power3.out" }, at + .34);
      tl.fromTo(box.querySelector(".mark"), { scaleY: 0 }, { scaleY: 1, duration: .34, ease: "back.out(2)" }, at + .5);
      tl.fromTo(box.querySelector(".pin"), { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: .34 }, at + .58);
      tl.fromTo(box.querySelectorAll(".labels div"), { opacity: 0 }, { opacity: 1, duration: .34, stagger: .1 }, at + .66);

    } else if (fig.type === "range") {
      tl.fromTo(box.querySelector(".bar"), { scaleX: 0 }, { scaleX: 1, duration: .68, ease: "power3.out" }, at + .12);
      tl.fromTo(box.querySelector(".edge.start"), { opacity: 0, x: -14 }, { opacity: 1, x: 0, duration: .34 }, at + .3);
      tl.fromTo(box.querySelector(".edge.stop"), { opacity: 0, x: 14 }, { opacity: 1, x: 0, duration: .34 }, at + .52);

    } else if (fig.type === "flow") {
      box.querySelectorAll(".step").forEach((st, i) => {
        tl.fromTo(st, { opacity: 0, y: 24, scale: .95 },
          { opacity: 1, y: 0, scale: 1, duration: .4, ease: "power3.out" }, at + .08 + i * .22);
      });
      box.querySelectorAll(".arrow").forEach((ar, i) => {
        tl.fromTo(ar, { opacity: 0, x: -10 }, { opacity: 1, x: 0, duration: .26 }, at + .3 + i * .22);
      });

    } else if (fig.type === "timeline") {
      tl.fromTo(box.querySelector(".line"), { scaleX: 0 }, { scaleX: 1, duration: .7, ease: "power2.out" }, at + .1);
      box.querySelectorAll(".tick").forEach((tk, i) => {
        tl.fromTo(tk, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: .32, ease: "power3.out" }, at + .3 + i * .18);
      });

    } else if (fig.type === "stat") {
      const big = box.querySelector(".big");
      if (big) {
        const state = { v: 0 }, target = Number(big.dataset.target) || 0, unit = big.dataset.unit;
        tl.to(state, { v: target, duration: .9, ease: "power2.out",
                       onUpdate: () => { big.textContent = formatQuantity(state.v, unit); } }, at + .12);
      }
      const fill = box.querySelector(".fill");
      if (fill) tl.fromTo(fill, { scaleX: 0 }, { scaleX: 1, duration: .7, ease: "power2.out" }, at + .2);
    }
  }

  // Thuật toán gom 3–6 tiếng/cụm theo nhịp đọc cho video dài (010b)
  const LONG_COMPOUNDS = new Set([
    "làm ăn", "hoạn nạn", "hưởng dụng", "để dành", "tiền bạc", "tại gia", "chối bỏ",
    "khôn ngoan", "tài chính", "nguyên tắc", "hôm nay", "ngày mai", "đời sống", "hằng ngày",
    "gia đình", "đồng vốn", "sinh sôi", "phòng thân", "sáu phương", "cha mẹ", "thầy dạy",
    "vợ con", "bạn bè", "người làm", "làm công", "tu hành", "niềm vui", "người có",
    "đồng tiền", "tiền vàng", "triều đại", "ấn độ", "thước đo", "giàu sang", "đinh ba",
    "bái lạy", "gia chủ", "phần tư", "quỹ phòng", "bài kinh", "bậc tu", "đăng ký",
    "phật dạy", "đức phật", "người gia", "khắc cốt", "ghi tâm", "hoàng đạo", "hắc đạo",
    "kinh doanh", "cưới hỏi", "khai trương", "làm nhà", "nhập trạch", "tam nương",
    "nguyệt kỵ", "dương công", "thiên can", "địa chi", "ngũ hành", "phong thủy", "tử vi",
    "con giáp", "phát tài", "may mắn", "tài lộc", "an lạc", "từ bi", "trí tuệ", "giải thoát",
    "nhân quả", "luân hồi", "nghiệp báo", "tiền thân", "lịch sử", "thời gian", "không gian",
    "con người", "cuộc sống", "sức khỏe", "bình an", "bình luận", "chia sẻ", "theo dõi", "vạn sự", "như ý"
  ]);

  function splitLongChunks(words, lineEnd) {
    if (!words || !words.length) return [];
    const n = words.length;
    if (n <= 6) {
      const single = words.slice();
      single.lineEnd = lineEnd;
      return [single];
    }
    function cleanWord(str) {
      return String(str || "").replace(/\*\*/g, "").replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, "").toLowerCase();
    }
    function isCompound(w1, w2) {
      const c1 = cleanWord(w1.w);
      const c2 = cleanWord(w2.w);
      if (LONG_COMPOUNDS.has(c1 + " " + c2)) return true;
      const raw1 = String(w1.w || "").replace(/\*\*/g, "").replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, "");
      const raw2 = String(w2.w || "").replace(/\*\*/g, "").replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, "");
      if (raw1 && raw2 && /^\p{Lu}/u.test(raw1) && /^\p{Lu}/u.test(raw2)) return true;
      return false;
    }
    const dp = new Array(n + 1).fill(Infinity);
    const prev = new Array(n + 1).fill(-1);
    dp[0] = 0;
    for (let i = 1; i <= n; i++) {
      for (let L = 3; L <= 6; L++) {
        const j = i - L;
        if (j < 0 || dp[j] === Infinity) continue;
        let cutCost = 0;
        if (j > 0) {
          const wPrev = words[j - 1];
          const wCurr = words[j];
          const hasPunct = /[.,…?!:;]$/.test(wPrev.w);
          if (hasPunct) cutCost -= 60;
          else cutCost += 10;
          if (!hasPunct && isCompound(wPrev, wCurr)) cutCost += 250;
        }
        const lenCost = Math.abs(L - 4.5) * 2;
        const cost = dp[j] + cutCost + lenCost;
        if (cost < dp[i]) {
          dp[i] = cost;
          prev[i] = j;
        }
      }
    }
    if (dp[n] === Infinity) {
      let cur = [];
      const res = [];
      words.forEach((w, k) => {
        cur.push(w);
        if (cur.length >= 5 || k === n - 1) { cur.lineEnd = lineEnd; res.push(cur); cur = []; }
      });
      return res;
    }
    const res = [];
    let curr = n;
    while (curr > 0) {
      const p = prev[curr];
      const c = words.slice(p, curr);
      c.lineEnd = lineEnd;
      res.push(c);
      curr = p;
    }
    res.reverse();
    return res;
  }

  function build() {
    const V = window.__hyperframes.getVariables();
    const LINES = typeof V.lines === "string" ? JSON.parse(V.lines || "[]") : (V.lines || []);
    const DUR = Number(V.duration) || 30;
    const KC2 = V.kc === "v2";   // plan "kinetic": thẻ chữ động + mở chương đặc trưng (video dài)
    const STYLE = window.HF_STYLE || {};
    const root = document.getElementById("root");
    const rand = rng(hashSeed(V.kicker + "|" + (LINES[0] && LINES[0].words && LINES[0].words[0] ? LINES[0].words[0].w : "")));

    root.style.setProperty("--accent", V.accent);
    root.style.setProperty("--accent-30", hexA(V.accent, 0.30));
    root.style.setProperty("--accent-12", hexA(V.accent, 0.12));
    const setText = (id, t) => { const n = document.getElementById(id); if (n) n.textContent = t || ""; };
    setText("kicker", V.kicker); setText("badge", V.badge); setText("footer", V.footer);

    // --- scene: 1 câu narration = 1 cảnh, cảnh đầu hiện sẵn, còn lại opacity 0 ---
    const stage = document.getElementById("stage");
    // Video dài (longform.js): bố cục ảnh khác ô mặc định, sơ đồ, thẻ chương.
    // Style không nạp longform.js thì LONG = null và mọi thứ như cũ.
    const LONG = window.HF_LONG || null;
    const OVERLAY_TYPES = { ask: 1, timeline: 1, stat: 1, list: 1 };
    const isOverlay = (ln) => {
      const v = ln && (ln.visual || (ln.visual_cont && LINES[ln.visual_cont - 1] && LINES[ln.visual_cont - 1].visual));
      return !!(LONG && v && v.overlay && OVERLAY_TYPES[v.type]);
    };
    const segOff = Number(V.seg_off) || 0;
    if (LONG) {
      // Cổng mở đầu 40s (026): câu không có hình không được rơi về thẻ chữ khoá trên nền trống
      // (kể cả kinetic: true) — giữ hình của mốc trước; thẻ overlay: true phủ lên ảnh đang chạy.
      let lastMediaIdx = -1;
      LINES.forEach((ln, i) => {
        if (ln.chapter_no || ln.heading) { lastMediaIdx = -1; return; }
        if (ln.media) { lastMediaIdx = i; return; }
        const inOpening = (segOff + (Number(ln.start) || 0)) < 40;
        const hasBlockingVis = (ln.visual || ln.visual_cont) && !isOverlay(ln);
        const hasFig = ln.figure && ln.figure.type && ln.figure.type !== "none";
        if (lastMediaIdx >= 0 && !hasBlockingVis && !hasFig && (inOpening || isOverlay(ln))) {
          if (!ln.media_cont) ln.media_cont = LINES[lastMediaIdx].sentence_id;
          const prevOwner = LINES[ln.media_cont - 1] || LINES[lastMediaIdx];
          if (prevOwner) prevOwner.media_end = Math.max(prevOwner.media_end || prevOwner.end, ln.end);
        }
      });
    }
    if (LONG && LONG.begin) LONG.begin(LINES, V);  // hạt giống cho bộ chọn biến thể
    const layoutOf = (ln) => {
      const m = ln.media || (ln.media_cont && LINES[ln.media_cont - 1].media) || null;
      return (LONG && m && m.layout && LONG.layouts[m.layout]) ? LONG.layouts[m.layout] : null;
    };
    const visualOf = (ln) => (LONG && ln.visual && LONG.visuals[ln.visual.type]) || null;
    // Hết khoảng của một sơ đồ = cuối câu cuối cùng nó còn chiếm màn hình.
    const untilOf = (i) => { let k = i; while (k + 1 < LINES.length && LINES[k + 1].visual_cont === LINES[i].sentence_id) k++; return LINES[k].end; };
    const scenes = LINES.map((ln, i) => {
      const s = el("div", "scene");
      s.id = "scene" + i;
      s.style.opacity = i === 0 ? "1" : "0";
      const inner = el("div", "scene-inner");
      s.appendChild(inner);
      stage.appendChild(s);
      if (visualOf(ln) && isOverlay(ln)) {
        s.classList.add("has-visual", "has-overlay");
        if (ln.media || ln.media_cont) s.classList.add("has-media");
        visualOf(ln).build(inner, ln, i, { rand, V, LINES });
      } else if (ln.media) {
        // MÀN VIDEO: một loại màn khác hẳn, không phải thẻ thường có dán
        // thêm clip. Style tự quyết cắt khung, che tối, nhãn, chữ.
        s.classList.add("has-media");
        const lay = layoutOf(ln);
        if (lay) lay.build(inner, ln, i, { rand, V });
        else (STYLE.buildMediaScene || defaultMediaScene)(inner, ln, i, LINES.length, { rand, V });
        mediaTag(inner, ln.media);
      } else if (visualOf(ln)) {
        s.classList.add("has-visual");
        visualOf(ln).build(inner, ln, i, { rand, V, LINES });
      } else if (ln.visual_cont) {
        // cảnh rỗng: sơ đồ của câu gốc vẫn đứng trên màn hình
      } else if (LONG && ln.chapter_no) {
        (KC2 && LONG.signatureChapter ? LONG.signatureChapter : LONG.chapter).build(inner, ln, i, { rand, V });
      } else if (ln.media_cont && layoutOf(ln)) {
        s.classList.add("has-media");
        layoutOf(ln).build(inner, ln, i, { rand, V });
        mediaTag(inner, LINES[ln.media_cont - 1].media);
      } else if (ln.media_cont) {
        // Câu nối tiếp của một ảnh đang giữ (video dài): dựng lại ĐÚNG khung
        // đó ở trạng thái đứng yên, không có hoạt cảnh vào. Ảnh vẫn là clip
        // của câu gốc, chạy xuyên suốt bên dưới.
        s.classList.add("has-media");
        (STYLE.buildMediaScene || defaultMediaScene)(inner, ln, i, LINES.length, { rand, V });
        mediaTag(inner, LINES[ln.media_cont - 1].media);
      } else if (KC2 && LONG && LONG.keycard) {
        // Plan "kinetic": thẻ chữ động thế hệ mới thay cảnh chữ khoá đứng yên của style.
        s.classList.add("has-visual");
        LONG.keycard.build(inner, ln, i, { rand, V, LINES });
      } else if (STYLE.buildScene) {
        STYLE.buildScene(inner, ln, i, LINES.length, { rand, V });
      }
      if (ln.figure && ln.figure.type !== "none") {
        s.classList.add("has-fig");
        inner.appendChild(buildFigure(ln.figure, ln.figure_labels));
      }
      return s;
    });

    // --- phụ đề: lớp riêng NẰM TRÊN transition, chữ luôn đọc được ---
    const capzone = document.getElementById("capzone");
    // Nền giấy mực (video dài): thẻ chương là vết mực đen phủ cả vùng phụ đề, tên chương đã to giữa màn
    // -> bỏ phụ đề của câu tiêu đề chương (chữ tối trên mực đen không đọc được).
    const NO_CHAP_CAP = !!(LONG && capzone.classList.contains("skin-ink"));
    const caps = LINES.map((ln) => {
      const cap = el("div", "cap");
      (NO_CHAP_CAP && ln.chapter_no ? [] : (ln.words || [])).forEach(w => {
        const span = el("span", "w" + (w.hot ? " hot" : ""), w.w);
        const on = el("span", "on", w.w);
        span.appendChild(on);
        cap.appendChild(span);
      });
      cap.style.opacity = "0";
      // Video dài: ảnh/clip đứng ở khung cố định (đáy ~y=785). Phụ đề 4 dòng mọc cao quá đáy khung,
      // dòng đầu đè lên ảnh (lỗi F10/B10/F11 03/10/2026). Câu dài trên màn ảnh -> chữ gọn, khối rộng hơn, giữ <= 3 dòng.
      // 04/10/2026: mở rộng cho MỌI câu dài của video dài -- thẻ trích kinh/sơ đồ cũng đứng trên phụ đề
      // (câu kinh 60 chữ thành 5 dòng phụ đề, đè thẻ trích ở B13).
      if (LONG) {
        const n = (ln.words || []).reduce((a, w) => a + String(w.w).length + 1, 0);
        if (n > 290) cap.classList.add("cap-dense3");
        else if (n > 225) cap.classList.add("cap-dense2");
        else if (n > 165) cap.classList.add("cap-dense");
      }
      capzone.appendChild(cap);
      return cap;
    });

    // Phụ đề cụm chữ (Phase D, S-tier; 010b Long: gom 3–6 chữ theo nhịp đọc, hiện cả cụm, tô chữ đang đọc)
    const CHUNK = V.caps === "chunk" || V.subs === "chunk";
    const isLong = Boolean(LONG || V.lane === "long" || (typeof document !== "undefined" && (document.body.classList.contains("wide") || document.documentElement.getAttribute("data-resolution") === "landscape")));
    const chunks = [];
    if (CHUNK) {
      capzone.classList.add("caps-chunk");
      LINES.forEach((ln) => {
        if (ln.visual && ln.visual.type === "ask") return;
        // Chữ trồi: thẻ đã hiện từng từ đúng lúc đọc, phụ đề cụm sẽ lặp lại chữ.
        if (ln.visual && ln.visual.type === "quote" && ln.visual.variant === "rise") return;
        if ((LONG || NO_CHAP_CAP) && ln.chapter_no) return;
        const ws = ln.words || [];
        if (!ws.length) return;
        if (isLong) {
          const lchunks = splitLongChunks(ws, ln.end);
          lchunks.forEach((c) => chunks.push(c));
        } else {
          let cur = [];
          ws.forEach((w, k) => {
            cur.push(w);
            if (/[.,…?!:;]$/.test(w.w) || cur.length >= 4 || k === ws.length - 1) { cur.lineEnd = ln.end; chunks.push(cur); cur = []; }
          });
        }
      });
      chunks.forEach((c) => {
        const box = el("div", "ck");
        c.forEach((w) => box.appendChild(el("span", "cw" + (w.hot || /\d/.test(w.w) ? " acc" : ""), String(w.w).replace(/\*\*/g, ""))));
        capzone.appendChild(box);
        c.box = box;
      });
    }

    // Lớp điện ảnh phủ CẢ video, không riêng màn ảnh -- vá từng chỗ thì mỗi
    // màn một chất, mất cảm giác cùng một cuộn phim. Chỉ BUD: nhịp chiêm
    // nghiệm chịu được hạt phim, nhịp nhanh và căng của CL thì không.
    let grain = null;
    if (V.series === "bud") {
      const cine = el("div"); cine.id = "cine";
      grain = el("div", "cine-grain");
      cine.appendChild(grain);
      cine.appendChild(el("div", "cine-bloom"));
      root.appendChild(cine);
    }

    const tl = gsap.timeline({ paused: true });

    if (STYLE.ambient) STYLE.ambient(tl, DUR, { rand, V, root });
    if (LONG && LONG.ambient) LONG.ambient(tl, DUR, { rand, V, root, LINES });  // hạt bay, vệt sáng

    if (grain) {
      // Hạt phim đứng yên là bụi trên ống kính, không phải hạt phim. Nhảy
      // từng nấc bằng steps() -- vẫn tất định, không dùng Math.random.
      tl.fromTo(grain, { backgroundPosition: "0px 0px" },
        { backgroundPosition: "190px 190px", duration: DUR, ease: "steps(" + Math.max(8, Math.round(DUR * 1.4)) + ")" }, 0);
    }

    // Chuyển cảnh qua kho hiệu ứng (longform.js) nếu style có nạp; kho từ chối
    // (hoặc style không nạp) thì dùng chuyển cảnh riêng của style như cũ.
    const clipOfGroup = (k) => {
      const L = LINES[k], gid = L.media_cont || (L.media && L.sentence_id);
      return gid ? document.getElementById("mediaclip" + gid) : null;
    };
    const transit = (oldIdx, newIdx, T) => {
      const cOld = clipOfGroup(oldIdx), cNew = clipOfGroup(newIdx);
      const ctx = {
        rand,
        V,
        toChapter: !!(LONG && LINES[newIdx].chapter_no),
        oldClip: (cOld && cOld === cNew) ? null : cOld,
        oldLn: LINES[oldIdx],
        newLn: LINES[newIdx],
      };
      if (LONG && LONG.transition && LONG.transition(tl, scenes[oldIdx], scenes[newIdx], T, ctx)) return;
      (STYLE.transition || defaultTransition)(tl, scenes[oldIdx], scenes[newIdx], T, { rand, V });
    };

    LINES.forEach((ln, i) => {
      const inner = scenes[i].firstChild;
      if (ln.media) {
        const clip = document.getElementById("mediaclip" + (i + 1));
        const hasCine = !!(LONG && LONG.cine && ln.media.cine);
        const hasPan = !!(LONG && LONG.pan && ln.media.pan);
        let lastContIdx = i;
        for (let k = i + 1; k < LINES.length; k++) {
          if (LINES[k].media_cont === ln.sentence_id) lastContIdx = k;
          else break;
        }
        const nextLn = (lastContIdx + 1 < LINES.length) ? LINES[lastContIdx + 1] : null;
        if (clip) {
          // Khung tự bật/tắt thẻ media theo data-start -- tức là CẮT CỨNG,
          // trong khi mọi thứ còn lại đều chuyển mềm. Đó là cú khựng. Fade
          // opacity bằng GSAP để hai đầu màn nối liền. (opacity hợp lệ trên
          // .clip; chỉ display/visibility là cấm.)
          // Ảnh có `cine` hoặc `pan` tự quản lý opacity/transition_in trong longform.js.
          if (!hasCine && !hasPan) {
            if (i === 0 || ln.start === 0) {
              // Mở đầu video (0s): media hiện sẵn từ giây 0, không fade-in từ đen/trống
              tl.set(clip, { opacity: 1 }, 0);
            } else {
              tl.fromTo(clip, { opacity: 0 },
                { opacity: 1, duration: .55, ease: "sine.out" }, ln.start);
            }
            // Tắt clip: thay vì tắt sớm ở (mEnd - 0.45) làm lộ nền kem trắng trơn
            // trong khoảng lặng giữa các câu, giữ clip xuyên suốt khoảng lặng tới tận
            // câu kế tiếp (nextLn.start) để crossfade mượt mà với cảnh sau.
            let fadeOutStart;
            if (nextLn) {
              if (nextLn.chapter_no || nextLn.heading) {
                const gap = nextLn.start - LINES[lastContIdx].end;
                fadeOutStart = gap > 0.25 ? nextLn.start - 0.35 : Math.max(ln.start + 0.6, LINES[lastContIdx].end - 0.35);
              } else {
                fadeOutStart = nextLn.start;
              }
            } else {
              fadeOutStart = Math.max(ln.start + .6, (ln.media_end || ln.end) - .45);
            }
            tl.to(clip, { opacity: 0, duration: .45, ease: "sine.in" }, fadeOutStart);
          }

          // Mask nở theo CẢ khung 1080x1920, trong khi cửa sổ nhìn thấy nhỏ
          // hơn nhiều -- để 210% thì nó phủ kín trước khi mắt kịp thấy.
          const how = ln.media.reveal || "";
          if (how === "ink") {
            // Vệt mực loang: ảnh thấm ra từ một điểm thay vì bật lên.
            tl.fromTo(clip, { "--ink": "4%" },
              { "--ink": "115%", duration: 2.6, ease: "power1.inOut" }, ln.start);
          } else if (how === "wipe") {
            tl.fromTo(clip, { "--wipe": "16%" },
              { "--wipe": "132%", duration: 1.9, ease: "power2.out" }, ln.start);
          } else if (how === "iris") {
            tl.fromTo(clip, { "--iris": "14%" },
              { "--iris": "128%", duration: 2.0, ease: "power2.out" }, ln.start);
          } else if (how === "rise") {
            tl.fromTo(clip, { "--rise": "16%" },
              { "--rise": "132%", duration: 1.9, ease: "power2.out" }, ln.start);
          }
        }
        const lay = layoutOf(ln);
        if (clip && hasPan && (!lay || !lay.motion)) {
          LONG.pan(tl, clip, ln, ln.media_end || ln.end);
        } else if (clip && hasCine && (!lay || !lay.motion)) {
          LONG.cine(tl, clip, ln, ln.media_end || ln.end);
        } else if (clip && lay && lay.motion && lay.motion(tl, clip, ln, ln.media_end || ln.end)) {
          // bố cục tự lo chuyển động của clip (thẻ 3D, màn chia đôi, cine, hoặc pan)
        } else if (clip) {
          // Ken Burns: clip đứng yên trong 6 giây là ảnh tĩnh biết nhúc nhích.
          // BUD đi chậm hơn: 1.12 trong sáu giây là cú đẩy thấy rõ, hợp nhịp
          // căng của CL; ở đây nó làm khuôn hình bồn chồn.
          const kb = V.series === "bud" ? 1.075 : 1.12;
          const kbx = (ln.kb_dir || -1.5) * (V.series === "bud" ? 0.6 : 1);
          const animEnd = nextLn ? nextLn.start : (ln.media_end || ln.end);
          tl.fromTo(clip, { scale: 1.0, xPercent: 0 },
            { scale: kb, xPercent: kbx,
              duration: Math.max(1, animEnd - ln.start), ease: "none" }, ln.start);
        }
        if (visualOf(ln) && isOverlay(ln)) {
          visualOf(ln).enter(tl, inner, ln, { rand, V, LINES, i, until: untilOf(i) });
        } else if (lay) { if (lay.enter) lay.enter(tl, inner, ln, i, { rand, V, clip }); }
        else (STYLE.enterMedia || defaultEnterMedia)(tl, inner, ln, i, { rand, V, clip });
      } else if (visualOf(ln)) {
        visualOf(ln).enter(tl, inner, ln, { rand, V, LINES, i, until: untilOf(i) });
        if (isOverlay(ln) && ln.media_cont && (segOff + (Number(ln.start) || 0)) < 40 && LONG && LONG.holdCameraMove) {
          LONG.holdCameraMove(tl, clipOfGroup(i), ln, i, { rand, V, LINES });
        }
      } else if (ln.visual_cont) {
        // sơ đồ gốc tự chạy các bước của nó
      } else if (LONG && ln.chapter_no) {
        (KC2 && LONG.signatureChapter ? LONG.signatureChapter : LONG.chapter).enter(tl, inner, ln, { rand, V });
      } else if (ln.media_cont) {
        const lay2 = layoutOf(ln);
        if (lay2 && lay2.enterCont) lay2.enterCont(tl, inner, ln);
        if ((segOff + (Number(ln.start) || 0)) < 40 && LONG && LONG.holdCameraMove) {
          LONG.holdCameraMove(tl, clipOfGroup(i), ln, i, { rand, V, LINES });
        }
      } else if (KC2 && LONG && LONG.keycard && inner._kc) {
        LONG.keycard.enter(tl, inner, ln, { rand, V, LINES, i, until: ln.end });
      } else if (STYLE.enter) {
        STYLE.enter(tl, inner, ln, i, { rand, V });
      }
      if (ln.figure && ln.figure.type !== "none") {
        animateFigure(tl, inner.querySelector(".fig"), ln.figure, ln.start + .34);
      }

      // Transition sang cảnh kế: cảnh ra và cảnh vào chạy CÙNG mốc T --
      // bản thân chuyển động LÀ cú bàn giao, không fade-out rồi mới vào.
      if (i < LINES.length - 1) {
        const nx = LINES[i + 1];
        // Khoảng nghỉ có chủ đích (video dài, hf_voice) thuộc về câu VỪA nói: giữ cảnh
        // qua khoảng lặng, chuyển ngay trước câu sau. Nghỉ ngắn (short) giữ như cũ.
        const T = nx.start - ln.end > 0.25 ? nx.start - 0.34 : Math.max(ln.start + 0.2, ln.end - 0.34);
        const vg = ln.visual_cont || (ln.visual && ln.sentence_id);
        if (nx.visual_cont && nx.visual_cont === vg) {
          // cùng một sơ đồ: không chuyển cảnh
        } else if (ln.visual_cont) {
          transit(ln.visual_cont - 1, i + 1, T);
        } else if (!visualOf(ln) && !visualOf(nx) && nx.media_cont && nx.media_cont === (ln.media_cont || (ln.media && ln.sentence_id))) {
          // Cùng một ảnh, cùng một khung: tráo cảnh tức thì. Crossfade hai
          // khung giống hệt nhau làm độ phủ tụt giữa chừng, và ảnh full-frame
          // bên dưới loé qua lớp giấy.
          tl.set(scenes[i], { opacity: 0 }, T);
          tl.set(scenes[i + 1], { opacity: 1 }, T);
        } else {
          transit(i, i + 1, T);
        }
      }

      // Phụ đề + karaoke theo timing thật của TTS (chế độ cụm chữ / câu hỏi lặng: bỏ qua)
      const cap = caps[i];
      // Câu trích đánh máy / chữ trồi: thẻ đã mang trọn câu -> phụ đề lặp lại và đè đáy thẻ.
      if (CHUNK || (ln.visual && (ln.visual.type === "ask" || (ln.visual.type === "quote" && (ln.visual.variant === "type" || ln.visual.variant === "rise"))))) return;
      tl.fromTo(cap, { opacity: 0, y: 22 }, { opacity: 1, y: 0, duration: 0.24, ease: "power2.out" }, ln.start);
      if (i < LINES.length - 1) {
        const gap = LINES[i + 1].start - ln.end;   // nghỉ dài: phụ đề ở lại qua khoảng lặng như cảnh
        tl.to(cap, { opacity: 0, duration: 0.14, ease: "power1.in" }, gap > 0.6 ? LINES[i + 1].start - 0.1 : ln.end - 0.1);
      }
      (ln.words || []).forEach((w, k) => {
        const on = cap.children[k] && cap.children[k].querySelector(".on");
        if (!on) return;
        tl.set(on, { opacity: 1 }, w.t);
        tl.set(on, { opacity: 0 }, w.t + w.d);
      });
    });

    chunks.forEach((c, n) => {
      // Tắt ở cụm kế HOẶC cuối câu của nó (cụm cuối trước câu hỏi lặng không được đọng sang).
      const t0 = c[0].t - .06, nx = chunks[n + 1], t1 = Math.min(nx ? nx[0].t - .06 : DUR - .3, c.lineEnd + .15);
      tl.set(c.box, { opacity: 1 }, t0);
      if (isLong) {
        // Long: hiện cả cụm 3–6 chữ, tô chữ đang đọc theo nhịp (010b)
        c.forEach((w, k) => {
          const elW = c.box.children[k];
          const baseCls = elW.className.replace(/\blit\b/g, "").trim();
          const tStart = Math.max(t0, w.t - .03);
          const tEnd = k < c.length - 1 ? Math.max(tStart + .08, c[k + 1].t - .03) : Math.min(t1, w.t + Math.max(.14, w.d || .25));
          tl.set(elW, { attr: { class: baseCls } }, t0);
          tl.set(elW, { attr: { class: baseCls + " lit" } }, tStart);
          tl.set(elW, { attr: { class: baseCls } }, tEnd);
        });
      } else {
        // Short: hiện từng chữ từ dưới lên
        c.forEach((w, k) => tl.fromTo(c.box.children[k], { opacity: 0, y: 14, scale: .92 },
          { opacity: 1, y: 0, scale: 1, duration: .12, ease: "power2.out" }, w.t - .04));
      }
      tl.set(c.box, { opacity: 0 }, Math.min(t1, DUR - .3));
    });

    // Kết vòng lặp (V.loop): những khung cuối trở lại cảnh mở màn -> Shorts lặp lại
    // liền mạch, người xem dễ xem tiếp vòng hai.
    if (V.loop && scenes.length > 1) {
      const lastLoop = LINES[LINES.length - 1];
      const lastS = lastLoop && lastLoop.visual_cont ? scenes[lastLoop.visual_cont - 1] : scenes[scenes.length - 1];
      tl.to(lastS, { opacity: 0, duration: .3, ease: "power2.in" }, DUR - .45);
      tl.to(scenes[0], { opacity: 1, duration: .3, ease: "power2.out" }, DUR - .45);
      if (HOOK_SHORT(V)) hookFirstFrame(tl);
      window.__timelines["main"] = tl; tl.seek(0);
      addAudio(root, "narration", V.narration, 1, null, DUR);
      addAudio(root, "bgm", V.bgm, V.bgm_gain != null ? V.bgm_gain : 0.16, 1.2, DUR);
      return;
    }

    // Cảnh cuối là cảnh DUY NHẤT được phép có animation thoát
    const lastLn = LINES[LINES.length - 1];
    const last = lastLn && lastLn.visual_cont ? scenes[lastLn.visual_cont - 1] : scenes[scenes.length - 1];
    if (last) tl.to(last, { opacity: 0, duration: 0.5, ease: "power2.in" }, Math.max(0, DUR - 0.5));
    const lastCap = caps[caps.length - 1];
    if (lastCap) tl.to(lastCap, { opacity: 0, duration: 0.4, ease: "power2.in" }, Math.max(0, DUR - 0.45));

    addAudio(root, "narration", V.narration, 1, null, DUR);
    addAudio(root, "bgm", V.bgm, V.bgm_gain != null ? V.bgm_gain : 0.16, 1.2, DUR);

    if (HOOK_SHORT(V)) hookFirstFrame(tl);

    // KIỂM TRẠNG THÁI O9 (0–40s): tại mọi thời điểm 0–min(40, DUR)s phải có ≥1 lớp media/visual đã tải xong hiện ≥ 50% độ mờ
    // Render theo chương: mỗi chương là một composition riêng có seg_off; O9 chỉ xét phần nằm trong 0–40s của CẢ video.
    const o9Off = Number(V.seg_off) || 0;
    if (LONG_MODE() && !V.loop && o9Off < 40.0) {
      const mediaClips = Array.from(root.querySelectorAll(".media-clip, .lf-cine-wrap, .lf-pan-canvas"));
      const visualScenes = Array.from(root.querySelectorAll(".lf-scene"));
      const targets = [...mediaClips, ...visualScenes];
      if (targets.length > 0) {
        const maxCheckT = Math.min(40.0 - o9Off, DUR);
        const step = 0.2;
        const violations = [];
        for (let t = 0; t <= maxCheckT + 1e-4; t += step) {
          tl.seek(t);
          let maxOp = 0;
          for (const el of targets) {
            const op = parseFloat(getComputedStyle(el).opacity) || 0;
            const ds = el.dataset.start != null ? parseFloat(el.dataset.start) : -1;
            const dd = el.dataset.duration != null ? parseFloat(el.dataset.duration) : -1;
            let active = true;
            if (ds >= 0 && dd >= 0) {
              active = (t >= ds - 0.05 && t <= ds + dd + 0.05);
            }
            const loaded = (el.tagName !== "IMG" || (el.complete && el.naturalWidth > 0));
            if (active && loaded && op > maxOp) {
              maxOp = op;
            }
          }
          if (maxOp < 0.5) {
            violations.push({ t: Math.round(t * 10) / 10, maxOp: Math.round(maxOp * 100) / 100 });
          }
        }
        tl.seek(0);
        if (violations.length > 0) {
          const errMsg = "[O9 LỖI] 0–40s có thời điểm thiếu lớp media/visual (opacity < 50%): " + JSON.stringify(violations);
          console.error(errMsg);
          throw new Error(errMsg);
        } else {
          console.log("[O9 ĐẠT] Kiểm trạng thái media/visual 0–40s: toàn bộ thời điểm đều có lớp hiện >= 50% độ mờ.");
        }
      }
    }

    window.__timelines["main"] = tl;
    tl.seek(0);
  }

  // Video dài: nhãn loại tư liệu (TƯ LIỆU / ẢNH MINH HOẠ / VIDEO MINH HOẠ) + dòng ghi nguồn, góc trên phải.
  // Chỉ dựng khi bridge truyền label (plan video dài); short giữ nguyên như cũ.
  function mediaTag(inner, m) {
    if (!LONG_MODE() || !m || !m.label) return;
    const tag = el("div", "lf-media-tag");
    tag.appendChild(el("span", "lf-media-label", m.label));
    if (m.credit) tag.appendChild(el("span", "lf-media-credit", m.credit));
    inner.appendChild(tag);
  }
  function LONG_MODE() { return !!window.HF_LONG; }

  function defaultMediaScene(inner, ln, i, n) {
    const veil = el("div", "media-veil");
    inner.appendChild(veil);
    const slug = el("div", "media-slug", "TƯ LIỆU MINH HOẠ");
    inner.appendChild(slug);
  }

  function defaultEnterMedia(tl, inner, ln) {
    tl.fromTo(inner.querySelector(".media-veil"), { opacity: 0 }, { opacity: 1, duration: .5 }, ln.start);
    const slug = inner.querySelector(".media-slug");
    if (slug) tl.fromTo(slug, { opacity: 0, x: -14 }, { opacity: 1, x: 0, duration: .45 }, ln.start + .15);
  }

  function defaultTransition(tl, oldS, newS, T) {
    tl.to(oldS, { opacity: 0, duration: 0.34, ease: "power2.inOut" }, T);
    tl.to(newS, { opacity: 1, duration: 0.34, ease: "power2.inOut" }, T);
  }

  // Móc 1 giây (06/10/2026): khung 0 của short từng TRỐNG -- chữ móc gõ dần, ảnh/nhãn/phụ đề hiện dần trong ~1 giây,
  // người lướt feed thấy màn tối rồi lướt (engaged chỉ 20-45% view). Mọi tween HIỆN VÀO ngắn (<= 1,5 s, không lặp)
  // bắt đầu trong 0,9 s đầu được chạy xong rồi gỡ: phần tử đứng sẵn ở trạng thái cuối từ khung 0. Không dời vị trí
  // âm (GSAP sẽ đẩy cả timeline lùi, lệch tiếng); chuyển động dài (zoom chậm, hạt bay) và mọi mốc sau giữ nguyên.
  // Phụ đề (#capzone) giữ nguyên: chữ karaoke phải khớp tiếng (bản đầu hiện "đát" ở giây 0 khi giọng mới đọc "Nam").
  // Chỉ short dọc của BUD/FS (kênh CL không đụng tới); plan cũ không có cờ loop nên không dựa vào V.loop.
  function HOOK_SHORT(V) { return document.documentElement.dataset.resolution === "portrait" && (V.series === "bud" || V.series === "fs"); }
  function hookFirstFrame(tl) {
    const cz = document.getElementById("capzone");
    const inCap = (c) => cz && (c.targets ? c.targets() : []).some((t) => t && t.nodeType === 1 && cz.contains(t));
    tl.getChildren(false, true, false).forEach((c) => {
      // hé lộ ảnh bằng mặt nạ (--ink/--wipe/--iris/--rise, 1,9-2,6 s) cũng phải xong ở khung 0 -- plan cũ mở bằng ảnh có reveal
      const reveal = c.vars && ["--ink", "--wipe", "--iris", "--rise"].some((k) => k in c.vars);
      if (c.startTime() < 0.9 && (c.duration() <= 1.5 || reveal) && !c.repeat() && !inCap(c)) { c.progress(1); c.kill(); }
    });
  }

  function addAudio(root, id, src, vol, fadeOut, dur) {
    if (!src) return;
    const a = document.createElement("audio");
    a.id = id; a.className = "clip"; a.src = src;
    a.dataset.start = "0"; a.dataset.duration = String(dur);
    if (vol != null) a.dataset.volume = String(vol);
    if (fadeOut) a.dataset.fadeOut = String(fadeOut);
    root.appendChild(a);
  }

  function hashSeed(s) {
    let h = 2166136261;
    for (let i = 0; i < (s || "").length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  }

  return { build, el, hexA, rng, hashSeed, splitLongChunks };
})();
