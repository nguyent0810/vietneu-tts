# GH-173: nhãn VÍ DỤ GIẢ ĐỊNH theo phong cách điện ảnh (phần thiết kế)

Đọc issue #173 (`gh issue view 173 --repo nguyent0810/vietneu-tts`) trước. Ticket này chỉ làm phần **đề xuất kiểu nhãn kèm ảnh khung hình**. Code preflight làm sau, ở ticket khác.

**Việc:**
1. Tìm các Short đang có nhãn ví dụ giả định. Grep "GIẢ ĐỊNH" trong `data/` và `motion/`. Ghi lại nhãn đang được đặt ở đâu và cỡ chữ của dòng phụ hay subtitle trong Short, đo ở khung 1080×1920.
2. Mỗi kênh MIM, CK, CL làm 2–3 kiểu nhãn, theo theme có sẵn trong `motion/hf/assets/engine/*.css`: font, màu, kiểu vào/ra. Kiểu chú thích phim hoặc thẻ tiêu đề điện ảnh, không phải ô cảnh báo hay watermark.
   - Mỗi kiểu là một file HTML độc lập: `docs/pm/mockups/173/<kenh>_<kieu>.html`, khung 1080×1920, dùng một ảnh nền có sẵn trong repo.
   - Cỡ chữ nhãn **không nhỏ hơn cỡ dòng phụ** đo ở bước 1. Nhãn nằm trong vùng an toàn của Short và không che nội dung chính.
3. Chụp PNG từng mockup bằng Chrome headless (`--screenshot --window-size=1080,1920`), lưu cạnh file HTML.
4. Không chèn chữ máy móc hay tên bot/model vào khung hình.

**Được ghi:** chỉ `docs/pm/mockups/173/*` và `docs/pm/tickets/GH-173-report.md`. Không sửa `motion/hf/assets/engine/*`, `motion/stier/*`, `factory/*`, `tests/*`. Không render video, không đăng, không commit.

**Báo cáo** `docs/pm/tickets/GH-173-report.md`:
- nhãn hiện ở đâu, cỡ chữ dòng phụ đo được;
- bảng các kiểu nhãn (kênh, tên kiểu, file PNG, cỡ chữ, màu, chuyển động);
- kiểu đề xuất cho mỗi kênh và lý do.
