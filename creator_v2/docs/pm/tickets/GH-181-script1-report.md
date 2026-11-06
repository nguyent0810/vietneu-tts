# GH-181 — báo cáo script 1 (`ck-g1-tra-no-truoc-han`)

## Đã làm

- Viết `data/long/ck-g1-tra-no-truoc-han/script.md` theo dàn 8 chương của plan (CH00–CH07), UTF-8.
- Viết `data/long/ck-g1-tra-no-truoc-han/factcheck.md`: bảng theo chương, bảng phép tính, mục câu trích, mục chưa kiểm được. Có 10 URL nguồn.
- Không sinh cảnh, không TTS, không `chNN.json`, không commit, không đăng, không đổi lịch, không ghi `state.sqlite`. Không đụng `data/long/ck-g1-thuong-tet-2027/`.

## Lệnh đã chạy và kết quả

Máy sandbox không có `python` trong PATH, nên các lệnh Python dưới đây chạy ngoài sandbox. Tất cả chỉ đọc repo. Ngoài hai file được ghi và file báo cáo này, không ghi gì vào repo.

| Lệnh | Kết quả |
|---|---|
| `python motion/long/factcheck_lint.py ck-g1-tra-no-truoc-han` | **0 lỗi** |
| `script_lines.gate(script_lines.parse(script.md))` (gọi trong Python, không chạy `main` vì `main` ghi `chNN.json`) | **0 lỗi**, không cảnh báo SOURCE_DENSITY |
| Lệnh tự kiểm của GH-179 (regex `wikipedia\|bách khoa\|…\|chương (một…mười)`) | **0** |
| `python scripts/long_gate.py ck-g1-tra-no-truoc-han --min-syl 1900` | Dừng ở "không có chNN.json". Đúng dự kiến vì brief cấm sinh cảnh. Các ngưỡng của cổng đo được bằng tay ở dưới |

Ghi chú về lỗi gate đầu tiên: bản đầu có câu điệp "Lãi lần tới. Phí đã ghi. Tiền còn lại." ba lần, `INT_REPEATED_SENTENCE` chặn khối câu lặp. Đã gộp thành một câu có dấu phẩy và để các câu khác xen giữa.

### Số đo bằng tay (thay cho `long_gate` ở phần chưa có cảnh)

- Âm tiết (đếm theo dấu cách như `script_lines`): **2.228**, trong khoảng 1.900–2.600 của brief. CH00 295 · CH01 243 · CH02 290 · CH03 337 · CH04 360 · CH05 200 · CH06 184 · CH07 319.
- Thời lượng: 2.228 ÷ 210 ≈ 10,6 phút; ÷ 185 ≈ 12 phút. Chữ số như 8.400.000 đếm một âm tiết nhưng đọc dài hơn, nên thời lượng thật nằm ở nửa trên của khoảng 9–12 phút. Cần đo lại sau TTS.
- 167 câu. Câu dài nhất 29 âm tiết (dưới 35). Câu ≤ 6 âm tiết: 11/167.
- URL nguồn trong `factcheck.md`: 10 (≥ 8). Năm trong lời (2016, 2024, 2026) đều có trong `factcheck.md`.
- Tiêu đề đề xuất (từ plan, đếm `len` Python): `Trả 100 Triệu Nợ Nhà Hay Gửi 12 Tháng: Phí Nào Hòa?` = **51** ký tự (≤ 60).
- Phép tính kiểm lại bằng số nguyên: 300.000 / 4.300.000 / 4.900.000 / 9.400.000 trên 100.000.000; 36 tháng 900.000 / 12.900.000. Khớp plan.

## Cách bám plan

- Cold open: bảng NHNN tháng chín, bài đăng 22/10/2026, hai dải, hai góc 300.000 và 4.300.000 đồng, câu kéo "còn sống hay đã mất". Không có tên ngân hàng.
- Lộ trình "Chặng đường": ba chặng trên một dòng hợp đồng (lãi lần tới, phí đã ghi, tiền còn lại). Không có "trả lời ba câu hỏi", không dùng Nghịch lý.
- Ba vòng mở và chỗ đóng: lãi vay nhà có nằm trong 8,4–10,9% không (đóng CH02); pháp luật có trần phí trả trước không (đóng CH03); lãi vay cao hơn thì trả trước có luôn lời hơn không (đóng CH04 bằng góc 0,3 điểm, thêm điều kiện tiền mặt ở CH06).
- Dòng ba ô hiện ở CH00, CH04 (đã điền hai ô, ô tiền còn lại chờ) và CH07. Lời đọc không gọi tên mô-típ.
- Hai điều phải giữ: Điều 103 khoản 1 tách riêng khỏi phí trả sớm (CH03); không nói lãi vay mua nhà được trừ thuế (CH06).
- Kết bài: phép thử "lấy lãi lần tới trừ lãi gửi của bạn, rồi đặt dòng phí cạnh khoảng chênh ấy", câu cách đọc phiếu nói một lần ở CH07, kèm câu miễn trừ. Không có "nên trả" hay "nên gửi".
- Giọng: không đọc tên báo, tên trang, "Wikipedia". Chỉ nêu Ngân hàng Nhà nước, Bộ Xây dựng, Thông tư 39 và các điều luật. Không báo trước số chương.

