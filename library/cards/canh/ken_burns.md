---
{
  "id": "ken_burns",
  "ten": "Ken Burns trên ảnh",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "anh_tu_lieu",
    "khong_khi"
  ],
  "cam_ngach": [],
  "so_muc": 19,
  "so_nguon": 2,
  "nguon": [
    "LeaddeOpenLab",
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/condzxyz/status/2107594959666728991",
    "https://x.com/__drewface/status/2108663466383016430"
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

Ảnh tĩnh được phóng và lia chậm từ khung rộng tới chi tiết, giữ chủ thể trong vùng an toàn. Mẫu [1](https://x.com/condzxyz/status/2107594959666728991) minh họa lia từ toàn phòng tới cửa; mẫu [2](https://x.com/__drewface/status/2108663466383016430) cho thấy phóng vào chi tiết trong ảnh nguồn.

## Khi nào dùng

FS: Long phân tích một góc phòng từ ảnh tư liệu. Dạng Ca_hai. Không nên dùng khi phóng quá mức lộ ảnh mờ.

## Cách dựng trong HyperFrames

Kỹ thuật ken_burns chưa có trong engine như một visual riêng. Dùng ảnh đủ phân giải và hai transform x/y/scale đã chốt; GSAP tween giữa chúng theo timeline. Mọi trạng thái của ken_burns là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

phóng quá mức lộ ảnh mờ; pan lướt khỏi điểm cần xem.
