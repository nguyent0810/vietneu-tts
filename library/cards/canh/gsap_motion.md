---
{
  "id": "gsap_motion",
  "ten": "Chuyển động GSAP",
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
  "so_muc": 128,
  "so_nguon": 5,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "output/cl_staging/build_fs_tables_1013.py",
    "output/cl_staging/build_shorts_fs_test_1013.py",
    "output/cl_staging/grok/build_fs2027.py",
    "output/cl_staging/grok/build_r1026.py",
    "output/cl_staging/grok/build_r1027.py"
  ],
  "vi_du": [
    "https://x.com/deedydas/status/2102787937482252537",
    "https://x.com/charlesmendez/status/2102847039415476517"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/review_yeartable.html",
    "hyperframes_short/studio/core.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Timeline GSAP ghép nhiều tween có mốc vào/ra xác định; studio core đăng ký timeline để seek đúng frame.

## Khi nào dùng

Short motion chữ/shape ít lớp; Long khi nhịp tween phải bám voice. Không nên dùng: Chỉ cần chuyển cảnh tĩnh hoặc logic phụ thuộc thời gian thực.

## Cách dựng trong HyperFrames

Nhánh dựng cho gsap motion nằm tại `hyperframes_short/studio/core.js:1`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:658`.

style được chọn qua `render(...,style=...)`; timeline tween dùng mốc `start` cố định, seek-safe.

## Rủi ro

Callback đổi DOM có thể sai khi seek; dùng mốc timeline cố định, không dựa Date.now.
