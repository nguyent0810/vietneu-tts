# GH-147 — Báo cáo render thử nghiệm ảnh AI (MIM/CK gỡ nhãn ẢNH MINH HỌA)

## 1. Mục tiêu và phạm vi
- **Ticket:** GH-147 (theo brief `docs/pm/tickets/GH-147-render-agy.md`).
- **Mục tiêu:** Kiểm tra khung hình render thực tế của một chương Long có cảnh sử dụng ảnh AI sau khi code GH-147 (commit `e97506f`) gỡ bỏ nhãn `ẢNH MINH HỌA` đối với MIM/CK, đồng thời bảo đảm:
  1. Không còn chữ "MINH HỌA" trên ảnh AI.
  2. Không in dòng "ẢNH: TƯ LIỆU · PHẠM VI CÔNG CỘNG" (giữ `credit: false`).
  3. Ảnh thật và clip tư liệu/b-roll vẫn giữ đúng nhãn như cũ.
- **Quy tắc tuân thủ:** Không upload, không sửa state/lịch, không đụng git, không sửa code dùng chung, không sửa spec.

---

## 2. Lựa chọn topic và lý do

### Topic ban đầu: `ck-f3-tien-mung-cuoi` (CK) — Bị từ chối
Khi kiểm tra dựng HTML với `ck-f3-tien-mung-cuoi`, topic gặp các lỗi sau từ chính file spec và dữ liệu của topic:
- `ch00`: `ValueError: cảnh 0 (heat) quá ngắn: 0.00-0.00 — cảnh 1 (counter) neo at=0 trùng mốc với cảnh 0`
- `ch01`: `ValueError: cảnh 2 (bars) quá ngắn: 9.68-9.68 — cảnh 3 (counter) neo at=2 trùng mốc với cảnh 2`
- `ch04`: `IndexError: list index out of range`
- Thiếu audio / timing cho `ch05` và `ch06` (`output/long/ck-f3-tien-mung-cuoi/ch05/timing.json` không tồn tại).

Do luật ticket mục 4 ("Không sửa code hay spec. Lỗi thì ghi vào báo cáo"), agent không được tự ý sửa đổi file spec. Vì vậy, áp dụng điều khoản mục 1 của brief: chọn topic Long khác có ảnh trong `output/long/<topic>/img/ai*.jpg`.

### Topic thay thế: `mim-jobs-1985` (MIM) — Được chọn
- Đã có đầy đủ bộ ảnh AI: `output/long/mim-jobs-1985/img/ai01.jpg` đến `ai06.jpg`.
- Đã có đầy đủ dữ liệu audio, voice và timing cho toàn bộ các chương (`ch00` đến `ch08`).
- Chương `ch06` sử dụng ảnh AI `ai05` (trong spec `data/long/mim-jobs-1985/ch06.json` cảnh số 2 được khai báo `"illus": "ẢNH MINH HỌA"`, `"credit": false`), đáp ứng đúng 100% điều kiện thử nghiệm của ticket #147.

---

## 3. Quá trình thực hiện và lệnh đã chạy

1. **Chuẩn bị môi trường font chữ:**
   - Lệnh lint HTML yêu cầu font `Inter-900.ttf` và `Inter-700.ttf` cho theme `steel`/`lab` của MIM trong `motion/long/fonts/`.
   - Đã tải bộ font Inter chính thức từ Google Fonts đặt vào `motion/long/fonts/` theo đúng chỉ dẫn của lint error.
2. **Dựng HTML composition:**
   - Đã tạo `motion/hf/compositions/long/mim-jobs-1985_ch06.html` và nạp dữ liệu cảnh vào `output/long/mim-jobs-1985/ch06/data.js`.
   - Kiểm tra `data.js`: Cảnh `ai05` tại giây 6.41 - 10.14 đã được hàm `strip_ai_illustration_labels` gỡ bỏ hoàn toàn trường `"illus"`, giữ nguyên `"credit": false`.
