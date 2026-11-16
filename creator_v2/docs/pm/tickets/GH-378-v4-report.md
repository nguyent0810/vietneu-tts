# Báo cáo kết quả GH-378-v4 (agy Gemini)

- **Brief:** `docs/pm/tickets/GH-378-v4-agy.md`
- **Tập tin kịch bản đầu ra:** `data/long/cl-hoang-kim-vinh/script.v4.md`
- **Đầu vào so sánh:** `data/long/cl-hoang-kim-vinh/script.v3c.md`
- **Dữ liệu đối chiếu:** `data/long/cl-hoang-kim-vinh/factcheck.md` và `docs/pm/tickets/GH-378-v3-check.md`

---

## 1. Kết quả kiểm tra bằng công cụ (Gates & Integrity)

- **Tổng âm tiết bản v4:** **5.916 âm tiết** (so với v3c: 4.567 âm tiết; tăng +1.349 âm tiết).
  - *Mục tiêu brief:* 5.600 – 6.500 âm tiết -> **ĐẠT (5.916 nằm chính giữa dải mục tiêu)**.
- **Kiểm tra cổng `motion/long/script_lines.py`:**
  - `gate(chs) == []` -> **PASS (không có lỗi chặn nào)**.
- **Kiểm tra âm thanh `motion/long/craft.py`:**
  - `audio_problems(chs) == []` -> **PASS (không câu nào vượt 35 âm tiết, không gọi 'quý vị', gọi 'bạn', có câu hỏi 8 câu đầu, có nghỉ dài `‖`)**.
- **Kiểm tra độ dài câu theo brief (≤ 32 âm tiết/câu):**
  - Số câu > 32 âm tiết: **0 câu** -> **PASS**.
- **Ngân sách rào nguồn:**
  - `SOURCE_PATTERN`: 3/333 câu (0,90%) -> **PASS (ngân sách ≤ 8%)**.
- **Số cảnh phỏng dựng {pd}:**
  - v3c có 22 cảnh {pd} -> v4 có **41 cảnh {pd}** (thêm 20 cảnh {pd} mới đúng chuẩn §14 storytelling-guide).

---

## 2. Bảng phân bổ âm tiết qua 14 chương

| Chương | Tên chương | Âm tiết v3c | Âm tiết v4 | Tăng thêm | Số câu v4 |
|---|---|---|---|---|---|
| CH00 | Cây chổi trước Đại Thế Giới | 286 | 413 | +127 | 23 |
| CH01 | Đứa trẻ Tô Châu | 392 | 525 | +133 | 29 |
| CH02 | Chiếc huy hiệu hai mặt | 406 | 534 | +128 | 29 |
| CH03 | Đế chế khói đen | 332 | 457 | +125 | 26 |
| CH04 | Đòn ghen ở nhà hát | 286 | 315 | +29 | 19 |
| CH05 | Người bị bắt giữ | 180 | 336 | +156 | 19 |
| CH06 | Cuộc giải cứu và sự đảo vai | 287 | 424 | +137 | 27 |
| CH07 | Khu vườn ẩn mình | 305 | 364 | +59 | 21 |
| CH08 | Mùa xuân đẫm máu 1927 | 298 | 375 | +77 | 24 |
| CH09 | Sự thật dưới trang sách 1930 | 386 | 428 | +42 | 22 |
| CH10 | Lâu đài của những cám dỗ | 369 | 500 | +131 | 26 |
| CH11 | Kẻ ở lại thành phố đổ nát | 355 | 428 | +73 | 23 |
| CH12 | Bản tự thú mùa xuân 1951 | 304 | 327 | +23 | 21 |
| CH13 | Cái giá của hai bờ quyền lực | 381 | 490 | +109 | 24 |
| **Tổng cộng** | **14 chương** | **4.567** | **5.916** | **+1.349** | **333 câu** |

---

## 3. Danh sách các cảnh phỏng dựng {pd} mới thêm (đúng chuẩn §14)

Tất cả các câu phỏng dựng đều bắt đầu bằng lời báo hiệu ("Hãy hình dung..." hoặc "Có lẽ..."), kết thúc bằng nhãn `{pd}`, chỉ tái dựng không gian, thời tiết, đồ vật, người vô danh; tuyệt đối không gán hành vi hay nội tâm bịa đặt cho nhân vật lịch sử:

