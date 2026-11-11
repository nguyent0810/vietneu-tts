/* Tối thiểu để longform_styles.js đăng ký HF_LONG.visuals trên trang casewide,
   nơi không nạp engine.js / longform.js. el, rng, hashSeed giữ đúng hợp đồng
   của compositions/engine.js. Không gọi HF.build(). */
window.HF = window.HF || (function () {
  function rng(seed) {
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
  function hashSeed(s) {
    let h = 2166136261;
    for (let i = 0; i < (s || "").length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
    return h >>> 0;
  }
  return { el, rng, hashSeed };
})();
window.HF_LONG = window.HF_LONG || { visuals: {} };
