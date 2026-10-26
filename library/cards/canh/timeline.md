---
{
  "id": "timeline",
  "ten": "Dòng thời gian",
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
  "so_muc": 129,
  "so_nguon": 5,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "output/cl_staging/long/build_F11.py",
    "output/cl_staging/long/build_F14.py",
    "output/cl_staging/long/build_F17.py",
    "output/cl_staging/long/build_F20.py",
    "output/cl_staging/long/build_F26.py"
  ],
  "vi_du": [
    "https://x.com/Ror_Fly/status/2102853258582880547",
    "https://x.com/itsolelehmann/status/2103124033365762215"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {
    "bud": {
      "so_bai": 20,
      "bai": [
        "_r_bud_a1_01",
        "_r_bud_a1_02",
        "_r_bud_a1_03",
        "_r_bud_a2_01",
        "_r_bud_a2_02"
      ]
    },
    "fs": {
      "so_bai": 16,
      "bai": [
        "_r_fs_r26_a",
        "_r_fs_r26_b",
        "_r_fs_r26_c",
        "_r_fs_t3_02",
        "_r_fs_yd_02"
      ]
    }
  },
  "nguon_su_that": [
    "hyperframes_short/compositions/dongho_long.html",
    "hyperframes_short/compositions/laban.html",
    "hyperframes_short/compositions/review_yeartable.html",
    "hyperframes_short/studio/devices/cycle.js",
    "hyperframes_short/studio/devices/time.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Các mốc nằm trên trục thời gian và bật theo trình tự; longform timeline nhận `items` và neo nhãn theo lời đọc.

## Khi nào dùng

Short 3–5 mốc; Long lịch sử có mốc năm kiểm chứng. Không nên dùng: Mốc ước lượng không có nguồn hoặc quá nhiều ngày sát nhau.

## Cách dựng trong HyperFrames

Nhánh dựng cho timeline nằm tại `hyperframes_short/compositions/longform.js:559`; caller hoặc phần cấu hình tương ứng ở `hyperframes_short/studio/devices/time.js:1`.

visual type `timeline`; `items[{year,label,at,word}]`, các mốc được hẹn bằng `when()` theo lời đọc.

## Rủi ro

Khoảng cách không tỷ lệ dễ nói sai độ dài thời gian; nhãn mốc dài chồng nhau.
