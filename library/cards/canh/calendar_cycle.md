---
{
  "id": "calendar_cycle",
  "ten": "Chu kỳ / vòng lịch",
  "loai": "canh",
  "dinh_dang": [
    "ca_hai"
  ],
  "pham_vi": [
    "fs"
  ],
  "hop_ngach": [
    "lich",
    "van_hoa"
  ],
  "cam_ngach": [
    "bud"
  ],
  "so_muc": 17,
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
  "cap_nhat": "2026-10-27",
  "dang_dung_o": {},
  "nguon_su_that": [],
  "alias": [],
  "de_xuat_boi": "codex-p2",
  "ap_dung": "thu_nghiem_hoac_dang_thua",
  "do_hop": {
    "fs": 3,
    "bud": 0
  },
  "cong": "vua"
}
---

## Mô tả

Lưới ngày/tháng được nối thành chu kỳ, mốc đang nói được tô để liên hệ lịch với mùa hoặc sự kiện. Mẫu [1](https://prompt-motion.com/ultimaxbt-bbebf5) minh họa tô mốc tiết khí trên vòng năm; mẫu [2](https://prompt-motion.com/kantamk-61f410) cho thấy đặt các tháng quanh chu kỳ lặp.

## Khi nào dùng

FS: Short giải thích tiết khí hoặc ngày âm lịch. Dạng Ca_hai. Không nên dùng khi lẫn lịch âm/dương khiến thông tin sai.

## Cách dựng trong HyperFrames

Kỹ thuật calendar_cycle chưa có trong engine như một visual riêng. Tạo ô lịch SVG từ bảng ngày đã khóa; sector/mốc đang nói lấy theo khoảng thời gian tuyệt đối. Mọi trạng thái của calendar_cycle là hàm của t nên seek tới frame bất kỳ vẫn cho cùng kết quả. Công vua.

## Rủi ro

lẫn lịch âm/dương khiến thông tin sai.
