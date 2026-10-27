---
{
  "id": "0012_don_file_vao_thung_rac",
  "ten": "Dọn file sau khi đăng bằng cách chuyển vào Thùng rác, không xoá vĩnh viễn, và chỉ dọn khi YouTube đã xác nhận",
  "loai": "luat",
  "dinh_dang": [],
  "pham_vi": [
    "bud"
  ],
  "hop_ngach": [],
  "cam_ngach": [],
  "so_muc": 1,
  "so_nguon": 1,
  "nguon": [],
  "bang_chung_dung": [],
  "vi_du": [],
  "nguon_su_that": [
    "docs/adr/0012-don-file-vao-thung-rac.md:1"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "Trạng thái: đã chấp nhận (02/10/2026, bổ sung 20/10 và 22/10). Ổ đĩa đầy rất nhanh: một Long 30 phút cần khoảng 3 GB mp4, 3–6 GB file chương, và khoảng 12 GB tạm khi ghép cuối. Các sự cố đã gặp: - **04/10:** đợt dọn lúc 3:30 sáng xoá mất bản render lại của F10/B10, vì `uploaded.json` vẫn trỏ id cũ. Chủ kênh đổ Thùng rác nên mất hẳn. - **23/10:** short BUD đã đăng bị dọn mất mp4, nên bản TikTok phải render lại. Quy trình: 1. Sau mỗi đợt đăng, chạy `hf_cleanup.py` ở chế độ thử. 2. Chạy `--apply` để chuyển file vào `~/.Trash/vieneu_tu_don/<ngày>/`.",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `docs/adr/0012-don-file-vao-thung-rac.md:1`. Trạng thái: đã chấp nhận (02/10/2026, bổ sung 20/10 và 22/10). Ổ đĩa đầy rất nhanh: một Long 30 phút cần khoảng 3 GB mp4, 3–6 GB file chương, và khoảng 12 GB tạm khi ghép cuối. Các sự cố đã gặp: - **04/10:** đợt dọn lúc 3:30 sáng xoá mất bản render lại của F10/B10, vì `uploaded.json` vẫn trỏ id cũ. Chủ kênh đổ Thùng rác nên mất hẳn. - **23/10:** short BUD đã đăng bị dọn mất mp4, nên bản TikTok phải render lại. Quy trình: 1. Sau mỗi đợt đăng, chạy `hf_cleanup.py` ở chế độ thử.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
