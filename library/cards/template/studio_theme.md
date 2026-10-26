---
{
  "id": "studio_theme",
  "ten": "Chủ đề Studio",
  "loai": "template",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giai_thich",
    "tra_cuu",
    "van_hoa"
  ],
  "cam_ngach": [],
  "so_muc": 0,
  "so_nguon": 0,
  "nguon": [],
  "bang_chung_dung": [
    "output/cl_staging/grok/build_bud_nx.py",
    "output/cl_staging/grok/build_nx_v3.py",
    "output/cl_staging/long/build_B18.py",
    "output/cl_staging/long/build_F26.py",
    "output/cl_staging/long/plan_long_w58.json"
  ],
  "vi_du": [],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_short/studio/themes/archive.json",
    "hyperframes_short/studio/themes/blueprint.json",
    "hyperframes_short/studio/themes/saffron.json",
    "hyperframes_short/studio/themes/son-mai.json",
    "hyperframes_short/studio/themes/tet-poster.json"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Theme điều khiển font, nền và màu nhấn cùng lúc; studio theme JSON dùng palette riêng như saffron/son-mai.

## Khi nào dùng

Short/Long cần nhất quán màu theo series. Không nên dùng: Một theme làm subfoot hoặc chữ phụ mất tương phản.

## Cách dựng trong HyperFrames

Nhánh dựng cho studio theme nằm tại `hyperframes_short/studio/themes/saffron.json:1`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:658`.

theme JSON (`saffron|son-mai|blueprint`); chọn theme trong Studio, màu/font lấy từ file theme.

## Rủi ro

Theme ivory có subfoot gold2 chỉ đạt 1.35 contrast ngày 26/10; chọn theme theo cả trạng thái phụ.
