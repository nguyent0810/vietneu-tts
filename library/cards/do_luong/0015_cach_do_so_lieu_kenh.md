---
{
  "id": "0015_cach_do_so_lieu_kenh",
  "ten": "Đo mỗi video trong cửa sổ 7 ngày PT; Short xếp hạng trong cùng tuần; chỉ tin số liệu sạch; Lead tính lại mọi con số",
  "loai": "do_luong",
  "dinh_dang": [],
  "pham_vi": [
    "chung"
  ],
  "hop_ngach": [],
  "cam_ngach": [],
  "so_muc": 1,
  "so_nguon": 1,
  "nguon": [],
  "bang_chung_dung": [],
  "vi_du": [],
  "nguon_su_that": [
    "docs/adr/0015-cach-do-so-lieu-kenh.md:1"
  ],
  "alias": [],
  "da_dung": "co_san",
  "cap_nhat": "2026-10-27",
  "so_lieu": {},
  "dang_dung_o": {},
  "mo_ta_nguon": "Trạng thái: đã chấp nhận (05/10/2026, bổ sung 24/10). Lấy số liệu bừa thì dễ ra kết luận sai: - YouTube Analytics tính ngày theo giờ Thái Bình Dương (PT) và trễ khoảng 3 ngày. Nếu đo \"3 ngày sau khi đăng\" thì thực tế dài 51–71 giờ tuỳ giờ đăng. - Bản cập nhật Shorts ngày 01/10 cộng với đợt đăng dồn làm bẩn số liệu các tuần trước 05/10. - Data API (view trọn đời) lệch với Analytics (theo cửa sổ). Ví dụ một bài: 28.459 so với 22.957. Thợ cũng từng đưa số sai: - \"khung 10h30 tụt 50%\", thực tế là 20%;",
  "de_xuat_boi": "codex-p3",
  "noi_dung": "trich_tu_dong"
}
---
## Trích nguồn (tự động)

Nguồn sự thật: `docs/adr/0015-cach-do-so-lieu-kenh.md:1`. Trạng thái: đã chấp nhận (05/10/2026, bổ sung 24/10). Lấy số liệu bừa thì dễ ra kết luận sai: - YouTube Analytics tính ngày theo giờ Thái Bình Dương (PT) và trễ khoảng 3 ngày. Nếu đo "3 ngày sau khi đăng" thì thực tế dài 51–71 giờ tuỳ giờ đăng. - Bản cập nhật Shorts ngày 01/10 cộng với đợt đăng dồn làm bẩn số liệu các tuần trước 05/10. - Data API (view trọn đời) lệch với Analytics (theo cửa sổ). Ví dụ một bài: 28.459 so với 22.957. Thợ cũng từng đưa số sai: - "khung 10h30 tụt.

## Mô tả

<!-- Codex/Lead soạn ở P2 -->

## Khi nào dùng

<!-- Codex/Lead soạn ở P2 -->

## Cách dùng

<!-- Codex/Lead soạn ở P2 -->

## Rủi ro

<!-- Codex/Lead soạn ở P2 -->
