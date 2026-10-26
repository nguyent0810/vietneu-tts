---
{
  "id": "silhouette",
  "ten": "Silhouette",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "minh_hoa",
    "nhan_vat"
  ],
  "cam_ngach": [],
  "so_muc": 43,
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
    "https://x.com/majidmanzarpour/status/2102476258948927543",
    "https://x.com/Michaelzsguo/status/2102592355165782312"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
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

Chủ thể thành mảng tối/đơn sắc có đường bao rõ trên nền sáng hoặc ngược sáng. Mẫu [1](https://x.com/majidmanzarpour/status/2102476258948927543) minh họa dùng dáng người không nhận diện trong cảnh ngồi thiền; mẫu [2](https://x.com/Michaelzsguo/status/2102592355165782312) cho thấy tách đường bao khỏi phong cảnh.

## Khi nào dùng

BUD: Long minh họa tư thế ngồi bằng dáng không định danh. Dạng Ca_hai. Không nên dùng khi pose có thể không chuẩn hoặc giống người thật.

## Cách dựng trong HyperFrames

Kỹ thuật silhouette chưa có trong engine như một visual riêng. Dùng asset SVG/PNG đã duyệt; nếu animate chỉ tween transform/opacity theo mốc thời gian. Mọi trạng thái của silhouette là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

pose có thể không chuẩn hoặc giống người thật; tương phản thấp mất đường bao.