## Khẳng định không kiểm được hoặc chỉ kiểm mềm

- Tôi không mở lại từng trang nguồn. Nền dữ kiện là các trang đã mở trong bước plan (`GH-181-plan1-report.md`). Trong phiên này chỉ chạy lại hai lượt tìm web: các dải lãi tháng 9/2026 (6,6–8,1; 8,4–10,9; 0,1–0,2; 7,4–8,2; trần 4%) khớp plan; Điều 14 khoản 1 và Điều 16 khoản 1 Thông tư 39 khớp. Nguồn lượt tìm là các trang tổng hợp, nên mức tin cậy là OK-2.
- **Câu 12–14% và 15–16% của Bộ Xây dựng:** file gốc báo cáo chưa mở. Lời đọc nói "một bản tin hồi tháng 8 năm 2026 dẫn báo cáo quý hai của Bộ", không nói đã đọc báo cáo. Không đọc ngày cụ thể vì hai trang cho hai ngày (21/08 trang Bộ, 22/08 CafeBiz). Hình nên ghi nhãn "file gốc chưa mở" như plan.
- **Thông tư 39:** bản đã mở là văn bản gốc 2016. Lời đọc nói rõ điều đó ("các văn bản sau có thể sửa"). Thông tư 29/2026/TT-NHNN chưa mở toàn văn và không được nhắc.
- **Luật 32/2024/QH15 (Điều 100, 102, 103):** lấy từ hai trang tổng hợp, chưa đối chiếu PDF của Quốc hội. Lời đọc diễn đạt lại, không đặt trong ngoặc trích. Điều 14 khoản 1 và Điều 18 khoản 2 Thông tư 39 là hai câu trích nguyên văn tiếng Việt, đọc giọng trích. Điều 16 khoản 1 chỉ diễn đạt lại.
- **Điều 4 khoản 6 (miễn thuế lãi tiền gửi):** trang HTML đã mở; file PDF của văn bản hợp nhất chưa mở.
- **Hai câu không có điều khoản nguồn, nói ở dạng mềm:** (1) "tiền đã trả vào dư nợ không rút lại như sổ tiết kiệm" (CH06); (2) hợp đồng có thể xử lý khoản trả thêm bằng giảm tiền góp hoặc rút ngắn thời hạn (CH05). Cả hai dán nhãn SUY trong `factcheck.md`.
- "Trong các điều ấy không có một mức chung nào" (CH03) chỉ nói về các điều đã mở, không nói pháp luật nói chung.
- Không nhắc video `ck-e2-quy-khan-cap`: chưa rõ video đã có lịch hay chưa. Nếu muốn chỉ sang bài đó thì thêm lúc dựng cảnh, sau khi Lead chốt.
- Hợp đồng vay có thể ghi phí trên gốc khác; lời đọc nói khi đó phiếu này không áp được (CH07), đúng như plan.

## Đề xuất cho mô tả

Câu miễn trừ CK, đặt ở dòng đầu mô tả và trên thẻ cuối:

> Nội dung giáo dục, không phải tư vấn đầu tư.

Gợi ý thêm một câu giới hạn dùng được trong mô tả (không có `<`, `>`, "CẦN", "factcheck", "agent"): "Mọi khoản tiền trong video là ví dụ giả định, tính trên lãi đơn và gốc giữ nguyên trong mười hai tháng; số liệu lãi suất lấy từ bản tin của Ngân hàng Nhà nước về tháng 9/2026, đăng ngày 22/10/2026." Danh sách nguồn công khai lấy từ bảng ở `factcheck.md` (không đưa nguồn nội bộ như trang tổng hợp luật vào mô tả mà chưa hỏi Lead).

## Việc còn mở cho bước sau (không làm trong ticket này)

- Đo lại thời lượng sau TTS: có thể sát 12 phút.
- Dựng cảnh theo plan (hai biểu đồ, dòng hợp đồng ba ô). Khi dựng, nhãn "VÍ DỤ GIẢ ĐỊNH" phải đọc được ở khung 360 px, và hình của câu Bộ Xây dựng phải ghi "file gốc chưa mở".
- Lead cân nhắc: chương CH05 (200 âm tiết) và CH06 (184) ngắn hơn các chương khác. Nếu cần dài hơn thì thêm dữ kiện có nguồn, không thêm câu đệm.
- Đường dẫn clip sheet và thumbnail: chưa có (chưa dựng cảnh, chưa dựng thumbnail).
