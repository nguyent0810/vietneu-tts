---
{
  "id": "ink_drawing",
  "ten": "Tranh mực / nét vẽ",
  "loai": "canh",
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
  "so_muc": 199,
  "so_nguon": 5,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "hyperframes_short/compositions/_tb_fs_nx01.html",
    "hyperframes_short/compositions/_tb_fs_nx02.html",
    "hyperframes_short/compositions/_tb_fs_nx03.html",
    "output/cl_staging/grok/build_bud_1023.py",
    "output/cl_staging/grok/build_bud_t.py"
  ],
  "vi_du": [
    "https://x.com/Michaelzsguo/status/2102592355165782312",
    "https://x.com/songkeys/status/2102743212922384673"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/components/ink-bleed-reveal.html",
    "hyperframes_short/compositions/inkwash.html",
    "hyperframes_short/compositions/inkwash_long.html",
    "hyperframes_short/compositions/inkwash_wide.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Nét mực lan từ mép chữ hoặc hình như thấm giấy; ink-bleed-reveal dùng mask theo alpha.

## Khi nào dùng

Short câu trích hoặc mở ý; Long hợp phong cách giấy/mực Á Đông. Không nên dùng: Style nền tối không có chất giấy hoặc chữ phải hiện ngay tức thì.

## Cách dựng trong HyperFrames

Nhánh dựng cho ink drawing nằm tại `hyperframes_short/compositions/components/ink-bleed-reveal.html:1`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:779`.

component `ink-bleed-reveal.html`; mask alpha trên giấy và gọi reveal `ink`.

## Rủi ro

Reveal ink chỉ hợp PAPER_STYLES; trên style tối mask làm chữ biến mất.
