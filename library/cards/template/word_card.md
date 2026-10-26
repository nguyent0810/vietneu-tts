---
{
  "id": "word_card",
  "ten": "Thẻ từ khóa",
  "loai": "template",
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
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/longform.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Một từ khóa đứng riêng thành thẻ, xuất hiện đúng nhịp rồi nhường chỗ cho từ kế tiếp; visual word dựa vào `word` và mốc.

## Khi nào dùng

Short một khái niệm mỗi nhịp; Long chỉ dùng cho đoạn cần ghi nhớ từ khóa. Không nên dùng: Câu dài hoặc nhiều thuật ngữ cần định nghĩa đầy đủ.

## Cách dựng trong HyperFrames

Nhánh dựng cho word card nằm tại `hyperframes_short/compositions/longform.js:1083`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:703`.

visual type `word`; truyền một từ, `at` hoặc `word` marker và màu nhấn.

## Rủi ro

Từ có dấu bị cắt nếu hộp quá ngắn; hiển thị sai mốc làm từ khóa lệch giọng.
