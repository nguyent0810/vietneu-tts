---
{
  "id": "stat_callout",
  "ten": "Callout số liệu",
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
  "so_muc": 14,
  "so_nguon": 2,
  "nguon": [
    "LeaddeOpenLab",
    "prompt-motion"
  ],
  "bang_chung_dung": [
    "hyperframes_short/compositions/_rv_bud_khi.html",
    "hyperframes_short/compositions/_rv_bud_tho.html",
    "hyperframes_short/compositions/_v3_v3_a.html",
    "hyperframes_short/compositions/_v3_v3_b.html",
    "output/cl_staging/build_jataka_b1.py"
  ],
  "vi_du": [
    "https://x.com/gavinpurcell/status/2108932593911816392",
    "https://prompt-motion.com/kantamk-61f410"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/studio/devices/hook.js",
    "hyperframes_short/studio/devices/mark.js",
    "hyperframes_short/studio/devices/media.js",
    "hyperframes_short/studio/devices/number.js",
    "hyperframes_short/studio/devices/thiep_cuoi.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Con số lớn đi cùng nhãn giải nghĩa và điểm đánh dấu; device number/hook đặt số như một callout thay vì bảng nhiều hàng.

## Khi nào dùng

Short nhấn một thống kê có nguồn; Long chốt số liệu trong câu chuyện. Không nên dùng: Số thiếu mẫu số, thời điểm hoặc đơn vị.

## Cách dựng trong HyperFrames

Nhánh dựng cho stat callout nằm tại `hyperframes_short/studio/devices/number.js:1`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:658`.

device `number`; truyền value, label và unit rõ ràng.

## Rủi ro

Tween số có thể kết sai giá trị; nhãn không ghi đơn vị khiến tỷ lệ bị hiểu sai.
