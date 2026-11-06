# GH-180 vòng 2: lắp lại cảnh 9 Short CK (hình đang kém)

Lead đã soát contact sheet sau khi render (`output/stier/<slug>/final_sheet.jpg`). **Lời và dữ kiện giữ nguyên. Sửa phần hình.**

**Lỗi:**
1. Con số chính nằm trong thẻ xám "THÔNG TIN" có chữ li ti (ví dụ "LƯƠNG 25 TRIỆU · THƯỞNG 50 TRIỆU", "60% BÌNH QUÂN 6 THÁNG LƯƠNG ĐÓNG"). Trên điện thoại không đọc được.
2. Một ảnh stock (tay cầm tiền) lặp ở rất nhiều khung trong mỗi bài, và lặp qua cả 3 bài đã soát.
3. Ít biểu đồ, ít số lớn.

**Mẫu chuẩn phải làm theo:** `data/stier/specs/ck-e5-luong-25-trieu-thue-giam-13-lan.json` (xem `output/stier/ck-e5-luong-25-trieu-thue-giam-13-lan/final_sheet.jpg`):
- số lớn trong thẻ có nhãn ngắn ("LƯƠNG GỘP / 25 TRIỆU", "BẢN THÂN / 15,5 TRIỆU");
- biểu đồ cột so sánh ("THUẾ MỖI THÁNG": 447,5 và 33,75);
- counter hoặc slam cho con số chốt ("13 LẦN", "≈4,97 TRIỆU");
- ảnh chỉ ở cảnh mở.

Đọc thêm 2–3 spec CK đã đăng có nhiều loại cảnh để chọn đúng kiểu cảnh và tham số.

**Việc:** sửa 9 spec (danh sách trong `docs/pm/tickets/GH-180-specs-report.md`):
- mỗi bài **≥ 5 loại cảnh**, có ít nhất 1 biểu đồ hoặc so sánh số;
- con số chính hiện **cỡ lớn** (giá trị của card, counter hoặc slam), không để trong `sub` hay `note` nhỏ;
- ảnh stock tối đa 1 cảnh mỗi bài, và **không dùng cùng một ảnh cho 2 bài**. Có thể lấy ảnh từ kho chung: `python ../library/tools/assets.py find` với tag `ck`/`tien_bac` (ảnh AI ở `output/asset_library/lib198`, `lib198b`). Ảnh AI đặt `credit: false`;
- giữ `hypo` ở cảnh ví dụ giả định;
- lời đọc **không đổi một chữ**.

Chạy `python motion/stier/build.py --preflight <slug>` cho cả 9 đến khi OK.

**Bắt buộc:**
- sửa spec bằng script Python `json.dump(ensure_ascii=False)`, `encoding="utf-8"`;
- chạy lệnh kiểm mất dấu như ticket trước;
- không render, không commit.

**Báo cáo** `docs/pm/tickets/GH-180-respec-report.md`: mỗi bài ghi loại cảnh trước và sau, ảnh dùng.
