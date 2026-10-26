---
{
  "id": "parallax_2_5d",
  "ten": "Parallax 2.5D",
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
  "so_muc": 36,
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
    "output/cl_staging/sync_backup_2026-10-26/untracked_files/hyperframes_short/compositions/ui-3d-reveal.html"
  ],
  "vi_du": [
    "https://x.com/koldo2k/status/2103129343253778767",
    "https://x.com/agentgamesbot/status/2103401820261355554"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/ui-3d-reveal.html"
  ],
  "alias": [
    "card_2_5d"
  ],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Tiền cảnh và nền chạy lệch tốc độ tạo chiều sâu giả; reveal NX tách lớp ảnh trước khi camera tiến.

## Khi nào dùng

Short reveal một địa điểm; Long di chuyển chậm qua ảnh minh họa. Không nên dùng: Ảnh đơn không thể tách chủ thể khỏi nền sạch.

## Cách dựng trong HyperFrames

Nhánh dựng cho parallax 2 5d nằm tại `hyperframes_short/compositions/ui-3d-reveal.html:1`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:703`.

composition `ui-3d-reveal.html`; tách foreground/background, camera depth có mức nhẹ.

## Rủi ro

Mask quanh tóc/viền tạo halo; biên lớp hở lộ nền giả.
