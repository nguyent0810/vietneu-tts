---
{
  "id": "glitch",
  "ten": "Glitch / nhiễu số",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "hieu_ung",
    "ky_thuat_hinh"
  ],
  "cam_ngach": [
    "fs",
    "bud"
  ],
  "so_muc": 24,
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
    "https://x.com/pound75423/status/2103722556918464968",
    "https://x.com/HowDevelop/status/2103840883812733090"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 0,
    "bud": 0
  },
  "cong": "thap"
}
---

## Mô tả

Các dải chữ/ảnh lệch ngắn, scanline hoặc kênh màu nhiễu tạo lỗi tín hiệu thoáng qua. Mẫu [1](https://x.com/pound75423/status/2103722556918464968) minh họa chia ảnh thành dải dịch lệch; mẫu [2](https://x.com/HowDevelop/status/2103840883812733090) cho thấy đưa nhiễu màu ngắn lúc reveal.

## Khi nào dùng

Không hợp FS/BUD; chỉ thử nghiệm giải thích lỗi tín hiệu. Dạng Short. Không nên dùng khi nhấp nháy gây khó chịu.

## Cách dựng trong HyperFrames

Kỹ thuật glitch chưa có trong engine như một visual riêng. Tạo các bản layer tĩnh và mask dải SVG; bật translate/clip ở những đoạn t cố định, không random mỗi frame. Mọi trạng thái của glitch là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

nhấp nháy gây khó chịu; glitch tên người, số hoặc chữ kinh làm giảm tin cậy.
