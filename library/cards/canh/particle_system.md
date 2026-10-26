---
{
  "id": "particle_system",
  "ten": "Hệ hạt",
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
  "so_muc": 84,
  "so_nguon": 5,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "engine",
    "prompt-motion",
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
    "https://x.com/majidmanzarpour/status/2102476258948927543",
    "https://x.com/Michaelzsguo/status/2102592355165782312"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_short/compositions/dustbeam.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Các hạt bụi bay thành chùm trong vùng sáng; dustbeam dùng hạt làm lớp không khí, không thay vật thể chính.

## Khi nào dùng

Short mở cảnh sương/bụi; Long tạo chiều sâu cho cảnh tối. Không nên dùng: Bảng số hoặc lời cần cảm giác rõ, sạch.

## Cách dựng trong HyperFrames

Nhánh dựng cho particle system nằm tại `hyperframes_short/compositions/dustbeam.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/build_shorts_bu_1006.py:1`.

style `dustbeam`; build_shorts_bu_1006 là caller, mật độ hạt theo vùng ảnh.

## Rủi ro

Mật độ hạt dày làm nhiễu chữ; vận tốc ngẫu nhiên gây render không lặp nếu seed thay đổi.
