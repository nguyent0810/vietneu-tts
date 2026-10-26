---
{
  "id": "camera_pan",
  "ten": "Pan camera",
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
  "so_muc": 50,
  "so_nguon": 4,
  "nguon": [
    "LeaddeOpenLab",
    "athemeroy",
    "prompt-motion",
    "yihui-dev"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://x.com/lukasersil/status/2103742861971726495",
    "https://x.com/froessell/status/2103789415323562325"
  ],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_short/compositions/longform.js"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Khung dịch ngang/dọc qua ảnh lớn, đưa vùng đang nói vào trung tâm; trong longform.js vị trí bám điểm ảnh chuẩn hóa.

## Khi nào dùng

Long đọc ảnh tư liệu hoặc bản đồ có điểm nhìn nối tiếp; Short dùng một cú lia rất ngắn. Không nên dùng: Ảnh đã vừa khung và không có chi tiết cần khám phá.

## Cách dựng trong HyperFrames

Nhánh dựng cho camera pan nằm tại `hyperframes_short/compositions/longform.js:1441`; caller hoặc phần cấu hình tương ứng ở `hyperframes_bridge.py:703`.

visual type `doc`; `moves[{x,y,z,at,word,d}]`, x/y chuẩn hóa 0–1, z từ 1 trở lên.

## Rủi ro

Tọa độ ngoài 0–1 hoặc ảnh sai kích thước làm chủ thể trôi khỏi khung.
