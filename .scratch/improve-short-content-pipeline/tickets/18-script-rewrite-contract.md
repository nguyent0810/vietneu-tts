# 18: Script rewrite contract + deterministic invariant guard

**Spec:** `../spec-2.md`, mục Script rewrite contract (S11). Quyết định: D66, D67, D85.

**What to build:** Khi S8 FAIL trên một Short zodiac có invariant đủ, luồng xử lý như sau:

1. Finding được chuyển thành rewrite contract `{finding, câu cần sửa, invariant}`.
2. Writer viết lại **một lần**, chỉ sửa câu bị chỉ ra.
3. Bản viết lại đi qua deterministic invariant guard: tập token claim (số, can chi, tên, thuật ngữ có trong nguồn) phải giữ nguyên, và không có token số mới.

Kết quả:
- **Qua guard:** chạy lại S7 và hard gate của S1.
- **Vi phạm guard:** ghi là đổi Content và chuyển về Content gate, không coi là Script rewrite.
- **Viết lại thất bại:** Needs review.

Phép so sánh invariant bằng LLM chạy shadow. Không có retry loop, retry count hay feedback loop.

**Blocked by:** 13, 14

**Status:** done (grok review OK)

- [x] Contract chỉ chứa finding, câu cần sửa và invariant; writer được yêu cầu giữ nguyên các câu khác
- [x] Guard là hàm thuần: bắt token số mới, tên bị đổi, can chi bị bỏ, thuật ngữ nguồn bị mất
- [x] Qua guard: chạy lại S7 và hard gate của S1 trước khi dùng
- [x] Vi phạm guard: record ghi "đổi Content", Short về Content gate
- [x] Invariant không đủ: không viết lại, Needs review
- [x] Mỗi finding chỉ có đúng một lần viết lại; thất bại thì Needs review
- [x] So sánh invariant bằng LLM được ghi `shadow: true`, không đổi Gate status
- [x] Record lưu cả script trước và sau khi viết lại, cùng kết quả guard
- [x] Test guard thuần; test luồng qua zodiac với writer giả lập
