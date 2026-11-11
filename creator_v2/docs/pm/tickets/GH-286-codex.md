# GH-286: lint mạch kể Long và script review câu chuyện (Codex)

Đọc issue: `gh issue view 286 --repo nguyent0810/vietneu-tts`. Lead đã viết phần tài liệu: `docs/pm/storytelling-guide.md` §13, `docs/pm/prompts/long-story-review.md` và quy trình bước 3 trong `CLAUDE.md`. Đọc §13 trước khi làm. Bạn làm phần code.

## Môi trường
- Worktree `D:\Tools\Youtube Creator v2\wt-286`, nhánh `feat/286`. Đường dẫn tính từ `creator_v2/`.
- Python: `"D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe"`.
- Pytest: `--basetemp=tmp_pytest -p no:cacheprovider`. Bộ gốc có 7 test đỏ do thiếu `vnlunar`, bỏ qua. Gặp lỗi quyền khi dọn thư mục tạm thì ghi lại và **làm tiếp, không dừng**.
- Dữ liệu thật (chỉ đọc): `data/long/mata-hari/script.md`, chương `## CH03 · Đông Ấn Hà Lan` (dòng 126–166), và `data/long/mata-hari/factcheck.md`.
- Sandbox của bạn không có mạng và không SSH được. Script review phải test bằng mock subprocess.

## File được sửa (Lead cho phép đích danh)
1. `motion/long/script_lines.py`: thêm hàm `flow_warnings(chs) -> list[tuple[code, chương, chỉ số câu, ghi chú]]`, gọi trong `gate()` bằng `warnings.warn` (theo kiểu `SOURCE_DENSITY` có sẵn). **Chỉ cảnh báo, không chặn, không đổi kết quả ghi chNN.json.**
   - `RAO_NGUON`: từ 3 câu trở lên nói về nguồn hay độ tin cậy trong 8 câu liền nhau. Từ khóa gợi ý: "được kể lại", "lời kể", "tài liệu", "nguồn", "ta chỉ có thể", "không chắc", "theo hồ sơ", "người kể". Để danh sách thành hằng số ở đầu file.
   - `NHIP_DEU`: từ 5 câu liền nhau, mỗi câu dưới 9 tiếng (âm tiết).
   - `NHAY_MOC`: trong một chương, một năm (4 chữ số, 1000–2099) lớn hơn năm sớm nhất của chương quá 10 năm, xuất hiện trước 3 câu cuối của chương. Năm sớm nhất lấy từ tên chương nếu có, nếu không thì từ năm đầu tiên trong chương. **Bỏ qua** CH00 (cold open) và chương cuối (kết).
   - `META_NGUOI_KE`: câu bắt đầu hoặc chứa "ta phải", "ta giữ", "ta chỉ có thể", "chúng ta phải", "phải nói chậm".
2. File mới `scripts/long_story_review.py <topic> [chNN …] [--agent c|local|grok] [--dry-run]`:
   - Đọc `data/long/<topic>/script.md`, tách chương bằng `script_lines.parse` (đừng viết parser mới).
   - Với mỗi chương: ghép prompt theo `docs/pm/prompts/long-story-review.md`. Lấy nguyên văn khối `text` từ file đó, không chép cứng prompt trong code. Thêm tên chương, câu cuối chương trước, câu đầu chương sau, các câu đánh số, `factcheck.md` (cắt tối đa 12.000 ký tự) và yêu cầu 3 mục đầu ra.
   - Ghi kết quả `data/long/<topic>/story_review/chNN.md`, đầu file ghi agent, model, ngày.
   - Thứ tự agent, chuyển khi lỗi hoặc đầu ra rỗng:
     - **`c`**: máy C qua SSH. `ssh -o BatchMode=yes -o ConnectTimeout=15 -l "du bi" 100.65.218.98 "agy --model gemini-4-argon-high --input-format stream-json --output-format stream-json --print-timeout 1800s \"-p=\""`. Prompt đi qua **stdin** dạng một dòng JSON `{"event":"user","message":{"role":"user","content":<prompt>}}`. Lấy dòng `"event":"result"` cuối, `result.status == "SUCCESS"` thì dùng `result.response`. Cách làm đúng y như `../scripts/agents/agy_c.sh` (bản zsh): đọc file đó để chép logic sang Python.
     - **`local`**: `agy -p` trên máy này, model `gemini-4-argon-high`, prompt cũng qua stream-json stdin.
     - **`grok`**: `grok -p` (chỉ khi hai agent trên hỏng).
   - `--dry-run`: chỉ ghi prompt ra `story_review/chNN.prompt.md`, không gọi agent. Dùng cho test.
   - Không in biến môi trường, không đọc thư mục credentials.
3. `motion/long/build_long.py`: chỉ thêm cảnh báo (không chặn) ở bước `tts` khi topic **không** thuộc legacy (`is_legacy_topic`) và thiếu `story_review/chNN.md` cho một chương bất kỳ.
4. Test mới `tests/test_flow_lint.py` và `tests/test_long_story_review.py`.
5. `motion/long/README.md`: một đoạn ngắn về bước review và 4 cảnh báo.

## Tiêu chí đạt
- Lint trên CH03 Mata Hari thật bắt được ít nhất `RAO_NGUON` (vùng câu 9–15), `NHIP_DEU` (vùng câu 3–7), `NHAY_MOC` (câu nhắc 1919). Test đọc file thật và kiểm 3 mã này. Kèm test âm: một đoạn kể mạch lạc, nhịp xen kẽ không bị báo.
- Chạy lint trên cả `golden` (chuẩn): in số cảnh báo theo mã vào báo cáo. Nếu golden bị báo nhiều (hơn 1 cảnh báo mỗi chương trung bình), chỉnh ngưỡng cho tới khi Mata Hari ch03 vẫn bị bắt mà golden ít bị báo, và ghi lại lý do.
- `long_story_review.py mata-hari ch03 --dry-run` ra file prompt đúng dạng. Test mock subprocess cho chuỗi chuyển agent: c lỗi thì local, local lỗi thì grok.
- `pytest tests/test_flow_lint.py tests/test_long_story_review.py tests/test_long_defaults.py` xanh.

## Báo cáo
Ghi `docs/pm/tickets/GH-286-report.md` bằng Python utf-8, tiếng Việt có dấu. Gồm: cảnh báo trên Mata Hari ch03 (mã, câu), số cảnh báo trên golden, kết quả test, lệnh để Lead chạy thật trên máy C.

Không commit, không đăng, không gọi agent thật. **Phải làm đủ cả 5 mục. Dừng giữa chừng tính là hỏng.**
