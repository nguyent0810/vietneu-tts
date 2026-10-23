---
name: shorts-lookup
description: Playbook đóng gói tri thức Short dọc 9:16 dạng tra cứu cá nhân hóa (câu hỏi tìm kiếm + chìa khoá năm sinh/tuổi/ngày + bảng dừng hình tự dò) và các dạng video thắng mới cho FS & BUD. Dùng khi lên kịch bản, dựng bảng, phối âm thanh, và tiền kiểm trước khi bàn giao.
---

# Shorts Lookup Playbook (Bảng Tra Cứu Tự Dò & Dạng Thắng Mới)

Playbook tổng hợp cơ chế sản xuất Short dọc 9:16 có tỷ lệ giữ chân (AVP) vượt trội (>100% – 200%), biến luồng Shorts feed thành phễu chuyển đổi và xem lại nhiều lần thông qua bảng dữ liệu dừng hình và kịch bản có cú lật.

---

## 1. Cơ chế thắng & Bằng chứng thực nghiệm

### Công thức cốt lõi
$$\text{Short Thắng} = \text{Câu hỏi tìm kiếm / Hook tò mò} + \text{Chìa khoá cá nhân / Chi tiết lạ} + \text{Khung dừng hình tự dò / Cú lật nhân quả}$$

1. **Câu hỏi tìm kiếm / Hook tò mò**: Tiêu đề và 1 giây đầu giải quyết trực diện nhu cầu tìm kiếm hoặc đánh trúng tâm lý tự soi (ví dụ: *Tam Tai 2027 là những tuổi nào?*, *Khi giận một người nên làm gì?*, *Bạn có đường chỉ tay này không?*).
2. **Chìa khoá cá nhân / Chi tiết lạ**: Gắn liền với định danh người xem (năm sinh, con giáp/tên chi, tuổi mụ, đường chỉ tay) hoặc một điểm nhấn thị giác trên ảnh tượng thật/pháp khí.
3. **Khung dừng hình / Cú lật**: Dữ liệu toàn diện trong 8–15 giây cuối buộc người xem **bấm tạm dừng (pause)** hoặc để video **chạy lặp lại (loop)**; với truyện là cú lật nhân quả bất ngờ.

### Bằng chứng số liệu (Đo ngày 19–21/10/2026)
*(Nguồn: YouTube Analytics & Data API tại `nghien_cuu_short_2026-10-21.md` và `samples/19a_short_data.md`)*:
- **FS Tam Tai 2027** (`Mw-mhvayRU4`): 51.340 views, AVP **132,2%**, 98,2% Shorts Feed.
- **FS 3 tuổi hợp 2027** (`bDxeOQF9p6U`, 10s): 36.007 views, AVP **206,1%** (xem lặp hơn 2 vòng).
- **FS Thái Tuế 2027** (`LQt91YMCeYQ`, bảng 10s): Đạt **531 view/h** sau 7,6 giờ đầu.
- **FS Hoàng đạo daily** khuôn mới: Đạt 33.000 view sau 31 giờ.
- **Thị trường ngách BUD**: Nhóm câu ngắn ≤15s đạt trung vị 9.893 view/ngày (dài TV 9s); nhóm truyện nhân quả đạt trung vị 32.154 view/ngày.

---

## 2. 6 Dạng thắng và Cấu trúc chuẩn

