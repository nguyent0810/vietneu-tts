# AGENTS.md — luật cho agent sản xuất (Codex) trong repo này

Repo dựng video cho 3 kênh YouTube tiếng Việt: MIM (AI/công nghệ), CK (tài chính cá nhân), CL (Hình Sự). Từ 05/11/2026 CL cũng sản xuất trong repo này theo kế hoạch #177 (Bao Thanh Thiên, Hòa Thân). Agent chỉ làm CL khi có ticket kèm brief, đúng phạm vi brief; mọi luật dưới đây áp dụng cho CL như MIM/CK.

Vai trò:
- **Claude** điều phối: viết ticket, review cuối, đăng.
- **Agent sản xuất (bạn):** làm đúng ticket được giao trong `docs/pm/tickets/`, rồi viết báo cáo vào file kết quả mà ticket chỉ định.

## Cấm tuyệt đối

- **Không upload, không sửa và không xoá gì trên YouTube.** Không chạy `publish_long.py`, `publish_batch.py`, `enqueue_*.py`, `scripts/playlists.py`. Không đọc thư mục credential (`.youtube_channels`, `YT_CREDS_DIR`).
- **Không ghi `state.sqlite`.** Muốn xem lịch thì mở ở chế độ chỉ đọc:
  ```python
  sqlite3.connect('file:state.sqlite?mode=ro', uri=True)
  ```
- **Không đụng git:** không `git commit`, `push`, `reset`, `checkout`, `stash`.
- **Không sửa code dùng chung:** `motion/hf/assets/engine/*`, `motion/long/build_long.py`, `motion/stier/*.py`, `factory/*`, `tests/*`. Nếu thấy lỗi engine thì ghi vào báo cáo, đừng tự sửa.
  - **Ngoại lệ, ticket code (chủ kênh duyệt 06/11/2026):** khi brief ghi rõ tên từng file code dùng chung được sửa và việc chạy trong worktree hoặc nhánh riêng (không phải checkout sản xuất), agent được sửa đúng các file đó cùng test tương ứng. Lead review và chạy test xanh trước khi merge. Các luật khác vẫn giữ nguyên: không đụng git, không upload, không đổi lịch thật.
  - **Ghi file tiếng Việt bằng Python `encoding="utf-8"`**, không dùng PowerShell `Set-Content`/`echo`: cách đó biến chữ có dấu thành `?` (06/11, cả trong mã nguồn).
- **Không xoá file** ngoài thư mục topic của ticket (`data/long/<topic>/`, `output/long/<topic>/`, `motion/long/thumbs/<topic>_t*.html`).
- **Không chạy hai lệnh render cùng lúc.** Máy chỉ chạy một render một lúc (`factory/render_lock.py` tự xếp hàng). Không kill tiến trình của người khác.

## Luật nội dung

- **Sự thật:** mỗi khẳng định có số, ngày hoặc tên đều phải có một dòng trong `factcheck.md`, kèm URL đã mở được. Không mở được nguồn thì không đọc thành khẳng định: hoặc bỏ, hoặc nói rõ "theo …". Không bịa trích dẫn. Lời trích là bản dịch thì gắn `[TRÍCH DỊCH]`.
- **Ảnh:**
  - MIM chỉ nhận PD, CC0, CC BY. Không nhận CC BY-SA, GFDL, NC, ND.
  - Không dùng hình phim; phim chỉ được nhắc bằng lời và chữ.
  - Không gắn nhãn tên người thật lên clip stock của người lạ.
  - Clip không được lộ logo hay chữ đọc được của thương hiệu.
  - Long MIM/CK dùng ảnh AI: giữ `credit: false`, không in nhãn "ẢNH MINH HỌA" trên khung, và không nhắc AI trong mô tả (chủ kênh giữ quyết định 26/10, chọn lại 05/11); nhãn của ảnh thật, clip và mọi hành vi CL giữ nguyên.
- **Mô tả công khai** (`spec.youtube.*`, `description`) không được chứa: `<`, `>`, "CẦN", "cần kiểm", "WebFetch", "factcheck", "data/long", "tìm kiếm", "agent". Ghi chú làm việc để trong `sources_internal`.
- **CK:**
  - Không nêu tên ngân hàng thương mại, công ty chứng khoán, hãng xe hay mã cổ phiếu.
  - Không nói "nên mua/bán".
  - Số tự giả định phải ghi "VÍ DỤ GIẢ ĐỊNH".
  - Mô tả có câu "Nội dung giáo dục, không phải tư vấn đầu tư."
