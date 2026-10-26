---
{
  "id": "style_clean",
  "ten": "Phong cách clean",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giai_thich",
    "van_hoa",
    "lich_su"
  ],
  "cam_ngach": [],
  "so_muc": 57,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "hyperframes_short/compositions/_tb_fs_yd_01.html",
    "output/cl_staging/grok/build_budlookup.py",
    "output/cl_staging/grok/build_fs_1023.py",
    "output/cl_staging/grok/build_r1026.py",
    "output/cl_staging/grok/build_statues_bank.py"
  ],
  "vi_du": [
    "https://x.com/twoclipping/status/2102554209166000267",
    "https://x.com/deedydas/status/2102787937482252537"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_bridge.py"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Nền sáng thoáng, chữ và ảnh tách lớp rõ; bản statue lookup dùng saffron/clean để giữ bảng và tượng dễ đọc.

## Khi nào dùng

Short tra cứu hoặc giải thích ít dữ liệu; Long khi ưu tiên thông tin hơn texture. Không nên dùng: Cần không khí tư liệu tối hoặc hình ảnh nhiều lớp giàu cảm xúc.

## Cách dựng trong HyperFrames

Nhánh dựng cho style clean nằm tại `hyperframes_bridge.py:674`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/grok/build_budlookup.py:1`.

style `clean`; `render(style="clean")`; dùng palette sáng và đặt visuals nếu cần.

## Rủi ro

Màu chữ gold2 chìm trên nền ivory; kiểm contrast trên dòng phụ, không chỉ tiêu đề.
