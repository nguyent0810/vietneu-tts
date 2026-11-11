# Báo cáo GH-291

## Trạng thái: chưa hoàn tất

Đã làm các mục trong vùng ghi `creator_v2`. Còn thiếu mục sửa `../scripts/agents/agy_c.sh`: file nằm ngoài root được phép ghi của phiên (`D:\Tools\Youtube Creator v2\wt-291\creator_v2`), trong khi chính sách sandbox không cho xin thêm quyền. Không sửa file ngoài vùng ghi. Bộ kiểm đầy đủ cũng chưa xanh vì lỗi quyền thư mục tạm như dưới đây. Lead cần áp dụng thay đổi script Mac và chạy lại bộ kiểm trong môi trường có quyền ghi thư mục tạm.

## Đã làm

- `scripts/long_story_review.py`: thêm `NO_SHELL` cho `c` và `local`; tách `ask(agent, prompt)` và giữ `run_agent` làm lớp gọi tương thích; nếu kết quả rỗng có `denied_actions`, báo tên action cả khi status không thành công. Khi mọi agent thất bại, thông tin action vẫn xuất hiện trong lỗi tổng hợp.
- `scripts/plan_sources.py`: đọc URL và số cùng dòng trong plan; tải qua urllib với timeout 20 giây và user-agent yêu cầu; đánh dấu trạng thái, số thiếu và lỗi không mở được. Đếm file Commons trực tiếp và một cấp category con qua API có phân trang, loại file trùng. `--write` thêm khối mới vào đầu, giữ nguyên nội dung cũ và bỏ qua các khối kiểm cũ khi lấy URL. URL lỗi, thiếu số, không mở được hoặc đếm Commons thất bại cho mã thoát khác 0; `CHAN` không tự coi là đã xác minh.
- `tests/test_plan_sources.py`, `tests/test_long_story_review.py`: mock mạng và subprocess, bao gồm dữ liệu bảng từ plan mẫu, trang lỗi, số thiếu, status HTTP, API Commons phân trang/trùng file, ghi plan, `NO_SHELL`, action bị từ chối và fallback. Dòng chứa URL trong plan mẫu không có số 14.384.902, nên test bổ sung số vào chính dòng này để kiểm đúng quy tắc cùng dòng.
- `CLAUDE.md`: bổ sung câu yêu cầu kiểm plan, model mạnh và đếm Commons ở bước 1.

## Kiểm tra và giới hạn

- Đã đọc issue bằng `gh issue view 291 --repo nguyent0810/vietneu-tts`.
- Chạy lệnh yêu cầu với Python theo brief: `python -m pytest tests/test_plan_sources.py tests/test_long_story_review.py tests/test_console.py --basetemp=tmp_pytest -p no:cacheprovider`. Pytest gặp `PermissionError: [WinError 5]` trên thư mục tạm `tmp_pytest`, kể cả lúc kết thúc. Chạy lại với basetemp mới cũng gặp lỗi quyền tương tự.
- Chạy lại qua `pytest.main` với một điều chỉnh chỉ trong tiến trình kiểm thử: đổi `Path.mkdir(mode=0o700)` thành `0o777` và dùng basetemp mới. Trước thay đổi test cuối: 19 đạt, 2 lỗi trong `test_console.py` vì tiến trình con `qa_blank.py` tạo thư mục tạm mặc định, `ffmpeg` không ghi được và dọn dẹp trả `WinError 5`. Không sửa code dùng chung để né lỗi môi trường.
- Sau thay đổi cuối, chạy lại cùng cách và loại hai trường hợp `test_qa_blank_cli_prints_vietnamese_on_cp1252_console`: **22 đạt, 2 không chạy**. Do đó chưa thể báo bộ yêu cầu xanh đầy đủ.
- `zsh` không có trong PATH; chưa chạy `zsh -n`. Chưa chạy gọi mạng thật, API Commons thật hoặc máy C; các trường hợp đó mới kiểm bằng mock. Chưa xác minh hai URL thực tế của plan CK bài 10. Không có clip sheet hay thumbnail vì đây là ticket code.
- Phép kiểm số là phép so chuỗi số cùng dòng, bỏ dấu chấm/phẩy khi so. Số thứ tự bảng, ngày và số hiệu cũng có thể bị coi là số cần kiểm; kết quả `KHONG_CHUA_SO` cần người đọc đối chiếu, còn `OK` không chứng minh khẳng định đúng ngữ cảnh.

## Thay đổi còn chờ cho script Mac

Trong `../scripts/agents/agy_c.sh`, ở đoạn Python tạo stream JSON, thay phần `content` bằng biến sau rồi dùng biến đó cho `content`:

```python
no_shell = "KHÔNG chạy lệnh shell (run_command bị cấm và sẽ làm hỏng phiên). Chỉ dùng công cụ tìm kiếm và đọc web có sẵn. URL nào không mở được thì ghi 'không mở được'."
prompt = no_shell + "\n\n" + open(sys.argv[1], encoding="utf-8").read()
```

Trong Python xử lý `result`, trước kiểm tra `status`, lấy response, nếu response rỗng sau `strip()` và `denied_actions` có dữ liệu thì ghi lỗi kèm `json.dumps(r["denied_actions"], ensure_ascii=False)` ra stderr và thoát khác 0. Sau đó giữ kiểm tra status, và cũng nên báo lỗi cho response rỗng thông thường. Kiểm tra cú pháp bằng `zsh -n ../scripts/agents/agy_c.sh` trên máy có zsh.

Không đăng, không commit, không đổi lịch.
