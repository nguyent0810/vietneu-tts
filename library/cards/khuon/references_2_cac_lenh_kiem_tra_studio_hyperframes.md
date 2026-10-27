---
{
  "id": "references_2_cac_lenh_kiem_tra_studio_hyperframes",
  "ten": "2. Các lệnh kiểm tra Studio HyperFrames",
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
    ".claude/skills/shorts-studio/references/qa.md:40"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "1. `npx hyperframes@0.8.75 lint --json`: Phải 0 lỗi. Lỗi bất kỳ (vd: `font_family_without_font_face`) làm `check` bỏ qua soát trình duyệt (\"0 sample\" $\\ne$ đạt). 2. `npx hyperframes@0.8.75 check --json --at <giữa mỗi cảnh>`: `ok:true` (runtime 0 lỗi JS, layout 0 lỗi, contrast 0 lỗi). 3. `qa_sheet.jpg` (16 khung): Nhìn tổng quan khung 0 đủ nghĩa, chữ không tràn dải phụ đề, cảnh không bị trống trơ trọi. 4. Kiểm tra tua ngược (với thiết bị mới): `snapshot --at T_muộn,T_sớm` so với `snapshot --at T_sớm`. 5. Âm thanh (`ffprobe` + LUFS): - Thời lượng khớp `data-duration`. - BUD: Đo âm lượng giọng đọc và BGM, xác nhận chênh lệch đạt đúng $-20.0\\text{ dB}$ LUFS; chuông CC0 vang ở giây 0; nhạc giảm n",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `.claude/skills/shorts-studio/references/qa.md:40`. 1. `npx hyperframes@0.8.75 lint --json`: Phải 0 lỗi. Lỗi bất kỳ (vd: `font_family_without_font_face`) làm `check` bỏ qua soát trình duyệt ("0 sample" $\ne$ đạt). 2. `npx hyperframes@0.8.75 check --json --at <giữa mỗi cảnh>`: `ok:true` (runtime 0 lỗi JS, layout 0 lỗi, contrast 0 lỗi). 3. `qa_sheet.jpg` (16 khung): Nhìn tổng quan khung 0 đủ nghĩa, chữ không tràn dải phụ đề, cảnh không bị trống trơ trọi. 4. Kiểm tra tua ngược (với thiết bị mới): `snapshot --at T_muộn,T_sớm` so v.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
