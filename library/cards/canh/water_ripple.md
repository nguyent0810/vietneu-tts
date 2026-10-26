---
{
  "id": "water_ripple",
  "ten": "Gợn sóng nước",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "hieu_ung",
    "thien_nhien"
  ],
  "cam_ngach": [
    "fs",
    "bud"
  ],
  "so_muc": 48,
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
    "https://x.com/Viggle_PINOC/status/2102861939072434495",
    "https://x.com/alexwtlf/status/2103713416367981005"
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
  "cong": "vua"
}
---

## Mô tả

Vòng gợn đồng tâm nở khỏi một điểm, bán kính tăng khi opacity giảm. Mẫu [1](https://x.com/Viggle_PINOC/status/2102861939072434495) minh họa vẽ gợn trên mặt hồ trong ảnh nguồn; mẫu [2](https://x.com/alexwtlf/status/2103713416367981005) cho thấy làm gợn mờ dần theo thời gian.

## Khi nào dùng

Không hợp FS/BUD nếu chỉ là nền; thử giải thích mặt nước. Dạng Short. Không nên dùng khi nhiều vòng tăng tải gpu.

## Cách dựng trong HyperFrames

Kỹ thuật water_ripple chưa có trong engine như một visual riêng. Vẽ vài ellipse/path; bán kính và opacity lấy từ easing(t) hữu hạn, không dùng fluid simulation. Mọi trạng thái của water_ripple là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

nhiều vòng tăng tải GPU; gợn che chi tiết ảnh/bản đồ.
