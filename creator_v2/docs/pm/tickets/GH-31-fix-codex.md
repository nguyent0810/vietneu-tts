# GH-31 · Codex vòng sửa P0: bật nguồn đã rà ToS, Wikipedia chỉ làm tín hiệu

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/31. Đầu vào:
- `docs/pm/tickets/GH-31-sources.json`: 45 nguồn Grok đã rà điều khoản; 13 `ok`, 17 `pending`, 15 `blocked`;
- `docs/pm/tickets/GH-31-grok-report.md`;
- báo cáo vòng trước `docs/pm/tickets/GH-31-report.md`.

## Lỗi vòng trước
Lần chạy thử lấy 1000 trang top Wikipedia làm "bài", nên báo cáo ra 943 sự kiện nhiễu: `Main_Page`, `Special:Search`, `Wikipedia:About`… và các trang top toàn cầu không liên quan kênh.

## Được ghi
- `factory/trend/*`
- `tests/test_trend_*.py`
- `tests/fixtures/trend/`
- báo cáo `docs/pm/tickets/GH-31-fix-report.md`

**Không:** đổi `tos_status` khác với file của Grok, gọi nguồn `pending`/`blocked`, dùng yt-dlp hoặc autocomplete, thêm dependency, commit, đụng `state.sqlite` hay lịch.

## Việc
1. **Nguồn.** Thay `factory/trend/sources.json` bằng 45 mục từ `GH-31-sources.json`, giữ nguyên `tos_status`, `tos_note`, `owner_group`, `channels`. Thêm trường `role`:
   - `article`: nguồn tin, tạo bài để gom sự kiện. Gồm GDELT VI, Hacker News, arXiv, Google blog, SEC, NIST, Fed, BLS.
   - `signal`: chỉ cộng tín hiệu cho sự kiện đã có. Gồm Wikipedia pageviews (vi và en), Google Trends daily.
2. **Parser.**
   - GDELT DOC 2.0 dạng RSS (`sourcelang:vie`): lấy domain gốc của từng bài làm `owner_group` phụ để đếm nguồn độc lập. GDELT chỉ là bộ tổng hợp, tòa soạn mới là nguồn.
   - Hacker News Firebase: top stories, giới hạn 60 bài.
   - Google Trends daily RSS VN: mục xu hướng kèm traffic xấp xỉ.
   - Atom/RSS cho arXiv, SEC, NIST, Fed, BLS.
   - Tôn trọng giới hạn tần suất ghi trong `tos_note`: SEC ≤ 10 req/s, khai báo User-Agent kèm email liên hệ dạng placeholder để Lead điền. Mỗi nguồn timeout 20 s, lỗi thì ghi `run` rồi chạy tiếp.
3. **Wikipedia và Google Trends = tín hiệu.** Không tạo `article`.
   - Lọc namespace (`Special:`, `Wikipedia:`, `File:`, `Main_Page`, `Trang_Chính`, …).
   - Chỉ khớp vào sự kiện đã có qua thực thể (tiêu đề trang chuẩn hóa ≈ thực thể của sự kiện).
   - Ghi `signals` của sự kiện: pageviews hôm qua so với trung vị 7 ngày, có trong Trends VN hay không.
4. **Lọc theo kênh.** Mỗi sự kiện gắn kênh theo `channels` của nguồn, cộng bộ từ khóa trụ cột:
   - MIM: AI, chip, bảo mật, hack, dữ liệu, robot, các hãng công nghệ…
   - CK: lãi suất, giá vàng, thuế, BHXH, lương, tỷ giá, ngân hàng, chứng khoán…
   - Đặt bộ từ khóa trong `factory/trend/keywords.json`. Sự kiện không hợp kênh nào thì không vào báo cáo.
5. **Báo cáo.**
   - Mỗi kênh tối đa 20 sự kiện.
   - Không có trang Wikipedia rác. Mỗi sự kiện có ≥ 1 URL bài báo hoặc nguồn sơ cấp.
   - Ghi số nguồn độc lập (theo domain gốc của GDELT và `owner_group`), tốc độ, tín hiệu.
   - Cuối báo cáo có bảng tình trạng từng nguồn trong lần chạy (ok, lỗi, số bài).
6. **Test (offline, fixture).**
   - Không tạo article từ nguồn `signal`.
   - Lọc namespace.
   - Domain GDELT đếm như nguồn độc lập; hai bài cùng domain chỉ tính 1.
   - Nguồn `pending`/`blocked` không bao giờ được gọi.
   - Lọc kênh theo từ khóa.
7. Chạy thử một lần thật với các nguồn `ok`. Nếu sandbox chặn mạng hoặc DNS thì ghi lại; Lead sẽ chạy 3 lần nghiệm thu ngoài sandbox.

## Báo cáo
Cấu trúc thay đổi, kết quả test, output chạy thử: số bài và số sự kiện mỗi kênh, 5 sự kiện đầu mỗi kênh.
