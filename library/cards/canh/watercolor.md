---
{
  "id": "watercolor",
  "ten": "Màu nước",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "bud"
  ],
  "hop_ngach": [
    "minh_hoa",
    "chat_lieu"
  ],
  "cam_ngach": [
    "fs"
  ],
  "so_muc": 25,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/kinderlayer/status/2108936150681305270",
    "https://x.com/sato_neet/status/2102622120631267807"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 0,
    "bud": 2
  },
  "cong": "vua"
}
---

## Mô tả

Mảng pigment loang, mép màu không đều và nền giấy tạo vẻ tranh màu nước. Mẫu [1](https://x.com/kinderlayer/status/2108936150681305270) minh họa dùng phong cảnh màu nước làm nền dẫn nhập; mẫu [2](https://x.com/sato_neet/status/2102622120631267807) cho thấy chuyển lớp màu bằng mask loang.

## Khi nào dùng

BUD: Long có thể dùng minh họa phong cảnh không tạo hình Đức Phật. Dạng Ca_hai. Không nên dùng khi loang tổng hợp dễ mùi ai.

## Cách dựng trong HyperFrames

Kỹ thuật watercolor chưa có trong engine như một visual riêng. Dùng asset/mask loang raster tiền vẽ; reveal bằng opacity/clip theo t, không chạy shader fluid. Mọi trạng thái của watercolor là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

loang tổng hợp dễ mùi AI; không biến dạng biểu tượng/tư liệu.
