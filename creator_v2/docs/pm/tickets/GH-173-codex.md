# GH-173: đưa nhãn VÍ DỤ GIẢ ĐỊNH kiểu điện ảnh vào engine Short

**Áp dụng ngoại lệ AGENTS.md cho ticket code.** Bạn chạy trong worktree riêng. Được sửa đúng các file sau:
- các file engine Short trong `motion/hf/assets/engine/` mà bạn cần (JS/CSS của theme Short MIM, CK, CL). Ghi rõ từng file đã sửa trong báo cáo;
- `motion/stier/build.py`, chỉ phần preflight;
- test mới `tests/test_hypo_label_173.py`;
- báo cáo `docs/pm/tickets/GH-173-codex-report.md`.

Ghi file bằng Python `encoding="utf-8"`, không dùng PowerShell `Set-Content`.

**Chủ kênh chọn ngày 06/11** (mockup trong `docs/pm/mockups/173/`, mở `?static` để thấy trạng thái cuối; báo cáo `docs/pm/tickets/GH-173-report-v2.md`):
- CK: `ck_ribbon.html`;
- MIM: `mim_terminal_bracket.html`;
- CL: `cl_evidence_tape.html`.

**Việc:**
1. Đọc báo cáo vòng 1 `docs/pm/tickets/GH-173-report.md`, mục 1, để biết nhãn hiện đang nằm trong các trường `sub`/`note`/`unit` của 8 loại cảnh. Thêm một cơ chế nhãn riêng ở cấp cảnh: trường spec `"hypo": true`, hoặc `"hypo": "<chữ>"` (mặc định "VÍ DỤ GIẢ ĐỊNH"). Nhãn vẽ thành lớp phủ theo kiểu của kênh, chép đúng CSS và chuyển động vào/ra từ mockup:
   - chữ nhãn ≥ cỡ subtitle `#caps .cap`; đọc cỡ này từ CSS, không cố định 62px ở chỗ khác;
   - vị trí trong vùng an toàn: không đè subtitle, x < 900px;
   - dòng phụ tiếng Việt tự nhiên tuỳ chọn (`"hypo_sub"`).
2. Không sửa nội dung spec đã có. Spec cũ để chữ "giả định" trong `sub`/`note` vẫn render như cũ.
3. Preflight trong `motion/stier/build.py`:
   - cảnh nào có chữ "GIẢ ĐỊNH" trong `sub`/`note`/`unit`/`title` nhỏ (theo bảng cỡ chữ ở báo cáo vòng 1) mà không có `hypo` thì cảnh báo, nêu tên cảnh;
   - cảnh có `hypo` thì kiểm cỡ chữ nhãn ≥ cỡ subtitle.
   Chỉ cảnh báo, không chặn build.
4. Test `tests/test_hypo_label_173.py`:
   - preflight cảnh báo khi nhãn nằm trong `note` nhỏ;
   - không cảnh báo khi có `hypo`;
   - HTML sinh ra có lớp nhãn đúng kiểu của từng kênh;
   - cỡ chữ ≥ subtitle (so trong CSS).
5. Chạy `python -m pytest tests/test_hypo_label_173.py tests -q -k "stier or build or hypo or preflight"`, ghi kết quả.

**Không:** render video (Codex không render được; agy sẽ chụp QA sau), commit, upload, sửa Short đã đăng.

**Báo cáo:** file đổi, cách dùng trường `hypo` trong spec, ví dụ spec, kết quả pytest.
