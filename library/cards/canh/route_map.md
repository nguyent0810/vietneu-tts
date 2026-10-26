---
{
  "id": "route_map",
  "ten": "Tuyến đường trên bản đồ",
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
  "so_muc": 13,
  "so_nguon": 1,
  "nguon": [
    "prompt-motion"
  ],
  "bang_chung_dung": [
    "output/cl_staging/hyperframes_oct/plan_o05.json",
    "output/cl_staging/hyperframes_sept/plan_d29.json"
  ],
  "vi_du": [
    "https://prompt-motion.com/kantamk-61f410",
    "https://prompt-motion.com/samaote-5e2fc2"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [
    "hyperframes_short/compositions/casemap.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Đường nối các điểm lần lượt được vẽ, marker bật khi lời đến địa danh; casemap giữ tuyến trên nền bản đồ.

## Khi nào dùng

Short hành trình một chiều; Long hành trình nhiều chặng có thứ tự. Không nên dùng: Điểm đến không có thứ tự hoặc tuyến đường chỉ suy đoán.

## Cách dựng trong HyperFrames

Nhánh dựng cho route map nằm tại `hyperframes_short/compositions/casemap.html:1`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:700`.

visual type `map`; tuyến theo tọa độ cùng projection, caller để bridge bake hình học.

## Rủi ro

Tuyến cắt qua địa hình sai khiến người xem hiểu nhầm khoảng cách; tọa độ cần cùng projection.
