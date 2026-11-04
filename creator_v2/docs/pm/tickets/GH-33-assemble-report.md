# GH-33 — báo cáo ráp spec Short

Phạm vi đã làm: cập nhật đúng 12 file `data/stier/specs/<slug>.json` theo `GH-33-lines.json` và `GH-33-titles.json`. Không render, TTS, upload, đổi lịch, sửa code hay thao tác git.

Các lệnh kiểm đã chạy:

```text
python motion/stier/build.py <12 slug> --preflight
12/12 PASS

python motion/stier/script_lint.py <12 slug>
12/12: 0 lỗi
```

Đối chiếu `lines` bằng chuỗi JSON cho cả 12 spec: khớp 100% với `GH-33-lines.json`. Các cảnh đầu hiển thị đúng `frame0` ở giây 0. `title`, `say`, mô tả đầu và tags đã lấy từ hai file ticket; `sources`/ghi công cũ được giữ lại. Các cảnh CK giữ câu miễn trừ trong mô tả.

## Theo slug

| Slug | Chuỗi kiểu cảnh | Clip/ảnh | Preflight / lint / lines |
|---|---|---|---|
| `mim-binance-20-phut-6-3-ty` | counter → timeline → kinetic+clip → board → table → kinetic → cards3d → kinetic | Pexels `9783691`; chờ điền `q: server room red light rack` | PASS; 0 lỗi, 12 cảnh báo; khớp |
| `mim-cam-nhap-dien-thoai-cu-2027` | counter → ledger → cards3d → kinetic+clip → board → kinetic+clip → table → kinetic | Pexels `6755165`, `6755168` | PASS; 0 lỗi, 12 cảnh báo; khớp |
| `mim-sam-altman-ram-5-phan-tram` | photo → chart → board → quote → kinetic+clip → cards3d → ledger → board | Commons `File:“Sam Altman” by Village Global.jpg` (CC BY 2.0, Village Global); Pexels `10470834` | PASS; 0 lỗi, 15 cảnh báo; khớp |
| `mim-ve-tinh-google-4-chip-tpu` | counter → map → quote → cards3d → kinetic → board → ledger → kinetic+clip | chờ điền `q: satellite in orbit earth space`; Pexels `39433173` | PASS; 0 lỗi, 13 cảnh báo; khớp |
| `mim-9-tren-10-ai-tu-lay-otp` | counter → cards3d → table → board → kinetic+clip → ledger → cards3d → kinetic | Pexels `33315117` | PASS; 0 lỗi, 16 cảnh báo; khớp |
| `mim-android-20-tin-nhan-tu-than` | counter → cards3d → kinetic → board → table → kinetic+clip → ledger → kinetic | chờ điền `q: smartphone dark screen glitch`; Pexels `8865818` | PASS; 0 lỗi, 10 cảnh báo; khớp |
| `ck-thue-xang-0-giam-1804` | chart → timeline → board → table → ledger → kinetic+clip → cards3d → kinetic | Pexels `39189857` | PASS; 0 lỗi, 12 cảnh báo; khớp |
| `ck-dien-giam-44-dong-20-nam` | timeline → board → counter → chart → cards3d → kinetic+clip → ledger → board → kinetic | Pexels `38362060` | PASS; 0 lỗi, 10 cảnh báo; khớp |
| `ck-ho-kinh-doanh-giam-30-thue` | counter → cards3d → table → board → timeline → ledger → kinetic+clip → board → kinetic | Pexels `7233781` (dùng cho clip chủ cửa hàng và nền cầu nối đồ họa) | PASS; 0 lỗi, 15 cảnh báo; khớp |
| `ck-vang-sjc-140-trieu-chenh-14-trieu` | chart → counter → kinetic+clip → table → board → cards3d → ledger → kinetic | Pexels `7082895` | PASS; 0 lỗi, 15 cảnh báo; khớp |
| `ck-lai-giam-05-tien-gui-80-ngan-han` | board → chart → ledger → kinetic+clip → cards3d → chart → kinetic+clip → kinetic | Pexels `6326861`, `35771190` | PASS; 0 lỗi, 12 cảnh báo; khớp |
| `ck-binance-63-ty-rut-36-ty` | counter → board → timeline → board → table → chart → cards3d → ledger → kinetic+clip → kinetic | Pexels `32365210` | PASS; 0 lỗi, 16 cảnh báo; khớp |

## Ghi chú kiểm

- Không có lỗi lint còn lại. Cảnh báo lint nêu trên đến từ câu đã được Lead duyệt (độ dài câu, chữ số/từ viết tắt, hook/câu chốt); không sửa `lines` vì ticket cấm.
- Hai query Pexels chờ điền: `server room red light rack`, `satellite in orbit earth space`, `smartphone dark screen glitch`. Chúng được để `vid: null` và `q` trong spec vì kết quả tìm ban đầu không đủ chắc chắn để bảo đảm đúng ngữ nghĩa/không lộ logo.
- Không bổ sung hoặc thay đổi bất kỳ khẳng định nội dung nào. Chưa thực hiện xác minh lại dữ kiện đã Lead duyệt; nguồn hiện có được giữ nguyên trong từng spec.
- Không có clip sheet hay thumbnail mới: ticket cấm render và không yêu cầu thumbnail. Các bảng poster Pexels nội bộ đã tạo trong quá trình tìm ID nằm tại `motion/hf/assets/clips/sheets/`.
