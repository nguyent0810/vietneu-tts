---
{
  "id": "style_laban_long",
  "ten": "Phong cách laban_long",
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
  "so_muc": 3,
  "so_nguon": 1,
  "nguon": [
    "engine"
  ],
  "bang_chung_dung": [
    "output/cl_staging/long/build_F1.py",
    "output/cl_staging/long/build_F12.py",
    "output/cl_staging/long/build_F15.py",
    "output/cl_staging/long/build_F18.py",
    "output/cl_staging/long/build_F2.py"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/laban.html",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/laban_long.html"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {
    "fs": {
      "so_bai": 14,
      "bai": [
        "L_fs_01b",
        "L_fs_03",
        "L_fs_04",
        "L_fs_05",
        "L_fs_06"
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

Bát quái và dải nội dung trải theo khung ngang, từng mục có chỗ giải nghĩa; build_F1/F2 dùng nhịp chương dài.

## Khi nào dùng

Long giải thích hệ thống cung/hướng; Short chọn một quan hệ đơn. Không nên dùng: Bảng ngày có nhiều hàng cần tra đồng thời.

## Cách dựng trong HyperFrames

Nhánh dựng cho style laban long nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/long/build_F1.py:1`.

style `laban_long`; caller Long theo build_F1, các nhịp chia theo chương.

## Rủi ro

Mốc chuyển cung cố định không theo số mục sẽ để trống cuối hoặc dồn nhãn.
