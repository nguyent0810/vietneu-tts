---
{
  "id": "lottie_motion",
  "ten": "Lottie animation",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "do_hoa",
    "asset"
  ],
  "cam_ngach": [
    "fs",
    "bud"
  ],
  "so_muc": 10,
  "so_nguon": 1,
  "nguon": [
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://prompt-motion.com/kantamk-61f410",
    "https://prompt-motion.com/samaote-5e2fc2"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 0,
    "bud": 0
  },
  "cong": "vua"
}
---

## Mô tả

Asset vector Lottie gồm shape/keyframe đóng gói, phát theo tiến độ của một animation. Mẫu [1](https://prompt-motion.com/kantamk-61f410) minh họa chạy icon vector theo các mốc đã khóa; mẫu [2](https://prompt-motion.com/samaote-5e2fc2) cho thấy dùng shape animation thay footage.

## Khi nào dùng

Không hợp FS/BUD nếu chỉ thêm mascot/hiệu ứng thương mại. Dạng Ca_hai. Không nên dùng khi runtime có thể lệch khi seek.

## Cách dựng trong HyperFrames

Kỹ thuật lottie_motion chưa có trong engine như một visual riêng. Nếu dùng Lottie cục bộ, đặt progress = f(t/duration); nếu runtime không seek-safe, bake thành sprite và chọn frame từ t. Mọi trạng thái của lottie_motion là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

runtime có thể lệch khi seek; file phức tạp tăng bundle.
