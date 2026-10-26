---
{
  "id": "references_1_bo_kiem_6_buoc_bat_buoc_cho_tho",
  "ten": "1. Bộ kiểm 6 bước bắt buộc cho Thợ",
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
    ".claude/skills/shorts-studio/references/qa.md:13"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "1. **Kiểm tràn chữ (Overflow Check)**: - Chạy script kiểm tra bounding box trên headless Chrome: `overflow n = 0`. - Bắt buộc kiểm tra `font900 = có` đối với tiêu đề và chữ số chính; không có ký tự bị cắt dấu tiếng Việt (Ấ, Ầ, Ỗ, Ữ, Ự...). 2. **Safe-Zone & Top $\\ge 40$**: - Đo tại 4 mốc thời gian: 10%, 35%, 65% và khung cuối (100%). - Mép trên của thành phần hiển thị phải cách đỉnh ít nhất $40\\text{px}$ (`top >= 40`), không đè lên chip danh mục ($y < 110$). - Giới hạn trên: Tiêu đề nằm trong $y = 110 - 400$. - Giới hạn dưới: Toàn bộ nội dung/CTA không vượt quá $y = 1473\\text{px}$; phụ đề nằm dưới $y = 1490$. 3. **Đo khoảng trống dọc & Độ phủ an toàn**: - Độ phủ bề ngang: Phủ $\\ge 85\\%$ bề ng",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/shorts-studio/references/qa.md:13`. 1. **Kiểm tràn chữ (Overflow Check)**: - Chạy script kiểm tra bounding box trên headless Chrome: `overflow n = 0`. - Bắt buộc kiểm tra `font900 = có` đối với tiêu đề và chữ số chính; không có ký tự bị cắt dấu tiếng Việt (Ấ, Ầ, Ỗ, Ữ, Ự...). 2. **Safe-Zone & Top $\ge 40$**: - Đo tại 4 mốc thời gian: 10%, 35%, 65% và khung cuối (100%). - Mép trên của thành phần hiển thị phải cách đỉnh ít nhất $40\text{px}$ (`top >= 40`), không đè lên chip danh mục ($y < 110$). - Giới hạn trên: T.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
