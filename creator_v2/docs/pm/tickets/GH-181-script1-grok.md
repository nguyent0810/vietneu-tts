# GH-181: kịch bản Long CK 1 (`ck-g1-tra-no-truoc-han`)

Plan `data/long/ck-g1-tra-no-truoc-han/plan.md` đã được Lead duyệt ngày 06/11.

**Đọc:**
- `CLAUDE.md`, bước 3;
- skill `../.claude/skills/long-script/SKILL.md` và các file `references/`;
- `motion/long/RETENTION.md`;
- kịch bản và factcheck mẫu: `data/long/hoa-than/script.md`, `factcheck.md`. Đây là giọng kể và định dạng mới nhất, đã qua gate;
- một Long CK đã có `script.md`, để làm quen nhịp kênh CK.

**Việc:**
1. Viết `script.md` theo dàn 8 chương của plan:
   - 9–12 phút, khoảng 1.900–2.600 âm tiết (`long_gate` của CK dùng `--min-syl 1900`; xem `scripts/long_gate.py`);
   - lộ trình "Chặng đường" như plan, không dùng "trả lời ba câu hỏi".
2. **Dữ kiện:**
   - mọi số, ngày và văn bản luật phải có trong nguồn đã mở, kèm URL trong bảng nguồn;
   - các số mà báo cáo plan ghi "chưa có nguồn" thì chỉ được dùng khi đã ghi rõ là ví dụ tính toán, trên số tròn của chính phép tính;
   - không nêu tên ngân hàng, không khuyên mua bán hay đầu tư;
   - kết bài là một phép thử để người xem tự áp vào trường hợp của mình.
3. **Giọng:**
   - không đọc tên nguồn trong lời ("Wikipedia", "theo bài báo…"), trừ văn bản luật hay cơ quan có giá trị kể (Thông tư 39, NHNN);
   - không để lọt ghi chú sản xuất;
   - không báo trước cấu trúc chương.
4. Viết `factcheck.md`. Chạy cho tới khi đạt:
   - `factcheck_lint.py ck-g1-tra-no-truoc-han`: 0 lỗi;
   - `script_lines.gate`: 0 lỗi; đọc mục self-check trong `docs/pm/tickets/GH-179-hoathan-script-v2-grok.md`.
5. **Mô tả:** đề xuất câu miễn trừ CK ("Nội dung giáo dục, không phải tư vấn đầu tư.").

**Được ghi:**
- `data/long/ck-g1-tra-no-truoc-han/script.md`;
- `data/long/ck-g1-tra-no-truoc-han/factcheck.md`;
- báo cáo `docs/pm/tickets/GH-181-script1-report.md`.

Ghi UTF-8. Không sinh cảnh, không TTS, không commit.
