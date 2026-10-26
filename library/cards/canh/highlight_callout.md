---
{
  "id": "highlight_callout",
  "ten": "Khoanh / chú thích điểm",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "phan_tich_anh",
    "chu_thich"
  ],
  "cam_ngach": [],
  "so_muc": 31,
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
    "https://x.com/VectorCrossProd/status/2104093497561436573",
    "https://x.com/akokoi1/status/2104520072014508316"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 3,
    "bud": 1
  },
  "cong": "thap"
}
---

## Mô tả

Vòng khoanh/connector và nhãn ngắn chỉ đúng chi tiết; phần ngoài có thể giảm sáng. Mẫu [1](https://x.com/VectorCrossProd/status/2104093497561436573) minh họa khoanh vị trí cửa trên bản vẽ; mẫu [2](https://x.com/akokoi1/status/2104520072014508316) cho thấy kéo đường dẫn tới chi tiết ảnh.

## Khi nào dùng

FS: Short nhấn hướng mở cửa trên sơ đồ. Dạng Ca_hai. Không nên dùng khi tọa độ sai sau crop chỉ nhầm vật thể.

## Cách dựng trong HyperFrames

Kỹ thuật highlight_callout chưa có trong engine như một visual riêng. Lưu tọa độ marker chuẩn hóa trong viewBox; tween connector/opacity từ mốc t, không dò DOM lúc render. Mọi trạng thái của highlight_callout là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

tọa độ sai sau crop chỉ nhầm vật thể; nhiều callout che ảnh.
