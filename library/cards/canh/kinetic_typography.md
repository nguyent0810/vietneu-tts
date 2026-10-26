---
{
  "id": "kinetic_typography",
  "ten": "Chữ động / kinetic typography",
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
  "so_muc": 1262,
  "so_nguon": 5,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "output/cl_staging/build_fs_tables_1013.py",
    "output/cl_staging/build_shorts_fs_test_1013.py",
    "output/cl_staging/grok/build_fs2027.py",
    "output/cl_staging/grok/build_r1026.py",
    "output/cl_staging/grok/build_r1027.py"
  ],
  "vi_du": [
    "https://x.com/majidmanzarpour/status/2102476258948927543",
    "https://x.com/twoclipping/status/2102554209166000267"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/review_yeartable.html",
    "hyperframes_short/studio/core.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Từ khóa đổi cỡ/vị trí theo nhịp đọc, các chữ còn lại đứng yên để giữ câu; year-table dùng word highlight theo timing.

## Khi nào dùng

Short một câu chốt; Long đoạn có nhịp nhấn rõ. Không nên dùng: Cả câu đều được nhấn hoặc lời đọc quá dày.

## Cách dựng trong HyperFrames

Nhánh dựng cho kinetic typography nằm tại `hyperframes_short/compositions/review_yeartable.html:1`; caller hoặc phần cấu hình tương ứng ở `hyperframes_short/studio/core.js:1`.

style `review_yeartable`/device word; truyền cụm từ ngắn và mốc theo voice manifest.

## Rủi ro

Chữ hoa dài tràn khung; lỗi THỀ→THÊ từng phát sinh khi clip cắt dấu.
