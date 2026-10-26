---
{
  "id": "style_lightfield",
  "ten": "Phong cách lightfield",
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
  "so_muc": 3,
  "so_nguon": 1,
  "nguon": [
    "engine"
  ],
  "bang_chung_dung": [
    "output/cl_staging/build_shorts_bu_1006.py",
    "output/cl_staging/build_shorts_bu_1006b.py",
    "output/cl_staging/build_shorts_bud_b2_1013.py",
    "output/cl_staging/build_shorts_v2_1.py",
    "output/cl_staging/build_shorts_v2_2.py"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/lightfield.html",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/.claude/skills/motion-library/SKILL.md"
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

Một dải sáng rộng mở từ nền tối, chữ nằm ở vùng tương phản cao; BUD build dùng lightfield làm nền mềm.

## Khi nào dùng

Short câu dẫn mở đầu hoặc nhãn một ý. Không nên dùng: Cảnh nhiều chữ hay nền gốc sáng.

## Cách dựng trong HyperFrames

Nhánh dựng cho style lightfield nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/build_shorts_bu_1006.py:1`.

style `lightfield`; caller short dùng vùng sáng làm nền, không đặt chữ trên bloom.

## Rủi ro

Vùng bloom làm chữ trắng mất biên; giữ tâm sáng lệch khỏi caption.
