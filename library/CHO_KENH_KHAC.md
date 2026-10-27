# Dùng thư viện cho kênh khác (bản thử, trước P7)

Thư viện sinh ra ở repo kênh FS và BUD. Trang này chỉ cho kênh khác dùng phần nào, bỏ qua phần nào, và gửi kết quả về bằng cách nào. Đọc trước: `README.md` và `docs/adr/0018-thu-vien-tri-thuc-chung.md`, nhất là mục 7.

## Phần dùng được ngay
| Phần | Ở đâu | Ghi chú |
|---|---|---|
| 138 thẻ kỹ thuật dựng | `cards/canh/`, `cards/template/`, `cards/thiet_bi/` | 106 thẻ cảnh gắn `pham_vi: chung`. Mỗi thẻ có mô tả, số nguồn, ví dụ ngoài, và cờ `da_dung` (đã dựng ở FS/BUD hay chưa). |
| 26 thẻ chủ đề / hook / thumbnail | `cards/khuon/chude_*`, `cards/kich_ban/hook_*`, `cards/*/thumb_*` | Mỗi thẻ ghi `chua_duoc` và mức bằng chứng. Nghiên cứu gốc: `research/chu_de_hook_thumbnail_2026-10-26.md`. |
| Báo cáo kiểm kê | `inventory/report.md` | 2.752 mục sau khử trùng, gom về 138 kỹ thuật. |
| Lệnh tra cứu | `tools/lib.py find`, `rank`, `pick`, `register-cell` | Chỉ cần Python 3 chuẩn, chạy được trên Windows (đầu ra UTF-8). `pick` của kênh ngoài không ghi gì vào `channels/`; muốn sinh lại hồ sơ FS/BUD thì dùng `lib.py sync`. |

## Phần chỉ để tham khảo
- **"Cách dựng" trỏ vào engine HyperFrames của repo này** (`longform.js`, `engine.js`, `studio/devices/*.js`). Nếu kênh bạn dùng engine khác, hãy lấy ý tưởng, đừng gọi thẳng code đó.
- **273 thẻ `noi_dung: trich_tu_dong`** (luật, quy trình, khuôn, bài học…) mới là trích máy, chưa có diễn giải. Nhãn `pham_vi` của chúng chưa được duyệt, và nhiều thẻ `khuon` gắn `chung` thật ra là khuôn riêng của BUD/FS. Đừng áp chúng vào kênh bạn.

## Năm bước thử
1. **Lấy thư viện.**
   ```bash
   git clone --branch feat/library-inventory https://github.com/nguyent0810/vietneu-tts.git
   ```
   Chỉ cần thư mục `library/`.
2. **Khai hồ sơ kênh.** Chép `channels/_mau.yaml` thành `channels/<kenh>.yaml`.
   - Mỗi khuôn ghi `trang_thai` là `thang`, `ngang` hoặc `thua`, theo số liệu thật của kênh, kèm nguồn.
   - Chuỗi đang thắng nằm trong một khuôn thua thì ghi vào `bao_ve` và đặt `tu_khoa`.
   - Khuôn thua hoặc ngang thì ghi `ly_do_thua`, chọn trong `hook`, `chu_de`, `ctr`, `nhip`, `hinh`. `pick` chỉ gợi ý những thẻ chữa đúng lý do đó (trường `chua_duoc` của thẻ; thẻ hình mặc định chỉ chữa `hinh`). Nếu không có thẻ nào, lệnh báo "thư viện chưa có" thay vì gợi ý bừa.
   - `do_hop_mac_dinh` là độ hợp chung (0–3) cho mọi thẻ `chung`. Thẻ nào hợp hơn hoặc kém hơn thì ghi đè trong `do_hop`; ghi 0 để loại thẻ đó.
   - `thu_muc_thu_nghiem` là thư mục ô thử, tính từ gốc repo kênh bạn.
3. **Chọn chỗ áp và kỹ thuật.**
   ```bash
   python library/tools/lib.py pick --channel <kenh> --usage-root <repo kênh>
   ```
   Lệnh tự loại khuôn đang thắng và các ô thử chạm chuỗi bảo vệ. `rank --channel <kenh>` cho danh sách đầy đủ hơn. Đọc thẻ của kỹ thuật được chọn trong `cards/`.
4. **Đăng ký ô thử.**
   ```bash
   python library/tools/lib.py register-cell --channel <kenh> --ma <MÃ> --khuon <khuôn thua/ngang> --ky-thuat <id thẻ> --gia-thuyet "..." --usage-root <repo kênh>
   ```
   Sau đó tự thêm slot, đối chứng, ngày đo, ngưỡng thắng và ngưỡng thua (mẫu: ô LIB1 của BUD).
5. **Dựng, đăng, đo**, rồi gửi kết quả về theo mục dưới.

## Gửi kết quả về
Ghi `library/eval/<kenh>/ket_qua.md`, rồi mở PR vào nhánh `feat/library-inventory`, hoặc nhắn phiên Lead. Gồm:
- thẻ đã dùng (id) và thẻ đã cân nhắc nhưng bỏ, kèm lý do;
- chỗ thẻ sai hoặc thiếu: nhãn `pham_vi` sai, "Cách dựng" không làm theo được, rủi ro chưa ghi;
- số đo của ô thử: view, AVP hoặc giữ chân so với đối chứng, ngày đo;
- kỹ thuật mới kênh bạn có mà thư viện chưa có (để thêm adapter hoặc thẻ).

Lead sẽ ghi `bang_chung` vào thẻ, kèm nhãn kênh của bạn.

Không đưa khoá, token hay dữ liệu kênh riêng tư vào PR.
