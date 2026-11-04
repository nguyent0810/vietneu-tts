# YCV-ju9q · M1 W1: kịch bản và factcheck cho `mim-jobs-1985`

Long này cũng là bài thử đầu tiên cho hai công cụ mới:
- cổng phủ hình `motion/long/coverage_lint.py`: chỉ chữ ≤ 22%, chuỗi chỉ chữ ≤ 17 giây;
- `motion/long/scene_rules.py`.

Cả hai chạy ở W2. Vòng W1 này chỉ viết lời.

## Phạm vi

**Chỉ ghi 3 file:**
- `data/long/mim-jobs-1985/script.md`
- `data/long/mim-jobs-1985/factcheck.md`
- `docs/pm/tickets/YCV-ju9q-M1-W1-ket-qua.md`

Lệnh `script_lines.py` sẽ tạo thêm các `chNN.json` chứa `lines`. Điều đó chấp nhận được.

**Chỉ đọc:**
1. Ticket này.
2. `docs/codex/long-rules.md`, các mục:
   - "Lỗi đã gặp";
   - "Chiến lược Long 45 ngày";
   - "Áp dụng ngay";
   - "Short đi kèm Long".
3. `docs/codex/long-cheatsheet.md`, mục "Bài học Moneyball".
4. `docs/pm/briefs/2026-10-28-content-brief-mim-0112.md`, mục M1 và mục "Sửa sau bước R", phần M1.
5. `data/long/mim-jobs-1985/research.md`. Đây là kho đã duyệt.
   - **Chỉ dùng dữ kiện trong kho.**
   - Dữ kiện ghi [SECONDARY] hoặc "theo …" phải quy dẫn ngay trong câu đọc.
   - Dữ kiện ghi CHƯA KIỂM ĐƯỢC thì không dùng.
6. Mẫu định dạng: CH00 và CH01 của `data/long/mim-moneyball/script.md`.

Không grep repo, không đọc code.

## Quyết định cho các câu hỏi mở trong research §7 (Claude chốt)

1. Mốc quyết định: nói "tháng 4/1985, hội đồng quản trị chọn Sculley". Không đọc ngày 10–11/4. Cuối tháng 5, Jobs mất quyền điều hành. Ngày từ chức: đọc "tháng 9/1985" hoặc "giữa tháng 9"; trên màn hình được ghi 17/9/1985.
2. **Câu đầu tiên** là sự kiện có thời điểm, ví dụ: "Tháng 9 năm 1985, người lập ra Apple nộp đơn rời Apple." Không mở bằng lời trích. Câu "at 30 I was out" của Jobs dùng ở CH01 hoặc ở phần kết, gắn [TRÍCH DỊCH] và ghi rõ là bài nói ở Stanford năm 2005.
3. Vụ Apple kiện NeXT: được nói một câu, kèm "theo tư liệu tổng hợp".
4. Kết nối với hiện tại: một câu, không nêu vụ cụ thể nào.
5. Con số cho Apple 1996–97: lỗ ròng 1.045 triệu USD năm tài chính 1997, theo báo cáo năm của Apple.

## Yêu cầu

- **Tiêu đề:** dòng 1 của `script.md`, tối đa 60 ký tự, đúng một dấu `:`.
  - Chọn hoặc sửa từ ba tiêu đề trong brief.
  - Nếu tiêu đề có 427 triệu thì lời đọc phải nói đó là tổng giá mua theo báo cáo năm. Lúc công bố, Apple nói 400 triệu.
- **Độ dài:** 9 chương (CH00–CH08), **2.500–2.800 âm tiết**, khoảng 12 phút.
- **Cấu trúc theo chiến lược 45 ngày:**
  - 0–30 giây là hook: sự thật, nghịch lý, câu hỏi trung tâm;
  - tới phút 2 là bối cảnh;
  - cứ 3–5 phút có một bước tiến mới của lập luận;
  - phần kết trả lời đúng câu hỏi trung tâm.
  - Theo 7 nhịp trong research §3.
- **Mô-típ:** một mô-típ, mỗi chương thêm một dòng. Phải khác "sáu răng", "sổ một con số", "tấm bảng lên gôn" và mô-típ của `mim-social-network`.
- **Người thật còn sống** (Sculley, các thành viên hội đồng quản trị):
  - chỉ kể sự kiện có nguồn;
  - không suy diễn động cơ;
  - lời trích lấy đúng nguồn trong kho, gắn [TRÍCH DỊCH].
- **Chữ "đuổi":**
  - lời đọc tách rõ hai việc: "bị tước quyền điều hành" và "tự nộp đơn từ chức";
  - chữ "fired" chỉ dùng khi đó là lời chính Jobs, có quy dẫn.
- **Viết cho tai:**
  - câu một hơi, nói với "bạn";
  - thuật ngữ (hội đồng quản trị, CEO tạm quyền, báo cáo năm 10-K…) giải thích ngay lần đầu xuất hiện;
  - không câu đệm.
- **Đánh dấu chỗ có hình (mới, để thử cổng phủ hình).** Cuối mỗi chương, thêm một dòng bắt đầu bằng `> HÌNH:`.
  - Liệt kê các câu nên đi với ảnh tư liệu: dùng các file PD/CC BY trong research §4.
  - Liệt kê các câu cần ảnh AI theo luật người thật: dáng gốc, góc nghiêng hoặc quay lưng.
  - Mỗi câu ghi chỉ số câu và một cụm mô tả hình.
  - Mục tiêu: không đoạn nào quá 17 giây chỉ có chữ.
  - Dòng `>` không được đọc thành tiếng. Nếu `script_lines.py` coi dòng `>` là lời đọc thì chuyển phần này sang mục "HÌNH" trong `factcheck.md`, và ghi lại việc đó trong báo cáo.
- **Short S/L:** ghi 2–3 phương án ở cuối `factcheck.md`, lấy từ research §8, đã sửa theo "Sửa sau bước R".
- **`factcheck.md`:**
  - mỗi khẳng định có số, ngày hoặc tên: một dòng kèm URL và số # trong research;
  - mọi năm có trong kịch bản đều phải xuất hiện.

## Cổng (bắt buộc trong vòng này)

1. Chạy:
   ```
   PYTHONIOENCODING=utf-8 python motion/long/script_lines.py mim-jobs-1985
   ```
   Phải qua integrity. Ghi số âm tiết in ra.
2. Chạy:
   ```
   PYTHONIOENCODING=utf-8 python motion/long/studio_lint.py mim-jobs-1985 --strict
   ```
   - Gặp lỗi "câu > 35 tiếng" thì tách câu trong `script.md`, rồi chạy lại bước 1 và 2.
   - Lặp tới khi còn **0 lỗi**. Cảnh báo không cần sửa.

## Báo cáo

Ghi vào `YCV-ju9q-M1-W1-ket-qua.md`:
- tiêu đề, số âm tiết, mô-típ;
- số dữ kiện dùng ở từng chương;
- kết quả `studio_lint`;
- số câu đã đánh dấu ảnh tư liệu và số câu cần ảnh AI;
- các chỗ lệch so với brief.

Không render, không đăng, không commit.
