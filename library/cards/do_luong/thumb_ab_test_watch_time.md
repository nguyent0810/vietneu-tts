---
{
  "id": "thumb_ab_test_watch_time",
  "ten": "A/B Test & Compare: thắng theo watch time",
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
    "https://support.google.com/youtube/answer/16391400"
  ],
  "vi_du": [
    "https://support.google.com/youtube/answer/16391400"
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
    "ctr",
    "hook"
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

Thử tối đa 3 tiêu đề, thumbnail hoặc cặp; YouTube chọn bản có tỉ phần watch time cao nhất. Không tự đổi thumbnail giữa chừng.

## Cách dùng

Dùng cho Long (Shorts không thử được). Ghi kết quả vào `bang_chung` của thẻ thumbnail tương ứng. chưa có trong engine: đọc kết quả A/B qua API.

## Bằng chứng

YouTube Help (Lead đọc lại 26/10): tối đa 3 bản; tối ưu theo watch time chứ không theo CTR; Shorts, Live đã hẹn và Premiere đang hẹn không thử được; xong trong 2 tuần; kết quả Winner / Performed Same / Inconclusive; không có bản thắng thì bản tải lên đầu tiên được dùng.

## Rủi ro

Đọc kết quả bằng CTR sẽ chọn sai so với YouTube. Kênh nhỏ ít lượt hiển thị dễ ra Inconclusive: coi đó là dữ liệu "ba bản chưa đủ khác", không phải thất bại.
