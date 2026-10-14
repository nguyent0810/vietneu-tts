Bạn đang rà soát tầng kiểm định schema 2.1 của một pipeline phân tích YouTube.
Phạm vi HẸP. Chỉ trả lời bảy câu hỏi dưới đây. KHÔNG rà soát persistence,
provenance, migration, timeout, subprocess — các vùng đó đã ổn định và không đổi.

Tệp cần đọc (đường dẫn tương đối từ thư mục hiện tại):
  src/lib/cursor/source-ref.ts
  src/lib/cursor/validate.ts
  src/lib/cursor/schema.ts
  src/lib/cursor/prompt.ts
  src/lib/cursor/run.ts   (chỉ hàm detectSemanticDrift)

## Bối cảnh thiết kế

Nguyên tắc: thuật toán tính sự kiện, LLM suy luận trên sự kiện. Mô hình sinh ra
một output JSON; mọi phát biểu nhắc tới impressions / CTR / thumbnail / packaging
phải có ĐÚNG MỘT mục trong `metricClaims`. Ở 2.0 claim SAO CHÉP câu vào trường
`text`; cách đó hỏng vì hai bản văn bản lệch nhau. 2.1 bỏ `text` và thay bằng
`sourceRef {section, itemId, field, ordinal}` — một tham chiếu tới Ô văn bản gốc.
Bộ kiểm định PHÂN GIẢI tham chiếu rồi chạy mọi phép kiểm ngữ nghĩa trên VĂN BẢN
THẬT tại ô đó.

Đơn vị khai báo là Ô: một trường chuỗi, hoặc MỘT PHẦN TỬ của trường mảng.

Nhóm quy tắc:
- R (phân giải, tất định): R1 item phải có thật; R2 field phải là trường văn xuôi;
  R3 ordinal trong phạm vi; R4 itemId duy nhất trong section; R5 section không có
  id thì itemId phải rỗng.
- U (đầy đủ, heuristic ngôn ngữ): U1 mỗi ô tối đa một mệnh đề nhạy cảm; U2 mỗi ô
  đúng một claim trỏ tới; U3 mọi ô nhạy cảm phải có claim; U4 claim không được
  trỏ ô không liên quan chỉ số đã khai.
- S (ngữ nghĩa, heuristic): chủ ngữ có trong ô, tình thái khớp, chiều phán xét
  không ngược, phân cực khớp, ASSERTED về chỉ số phủ 0% bị chặn, CAUSAL cần bằng
  chứng, METHODOLOGY_LIMITATION không được nguỵ trang khẳng định.
- D (bất biến khi SỬA LỖI kỹ thuật, trong detectSemanticDrift): tập id claim
  không đổi; các trường ngữ nghĩa không đổi; danh tính ô `section|itemId|field`
  KHÔNG đổi (chỉ `ordinal` được đổi); văn bản ô được trỏ tới không đổi; số trong
  văn bản đó không đổi.

Một kết quả chỉ ĐẠT khi không còn lỗi mức BLOCKER và không còn lỗi mức HIGH.

## Bảy câu hỏi

1. `resolveSourceRef`: có ca nào PHÂN GIẢI SAI mà vẫn trả về kết quả không? Tức
   ref trỏ tới ô A nhưng hàm trả về nội dung ô B, hoặc trả về ok cho một ref lẽ
   ra phải là lỗi.

2. `buildSourceIndex` (nay là `findDuplicateItemIds` + bảng SECTION_ITEMS /
   SECTION_ROOTS): xử lý `itemId` trùng, `itemId` rỗng, và `section` lạ đã đúng
   chưa? Có section nào trong `claimSourceEnum` mà không bảng nào phủ không?

3. U1 đếm mệnh đề (`clausesOf` + `SENSITIVE_MENTION` trong validate.ts): có cách
   nào NHỒI HAI phát biểu nhạy cảm vào một mệnh đề để chỉ bị đếm là một không?
   Lưu ý: việc `và` KHÔNG phải dấu tách là lựa chọn có ý thức đã ghi trong
   creator_specs/PHASE4_TRUST_BOUNDARIES.md — đừng báo lại nó, hãy tìm ca KHÁC.

4. `enumerateUnits`: có BỀ MẶT VĂN BẢN nào của `cursorOutputSchema` bị bỏ sót,
   tức một ô mà mô hình viết được nhưng không bao giờ bị đòi khai báo?

5. D3/D4 trong `detectSemanticDrift`: có đường nào đổi ĐỒNG THỜI `sourceRef` và
   nội dung ô mà cả hai phép so đều không thấy không?

6. Có đường nào để một lỗi `evidence_support_unverified` (mức HIGH) hay bất kỳ
   lỗi HIGH nào lọt qua và kết quả vẫn được ghi là ĐẠT không?

7. Ràng buộc sinh từ schema (`schemaConstraintLines`, `sourceRefSections` trong
   schema.ts) có phủ `sourceRef` không? Có ràng buộc nào có hiệu lực lúc chạy mà
   prompt không hề nói cho mô hình biết không?

## Cách trả lời

Với mỗi phát hiện, nêu: mức (BLOCKER / HIGH / MEDIUM), tệp và số dòng, và một CA
CỤ THỂ tái hiện được (giá trị đầu vào thật, không phải mô tả chung chung). Nếu
một câu hỏi không tìm ra vấn đề, nói thẳng "không tìm thấy" — đừng bịa ra phát
hiện để lấp chỗ trống.
