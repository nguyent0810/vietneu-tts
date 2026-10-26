---
{
  "id": "isometric",
  "ten": "Đồ họa isometric",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "fs"
  ],
  "hop_ngach": [
    "khong_gian",
    "so_do"
  ],
  "cam_ngach": [
    "bud"
  ],
  "so_muc": 35,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/goofyninjaaa/status/2103641843963473981",
    "https://x.com/deedydas/status/2104391577091407965"
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

Mặt phẳng song song nghiêng giả lập 3D, thường theo lưới 30°, tạo sơ đồ không gian dạng axonometric. Mẫu [1](https://x.com/goofyninjaaa/status/2103641843963473981) minh họa xếp tầng nhà và cầu thang theo lưới nghiêng; mẫu [2](https://x.com/deedydas/status/2104391577091407965) cho thấy đẩy từng tầng ra khỏi mặt bằng.

## Khi nào dùng

FS: Long giải thích tầng nhà bằng mặt cắt minh họa. Dạng Ca_hai. Không nên dùng khi góc chiếu bóp méo tương quan kích thước.

## Cách dựng trong HyperFrames

Kỹ thuật isometric chưa có trong engine như một visual riêng. Tính trước tọa độ mặt theo lưới isometric; dựng từng mặt SVG và dịch lớp z bằng translate theo t. Mọi trạng thái của isometric là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

góc chiếu bóp méo tương quan kích thước; chữ dày khó đọc trên mobile.