| STT | Dạng | Thời lượng | Cấu trúc chuẩn | Nguồn & Kiểm |
|:---:|:---|:---:|:---|:---|
| 1 | **Bảng tự dò** | 10–15s | Hook câu hỏi tìm kiếm $\rightarrow$ Bảng dữ liệu toàn diện (ô/hàng tự giãn) $\rightarrow$ Khung cuối đứng $\ge 3\text{s}$ + CTA dừng hình để tra cứu | `tuvi_year`, `amlich`, `canchi` |
| 2 | **Lời Phật 9 giây** | 9–12s | Ảnh tượng Phật thật chuyển động chậm (1.00 $\rightarrow$ 1.04) $\rightarrow$ Câu kinh hiện từng dòng theo giọng $\rightarrow$ Dẫn nguồn *"Pháp Cú, câu X"* $\rightarrow$ Khung cuối đứng $\ge 3\text{s}$ | `hf_sutta.py` (Kinh Pháp Cú) |
| 3 | **Nhân quả trong kinh** | 75–120s | Mở đầu bằng cảnh cao trào nhất ở câu 1 $\rightarrow$ Lùi lại kể diễn tiến $\rightarrow$ Cú lật nhân quả $\rightarrow$ 1 câu Phật dạy (kèm Pháp Cú liên quan) $\rightarrow$ Câu hỏi chiêm nghiệm | Chú giải Pháp Cú (Burlingame), Jātaka (Cowell); nhãn "theo chú giải / truyền thuyết" |
| 4 | **Biểu tượng – trả lời nhanh** | 12–18s | Ảnh tượng/vật thật làm hero $\rightarrow$ Câu hỏi chi tiết lạ $\rightarrow$ Câu trả lời 1–2 dòng + chú thích spotlight/mũi tên chỉ vào chi tiết | Nhãn *"theo cách giải thích phổ biến"* |
| 5 | **Chỉ tay / nhân tướng** | 8–12s | Hook tò mò tự kiểm (*"Bạn có đường tâm đạo này không?"*) $\rightarrow$ Sơ đồ bàn tay nét vàng + đèn quét soi vị trí $\rightarrow$ 2–3 thẻ lật giải nghĩa tham khảo | Nhãn tham khảo; không đoán thọ, không nói bệnh tật |
| 6 | **"N con giáp tháng tới"** | 10–15s | Lưới 12 con giáp (gọi bằng tên chi Tý…Hợi) $\rightarrow$ N ô sáng theo tam hợp/lục hợp với chi tháng $\rightarrow$ Bảng phân tích ngắn, không hứa tiền | Code tính tam hợp/lục hợp từ `canchi.py`, khung *"theo truyền thống"* |

---

## 3. Dạng đã thua — KHÔNG làm lại

Tránh tuyệt đối 4 dạng đã thất bại trong thực nghiệm:
1. **Hỏi – giảng lý thuyết (20–35s)**: Khô khan, mang tính độc thoại giảng giải một chiều, người xem lướt qua ngay (trung vị kênh chỉ 600–970 view).
2. **Hoạt hình Tiền Thân kể tóm tắt**: Kể dàn trải thiếu cao trào, không có cú lật nhân quả (bài 36s chỉ đạt 302 view).
3. **Cung hoàng đạo phương Tây**: Lệch hoàn toàn tệp khán giả quan tâm phong thủy Á Đông và Phật giáo truyền thống.
4. **Giọng doạ nạt / hứa hẹn làm giàu**: Cấm dùng từ ngữ hù dọa (*"hậu họa khôn lường"*, *"tai ương ập đến"*) hoặc hứa tiền bạc (*"giàu ngầm"*, *"phát tài sau một đêm"*). Vừa phạm luật đạo đức kênh vừa bị thuật toán hạn chế.

---

## 4. Vibe từng kênh & "Chữ ký" hình riêng

Mỗi kênh có bộ nhận diện thị giác đặc trưng. Hai bài đăng liền kề trên cùng kênh phải có **"chữ ký" hình riêng** (khác biệt về bố cục, biểu tượng mờ hoặc hiệu ứng xuất hiện), không lặp lại nguyên xi:

- **Phong Thủy (FS)**:
  - Tông màu: Nền chàm huyền bí hoặc đỏ son – vàng kim (`tet-poster`, `son-mai`).
  - Họa tiết: Bát quái / Thái cực mờ sau bảng, dấu son niêm ấn, núi non thủy mặc.
  - Chữ ký: Thay đổi giữa đĩa la bàn quay 3D, sơ đồ bàn tay nét vàng, hoặc dải hạt ngũ hành.
