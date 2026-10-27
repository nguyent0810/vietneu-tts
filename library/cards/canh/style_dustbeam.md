---
{
  "id": "style_dustbeam",
  "ten": "Phong cách dustbeam",
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
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/dustbeam.html",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/.claude/skills/motion-library/SKILL.md"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {
    "bud": {
      "so_bai": 56,
      "bai": [
        "b01_a",
        "b02_d",
        "b03_e",
        "b04_d",
        "b05_e"
      ]
    }
  },
  "nguon_su_that": [
    "hyperframes_bridge.py"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Chùm sáng xiên làm bụi hiện ra trong không khí; BUD short dùng lớp bụi thưa sau chủ thể.

## Khi nào dùng

Short mở câu chuyện hoặc chuyển cảnh; Long đoạn không lời có chủ thể rõ. Không nên dùng: Bảng tra cứu hay khuôn mặt cần nhìn rõ.

## Cách dựng trong HyperFrames

Nhánh dựng cho style dustbeam nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/build_shorts_bu_1006.py:1`.

style `dustbeam`; caller cấp figure/media; build_shorts_bu_1006 là ví dụ tạo.

## Rủi ro

Bụi đè chi tiết/độ tương phản; layer sáng không được che chữ vàng.
