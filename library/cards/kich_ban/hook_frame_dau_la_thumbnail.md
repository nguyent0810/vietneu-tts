---
{
  "id": "hook_frame_dau_la_thumbnail",
  "ten": "Frame đầu Short là thumbnail",
  "loai": "kich_ban",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "hook"
  ],
  "cam_ngach": [],
  "so_muc": 1,
  "so_nguon": 1,
  "nguon": [
    "https://1of10.com/blog/youtube-shorts-analytics/"
  ],
  "vi_du": [
    "https://1of10.com/blog/youtube-shorts-analytics/"
  ],
  "nguon_su_that": [],
  "alias": [],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "bang_chung_dung": [],
  "do_hop": {
    "fs": 2,
    "bud": 3
  },
  "cong": "thap",
  "chua_duoc": [
    "hook",
    "nhip"
  ],
  "muc_bang_chung": [
    "đo được ngoài YouTube (tương quan, không nhân quả)"
  ],
  "de_xuat_boi": "muse-lead",
  "nghien_cuu": "library/research/chu_de_hook_thumbnail_2026-10-26.md",
  "ap_dung": "thu_nghiem_hoac_dang_thua"
}
---
## Mô tả

Giây đầu phải có chuyển động, chữ lớn đọc được khi tắt tiếng, và lời hứa hoặc câu hỏi. Không logo, không chào, không nền đen chờ.

## Cách dùng

Cổng tràn chữ và kiểm khung 0 trống chạy trước render: `hf_qa.py:163`. Thẻ chữ lớn mở đầu: visual `word` trong `hyperframes_short/compositions/longform.js:1083`.

## Bằng chứng

1of10 (creator tự đo): quyết định ở lại hay vuốt đi diễn ra trong 1–2 giây đầu; frame 1 phải làm cùng lúc việc của thumbnail, hook và lời hứa.

## Rủi ro

Nhồi quá nhiều chữ và hiệu ứng vào frame 1 khiến người xem không hiểu gì. Một tiêu điểm vẫn hơn ba hiệu ứng.
