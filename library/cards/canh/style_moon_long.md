---
{
  "id": "style_moon_long",
  "ten": "Phong cách moon_long",
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
    "output/cl_staging/long/build_B10.py",
    "output/cl_staging/long/build_B13.py",
    "output/cl_staging/long/build_B16.py",
    "output/cl_staging/long/build_B19.py",
    "output/cl_staging/long/build_B4.py"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/moon_long.html"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {
    "bud": {
      "so_bai": 7,
      "bai": [
        "L_bud_08",
        "L_bud_11",
        "L_bud_14",
        "L_bud_17",
        "L_bud_20"
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

Trăng làm điểm sáng trên cảnh đêm, không gian rộng giữ đường nhìn đến nhân vật; build_B10/B13 dùng cảnh trăng truyện.

## Khi nào dùng

Long truyện tiền hiện đại hoặc cảnh đêm có căn cứ trong lời. Không nên dùng: Nội dung dữ kiện khô hoặc bối cảnh ban ngày.

## Cách dựng trong HyperFrames

Nhánh dựng cho style moon long nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/long/build_B10.py:1`.

style `moon_long`; caller build_B10; giữ trăng làm nguồn sáng nền.

## Rủi ro

Trăng quá lớn lấn chủ thể; mốc tối phải đủ sáng cho chi tiết chính.
