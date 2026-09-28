# 11: S8 Toàn vẹn văn bản (deterministic)

**Spec:** `../spec-2.md`, mục Toàn vẹn văn bản (S8). Quyết định: D62, D68, D88, D91.

**What to build:** Một hàm thuần nhận script và trả về danh sách finding `{loại, câu/span, vị trí, chặn}` kèm reason code `SCR_`. Hàm kiểm trên **text sẽ thật sự được đọc**, tức là sau khi đã bỏ `**` và emotion tag bằng đúng hàm strip mà bước render đang dùng (dùng lại hàm đó, không viết bản sao).

Các loại finding:
- **Chặn:** câu lặp (nguyên văn, và sau khi chuẩn hoá bằng cách hạ chữ, bỏ dấu câu); markup hoặc ký hiệu còn sót (dấu sao lẻ, ngoặc vuông, `#`, `*** N`, nhãn "Phương án", mảnh JSON, URL).
- **Không chặn:** câu cuối thiếu dấu kết câu.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Dùng lại chính hàm strip `**` và emotion tag của bước render. Emotion tag hợp lệ đã bị strip không bị tính là lỗi
- [ ] Bắt câu lặp nguyên văn và câu lặp sau khi chuẩn hoá; evidence gồm các câu lặp và vị trí của chúng
- [ ] Bắt markup hoặc ký hiệu còn sót, evidence là span
- [ ] Câu cuối thiếu dấu kết câu là finding `chặn = false`, reason code `SCR_TRUNCATED`
- [ ] Reason code thuộc tập đóng `SCR_` (`SCR_REPEATED_SENTENCE`, `SCR_LEFTOVER_MARKUP`, `SCR_TRUNCATED`)
- [ ] Có ít nhất một finding chặn thì kết quả là FAIL; chỉ có finding không chặn thì không FAIL
- [ ] Có test case "lặp một câu 3 lần", test script sạch, test `**` lẻ và test emotion tag hợp lệ
- [ ] Hàm thuần, không phụ thuộc khoá chỉ có trên Unix, chạy được trên Windows
