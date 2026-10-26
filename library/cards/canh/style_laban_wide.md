---
{
  "id": "style_laban_wide",
  "ten": "Phong cách laban_wide",
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
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/laban.html",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/laban_long.html"
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

Lưới phương vị rộng, tâm sơ đồ giữ giữa canvas còn phần giải nghĩa mở hai bên; plan_long_w40 chọn wide.

## Khi nào dùng

Long có nhiều nhãn quanh sơ đồ. Không nên dùng: Short vertical hoặc chỉ một chữ khóa.

## Cách dựng trong HyperFrames

Nhánh dựng cho style laban wide nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/long/plan_long_w40.json:1`.

style `laban_wide`; plan_long_w40; bố cục ngang, không đổi sang portrait.

## Rủi ro

Khi cắt xuống dọc, nhãn biên rơi khỏi khung.
