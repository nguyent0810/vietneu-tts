---
{
  "id": "ui_mockup",
  "ten": "Mô phỏng giao diện UI",
  "loai": "template",
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
  "so_muc": 905,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "output/cl_staging/long/build_BT01.py",
    "output/cl_staging/long/build_BT02.py",
    "output/cl_staging/long/build_BT03.py",
    "output/cl_staging/long/build_BT04.py",
    "output/cl_staging/long/build_FT01.py"
  ],
  "vi_du": [
    "https://x.com/twoclipping/status/2102554209166000267",
    "https://x.com/deedydas/status/2102787937482252537"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/studio_long.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Giao diện giả lập đặt chữ và nút trong khung thiết bị, con trỏ/scroll dẫn mắt đến điểm cần nói; studio_long dùng bố cục bàn làm việc.

## Khi nào dùng

Long hướng dẫn thao tác qua vài trạng thái; Short một màn hình có highlight. Không nên dùng: Sản phẩm thật cần quay giao diện chính xác hoặc dữ liệu riêng tư.

## Cách dựng trong HyperFrames

Nhánh dựng cho ui mockup nằm tại `hyperframes_short/compositions/studio_long.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/long/build_BT01.py:1`.

style `studio_long`; caller build_BT01, media layout theo theme và vùng thiết bị.

## Rủi ro

Mockup có thể khác UI thật; nhãn/nút dài tràn khung thiết bị.
