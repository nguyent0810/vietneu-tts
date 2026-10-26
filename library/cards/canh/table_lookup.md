---
{
  "id": "table_lookup",
  "ten": "Bảng tra / bảng dữ liệu",
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
  "so_muc": 18,
  "so_nguon": 3,
  "nguon": [
    "LeaddeOpenLab",
    "engine",
    "prompt-motion"
  ],
  "bang_chung_dung": [
    "output/cl_staging/grok/build_budlookup.py",
    "output/cl_staging/grok/tools/lookup/renderer.py",
    "output/cl_staging/build_fs_tables_1013.py",
    "output/cl_staging/build_shorts_fs_test_1013.py",
    "output/cl_staging/grok/build_fs2027.py"
  ],
  "vi_du": [
    "https://x.com/notdwd/status/2104401208958230764",
    "https://x.com/threeaus/status/2104535752373895249"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/review_budtable.html",
    "hyperframes_short/compositions/review_yeartable.html",
    "hyperframes_short/studio/devices/month_sheet.js",
    "hyperframes_short/studio/devices/table.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Bảng có header và hàng tra, có thể khoanh dòng cần xem; lookup visual còn có trống số lật để tìm năm.

## Khi nào dùng

Short tra tuổi/năm có nguồn; Long khi cần trình bày nhiều kết quả. Không nên dùng: Số liệu đang tranh cãi hoặc bảng quá rộng cho canvas.

## Cách dựng trong HyperFrames

Nhánh dựng cho table lookup nằm tại `hyperframes_short/compositions/longform.js:2368`; caller hoặc phần cấu hình tương ứng ở `hyperframes_short/compositions/review_budtable.html:1`.

visual type `lookup`; `cols`, `widths`, `rows[{cells}]`, `find[{row,at,word}]`, tùy chọn `pause`.

## Rủi ro

Lỗi 55b: tiêu đề cột 2 dòng tràn header 21/10; lỗi 24–26/10: nhãn/hàng cuối tràn hoặc shimmer kẹt.
