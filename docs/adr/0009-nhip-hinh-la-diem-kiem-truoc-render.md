# Nhịp hình được kiểm trước khi render: phần chặn cứng giữ nhỏ, các sàn chỉ cảnh báo

Trạng thái: đã chấp nhận (01/10/2026, bổ sung 21/10 và 24/10).

Ngày 01/10 đo hai Long F1 và B1:

- 68% thời lượng là ba loại sơ đồ lặp đi lặp lại;
- 35% là thẻ chữ khoá trên nền trơn;
- có cảnh đứng yên 64 giây.

Ngày 19/10, tt03 chỉ có 36 ảnh/clip cho 758 câu nên phải dừng render và làm lại. Nếu chỉ soát bằng mắt sau khi render xong, mỗi vòng sửa tốn khoảng 1,7 lần thời lượng video.

`hf_batch_render.pacing()` chạy trên spec dựng cộng mốc giây của TTS, trước khi render hình:

- **Chặn render**:
  - câu không có hình gì (`bare_lines`);
  - một loại sơ đồ chiếm hơn 25% thời lượng;
  - thẻ chữ khoá đứng yên hơn 15% khi không bật chữ chạy (`kinetic`);
  - một cảnh đứng hơn 25 giây, trừ khi spec dựng ghi lý do bằng `"slow_hold": {"<câu>": "đọc nguyên văn bia"}`.
- **Chỉ cảnh báo** (sàn cảnh):
  - dưới 14 loại cảnh;
  - chữ trên nền trống hơn 12%;
  - 3 cảnh liền nhau cùng một loại;
  - phút đầu hoặc phút cuối dài hơn 4 giây mỗi cảnh (mục tiêu 2–4 giây).
- **Báo thêm**: p50/p90 số giây mỗi cảnh, tỉ lệ tư liệu / stock / ảnh AI.

## Các phương án đã cân nhắc

- **Chỉ soát mắt sau render.** Tốn thời gian và hay sót.
- **Chặn cả các sàn.** Chưa có đủ hình để đạt: L_bud_26 có 97 ảnh vẫn còn 21,5% chữ trên nền trống. Mốc "2–4 giây" lấy từ dữ liệu của một nhà cung cấp (Overseeros, mẫu 33 video), chưa có A/B trên kênh ta.

## Hệ quả

- Thợ gọi các hàm chỉ-kiểm (`bare_lines`, `retention_issues`, `reveal_issues`), không render thật.
- Luật thợ: mỗi 5 câu phải có ít nhất 1 ảnh/clip.
- Số đo hai Long thử (24/10):
  - BUD: p50 6,3 giây, p90 8,4 giây, phút đầu 8,4 giây/cảnh.
  - Cao Biền: bắt được 2 cảnh đứng 26 và 35 giây, có ghi số câu.
- Ranh giới cảnh hiện tính theo câu. Muốn đạt 2–4 giây ở phút đầu thì phải đổi hình giữa câu (chữ chạy theo từng từ, clip ngắn).

## Bằng chứng

`hf_batch_render.py` (`pacing`, `floor_warnings`, `tempo_edges`), `tests/test_long_pacing_floor.py`, `tests/test_pacing_ticket65.py`, `output/cl_staging/grok/reports/65_visual_pacing_long_short.md`, commit `882346f`.