1. `[CH00]`: "Hãy hình dung những cơn gió mùa đông thổi buốt qua sảnh lớn của Đại Thế Giới. {pd}"
2. `[CH00]`: "Hãy hình dung tiếng chổi quét chạm vào sàn gạch đá hoa từng đón bước chân của khách ăn chơi. {pd}"
3. `[CH01]`: "Hãy hình dung mùi giấy dó, mực nho và hồ dán thoang thoảng trong con ngõ nhỏ gần miếu Thành Hoàng. {pd}"
4. `[CH01]`: "Hãy hình dung những con ngõ tối tăm quanh Lão Bắc Môn, nơi chỉ người bản địa mới thuộc từng ngóc ngách. {pd}"
5. `[CH02]`: "Có lẽ đất rộng ra, trộm cướp và mâu thuẫn băng nhóm cũng nhiều theo. {pd}"
6. `[CH02]`: "Hãy hình dung tiếng chuông xe điện leng keng trên những đại lộ mới mở của tô giới Pháp. {pd}"
7. `[CH03]`: "Hãy hình dung làn khói ngai ngái đặc quánh bốc lên từ những chiếc tẩu thuốc phiện trong góc tối. {pd}"
8. `[CH03]`: "Có lẽ những đồng bạc hoa xòe đếm lách cách trên bàn gỗ là thứ gắn kết những kẻ trong bóng tối lại với nhau. {pd}"
9. `[CH04]`: "Hãy hình dung ánh đèn rực rỡ và tiếng đàn sáo bỗng chốc im bặt giữa khán phòng rạp hát. {pd}"
10. `[CH05]`: "Hãy hình dung những cơn gió bấc thổi qua song sắt lạnh buốt nơi doanh trại quân đội. {pd}"
11. `[CH05]`: "Hãy hình dung chiếc bàn làm việc của viên đốc sát trưởng ở bốt Mạch Lan bỗng chốc trống trơn. {pd}"
12. `[CH06]`: "Hãy hình dung những chuyến tàu xuôi ngược nối liền Thượng Hải và Hàng Châu trong sương sớm. {pd}"
13. `[CH06]`: "Hãy hình dung những chiếc rương tiền bạc được chuyển giao bí mật trong đêm tối. {pd}"
14. `[CH07]`: "Hãy hình dung tiếng ê a học bài của những đứa trẻ nghèo vang lên bên ngoài bức tường hoa viên. {pd}"
15. `[CH07]`: "Có lẽ việc mở trường làm từ thiện vừa để tích đức, vừa làm tấm bình phong che mắt người đời. {pd}"
16. `[CH08]`: "Hãy hình dung tiếng súng nổ rát và tiếng chân chạy dồn dập trong các ngõ hẹp Áp Bắc. {pd}"
17. `[CH09]`: "Hãy hình dung người đọc thời ấy giở từng trang sách và nhận ra sự mâu thuẫn đến rợn người. {pd}"
18. `[CH10]`: "Hãy hình dung ánh đèn neon rực rỡ từ ngọn tháp cao soi rọi xuống dòng người nườm nượp qua lại giữa ngã tư. {pd}"
19. `[CH10]`: "Hãy hình dung tiếng cười nói huyên náo lẫn tiếng nhạc xập xình vang lên suốt ngày đêm. {pd}"
20. `[CH12]`: "Hãy hình dung những tờ báo in chữ chì được chuyền tay nhau trên các góc phố Thượng Hải buổi sáng hôm ấy. {pd}"

---

## 4. Chi tiết Factcheck mới đưa vào sử dụng (kèm dòng đối chiếu)

