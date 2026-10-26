---
{
  "id": "style_casemap",
  "ten": "Phong cách casemap",
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
    "output/cl_staging/hyperframes_oct/plan_o05.json",
    "output/cl_staging/hyperframes_sept/plan_d29.json"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/casemap.html"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_bridge.py"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Tông bản đồ tối, đường ranh sáng và marker ấm dẫn mắt theo tuyến; style được gọi qua bridge rồi nạp composition casemap.

## Khi nào dùng

Long khảo cứu địa danh; Short chọn cảnh map khi câu nói có tuyến cụ thể. Không nên dùng: Bản đồ chỉ làm nền trang trí cho nội dung không gian khác.

## Cách dựng trong HyperFrames

Nhánh dựng cho style casemap nằm tại `hyperframes_bridge.py:658`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/hyperframes_oct/plan_o05.json:1`.

style `casemap`; `render(style="casemap", visuals=...)`; plan_o05 là cấu hình dùng thật.

## Rủi ro

Tọa độ giả làm lệch tuyến; ranh giới mờ khiến vị trí bị đọc nhầm.
