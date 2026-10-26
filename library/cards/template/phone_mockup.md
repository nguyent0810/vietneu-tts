---
{
  "id": "phone_mockup",
  "ten": "Khung điện thoại",
  "loai": "template",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giao_dien",
    "nguon_so"
  ],
  "cam_ngach": [],
  "so_muc": 41,
  "so_nguon": 3,
  "nguon": [
    "LeaddeOpenLab",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/zakisbuilding/status/2104389736647495680",
    "https://x.com/buildwithgautam/status/2104522362402267138"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 2
  },
  "cong": "vua"
}
---

## Mô tả

Ảnh giao diện nằm trong vỏ điện thoại có notch/viền; phối cảnh nhẹ gợi đang xem trên thiết bị. Mẫu [1](https://x.com/zakisbuilding/status/2104389736647495680) minh họa đặt ảnh trang tra cứu trong màn hình điện thoại; mẫu [2](https://x.com/buildwithgautam/status/2104522362402267138) cho thấy phóng vào đoạn trích đã chụp.

## Khi nào dùng

BUD: Short dẫn nguồn tra cứu bản kinh số. Dạng Short. Không nên dùng khi chữ screenshot nhỏ.

## Cách dựng trong HyperFrames

Kỹ thuật phone_mockup chưa có trong engine như một visual riêng. Dựng vỏ điện thoại CSS/SVG và snapshot cục bộ; pan/zoom màn hình theo transform là hàm của t. Mọi trạng thái của phone_mockup là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

chữ screenshot nhỏ; UI giả bị hiểu là ứng dụng thật.
