---
{
  "id": "style_oilpaint",
  "ten": "Phong cách oilpaint",
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
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/oilpaint.html",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/.claude/skills/motion-library/SKILL.md"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {
    "bud": {
      "so_bai": 56,
      "bai": [
        "b01_c",
        "b02_e",
        "b03_b",
        "b04_c",
        "b05_a"
      ]
    },
    "fs": {
      "so_bai": 27,
      "bai": [
        "f01_d",
        "f02_d",
        "f03_d",
        "f04_d",
        "f28_d"
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

Bề mặt cọ dày và viền loang làm ảnh có chất tranh; khác lớp oil_paint ở chỗ đây là style nền cho cả cảnh.

## Khi nào dùng

Short tranh minh họa một cảnh; Long giữ thống nhất một chương ảnh. Không nên dùng: Tư liệu ảnh thật cần kiểm chi tiết.

## Cách dựng trong HyperFrames

Nhánh dựng cho style oilpaint nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/build_shorts_bu_1006.py:1`.

style `oilpaint`; caller short build_shorts_bu_1006; chọn ảnh minh họa có viền rõ.

## Rủi ro

Mặt người có thể biến dạng do texture; đừng mô tả tranh như ảnh ghi nhận.
