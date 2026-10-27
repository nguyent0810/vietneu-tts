---
{
  "id": "source_transformation",
  "ten": "Biến đổi tư liệu nguồn",
  "loai": "quy_trinh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "nguon",
    "phan_tich"
  ],
  "cam_ngach": [],
  "so_muc": 46,
  "so_nguon": 3,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/twoclipping/status/2102554209166000267",
    "https://x.com/deedydas/status/2102787937482252537"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 3,
    "bud": 3
  },
  "cong": "vua"
}
---

## Mô tả

Tư liệu gốc thành crop/chú giải/sơ đồ trong khi vẫn giữ dấu vết nguồn để kiểm tra. Mẫu [1](https://x.com/twoclipping/status/2102554209166000267) minh họa đặt bản dịch cạnh đoạn kinh gốc; mẫu [2](https://x.com/deedydas/status/2102787937482252537) cho thấy đánh dấu vùng ảnh cần chú giải.

## Khi nào dùng

BUD: Short giải thích bản dịch có ghi người dịch. Dạng Ca_hai. Không nên dùng khi crop bỏ điều kiện gốc.

## Cách dựng trong HyperFrames

Kỹ thuật source_transformation chưa có trong engine như một visual riêng. Giữ file gốc và crop riêng; khai báo mask/chú thích theo tọa độ cố định và reveal theo t, giữ credit. Mọi trạng thái của source_transformation là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

crop bỏ điều kiện gốc; chú giải bị tưởng là nội dung tài liệu.
