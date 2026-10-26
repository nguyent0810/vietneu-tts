---
{
  "id": "thumb_ctr_theo_nguon",
  "ten": "Đọc CTR theo nguồn traffic",
  "loai": "do_luong",
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
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "bang_chung_dung": [],
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

So CTR Home/Suggested trong 24 giờ đầu ở các video có lượt hiển thị trên trung bình; xem riêng CTR Subscriptions Feed cho người đã đăng ký. Không so CTR Search với CTR Browse như cùng chuẩn.

## Cách dùng

Thêm cột CTR theo nguồn vào báo cáo tuần `hf_brief.py:153`. chưa có trong engine: tách CTR theo nguồn traffic.

## Bằng chứng

YouTube Help: với khán giả chung, xem CTR Home và Suggested trong 24 giờ đầu trên video có lượt hiển thị trên trung bình; với người đăng ký, xem CTR Subscriptions Feed trong 24 giờ đầu.

## Rủi ro

CTR tổng cao nhờ Search có thể che việc Browse đang yếu, hoặc ngược lại. Khi đổi thumbnail, ghi rõ nguồn traffic đổi hay CTR đổi.
