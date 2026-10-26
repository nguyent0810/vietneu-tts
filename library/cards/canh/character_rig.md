---
{
  "id": "character_rig",
  "ten": "Nhân vật / rig",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "huong_dan",
    "minh_hoa"
  ],
  "cam_ngach": [],
  "so_muc": 100,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/AxtonLiu/status/2103119648271290566",
    "https://x.com/ishuagra02/status/2103247844542922825"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 1,
    "bud": 0
  },
  "cong": "cao"
}
---

## Mô tả

Nhân vật chia thành đầu/thân/tay/chân có pivot riêng; xoay từng khớp tạo cử chỉ minh họa. Mẫu [1](https://x.com/AxtonLiu/status/2103119648271290566) minh họa cho nhân vật chỉ vào vị trí trên sơ đồ; mẫu [2](https://x.com/ishuagra02/status/2103247844542922825) cho thấy đổi pose để minh họa thao tác kê đồ.

## Khi nào dùng

FS: Short minh họa người đứng trong bố cục phòng. Dạng Short. Không nên dùng khi khớp cứng hoặc hướng nhìn sai tạo uncanny.

## Cách dựng trong HyperFrames

Kỹ thuật character_rig chưa có trong engine như một visual riêng. Tách nhân vật thành nhóm SVG quanh pivot đã đặt; tween góc từng khớp bằng keyframe tuyệt đối. Mọi trạng thái của character_rig là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công cao.

## Rủi ro

khớp cứng hoặc hướng nhìn sai tạo uncanny; không thay lời chứng BUD.
