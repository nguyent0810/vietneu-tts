# GH-12 · Cổng sàn theo kênh: cổng kỹ thuật chung, cổng nội dung riêng cho MIM/CK (Codex)

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/12. Đọc issue này trước: quyết định của chủ kênh ngày 29/10 nằm ở đó.

## Được ghi

- `motion/long/floor.py`
- `motion/long/build_long.py`: chỉ được sửa `_refuse_floor` và đoạn in `floor` trong `html`
- `motion/long/publish_long.py`: chỉ được sửa đoạn gọi `floor`
- `motion/long/coverage_lint.py`: được import hoặc tái dùng; nếu sửa thì chỉ sửa API, không đổi cách đo
- `tests/test_long_floor.py` (file mới)
- `docs/codex/long-rules.md`: thêm mục "Cổng sàn theo kênh (29/10/2026)"
- báo cáo `docs/pm/tickets/GH-12-report.md`

**Không** sửa `data/long/**`, engine JS, hay ngưỡng của CL.

## Việc

1. **`floor.problems(chapters, channel="CL", topic=None)`**
   - **Mọi kênh** bị chặn khi có cảnh `auto`.
   - **CL**, và mọi spec không ghi `channel`: giữ nguyên các ngưỡng hiện tại.
   - **MIM và CK** dùng cổng nội dung thay cho các ngưỡng CL về âm tiết, số chương, số loại cảnh, số ảnh, số b-roll và nền trống 12%:
     - chữ trên nền trống ≤ 22% thời lượng;
     - chuỗi chữ liên tục ≤ 17 giây.
     - Số đo lấy theo cách của `coverage_lint.py`: biểu đồ, timeline và infographic không tính là chữ nền trống.
     - Cần `timing.json`. Nếu thiếu thì **trượt** với lý do "chưa có timing".
   - Ngưỡng của từng kênh đặt thành hằng số có tên, kèm chú thích lý do theo kênh.
2. **Cổng kỹ thuật chung, áp cho mọi kênh.** Liệt kê trong docstring những gì `build_long.py` và `long_gate.py` đã kiểm sẵn: TTS/timing, asset, `html_lint`, `craft`, nguồn.
   - Không viết lại các kiểm tra đó.
   - Chỉ đảm bảo `render` (bản thật), `final` và `publish` gọi đủ cổng kỹ thuật cho mọi kênh, không miễn kênh nào.
   - Nếu phát hiện thiếu một kiểm tra (ví dụ crop ảnh dọc không có `focus` chỉ được cảnh báo), ghi vào báo cáo dưới dạng đề xuất. **Không tự đổi** cảnh báo thành lỗi.
3. **`build_long.py` và `publish_long.py`** truyền `spec.get("channel", "CL")` và `topic` vào `floor`.
4. **Test hồi quy** `tests/test_long_floor.py`, dùng dữ liệu giả, không đọc file thật:
   - một Long CL giống 6 Long đã đăng thì ĐẠT;
   - một Long CL kiểu sự cố 11/10 thì TRƯỢT (1.500 âm tiết, 94% chữ nền trống, cảnh `auto`);
   - MIM có chữ nền trống 25% thì TRƯỢT; MIM 20% với chuỗi 20 giây thì TRƯỢT; MIM 20% với chuỗi 10 giây thì ĐẠT;
   - MIM có cảnh `auto` thì TRƯỢT;
   - CK áp cùng luật với MIM;
   - spec không có `channel` thì dùng luật CL.
5. **Chạy kiểm tra:**
   - `python -m pytest tests/test_long_floor.py tests/test_long_coverage.py -q`
   - script nhỏ in `floor.problems` cho `mim-jobs-1985`, `mim-macintosh-1984` và `golden`.
   - Ghi kết quả vào báo cáo. **Không render.**

## Báo cáo

Ghi `docs/pm/tickets/GH-12-report.md`, gồm:
- diff tóm tắt;
- kết quả test;
- kết quả `floor` cho 3 topic trên;
- các đề xuất cho cổng kỹ thuật.
