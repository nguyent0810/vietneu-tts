---
name: shorts-lookup
description: Playbook đóng gói tri thức Short dạng tra cứu cá nhân hóa (câu hỏi tìm kiếm + chìa khoá năm sinh/tuổi/ngày + bảng dừng hình tự dò). Dùng để nhân rộng các khuôn thắng (Tam Tai, Tuổi hợp, Thái Tuế, Ngày tốt theo việc, Hoàng đạo daily, Lịch vía Phật giáo) sang các kênh và làn nội dung mới.
---

# Shorts Lookup Playbook (Bảng Tra Cứu Tự Dò)

Playbook tổng hợp cơ chế sản xuất Short dọc 9:16 có tỷ lệ giữ chân (AVP) vượt trội (>100% – 200%), biến luồng Shorts feed thành phễu chuyển đổi và xem lại nhiều lần thông qua bảng dữ liệu dừng hình.

---

## 1. Cơ chế thắng & Bằng chứng thực nghiệm

### Công thức cốt lõi
$$\text{Short Thắng} = \text{Câu hỏi tìm kiếm} + \text{Chìa khoá cá nhân} + \text{Bảng dừng hình tự dò}$$

1. **Câu hỏi tìm kiếm**: Tiêu đề và hook giải quyết trực diện một thắc mắc có nhu cầu tìm kiếm cao (ví dụ: *Tam Tai 2027 là những tuổi nào?*, *Năm 2027 tuổi nào làm nhà được?*).
2. **Chìa khoá cá nhân**: Gắn liền với định danh của từng khán giả: năm sinh (19xx), tuổi mụ, con giáp (chi), mệnh, ngày âm/dương.
3. **Bảng dừng hình tự dò (Frame-freeze table)**: Cung cấp bảng dữ liệu toàn diện trong 8–15 giây cuối hoặc cố định toàn màn hình. Khán giả buộc phải **bấm tạm dừng (pause)** hoặc để video **chạy lặp lại (loop)** nhằm dò tìm thông tin của bản thân và người thân.

### Bằng chứng số liệu (Đo ngày 19–20/10/2026)
*(Trích xuất từ YouTube Analytics & Data API tại `output/cl_staging/grok/samples/19a_short_data.md`)*:

| Video ID | Tiêu đề | Views (19/10) | % Xem TB (AVP) | Nguồn Shorts Feed | Điểm đặc biệt |
|:---|:---|:---:|:---:|:---:|:---|
| `Mw-mhvayRU4` | Tam Tai năm 2027 là những tuổi nào? | **51.340** | **132,2%** | **98,2%** | Bảng danh sách 15 năm sinh tự dò |
| `bDxeOQF9p6U` | Năm 2027: 3 tuổi được xem là hợp nhất | **36.007** | **206,1%** | **98,6%** | Video 10s, khán giả xem lặp hơn 2 vòng |
| `LQt91YMCeYQ` | Năm 2027: 4 tuổi phạm Thái Tuế | **4.035** (sau 7,6h) | Tốc độ **531 view/h** | **98,0%** | Bảng 4 nhóm hạn Thái Tuế |

- **95% – 99% lưu lượng đến từ Shorts Feed**: Video bảng tra cứu không chỉ ăn tìm kiếm mà được thuật toán đẩy mạnh trên Shorts Feed nhờ AVP vượt ngưỡng 100%.

---

## 2. Bốn trục mở rộng (4D Scaling Matrix)

Khi nhân rộng sang chủ đề mới hoặc kênh mới, xây dựng kịch bản dựa trên ma trận 4 trục:

```
[Chìa khoá] × [Câu hỏi] × [Mốc thời gian] × [Khuôn hiển thị]
```

1. **Chìa khoá cá nhân**:
   - Năm sinh (197x, 198x, 199x, 200x)
   - Con giáp / Tên Chi (Tý, Sửu, Dần... Hợi)
   - Tuổi mụ (tính theo năm âm lịch)
   - Bản mệnh / Cung phi / Trực ngày
2. **Câu hỏi truy vấn**:
   - Vận hạn: Tam Tai, Kim Lâu, Hoang Ốc, Thái Tuế, Sao hạn Cửu Diệu.
   - Việc sự: Làm nhà (động thổ), Cưới hỏi, Khai trương, Xuất hành, Nhập trạch.
   - Tương hợp: Tuổi hợp làm ăn, Tuổi xông đất, Cặp tam hợp / lục hợp.
3. **Mốc thời gian**:
   - Năm tới (ví dụ: đón đầu 2027 Đinh Mùi).
   - Tháng tới (ngày tốt trong tháng âm/dương tiếp theo).
   - Hằng ngày (Lịch hoàng đạo daily cho ngày mai).
4. **Khuôn hiển thị (Template)**:
   - Bảng tra cứu danh sách (Lookup Table).
   - Tờ lịch tháng khoanh ngày (`month_sheet`).
   - Thiệp cưới trang trọng (`thiep_cuoi`).
   - Bảng ngày lễ / ngày vía tôn nghiêm (`review_budtable`).
   - Lưới 12 con giáp / Hoàng đạo daily (`hoangdao_daily`).

