# GH-31 · Codex vòng sửa 6 P0: chặn gom quá đà theo thực thể chung, siết luật khớp benchmark

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/31. Vòng trước: `docs/pm/tickets/GH-31-fix5-report.md`.

## Lead soát tay (02/11)
Soát cặp khớp tốt nhất của từng sự kiện được tính là bắt được. Recall báo cáo (MIM 12/18, CK 8/20) bị thổi phồng.

**MIM.** Đúng: `mim_03`, `mim_05`, `mim_10`, có thể cả `mim_09` (qua event "Alphabet mất 500 tỷ"). Sai: `mim_04`, `mim_06`, `mim_07`, `mim_08`, `mim_12`, `mim_13`, `mim_15`, `mim_17`. Ví dụ:
- `mim_06` (Musk cảnh báo AI agent) khớp với event "google" (vệ tinh AI);
- `mim_04` (iPhone Duo bản lề) khớp với "Apple cập nhật bảo mật".

**CK.** Đúng: `ck_01`, `ck_02`, `ck_03`, `ck_04`, `ck_09`, `ck_10`. Sai: `ck_07` ("Tổng lực giảm chi phí"), `ck_14` ("Báo Thái Lan…").

Ước tính recall ứng viên thật: MIM khoảng 4/18, CK 6/20.

**Hai nguyên nhân:**
1. **Gom quá đà.** Event `google` và `3 000 ty · lg electronics` hút nhiều bài không liên quan. Chỉ một thực thể chung (Google, Apple, Samsung, OpenAI, "3.000 tỷ") đã đủ nối bài.
2. **Luật khớp lỏng.** Nhánh thực thể chấp nhận một thực thể chung + 1 token bất kỳ.

## Được ghi
- `factory/trend/cluster.py`, `benchmark.py`, `keywords.json`
- test, fixture
- báo cáo `docs/pm/tickets/GH-31-fix6-report.md`

**Không:** thêm nguồn, sửa benchmark JSON, commit.

## Việc
1. **Thực thể chung.** Lập danh sách `generic_entities`: các hãng lớn, số tiền trơn, từ chung kiểu "ngân hàng", "chứng khoán". Mở rộng danh sách tự động: thực thể nào xuất hiện ở > 5% số bài trong cửa sổ cũng tính là chung.
   - Gom sự kiện: hai bài chỉ chung thực thể chung thì không được nối. Cần thêm ≥ 1 thực thể đặc thù, hoặc Jaccard tiêu đề ≥ 0,35.
   - Chống chuỗi bắc cầu: một event có độ tương đồng nội bộ trung bình thấp thì tách ra. Gợi ý: kiểm từng bài với tâm cụm (centroid).
2. **Luật khớp benchmark.** Nhánh thực thể chỉ tính thực thể đặc thù, không tính thực thể chung. Cần ≥ 2 token nội dung của nhãn benchmark xuất hiện trong tiêu đề, ngoài thực thể. Nhánh Jaccard giữ ngưỡng 0,25.
3. **Kiểm tra bằng nhãn tay của Lead:** cặp đúng/sai ở trên thành test hồi quy trên dữ liệu đã lưu, hoặc fixture trích từ đó. Các ca đúng phải còn khớp, các ca sai không được khớp. Không chỉnh luật riêng cho từng ca. Luật phải chung, ghi rõ trong báo cáo.
4. Cluster lại trên dữ liệu đã lưu, chạy `report` và `benchmark`. Báo cáo gồm:
   - 4 số mỗi kênh;
   - 2 loại recall;
   - 10 event lớn nhất (số bài) kèm 3 tiêu đề mỗi event, để Lead kiểm còn gom quá đà không;
   - 10 cặp khớp điểm thấp nhất.

## Báo cáo
Thay đổi, test, bảng trước/sau, kiểm gom quá đà.
