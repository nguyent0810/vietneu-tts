# GH-248 — Báo cáo storytelling v2

1. Đặt hàng rào nguồn cho chi tiết giác quan, thời điểm, động cơ, suy nghĩ và lời thoại; yêu cầu nhận diện ngay nhân vật và số giả định CK; đổi cách đảo kỳ vọng thành nhận định có căn cứ rồi dùng chứng cứ làm rõ.
2. Tách khuyến nghị chung, luật series CL GH-248, quy trình/cổng Long và profile BUD, dẫn file gốc; chuyển cold open, vị trí cú lật và kết mở thành lựa chọn.
3. Thêm stakes và góc nhìn có nguồn, hành động/vật chứng, thang cụ thể, bảng lời hứa → bằng chứng → vị trí trả, yêu cầu Short tự trả ít nhất một thông tin và hướng dẫn nghe TTS đúng giọng.
4. Thêm checklist 10 câu Có / Không ở cuối guide.
5. Viết ví dụ trước/sau theo mẫu phản biện, đối chiếu factcheck Đông Lăng; v1 45 dòng, v2 59 dòng, không quá hai lần v1.

## Nguồn và giới hạn

Đã mở https://en.wikipedia.org/wiki/Sun_Dianying và https://en.wikipedia.org/wiki/Eastern_Qing_tombs, đối chiếu `data/long/dong-lang/factcheck.md`. Trang về Tôn Điện Anh hiện xác nhận kế hoạch cướp lăng năm 1928, nhưng không tìm thấy thông tin phiên tòa tạm đình chỉ hoặc việc không ai bị kết án. Vì vậy không dùng hai kết luận này trong ví dụ v2; cần nguồn khác đã mở trước khi đưa trở lại. Ví dụ CK là tình huống giả định, không xác nhận phép tính hay dựng lời thoại.

## Kiểm tra và phạm vi

Đã dùng Python đọc/ghi UTF-8, đếm dòng và kiểm tra ký tự thay thế, dấu hỏi khả nghi; kết quả được kiểm sau khi ghi. Không chạy lint kịch bản hoặc render vì ticket chỉ sửa tài liệu. Không sửa code, spec, data; không đăng, commit hay đổi lịch. Cố ý không triển khai P2 (lint theo profile, thử nghiệm mở bài có đo lường) hoặc P3 (công cụ ánh xạ lời hứa/factcheck); bảng trong guide chỉ là hướng dẫn nội bộ thuộc P1, không phải triển khai công cụ hay thử nghiệm P3.
