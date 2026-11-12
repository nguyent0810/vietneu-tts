# GH-277 — báo cáo Codex

**Trạng thái: chưa đạt toàn bộ tiêu chí; cần Lead xử lý và kiểm lại trước khi merge.** Không render, không commit, không đăng và không đổi lịch.

## Đã làm

- `motion/long/kinetic_style.py` (mới): chọn tất định cho item kinetic/chữ phủ và slam; giữ `fx`, `style` viết tay; không thay dữ liệu khi tắt. Khớp mốc từng từ trong cảnh cho sync, chuyển từ nhấn sang `emw`; tự nhận diện KHÔNG PHẢI, CHẲNG PHẢI, ĐỪNG, SAI để bật gạch.
- `motion/hf/assets/engine/beat.js`, `beat.css`: thêm tám ID hiệu ứng, bảy kiểu chữ và gạch cho đường đi mới. Dùng timeline có sẵn, không thêm đồng hồ hay số ngẫu nhiên mới. Không tải font mới; dùng họ font của look hiện hành.
- `motion/long/build_long.py`: chọn sau khi cảnh đã được lập và sau cine_auto, bật mặc định cho topic mới, topic legacy tắt nếu không chủ ý bật `kinetic_auto`; in phân bố theo chương và tổng lượt chạy, cảnh báo khi thiếu đa dạng hoặc vượt 20%.
- `motion/long/README.md`: khóa, ví dụ, luật xoay và giới hạn. `tests/test_kinetic_style.py` (mới): sáu test.
- Đã đọc mô tả PR #294 và #293 bằng `gh pr view --repo nguyent0810/vietneu-tts`: #294 là bước gợi ý ở kế hoạch, #293 là gợi ý style và hook engine; bộ chọn này không tạo hay đổi loại cảnh.

## Phân bố mẫu

Mẫu kiểm thử 40 dòng kinetic trong một chương, không ép hiệu ứng; tổng 40:

| Hiệu ứng | Số dòng |
|---|---:|
| depth-parallax-words | 4 |
| drop | 4 |
| per-word-crossfade | 4 |
| stagger-from-center | 4 |
| blur, flip, focus-blur-resolve, kinetic-center-build, mask-reveal-up, pop, rise, shimmer-sweep | 3 mỗi kiểu |

Kiểu chữ: duo 6, editorial 6, gold 6, marker 5, outline 6, poster 6, solid 5. Không có sync trong mẫu này vì mẫu không có lời đọc; test riêng kiểm tra sync khi có và khi thiếu mốc. Đây là dữ liệu thử, không phải bảng của một video thực.

## Cổng kiểm

- Trước sửa: `python -m pytest tests -q --basetemp=tmp_pytest -p no:cacheprovider`, dùng Python của brief. Tiến trình đã có nhiều E và F trước khi sửa, sau đó pytest bị `PermissionError: [WinError 5] Access is denied` khi dọn `tmp_pytest`; không in tổng kết.
- Sau sửa: `python -m pytest tests -q --basetemp=tmp_pytest_277_after -p no:cacheprovider`: cũng nhiều E/F, rồi cùng lỗi quyền khi pytest dọn thư mục tạm mới; không có tổng kết. Chưa chứng minh được không thêm test đỏ. Chạy `-x` với thư mục tạm khác cũng kết thúc ở lỗi quyền dọn thư mục.
- `python -m pytest tests/test_kinetic_style.py -q --basetemp=tmp_pytest -p no:cacheprovider`: **6 passed** sau các thay đổi.
- `python -m py_compile motion/long/kinetic_style.py motion/long/build_long.py tests/test_kinetic_style.py`: đạt.
- `rg` kiểm các mẫu lỗi mã hóa KH?NG, PH?I, CH?NG trong file mới và README: không thấy. Không chạy lint HTML topic vì ticket không chọn topic và bước html sẽ tạo sản phẩm topic; không kiểm JavaScript qua Node/Chrome theo giới hạn brief. Chưa chạy `build_long.py <topic> html` thực tế, nên bảng in từ builder chưa được xác nhận đầu-cuối.
- So sánh legacy bằng cờ `enabled=False` trong test: đầu vào không đổi. Chưa dựng/so chuỗi HTML golden hoặc so khung hình.
- HyperFrames CLI/registry không chạy: brief nói sandbox không chạy Node/Chrome và yêu cầu tự viết hiệu ứng trong beat.js. Tài liệu tham chiếu `.claude/skills/motion-library/SKILL.md` không tồn tại tại đường dẫn issue nêu.

## Còn thiếu và rủi ro cần Lead quyết

1. **Quote chưa hỗ trợ:** `B.quote` trong `casewide.js` trực tiếp tạo các span gõ chữ, không gọi `makeBeat`; brief không cho sửa `casewide.js`. Cần mở rộng phạm vi hoặc Lead sửa hook phù hợp. Slam có hiệu ứng viết tay thuộc bộ cũ cũng chưa áp typestyle, vì đường đi cũ không gọi beat.
2. Bộ chọn cân bằng theo từng chương và cảnh báo các giới hạn, chưa cưỡng chế được 4 hiệu ứng/chương hoặc ≤20% trên toàn video trong mọi trường hợp, nhất là chương quá ngắn hoặc có lựa chọn viết tay; kết quả chọn một chương độc lập không phụ thuộc các chương được dựng cùng. Cần bộ phân bổ toàn bài ổn định với lệnh dựng từng chương, vẫn tôn trọng dữ liệu viết tay.
3. Look hiện tham gia hạt chọn và các kiểu dùng font hiện có, nhưng chưa có bảng tương thích kiểu/look được kiểm hình. `duo` chỉ đổi cỡ với hiệu ứng dựng span theo từ; poster dùng họ sans hiện có chứ chưa đảm bảo kiểu cao hẹp ở mọi look. Font của các look và việc đo tràn cho serif/typestyle mới chưa được mở rộng trong `KIN_FONTS`. Cần Lead rà font OFL tiếng Việt, bề rộng và bổ sung khi cần.
4. `sync` lấy mốc từ `word_lines` hiện hữu, vốn ước lượng theo năng lượng/trọng số, không phải bằng chứng mốc STT chính xác tuyệt đối. Cần so với giọng thực. Gạch vế trước dấu · được ước lượng theo tỷ lệ số ký tự; cần soi hình thực. Chưa kiểm tính tua/hiệu ứng bằng trình duyệt và chưa đánh giá va chạm với beat2/layout qua render. Các hiệu ứng mới chưa được kiểm hình; không coi báo cáo test Python là nghiệm thu hình.
5. Đã sửa `beat.js/css` dùng chung nên hàm render key của repo có thể thay đổi hash engine dù cờ mới tắt. Đầu ra hình topic cũ chưa được so sánh thực tế; Lead cần so golden theo brief.

Không có khẳng định nội dung video cần factcheck. Không có clip sheet hoặc thumbnail: ticket cấm render.

## Lệnh để Lead dựng thử

Thay `TOPIC_MOI` bằng topic mới đã có TTS và chương phù hợp, rồi chạy lần lượt trong PowerShell; cần so với bản trước sửa và xem bảng phân bố:

```powershell
$topic = "TOPIC_MOI"
& "D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe" motion/long/build_long.py $topic html ch01
& "D:\Tools\Youtube Creator v2\vietneu-main\creator_v2\.venv\Scripts\python.exe" motion/long/build_long.py $topic render ch01 --draft
```
