# Đề xuất: chuẩn hình ảnh chung 5 kênh (issue #467)

Trạng thái: **ĐỀ XUẤT, chờ bên FS/BUD/VSD xem và cùng duyệt**. Chưa áp vào cổng hay quy trình.

Chủ kênh 17/11/2026, sau khi xem Sarin (57% cảnh là chữ): *"cắt cảnh không nhất thiết 5–6s; nếu ảnh/video minh hoạ đủ cho 1 cảnh thì áp panorama, video để kéo dài cảnh, không áp luật cứng cho việc cắt cảnh… nếu thiếu cảnh thì còn chart/đồ hoạ dữ liệu/map… rất nhiều bộ skill đã build trong hyperframes, sao cứ phải dùng chữ"*; beattext chỉ nên **10–15%** một video. Chủ kênh yêu cầu: Lead creator_v2 đưa nghiên cứu + đề xuất cho **flow dùng chung cả 5 kênh** (MIM, CK, CL, FS, BUD); **Lead/agent luồng FS/BUD/VSD xem và bổ sung**; cùng approve rồi mới dựng lại Sarin.

## 1. Số liệu hiện trạng (creator_v2, đếm cảnh trong `data/long/*/chNN.json`)
"Chữ" = kinetic + slam + quote + question.

| Kênh | Số Long | Chữ trung bình | Ghi chú |
|---|---|---|---|
| CL | 17 | **45%** | Sarin 60%, HKV 53%, ripper 50%; thấp nhất hoa-than 29%. pano = 0 ở mọi video |
| MIM | 27 | **38%** | cao: ai-voice 64%, ai-gpu 59%; thấp: watson 20%, poker 23% (nhiều đồ hoạ dữ liệu) |
| CK | 5 | **22%** | g2 9%, g1 18%: đồ hoạ dữ liệu 23–35% số cảnh → bằng chứng đồ hoạ thay được chữ |

FS/BUD (luồng gốc `hyperframes_short`/`hf_*`): **chưa đo — nhờ bên FS/BUD bổ sung.**

## 2. Vì sao chữ cao
1. `motion/long/floor.py` chỉ chặn **kinetic > 38%**; slam/quote/question **không tính** → người viết cảnh đẩy sang slam (Sarin: 117 kinetic + 78 slam).
2. **Thiếu hình**: mỗi câu lời = một cảnh; câu không có hình hợp thì thành chữ trên nền ảnh (Sarin: 31 ảnh tư liệu + 29 ảnh AI cho 343 cảnh; ảnh AI ai09 lặp 15 lần).
3. **Nhịp cắt cứng** ~5,6 s/cảnh → cần nhiều cảnh → chữ là thứ rẻ nhất để lấp.
4. Bộ công cụ hình có sẵn **không được dùng**: `pano` 0%, style ảnh (`woodcut`, `pencil`, `film16`, `blueprint`, `papercut`, `oneline`) gần như 0, phim tư liệu PD (#445) và `media_map` (#433) chưa áp cho Long đã dựng.

## 3. Đề xuất chuẩn dùng chung 5 kênh
**A. Ngân sách chữ:** kinetic + slam + quote (+ question) **≤ 15%** số cảnh của Long (Short: đề nghị bên FS/BUD đặt số riêng). Chữ dành cho câu then chốt: nghịch lý, con số sốc, câu hỏi chương.

**B. Không có độ dài cảnh cứng:** hình mạnh được giữ theo nhịp kể bằng `pano`, chuyển động máy, parallax nhiều lớp, b-roll video, phim PD. Ngoại lệ duy nhất: cửa sổ mở đầu (cổng #453, 120 s đầu) và cold open §survival.

**C. Thứ tự lấp chỗ thiếu hình (thay vì chữ):**
1. Clip/video thật có giấy phép, phim tư liệu PD (#445).
2. Ảnh AI phỏng tác nhân vật/cảnh (§15, chủ kênh 17/11) — nhân vật lịch sử; người còn sống không.
3. Ảnh tư liệu giữ lâu: `pano`, camera, parallax.
4. Đồ hoạ dữ liệu: `bars`, `heat`, `waterfall`, `stack`, `counter`, `units`, `candles`…
5. Bản đồ/thời gian/quan hệ: `map`, `timeline`, `org`.
6. Tư liệu dạng vật thể: `file`, `print`, `book`, `source`, `ledger`.
7. Một ảnh → nhiều cảnh khác chất: `woodcut`, `pencil`, `film16`, `blueprint`, `papercut`, `oneline`.
8. Minh hoạ chung `minh_hoa_chung`.

**D. Ngân sách hình mỗi Long (25–30 phút):** 120–150 hình khác nhau; một ảnh tĩnh dùng tối đa 3–4 lần (đổi style/khung được tính là lần mới); kiểm kê trước khi viết cảnh, thiếu thì tạo ảnh phỏng tác qua GrokBot trước (≈2 phút/ảnh).

**E. Cổng tự động (code, Codex làm sau khi duyệt):**
- `floor.py`: tỷ lệ chữ gộp ≤ 15% cho Long mới (Long cũ: legacy, không chặn).
- Cảnh báo ảnh lặp > 4 lần, cửa sổ 2 phút < 3 kiểu chuyển động (đã có, nâng thành lỗi?).
- Báo cáo phân bố loại cảnh in ở bước `html` để Lead thấy ngay.

**F. Quy trình viết cảnh:** brief viết cảnh ghi ngân sách chữ/hình; `media_map` gắn hình theo nghĩa câu trước, chỉ câu then chốt mới thành chữ.

## 4. Nhờ bên FS/BUD/VSD xem và bổ sung
- Tỷ lệ chữ thực tế của Long/Short FS, BUD, VSD hiện nay; engine gốc có dạng hình nào chưa có ở creator_v2 (và ngược lại).
- Ngưỡng hợp lý cho Short (dạng bảng tra FS là chữ có chủ đích — có tính là "chữ" không?).
- Đề xuất có xung đột với cổng nào bên đó (`hook_lint`, cổng 3 giây #253…)?
- Có nên hợp nhất thành một module kiểm "visual mix" chung (#159)?

## 5. Sau khi cùng duyệt
- [ ] Ghi chuẩn vào `docs/pm/storytelling-guide.md` + skill long-video / shorts-studio.
- [ ] Codex sửa cổng (`floor.py` và tương đương bên gốc).
- [ ] Dựng lại Sarin theo chuẩn (giữ lời và giọng đã có), thay bản đã tải lên, vẫn kịp 01/12.
- [ ] Vidocq làm theo chuẩn từ đầu.
