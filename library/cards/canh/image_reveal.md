---
{
  "id": "image_reveal",
  "ten": "Ảnh reveal",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "anh_tu_lieu",
    "reveal"
  ],
  "cam_ngach": [],
  "so_muc": 136,
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
    "https://x.com/jake11moran/status/2103237884564414633",
    "https://x.com/iamtanzil_/status/2103459843831120030"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
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

Ảnh hoặc chi tiết mở dần qua mask/khung cắt, chuyển mắt từ toàn cảnh tới vùng cần xem. Mẫu [1](https://x.com/jake11moran/status/2103237884564414633) minh họa mở crop của vật phẩm trên bàn; mẫu [2](https://x.com/iamtanzil_/status/2103459843831120030) cho thấy quét vùng chú thích vào ảnh.

## Khi nào dùng

FS: Short hé lộ chi tiết hướng cửa trong ảnh. Dạng Short. Không nên dùng khi crop có thể giấu nguồn hoặc che mất điểm chứng minh.

## Cách dựng trong HyperFrames

Kỹ thuật image_reveal chưa có trong engine như một visual riêng. Lưu ảnh đã crop và clipPath SVG; nội suy biên mask theo t, khai báo rõ frame đầu/cuối. Mọi trạng thái của image_reveal là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

crop có thể giấu nguồn hoặc che mất điểm chứng minh.
