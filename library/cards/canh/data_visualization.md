---
{
  "id": "data_visualization",
  "ten": "Trực quan hóa dữ liệu",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "du_lieu",
    "giai_thich"
  ],
  "cam_ngach": [],
  "so_muc": 57,
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
    "https://x.com/GroundControl/status/2103678647777230877",
    "https://x.com/threeaus/status/2104535752373895249"
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
    "bud": 2
  },
  "cong": "vua"
}
---

## Mô tả

Dữ liệu được mã hóa bằng trục, màu, kích thước và nhãn có quy ước nhất quán. Mẫu [1](https://x.com/GroundControl/status/2103678647777230877) minh họa đặt số khảo sát cạnh luận điểm; mẫu [2](https://x.com/threeaus/status/2104535752373895249) cho thấy tô nhóm dữ liệu đang được đọc.

## Khi nào dùng

FS: Long giải thích số liệu khảo sát khu vực. Dạng Ca_hai. Không nên dùng khi thiếu nguồn/đơn vị biến đồ họa thành khẳng định gây hiểu lầm.

## Cách dựng trong HyperFrames

Kỹ thuật data_visualization chưa có trong engine như một visual riêng. Chuẩn hóa dữ liệu/miền trục trước; dựng SVG với đơn vị/legend rồi reveal nhóm theo mốc t. Mọi trạng thái của data_visualization là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

thiếu nguồn/đơn vị biến đồ họa thành khẳng định gây hiểu lầm.
