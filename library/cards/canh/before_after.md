---
{
  "id": "before_after",
  "ten": "Trước và sau",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "so_sanh",
    "huong_dan"
  ],
  "cam_ngach": [],
  "so_muc": 14,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/redpersongpt/status/2103807094554284430",
    "https://x.com/hii_studio_jp/status/2105051697525686340"
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
  "cong": "thap"
}
---

## Mô tả

Hai trạng thái cùng góc máy nằm hai phía đường ranh quét, để mắt nhận ra một thay đổi chính. Mẫu [1](https://x.com/redpersongpt/status/2103807094554284430) minh họa quét ranh giữa hai ảnh cùng bố cục; mẫu [2](https://x.com/hii_studio_jp/status/2105051697525686340) cho thấy lộ phần đã chỉnh sau khi giữ ảnh gốc.

## Khi nào dùng

FS: Short chỉ ra khác biệt vị trí đồ vật. Dạng Short. Không nên dùng khi khác crop/ánh sáng khiến người xem quy nhiều thay đổi cho một nguyên nhân.

## Cách dựng trong HyperFrames

Kỹ thuật before_after chưa có trong engine như một visual riêng. Dùng hai ảnh cùng crop và mask CSS/SVG; tọa độ đường ranh là hàm tuyến tính của t. Mọi trạng thái của before_after là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

khác crop/ánh sáng khiến người xem quy nhiều thay đổi cho một nguyên nhân.
