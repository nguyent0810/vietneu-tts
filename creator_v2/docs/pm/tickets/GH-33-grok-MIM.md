# GH-33 · Grok: packaging và factcheck cho pilot tin nóng tuần 45, kênh MIM

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/33. Chủ kênh duyệt 02/11: dựng Short và Long bám sự kiện trong tuần, chuẩn SS-tier, title giật gân, hook cuốn hút, đánh giá sau 1 tuần.

## Đầu vào
- `docs/pm/tickets/GH-31-benchmark.json`: các sự kiện kênh MIM, 31/10–02/11
- `output/trend/2026-11-02/12.md`: báo cáo scanner, phần MIM
- mẫu thắng/thua tuần 44: `docs/pm/2026-11-02-thang-thua-tuan-44.md`
- chuẩn Short: `motion/stier/README.md`; luật 8 điều trong `docs/pm/2026-10-12-shorts-analysis.md` §7
- góc kênh MIM: cơ chế công nghệ, người có tên, hậu trường kỹ thuật

## Được ghi
- `docs/pm/tickets/GH-33-MIM-pack.md`: báo cáo chính
- `docs/pm/tickets/GH-33-MIM-facts.json`: dữ kiện đã kiểm, cho Codex viết spec
- `data/long/<topic>/plan.md` cho đúng 1 đề xuất Long, topic tiền tố `mim-`

**Không:** sửa code, spec hay lịch; render; đọc credentials; commit.

## Việc
1. **Chọn 6 sự kiện cho Short MIM.** Tiêu chí: nóng nhất, còn kịp lên sóng trong 72 h–7 ngày, có tên người hoặc cặp số cho hook, chưa trùng kho (grep `data/stier/specs/`, `data/long/`). Sự kiện chạm cả hai kênh thì giữ góc MIM.
2. **Factcheck từng sự kiện:**
   - ≥ 1 nguồn sơ cấp (văn bản, thông cáo, công bố gốc) và ≥ 1 nguồn độc lập khác tòa soạn, đều mở được;
   - mọi con số, tên, ngày dùng trong title/hook/lời đọc phải trích được từ nguồn (trích ≤ 25 từ, kèm URL);
   - chưa kiểm được thì ghi "CHƯA KIỂM" và không dùng cho hook.
3. **Packaging mỗi Short:**
   - **3 title giật gân nhưng ĐÚNG sự thật:** ≤ 60 ký tự, tiếng Việt có dấu. Không bịa, không phóng đại số, không câu hỏi gây hiểu sai. Kiểu được: số sốc thật, mâu thuẫn thật, nhân vật thật.
   - **Hook 3 s:** câu đầu ≤ 9 từ, có tên người hoặc cặp số; chữ khung đầu ≤ 6 từ, có số.
   - **Dàn ý 6–9 câu đọc:** một insight, kết bằng cú chốt, không CTA, không câu hỏi trong lời đọc.
   - **Loại Short:** S (đứng riêng) hoặc L (dẫn sang Long có thật).
   - **Gợi ý hình:** cảnh dữ liệu, sơ đồ, clip tự do; không ảnh hay clip báo chí có bản quyền.
   - Riêng CK: câu "Nội dung giáo dục, không phải tư vấn đầu tư"; số ví dụ thì ghi VÍ DỤ GIẢ ĐỊNH.
4. **Một đề xuất Long MIM** (10–15 phút; CK 8–13 phút) bám sự kiện lớn nhất tuần. Viết `plan.md` theo mẫu các `data/long/*/plan.md` hiện có: vì sao đề tài này, cold open dữ kiện thật, các vòng lặp mở, 8–10 chương, nguồn chính, 2–3 Short đi kèm. Chủ kênh phải duyệt plan trước khi viết kịch bản.
5. Gửi webhook Grok Bot xin ảnh AI chỉ khi thật cần, theo `scripts/ai_img_request.py`. Có xin thì ghi lại; không bắt buộc.

## Báo cáo `GH-33-MIM-pack.md`
- Bảng 6 Short: sự kiện, title ×3, hook, chữ khung đầu, loại, hạn lên sóng đề xuất
- Bảng nguồn
- Tóm tắt plan Long
- Danh sách CHƯA KIỂM

Ghi rõ đâu là số đo, đâu là suy đoán. Giọng đọc kênh: Thanh Bình (không cần chọn).
