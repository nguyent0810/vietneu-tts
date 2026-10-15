# Kể chuyện trung thành nguồn (Tiền Thân, sử, nhân vật minh hoạ)

Luật kênh: lời Phật chỉ khi có kinh; chi tiết không từ nguồn phải gắn nhãn. Kể hay KHÔNG có nghĩa là thêm tình tiết.

## 1. Nguồn và nhãn
| Lớp | Ví dụ | Kiểm bằng | Câu dẫn trong lời đọc |
|---|---|---|---|
| Kinh (Nikāya, Pháp Cú, KỆ Tiền Thân) | lời Phật, kệ | `python hf_sutta.py <uid> "<cụm>"`; kệ Tiền Thân `hf_sutta.py ja<N>` (bản Sujato, chỉ có kệ) | "Trong kinh Tương Ưng, Đức Phật dạy..." (số kinh trên màn hình) |
| Chú giải (truyện văn xuôi Tiền Thân, Pháp Cú chú giải) | cốt truyện quá khứ, chuyện hiện tại, nhận diện | bản Anh Cowell (1895-1907, phạm vi công cộng); bản Việt chỉ đọc để đối chiếu, **không chép** | "Theo truyện kể trong Chuyện Tiền Thân...", "sách chú giải kể..." |
| Truyền thống / truyền thuyết | voi trắng sáu ngà, xá lợi bay | Wikipedia + nguồn sách | "Truyền thống kể rằng...", "tương truyền..." |
| Sử | năm, trận, chiếu chỉ | Toàn thư, Thánh đăng ngữ lục... (ghi tên sách) | "Sử chép...", "Theo Đại Việt sử ký toàn thư..." |
| Nhân vật minh hoạ của kênh | mẹ con chị Thảo, người tuổi Hợi 1983 | -- | ghi trong `seo.summary`: "là nhân vật minh hoạ" |

Phần văn xuôi Tiền Thân là chú giải (soạn khoảng thế kỷ 5), chỉ KỆ thuộc Tiểu Bộ: không gọi lời thoại trong truyện là
"lời Phật dạy trong kinh". Ghi "Dựa trên Chuyện Tiền Thân số N (tên Pali đã Việt hoá)" trong mô tả như đối thủ làm.

## 2. Được thêm / không được thêm
**Được**: bối cảnh giác quan trung tính (gió sa mạc, tiếng xe, đêm tối) khớp nơi chốn; nhịp, câu ngắn, lặng; câu hỏi gửi
người xem; câu nối với đời nay; diễn ý lời thoại có trong nguồn; nhân vật minh hoạ hiện đại ở khung ngoài (ghi rõ).
**Không**: tình tiết, nhân vật, tên, con số, lời thoại mới trong chuyện; động cơ / suy nghĩ của nhân vật mà nguồn không nói
(nếu cần: "có lẽ", "ta có thể hình dung" -- tối đa một lần mỗi truyện); kết cục khác; lời Đức Phật không có nguồn;
"phép màu" khẳng định như sự thật.

## 3. Mẫu một truyện (6-9 phút, ~1.100-1.700 tiếng)
1. **Móc ở khủng hoảng** (3-5 câu): một cảnh cụ thể ngay trước lựa chọn; câu hỏi chưa trả. Không nêu bài học.
2. **Chuyện hiện tại** (3-6 câu): ai, ở đâu, vì sao Đức Phật kể -- nối với một câu hỏi đời thường ("Bạn đã bao giờ...").
3. **Bối cảnh quá khứ** (4-8 câu): "Thuở xưa, khi vua Phạm Dự trị vì ở Ba La Nại..." -- 1 chi tiết giác quan / cảnh.
4. **Leo thang** (8-15 câu): hai lựa chọn, hai nhân vật đối chiếu (người khôn / kẻ vội); thoại mỗi lượt một dòng (line-rules §6).
5. **Đỉnh + lặng**: câu ngắn ≤ 6 tiếng, `pause` 1,0-1,4, `tempo` 0,85-0,88; có thể `SILENCE`.
6. **Kệ** (≤ 2 câu diễn ý, `alt=True`, đã đối chiếu `ja<N>`).
7. **Nhận diện** (1-2 câu): "Người lái buôn khôn ngoan ấy, chính là Bồ Tát" -- cú lật, không nói trước.
8. **Bài học hôm nay** (1-2 câu, cụ thể, có một việc làm được) + **câu cầu nối** mở truyện sau. Không "Tóm lại".

## 4. Soát truyện trước khi giao
- Đặt bản tóm tắt cốt truyện từ nguồn (5-10 gạch) cạnh beat sheet; mỗi beat chỉ dùng gạch có trong tóm tắt.
- Tìm trong kịch bản các câu có "nói", "dạy", "thưa", "nghĩ" -> mỗi câu phải có ở nguồn hoặc mang nhãn.
- Số (năm trăm cỗ xe, sáu mươi do tuần...) đúng nguồn; đổi đơn vị cổ ra cách hiểu nay thì nói "khoảng".
- Ví dụ thật đã bắt được: b45_b viết "tự bắn mũi tên thứ hai" trong khi SN 36.6 là "bị trúng mũi tên thứ hai" (long-video §3).
