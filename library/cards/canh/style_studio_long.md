---
{
  "id": "style_studio_long",
  "ten": "Phong cách studio_long",
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
  "so_muc": 5,
  "so_nguon": 1,
  "nguon": [
    "engine"
  ],
  "bang_chung_dung": [
    "output/cl_staging/long/build_BT01.py",
    "output/cl_staging/long/build_BT02.py",
    "output/cl_staging/long/build_BT03.py",
    "output/cl_staging/long/build_BT04.py",
    "output/cl_staging/long/build_FT01.py"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/studio_long.html",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/longform.js"
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

Mặt bàn và khung làm việc cho phép đặt nhiều tài liệu như một buổi phân tích; build_BT/FT dùng theme theo series.

## Khi nào dùng

Long bàn luận nhiều nguồn hoặc đọc tài liệu. Không nên dùng: Short một mệnh đề đơn giản không cần đạo cụ.

## Cách dựng trong HyperFrames

Nhánh dựng cho style studio long nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/long/build_BT01.py:1`.

style `studio_long`; truyền theme và media theo build_BT01.

## Rủi ro

Theme sai làm font/màu lệch; nhiều tài liệu chồng nhau khó biết đâu là nguồn chính.
