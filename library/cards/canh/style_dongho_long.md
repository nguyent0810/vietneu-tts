---
{
  "id": "style_dongho_long",
  "ten": "Phong cách dongho_long",
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
    "output/cl_staging/long/build_F11.py",
    "output/cl_staging/long/build_F14.py",
    "output/cl_staging/long/build_F17.py",
    "output/cl_staging/long/build_F20.py",
    "output/cl_staging/long/build_F26.py"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/dongho_long.html"
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

Bảng lịch dài có vòng giờ và nhãn ngày, mạch hình chuyển từ mặt đồng hồ sang các ô tra cứu.

## Khi nào dùng

Long giải thích ngày/giờ theo từng chặng; Short dùng chỉ một mặt lịch. Không nên dùng: Nguồn lịch chưa xác định múi giờ hoặc quy ước tháng.

## Cách dựng trong HyperFrames

Nhánh dựng cho style dongho long nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/long/build_F11.py:1`.

style long qua `render(style=...)`; composition `dongho_long.html`, plan/build_F11 là ví dụ caller.

## Rủi ro

Mốc âm lịch lệch tháng sẽ làm bảng sai dù layout cân.
