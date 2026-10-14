# Thêm thiết bị mới

1. Tìm có sẵn: `npx hyperframes@0.8.75 catalog --query "<động tác, tiếng Anh>" --json` (Node 22). Có -> port logic (đọc nguồn read-only, không `add` vào repo
   nếu chỉ lấy ý). Không -> đọc rule/blueprint liên quan trong `/hyperframes-animation`.
2. File `hyperframes_short/studio/devices/<nhóm>.js`:
```js
HFS.device("ten_thiet_bi", {
  meta: { purpose: "number", framing: "grid", axis: "X", circle: 0, energy: "M" },
  css: `.tt-x{position:absolute;left:100px;top:420px;color:var(--accent)}`,   // CHỈ biến token, không hex
  build(c, s, st, i) {          // dựng DOM trong st (.stage); KHÔNG tween ở đây; trả về mọi thứ enter cần
    const box = c.el("div", "tt-x", null, st); return { box };
  },
  enter(c, h, t0, s) {          // tween ở giây tuyệt đối; mốc đã là số: c.t(s.at, mặc_định)
    c.reveal(h.box, c.t(s.at, t0 + .3), { y: 30 });
  },
});
```
3. Công cụ trong `c`: `tl, T (token), E (ease: entry/exit/move/draw/pop()), S(d) (nhân tốc độ theme), el, sv, words(box,text,{mask}), waterfall,
   spread, reveal, underline, draw(path,t,d), stamp, burst(parent,x,y,t,key), count(node,from,to,t,d,fmt), rng(key), dur, lines, fail`.
4. Luật: `fromTo` có from tường minh, `immediateRender:false` cho tween sau; ẩn/hiện bằng `autoAlpha`; không Math.random (dùng `c.rng(key)`);
   không repeat:-1; không tween width/height/fontSize/letterSpacing; mốc `Math.max(0,t)`; không đo layout lúc tween (gắn phần tử con tuyệt đối);
   chồng lớp có chủ ý -> `data-layout-allow-overlap`.
5. Thêm metadata vào `DEVICES` trong `studio.py` (khớp `meta`) + mục trong `references/devices.md`.
6. Demo trong một spec, chạy `--render --qa`, xem bảng khung, thử tua ngược (qa.md bước 4).
