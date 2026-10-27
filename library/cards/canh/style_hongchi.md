---
{
  "id": "style_hongchi",
  "ten": "Phong cách hongchi",
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
  "so_muc": 2,
  "so_nguon": 1,
  "nguon": [
    "engine"
  ],
  "bang_chung_dung": [
    "output/cl_staging/build_shorts_bu_1006.py",
    "output/cl_staging/build_shorts_bu_1006b.py",
    "output/cl_staging/build_shorts_fs_test_1013.py",
    "output/cl_staging/build_shorts_v2_1.py",
    "output/cl_staging/build_shorts_v2_2.py"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/hongchi.html"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {
    "fs": {
      "so_bai": 52,
      "bai": [
        "f01_a",
        "f02_a",
        "f03_a",
        "f04_a",
        "f29_a"
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

Chữ mực đỏ đậm đặt trên nền giấy, hình khắc gọn thành cụm; Hongchi làm tiêu đề theo tranh in dân gian.

## Khi nào dùng

Short Tết/văn hóa dân gian; Long chương giải thích có không khí tranh khắc. Không nên dùng: Số liệu cần nền trung tính hoặc chủ đề không liên quan.

## Cách dựng trong HyperFrames

Nhánh dựng cho style hongchi nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/build_shorts_bu_1006.py:1`.

style `hongchi`; caller `render(style="hongchi")`; giữ nhãn chữ trong vùng giấy.

## Rủi ro

Chữ đỏ và nền đỏ nhập nhau; hoạ tiết dày cạnh dấu tiếng Việt làm giảm độ đọc.
