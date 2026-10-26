---
{
  "id": "style_night",
  "ten": "Phong cách night",
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
  "so_muc": 99,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "yihui-dev"
  ],
  "bang_chung_dung": [
    "output/cl_staging/build_jataka_b1.py",
    "output/cl_staging/build_shorts_bu_1006.py",
    "output/cl_staging/build_shorts_bud_b2_1013.py",
    "output/cl_staging/build_shorts_fs_test_1013.py",
    "output/cl_staging/build_shorts_v2_1.py"
  ],
  "vi_du": [
    "https://x.com/majidmanzarpour/status/2102476258948927543",
    "https://x.com/Viggle_PINOC/status/2102861939072434495"
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

Nền đêm xanh tím với vùng sáng chọn lọc, chủ thể còn đọc được tách khỏi bóng tối.

## Khi nào dùng

Short chuyển cảnh đêm; Long đoạn kể cần không khí tĩnh. Không nên dùng: Bảng tra cứu có nhiều ô tối màu.

## Cách dựng trong HyperFrames

Nhánh dựng cho style night nằm tại `hyperframes_bridge.py:684`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/build_jataka_b1.py:1`.

style `night`; caller build_jataka_b1; điều tiết vùng tối quanh caption.

## Rủi ro

Chữ vàng chìm ở vùng highlight; nén video làm bóng đen bệt.