3. **Render bản nháp chương (Draft Render):**
   - Chạy lệnh render:
     ```bash
     python motion/long/build_long.py mim-jobs-1985 render ch06 --draft --force
     ```
   - Kết quả: Tiến trình HyperFrames render thành công trong 282s.
   - File xuất bản: `output/long/mim-jobs-1985/ch06/draft.mp4` (14.135.529 bytes, thời lượng 86.37s).

---

## 4. Kết quả kiểm tra khung hình thực tế (Visual Audit)

Đã trích xuất các khung hình và contact sheet từ `output/long/mim-jobs-1985/ch06/draft.mp4`:
- `output/long/mim-jobs-1985/ch06/snapshot_08s5_ai05.jpg` (khung hình tại giây 8.5, lúc ảnh AI `ai05` đang hiển thị trọn vẹn).
- `output/long/mim-jobs-1985/ch06/snapshot_07s5_ai05.jpg` (khung hình tại giây 7.5).
- `output/long/mim-jobs-1985/ch06/snapshot_05s_broll.jpg` (khung hình tại giây 5.0, lúc cảnh clip b-roll đang hiển thị).
- `output/long/mim-jobs-1985/ch06/contact_sheet_ai.jpg` (tờ contact sheet 6 khung 3x2 trải từ giây 5.0 đến 11.0).

### Đánh giá từng điểm soát theo brief:
| Tiêu chí | Kết quả | Chi tiết kiểm tra |
|---|---|---|
| **Không có chữ "MINH HỌA" trên ảnh AI** | **ĐẠT** | Góc trên bên phải (vị trí lớp `.illus` theo CSS) hoàn toàn trống. Không xuất hiện chữ "ẢNH MINH HỌA" hay "MINH HỌA". |
| **Không có "TƯ LIỆU · PHẠM VI CÔNG CỘNG" trên ảnh AI** | **ĐẠT** | Không có dòng ghi nguồn tư liệu ở góc dưới trái (giữ `credit: false`, `ctext` là `null`). |
| **Clip và ảnh thật vẫn giữ đúng nhãn** | **ĐẠT** | Cảnh clip b-roll tại giây 5.0 (trước cảnh AI) vẫn hiển thị sắc nét nhãn `VIDEO MINH HỌA` ở góc trên bên phải. Nhãn hạ tầng lower-third (`HAI ỨNG VIÊN / BEOS · HỆ ĐIỀU HÀNH CỦA NEXT`) vẫn hiển thị đầy đủ. |

---

## 5. Kết quả kiểm thử hồi quy

Chạy lại bộ test GH-147:
```bash
python -m pytest tests/test_gh147_ai_media.py -q -p no:cacheprovider
```
Kết quả:
`5 passed in 9.28s` (100% pass: MIM gỡ nhãn AI, ảnh thật giữ nhãn, CL giữ nguyên nhãn, sidecar dict, non-dict sidecar).

---

## 6. Ghi nhận lỗi engine (Dành cho Lead/Engine dev)

- **Lỗi `build_long.py` khi chạy với tham số chương lẻ (`only`):**
  Tại `motion/long/build_long.py:1030-1033`:
  ```python
  source_check = scene_params.validate_topic(
      ((name, ch.get("scenes") or []) for name, ch in chs if not only or name in only),
      spec.get("imgs") or {}, THEME["name"], check_scenes=False,
  )
  ```
  Khi người dùng chỉ định chạy lệnh `html <chNN>`, `chs` bị lọc chỉ còn đúng chương đó, nhưng lại truyền toàn bộ `spec.imgs` của cả video vào `validate_topic`. Hàm `validate_topic` sẽ báo lỗi `spec.imgs: ảnh '<key>' không có cảnh nào dùng` đối với tất cả các ảnh được sử dụng ở các chương khác, khiến lệnh `html <chNN>` cho một chương đơn lẻ luôn thất bại.
