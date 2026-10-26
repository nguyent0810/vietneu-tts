---
{
  "id": "map_pin",
  "ten": "Ghim địa điểm",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "dia_diem",
    "ban_do"
  ],
  "cam_ngach": [],
  "so_muc": 17,
  "so_nguon": 1,
  "nguon": [
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://prompt-motion.com/ultimaxbt-bbebf5",
    "https://prompt-motion.com/kantamk-61f410"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 0
  },
  "cong": "vua"
}
---

## Mô tả

Ghim tọa độ đi cùng nhãn địa danh, xuất hiện đúng vị trí trên ảnh/bản đồ. Mẫu [1](https://prompt-motion.com/ultimaxbt-bbebf5) minh họa đánh dấu vị trí công trình trên bản đồ; mẫu [2](https://prompt-motion.com/kantamk-61f410) cho thấy gắn nhãn vào điểm có nguồn.

## Khi nào dùng

FS: Short định vị khu vực công khai trên bản đồ. Dạng Short. Không nên dùng khi hệ tọa độ/crop sai vị trí.

## Cách dựng trong HyperFrames

Kỹ thuật map_pin chưa có trong engine như một visual riêng. Lưu bản đồ và tọa độ đã kiểm trong cùng hệ quy chiếu; SVG pin/label bật theo mốc t, không lấy GPS/tile live. Mọi trạng thái của map_pin là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Tọa độ và nền bản đồ có thể dựa trên visual map `hyperframes_short/compositions/longform.js:854`. Công vua.

## Rủi ro

hệ tọa độ/crop sai vị trí; pin nhà riêng lộ dữ liệu cá nhân.
