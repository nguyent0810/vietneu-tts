# Long phải qua bước soát SEO trước khi đăng; spec dựng khai keyword chính

Trạng thái: đã chấp nhận (24/10/2026, PR #29).

Audit ticket 69 trên 562 video (25/09–22/10) cho thấy nhiều Long FS/BUD thiếu những thứ cơ bản:

- thiếu mốc chương: 165/225;
- tiêu đề dài hơn 60 ký tự: 157/196;
- mô tả dưới 200 từ: 153/203;
- hơn 5 hashtag: 97/138;
- dưới 8 tag: 65/101.

Không spec dựng nào khai keyword chính, nên không ai kiểm được keyword có nằm ở đầu tiêu đề và đầu mô tả hay không.

`seo_check.check_row` chạy trong `upload_long.py` ở mọi lần chạy thử và chạy thật.

- **ERROR thì dừng đăng** (bỏ qua bằng `--seo-ok`):
  - keyword không nằm trong 4 từ đầu tiêu đề;
  - keyword không nằm trong 150 ký tự đầu mô tả;
  - hơn 60 hashtag (YouTube bỏ qua toàn bộ);
  - thumbnail không phải 1280×720, hoặc nặng hơn 2 MiB.
- **WARN**:
  - tiêu đề dài hơn 60 ký tự;
  - dưới 8 tag, hoặc tag đầu không trùng keyword;
  - hơn 5 hashtag;
  - thiếu mốc chương;
  - keyword không có trong 3 câu đầu lời đọc (khoảng 30 giây).

## Các phương án đã cân nhắc

- **Soát SEO bằng mắt.** Số liệu audit cho thấy cách này không giữ được.
- **Chặn cứng tiêu đề dài hơn 60 ký tự.** Khuôn "X Ngoài Đời Thật: … — …" của ADR 0001 thường dài 70–90 ký tự vì cần mỏ neo cộng chi tiết tò mò. Ngưỡng 60 lấy từ khuyến nghị, chưa có số kênh xác nhận, nên chỉ cảnh báo.

## Hệ quả

- Spec dựng Long khai `"seo": {"keyword": "..."}`, và tag đầu trùng keyword.
- Mô tả có sẵn:
  - mục lục chương lấy từ giờ thật;
  - ghi nguồn ảnh và đúng bài nhạc đã trộn;
  - dòng "Một số hình minh hoạ được tạo bằng AI";
  - phần "Xem tiếp" chỉ link tới video đã công khai trước ngày lên sóng.
- Hai Long thử đăng 24/10 chưa khai keyword (WARN `KEYWORD_MISSING`). Từ tập sau phải khai.
- Thử thumbnail A/B bằng "Test & Compare" của YouTube cần Long công khai và quyền Advanced Features; quyền này chưa kiểm.

## Bằng chứng

`seo_check.py`, `tests/test_seo_check.py`, `output/cl_staging/grok/reports/69_seo_title_thumb_audit.md`, skill `long-video` §8, commit `7fb3867`.