---

## 3. "Gia đình bảng" (Board Family) & Nguyên tắc 60/40

### Cấu trúc nhận diện cố định (Family Identity)
Mọi biến thể đều phải tuân thủ layout 3 tầng chuẩn 1080x1920:
- **Tầng trên (Header)**: Chip danh mục nổi bật + Tiêu đề 2 dòng đậm nét, giải thích rõ đối tượng tra cứu.
- **Tầng giữa (Body)**: Khối bảng trung tâm, cỡ chữ số/ngày lớn (chữ số chính $\ge 90\text{px}$, dòng giải nghĩa $\ge 36\text{px}$). Ô/hàng tự co giãn, không để tràn màn hình hoặc đè vào lề an toàn ($x > 940\text{px}$ nút Shorts, $y > 1490\text{px}$ dải phụ đề).
- **Tầng dưới (Footer)**: Nút kêu gọi *"DỪNG HÌNH ĐỂ TRA CỨU / LƯU LẠI"* + dòng ghi chú miễn trừ trách nhiệm theo quy định của kênh.

### 5 Biến thể theo hình dạng dữ liệu
1. **Bảng danh sách cột/hàng (Review List)**: Dùng cho Tam Tai, Tuổi hợp, Thái Tuế, Kim Lâu. Hiển thị rõ: Năm sinh – Can Chi – Cung hạn.
2. **Tờ lịch tháng (`month_sheet`)**: Lưới lịch 7 cột (Thứ Hai – Chủ Nhật), khoanh vòng tròn đỏ ngày tốt; dải băng chân trang ghi trực và tuổi xung. Phù hợp cho việc làm nhà, khai trương.
3. **Thiệp cưới trang trọng (`thiep_cuoi`)**: Nền đỏ song hỷ (囍), khung viền vàng kim, phân tách rõ ngày dương và ngày âm, chú thích giờ lành. Dành riêng cho làn cưới hỏi.
4. **Bảng nghi lễ / Ngày vía (`review_budtable`)**: Họa tiết Bánh xe Pháp luân (Dharmachakra), tông màu nâu vàng ấm cúng, liệt kê ngày âm – tên ngày vía – ngày dương. Dành cho kênh Phật giáo.
5. **Lưới 12 con giáp (`hoangdao_daily`)**: Lưới trực quan hiển thị giờ hoàng đạo liền kề (vd: 7–11h), hướng xuất hành cát lợi và 2 con giáp xung khắc trong ngày.

### Tỷ lệ 60/40 & Thử nghiệm
- **60% sản lượng**: Duy trì các khuôn thắng đã chứng minh hiệu quả cao (bảng danh sách tuổi, tờ lịch tháng).
- **40% sản lượng**: Thử nghiệm các biến thể hoặc góc tiếp cận mới.
- **Nhịp thử nghiệm**: Tối đa thử **1 biến thể mới mỗi tuần**.

---

## 4. Luật chống trùng nội dung (Anti-Duplication)

> [!CAUTION]
> **Bài học vụ Thái Tuế (20/10/2026)**: Video `fs27_05_a` (`U8UOEAc1RWc`, *Năm 2027: 4 tuổi phạm Thái Tuế*) trùng gần như hoàn toàn với short cũ `LQt91YMCeYQ` đã đăng trước đó 1 ngày. Hậu quả: Phải khẩn cấp chuyển video sang chế độ riêng tư và render video thay thế `KvK9jo8ibrw` (Tam Tai 2027) để bù lịch.

### Quy tắc bắt buộc:
1. **Kiểm tra Sổ cái tổ hợp (Combination Ledger)**: Trước khi lên kịch bản, đối chiếu ma trận `[Chủ đề] × [Chìa khoá] × [Mốc] × [Khuôn]`. Không phê duyệt nếu tổ hợp này đã được thực hiện trong vòng 60 ngày.
2. **Quét tiêu đề toàn kênh**: Chạy kiểm tra chuỗi tiêu đề đối chiếu với danh sách video đã đăng và video đang hẹn giờ trên kênh. Trùng từ khoá chính $\ge 80\%$ phải đổi góc khai thác hoặc chuyển đổi khuôn hiển thị.

---

## 5. Nhịp đăng, Thời điểm đón đầu & Quy tắc dừng

### Nhịp đăng
- **$\le 2$ video/ngày** trên cùng một làn nội dung (tránh tự phân tán và ăn thịt lưu lượng của nhau).
- Hai video sử dụng **cùng một khuôn hiển thị** phải đăng cách nhau **$\ge 3$ ngày**.

