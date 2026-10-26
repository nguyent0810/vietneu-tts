---
{
  "id": "style_silence",
  "ten": "Phong cách silence",
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
  "so_muc": 20,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "output/cl_staging/build_shorts_bu_1006.py",
    "output/cl_staging/build_shorts_bu_1006b.py",
    "output/cl_staging/build_shorts_bud_b2_1013.py",
    "output/cl_staging/build_shorts_v2_1.py",
    "output/cl_staging/build_shorts_v2_2.py"
  ],
  "vi_du": [
    "https://x.com/gmgmgm1545/status/2103793820815245507",
    "https://x.com/ito1217yo/status/2104560073217597459"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "dang_dung_o": {
    "bud": {
      "so_bai": 57,
      "bai": [
        "b01_d",
        "b02_b",
        "b03_a",
        "b04_e",
        "b05_b"
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

Khoảng trống lớn, ít chuyển động và một điểm nhìn đơn giữ nhịp lặng; các bản BUD dùng style làm nền nghỉ.

## Khi nào dùng

Short đoạn suy ngẫm; Long đặt sau cao trào để người xem ngẫm. Không nên dùng: Danh sách bước hoặc nội dung cần tra nhanh.

## Cách dựng trong HyperFrames

Nhánh dựng cho style silence nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/build_shorts_bu_1006.py:1`.

style `silence`; caller build_shorts_bu_1006; giữ chuyển động thưa và ngắt nhịp.

## Rủi ro

Thời lượng lặng kéo dài làm rơi nhịp; tránh thêm hiệu ứng để lấp khoảng trống.
