---
{
  "id": "years_layout",
  "ten": "Bố cục năm",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "fs"
  ],
  "hop_ngach": [
    "tra_cuu",
    "van_hoa",
    "tam_linh"
  ],
  "cam_ngach": [],
  "so_muc": 0,
  "so_nguon": 0,
  "nguon": [],
  "bang_chung_dung": [],
  "vi_du": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/longform.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Một hàng thẻ năm hiện dần; `years` lấy `items`, có flip/deal/count và hẹn từng thẻ theo `at` hoặc `word`.

## Khi nào dùng

Short so nhóm năm liền nhau; Long kể chu kỳ qua các mốc được đọc. Không nên dùng: Cần đối chiếu nhiều thuộc tính trong từng năm.

## Cách dựng trong HyperFrames

Nhánh dựng cho years layout nằm tại `hyperframes_short/compositions/longform.js:468`; caller hoặc phần cấu hình tương ứng ở `hyperframes_short/compositions/longform.js:483`.

visual type `years`; truyền `items[{yr,sub,note,at,word}]`, biến thể `flip|deal|count`.

## Rủi ro

Thẻ quá ba thêm lớp `many`; chữ note dài có thể đẩy hàng cao và dính mép.
