---
{
  "id": "geometry_manim",
  "ten": "Hình học kiểu Manim",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giao_duc",
    "toan"
  ],
  "cam_ngach": [
    "fs",
    "bud"
  ],
  "so_muc": 61,
  "so_nguon": 5,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/hyuki/status/2102832558602072560",
    "https://x.com/LinearUncle/status/2103128559174971663"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 0,
    "bud": 0
  },
  "cong": "cao"
}
---

## Mô tả

Hình hình học có trục, điểm và ký hiệu; phép biến đổi hoặc quan hệ được dựng lần lượt để chứng minh. Mẫu [1](https://x.com/hyuki/status/2102832558602072560) minh họa dời điểm trên hình để thấy góc đổi; mẫu [2](https://x.com/LinearUncle/status/2103128559174971663) cho thấy tô cạnh tương ứng trước giải thích.

## Khi nào dùng

Không hợp FS/BUD nếu không có phép hình học cần chứng minh. Dạng Ca_hai. Không nên dùng khi sai tỉ lệ làm sai lập luận.

## Cách dựng trong HyperFrames

Kỹ thuật geometry_manim chưa có trong engine như một visual riêng. Vẽ hình bằng SVG; keyframe vị trí/độ dài cạnh theo t, bake sẵn mọi góc 3D cần thiết. Mọi trạng thái của geometry_manim là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công cao.

## Rủi ro

sai tỉ lệ làm sai lập luận; 3D headless có thể giật hoặc chậm.
