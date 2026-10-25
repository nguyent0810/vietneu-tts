# Đo kênh bằng số bài trúng và tín hiệu xem lặp; nhân khuôn ngay khi có tín hiệu; giữ một sổ thất bại để không lặp lại

Trạng thái: đã chấp nhận (24/10/2026).

Ngày 24/10 short "Năm 2027: 4 tuổi phạm Thái Tuế" vượt 100k view; riêng 48 giờ gần nhất đạt 26.775 view, 97% từ Shorts feed. Ta lấy toàn bộ video có view của hai kênh trong cửa sổ 25/09–22/10 (YouTube Analytics, cùng cửa sổ với trang "Top content" của Studio), xếp theo dạng bài để xem view thật sự đến từ đâu. Số API trễ 2–3 ngày so với Studio (bài Thái Tuế: API 77.590, Studio 92,4k). Tỉ lệ giữa các bài thì vẫn dùng được.

## Số đo

### 1. View dồn vào rất ít bài, nhất là ở FS

| 25/09–22/10 | FS | BUD |
|---|---|---|
| Video có view | 200 (181 short, 19 Long) | 200 (175 short, 25 Long) |
| Tổng view | 471.414 | 108.005 |
| Top 3 / top 10 | 45% / **74%** | top 10: **15%** |
| Trung vị short | 418 | 704 |
| Short dưới 1.000 view | 138/181 | 134/175 |
| Bài cao nhất | 77.590 | 2.634 |
| Sub từ top 10 | 308/426 (72%) | — |
| Long: tổng view / trung vị | 2.649 / 57 | 1.800 / 24 |

FS là phân phối "bài trúng": vài bài kéo cả kênh. BUD đều đặn nhưng chưa có bài nào bứt khỏi trần. Long của cả hai kênh chỉ chiếm 0,6% (FS) và 1,7% (BUD) view.

### 2. FS: dạng bài quyết định, không phải chủ đề

| Dạng (short FS) | n | Trung vị view | AVP trung vị | Bài > 10k |
|---|---|---|---|---|
| Năm 2027 + tuổi/năm sinh | 10 | **15.431** | **111%** | 6 |
| Ngày cụ thể, khuôn mới "ngày X: tuổi nào…" (bảng) | 3 | **17.030** | **159%** | 2 |
| Ngày cụ thể, khuôn cũ (thuật ngữ sao + trực) | 26 | 548 | 76% | 0 |
| Con giáp / tuổi chung | 31 | 1.058 | 93% | 0 |
| Năm sinh / mệnh | 48 | 538 | 65% | 0 |
| Ngũ Hành / Kinh Dịch | 9 | 857 | 44% | 0 |
| Can chi, nhật chủ, chiêm tinh, chỉ tay | 47 | 263 | — | 0 |
| Nhà / đồ vật | 7 | 21 | 77% | 0 |

Nhóm 2027 có 10 bài nhưng đạt 290.528 view (62% kênh) và 252/426 sub (59%).

Cùng chủ đề ngày tốt/xấu, khuôn mới đạt trung vị gấp khoảng 31 lần khuôn cũ. Đây là bằng chứng mạnh nhất cho ADR 0006: giữ chủ đề, đổi khuôn.

### 3. Trong nhóm thắng, cái gì làm bài trúng hơn

- **Bảng 10 giây, xem lặp:**
  - Thái Tuế: AVP 242%, 77,6k view.
  - 3 tuổi hợp: AVP 199%, 69,6k.
  
  Bản 26–31 giây cùng nhóm có AVP 99–128%.
- **Có chìa khoá cá nhân thì thắng.** "Năm 2027 có tháng nhuận không?" chỉ đạt 1.260 view: người xem không có lý do dò tuổi mình.
- **Chia giới làm hẹp người xem:**
  - nam, sao Thái Bạch: 15,2k;
  - nam, Kế Đô: 9,9k;
  - nữ, La Hầu: 5,4k.
