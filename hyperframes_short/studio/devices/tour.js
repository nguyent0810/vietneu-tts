/* TOUR devices -- máy quay dạo trên MỘT tư liệu thật (phù điêu, tranh cổ, bản đồ, ảnh xưa).
 * Mỗi điểm dừng = một mốc lời đọc: camera trượt (move ease) tới chi tiết, vòng tròn vẽ tay quanh chi tiết, nhãn chú thích.
 * Giữa hai điểm dừng camera trôi rất chậm (không đứng chết). Không filter lên ảnh (giữ màu thật của tư liệu).
 * Spec: { src (bridge điền từ museum/file/query), w, h, label, credit,
 *         stops: [ { x, y (0..1 trên ảnh), z (độ phóng, 1 = toàn ảnh), at, note, r (bán kính vòng, px màn hình) } ] }
 */
HFS.device("pan_tour", {
  meta: { purpose: "evidence", framing: "full-bleed", axis: "camera", circle: 0, energy: "C" },
  css: `.pt-vp{position:absolute;left:0;top:250px;width:1080px;height:1180px;overflow:hidden;background:var(--ink)}
        .pt-lab{position:absolute;left:100px;top:180px;font-size:28px;color:var(--accent)}
        .pt-cred{position:absolute;right:110px;top:1444px;font-size:18px;color:var(--soft-text,#6B6156);max-width:860px;text-align:right}
        .pt-note{position:absolute;padding:10px 20px 12px;background:var(--card, var(--ground));color:var(--ink);font-weight:900;font-size:44px;
                 border-left:8px solid var(--accent);white-space:nowrap;box-shadow:0 12px 30px var(--shadow, rgba(0,0,0,.25))}`,
  cssW: `.pt-vp{position:absolute;left:150px;top:108px;width:1620px;height:742px;overflow:hidden;background:var(--ink);box-shadow:0 0 0 3px var(--ink),0 0 0 12px var(--ground),0 0 0 14px var(--line),0 26px 60px var(--shadow, rgba(0,0,0,.2))}
        .pt-lab{position:absolute;left:640px;right:150px;top:58px;font-size:24px;color:var(--accent);text-align:right;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
        .pt-cred{position:absolute;right:150px;top:862px;font-size:16px;color:var(--soft-text,#6B6156);max-width:1200px;text-align:right}
        .pt-note{position:absolute;padding:10px 22px 12px;background:var(--card, var(--ground));color:var(--ink);font-weight:900;font-size:40px;
                 border-left:8px solid var(--accent);white-space:nowrap;box-shadow:0 12px 30px var(--shadow, rgba(0,0,0,.25))}`,
  build(c, s, st, i) {
    st.setAttribute("data-layout-allow-overlap", "");
    const vp = c.el("div", "pt-vp", null, st), W = c.L.wide ? 1620 : 1080, H = c.L.wide ? 742 : 1180;
    // Toàn cảnh = vừa khít (contain) trên nền mờ của chính ảnh ấy -> thấy trọn tư liệu, rồi mới phóng vào chi tiết.
    const iw = s.w || 1600, ih = s.h || 1000, s0 = Math.min(W / iw, H / ih), Iw = iw * s0, Ih = ih * s0;
    const bd = c.el("img", "", null, vp); bd.src = s.src || s.img || "";
    bd.style.cssText = "position:absolute;inset:-40px;width:calc(100% + 80px);height:calc(100% + 80px);object-fit:cover;filter:blur(28px) brightness(.55);opacity:.9";
    const cam = c.el("div", "", null, vp); cam.style.cssText = `position:absolute;left:0;top:0;width:${Iw}px;height:${Ih}px;transform-origin:0 0`;
    const img = c.el("img", "", null, cam); img.src = s.src || s.img || ""; img.style.cssText = `width:${Iw}px;height:${Ih}px;display:block`;
    const svg = c.sv("svg", { width: W, height: H, style: "position:absolute;left:0;top:0;overflow:visible" }, vp);
    if (s.label) c.el("div", "pt-lab mono", c.esc(s.label), st);
    if (s.credit) c.el("div", "pt-cred mono", c.esc(s.credit), st);
    // Toạ độ camera cho từng điểm dừng (kẹp để không lộ mép ảnh), vị trí chi tiết trên màn hình sau khi kẹp.
    const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
    const fit = (want, size, view) => (size <= view ? (view - size) / 2 : clamp(want, view - size, 0));   // ảnh nhỏ hơn khung -> giữa
    const pose = (p) => { const z = Math.max(1, p.z || 1), px = (p.x != null ? p.x : .5) * Iw, py = (p.y != null ? p.y : .5) * Ih;
      const tx = fit(W / 2 - px * z, Iw * z, W), ty = fit(H / 2 - py * z, Ih * z, H);
      return { z, tx, ty, px, py, sx: tx + px * z, sy: ty + py * z }; };
    const r = c.rng("pt" + i);
    const stops = (s.stops || []).map((p, k) => { const P = pose(p); let ring = null, note = null;
      if (p.note) { const R = p.r || 120, j = () => (r() - .5) * 10;
        // vòng vẽ tay: hai nét elip lệch nhau một chút
        const d = `M${P.sx + R},${P.sy + j()} A${R + j()},${R * .78 + j()} -8 1 1 ${P.sx + R * .96},${P.sy - R * .2} ` +
                  `M${P.sx + R * .9},${P.sy - R * .25} A${R * 1.04},${R * .8} 4 0 1 ${P.sx + R * 1.08},${P.sy + R * .12}`;
        ring = c.sv("path", { d, style: "fill:none;stroke:var(--accent)", "stroke-width": 6, "stroke-linecap": "round", opacity: 0 }, svg);
        note = c.el("div", "pt-note", c.esc(p.note), vp);
        const nw = 23 * p.note.length + 70, right = P.sx + R + 24 + nw < W - 16;     // ước bề rộng nhãn; không đủ chỗ thì sang trái vòng
        note.style.left = clamp(right ? P.sx + R + 24 : P.sx - R - 24 - nw, 16, W - nw - 16) + "px";
        note.style.top = clamp(P.sy - R - 10, 12, H - 90) + "px"; }
      return { P, ring, note }; });
    return { cam, stops, base: pose({ x: .5, y: .5, z: 1 }) };
  },
  enter(c, h, t0, s) {
    const tl = c.tl, END = c.dur || t0 + 8, mv = c.S(1.5);
    tl.set(h.cam, { x: h.base.tx, y: h.base.ty, scale: 1 }, 0);
    tl.fromTo(h.cam, { scale: 1.04 }, { scale: 1, duration: c.S(1.2), ease: c.E.entry, immediateRender: false }, t0);
    const times = h.stops.map((p, k) => Math.max(t0 + .4 + k * .2, c.t(s.stops[k].at, t0 + 1 + k * 2.5)));
    h.stops.forEach((p, k) => {
      const ta = times[k], next = k + 1 < times.length ? times[k + 1] : END, P = p.P;
      tl.to(h.cam, { x: P.tx, y: P.ty, scale: P.z, duration: mv, ease: c.E.move }, ta);
      // trôi rất chậm quanh chi tiết cho tới điểm dừng sau (giữ chi tiết ở chỗ cũ trên màn hình)
      const z2 = P.z * 1.035, hold = Math.max(.3, next - (ta + mv) - .05);
      tl.to(h.cam, { x: P.sx - P.px * z2, y: P.sy - P.py * z2, scale: z2, duration: hold, ease: "none" }, ta + mv);
      if (p.ring) { c.draw(p.ring, ta + mv - .1, .6); tl.to(p.ring, { opacity: 0, duration: .25 }, Math.max(ta + mv + .6, next - .1)); }
      if (p.note) { c.reveal(p.note, ta + mv + .2, { x: -24, y: 0, d: .4 }); tl.to(p.note, { autoAlpha: 0, duration: .25 }, Math.max(ta + mv + .8, next - .1)); }
    });
  },
});
