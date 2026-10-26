---
{
  "id": "thumb_tuy_chinh",
  "ten": "Thumbnail tuỳ chỉnh cho mọi Long",
  "loai": "khuon",
  "dinh_dang": [
    "long"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "thumbnail"
  ],
  "cam_ngach": [],
  "so_muc": 1,
  "so_nguon": 1,
  "nguon": [
    "https://support.google.com/youtube/answer/12340300"
  ],
  "vi_du": [
    "https://support.google.com/youtube/answer/12340300"
  ],
  "nguon_su_that": [],
  "alias": [],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "bang_chung_dung": [
    "output/cl_staging/long/thumb_v2.py"
  ],
  "do_hop": {
    "fs": 2,
    "bud": 2
  },
  "cong": "thap",
  "chua_duoc": [
    "ctr"
  ],
  "muc_bang_chung": [
    "YouTube Help (chính thức, Lead đã đọc lại 26/10)"
  ],
  "de_xuat_boi": "muse-lead",
  "nghien_cuu": "library/research/chu_de_hook_thumbnail_2026-10-26.md",
  "ap_dung": "thu_nghiem_hoac_dang_thua"
}
---
## Mô tả

Thiết kế riêng một ảnh 1280×720 cho mỗi Long với một thông điệp rõ, không để YouTube chọn khung hình.

## Cách dùng

Kênh đã làm: nền AI không chữ + chữ tự đặt (`output/cl_staging/long/thumb_v2.py`, quy ước trong memory thumbnail 23/10). chưa có trong engine: cổng kiểm thumbnail tự động.

## Bằng chứng

YouTube Help (Lead đọc lại 26/10): "90% of the best-performing videos have custom thumbnails." YouTube không định nghĩa "best-performing", nên đây là tương quan.

## Rủi ro

Thumbnail đẹp mà sai nội dung sẽ thắng click, thua giữ chân (xem thẻ hứa đúng).
