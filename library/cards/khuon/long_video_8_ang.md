---
{
  "id": "long_video_8_ang",
  "ten": "8. Đăng",
  "loai": "khuon",
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
    ".claude/skills/long-video/SKILL.md:144"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "mo_ta_nguon": "`upload_long.py --only <id> --confirm`: riêng tư + hẹn giờ, dò sâu khung giờ (search.list cộng dồn), mục lục chương có mốc, ghi nguồn ảnh + nhạc đúng track đã trộn, gắn thumbnail, thêm playlist (công khai, idempotent). Mỗi kênh một API project, quota riêng; hết quota search thì chờ reset 14:00 VN, không đăng mù. Kiểm lại bằng video ID (privacy, publishAt). `upload_long` gọi `seo_check.check_row` (ticket 69) trước mỗi lần đăng: ERROR thì dừng (bỏ qua bằng `--seo-ok`). Plan khai `\"seo\": {\"keyword\": \"...\"}` + tag đầu trùng keyword; keyword nằm trong 4 từ đầu tiêu đề, 150 ký tự đầu mô tả và 3 câu đầu lời đọc. Tiêu đề > 60 ký tự, < 8 tag, > 5 hashtag chỉ cảnh báo.",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---

## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/long-video/SKILL.md:144`. `upload_long.py --only <id> --confirm`: riêng tư + hẹn giờ, dò sâu khung giờ (search.list cộng dồn), mục lục chương có mốc, ghi nguồn ảnh + nhạc đúng track đã trộn, gắn thumbnail, thêm playlist (công khai, idempotent). Mỗi kênh một API project, quota riêng; hết quota search thì chờ reset 14:00 VN, không đăng mù. Kiểm lại bằng video ID (privacy, publishAt). `upload_long` gọi `seo_check.check_row` (ticket 69) trước mỗi lần đăng: ERROR thì dừng (bỏ qua bằng `--seo-ok`). Plan kha.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
