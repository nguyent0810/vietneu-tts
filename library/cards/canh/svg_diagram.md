---
{
  "id": "svg_diagram",
  "ten": "Sơ đồ SVG",
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
  "so_muc": 262,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/twoclipping/status/2102554209166000267",
    "https://x.com/deedydas/status/2102787937482252537"
  ],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/longform.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Sơ đồ SVG gồm hình học và nhãn có thể giữ sắc nét khi scale; longform dựng các nút/đường theo dữ liệu spec.

## Khi nào dùng

Long giải quan hệ nhiều nút; Short chỉ dùng khi số nhãn ít. Không nên dùng: Ảnh chụp phức tạp hoặc dữ liệu chưa có cấu trúc node/edge.

## Cách dựng trong HyperFrames

Nhánh dựng cho svg diagram nằm tại `hyperframes_short/compositions/longform.js:356`; caller hoặc phần cấu hình tương ứng ở `hyperframes_short/compositions/longform.js:2664`.

visual type theo nhánh `wheel|elements|pie|compass`; dữ liệu `steps`, `parts`, `dirs` tùy sơ đồ.

## Rủi ro

Nút thiếu tọa độ làm mất liên kết; label dài có thể chồng nhau khi scale dọc.
