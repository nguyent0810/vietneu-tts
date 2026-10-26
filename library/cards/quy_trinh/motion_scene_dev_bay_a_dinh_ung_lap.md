---
{
  "id": "motion_scene_dev_bay_a_dinh_ung_lap",
  "ten": "Bẫy đã dính (đừng lặp)",
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
    ".claude/skills/motion-scene-dev/SKILL.md:23"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "| Triệu chứng | Nguyên nhân | Cách đúng | |---|---|---| | Phần tử hiện lơ lửng từ giây 0 | `fromTo` vẽ trạng thái đầu ngay lúc dựng | CSS mặc định ẩn + `tl.set` + `tl.to` | | Dạ quang/nét vẽ lệch chữ | đo `getBoundingClientRect` khi font chưa nạp | phần tử CON của thứ được đánh dấu, đặt bằng `inset`, SVG viewBox 0..100 | | Chữ trích dẫn trắng trên giấy | class `.w` trùng chữ phụ đề trong base.css | đặt tiền tố riêng (`qw`, `lf-*`) | | Nét vẽ tay chỉ còn vệt ngắn | `<svg>` tuyệt đối với left+right không giãn | ghi rõ `width/height` | | Nét thành chấm 1px | `non-scaling-stroke` làm dash theo pixel | lộ dần bằng `clipPath` / mặt nạ `conic-gradient` | | Thẻ tên nhảy khỏi ghim | tween `x` ghi đè ",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/motion-scene-dev/SKILL.md:23`. | Triệu chứng | Nguyên nhân | Cách đúng | |---|---|---| | Phần tử hiện lơ lửng từ giây 0 | `fromTo` vẽ trạng thái đầu ngay lúc dựng | CSS mặc định ẩn + `tl.set` + `tl.to` | | Dạ quang/nét vẽ lệch chữ | đo `getBoundingClientRect` khi font chưa nạp | phần tử CON của thứ được đánh dấu, đặt bằng `inset`, SVG viewBox 0..100 | | Chữ trích dẫn trắng trên giấy | class `.w` trùng chữ phụ đề trong base.css | đặt tiền tố riêng (`qw`, `lf-*`) | | Nét vẽ tay chỉ còn vệt ngắn | `<svg>` tuy.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
