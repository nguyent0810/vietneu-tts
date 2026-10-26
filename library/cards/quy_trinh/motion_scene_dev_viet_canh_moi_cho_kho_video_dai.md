---
{
  "id": "motion_scene_dev_viet_canh_moi_cho_kho_video_dai",
  "ten": "Viết cảnh mới cho kho video dài",
  "loai": "quy_trinh",
  "dinh_dang": [],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [],
  "cam_ngach": [],
  "so_muc": 1,
  "so_nguon": 1,
  "nguon": [],
  "bang_chung_dung": [],
  "vi_du": [],
  "nguon_su_that": [
    ".claude/skills/motion-scene-dev/SKILL.md:6"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "## Nơi đặt - Sơ đồ: `visuals.<type> = { build(inner, ln, i, ctx), enter(tl, inner, ln, ctx) }` trong `longform.js`; đăng ký `VISUAL_TYPES` trong `hyperframes_bridge.py`. `ctx.until` = giây kết thúc khoảng sơ đồ; `when(ctx, step, fallback)` ra thời điểm của `at`/`word`. - Bố cục ảnh: `layouts.<name> = { build, enter?, enterCont?, motion?(tl, clip, ln, mEnd) }` (motion trả true = tự lo chuyển động clip); thêm vào `MEDIA_LAYOUTS` (+ `LAYOUT_POOL`). - Biến thể: `variantOf(\"<họ>\", spec, [...])` — bộ chọn lo luân phiên. - CSS: `longform.css`; màu theo biến `--lf-*` (nền giấy ghi đè trong `inkwash_long.html`).",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/motion-scene-dev/SKILL.md:6`. ## Nơi đặt - Sơ đồ: `visuals.<type> = { build(inner, ln, i, ctx), enter(tl, inner, ln, ctx) }` trong `longform.js`; đăng ký `VISUAL_TYPES` trong `hyperframes_bridge.py`. `ctx.until` = giây kết thúc khoảng sơ đồ; `when(ctx, step, fallback)` ra thời điểm của `at`/`word`. - Bố cục ảnh: `layouts.<name> = { build, enter?, enterCont?, motion?(tl, clip, ln, mEnd) }` (motion trả true = tự lo chuyển động clip); thêm vào `MEDIA_LAYOUTS` (+ `LAYOUT_POOL`). - Biến thể: `variantOf("<họ>",.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
