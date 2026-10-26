---
{
  "id": "style_inkwash",
  "ten": "Phong cách inkwash",
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
  "so_muc": 9,
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
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/inkwash.html"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {
    "bud": {
      "so_bai": 53,
      "bai": [
        "b01_b",
        "b02_c",
        "b03_d",
        "b04_b",
        "b05_d"
      ]
    },
    "fs": {
      "so_bai": 25,
      "bai": [
        "f01_c",
        "f02_c",
        "f03_c",
        "f04_c",
        "f28_c"
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

Nền giấy có loang mực ở rìa, khoảng trắng ở giữa dành cho lời; bản BUD phối mực với nhấn vàng.

## Khi nào dùng

Short câu kệ/trích dẫn; Long đoạn giáo lý cần tiết chế. Không nên dùng: Cảnh có nhiều ảnh thật hoặc nội dung tốc độ cao.

## Cách dựng trong HyperFrames

Nhánh dựng cho style inkwash nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/build_shorts_bu_1006.py:1`.

style `inkwash`; chỉ bật reveal `ink` với `PAPER_STYLES` trong bridge.

## Rủi ro

Mực loang dưới chữ làm mất nét; chỉ dùng reveal ink khi style thật sự có nền giấy.
