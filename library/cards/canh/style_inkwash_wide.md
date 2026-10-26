---
{
  "id": "style_inkwash_wide",
  "ten": "Phong cách inkwash_wide",
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
  "so_muc": 2,
  "so_nguon": 1,
  "nguon": [
    "engine"
  ],
  "bang_chung_dung": [
    "output/cl_staging/long/plan_long_w40.json"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/inkwash_wide.html"
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

Bố cục ngang để tranh mực thở ở hai bên, tiêu đề nằm trong dải trống giữa; plan long_w40 dùng biến thể wide.

## Khi nào dùng

Long 16:9 có voice và tranh rộng. Không nên dùng: Short dọc hoặc đồ thị nhiều nhãn.

## Cách dựng trong HyperFrames

Nhánh dựng cho style inkwash wide nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/long/plan_long_w40.json:1`.

style `inkwash_wide`; bố cục ngang, plan_long_w40 khai báo style.

## Rủi ro

Ảnh portrait bị kéo rộng; safe zone ngang không tự chuyển sang canvas dọc.
