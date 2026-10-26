---
{
  "id": "motion_scene_dev_luat_tat_inh_hyperframes_tua_toi_tung_khung_roi",
  "ten": "Luật tất định (HyperFrames tua tới từng khung rồi chụp)",
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
    ".claude/skills/motion-scene-dev/SKILL.md:17"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "- Mọi chuyển động nằm trên `tl` đã pause. Không `Math.random` (dùng `HF.rng(HF.hashSeed(..))`), không `Date`, không mạng lúc render (địa lý nướng sẵn bằng `hf_geo`). - Trạng thái thay đổi liên tục (hạt, số đếm, shader): MỘT tween tiến trình + `onUpdate` tính từ `t` — không đặt tween ở thời điểm âm, không `tl.call`.",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/motion-scene-dev/SKILL.md:17`. - Mọi chuyển động nằm trên `tl` đã pause. Không `Math.random` (dùng `HF.rng(HF.hashSeed(..))`), không `Date`, không mạng lúc render (địa lý nướng sẵn bằng `hf_geo`). - Trạng thái thay đổi liên tục (hạt, số đếm, shader): MỘT tween tiến trình + `onUpdate` tính từ `t` — không đặt tween ở thời điểm âm, không `tl.call`.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
