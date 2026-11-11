# CL — chẩn đoán sụt view và sub (10/11/2026)

Nguồn: `scripts/analytics_pull_183.py --channel CL --end 2026-11-09` (YouTube Analytics, chỉ đọc).

## Số liệu
| | 28 ngày (13/10–09/11) | 7 ngày (03–09/11) |
|---|---|---|
| Views | 92.638 | 12.635 (≈ 46% nhịp 28 ngày) |
| Sub mới | 111 (≈ 28/tuần) | 11 |
| Short views/ngày | 5.500 (07–09/10) → ~3.000 (cuối 10) | 1.200–3.700 |
| Long views | 8.282 (6.721 từ thông báo người đăng ký) | 286 |

Short theo tuần đăng (trung vị views trọn đời / tổng sub):
| Tuần | Số Short | Trung vị | Cao nhất | Sub |
|---|---|---|---|---|
| 21/09 | 26 | 1.041 | 1.368 | 18 |
| 05/10 | 39 | 925 | 1.452 | 29 |
| 12/10 | 20 | 1.003 | 1.381 | 24 |
| 19/10 | 21 | 973 | 1.306 | 16 |
| 26/10 | 21 | 986 | 1.173 | 26 |
| 02/11 | 21 | 754 | 1.149 | 8 |

Nguồn traffic Short: 94% Shorts feed, gần như 0 từ trang kênh/tìm kiếm. Long: 81% từ thông báo người đăng ký, gợi ý/duyệt gần 0.

## Chẩn đoán
1. **Short chạm trần ~1.000 views.** Từ 21/09, khoảng 150 Short không bài nào vượt 1.452 views. Feed cho mỗi bài một lượt thử khoảng 1.000 người, rồi không mở rộng thêm. AVP vẫn 67–70%, tức người đã xem thì xem hết, nên vấn đề nằm ở tỉ lệ vuốt qua trong 1–2 giây đầu và độ tương tác thấp, khiến YouTube không đẩy tiếp. 3 bài/ngày dùng cùng một khuôn cũng làm điểm "mới lạ" giảm dần.
2. **Short không biến người xem thành sub.** Đa số là vụ án Âu–Mỹ rời rạc, không thành series, không có lý do để bấm đăng ký. Tuần 02/11, 21 bài chỉ mang về 8 sub.
3. **Long sống nhờ thông báo.** Gợi ý/duyệt gần 0, tức CTR thumbnail và tiêu đề quá thấp để YouTube đẩy ra ngoài tập người đăng ký. Đề tài ít người biết (Lưu Vĩnh Phúc 51 views) càng yếu. Bao Thanh Thiên (IP quen) tốt nhất: 265 views sau 2 ngày.

## Đề xuất (chờ chủ kênh duyệt)
- **Short:** giảm còn 2 bài/ngày, chỉ làm series có danh tính: (a) Short L nối Long Trung Hoa / Đông Nam Á, đánh số "Hồ sơ #"; (b) vụ án châu Á. Dừng vụ án Âu–Mỹ rời rạc sau khi hết hàng chờ.
- **3 giây đầu Short:** khung đầu là chân dung/hiện vật + con số lớn, câu 1 ≤ 9 từ (đã có cổng #253), thêm âm nhấn t=0 (đang port từ v1). Thử A/B 6 ngày, đo trung vị views và tỉ lệ sub/1.000 views.
- **Long:** làm lại thumbnail có ảnh chủ thể (mặt người/hiện vật), ≤ 4 từ, đúng chuẩn v1; tiêu đề giữ khuôn "[IP] Ngoài Đời Thật" với IP quen thuộc.
- **Đo:** 72 giờ sau mỗi lô; dừng hướng nào không vượt trung vị 1.000 hoặc không đạt ≥ 1 sub/1.000 views.