- **Phật Giáo (BUD)**:
  - Tông màu: Nâu trầm / vàng nghệ ấm cúng (`saffron`), tạo cảm giác tôn nghiêm, thanh tịnh.
  - Họa tiết: Bánh xe Pháp luân mờ, hoa sen nở đáy, ánh nến lung linh.
  - **ẢNH THẬT tượng Phật (Luật 17)**: Dùng ảnh chụp tượng Phật thật, phù điêu, tranh cổ từ bảo tàng công cộng CC0 (CMA, Met, AIC) hoặc Wikimedia Commons. **Cấm vẽ mặt Đức Phật bằng code, hoạt hình, biếm họa.** Từ 23/10/2026 được dùng ảnh AI (ChatGPT, Flow) có mặt Đức Phật khi mặt không méo và trang nghiêm (docs/adr/0004). Ảnh trang nghiêm: không đè chữ lên mặt tượng, không cắt ngang đầu, phóng chậm 1.00 $\rightarrow$ 1.04.

---

## 5. Quy chuẩn Bố cục 1080×1920

Toàn bộ thành phần đồ họa phải nằm trong vùng hiển thị an toàn (safe-zone), tránh bị che bởi các nút tương tác bên phải ($x > 940$) và dải phụ đề/thanh tiến trình bên dưới ($y > 1490$):

```
+----------------------------------------------------+ y = 0
| [VÙNG TRÊN: y 0 - 110] Lề an toàn trên cùng        |
+----------------------------------------------------+ y = 110
| TIÊU ĐỀ: y 110 - 400 (Chip top 64; Tiêu đề 2 dòng) |
+----------------------------------------------------+ y = 400
| [KHOẢNG ĐỆM: y 400 - 430] Tối đa 30px              |
+----------------------------------------------------+ y = 430
| NỘI DUNG CHÍNH (Bảng / Ảnh / Sơ đồ): y 430 - 1440  |
| - Phủ >= 85% bề ngang an toàn (cover >= 880px)     |
| - Không để khoảng trống dọc nào > 250px            |
| - Mặt tượng Phật ở BUD không bị chữ đè lên         |
+----------------------------------------------------+ y = 1440
| [FOOTER / CTA]: Bottom <= 1473px                   |
+----------------------------------------------------+ y = 1490
| [DẢI PHỤ ĐỀ / NÚT SHORTS]: y 1490 - 1920           |
+----------------------------------------------------+ y = 1920
```

- **Tiêu đề (Header)**: Nằm gọn trong $y = 110 - 400$. Cỡ chữ tiêu đề $\ge 64\text{px}$.
- **Nội dung chính (Body)**: Nằm gọn trong $y = 430 - 1440$. Phủ $\ge 85\%$ bề ngang an toàn ($x$ trong $60 - 940$, $x_{\min} \le 80$, $x_{\max} \ge 860$).
- **Khoảng trống dọc (Vertical Gap)**: Giữa các khối không được có khoảng trống dọc trống trơn $> 250\text{px}$.
- **Cỡ chữ**: Nội dung/chú thích $\ge 36\text{px}$; chữ số chính/năm sinh $\ge 90\text{px}$.
- **Phụ đề**: Đặt hoàn toàn dưới $y = 1490$.
- **Khung cuối (Hold Frame)**: Giữ hình tĩnh tuyệt đối $\ge 3$ giây ở cuối video (`mean abs difference` giữa khung $-3\text{s}$ và khung cuối $\le 0.05$).

---

## 6. Quy chuẩn Âm thanh (Audio Mixing)

