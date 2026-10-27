---
{
  "id": "style_dossier",
  "ten": "Phong cách dossier",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "cl"
  ],
  "hop_ngach": [
    "ho_so",
    "lich_su",
    "giai_thich"
  ],
  "cam_ngach": [
    "bud"
  ],
  "so_muc": 2,
  "so_nguon": 1,
  "nguon": [
    "engine"
  ],
  "bang_chung_dung": [
    "output/cl_staging/hyperframes_oct/plan_o02.json",
    "output/cl_staging/hyperframes_oct/plan_o07.json",
    "output/cl_staging/hyperframes_sept/plan_d26.json"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/dossier.html"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_bridge.py"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Tờ hồ sơ ghim trên nền giấy, có ảnh và chú thích như tài liệu lưu trữ; dossier dùng trang giấy làm khung nội dung.

## Khi nào dùng

Long kể hồ sơ/diễn biến cần nhiều tư liệu; Short một thẻ trích có nguồn. Không nên dùng: Nội dung thiền/giáo lý cần nhịp tĩnh và không có hồ sơ.

## Cách dựng trong HyperFrames

Nhánh dựng cho style dossier nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/hyperframes_oct/plan_o02.json:1`.

style `dossier`; caller cấp media/visuals; `plan_o02.json` có `style` cụ thể.

## Rủi ro

Ảnh và chú thích sát mép giấy bị crop; nội dung giả tài liệu không được trình bày như chứng cứ thật.
