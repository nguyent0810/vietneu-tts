# GH-228: cadence.py sập với mốc `[câu, null, n, lệch]`

`motion/long/cadence.py` báo "word anchor not found" và dừng khi cảnh hoặc phần tử con dùng mốc dạng `[lineIdx, null, 0, 0.3]` (null = đầu câu + lệch). Engine (`motion/stier/build.py` lớp `Anchors.__call__`) hỗ trợ dạng này: `w is None` → `L[i]["start"] + off`. Hòa Thân ch00 và Mata Hari dùng nó.

**Việc:** sửa `motion/long/cadence.py` để hiểu mốc `w = None` (và mọi dạng mà `Anchors` hiểu: int, float, `[i]`, `[i, w]`, `[i, w, n]`, `[i, w, n, off]`), dùng chung logic với `Anchors` nếu được thay vì viết lại. Thêm test trong `tests/` cho mốc null. Chạy `python -m pytest tests -q -k "cadence or anchor"` và toàn bộ `python -m pytest tests -q` phải xanh. Chạy `PYTHONIOENCODING=utf-8 python motion/long/cadence.py mata-hari` và `hoa-than` không sập.

File được ghi: `motion/long/cadence.py`, test mới trong `tests/`, báo cáo `docs/pm/tickets/GH-228-cadence-null-report.md`. Ghi file Python UTF-8. Không commit, không đổi nhánh.
