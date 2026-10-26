---
{
  "id": "3d_reveal",
  "ten": "Reveal vật thể 3D",
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
  "so_muc": 17,
  "so_nguon": 2,
  "nguon": [
    "engine",
    "prompt-motion"
  ],
  "bang_chung_dung": [
    "hyperframes_short/compositions/_tb_fs_nx01.html",
    "hyperframes_short/compositions/_tb_fs_nx02.html",
    "hyperframes_short/compositions/_tb_fs_nx03.html",
    "output/cl_staging/grok/build_nx_v3.py",
    "output/cl_staging/sync_backup_2026-10-26/untracked_files/hyperframes_short/compositions/ui-3d-reveal.html"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/ui-3d-reveal.html",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/.claude/skills/shorts-studio/SKILL.md"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/ui-3d-reveal.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Khối vật thể tách khỏi nền theo chiều sâu; bản NX dùng camera tiến qua mép khối thay vì xoay vật thể liên tục.

## Khi nào dùng

Short mở một khái niệm không gian; Long chỉ khi có vật thể cần soi nhiều mặt. Không nên dùng: Bản vẽ phẳng hoặc chủ thể cần đọc từng dòng.

## Cách dựng trong HyperFrames

Nhánh dựng cho 3d reveal nằm tại `hyperframes_short/compositions/ui-3d-reveal.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/grok/build_nx_v3.py:1`.

composition `ui-3d-reveal.html`; chia lớp theo chiều sâu và khai báo camera transform.

## Rủi ro

Cạnh giả 3D dễ che chữ; ở NX lệch lớp/parallax làm viền đôi.
