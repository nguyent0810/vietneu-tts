# GH-181: plan Long CK 2, "Bảo hiểm liên kết đầu tư: hủy hay đóng tiếp?"

**Đọc:**
- `CLAUDE.md` (quy trình Long, bước 1);
- báo cáo đề tài `docs/pm/tickets/GH-181-topics-report.md`, đề 2;
- plan mẫu của một Long CK đã thắng: `data/long/ck-b1-mua-hay-thue/plan.md` (Trả góp 19 triệu hay thuê 6 triệu, Long CK tốt nhất);
- `motion/long/RETENTION.md`.

Long CK dài 8–13 phút.

**Việc:** viết `data/long/ck-g2-bao-hiem-lien-ket/plan.md`:
1. **Câu mở bằng sự kiện hoặc con số thật có ngày và nguồn chính thức.** Ví dụ: mức lãi cho vay mua nhà sau ưu đãi do NHNN hay các báo cáo công bố, kèm tháng và năm. **Không dùng** con số minh họa của báo cáo đề tài (11,2%, phí 1,5%) nếu không có nguồn đã mở. Con số nào là ví dụ tính toán thì ghi rõ "ví dụ".
2. **Dữ liệu và cách tính:**
   - lãi vay thả nổi thực tế, lãi tiết kiệm 12 tháng, khung phí trả nợ trước hạn theo Thông tư 39/2016 và Luật Các TCTD 2024 (mở văn bản thật, trích điều khoản);
   - giai đoạn so sánh, công thức, các giả định, giới hạn.
3. **Xương sống A → B:**
   - cold open;
   - 3 vòng mở;
   - dàn 6–9 chương;
   - 2 biểu đồ chính (dữ liệu nào, trục gì);
   - một quyết định cuối cho người xem tự áp, không khuyên đầu tư.
4. **Tiêu đề:** 2–3 tiêu đề ≤ 60 ký tự (giới hạn của kênh CK), dạng một quyết định thật, kèm 1–2 chữ thumbnail.
5. 2–3 Short loại L nối về Long.
6. Rủi ro:
   - không nêu tên ngân hàng;
   - không khuyên mua bán;
   - mô tả có câu miễn trừ của CK.

**Được ghi:** `data/long/ck-g2-bao-hiem-lien-ket/plan.md` và báo cáo `docs/pm/tickets/GH-181-plan2-report.md` (UTF-8). Báo cáo gồm URL đã mở và các số còn chưa có nguồn. Không viết script, không commit.

**Riêng đề 2 (Lead, 07/11):**
- Dữ liệu chính thức: Luật Kinh doanh bảo hiểm 2022, Thông tư 67/2023/TT-BTC (quy định tư vấn, thời gian cân nhắc 21 ngày), số liệu Bộ Tài chính / Hiệp hội Bảo hiểm về hợp đồng liên kết đầu tư và khiếu nại.
- **Không nêu tên công ty bảo hiểm.** Không kết luận "nên hủy" hay "nên đóng". Đưa ra phép tính để người xem tự áp: giá trị hoàn lại, phí ban đầu, phí rủi ro.
- Viết tiếp kịch bản `script.md` và `factcheck.md` ngay sau plan, theo mẫu `data/long/ck-g1-tra-no-truoc-han/` đã duyệt: 1.900–2.600 âm tiết, `factcheck_lint` 0 lỗi, gate 0 lỗi.
