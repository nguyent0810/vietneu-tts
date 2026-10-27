---
{
  "id": "references_4_chu_khoa_va_tieu_e_chuong_dsl_build_x_py",
  "ten": "4. Chữ khoá và tiêu đề chương (DSL build_X.py)",
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
    ".claude/skills/long-script/references/line-rules.md:50"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "- `**cụm**` giữa câu = chữ khoá (chữ động, callout). **Một cụm mỗi câu, 1-4 tiếng**, là danh từ / con số mang nghĩa (\"**da bọc lấy xương**\", \"**năm tuổi**\", \"**42**\"), không phải hư từ. Câu không có visual, ảnh hay chữ khoá thì engine lấy mấy chữ đầu câu làm tiêu đề lớn (`bare_lines`, lỗi F1/B1 01/10) -> mỗi câu cần một chữ khoá hoặc một visual. - `chap(\"Tiêu đề\")` = dòng in đậm TRỌN -> thẻ chương + mốc trong mô tả + điểm cắt render. Tiêu đề **được đọc to**: 2-7 tiếng, là điều người xem tìm hoặc một cảnh (\"Tuổi Tý\", \"Lọ hoa đặt bên nào?\", \"Đêm dưới cội Bồ Đề\"); không \"Phần 1\", không định nghĩa (\"X là gì?\") làm chương thứ hai (F1, F3, F6 rơi mạnh ở đúng chương ấy). - Không đặt `**...**` trọn ",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/long-script/references/line-rules.md:50`. - `**cụm**` giữa câu = chữ khoá (chữ động, callout). **Một cụm mỗi câu, 1-4 tiếng**, là danh từ / con số mang nghĩa ("**da bọc lấy xương**", "**năm tuổi**", "**42**"), không phải hư từ. Câu không có visual, ảnh hay chữ khoá thì engine lấy mấy chữ đầu câu làm tiêu đề lớn (`bare_lines`, lỗi F1/B1 01/10) -> mỗi câu cần một chữ khoá hoặc một visual. - `chap("Tiêu đề")` = dòng in đậm TRỌN -> thẻ chương + mốc trong mô tả + điểm cắt render. Tiêu đề **được đọc to**: 2-7 tiếng, là điề.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
