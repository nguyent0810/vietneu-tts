---
{
  "id": "year_table",
  "ten": "Bảng tra năm",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giai_thich",
    "tra_cuu",
    "van_hoa"
  ],
  "cam_ngach": [],
  "so_muc": 0,
  "so_nguon": 0,
  "nguon": [],
  "bang_chung_dung": [
    "output/cl_staging/build_fs_tables_1013.py",
    "output/cl_staging/build_shorts_fs_test_1013.py",
    "output/cl_staging/grok/build_fs2027.py",
    "output/cl_staging/grok/build_r1026.py",
    "output/cl_staging/grok/build_r1027.py"
  ],
  "vi_du": [],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/review_yeartable.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Bảng chia nhóm năm và tô ô đang nói; review_yeartable đồng bộ hàng với câu voice-over.

## Khi nào dùng

Short tra năm sinh; Long tổng hợp chu kỳ nếu bảng ít cột. Không nên dùng: Nguồn năm/tuổi chưa được xác nhận độc lập.

## Cách dựng trong HyperFrames

Nhánh dựng cho year table nằm tại `hyperframes_short/compositions/review_yeartable.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/grok/build_fs2027.py:1`.

style `review_yeartable`; cấp các hàng/năm và word timing; build_fs2027 là caller phía tạo bảng.

## Rủi ro

Nhãn KIM LÂU THÂN từng bị đọc nhầm thành tuổi Thân (26/10); bảng ivory có subfoot tương phản 1.35.
