---
{
  "id": "flowchart",
  "ten": "Lưu đồ",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "quy_trinh",
    "so_do"
  ],
  "cam_ngach": [],
  "so_muc": 20,
  "so_nguon": 2,
  "nguon": [
    "LeaddeOpenLab",
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/kevinpiac/status/2104489806713553012",
    "https://x.com/carajnikant/status/2104539072106492193"
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
  "cong": "vua"
}
---

## Mô tả

Hộp điều kiện, nhánh có nhãn và mũi tên biến quy tắc thành các đường quyết định nhìn được. Mẫu [1](https://x.com/kevinpiac/status/2104489806713553012) minh họa đưa ba điều kiện vào các nhánh riêng; mẫu [2](https://x.com/carajnikant/status/2104539072106492193) cho thấy tô nhánh được chọn theo lời đọc.

## Khi nào dùng

FS: Short kiểm tra điều kiện trước kết luận vị trí bếp. Dạng Short. Không nên dùng khi nhánh thiếu nhãn hoặc mũi tên giao nhau khiến quy trình sai.

## Cách dựng trong HyperFrames

Kỹ thuật flowchart chưa có trong engine như một visual riêng. Khai báo nhánh/node theo dữ liệu cố định, tính tọa độ SVG một lần; reveal connector theo t. Mọi trạng thái của flowchart là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

nhánh thiếu nhãn hoặc mũi tên giao nhau khiến quy trình sai.