### Thời điểm đăng đón đầu theo việc
Hành vi tìm kiếm của khán giả diễn ra trước thời điểm sự kiện:
- **Cưới hỏi**: Đăng trước **3 – 5 tháng** (người dùng chốt ngày cưới, in thiệp và đặt tiệc từ sớm).
- **Làm nhà (động thổ)**: Đăng trước **1 – 3 tháng** (chuẩn bị bản vẽ, tài chính, lễ vật).
- **Khai trương**: Đăng trước **2 – 4 tuần**.
- **Hoàng đạo hằng ngày**: Đăng trước **1 ngày** (khung giờ vàng 18h00 – 19h30 tối hôm trước để khán giả xem cho ngày hôm sau).

### Quy tắc dừng (Kill-switch)
- Nếu một chủ đề hoặc một khuôn hiển thị mới có **3 video liên tiếp** đạt AVP $< 80\%$ hoặc lượt xem 48h tụt dưới mức nền ($\sim 1.000 - 1.300$ views): **Dừng ngay nhánh đó**, không tiếp tục sản xuất biến thể cho chủ đề đó.

---

## 6. Phễu chuyển đổi Short $\rightarrow$ Long

Short tra cứu đóng vai trò là "mồi câu" và "mục lục tóm tắt":
1. **Link mô tả & Bình luận ghim**: Luôn đặt link dẫn thẳng đến video Long tương ứng (phân tích trọn đời 60 năm, chi tiết sao hạn từng tháng).
2. **Video liên quan (`related_videos.csv`)**: Gắn thủ công trường Related Video trong YouTube Studio cho từng Short trỏ về tập Long chính.
3. **Short "mục lục series"**: Cung cấp bức tranh tổng thể ngắn gọn trong 30s, mời khán giả xem video dài $\ge 20-30$ phút để nắm trọn phương pháp hóa giải hoặc hướng dẫn chi tiết.

---

## 7. Quy chuẩn nội dung cho Phong Thủy (FS) & Phật Giáo (BUD)

### Làn Phong Thủy (FS)
- **Tên Chi**: Gọi con giáp bằng tên chi chuẩn (*Tý, Sửu, Dần... Hợi*). Tuyệt đối **không** gọi "tuổi Mèo / Lợn / Dê".
- **Mật độ tên chi**: Tối đa **3 tên chi** trong một câu để lời đọc mạch lạc, không gây rối tai.
- **Tính toán thuần bằng code**: 100% số liệu (can chi, tiết khí, trực, thần, sao hạn, Hoang Ốc, Kim Lâu, Tam Tai) lấy từ package `fs_calendar` (`tuvi_year`, `canchi`, `amlich`, `ngaytot`). Tuyệt đối không dùng thư viện ngoài thiếu chuẩn xác và không gõ tay số liệu.
- **Nguyên tắc đạo đức**: Luôn đặt trong khung *"theo truyền thống / tham khảo"*; **không dọa nạt**, không phán tai họa chết chóc, **không hứa hẹn tài lộc tiền bạc**.

### Làn Phật Giáo (BUD)
- **Mượn cơ chế, không mượn chủ đề**: Chỉ mượn cơ chế *bảng dừng hình tra cứu* cho lịch ngày vía chư Phật/Bồ Tát, lịch ăn chay âm lịch (`amlich`), giải nghĩa biểu tượng pháp khí có nguồn tài liệu xác thực, lời Phật dạy trong Kinh Pháp Cú. Tuyệt đối **không đưa bói toán, sao hạn, tử vi vào kênh Phật giáo**.
- **Kiểm chứng kinh điển**: Lời Phật chỉ được trích dẫn khi đã kiểm tra qua công cụ `.venv/bin/python hf_sutta.py` (Kinh tạng Pali) hoặc có văn bản nguồn rõ ràng (Bắc tông). Không gán cho kinh những điều kinh không nói (ví dụ: ngày ăn chay của tháng thiếu).
- **Ý nghĩa biểu tượng**: Các giải thích đời sau về màu sắc, pháp khí phải gắn nhãn *"theo cách giải thích phổ biến"*.
- **Mỹ thuật tôn nghiêm**: Tuyệt đối **không vẽ mặt Đức Phật**, **không dùng ảnh AI**, **không dùng hình ảnh người phương Tây**, không lẫn lộn với các tôn giáo khác.

---

## 8. Quy trình điều phối Thợ – Lead

Mọi tác vụ sản xuất tự động được tổ chức theo cơ chế phân quyền nghiêm ngặt:
- **Hàng đợi công việc**: Theo dõi qua `output/cl_staging/grok/` (`queue/`, `reports/`, `rules.md`).
- **Luật làm việc của Thợ (Worker Rules)**: Xem chi tiết 12 điều luật bắt buộc tại [worker_rules.md](file://references/worker_rules.md).
- **Đánh giá sau đợt (Retro)**: Xem bài học kinh nghiệm và các sự cố thực tế tại [retro_2026-10-19.md](file://references/retro_2026-10-19.md).
- **Phân công trách nhiệm**: Thợ tập trung viết mã, dựng layout bảng và test tự động; Lead chịu trách nhiệm soát số liệu, review chất lượng hiển thị và thực hiện lệnh đăng/commit chính thức.
