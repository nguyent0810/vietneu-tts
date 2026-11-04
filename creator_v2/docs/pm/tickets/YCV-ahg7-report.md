# YCV-ahg7 — báo cáo scene rules Long MIM/CK

## Vòng 2: đã sửa gì

- Đã sửa `motion/long/scene_rules.py` theo contract của `casewide.js`, không còn so với `longform.js` hay `engine.js` cũ.
- Đã bỏ hẳn luật coi `photo` không có `move`/`zoom` là lỗi. `photo` thiếu `move` có hiệu ứng thực tế là `move: "in"`.
- Hai ảnh đứng liền nhau có cùng hiệu ứng thực tế (kể cả `in` mặc định) nhận đề xuất đổi hiệu ứng. Patch cho `photo` dùng `move: "in"|"out"|"pan"`; với `print` lặp, patch đổi sang `type: "photo"` cùng `move` hợp lệ vì `B.print` không có biến thể `move`.
- Ảnh dài hơn 8 giây nhận hiệu ứng bổ sung ở đầu câu gần giữa cảnh: `photo` ưu tiên `zoom`, đã có `zoom` thì dùng `reveal`; `print` nhận `circles` để khoanh chi tiết. Chỉ khi dài hơn 12 giây mới đề xuất `replacement_scenes` để chia shot tại đầu câu, mỗi phía tối thiểu 2,5 giây.
- Các patch/replacement scene chỉ dùng trường engine đọc: `type`, `at`, `move`, `zoom`, `reveal`, `circles` và các trường sẵn có của scene gốc. Không còn xuất preset trung gian `missing_motion`, `suggested_move` hay `shots`.
- Đã cập nhật `tests/test_long_scene_rules.py` với dữ liệu giả: hiệu ứng `in` mặc định, ngưỡng 8/12 giây, `circles` của `print`, và fallback `reveal` khi ảnh đã có `zoom`.

## So engine

| Hạng mục `motion_picker` | `casewide.js` Long | Cách `scene_rules.py` xuất đề xuất |
|---|---|---|
| `slow_zoom` | `photo.move`: mặc định `"in"` (scale 1 → 1,12), có `"out"` | Patch `move: "in"` hoặc `"out"`; khi so lặp tính cả mặc định `in` |
| `pan_focus` | `photo.move: "pan"` | Patch `move: "pan"` |
| `push_detail` | `photo.zoom: {x, y, z, at, d}` | Patch `zoom` ở đầu câu giữa cảnh; tâm và vùng phóng là giá trị để producer rà theo lời đọc |
| `reveal` | `photo.reveal: {kind: "wipe"|"circle", at, d}` | Patch `reveal` dạng `wipe` khi ảnh dài đã có `zoom` |
| `highlight` | `photo.circles` | Patch `circles` để khoanh chi tiết cho `print` dài; producer đặt lại tâm khoanh cho đúng chi tiết lời đọc |
| `parallax` | Chưa có trường/treatment tương ứng trong contract được ticket xác nhận | Không đề xuất và không tự đặt trường mới |
| `B.print` | Vào trong 0,5 giây rồi phóng nhẹ tới 1,04; không có `move` biến thể | Không báo “thiếu move”; khi quá 8 giây đề xuất `circles`, quá 12 giây mới chia shot |

Kết luận: không dùng nguyên payload preset của `motion_picker`, nhưng các quyết định tương ứng năm hiệu ứng có hỗ trợ được port thành patch của `casewide.js` để producer chép vào spec. Không cần adapter engine cho các field này. `parallax` chưa có nên không được đề xuất.

Nguồn quy tắc tham chiếu: `.ref/vietneu-main/library/tools/scene_picker.py` (log cảnh liền kề) và `.ref/vietneu-main/library/tools/motion_picker.py` (cắt theo ranh giới câu, thời lượng shot tối thiểu, chống lặp hiệu ứng); mapping runtime được xác nhận lại bởi brief vòng 2 cho `motion/hf/assets/engine/casewide.js`.

## Lệnh đã chạy

```text
python -m pytest tests/test_long_scene_rules.py -q -p no:cacheprovider
4 passed in 0.16s

python -m py_compile motion/long/scene_rules.py
thành công

python motion/long/scene_rules.py --all
60 topics; mọi topic có timing; đã ghi output/long/<topic>/scene_rules.json
```

Không còn lỗi test, lỗi cú pháp hay lint riêng của tiện ích. Không render, không thay spec, không chạy CL, không đổi lịch hay đăng YouTube.

## Top 10 theo số đề xuất

| # | Topic | Đề xuất | Cảnh báo lặp |
|---:|---|---:|---:|
| 1 | `mim-macintosh-1984` | 20 | 5 |
| 2 | `mim-ai-70` | 15 | 9 |
| 3 | `mim-katherine-johnson` | 13 | 2 |
| 4 | `mim-oppenheimer-feynman` | 12 | 1 |
| 5 | `mim-turing-bombe` | 11 | 3 |
| 6 | `mim-moneyball` | 9 | 0 |
| 7 | `mim-social-network` | 7 | 6 |
| 8 | `mim-ai-voice` | 6 | 40 |
| 9 | `mim-google-maps-kal007` | 6 | 1 |
| 10 | `mim-ai-gpu` | 5 | 22 |

Không có khẳng định nội dung cần fact-check trong ticket kỹ thuật này. Clip sheet và thumbnail: không áp dụng, vì ticket cấm render và không dựng thumbnail.
