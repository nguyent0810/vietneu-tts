---
{
  "id": "transition_wipe",
  "ten": "Chuyển cảnh wipe",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "chuyen_canh",
    "anh"
  ],
  "cam_ngach": [],
  "so_muc": 9,
  "so_nguon": 1,
  "nguon": [
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://prompt-motion.com/kantamk-61f410",
    "https://prompt-motion.com/amitsingha89-150378"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
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

Mép thẳng hoặc shape quét qua khung che cảnh cũ và lộ cảnh mới theo một hướng. Mẫu [1](https://prompt-motion.com/kantamk-61f410) minh họa chuyển từ ảnh tổng sang sơ đồ chi tiết; mẫu [2](https://prompt-motion.com/amitsingha89-150378) cho thấy quét cùng hướng với tuyến nhìn.

## Khi nào dùng

FS: Short chuyển từ ảnh tổng quan sang chi tiết. Dạng Short. Không nên dùng khi có thể che chữ hoặc làm tưởng hai cảnh cùng nguồn.

## Cách dựng trong HyperFrames

Kỹ thuật transition_wipe chưa có trong engine như một visual riêng. Đặt hai ảnh tĩnh chồng nhau; thay polygon clipPath theo progress tuyến tính của t. Mọi trạng thái của transition_wipe là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

có thể che chữ hoặc làm tưởng hai cảnh cùng nguồn.
