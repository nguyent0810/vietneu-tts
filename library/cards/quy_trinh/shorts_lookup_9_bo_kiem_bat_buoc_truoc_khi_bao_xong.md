---
{
  "id": "shorts_lookup_9_bo_kiem_bat_buoc_truoc_khi_bao_xong",
  "ten": "9. Bộ kiểm bắt buộc trước khi báo xong",
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
    ".claude/skills/shorts-lookup/SKILL.md:153"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "mo_ta_nguon": "Mọi short (FS và BUD) trước khi gửi Lead review phải vượt qua 6 cổng kiểm tra tự động và thủ công: 1. **Tràn chữ (Overflow check)**: Chạy script kiểm tra bounding box trên headless browser, xác nhận `n = 0` phần tử bị tràn viền; font độ đậm 900 hiển thị đầy đủ dấu tiếng Việt. 2. **Safe-zone & Top $\\ge 40$**: Đo tại 4 mốc thời gian (10%, 35%, 65%, khung cuối), xác nhận mép trên chữ cách đỉnh $\\ge 40\\text{px}$, không đè chip danh mục ($y < 110$). 3. **Đo khoảng trống dọc & Độ phủ**: Bề ngang an toàn phủ $\\ge 85\\%$ ($cover \\ge 880\\text{px}$); không có khoảng cách dọc giữa các khối $> 250\\text{px}$. 4. **Soát 2 kích thước hiển thị**: - Khung $1080\\times 1920$: Rõ nét, không răng cưa, bố cục cân ",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---

## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/shorts-lookup/SKILL.md:153`. Mọi short (FS và BUD) trước khi gửi Lead review phải vượt qua 6 cổng kiểm tra tự động và thủ công: 1. **Tràn chữ (Overflow check)**: Chạy script kiểm tra bounding box trên headless browser, xác nhận `n = 0` phần tử bị tràn viền; font độ đậm 900 hiển thị đầy đủ dấu tiếng Việt. 2. **Safe-zone & Top $\ge 40$**: Đo tại 4 mốc thời gian (10%, 35%, 65%, khung cuối), xác nhận mép trên chữ cách đỉnh $\ge 40\text{px}$, không đè chip danh mục ($y < 110$). 3. **Đo khoảng trống dọc & Độ p.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
