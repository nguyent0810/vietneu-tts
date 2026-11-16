# Báo cáo GH-278

## Trạng thái

Đã triển khai và kiểm thử bằng metadata/fetch giả, nhưng **chưa đạt cổng toàn bộ test và chưa kiểm chứng dựng thật**, nên chưa thể báo hoàn tất ticket. Issue GitHub và API trả lỗi không truy cập được; căn cứ triển khai là brief tại repo và danh mục ref được chỉ định.

## Thay đổi

- `motion/long/pdvideo.py`: wrapper dùng lại `../hf_pdvideo.py`, lọc Commons, IA, NASA theo brief; cache đặt trong `output/long/<topic>/pd/`, giữ mp4 và sidecar, tạo credit có tên, kho, giấy phép và trang nguồn. Community IA tự khai bị từ chối kể cả khi tự gắn PDM.
- `motion/long/build_long.py`: nhận cảnh `broll` với `pd`, `start`, `dur`, `fit`, `label`; xác minh, tải/cắt, chèn video và đổi nhãn sang cấu trúc nhãn sẵn có; ref lỗi làm dừng và báo lý do. `dur` mặc định 15 giây, tối đa 20; `fit` mặc định blur với 4:3, cover với nguồn khác; nhãn mặc định là TƯ LIỆU và năm khi metadata có năm.
- `motion/long/describe.py`: đọc credit video từ `credits.json` cho mô tả CL và MIM/CK. `motion/long/floor.py`: tính cảnh broll có `pd` vào số cảnh b-roll.
- `motion/long/media_search.py`: thêm `pd` và `pd-strip`; `motion/long/README.md`: bảng khóa, ví dụ và luật giấy phép. `tests/test_pdvideo_long.py`: kiểm tra lọc, sidecar/credit giả, cấu trúc cảnh cũ và floor.

## Kiểm tra và giới hạn

- `python -m compileall -q motion/long/pdvideo.py motion/long/build_long.py motion/long/describe.py motion/long/media_search.py motion/long/floor.py tests/test_pdvideo_long.py`: đạt.
- `PYTHONIOENCODING=utf-8 python -m pytest tests -q`: chạy nhưng phải dừng khi nhiều fixture thư mục tạm báo lỗi quyền. Trên Windows sandbox, thư mục do pytest tạo chế độ 0700 không đọc lại được; cấu hình `--basetemp` trong worktree cũng gặp `PermissionError: [WinError 5]`.
- Chạy lại qua `pytest.main`, đổi riêng mode tạo thư mục tạm thành 0777, `--basetemp=output/long/gh278-pytest-c -p no:cacheprovider`: **1.300 đạt, 11 lỗi, 15 bỏ qua, 65 cảnh báo**. `test_branch_gate_rejects_non_repository` dùng thư mục thử nằm dưới worktree nên nhận nhầm repo cha; hai test `qa_blank` không đọc/ghi được thư mục Temp của tiến trình con; hai test `run_chain` bị bash `CreateFileMapping` Win32 error 5; sáu test `test_stier_render_gates` không chạy được HyperFrames/npx. Chưa có kết quả xanh toàn bộ.
- Cùng cách xử lý thư mục tạm, chạy `tests/test_pdvideo_long.py -q` sau thay đổi cuối: **4 đạt**. Kiểm tra cấu trúc cảnh cũ là so object đầu ra `plan`, chưa so toàn bộ HTML theo byte. Chưa có test tích hợp dựng HTML thật và chưa kiểm tra nhãn trên khung hình.
- Lưu ý sai sót khi chạy bộ test tổng: một số test hiện có tự gọi ffmpeg, bash/Git và thử cổng render HyperFrames. Đây là tác dụng phụ không phù hợp chỉ dẫn không gọi ffmpeg/render ngoài fetch; tôi không chủ động chạy lệnh render video hoặc Chrome, nhưng lẽ ra phải kiểm tra các test trước khi chạy. Không có clip Mata Hari được render bởi tác vụ này.
- `rg -n '\?' motion/long/pdvideo.py tests/test_pdvideo_long.py`: chỉ thấy dấu hỏi trong regex Python, không thấy chữ tiếng Việt bị thay bằng dấu hỏi ở hai file mới. Không dùng git diff theo lệnh cấm git.
- Không kiểm được metadata và giấy phép thực tế của ba ref dưới đây trong lượt này; danh mục ref chỉ là điểm xuất phát, wrapper vẫn phải kiểm tra trực tiếp khi Lead dựng. Không có clip sheet hoặc thumbnail vì ticket cấm render và không giao tạo thumbnail.

## Lead dựng thử trên bản sao

Chuẩn bị một bản sao topic Mata Hari và dữ liệu timing/voice cần thiết, không chỉnh topic thật. Đặt lần lượt ba cảnh b-roll trong các chương thích hợp, chọn thời điểm và thời lượng theo cảnh; thời lượng cảnh cộng biên 0,5 giây phải không vượt `dur`:

```json
{"type":"broll", "at":0, "pd":"commons:File:Arrivée d'un train gare de Vincennes (Arrival of a Train at Vincennes Station) (1896).webm", "start":0, "dur":18}
{"type":"broll", "at":0, "pd":"commons:File:Paris Exhibition viewed from the Seine 1.ogv", "start":15, "dur":18}
{"type":"broll", "at":0, "pd":"ia:Islandof1920", "start":130, "dur":18}
```

Thay tên chương theo bản sao thực tế, rồi chạy tuần tự:

```powershell
python motion/long/build_long.py <ban-sao> html ch00 ch01 ch02
python motion/long/build_long.py <ban-sao> render ch00 ch01 ch02 --draft
python motion/long/describe.py <ban-sao>
```

Kiểm mp4 và JSON trong `output/long/<ban-sao>/pd/`, credit và mô tả, nhãn trên khung, tờ clip và các cổng QA trước khi Lead quyết định bước tiếp theo. Không dùng `ia:H-1518` hay clip Commons Third Aviation Instruction Center CC BY 3.0.
