# Tốc độ giọng đo từ segments — 17/11/2026

Đọc tại repo chính `output/cl_staging/long/out/L_bud_*.json`, `L_fs_*.json`; tối đa ba manifest mới nhất theo mtime trong từng cấu hình, không đếm lại JSON chương. Tính bằng `long_script_lint.syllables(spoken hoặc text)`, gồm cả thẻ đã đọc. Không TTS, không mở audio.

| Giọng | Engine/tempo manifest chính | Tệp / segments | Tiếng | Giọng thuần (s) | Cả nghỉ (s) | Tiếng/phút thuần | Tiếng/phút cả nghỉ |
|---|---|---:|---:|---:|---:|---:|---:|
| Binh | standard / 0.9 | 3 / 693 | 5291 | 1415.089 | 1776.59 | 224.3 | 178.7 |
| Binh | standard / 0.91 | 3 / 1014 | 16218 | 4564.907 | 5314.144 | 213.2 | 183.1 |
| Quang Sơn | standard / 0.91 | 3 / 68 | 1289 | 395.676 | 475.876 | 195.5 | 162.5 |
| Binh | unspecified / None | 3 / 186 | 3230 | 854.0 | 886.94 | 226.9 | 218.5 |
| Sơn | unspecified / None | 3 / 189 | 3529 | 954.3 | 987.78 | 221.9 | 214.4 |
| Thái Sơn | unspecified / 0.96 | 3 / 420 | 3583 | 970.678 | 1174.84 | 221.5 | 183.0 |
| Thái Sơn | v3 / 0.96 | 1 / 235 | 5388 | 1574.544 | 1737.44 | 205.3 | 186.1 |

Giọng thuần = tổng(end−start); cả nghỉ = tổng(start kế−start), segment cuối dùng duration_s−start. Pause gán cho giọng vừa đọc; Quang Sơn là đoạn alt trong các tệp Binh, không phải cấu hình chính Binh. `unspecified` nghĩa manifest không ghi engine; không tự đoán v3. Mẫu chỉ có manifest thiếu cấu hình không dùng để áp cho giọng mới.

**Thục Đoan: chưa có segments trong tập đường dẫn đã quét; 175 tiếng/phút trong PO16/11 là mốc cấu hình cũ, không phải đo mới của075b.** Tiếng là ước cách đọc của bộ đếm (số/tên có sai số), không phải phiên âm nghe tay. Mẫu Long khác độ dài câu, không cam kết tốc độ Short.

Danh sách tệp, SHA256, TTS và số tổng: [receipt](../research/075b/voice-rates.json). Chỉ đo lời trong manifest, không chứng minh plan hiện tại khớp audio. Giữ185 mặc định nháp tương thích; writer chọn --rate theo giọng, không thay hàng loạt bằng175.
