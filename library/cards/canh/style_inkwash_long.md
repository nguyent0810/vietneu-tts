---
{
  "id": "style_inkwash_long",
  "ten": "Phong cách inkwash_long",
  "loai": "canh",
  "dinh_dang": [
    "long"
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
  "so_muc": 4,
  "so_nguon": 1,
  "nguon": [
    "engine"
  ],
  "bang_chung_dung": [
    "output/cl_staging/long/build_B1.py",
    "output/cl_staging/long/build_B12.py",
    "output/cl_staging/long/build_B15.py",
    "output/cl_staging/long/build_B18.py",
    "output/cl_staging/long/build_B2.py"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/inkwash_long.html",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/.claude/skills/motion-library/SKILL.md"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {
    "bud": {
      "so_bai": 12,
      "bai": [
        "L_bud_03",
        "L_bud_04",
        "L_bud_05",
        "L_bud_06",
        "L_bud_07"
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

Khung giấy mực mở rộng cho tiêu đề và tranh theo chương; các bản B dài dùng cùng vùng chữ xuyên nhiều cảnh.

## Khi nào dùng

Long truyện/giải thích Phật học; Short dùng bản rút gọn riêng. Không nên dùng: Video bảng tra cứu dày hoặc muốn nhấn dữ liệu kỹ thuật.

## Cách dựng trong HyperFrames

Nhánh dựng cho style inkwash long nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/long/build_B1.py:1`.

style `inkwash_long`; caller Longform; build_B1 là ví dụ nối cảnh dài.

## Rủi ro

Chữ trắng đặt vào vùng loang tối; frame chuyển cảnh đổi nền khiến độ tương phản nhảy.
