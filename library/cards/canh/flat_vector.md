---
{
  "id": "flat_vector",
  "ten": "Đồ họa vector phẳng",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "minh_hoa",
    "do_hoa"
  ],
  "cam_ngach": [],
  "so_muc": 291,
  "so_nguon": 3,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/songkeys/status/2102743212922384673",
    "https://x.com/Ror_Fly/status/2102853258582880547"
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

Mảng màu phẳng, viền gọn, bóng tối giản tạo hình minh họa có thể scale mà không vỡ nét. Mẫu [1](https://x.com/songkeys/status/2102743212922384673) minh họa minh họa cửa và cửa sổ bằng mảng hình; mẫu [2](https://x.com/Ror_Fly/status/2102853258582880547) cho thấy tách icon đồ vật theo lớp màu.

## Khi nào dùng

FS: Short chỉ vị trí cửa trên sơ đồ. Dạng Ca_hai. Không nên dùng khi tối giản quá làm mất định hướng.

## Cách dựng trong HyperFrames

Kỹ thuật flat_vector chưa có trong engine như một visual riêng. Vẽ nhóm SVG theo palette khóa; animate transform/opacity và giữ viewBox cố định khi scale. Mọi trạng thái của flat_vector là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

tối giản quá làm mất định hướng; pha nhiều bộ icon trông như stock AI.
