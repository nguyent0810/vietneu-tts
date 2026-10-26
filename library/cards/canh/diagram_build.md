---
{
  "id": "diagram_build",
  "ten": "Sơ đồ dựng theo lời",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "so_do",
    "quy_trinh"
  ],
  "cam_ngach": [],
  "so_muc": 10,
  "so_nguon": 1,
  "nguon": [
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://prompt-motion.com/kantamk-61f410",
    "https://prompt-motion.com/samaote-5e2fc2"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 3,
    "bud": 1
  },
  "cong": "vua"
}
---

## Mô tả

Nút xuất hiện trước, sau đó cạnh và nhãn quan hệ; thứ tự dựng dẫn mắt theo lời giải thích. Mẫu [1](https://prompt-motion.com/kantamk-61f410) minh họa nối cửa chính với các khu vực trên sơ đồ; mẫu [2](https://prompt-motion.com/samaote-5e2fc2) cho thấy đưa quan hệ vào sau khi hiện các nút.

## Khi nào dùng

FS: Short giải thích tuyến từ cửa tới phòng. Dạng Ca_hai. Không nên dùng khi cạnh giao nút hoặc thứ tự không khớp thoại làm sai logic.

## Cách dựng trong HyperFrames

Kỹ thuật diagram_build chưa có trong engine như một visual riêng. Khai báo node/edge/label trong JSON; đặt tọa độ cố định, SVG path dashoffset và reveal node theo beat. Mọi trạng thái của diagram_build là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

cạnh giao nút hoặc thứ tự không khớp thoại làm sai logic.
