---
{
  "id": "wheel_layout",
  "ten": "Bố cục vòng",
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
  "bang_chung_dung": [],
  "vi_du": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_short/compositions/longform.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Các nhãn được chia đều theo góc quanh tâm; longform.js `wheel` đặt 12 chi ở bán kính 360.

## Khi nào dùng

Short vòng phân loại; Long khi lời đi qua từng cung. Không nên dùng: Số mục không đều hoặc nhãn dài không vừa từng ô.

## Cách dựng trong HyperFrames

Nhánh dựng cho wheel layout nằm tại `hyperframes_short/compositions/longform.js:246`; caller hoặc phần cấu hình tương ứng ở `hyperframes_short/compositions/longform.js:302`.

visual type `wheel`; nút lấy `CHI`, chia góc 30°, bán kính 360; cấu hình `steps` và `focus`.

## Rủi ro

Sắp thứ tự lệch một cung làm sai quy ước; legend dài có thể chạm vòng.
