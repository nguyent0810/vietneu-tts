---
{
  "id": "node_edge_diagram",
  "ten": "Sơ đồ node và cạnh",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "quan_he",
    "so_do"
  ],
  "cam_ngach": [],
  "so_muc": 16,
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
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 1
  },
  "cong": "vua"
}
---

## Mô tả

Thực thể là nút, quan hệ là cạnh có hướng/nhãn; vị trí giúp phân biệt vai trò từng nút. Mẫu [1](https://prompt-motion.com/ultimaxbt-bbebf5) minh họa nối cửa, hành lang và phòng trên sơ đồ; mẫu [2](https://prompt-motion.com/kantamk-61f410) cho thấy làm sáng một cạnh khi lời nhắc tới.

## Khi nào dùng

FS: Short diễn tả luồng đi qua các khu vực. Dạng Ca_hai. Không nên dùng khi layout tự sinh đổi lần render.

## Cách dựng trong HyperFrames

Kỹ thuật node_edge_diagram chưa có trong engine như một visual riêng. Chốt tọa độ node trong JSON; dựng cạnh có hướng bằng SVG path và tô cạnh theo khoảng t. Mọi trạng thái của node_edge_diagram là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

layout tự sinh đổi lần render; cạnh chồng nhau ngụ ý sai quan hệ.
