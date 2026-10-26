---
{
  "id": "3d_procedural",
  "ten": "3D procedural",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giai_thich",
    "do_hoa"
  ],
  "cam_ngach": [],
  "so_muc": 735,
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
    "https://x.com/alexalbert__/status/2102466523164274839",
    "https://x.com/twoclipping/status/2102554209166000267"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 1,
    "bud": 1
  },
  "cong": "cao"
}
---

## Mô tả

Khối và mặt được dựng từ lưới hình học, ánh sáng tạo thể tích; camera đổi nhẹ để lộ mặt khuất. Mẫu [1](https://x.com/alexalbert__/status/2102466523164274839) minh họa tách một vật phẩm thành các mặt hình khối; mẫu [2](https://x.com/twoclipping/status/2102554209166000267) cho thấy xoay mô hình tĩnh để so góc nhìn.

## Khi nào dùng

FS: Long giải thích cấu tạo vật phẩm theo lớp. Dạng Ca_hai. Không nên dùng khi lưới dày làm headless chậm, mặt bóng dễ trông cgi giả.

## Cách dựng trong HyperFrames

Kỹ thuật 3d_procedural chưa có trong engine như một visual riêng. Dựng mesh đơn giản thành các mặt SVG hoặc bake góc thành sprite; nội suy góc camera bằng GSAP theo t, khóa seed hình học. Mọi trạng thái của 3d_procedural là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công cao.

## Rủi ro

lưới dày làm headless chậm, mặt bóng dễ trông CGI giả.
