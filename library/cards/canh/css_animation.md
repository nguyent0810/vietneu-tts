---
{
  "id": "css_animation",
  "ten": "Chuyển động CSS",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giao_dien",
    "huong_dan"
  ],
  "cam_ngach": [],
  "so_muc": 73,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/twoclipping/status/2102554209166000267",
    "https://x.com/GonzaloMacagno/status/2102897651008344202"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 2,
    "bud": 1
  },
  "cong": "thap"
}
---

## Mô tả

Phần tử giao diện đổi transform/opacity/clip-path bằng keyframe CSS thay vì footage. Mẫu [1](https://x.com/twoclipping/status/2102554209166000267) minh họa mở tuần tự các nhãn hướng; mẫu [2](https://x.com/GonzaloMacagno/status/2102897651008344202) cho thấy trượt thẻ chú giải vào khung.

## Khi nào dùng

FS: Short giải thích ba bước chọn hướng cửa. Dạng Ca_hai. Không nên dùng khi css infinite chạy theo clock thật lệch khi seek.

## Cách dựng trong HyperFrames

Kỹ thuật css_animation chưa có trong engine như một visual riêng. Dùng CSS keyframes hữu hạn hoặc GSAP cho transform/opacity; không dùng animation vô hạn theo wall-clock. Mọi trạng thái của css_animation là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

CSS infinite chạy theo clock thật lệch khi seek; easing nảy phá nhịp.
