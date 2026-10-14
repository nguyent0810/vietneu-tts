Rà soát ĐỐI KHÁNG một thay đổi DUY NHẤT. Phạm vi rất hẹp — đừng rà soát gì khác.

Tệp: `src/lib/cursor/validate.ts`, chỉ phần bộ tách mệnh đề:
`clausesOf`, `CLAUSE_SEPARATOR`, `isSingleStatementRun`, `maskParentheticals`,
`LIST_COORD_INITIAL`, `LIST_COORD_ANY`, `NEW_CLAUSE_INITIAL`, `FRONTED_ADJUNCT`,
`JUDGEMENT_ANY`, và chỗ DUY NHẤT gọi `clausesOf` cho quy tắc U1
(tìm `multiple_assertions_in_source_unit`).

Test đi kèm: `tests/unit/cursor-clause-split.test.ts`.

## Vai trò của mã này

`clausesOf` tách một Ô văn bản thành các mệnh đề. Quy tắc U1 đếm số mệnh đề CHẠM
tới chỉ số nhạy cảm (impressions / CTR / thumbnail / packaging) và CHẶN nếu > 1,
với thông điệp "ô này chứa nhiều phát biểu, phải tách thành nhiều phần tử".

Vì vậy có HAI hướng hỏng, và cả hai đều tốn:
- tách QUÁ TAY  -> chặn oan một ô hoàn toàn hợp lệ;
- tách THIẾU    -> hai khẳng định về hai chỉ số lọt qua dưới một bản khai duy
  nhất, nghĩa là một phát biểu không ai kiểm.

## Thay đổi vừa làm

Trước đây mọi dấu phẩy đều là ranh giới mệnh đề. Nay một CHUỖI mảnh nối bằng dấu
phẩy được gộp lại thành MỘT mệnh đề khi:
- một mảnh (không phải mảnh đầu) MỞ ĐẦU bằng `và`/`hay`/`hoặc`; hoặc
- một mảnh như thế CHỨA `và`/`hay`/`hoặc` mà KHÔNG mang dấu hiệu phán xét nào
  (`JUDGEMENT_ANY`); hoặc
- mảnh ĐẦU mở đầu bằng trạng ngữ (`nếu`, `khi có`, `sau khi`, …).

Mảnh mở đầu bằng liên từ đối lập/nhân quả (`nhưng`, `tuy nhiên`, `do đó`, …) luôn
cắt ngang phép gộp. Ngoài ra: dấu chấm đứng trước chữ số không kết câu
(`\.(?!\d)`, cho "1.000" và "0.7262"), và cụm trong ngoặc đơn được che trước khi
tách.

Cơ sở: quét 517 ô THẬT từ 74 lần chạy đã lưu trong database. Trước khi sửa, dấu
phẩy làm đổi kết quả U1 ở 25 ô và cả 25 đều là tách SAI. Sau khi sửa: 0.

## Câu hỏi

1. **Tách THIẾU.** Dựng một ô chứa HAI khẳng định nhạy cảm THẬT về hai chỉ số
   khác nhau mà `clausesOf` nay gộp thành một, tức U1 không còn chặn. Đây là câu
   hỏi quan trọng nhất — mọi phép gộp mới đều là một lỗ tiềm năng.

2. `JUDGEMENT_ANY` có đủ để phân biệt "mục liệt kê" với "một phát biểu" không?
   Nêu một phát biểu thật về chỉ số nhạy cảm mà KHÔNG chứa từ nào trong đó, và
   nằm sau dấu phẩy cùng một liên từ liệt kê.

3. `LIST_COORD_ANY` = `/(?:^|\s)(?:và|hay|hoặc)(?=\s)/iu`. Có chuỗi nào khớp nhầm
   không (ví dụ "hay" trong "hay thay đổi", "hoặc" trong một danh từ ghép)? Có
   biên nào là NHÁNH CHẾT vì chữ có dấu không?

4. `maskParentheticals` thay cụm ngoặc bằng ` <số> `. Có văn bản nào khiến phép
   khôi phục trả lại SAI, hoặc khiến một số có sẵn trong câu bị hiểu nhầm thành
   placeholder không? Ngoặc lồng nhau, ngoặc thiếu vế đóng thì sao?

5. `\.(?!\d)` có làm mất ranh giới câu THẬT nào không (ví dụ một câu kết thúc
   bằng dấu chấm rồi câu sau mở đầu bằng chữ số)?

6. Việc đọc `seps[j]` để biết ranh giới có phải dấu phẩy — chỉ số có lệch pha
   trong ca nào không (mảnh rỗng, dấu phân cách liên tiếp, chuỗi mở đầu hoặc kết
   thúc bằng dấu phân cách)?

7. `clausesOf` còn được dùng ở quy tắc phân cực S4. Thay đổi này có làm S4 nhìn
   vào một mệnh đề RỘNG HƠN và bỏ lọt một phép đảo chiều không?

## Cách trả lời

Mỗi phát hiện: mức (BLOCKER / HIGH / MEDIUM), số dòng, và một CHUỖI ĐẦU VÀO cụ
thể tái hiện được kèm kết quả `clausesOf` mong đợi so với thực tế. Không tìm thấy
thì nói thẳng "không tìm thấy" — đừng bịa cho đủ mục.
