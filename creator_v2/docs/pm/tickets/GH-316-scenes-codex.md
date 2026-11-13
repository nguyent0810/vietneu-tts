# GH-316: CK bài 10 (ck-c7-mo-tai-khoan-phi), bước 4: cảnh và spec (Codex)

Đọc issue (chỉ đọc): `gh issue view 316 --repo nguyent0810/vietneu-tts`. Kịch bản bản 2 đã được Lead duyệt: `data/long/ck-c7-mo-tai-khoan-phi/script.md` (8 chương, 128 câu, 2.571 âm tiết). Factcheck nằm ở `factcheck.md`, plan ở `plan.md`.

## Môi trường
- Worktree `D:\Tools\Youtube Creator v2\wt-ck10`, nhánh `long/ck-c7-mo-tai-khoan-phi`. Đường dẫn tính từ `creator_v2/`. Lead commit.
- Tư liệu (chỉ đọc) ở checkout sản xuất `D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\`:
  - `output/long/ck-c7-mo-tai-khoan-phi/research.json`: 138 ảnh, kèm bảng `sheet_0`–`sheet_3`. Đọc `LOAI.md` cùng thư mục để biết ảnh bị loại (logo, mã cổ phiếu, mặt người, tiền giấy, lạc đề). Ảnh nên dùng: HOSE (sheet_0 #0, #4, #6, #7), két và hầm (sheet_2 #9–21, #23, #24, #26), skyline, phố Hà Nội (sheet_3 #14–20).
  - Ảnh AI `ai01`–`ai16` (đã import, khai báo `"aiNN": "EXT:ai:ai_NN"`): điện thoại có biểu đồ chung, cửa két, tủ két, máy tính và giấy, trạm thu phí, skyline TP.HCM, phòng giao dịch, phễu và đồng xu, đồng hồ cát xu, tủ két kính, lịch có khoanh đỏ, tòa nhà cột, điện thoại trên giường, cổng nhỏ và băng chuyền xu, sổ mở, két trong suốt và ống dẫn. Ảnh không có người, chữ hay mã cổ phiếu.
  - Clip `output/long/ck-c7-mo-tai-khoan-phi/broll/900002`–`900006.mp4`: điện thoại biểu đồ, phố đêm xe chạy, đồng hồ cát, trạm thu phí đêm, cửa hầm két. **Không dùng `900001`**, vì clip có bàn tay người.
  - Chép `research.json` sang `output/long/ck-c7-mo-tai-khoan-phi/` của worktree nếu `gen_scenes.py` cần.

## Khuôn mẫu
Chép cấu trúc một Long CK đã đăng: `data/long/ck-e2-quy-khan-cap/gen_scenes.py` hoặc `ck-e3-no-the-tin-dung`, gồm `IMGS`, helper, `CH[...]`, spec. Đọc `motion/long/README.md` để biết loại cảnh: ledger, bars, counter, timeline, thẻ thông tin #276, chữ động #277.

## Yêu cầu
- Mỗi câu neo vào cảnh thật; `at` và `hitAt` dùng từ có trong câu. Nhịp 3–5 giây một cảnh.
- **Mọi cảnh phải dài 2,5–9 giây sau TTS.** Câu ngắn dưới khoảng 2,5 giây thì gộp hai câu vào một cảnh. Trong ledger, timeline và split, phần tử con thứ hai phải hiện trong vòng 1 giây sau khi cảnh bắt đầu: cho các dòng neo theo mốc của chính cảnh. Counter không dùng `countAt` trễ.
- **Thẻ `file` ≤ 12% số cảnh và các thẻ cách nhau ≥ 5 cảnh** (floor #276). Long Lưu Gù vừa vướng lỗi này.
- **Nhãn "VÍ DỤ GIẢ ĐỊNH"** hiện trên màn hình ở mọi cảnh có số liệu của chị Hạnh (50 triệu, phí 0,15%, thuế giả định 0,1%, hòa vốn, ứng trước). Cảnh thuế ở CH04 hiện rõ nhãn GIẢ ĐỊNH.
- Không tên công ty chứng khoán, ngân hàng, ứng dụng hay mã cổ phiếu trên màn hình. Mọi con số trên màn hình phải có trong `factcheck.md` hoặc ghi chú kiểm chứng của `script.md`.
- Spec:
  - `channel: "CK"`.
  - Tiêu đề (Lead chọn): **"Mua 50 Triệu Cổ Phiếu: Giá Phải Tăng Bao Nhiêu Mới Hòa Vốn?"**, kèm 2 phương án dự phòng theo luật #337 (một phương án khoản tiền + mốc thời gian, một phương án rủi ro hoặc lợi ích).
  - `acc` có "chị Hạnh"; mô tả có câu "Nội dung giáo dục, không phải tư vấn đầu tư."
  - Theme, look và nhạc khác 3 video gần nhất (`motion/variety.py`).
  - `opening_gate: true`, `craft: true`. Trong 8 câu đầu đã có câu hỏi: "tiền của bạn sẽ đi đâu?"

## Kiểm (từ `creator_v2/`)
1. `python data/long/ck-c7-mo-tai-khoan-phi/gen_scenes.py`
2. `PYTHONIOENCODING=utf-8 python motion/variety.py audit ck-c7-mo-tai-khoan-phi`
3. `python motion/long/cadence.py ck-c7-mo-tai-khoan-phi`
4. Floor, gọi `floor.problems(chapters, "CK", topic, idcards_enabled=True)` từ Python: không lỗi trừ những mục cần TTS.
5. `python scripts/plan_lint.py ck-c7-mo-tai-khoan-phi`

TTS chưa có, nên `check_scene_durations.py` chưa chạy được. Hãy ước lượng 4,2 âm tiết/giây để tránh cảnh dưới 2,5 giây.

## Tiếng Việt
Ghi mọi file bằng Python `open(..., 'w', encoding='utf-8')`. **Không dùng PowerShell để ghi.** Sau khi ghi, grep để chắc không có `??`.

## Báo cáo
`docs/pm/tickets/GH-316-scenes-report.md`: số cảnh mỗi chương, loại cảnh, ảnh đã dùng, kết quả 5 bước kiểm, các chỗ khó minh họa.

Không render, không TTS, không commit, không đăng.
