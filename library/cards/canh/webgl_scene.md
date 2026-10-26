---
{
  "id": "webgl_scene",
  "ten": "Cảnh WebGL",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "3d",
    "do_hoa"
  ],
  "cam_ngach": [
    "fs",
    "bud"
  ],
  "so_muc": 41,
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
    "https://x.com/jrayon/status/2102861376184054015",
    "https://x.com/AxtonLiu/status/2103119648271290566"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 0,
    "bud": 0
  },
  "cong": "cao"
}
---

## Mô tả

Canvas WebGL dựng vật thể/lưới 3D, camera và đèn theo không gian thay vì chỉ là lớp ảnh. Mẫu [1](https://x.com/jrayon/status/2102861376184054015) minh họa xoay mô hình hình học có dữ liệu; mẫu [2](https://x.com/AxtonLiu/status/2103119648271290566) cho thấy đổi góc nhìn vật thể 3D.

## Khi nào dùng

Không hợp FS/BUD trừ mô hình khoa học đã đối chiếu. Dạng Ca_hai. Không nên dùng khi driver/gpu headless gây lệch.

## Cách dựng trong HyperFrames

Kỹ thuật webgl_scene chưa có trong engine như một visual riêng. Bake camera thành sprite nếu có thể; nếu giữ WebGL thì camera/material là keyframe theo t, tắt render loop realtime. Mọi trạng thái của webgl_scene là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công cao.

## Rủi ro

driver/GPU headless gây lệch; tốn VRAM và sai tỷ lệ gây hiểu lầm.
