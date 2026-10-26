---
{
  "id": "line_draw",
  "ten": "Nét vẽ hiện dần",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "so_do",
    "reveal"
  ],
  "cam_ngach": [],
  "so_muc": 21,
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
    "https://x.com/cristianvega/status/2110046079983001783",
    "https://x.com/hanifproduktif/status/2102695622042411419"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
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

Path được lộ theo chiều dài stroke, cho thấy đường biên hoặc tuyến được vẽ theo thứ tự. Mẫu [1](https://x.com/cristianvega/status/2110046079983001783) minh họa vẽ vòng ranh giới trên sơ đồ; mẫu [2](https://x.com/hanifproduktif/status/2102695622042411419) cho thấy lộ tuyến trước khi đặt nhãn.

## Khi nào dùng

FS: Short vẽ tuyến đi trên mặt bằng. Dạng Ca_hai. Không nên dùng khi đầu path hở dễ lộ.

## Cách dựng trong HyperFrames

Kỹ thuật line_draw chưa có trong engine như một visual riêng. Lưu path SVG và độ dài; điều khiển stroke-dashoffset bằng progress t, không phụ thuộc frame trước. Mọi trạng thái của line_draw là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công thap.

## Rủi ro

đầu path hở dễ lộ; nét sai chiều gợi đường đi ngược.
