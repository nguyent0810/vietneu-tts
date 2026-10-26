---
{
  "id": "bar_chart",
  "ten": "Biểu đồ cột",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "so_sanh",
    "du_lieu"
  ],
  "cam_ngach": [],
  "so_muc": 19,
  "so_nguon": 2,
  "nguon": [
    "LeaddeOpenLab",
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/Sayan_shanky/status/2104424421641314396",
    "https://x.com/yeiken_app/status/2104820349838000492"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 3,
    "bud": 2
  },
  "cong": "vua"
}
---

## Mô tả

Các cột chung trục gốc, chiều cao tỉ lệ số liệu; nhãn và đơn vị giúp so sánh. Mẫu [1](https://x.com/Sayan_shanky/status/2104424421641314396) minh họa so độ cao các cột theo cùng trục; mẫu [2](https://x.com/yeiken_app/status/2104820349838000492) cho thấy tô cột đang được nhắc tới.

## Khi nào dùng

FS: Short so sánh ba mốc dữ liệu nhà ở. Dạng Ca_hai. Không nên dùng khi trục bị cắt phóng đại chênh lệch.

## Cách dựng trong HyperFrames

Kỹ thuật bar_chart chưa có trong engine như một visual riêng. Tính chiều cao từ mảng số đã chốt, dựng trục/cột/nhãn SVG; tween height/opacity theo mốc thoại. Mọi trạng thái của bar_chart là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

trục bị cắt phóng đại chênh lệch; nhiều cột quá nhỏ trên khung dọc.
