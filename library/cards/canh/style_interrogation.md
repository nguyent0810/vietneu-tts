---
{
  "id": "style_interrogation",
  "ten": "Phong cách interrogation",
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
    "output/cl_staging/hyperframes_oct/plan_o03.json",
    "output/cl_staging/hyperframes_oct/plan_o08.json",
    "output/cl_staging/hyperframes_sept/plan_d27.json"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/interrogation.html"
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

Ánh đèn tập trung vào một vùng, xung quanh tối như bàn hỏi cung; plan O03/O08 dùng style làm khung căng thẳng.

## Khi nào dùng

Short mở câu hỏi có căn cứ; Long điều tra một mâu thuẫn nguồn. Không nên dùng: Bài hướng dẫn, sức khỏe hoặc BUD cần giọng ôn hòa.

## Cách dựng trong HyperFrames

Nhánh dựng cho style interrogation nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/hyperframes_oct/plan_o03.json:1`.

style `interrogation`; plan_o03/O08 là ví dụ; hạn chế vùng spotlight ở một điểm.

## Rủi ro

Đèn gắt làm mất mặt/chi tiết; ngôn ngữ gợi buộc tội khi chứng cứ chưa đủ.
