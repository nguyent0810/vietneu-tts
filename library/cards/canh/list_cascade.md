---
{
  "id": "list_cascade",
  "ten": "Danh sách xuất hiện tuần tự",
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
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "output/cl_staging/build_shorts_bu_1006.py",
    "output/cl_staging/build_shorts_fs_test_1013.py",
    "output/cl_staging/build_shorts_v2_1.py",
    "output/cl_staging/build_shorts_v2_2.py",
    "output/cl_staging/grok/build_fs2027.py"
  ],
  "vi_du": [
    "https://x.com/brainextends/status/2103801834930606193",
    "https://prompt-motion.com/ultimaxbt-bbebf5"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_short/compositions/laban.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Các dòng lần lượt trượt vào theo thứ tự đọc; Laban đặt danh sách cạnh hình minh họa thay vì làm slide chữ kín màn.

## Khi nào dùng

Short 3–5 bước/ý; Long liệt kê quy trình có mốc lời tương ứng. Không nên dùng: Danh sách nhiều hơn số dòng đọc kịp hoặc các mục không cùng cấp.

## Cách dựng trong HyperFrames

Nhánh dựng cho list cascade nằm tại `hyperframes_short/compositions/longform.js:941`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:710`.

visual type `list`; `items[{text,at,word}]`, lần lượt bật theo thứ tự đọc.

## Rủi ro

Mục cuối có thể xuất hiện ngoài nhịp; cần chừa chiều cao cho số dòng dài.
