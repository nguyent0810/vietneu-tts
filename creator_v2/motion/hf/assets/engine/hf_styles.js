/* Cảnh style #258 cho casewide (CL / MIM / CK). Nạp SAU chart.js và longform_styles.js, TRƯỚC casewide.js.
   casewide đã gọi window.chartScenes. File này bọc hook đó để gắn builder style.
   Không sửa casewide.js — chương cũ giữ nguyên render_key. Không nạp file này thì bảng cảnh cũ giữ nguyên. */
(() => {
  const prev = window.chartScenes;
  const NAMES = ["woodcut", "papercut", "oneline", "film16", "blueprint", "pencil"];
  function mount(name, s, d, tl, el, C) {
    const pack = window.HF_LONG && HF_LONG.visuals && HF_LONG.visuals[name];
    if (!pack) throw new Error("thiếu HF_LONG.visuals." + name + " — nạp longform_styles_boot.js rồi longform_styles.js");
    const words = (s.words || []).map((w) => (typeof w === "string" ? { w: w, t: s.t0 } : w));
    const sid = s.sid || (s.steps && s.steps[0] && s.steps[0].at) || 1;
    const ln = { start: s.t0, end: s.t1, words: words, visual: s, sentence_id: sid };
    const lines = (C.lines || []).map((L) => ({ start: L.start || 0, end: L.end || 0, words: L.words || [] }));
    if (!lines.length) lines.push({ start: s.t0, end: s.t1, words: words });
    // longform untilOf trả GIÂY cuối khoảng sơ đồ. Số câu trong plan (until: 41) không phải giây.
    let until = s.t1;
    if (typeof s.until === "number" && s.until > s.t0 && s.until <= s.t1 + 0.5) until = s.until;
    const ctx = { LINES: lines, start: s.t0, end: s.t1, words: words, until: until };
    const host = el("div", "hf-style-host", null, d);
    host.style.cssText = "position:absolute;inset:0";
    pack.build(host, ln, 0, ctx);
    if (pack.enter) pack.enter(tl, host, ln, ctx);
  }
  window.chartScenes = (ctx) => {
    if (typeof prev === "function") prev(ctx);
    const { B, tl, el, C } = ctx;
    NAMES.forEach((name) => { B[name] = (s, d) => mount(name, s, d, tl, el, C); });
  };
})();
