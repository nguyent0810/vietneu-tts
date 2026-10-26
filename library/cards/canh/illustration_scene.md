---
{
  "id": "illustration_scene",
  "ten": "Cảnh minh họa",
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
  "so_muc": 2,
  "so_nguon": 1,
  "nguon": [
    "athemeroy"
  ],
  "bang_chung_dung": [
    "output/cl_staging/build_jataka_b1.py",
    "output/cl_staging/long/build_B10.py",
    "output/cl_staging/long/build_B13.py",
    "output/cl_staging/long/build_B16.py",
    "output/cl_staging/long/build_B19.py"
  ],
  "vi_du": [
    "https://x.com/superalesha/status/2102463796149440888",
    "https://x.com/other__reality/status/2102514581684052169"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/jataka_engine.html",
    "hyperframes_short/compositions/moon_long.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Một cảnh vẽ có tiền cảnh, nhân vật và nền kể cùng một khoảnh khắc; Jataka engine dùng lớp SVG để dựng cảnh.

## Khi nào dùng

Short minh họa một hành động trong truyện; Long khi lời kể cần không gian diễn tiến. Không nên dùng: Cần chứng minh một chi tiết lịch sử bằng ảnh tư liệu.

## Cách dựng trong HyperFrames

Nhánh dựng cho illustration scene nằm tại `hyperframes_short/compositions/jataka_engine.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/build_jataka_b1.py:1`.

composition `jataka_engine.html`; cấu hình scene/đạo cụ trong SVG layers.

## Rủi ro

Tư thế nhân vật sai làm đổi nghĩa truyện; lớp foreground có thể che mặt/đạo cụ.