- **Tiêu đề** ≤ 60 ký tự. MIM: người + năm + bước ngoặt, hoặc khuôn "[PHIM/APP] Ngoài Đời Thật: [người thật]". CK: một khoản tiền × một mốc thời gian.
- **Viết cho tai:** câu một hơi, nói với "bạn", số làm tròn dễ nghe. Mã tài liệu và giờ chính xác chỉ hiện trên màn hình. Không mở bài bằng "trả lời ba câu hỏi"; mỗi bài dùng một dạng lộ trình riêng.
- **Giọng kể (v3, #264):** viết lời kể hấp dẫn, có diễn tiến và nhịp, không liệt kê khô. Theo ba vùng của `docs/pm/storytelling-guide.md`: sự thật có nguồn; bối cảnh tái dựng (được sáng tạo, không cần nguồn thứ hai); giọng người kể (tự do). Được bỏ dữ kiện phụ để lấy chỗ kể, nhưng không sửa sai dữ kiện. Ba lằn ranh: không bịa sự kiện, số hay lời trích như sự thật; không gán tội hoặc tính cách xấu cho người thật khi thiếu căn cứ; CK không hứa lợi nhuận và giả định phải có nhãn. BUD: không gán cho Đức Phật lời hay việc không có trong kinh.
- **Thumbnail:** chữ tiếng Việt chỉ dựng bằng `motion/long/thumb.py` (HTML), không vẽ chữ bằng AI. Phải soi `tN_small.jpg`.

## Lắp spec Short (rút từ retro 04/11/2026, GH-143)

- **Không có loại cảnh `"type": "clip"`.** Cảnh dùng footage là `"type": "kinetic"` (hoặc loại khác có sẵn trong bảng 19 loại của `motion/stier/README.md`) kèm trường `"clip": "pexels:<id>"` và ô (`win`, `win-band`, `full`). Điền `vid` không làm footage xuất hiện. Preflight "OK" chưa chứng minh cảnh có hiển thị (issue #145).
- **Loại cảnh chỉ lấy từ bảng trong `motion/stier/README.md`.** Không tự đặt loại mới; spec cần loại không có thì ghi vào báo cáo và dừng.
- **Sau render, mở tờ khung (`final_sheet.jpg` hoặc `qa_sheet.png`) và so các khung cách nhau ≥ 2 giây.** Nếu các khung giống nhau (chỉ khác hạt nền), video đứng hình: báo ngay, không báo "hoàn tất".
- **`script_lint.py` chạy bằng `PYTHONPATH=. python motion/stier/script_lint.py <slug>`** cho tới khi #144 xong. Báo cáo ghi rõ đã chạy lint hay không; lỗi import không phải lý do bỏ lint.
- **Lời đọc: số tròn.** Số chính xác (ví dụ 262,725 triệu, 2.725.000 đồng) chỉ hiện trên màn hình; lời đọc làm tròn ("khoảng 263 triệu", "gần ba triệu"). Mỗi câu một hơi, câu cuối không gượng ghép: đọc to một lần trước khi giao.
- **Nhãn "VÍ DỤ GIẢ ĐỊNH" phải đọc được trên khung hình thật** (đọc rõ ở khung rộng 360 px, không phải phóng to mới thấy), không chỉ có trong spec. Soi ở `qa_t*.png`; nhãn nhỏ hơn dòng phụ khác thì tăng cỡ.
- **Các sổ `data/variety/*.json` do `build.py` ghi là kết quả hợp lệ của build.** Không hoàn nguyên: nếu ticket cấm ghi các sổ này thì ghi vào báo cáo và để Lead quyết (hoàn nguyên làm sổ đa dạng nhạc thiếu bài vừa dùng).

## Làm Long: đọc đúng 3 file, không khám phá repo

Khi ticket là một video dài, chỉ đọc:
1. ticket;
2. `docs/codex/long-rules.md` (cổng chất lượng, lỗi đã gặp, ảnh AI);
3. `docs/codex/long-cheatsheet.md` (cấu trúc cảnh, helper, thứ tự lệnh).

Thêm vào đó là các file mẫu mà ticket chỉ đích danh.

**Không** grep hay đọc code engine, thư mục của bài khác, hay log cũ để "tìm hiểu". Cách đó từng tiêu hết quota mà chưa ghi được file nào (26/10/2026). Thiếu thông tin thì ghi câu hỏi vào báo cáo rồi dừng.

## Báo cáo

Ghi file kết quả theo ticket, gồm:
- đã làm gì, lệnh nào chạy và kết quả, lỗi lint còn lại;
- khẳng định nào không kiểm được;
- đường dẫn clip sheet và thumbnail.

Không tự nhận là xong nếu chưa chạy các cổng kiểm ở trên.
