---
{
  "id": "particle_dissolve",
  "ten": "Tan thành hạt",
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
    "output/cl_staging/sync_backup_2026-10-26/untracked_files/hyperframes_short/compositions/components/particle-text-dissolve.html"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/components/particle-text-dissolve.html",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/.claude/skills/shorts-studio/SKILL.md"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_short/compositions/components/particle-text-dissolve.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Chữ rã thành hạt nhỏ rồi tan khỏi vùng đọc; component particle-text-dissolve gắn chuyển động vào glyph.

## Khi nào dùng

Short chuyển ý hoặc kết một cụm chữ; Long chỉ dùng ở đoạn nghỉ. Không nên dùng: Tên riêng, câu trích hoặc dữ liệu phải còn đọc được.

## Cách dựng trong HyperFrames

Nhánh dựng cho particle dissolve nằm tại `hyperframes_short/compositions/components/particle-text-dissolve.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/grok/build_nx_v3.py:1`.

component `particle-text-dissolve.html`; gắn selector chữ và thời lượng dissolve.

## Rủi ro

Dissolve quá sớm mất nghĩa; hạt còn lại có thể bẩn frame cuối.
