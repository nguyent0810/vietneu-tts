---
{
  "id": "calendar_grid",
  "ten": "Lịch dạng lưới",
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
  "so_muc": 17,
  "so_nguon": 1,
  "nguon": [
    "prompt-motion"
  ],
  "bang_chung_dung": [
    "output/cl_staging/long/build_F11.py",
    "output/cl_staging/long/build_F14.py",
    "output/cl_staging/long/build_F17.py",
    "output/cl_staging/long/build_F20.py",
    "output/cl_staging/long/build_F26.py"
  ],
  "vi_du": [
    "https://prompt-motion.com/ultimaxbt-bbebf5",
    "https://prompt-motion.com/kantamk-61f410"
  ],
  "da_dung": "dung_that",
  "cap_nhat": "2026-10-26",
  "nguon_su_that": [
    "hyperframes_short/compositions/dongho_long.html"
  ],
  "alias": [],
  "de_xuat_boi": "codex-p2"
}
---

## Mô tả

Ngày được đặt vào ô tuần, cuối tuần phân màu; bản đồng hồ dài ghép lưới lịch với dải giờ.

## Khi nào dùng

Short tra ngày/tháng; Long kể chu kỳ có mốc ngày rõ. Không nên dùng: Ngày âm/dương chưa đối chiếu lịch nguồn.

## Cách dựng trong HyperFrames

Nhánh dựng cho calendar grid nằm tại `hyperframes_short/compositions/dongho_long.html:1`; caller hoặc phần cấu hình tương ứng ở `output/cl_staging/long/build_F11.py:1`.

composition `dongho_long.html`; cấp năm/tháng/ngày bắt đầu tuần theo lịch đã kiểm.

## Rủi ro

Ngày đầu tuần sai sẽ dịch toàn bộ cột; ô nhỏ khiến số ngày dài tràn.
