---
{
  "id": "studio_device",
  "ten": "Thiết bị Studio",
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
  "so_muc": 0,
  "so_nguon": 0,
  "nguon": [],
  "bang_chung_dung": [
    "output/cl_staging/grok/ab_compare.py",
    "output/cl_staging/grok/tools/build_54b_long_thumbs.py",
    "output/cl_staging/grok/tools/layout04.py",
    "output/cl_staging/long/build_B1.py",
    "output/cl_staging/long/build_B10.py"
  ],
  "vi_du": [],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/studio/devices/compare.js",
    "hyperframes_short/studio/devices/cycle.js",
    "hyperframes_short/studio/devices/hook.js",
    "hyperframes_short/studio/devices/mark.js",
    "hyperframes_short/studio/devices/media.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Một device xếp nội dung theo vai trò—compare, cycle, number hoặc table—với vùng title và dữ liệu tách nhau.

## Khi nào dùng

Short tra cứu có tương tác thị giác; Long dùng khi nhiều dòng cần giữ cố định. Không nên dùng: Tất cả device không cùng mẫu, hoặc cần xem toàn trang tài liệu.

## Cách dựng trong HyperFrames

Nhánh dựng cho studio device nằm tại `hyperframes_short/studio/devices/compare.js:1`; caller hoặc phần cấu hình tương ứng ở `hyperframes_short/studio/core.js:1`.

device phù hợp (`compare|number|table|quote`); data fields theo device, không thay tên field tùy ý.

## Rủi ro

Device chọn sai khiến trường dữ liệu không khớp; nhãn hẹp và chữ vàng có lỗi render thực tế.
