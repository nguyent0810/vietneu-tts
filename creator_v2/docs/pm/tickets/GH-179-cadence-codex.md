# Công cụ đo nhịp đổi hình của Long (cadence)

**Bối cảnh:** chủ kênh đặt mục tiêu ngày 06/11: Long có trung bình cứ 3–5 giây một thay đổi hình đáng kể, phối hợp 4 nhóm:
- A: tư liệu;
- B: AI tái dựng bối cảnh;
- C: AI minh họa khái niệm;
- D: motion graphics.

Cần công cụ đo trên Long đã có cảnh (`data/long/<topic>/ch*.json`), giống cách `motion/long/floor.py` đo sàn.

**File được sửa (tạo mới):**
- `motion/long/cadence.py`;
- `tests/test_cadence.py`;
- báo cáo `docs/pm/tickets/GH-179-cadence-report.md`.

Không sửa `floor.py` hay `build_long.py`. Ghi file bằng Python, `encoding="utf-8"`.

**Việc:** `python motion/long/cadence.py <topic> [--json]`
1. Đọc `data/long/<topic>/ch*.json`. Đọc `floor.py`, `scene_params.py`, `build_long.py` để hiểu cấu trúc cảnh, cách tính thời lượng từng cảnh, và nơi có timing thật sau TTS (ví dụ `output/long/<topic>/` timing hoặc `takes.json`). Có timing thật thì dùng timing thật, không có thì ước bằng cách mà `scene_params` đang dùng. Ghi rõ đang dùng nguồn thời lượng nào.
2. Đếm "thay đổi hình":
   - mỗi cảnh mới là một thay đổi;
   - bên trong một cảnh, các bước con đã khai báo (nhiều ảnh, nhiều hàng ledger hiện lần lượt, các điểm trên timeline hay map, các bước zoom/pan có khai báo) cũng là thay đổi, nếu engine thật sự hiện chúng theo thời gian.

   Ghi rõ luật đếm trong docstring.
3. Phân nhóm mỗi cảnh:
   - A: ảnh có nguồn trong `output/long/<topic>/img/*.json` mà không có cờ `ai_generated`;
   - B/C: ảnh có `asset_id` hoặc `ai_generated`, phân biệt bằng tag `tai_dung` và `khai_niem` nếu có, không có tag thì gộp thành "AI";
   - D: các loại cảnh không dùng ảnh (map, chart, counter, timeline, ledger, board, kinetic…);
   - broll clip tính riêng.
4. Xuất theo từng chương và cả video:
   - số thay đổi;
   - giây trung bình mỗi thay đổi;
   - khoảng dài nhất không đổi hình (giây, kèm cảnh);
   - % thời lượng theo nhóm.

   Gắn cờ CẢNH BÁO khi trung bình chương > 5 s hoặc có khoảng > 8 s. Chỉ cảnh báo, không chặn.
5. Test với dữ liệu giả nhỏ:
   - đếm cảnh;
   - đếm bước con;
   - phân nhóm A/AI/D;
   - cảnh báo > 5 s.
6. Chạy thử trên `bao-thanh-thien` và `golden`, ghi kết quả vào báo cáo. Đó là mốc so sánh hiện tại.

**Không:** commit, render, upload.
