---
{
  "id": "film_grain",
  "ten": "Hạt phim",
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
  "so_muc": 27,
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
    "output/cl_staging/grok/build_nx_v3.py",
    "output/cl_staging/sync_backup_2026-10-26/untracked_files/hyperframes_short/compositions/components/grain-overlay.html"
  ],
  "vi_du": [
    "https://x.com/koldo2k/status/2103129343253778767",
    "https://x.com/jake11moran/status/2103237884564414633"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/components/grain-overlay.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Hạt phim phủ đồng đều lên hình, làm nền bớt sạch kiểu kỹ thuật số; overlay NX nằm trên footage.

## Khi nào dùng

Short hoài niệm hoặc tư liệu; Long cần thống nhất chất ảnh qua nhiều cảnh. Không nên dùng: Bảng số nhỏ, chữ mảnh hoặc cảnh cần độ sắc nét cao.

## Cách dựng trong HyperFrames

Nhánh dựng cho film grain nằm tại `hyperframes_short/compositions/components/grain-overlay.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/grok/build_nx_v3.py:1`.

component `grain-overlay.html`; đặt lớp grain trên ảnh/clip, chỉnh opacity của overlay.

## Rủi ro

Grain dày ăn mất nét chữ và chi tiết mặt; overlay không nên làm nhấp sáng.
