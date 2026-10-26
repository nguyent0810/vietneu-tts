---
{
  "id": "light_leak",
  "ten": "Rò sáng / flare",
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
  "so_muc": 26,
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
    "output/cl_staging/sync_backup_2026-10-26/untracked_files/hyperframes_short/compositions/lens-flare.html"
  ],
  "vi_du": [
    "https://x.com/twoclipping/status/2102554209166000267",
    "https://x.com/alexwtlf/status/2103713416367981005"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/lens-flare.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Dải sáng ấm lọt từ cạnh khung, chạy ngang ảnh rồi tan; lens-flare là lớp riêng phía trên footage.

## Khi nào dùng

Short chuyển hồi ức hoặc đổi chương; Long dùng ở một điểm chuyển nhịp. Không nên dùng: Bảng dữ liệu hoặc cảnh cần màu chính xác.

## Cách dựng trong HyperFrames

Nhánh dựng cho light leak nằm tại `hyperframes_short/compositions/lens-flare.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/grok/build_nx_v3.py:1`.

composition `lens-flare.html`; lớp flare độc lập, đặt ngoài vùng chữ và fade về 0.

## Rủi ro

Flare làm bạc vùng sáng và mất chi tiết; không để vệt nằm trên mặt.
