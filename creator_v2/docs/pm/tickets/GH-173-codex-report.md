# GH-173 — Báo cáo Codex

## Thay đổi

- `motion/hf/assets/engine/casefile.js`: dựng nhãn riêng trong cảnh CK, MIM, CL; lấy nội dung từ spec, escape chữ, cho nhãn vào timeline của cảnh. Chuyển động vào theo mockup; khi cảnh kết thúc, nhãn mờ cùng cảnh. MIM có dấu nhắc và con trỏ nhấp nháy.
- `motion/hf/assets/engine/casefile.css`: thêm ribbon CK, terminal bracket MIM, evidence tape CL; dùng chung biến `--caption-size` cho tiêu đề nhãn và subtitle. Nhãn được đặt ở góc trên, giới hạn chiều rộng, không đặt tại vùng subtitle.
- `motion/stier/build.py`: thêm cảnh báo preflight không chặn build khi chữ giả định nằm trong trường nhỏ, và kiểm tra liên kết cỡ chữ CSS của nhãn với subtitle. Không chuyển cảnh báo thành lỗi.
- `tests/test_hypo_label_173.py`: kiểm tra cảnh báo, không cảnh báo khi có nhãn, kích thước CSS, và DOM do engine tạo cho ba theme bằng Node với DOM/timeline giả.
- `docs/pm/tickets/GH-173-codex-report.md`: báo cáo này.

Không sửa spec cũ: nội dung trong `sub`, `note`, `unit` vẫn dựng như trước.

## Cách dùng

Thêm vào từng cảnh; `hypo: true` hiển thị mặc định “VÍ DỤ GIẢ ĐỊNH”, chuỗi `hypo` thay chữ mặc định, còn `hypo_sub` là dòng phụ tùy chọn:

```json
{"type":"chart", "hypo":true, "hypo_sub":"Phép tính minh họa"}
```

Ví dụ chữ riêng: `"hypo": "TÌNH HUỐNG GIẢ ĐỊNH"`. Nên giữ chữ ngắn để không chiếm vùng nội dung cảnh; chuỗi dài sẽ xuống dòng và cần QA bố cục.

Cảnh báo xét `note`, `unit`, `sub` và các `title` có cỡ nhỏ theo loại cảnh; title board phụ thuộc look, nên phép kiểm board hiện chỉ cảnh báo khi cả hệ số bề rộng nhỏ nhất cũng cho cỡ dưới subtitle. Cỡ thực tế của title board theo look vẫn cần Lead kiểm thêm. Cảnh báo xuất trên stdout trong cả preflight và build, không làm đổi mã thoát.

## Kiểm tra

- `python -m pytest tests/test_hypo_label_173.py tests -q -k "stier or build or hypo or preflight"`: **3 passed, 1 warning**. Warning do pytest không ghi được cache (WinError 5). Lệnh này trong môi trường hiện tại chỉ thu thập ba test ở file được nêu riêng; không coi kết quả này là toàn bộ test của thư mục.
- Chạy thêm `python -m pytest tests/test_stier_scene_types.py tests/test_stier_build_gates.py tests/test_ck_stier.py tests/test_mim_stier.py -q -p no:cacheprovider`: **139 passed, 2 skipped, 19 errors**; các lỗi setup `tmp_path` do WinError 5 ở thư mục tạm pytest.
- Chạy thêm toàn bộ `tests` với cùng bộ lọc và `--basetemp` riêng: pytest cũng gặp WinError 5 trên thư mục tạm và lỗi khi kết thúc, không có tổng kết đáng tin cậy. Cần chạy lại trên máy Lead có quyền thư mục tạm.
- Chưa render hoặc chụp QA theo ticket. Test DOM giả không đo khung hình, font thực tế, vùng an toàn, hay va chạm với nội dung; agy cần chụp QA ba theme, đặc biệt với nhãn/dòng phụ dài. Chưa thể xác nhận bố cục thực tế hoặc chất lượng chuyển động.
- Không có khẳng định nội dung mới cần fact-check. Không có clip sheet hoặc thumbnail vì ticket cấm render. Không chạy lint kịch bản vì không sửa spec Short.

Không commit, upload, thay đổi lịch hoặc sửa video đã đăng.
