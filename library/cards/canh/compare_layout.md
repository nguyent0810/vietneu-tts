---
{
  "id": "compare_layout",
  "ten": "Bố cục so sánh",
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
  "so_muc": 1,
  "so_nguon": 1,
  "nguon": [
    "LeaddeOpenLab"
  ],
  "bang_chung_dung": [
    "output/cl_staging/grok/ab_compare.py",
    "output/cl_staging/grok/tools/build_54b_long_thumbs.py",
    "output/cl_staging/grok/tools/layout04.py",
    "output/cl_staging/long/build_B1.py",
    "output/cl_staging/long/build_B10.py"
  ],
  "vi_du": [
    "https://x.com/geek_zard/status/2110216255474897247"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_short/studio/devices/compare.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Hai đối tượng đứng thành hai vùng đối chiếu, mỗi bên có nhãn riêng; device compare.js điều khiển cặp nội dung.

## Khi nào dùng

Short so hai số liệu/quan niệm; Long chỉ khi hai phía có cùng tiêu chí. Không nên dùng: Một phía có nhiều dữ liệu hơn hẳn hoặc so sánh thiếu căn cứ.

## Cách dựng trong HyperFrames

Nhánh dựng cho compare layout nằm tại `hyperframes_short/studio/devices/compare.js:1`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:658`.

device `compare`; ghép hai vùng có cùng schema và đặt nhãn hai phía.

## Rủi ro

Tên phía dài làm lệch cân; nhãn màu không đủ phân biệt khi thu nhỏ.