- **Bảng kéo view, câu hỏi cụ thể kéo sub.** Sub/1k view: Tam Tai (câu hỏi, nền tối) 1,48; "3 tuổi hợp" (bảng) 0,83; Thái Tuế (bảng) 0,53.
- **AVP trên 100% là tín hiệu sớm:** 10/10 bài top của FS có AVP từ khoảng 99% trở lên, trong khi trung vị short FS khoảng 84%.

### 4. BUD: chuỗi đúng hướng nhưng chưa có bài trúng

- 155/175 short BUD là dạng câu hỏi đời sống hoặc vật trong chùa, trung vị 817 view.
- Bài cao nhất chỉ 2.634 ("Đức Phật mỗi ngày ăn mấy bữa?", AVP 134%).
- Ba trong tám bài top có AVP trên 100%: câu hỏi cụ thể kiểu này cũng gây xem lặp, chỉ chưa đủ để phá trần.
- Short tiêu đề dạng mệnh đề khái niệm ("Bát Chánh Đạo: Lộ Trình 8 Bước…", "Ba đặc tính vô thường – khổ – vô ngã") chỉ có 3–12 view.

## Quyết định

1. **Thước đo chính của mỗi kênh** là số bài vượt 10k view mỗi tuần, kèm tỉ lệ bài có AVP ≥ 1,3 lần trung vị AVP của nhóm cùng độ dài. Trung vị và tổng view chỉ để xem nền.
2. **Nhân khuôn theo tín hiệu sớm, nhưng cần hai điều kiện.** Bài vừa có hạng view trong tuần ≥ 0,9, vừa có AVP ≥ 1,3 lần trung vị AVP của nhóm cùng độ dài, thì làm thêm 2–3 bài cùng khuôn (đổi chủ đề trong cùng họ), không chờ đủ 7 ngày. Mỗi ngày tối đa 1 bài cùng họ, để feed không coi là lặp.

   Sửa ngày 24/10 sau phản biện Muse. AVP đứng một mình là tín hiệu yếu vì bài ngắn chạy vòng:
   - 8/9 short FS dưới 15 giây có AVP > 100% mà trung vị chỉ 883 view.
   - Ở nhóm 15–19 giây, bài AVP > 100% trung vị 727 view, nền 707.
   - Chỉ khi AVP vượt hẳn nhóm cùng độ dài mới thấy bài trúng: 3 bài dưới 15 giây vượt 1,3 lần nhóm có trung vị 69,6k view.

   `hf_brief` in mục "nên nhân khuôn" theo đúng hai điều kiện này.
3. **Mỗi bài thắng của FS phải có đủ:**
   - mốc thời gian cụ thể (năm 2027, ngày mai);
   - chìa khoá dò được (năm sinh, tuổi);
   - một con số trong tiêu đề;
   - bảng đứng yên đủ lâu để dò.
   
   Không chia giới trong tiêu đề. Nếu nội dung khác nhau theo giới thì gộp hai giới vào một bảng.
4. **BUD tìm bài trúng bằng câu hỏi cụ thể có xem lặp,** không bằng mệnh đề khái niệm, và không bằng bề mặt của FS.
5. **Ghi sổ thất bại.** Mỗi lần thử thua ghi một dòng vào bảng dưới đây: thử gì, số đo, bài học, đã đổi thành gì. Trước khi mở một chuỗi mới phải đọc bảng này.
6. **Luật dừng khuôn** (thêm 24/10). Khuôn nào trong 14 ngày gần nhất có ≥ 6 bài, trung vị view dưới sàn và không bài nào vượt 3 lần sàn thì dừng. Sàn FS là 1.000 view. Sàn BUD là trung vị short của chính cửa sổ: trung vị kênh BUD chỉ khoảng 700, nên sàn 1.000 sẽ dừng gần hết. Dừng nghĩa là đổi khuôn, giữ chủ đề (ADR 0006), rồi ghi một dòng vào sổ thất bại. `hf_brief` in bảng "luật dừng khuôn" theo khuôn (`lane` trong plan).

