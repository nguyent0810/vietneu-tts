---
{
  "id": "comparison_split",
  "ten": "Chia đôi so sánh",
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
  "so_muc": 124,
  "so_nguon": 5,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/goofyninjaaa/status/2103641843963473981",
    "https://x.com/pound75423/status/2103722556918464968"
  ],
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

Khung chia đôi để cùng lúc thấy trạng thái A và B; visual longform giữ cặp vùng song song.

## Khi nào dùng

Short trước/sau dễ nhận ra; Long đối chiếu hai mốc bằng cùng góc nhìn. Không nên dùng: Thay đổi chỉ khác màu nhẹ hoặc không có mốc so chung.

## Cách dựng trong HyperFrames

Nhánh dựng cho comparison split nằm tại `hyperframes_short/compositions/longform.js:600`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:703`.

visual type `compare`; hai vùng A/B cùng thời lượng và cùng điểm crop.

## Rủi ro

Ảnh hai vế khác crop sẽ tạo cảm giác biến đổi giả.
