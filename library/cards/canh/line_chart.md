---
{
  "id": "line_chart",
  "ten": "Biểu đồ đường",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "du_lieu",
    "xu_huong"
  ],
  "cam_ngach": [],
  "so_muc": 20,
  "so_nguon": 3,
  "nguon": [
    "LeaddeOpenLab",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/twoclipping/status/2103273003555402193",
    "https://x.com/threeaus/status/2104535752373895249"
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

Điểm dữ liệu theo hai trục được nối thành đường; mốc thời gian và nhãn trục giữ ngữ cảnh xu hướng. Mẫu [1](https://x.com/twoclipping/status/2103273003555402193) minh họa nối giá trị theo năm trên trục; mẫu [2](https://x.com/threeaus/status/2104535752373895249) cho thấy đánh dấu đoạn tăng/giảm.

## Khi nào dùng

FS: Long trình bày xu hướng có số liệu và nguồn. Dạng Ca_hai. Không nên dùng khi trục y rút gọn phóng đại biến động.

## Cách dựng trong HyperFrames

Kỹ thuật line_chart chưa có trong engine như một visual riêng. Map số liệu đã xác thực vào miền trục cố định; SVG path/marker đổi theo progress t. Mọi trạng thái của line_chart là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

trục Y rút gọn phóng đại biến động; nối dữ liệu thiếu gây sai.
