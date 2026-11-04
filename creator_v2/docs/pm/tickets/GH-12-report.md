# GH-12 · Báo cáo Codex

## Đã làm

- `motion/long/floor.py`: thêm `problems(chapters, channel="CL", topic=None)`.
  - Cảnh `auto` vẫn chặn mọi kênh.
  - CL và spec không có `channel` giữ nguyên toàn bộ ngưỡng sàn CL cũ.
  - MIM/CK dùng số đo thời lượng của `coverage_lint`: chữ nền trống tối đa 22% và chuỗi liên tục tối đa 17 giây; thiếu `topic` hoặc `timing.json` báo `chưa có timing` và trượt.
  - Thêm hằng số có tên cho ngưỡng MIM/CK, chú thích lý do khác với sàn sáu Long CL dài đã đăng, và docstring nêu rõ các cổng kỹ thuật hiện hữu không bị viết lại.
- `motion/long/build_long.py`: `_refuse_floor` và phần in `html` truyền `spec.get("channel", "CL")` cùng `topic` vào floor. Vì render bản thật và final đều đi qua `_refuse_floor`, chúng dùng đúng sàn theo kênh.
- `motion/long/publish_long.py`: truyền channel/topic khi gọi floor.
- `tests/test_long_floor.py`: thêm fixture giả, không đọc dữ liệu Long thật; phủ sàn CL, sự cố 11/10, MIM/CK, `auto`, thiếu timing và spec mặc định CL.
- `docs/codex/long-rules.md`: bổ sung mục **Cổng sàn theo kênh (29/10/2026)**.

Không render, không đăng, không sửa lịch hay trạng thái SQLite.

## Kiểm tra đã chạy

```text
python -m pytest tests/test_long_floor.py tests/test_long_coverage.py -q
13 passed, 1 warning in 0.17s
```

Cảnh báo còn lại: pytest không ghi được `.pytest_cache` vì quyền thư mục; không có lỗi test hay lỗi lint từ lệnh được ticket yêu cầu.

Script đọc-only kiểm `floor.problems` cho các topic:

```text
mim-jobs-1985 (MIM): ĐẠT
mim-macintosh-1984 (MIM): TRƯỢT
  chữ nền trống 32.07% > 22%
  chuỗi chữ nền trống 23.92s > 17s
golden (CL): ĐẠT
```

## Đề xuất cổng kỹ thuật (không tự đổi trong ticket này)

- `scripts/long_gate.py` hiện chỉ cảnh báo ảnh dọc thiếu `focus`; nên giữ hành vi hiện tại trong đợt này, rồi quyết định riêng có nâng thành lỗi chặn sau khi rà các Long cũ hay không.
- `audio_lint` ở bước final hiện chỉ chặn lỗi âm thanh cho CL, còn MIM/CK báo cảnh báo. Nếu chủ kênh muốn cổng kỹ thuật hoàn toàn không có ngoại lệ theo kênh, cần ticket riêng để thống nhất ngưỡng và nâng hành vi này; GH-12 không cho phép sửa đoạn đó.
