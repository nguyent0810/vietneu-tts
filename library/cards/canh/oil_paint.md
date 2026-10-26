---
{
  "id": "oil_paint",
  "ten": "Sơn dầu",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "giai_thich",
    "tra_cuu",
    "van_hoa"
  ],
  "cam_ngach": [],
  "so_muc": 11,
  "so_nguon": 3,
  "nguon": [
    "athemeroy",
    "engine",
    "prompt-motion"
  ],
  "bang_chung_dung": [
    "output/cl_staging/build_shorts_bu_1006.py",
    "output/cl_staging/build_shorts_bu_1006b.py",
    "output/cl_staging/build_shorts_bud_b2_1013.py",
    "output/cl_staging/build_shorts_v2_1.py",
    "output/cl_staging/build_shorts_v2_2.py"
  ],
  "vi_du": [
    "https://x.com/Tz_2022/status/2102501726431687055",
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/oilpaint.html"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/oilpaint.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Ảnh có vệt cọ và mảng màu dày như tranh sơn dầu; oilpaint giữ cấu trúc chủ thể thay vì biến toàn khung thành texture.

## Khi nào dùng

Short minh họa văn hóa/kể chuyện; Long làm chất liệu cho ảnh tĩnh. Không nên dùng: Cần đọc chữ nhỏ trên tài liệu gốc hoặc ảnh cần trung thực màu.

## Cách dựng trong HyperFrames

Nhánh dựng cho oil paint nằm tại `hyperframes_short/compositions/oilpaint.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/build_shorts_bu_1006.py:1`.

composition `oilpaint.html`; chọn asset và đặt texture trên lớp ảnh.

## Rủi ro

Texture che mắt và chữ trên ảnh; màu cọ có thể khiến tư liệu trông như ảnh thật.
