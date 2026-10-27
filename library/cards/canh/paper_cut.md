---
{
  "id": "paper_cut",
  "ten": "Giấy cắt lớp",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "minh_hoa",
    "thu_cong"
  ],
  "cam_ngach": [],
  "so_muc": 82,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/MustaphaFenzar/status/2102773737129156730",
    "https://x.com/x4b47x/status/2103019799614034026"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 1,
    "bud": 1
  },
  "cong": "vua"
}
---

## Mô tả

Silhouette có viền cắt, bóng ngắn và nhiều lớp giấy tạo mô hình thủ công có độ sâu. Mẫu [1](https://x.com/MustaphaFenzar/status/2102773737129156730) minh họa tách nền, tường, vật thể thành lớp; mẫu [2](https://x.com/x4b47x/status/2103019799614034026) cho thấy dịch lớp giấy để lộ bố cục.

## Khi nào dùng

FS: Short giải thích mặt bằng bằng lớp không gian. Dạng Ca_hai. Không nên dùng khi viền/bóng quá đều mang vẻ tạo sinh.

## Cách dựng trong HyperFrames

Kỹ thuật paper_cut chưa có trong engine như một visual riêng. Tách silhouette SVG/PNG thành lớp tĩnh có bóng; dịch từng lớp nhẹ theo keyframe t, không mô phỏng vật lý. Mọi trạng thái của paper_cut là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

viền/bóng quá đều mang vẻ tạo sinh; z-order sai làm sai cấu trúc.
