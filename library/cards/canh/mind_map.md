---
{
  "id": "mind_map",
  "ten": "Sơ đồ tư duy",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "tong_hop",
    "so_do"
  ],
  "cam_ngach": [],
  "so_muc": 16,
  "so_nguon": 1,
  "nguon": [
    "prompt-motion"
  ],
  "bang_chung_dung": [],
  "vi_du": [
    "https://prompt-motion.com/ultimaxbt-bbebf5",
    "https://prompt-motion.com/kantamk-61f410"
  ],
  "da_dung": "chua_co",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 1,
    "bud": 2
  },
  "cong": "vua"
}
---

## Mô tả

Một chủ đề trung tâm tỏa nhánh thành từ khóa, cho thấy các nhóm ý quanh chủ đề chứ không phải tiến trình. Mẫu [1](https://prompt-motion.com/ultimaxbt-bbebf5) minh họa nối chủ đề bài giảng với ba ý đã kiểm nguồn; mẫu [2](https://prompt-motion.com/kantamk-61f410) cho thấy mở các nhánh từ nút trung tâm.

## Khi nào dùng

BUD: Short tổng hợp ba ý trong phần giải nghĩa. Dạng Ca_hai. Không nên dùng khi nhánh gợi liên hệ không có trong nguồn.

## Cách dựng trong HyperFrames

Kỹ thuật mind_map chưa có trong engine như một visual riêng. Khai báo nhánh và tọa độ thủ công; vẽ connector SVG trước rồi hiện node theo mốc timeline. Mọi trạng thái của mind_map là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

nhánh gợi liên hệ không có trong nguồn; chữ nhỏ khó đọc dọc.
