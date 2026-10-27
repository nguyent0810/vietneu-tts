---
{
  "id": "style_laban",
  "ten": "Phong cách laban",
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
  "so_muc": 5,
  "so_nguon": 1,
  "nguon": [
    "engine"
  ],
  "bang_chung_dung": [
    "output/cl_staging/build_shorts_bu_1006.py",
    "output/cl_staging/build_shorts_fs_test_1013.py",
    "output/cl_staging/build_shorts_v2_1.py",
    "output/cl_staging/build_shorts_v2_2.py",
    "output/cl_staging/grok/build_fs2027.py"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/laban.html",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/laban_long.html"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {
    "fs": {
      "so_bai": 52,
      "bai": [
        "f01_b",
        "f01_e",
        "f02_b",
        "f02_e",
        "f03_b"
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

Lưới bát quái và ô chữ hiện từng lớp; Laban đặt nội dung phong thủy vào bố cục có trục giữa.

## Khi nào dùng

Short tra cứu khái niệm bát quái; Long giải thích quan hệ cung/hướng. Không nên dùng: Nội dung không có cấu trúc phương vị.

## Cách dựng trong HyperFrames

Nhánh dựng cho style laban nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/build_shorts_bu_1006.py:1`.

style `laban`; caller short theo build_shorts_bu_1006, nhãn điền đúng cung.

## Rủi ro

Nhãn cung đặt sai vòng làm sai nghĩa; cỡ chữ trong 8 ô phải kiểm ở portrait.