## Sổ thất bại (tới 24/10/2026)

| Khi | Đã thử | Kết quả có số | Bài học | Đã đổi thành |
|---|---|---|---|---|
| tới 05/10 | Đăng dồn nhiều short mỗi ngày, mọi chủ đề | Trần khoảng 1.000 view: 1/407 bài vượt 2.000; tuần trước 05/10 dính cập nhật Shorts 01/10 | Số lượng không phá được vòng thử | 5 ô/ngày/kênh, đo theo tuần sạch (ADR 0015) |
| 06/10 | BUD "đời sống chung" (lời khuyên không gắn kinh, không gắn vật) | 0/85 bài vượt 1.200 view | Người nghe BUD cần câu hỏi cụ thể + lời Phật có nguồn | Gỡ lịch 180 short; BUD chuyển sang câu hỏi đời sống, vật chùa |
| 06/10 | FS "lý thuyết" (giảng khái niệm) | 0,23 sub/bài | Không có chìa khoá cá nhân thì không ai dừng lại | Gỡ lịch; FS chuyển sang năm sinh, tuổi, bảng |
| 06/10 | Chiêm tinh Tây trên kênh phong thủy | Trung vị 340 view | Lệch kỳ vọng khán giả của kênh | Bỏ chuỗi |
| tới 19/10 | Ngày tốt/xấu khuôn cũ (thuật ngữ sao + trực) | n=26, trung vị 548 | Thuật ngữ chuyên môn không cho người xem biết "có liên quan tới mình không" | Khuôn "ngày X: tuổi nào…" dạng bảng: trung vị 17.030 |
| tới 21/10 | Ngũ Hành / Kinh Dịch dạng giảng | 120–270 view, stay 11–16% | Giữ chủ đề nhưng phải đổi khuôn (bảng, 3D), không giảng | ≤ 1 Ngũ Hành/ngày, thử khuôn bảng (ADR 0006) |
| tới 21/10 | FS nạp âm cặp năm sinh | khoảng 1.290 view dù stay cao nhất kênh (48%) | Giữ chân tốt nhưng không có mốc thời gian thì không bứt | Ghép mốc 2027 |
| 21–22/10 | Bê bề mặt FS sang BUD (bảng, lưới, câu 9 giây) | 2–6,5 view/giờ, so với nền 21–57 | Chép cơ chế, không chép bề mặt | BUD giữ giọng thầy và câu hỏi đời sống |
| 21/10 | Tiền Thân dạng hoạt hình (short) | 0/7 bài đạt nền | Hoạt hình hạ độ trang nghiêm của ngách | Truyện nhân quả 1,5–3 phút giọng kể |
| tới 21/10 | Tiêu đề "X có phải là Y?" với khái niệm trừu tượng | stay 9–15%, so với 45–53% khi hỏi cụ thể | Câu hỏi phải nhìn thấy được | Lint tiêu đề (`hook_lint.py`) |
| tới 24/10 | Short BUD tiêu đề mệnh đề khái niệm | 3–12 view/28 ngày | Như trên | Chỉ dùng câu hỏi cụ thể |
| tới 24/10 | FS chia giới trong tiêu đề | nữ La Hầu 5,4k so với nam Thái Bạch 15,2k | Mỗi giới chỉ còn một nửa người xem | Gộp hai giới vào một bảng |
| tới 21/10 | Long 30 phút chủ đề rộng ("Tử vi trọn đời", "Truyện Tiền Thân", "Lời Phật dạy về X") | Mất 76–92% người xem trong 90 giây; mỗi tập 5–172 view; Long chiếm 0,6–1,7% view kênh | Thua vì khuôn, không vì độ dài | Khuôn nhân vật (ADR 0001), điểm duyệt 22/11 |
| 01/10 | Giọng mẫu A (đọc nhanh), mẫu B (vang, nhạc to) | Chủ kênh chê "rẹt rẹt như robot" | Nghe trước khi áp | Preset C (ADR 0010) |
| 01/10 | Long với ba sơ đồ lặp khuôn | 68% thời lượng ba sơ đồ, cảnh đứng 64 giây | Đo nhịp hình trước render | `pacing` (ADR 0009) |
| 04/10 | Job dọn tự động lúc 3:30 sáng | Mất bản render lại của F10/B10 | Không dọn khi không có người nhìn | Dọn tay vào Thùng rác (ADR 0012) |
| 20/10 | Đếm lịch bằng playlist | Báo 0 video đã hẹn, thực tế 71 | Đếm theo ID | `hf_coverage` (ADR 0007) |
| 20/10 | Đọc "HẾT QUOTA" là quota API | Thực ra là trần 24 upload/24 giờ tự đặt | Đọc đúng mã lỗi trước khi chờ | Ghi rõ trong ADR 0007 |
| 13–21/10 | Tin phản biện ngoài ("2027 thắng nhờ search"; thợ ghi "10h30 tụt 50%") | Thực tế 95,8% view từ feed; mức tụt 20% | Lead tính lại mọi số | ADR 0008, 0015 |
| 23/10 | Stock tìm bằng tiếng Anh cho Long | Khoảng 45 ảnh phải gỡ (Kinh Thánh, chữ Hebrew, "STOP WAR") | Stock xếp cuối | Ảnh AI theo phong cách kênh (ADR 0004) |
| 23/10 | Thumbnail Long không có tên ("SẤM CỦA AI?") | Không ai nhận ra là Trạng Trình; 11/12 bài top có tên trên ảnh | Tên mỏ neo trước | Tên + ≤ 3 chữ (ADR 0005) |
| 24/10 | Ảnh chân dung dọc trong Long khung ngang | 5 cảnh chỉ còn búi tóc hoặc dải mắt | Đổi khung trước khi dùng | Bridge tự đặt vào khung 16:9 (PR #29) |

## Hệ quả

- `hf_brief` có thêm ba mục: bài trúng mỗi tuần (số bài > 10k, tỉ lệ AVP vượt nhóm độ dài), nên nhân khuôn, luật dừng khuôn. Mục "điểm rơi" (ticket 71) giữ nguyên.
- Tiêu chí thắng/thua của một ô thử (ADR 0006) giữ nguyên. Thêm một cửa nhân nhanh (hạng view + AVP so theo nhóm độ dài) và một cửa dừng.
- Rủi ro: nhân khuôn quá nhanh có thể làm feed coi là nội dung lặp. Giới hạn 1 bài cùng họ mỗi ngày, đổi chủ đề trong họ, đổi nhạc theo sổ (ADR 0011).
- Sổ thất bại nằm ngay trong ADR này để người mới đọc một chỗ. Khi bảng dài quá thì tách ra file riêng và giữ link.

## Bằng chứng

Truy vấn Analytics ngày 24/10:

- `dimensions=video`;
- `metrics=views,averageViewPercentage,subscribersGained`;
- cửa sổ 25/09–22/10, cả hai kênh;
- kết quả lưu ở `output/cl_staging/scoreboard/top28_2026-09-25_10-22.json`, script `top28.py` cùng thư mục.

Nguồn khác:

- ảnh Studio "Top content" 28 ngày và trang realtime của bài Thái Tuế (24/10);
- `output/cl_staging/bud/phan_tich_lan_short_2026-10-21.md`, `output/cl_staging/phan_tich_studio_2026-10-22.md`, `output/cl_staging/long/phan_tich_long_2026-10-21.md`;
- sổ khôi phục `shorts_unscheduled_2026-10-06.json`;
- `output/cl_staging/retro/*.md`.
