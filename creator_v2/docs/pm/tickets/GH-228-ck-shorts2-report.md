# GH-228 — báo cáo tiến độ, chưa hoàn tất

Đã tạo 3 trong 11 spec, đều là loại L. Chưa tạo 8 spec còn lại: 1 L cho `ck-f2-vien-phi-bhyt`, 2 L cho `ck-f4-vo-chong-chia-tien` và 5 S độc lập. Chưa đủ điều kiện bàn giao lô.

| Spec | Ảnh kho chung | Preflight cuối | Lint lời |
|---|---|---|---|
| `ck-f1-60-phan-tram-luong-dong` | `lib198/ai_21.png` | OK, 107 từ, 32,4 giây ước lượng | 0 lỗi, 7 cảnh báo |
| `ck-f1-bac-thang-tro-cap` | `lib198/ai_37.png` | OK, 96 từ, 29,1 giây ước lượng | 0 lỗi, 7 cảnh báo |
| `ck-f2-bhyt-nam-nam-lien-tuc` | `lib198/ai_40.png` | OK, 111 từ, 33,6 giây ước lượng | 0 lỗi, 8 cảnh báo |

Các cảnh báo lint còn lại gồm câu hoặc mệnh đề dài, thiếu móc giữa bài, thiếu liên hệ về hook và yêu cầu câu cuối là câu hỏi. Brief yêu cầu kết bằng câu chốt, không câu hỏi; cần biên tập lại các câu dài trước khi dựng. Không có lỗi lint. Preflight ước lượng thời lượng, chưa đo được giọng đọc thực tế.

Đã đọc ba kịch bản Long, so danh sách tiêu đề CK có sẵn và tra kho bằng `python ../library/tools/assets.py find --tag ck --kind img --top 200 --json`; ba ảnh được chọn có tag `ck`, khác nhau và không trùng chín ảnh trong báo cáo GH-180. Lời và nguồn của ba bài ở `GH-228-ck-shorts2-lines.md`; script ghi spec là `GH-228-ck-shorts2-work.py`. Nguồn luật việc làm và bài BHXH về điều kiện năm năm đã mở và đối chiếu. Ba bài lấy quy tắc có thật từ kịch bản Long, không sử dụng số tiền giả định. Nguồn VBPL về hôn nhân trong factcheck Long bị từ chối truy cập; chưa dùng nguồn đó để viết khẳng định mới.

Đã chạy `python docs/pm/tickets/GH-228-ck-shorts2-work.py`; sau chỉnh cảnh, chạy `python motion/stier/build.py --preflight <slug>` cho ba spec và đều exit 0. Lần đầu `ck-f1-bac-thang-tro-cap` không đạt do cảnh chữ 37%; sau đổi cảnh thì đạt. Đã chạy `PYTHONPATH=. python motion/stier/script_lint.py <slug>` cho ba bài, tất cả exit 0; số cảnh báo ở bảng trên. Đã kiểm đọc UTF-8/JSON và tìm ký tự thay thế, chuỗi dấu hỏi và dấu hiệu mojibake trong ba spec: không phát hiện; đây là kiểm tra giới hạn, không chứng minh mọi chữ đúng dấu.

Chưa render theo brief: không có clip sheet hay thumbnail cho lô này; chưa thể kiểm hình thực tế, chuyển động hoặc độ đọc ở 360 px. Không enqueue, upload, commit, sửa lịch hay ghi `state.sqlite`. Cần hoàn thiện tám bài còn thiếu, kiểm nguồn đã mở và không trùng chủ đề, chạy preflight và lint cho tất cả rồi cập nhật báo cáo trước khi bàn giao.
