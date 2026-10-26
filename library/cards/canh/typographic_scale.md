---
{
  "id": "typographic_scale",
  "ten": "Chữ phóng đại theo nhịp",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "typography",
    "nhan_manh"
  ],
  "cam_ngach": [],
  "so_muc": 14,
  "so_nguon": 1,
  "nguon": [
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://prompt-motion.com/ultimaxbt-bbebf5",
    "https://prompt-motion.com/kantamk-61f410"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 1
  },
  "cong": "thap"
}
---

## Mô tả

Từ khóa phóng lớn hơn phần còn lại theo nhịp câu, tạo phân cấp thị giác. Mẫu [1](https://prompt-motion.com/ultimaxbt-bbebf5) minh họa phóng từ “hướng” khi phân biệt hai khái niệm; mẫu [2](https://prompt-motion.com/kantamk-61f410) cho thấy thu nhỏ từ khóa trở lại sau nhịp nhấn.

## Khi nào dùng

FS: Short nhấn từ hướng trong câu giải thích cửa. Dạng Short. Không nên dùng khi tràn safe area hoặc lấn caption.

## Cách dựng trong HyperFrames

Kỹ thuật typographic_scale chưa có trong engine như một visual riêng. Đặt transform-origin/scale cho từ khóa trong layout cố định; GSAP tween theo beat, không thay layout từng frame. Mọi trạng thái của typographic_scale là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

tràn safe area hoặc lấn caption; nhấn sai từ đổi trọng tâm.
