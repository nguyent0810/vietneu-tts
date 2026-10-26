---
{
  "id": "paper_texture",
  "ten": "Texture giấy",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "chat_lieu",
    "nen"
  ],
  "cam_ngach": [],
  "so_muc": 25,
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
    "https://x.com/aollivier82/status/2102466456491536674",
    "https://x.com/jrayon/status/2102861376184054015"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 1,
    "bud": 2
  },
  "cong": "thap"
}
---

## Mô tả

Sợi giấy và hạt nhẹ nằm dưới nét/chữ, tạo bề mặt mà không thay nội dung. Mẫu [1](https://x.com/aollivier82/status/2102466456491536674) minh họa phủ hạt giấy dưới chú giải; mẫu [2](https://x.com/jrayon/status/2102861376184054015) cho thấy giữ texture mờ ở nền trang.

## Khi nào dùng

BUD: Short đặt chú giải trên giấy nhạt, không dưới kinh dài. Dạng Ca_hai. Không nên dùng khi texture tương phản làm bẩn chữ.

## Cách dựng trong HyperFrames

Kỹ thuật paper_texture chưa có trong engine như một visual riêng. Dùng texture tile cục bộ bất biến; opacity/blend CSS cố định hoặc tween hữu hạn theo t. Mọi trạng thái của paper_texture là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

texture tương phản làm bẩn chữ; hạt lặp lộ pattern giả cổ.