1. **CH01**: Cha Hoàng Bính Tuyền từng mở quán trà nhỏ tại Thượng Hải (`factcheck.md` §4, dòng 56 - nguồn W1).
2. **CH01**: Công việc đóng khung tranh, giấy quạt và thư họa tại Tụy Hoa Đường (`factcheck.md` §4, dòng 58-59, nguồn S1).
3. **CH01**: Bối cảnh Tô giới Pháp ban đầu 66 ha, năm 1862 Pháp rút khỏi Hội đồng chung tự lập cảnh sát riêng (`factcheck.md` §17, dòng 216, 219 - nguồn W11, W12).
4. **CH01**: Hoàng từng cãi nhau với sĩ quan Pháp, bỏ về Tô Châu một thời gian rồi được gọi quay lại (`factcheck.md` §4, dòng 64 - nguồn W1).
5. **CH02**: Năm 1914 Viên Thế Khải đồng ý mở rộng tô giới đổi lấy việc Pháp trục xuất người làm cách mạng (`factcheck.md` §17, dòng 217-218 - nguồn W11).
6. **CH02**: Chi tiết vụ cướp Thái Hồ: toán cướp hung hãn lộng hành trên vùng hồ, khó bắt (`factcheck.md` §16, dòng 192 - nguồn S1).
7. **CH02**: Giai thoại giang hồ Hoàng Kim Vinh tự dựng các vụ cướp rồi tự mình ra tay bắt giữ lập công (`factcheck.md` §5, dòng 74 - nguồn S3).
8. **CH03**: Cuối thế kỷ 19 lượng thuốc phiện sản xuất trong nước đã vượt nhập khẩu (`factcheck.md` §17, dòng 221 - nguồn W13).
9. **CH03**: Dù thao túng buôn thuốc phiện, thời điểm này Hoàng Kim Vinh vẫn chưa chính thức vào Thanh bang, đứng ngoài bảo trợ bằng ghế cảnh sát (`factcheck.md` §7, dòng 97 - nguồn W3).
10. **CH04**: Lộ Lan Xuân là ca sĩ sân khấu đang rất được ái mộ bấy giờ (`factcheck.md` §8, dòng 103 - nguồn W3).
11. **CH05**: Trích dẫn sách 1930 chép việc Hoàng xin thôi chức đốc sát vào mùa đông năm Giáp Tý (1924) vì đau chân và nhà cầm quyền Pháp giữ lại (`factcheck.md` §16, dòng 195-196 - nguồn S1).
12. **CH06**: Trích dẫn sách 1930 chép về Trương Khiếu Lâm (Trương Dần, Từ Khê Chiết Giang) và câu gặp Hoàng, Đỗ "mến nhau, gặp nhau đã tiếc là muộn" (`factcheck.md` §16, dòng 202-203 - nguồn S1).
13. **CH06**: Trích dẫn sách 1930 ca ngợi Đỗ Nguyệt Sanh "hào phóng, trọng nghĩa, giúp người lúc cấp" (`factcheck.md` §16, dòng 199 - nguồn S1).
14. **CH07**: Sách 1930 chép mua đất Tào Hà Kính dựng từ đường để ghi nhớ công ơn tổ tiên (`factcheck.md` §6, dòng 84 - nguồn S1).
15. **CH08**: Ngày 6/4/1927 lập ủy ban loại trừ cộng sản phối hợp chặt chẽ cùng Thanh bang (`factcheck.md` §17, dòng 224 - nguồn W14).
16. **CH08**: Ngày 13/4/1927 công nhân bãi công phản đối có thêm khoảng 100 người ngã xuống (`factcheck.md` §17, dòng 225 - nguồn W8).
17. **CH09**: Các chức danh danh giá của Đỗ Nguyệt Sanh trong sách 1930: Chủ tịch Tổng hội thương giới, Hoa đổng Công bộ cục (`factcheck.md` §16, dòng 201 - nguồn S1).
18. **CH10**: Đại Thế Giới mở cửa ngày 14/7/1917 ở góc đại lộ Edward VII và Tây Tạng; mười hai tấm gương méo từ Hà Lan (`factcheck.md` §11, dòng 143; §17 dòng 227 - nguồn W7).
19. **CH10**: Vụ bom 14/8/1937: có từ 700 đến 950 người chết ngay tại chỗ, khoảng 2.000 chết hoặc bị thương theo Đại Thế Giới (`factcheck.md` §17, dòng 230 - nguồn W15, W7).
20. **CH11**: Tháng 12/1941 Nhật chiếm Tô giới Quốc tế; ngày 30/7/1943 chính quyền Vichy bàn giao Tô giới Pháp cho chính quyền Uông Tinh Vệ; chính quyền hợp tác lấy phần lớn ngân quỹ từ thuốc phiện (`factcheck.md` §17, dòng 233-235 - nguồn W11, W12, W13).
21. **CH11**: Chiến dịch Thượng Hải kéo dài từ 12/5 đến 2/6/1949 (`factcheck.md` §17, dòng 236 - nguồn W16); tàu Bảo Thụ Vân (`factcheck.md` §12, dòng 160 - nguồn W4).
22. **CH13**: Thi thể Đỗ Nguyệt Sanh đưa sang Đài Loan an táng tại Tích Chỉ (`factcheck.md` §17, dòng 242 - nguồn W3).
23. **CH13**: Phim ảnh: TVB phát sóng Bến Thượng Hải năm 1980 (Hứa Văn Cường, Đinh Lực) không có tên Hoàng Kim Vinh; các phim Kiêu Hùng (2015) và 1921 (2021) mới tái hiện hình ảnh của ông (`factcheck.md` §3, dòng 43-47 - nguồn W1, W10).

---

## 5. Xác nhận tuân thủ quy tắc làm việc

- **Không upload, không xuất bản, không đổi lịch, không can thiệp YouTube.**
- **Không đụng git:** Không commit, push, stash, checkout hay đổi nhánh.
- **Không ghi `state.sqlite`.**
- **Không sửa file nào khác ngoài phạm vi ticket.**
- **Ghi file hoàn toàn bằng Python `open(..., 'w', encoding='utf-8')`.**