- **Phật Giáo (BUD)**:
  - Nhạc nền thiền tĩnh lặng (`hf_music.CATALOG["bud"]`: White Lotus, Peace of Mind, That Zen Moment...), không lời, không trống dồn dập.
  - Âm lượng nhạc đặt ở mức **$-20\text{ dB}$ LUFS dưới giọng đọc** (chênh lệch đúng $20.0\text{ dB}$, ví dụ giọng $-18\text{ LUFS}$ thì nhạc $-38\text{ LUFS}$).
  - Nhạc vào trước giọng đọc $0,5 - 1\text{s}$ (`adelay=600|600`).
  - Ở 3 giây cuối, nhạc giảm dần nhưng giữ lại $\sim 40\%$ âm lượng nền cho tới hết video (`afade=t=out:st=dur-3:d=3:silence=0.4`), không ngắt đột ngột.
  - **Điểm nhấn âm thanh**: 1 tiếng chuông xoay Tây Tạng / khánh thiền CC0 (Tibetan singing bowl) ở giây 0 hoặc ngay trước câu Phật dạy.
- **Phong Thủy (FS)**:
  - Nhạc phương Đông huyền bí, nhịp chậm (`CATALOG["fs"]`).
  - **BỎ Asian Drums cho dạng bảng tĩnh** (nhịp trống dồn dập gây phản cảm khi đọc bảng).
  - Điểm nhấn: Tiếng gió hoặc chuông gió nhẹ khi đóng dấu son.
- **Xoay vòng chống spam YouTube**:
  - Không để một bản nhạc chiếm $> 35\%$ tổng số video trong 7 ngày gần nhất trên kênh.
  - Cập nhật nhật ký phát nhạc vào file ledger `bgm_shorts.json`.

---

## 7. Bốn trục mở rộng (4D Scaling Matrix) & "Gia đình bảng"

```
[Chìa khoá] × [Câu hỏi] × [Mốc thời gian] × [Khuôn hiển thị]
```

1. **Chìa khoá**: Năm sinh, Tên Chi (Tý…Hợi, tối đa 3 tên chi/câu), Cung mệnh, Đường chỉ tay.
2. **Câu hỏi**: Tam Tai, Thái Tuế, Kim Lâu, Làm nhà, Cưới hỏi, Khai trương, Lời khuyên tâm trạng.
3. **Mốc thời gian**: Năm tới (đón đầu 2027), Tháng tới (ngày tốt), Hằng ngày (Hoàng đạo daily).
4. **Khuôn hiển thị (Board Family)**:
   - `Review List`: Danh sách tuổi/hạn (Tam Tai, Thái Tuế).
   - `month_sheet`: Tờ lịch tháng khoanh tròn ngày tốt làm nhà, cưới hỏi.
   - `thiep_cuoi`: Thiệp cưới song hỷ trang trọng, phân biệt ngày dương/âm.
   - `review_budtable`: Bảng ngày vía, ngày ăn chay, lịch Phật giáo tôn nghiêm.
   - `hoangdao_daily`: Lưới hoàng đạo hằng ngày, giờ cát lợi và tuổi xung.
- **Tỷ lệ 60/40**: 60% sản lượng duy trì khuôn thắng đã chứng minh hiệu quả; 40% thử nghiệm biến thể mới (tối đa 1 biến thể mới/tuần).

---

## 8. Luật kênh & Đạo đức nội dung

### Phong Thủy (FS)
- **Tên Chi**: Gọi chuẩn tên chi (*Tý, Sửu, Dần... Hợi*), tuyệt đối không dùng "Mèo/Lợn/Dê". Tối đa 3 tên chi mỗi câu.
- **Tính toán thuần bằng code**: 100% số liệu lấy từ `output/cl_staging/long/tuvi_year.py`, `canchi.py`, `amlich.py`. Không dùng thư viện ngoài cho trực/thần/nạp âm; không gõ tay số liệu.
- **Khung pháp lý**: Luôn gắn khung *"theo truyền thống / tham khảo"*. Không dọa nạt, không hứa tiền.

