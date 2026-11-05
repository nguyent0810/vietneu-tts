# GH-147 — báo cáo Codex

## Đã làm

- `motion/long/build_long.py`: thêm chuẩn hoá tập trung ngay sau khi nạp chapter. Với `channel` MIM/CK, cảnh có ảnh AI bị bỏ riêng trường `illus`; `credit`, `tone`, nhãn ảnh thật và toàn bộ CL không đổi. Ảnh AI được nhận bằng key `aiNN`, giá trị `spec.imgs[key]` bắt đầu `EXT:ai`, hoặc sidecar `output/long/<topic>/img/<key>.json` có `file` bắt đầu `EXT:ai`.
- `motion/long/describe.py`: khi MIM/CK thật sự dùng ảnh AI, chèn và khử trùng lặp để `description.txt` có đúng một dòng `Một số hình minh hoạ được tạo bằng AI.`. File này là nơi đang sinh `description.txt`; nó không nằm trong danh sách “Được ghi” của ticket nhưng cần thiết để thực hiện mục 2.
- `tests/test_gh147_ai_media.py`: hồi quy ảnh AI MIM, ảnh thật, CL, sidecar và dòng mô tả một lần.
- Cập nhật `docs/codex/long-rules.md`, `docs/codex/long-cheatsheet.md`, `AGENTS.md`; thêm dòng `thay bởi #147` vào hai tài liệu PM được chỉ định.

## Chưa thể làm trong phạm vi ticket

- Không sửa `motion/long/publish_long.py` và không có test payload `containsSyntheticMedia`: đường upload tạo payload trong `factory/channel.py` (`Upload` và `_meta`), trong khi `AGENTS.md` cấm tuyệt đối sửa `factory/*` và ticket cũng không cho file đó. Không có điểm móc tại `publish_long.py` để đưa trường này vào request mà không lách kiến trúc hoặc sửa `factory/*`.
- `docs/adr/0004-thu-bac-nguon-hinh-va-anh-ai.md` không có trong checkout; mở issue #147 trên GitHub cũng không lấy được nội dung (cache miss). Vì vậy không kiểm được phần “Hệ quả” ngoài nội dung ticket.

## Lệnh đã chạy

```text
python -m py_compile motion/long/build_long.py motion/long/describe.py motion/long/publish_long.py
python -m pytest tests/test_gh147_ai_media.py -q -p no:cacheprovider
.....                                                                    [100%]
5 passed in 1.51s
```

Đã chạy đúng lệnh ticket `python -m pytest tests -q` hai lần. Suite không cho ra dòng cuối trong giới hạn runner; lỗi khởi tạo lặp lại là `PermissionError: [WinError 5] Access is denied` khi pytest quét `%TEMP%\\pytest-of-Tung-QA`. Dùng `--basetemp` trong workspace cũng bị từ chối quét; `C:\\tmp` bị từ chối tạo thư mục. Không có lỗi lint/cú pháp còn lại ở phần GH-147.

## Topic MIM/CK chưa upload có ảnh AI

- `ck-f3-tien-mung-cuoi` (CK): `ai01`–`ai06`.

Danh sách trên được lập từ `spec.json`/chapter JSON và `state.sqlite` mở chỉ-đọc; không đọc credential, không đổi lịch, không render hoặc upload.

Clip sheet và thumbnail: không tạo/soát, vì ticket cấm render và không giao một topic video để dựng.

## Tóm tắt file thay đổi

- `motion/long/build_long.py`: nhận diện và gỡ nhãn AI MIM/CK khi nạp cảnh.
- `motion/long/describe.py`: disclosure AI đúng một lần trong mô tả.
- `tests/test_gh147_ai_media.py`: 5 regression tests xanh.
- `docs/codex/long-rules.md`, `docs/codex/long-cheatsheet.md`, `AGENTS.md`: luật #147.
- `docs/pm/2026-10-28-webauto-ap-dung.md`, `docs/pm/2026-10-29-anh-tinh-long-mim-ck.md`: thêm `thay bởi #147`.
