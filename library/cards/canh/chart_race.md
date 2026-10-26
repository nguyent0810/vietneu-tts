---
{
  "id": "chart_race",
  "ten": "Biểu đồ đua",
  "loai": "canh",
  "dinh_dang": [
    "short"
  ],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [
    "du_lieu",
    "so_sanh"
  ],
  "cam_ngach": [
    "fs",
    "bud"
  ],
  "so_muc": 13,
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
    "fs": 0,
    "bud": 0
  },
  "cong": "cao"
}
---

## Mô tả

Thanh xếp hạng đổi độ dài và thứ tự qua các mốc, cho thấy nhóm nào tăng/giảm theo thời gian. Mẫu [1](https://prompt-motion.com/ultimaxbt-bbebf5) minh họa đổi thứ hạng giữa các mốc dữ liệu; mẫu [2](https://prompt-motion.com/kantamk-61f410) cho thấy giữ nhãn gắn thanh khi thứ tự đổi.

## Khi nào dùng

Không hợp FS/BUD trừ thử nghiệm với dữ liệu công khai thật. Dạng Short. Không nên dùng khi đổi hạng liên tục phóng đại khác biệt nhỏ.

## Cách dựng trong HyperFrames

Kỹ thuật chart_race chưa có trong engine như một visual riêng. Lưu bảng giá trị từng mốc, nội suy theo khoảng t và sắp hạng có khóa phụ cố định; render thanh SVG. Mọi trạng thái của chart_race là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công cao.

## Rủi ro

đổi hạng liên tục phóng đại khác biệt nhỏ; phải hiện kỳ đo và nguồn.
