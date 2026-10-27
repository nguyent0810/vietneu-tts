---
{
  "id": "hook_vong_cuoi_short",
  "ten": "Câu cuối Short nối lại câu đầu",
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
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "bang_chung_dung": [
    ".claude/skills/shorts-lookup/SKILL.md"
  ],
  "do_hop": {
    "fs": 2,
    "bud": 2
  },
  "cong": "thap",
  "chua_duoc": [
    "nhip",
    "hook"
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

Kết Short bằng câu hoặc hình làm người xem xem lại từ đầu mà không thấy gượng: đáp án cuối đổi nghĩa câu mở đầu.

## Cách dùng

Plan short có cờ `loop: true` (vd `output/cl_staging/bud/plan_b39.json`); làn bảng tra FS dùng "khung dừng hình" cuối bài, `.claude/skills/shorts-lookup/SKILL.md:19`.

## Bằng chứng

1of10: Short có thể vượt 100% AVP khi loop, là tín hiệu xem lại mạnh. Nội bộ: FS "3 tuổi hợp 2027" (10 giây) AVP 206%.

## Rủi ro

Loop ép làm người xem thấy bị thao túng và thoát ở lần xem thứ hai. Chỉ loop khi nội dung thật sự khép vòng (bảng tra, quy trình, cú lật cuối).