### Phật Giáo (BUD)
- **Đối chiếu kinh điển**: Lời Phật chỉ trích dẫn khi đã kiểm bằng `.venv/bin/python hf_sutta.py` (Pali) hoặc có văn bản nguồn rõ ràng (Bắc tông). Dán nguyên văn đối chiếu vào báo cáo.
- **Truyện Jātaka**: Theo bản dịch Cowell (`output/cl_staging/long/research/jataka_cowell/`). Truyền thuyết/chú giải phải gắn nhãn *"theo chú giải / truyền thuyết"*.
- **Ý nghĩa biểu tượng**: Gắn nhãn *"theo cách giải thích phổ biến"*.
- **Mỹ thuật tôn nghiêm**: Tuân thủ Luật 17 (ảnh thật tượng Phật/phù điêu CC0, cấm vẽ mặt Phật bằng code/hoạt hình, ảnh AI có mặt Phật được dùng từ 23/10 nếu không méo, không đồ hiện đại trong truyện cổ, không người phương Tây, không tôn giáo khác).

---

## 9. Bộ kiểm bắt buộc trước khi báo xong

Mọi short (FS và BUD) trước khi gửi Lead review phải vượt qua 6 cổng kiểm tra tự động và thủ công:

1. **Tràn chữ (Overflow check)**: Chạy script kiểm tra bounding box trên headless browser, xác nhận `n = 0` phần tử bị tràn viền; font độ đậm 900 hiển thị đầy đủ dấu tiếng Việt.
2. **Safe-zone & Top $\ge 40$**: Đo tại 4 mốc thời gian (10%, 35%, 65%, khung cuối), xác nhận mép trên chữ cách đỉnh $\ge 40\text{px}$, không đè chip danh mục ($y < 110$).
3. **Đo khoảng trống dọc & Độ phủ**: Bề ngang an toàn phủ $\ge 85\%$ ($cover \ge 880\text{px}$); không có khoảng cách dọc giữa các khối $> 250\text{px}$.
4. **Soát 2 kích thước hiển thị**:
   - Khung $1080\times 1920$: Rõ nét, không răng cưa, bố cục cân đối.
   - Khung thu nhỏ $168\text{px}$ (mô phỏng thumbnail YouTube Shorts mobile): Tiêu đề và tên hàng chính phải đọc được rõ ràng.
5. **Tờ ảnh kiểm tra (Media sheet)**: Dựng tờ ảnh chụp khung hình tại 4 mốc thời gian: 25%, 50%, 75% và khung cuối.
6. **Mở xem và mô tả thật từng ảnh (Luật 15 & 17)**:
   - Mở file tờ ảnh ra nhìn tận mắt từng khung hình.
   - Ghi mô tả chân thực những gì thấy trên ảnh vào báo cáo (không chép câu truy vấn prompt).
   - Kiểm duyệt nghiêm ngặt: Nhân vật trong FS phải là người Việt/Á Đông; BUD không có đồ đời nay, không biểu tượng tôn giáo khác; ảnh tượng Phật phải trang nghiêm, ghi rõ nguồn (CMA/Met/AIC/Commons), không bị chữ đè lên mặt tượng.

---

## 10. Quy trình điều phối Thợ – Lead

- **Thợ**: Thực thi mã nguồn, dàn layout, trộn âm thanh, dựng tờ ảnh và chạy trọn vẹn bộ kiểm. Báo cáo bằng tiếng Việt $\le 300$ chữ vào `output/cl_staging/grok/reports/<tên task>.md`.
- **Lead**: Review độc lập chất lượng hiển thị, đối chiếu số liệu nguồn, duyệt và thực hiện lệnh render/đăng video.
- **Luật làm việc của Thợ**: Xem chi tiết 18 điều luật tại [worker_rules.md](file://references/worker_rules.md).
