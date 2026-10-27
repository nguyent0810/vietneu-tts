---
{
  "id": "style_ember_long",
  "ten": "Phong cách ember_long",
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
    "output/cl_staging/long/build_B11.py",
    "output/cl_staging/long/build_B14.py",
    "output/cl_staging/long/build_B17.py",
    "output/cl_staging/long/build_B20.py",
    "output/cl_staging/long/build_B25.py"
  ],
  "vi_du": [
    "file:///private/tmp/claude-501/-Users-nguyenthanhtung-Documents-Local-AI-Vietneu-TTS/6b542814-f0c8-4cb2-a2ff-54a242acf06a/scratchpad/wt_lib/hyperframes_short/compositions/ember_long.html"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {
    "bud": {
      "so_bai": 12,
      "bai": [
        "L_bud_09",
        "L_bud_25",
        "L_bud_26",
        "T_lf_after",
        "T_lf_before"
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

Nền tối và điểm lửa nhỏ tạo vùng sáng ấm, nhịp lửa đi theo cảnh chứ không bao khung.

## Khi nào dùng

Long truyện có bếp/lửa hoặc chuyển đoạn nội tâm. Không nên dùng: Bài tra cứu năm hoặc bài BUD cần tĩnh.

## Cách dựng trong HyperFrames

Nhánh dựng cho style ember long nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/long/build_B11.py:1`.

style `ember_long`; caller chia cảnh theo câu đọc; build_B11 là ví dụ thực tế.

## Rủi ro

Ngọn lửa lặp đều trông giả; tiêu đề nhạt nếu đặt trên vùng vàng sáng.
