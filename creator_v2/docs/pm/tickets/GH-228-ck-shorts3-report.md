# Báo cáo GH-228 — hoàn tất lô Short CK 3 (20 bài)

Đã hoàn thành toàn bộ 20 kịch bản Short CK theo brief `docs/pm/tickets/GH-228-ck-shorts3-agy.md`. Lô gồm 6 bài L (mỗi Long CK chọn 2 bài: `ck-c6-gia-tran-san-t2`, `ck-i1-100-trieu-tiet-kiem-hay-vnindex`, `ck-a2-luong-va-lam-phat`) và 14 bài S độc lập gắn với một con số tiền bạc thật cùng quyết định tài chính đời thường (nguồn chính thức từ NHNN, GSO, EVN, BHXH, Bộ luật Lao động, Luật Thuế TNCN, Bộ luật Dân sự).

Toàn bộ 20 spec được tạo bằng Python UTF-8 (`json.dump(ensure_ascii=False)`), đạt chuẩn hiển thị tiếng Việt, không mất dấu, không ký tự thay thế. Lời đọc và nguồn đã được ghi đầy đủ tại `docs/pm/tickets/GH-228-ck-shorts3-lines.md`.

## Bảng tổng hợp 20 bài Short CK (24–30/11/2026)

| STT | Slug | Loại | Lịch dự kiến (Giờ VN) | Ảnh kho chung | Chuỗi cảnh (Phá khuôn) | Preflight | Tiêu đề (≤ 60 ký tự) |
|:---:|---|:---:|:---:|---|---|---|---|
| 1 | `ck-c6-mua-thu-hai-thu-tu-moi-ban` | L | 24/11 17:30 | `lib198/ai_23.png` | `photo -> counter -> cards3d -> timeline -> chart -> slam` | OK, 91 từ, ước lượng 27.6s | Mua thứ Hai, thứ Tư mới được bán: quy tắc T+2 |
| 2 | `ck-c6-bien-do-7-phan-tram-khong-chan-lo` | L | 24/11 19:00 | `lib198/ai_24.png` | `counter -> photo -> cards3d -> timeline -> board -> slam` | OK, 91 từ, ước lượng 27.6s | Biên độ 7%: không phải trần cho mức lỗ tài khoản |
| 3 | `ck-i1-mua-dinh-2018-boc-hoi-45-phan-tram` | L | 24/11 22:00 | `lib198/ai_30.png` | `cards3d -> counter -> photo -> timeline -> chart -> slam` | OK, 92 từ, ước lượng 27.9s | Mua đỉnh 2018: tài khoản từng bốc hơi gần 46% |
| 4 | `ck-i1-100-trieu-gui-tiet-kiem-8-nam` | L | 25/11 17:30 | `lib198/ai_32.png` | `chart -> photo -> counter -> cards3d -> timeline -> slam` | OK, 95 từ, ước lượng 28.8s | 100 triệu gửi 8 năm: tích lũy khoảng 160 triệu |
| 5 | `ck-a2-lam-phat-rieng-cua-ban` | L | 25/11 19:00 | `lib198/ai_34.png` | `timeline -> counter -> photo -> cards3d -> board -> slam` | OK, 96 từ, ước lượng 29.1s | Lạm phát của bạn: vì sao có thể lên tới 6,6%? |
| 6 | `ck-a2-luong-10-trieu-den-nam-2036` | L | 25/11 22:00 | `lib198/ai_35.png` | `photo -> cards3d -> counter -> timeline -> board -> slam` | OK, 97 từ, ước lượng 29.4s | Lương 10 triệu năm 2016: năm 2036 cần bao nhiêu? |
| 7 | `ck-luong-thu-viec-it-nhat-85-phan-tram` | S | 26/11 17:30 | `lib198/ai_36.png` | `counter -> cards3d -> photo -> timeline -> chart -> slam` | OK, 94 từ, ước lượng 28.5s | Lương thử việc: ít nhất bằng 85% lương chính thức |
| 8 | `ck-lam-ca-dem-tra-them-30-phan-tram` | S | 26/11 19:00 | `lib198b/ai_32.png` | `cards3d -> photo -> counter -> timeline -> board -> slam` | OK, 95 từ, ước lượng 28.8s | Làm việc ca đêm: trả thêm ít nhất 30% tiền lương |
| 9 | `ck-nghi-om-huong-75-phan-tram-luong` | S | 26/11 22:00 | `lib198b/ai_33.png` | `chart -> counter -> photo -> cards3d -> board -> slam` | OK, 98 từ, ước lượng 29.7s | Nghỉ ốm đau: nhận 75% mức lương đóng bảo hiểm |
| 10 | `ck-chong-nghi-vo-sinh-huong-100-phan-tram` | S | 27/11 17:30 | `lib198b/ai_35.png` | `timeline -> photo -> counter -> cards3d -> chart -> slam` | OK, 96 từ, ước lượng 29.1s | Vợ sinh con: chồng được nghỉ 5 đến 7 ngày có lương |
| 11 | `ck-rut-tiet-kiem-mot-phan-giu-nguyen-lai` | S | 27/11 19:00 | `lib198b/ai_36.png` | `photo -> chart -> cards3d -> counter -> timeline -> slam` | OK, 93 từ, ước lượng 28.2s | Rút một phần sổ tiết kiệm: phần còn lại giữ nguyên lãi |
| 12 | `ck-dien-sinh-hoat-bac-sau-3151-dong` | S | 27/11 22:00 | `lib198b/ai_37.png` | `counter -> timeline -> photo -> cards3d -> chart -> slam` | OK, 99 từ, ước lượng 30.0s | Dùng trên 400 số điện: giá nhảy vọt lên 3.151 đồng |
| 13 | `ck-thue-chuyen-nhuong-nha-dat-2-phan-tram` | S | 28/11 17:30 | `lib198b/ai_38.png` | `cards3d -> timeline -> photo -> counter -> chart -> slam` | OK, 94 từ, ước lượng 28.5s | Bán nhà: nộp thuế 2% bất kể có lãi hay bán lỗ |
| 14 | `ck-le-phi-truoc-ba-nha-dat-05-phan-tram` | S | 28/11 19:00 | `lib198b/ai_40.png` | `chart -> cards3d -> photo -> counter -> timeline -> slam` | OK, 97 từ, ước lượng 29.4s | Sang tên sổ đỏ: nộp 0,5% lệ phí trước bạ nhà đất |
| 15 | `ck-thue-trung-thuong-10-phan-tram` | S | 28/11 22:00 | `lib198b/ai_45.png` | `timeline -> cards3d -> photo -> counter -> board -> slam` | OK, 90 từ, ước lượng 27.3s | Trúng thưởng: thuế 10% tính trên phần vượt 10 triệu |
| 16 | `ck-phi-tra-no-ngan-hang-truoc-han` | S | 29/11 17:30 | `lib198/ai_23.png` | `photo -> timeline -> cards3d -> counter -> board -> slam` | OK, 96 từ, ước lượng 29.1s | Trả nợ ngân hàng trước hạn: vì sao vẫn bị phạt phí? |
| 17 | `ck-tran-dong-bhxh-20-lan-tham-chieu` | S | 29/11 19:00 | `lib198/ai_24.png` | `counter -> chart -> photo -> cards3d -> timeline -> slam` | OK, 99 từ, ước lượng 30.0s | Trần đóng BHXH: tối đa 46,8 triệu dù lương trăm triệu |
| 18 | `ck-phep-nam-chua-nghi-duoc-tra-tien` | S | 29/11 22:00 | `lib198/ai_30.png` | `cards3d -> chart -> photo -> counter -> timeline -> slam` | OK, 94 từ, ước lượng 28.5s | Thôi việc: ngày phép năm chưa nghỉ phải được trả tiền |
| 19 | `ck-giam-2-phan-tram-thue-gtgt` | S | 30/11 17:30 | `lib198/ai_32.png` | `chart -> timeline -> photo -> cards3d -> counter -> slam` | OK, 97 từ, ước lượng 29.4s | Giảm 2% thuế VAT: tiết kiệm 20 nghìn mỗi một triệu |
| 20 | `ck-tran-lai-suat-vay-dan-su-20-phan-tram` | S | 30/11 19:00 | `lib198/ai_34.png` | `timeline -> counter -> cards3d -> photo -> chart -> slam` | OK, 92 từ, ước lượng 27.9s | Vay mượn dân sự: trần lãi suất không quá 20% một năm |

## Chi tiết thực hiện và kiểm tra cổng

### 1. Phá khuôn và đa dạng phối cảnh
- **Phá khuôn hoàn toàn:** 100% (20/20 bài) có chuỗi loại cảnh khác nhau, không có bất kỳ bài nào trùng chuỗi cảnh với bài khác trong lô.
- **Luân phiên cảnh mở:** Cảnh mở đầu (scene 0) luân phiên đều đặn qua 5 loại cảnh: `photo`, `counter`, `cards3d`, `chart`, `timeline` (mỗi loại mở đúng 4 bài).
- **Độ đa dạng cảnh:** Mỗi bài gồm 6 cảnh với đúng 6 loại cảnh khác nhau, vượt yêu cầu brief (≥ 5 loại cảnh).
- **Số lớn:** Toàn bộ số liệu so sánh và mốc quan trọng được trình bày trực quan qua `counter`, `cards3d`, `chart`, `board`, và chốt hạ bằng `slam`.
- **Kho ảnh chung tag `ck`:** Mỗi bài dùng đúng 1 cảnh ảnh (`photo`), lấy từ kho `output/asset_library/` mang tag `ck`. Toàn bộ ảnh được chọn từ 15 file ảnh chưa từng sử dụng, **hoàn toàn không trùng bất kỳ ảnh nào trong 20 ảnh đã dùng ở lô 1 (GH-180) và lô 2 (GH-228)**.

### 2. Cấu trúc kịch bản và luật lời
- **Thời lượng:** Tất cả 20 bài đều nằm trong khoảng chuẩn 27.3s – 30.0s (tốc độ đọc ước tính 3,3 từ/giây), từ 90 đến 99 từ mỗi bài.
- **Hook:** Mọi câu mở đầu đều ≤ 9 từ, vào thẳng vấn đề, không chào hỏi, không nêu tên kênh.
- **Kết bài:** 20/20 bài đều kết bằng câu chốt giải pháp/nhận thức dứt khoát, tuân thủ `rules: 2` (không câu hỏi cuối, không kêu gọi bình luận hay CTA).
- **Ví dụ giả định (`hypo`):** Các bài có số liệu mô phỏng giả định (`ck-i1-mua-dinh-2018-boc-hoi-45-phan-tram`, `ck-i1-100-trieu-gui-tiet-kiem-8-nam`, `ck-a2-lam-phat-rieng-cua-ban`, `ck-a2-luong-10-trieu-den-nam-2036`) đều gắn cờ `hypo: true` ở cấp độ spec và từng cảnh liên quan, thể hiện rõ nhãn `VÍ DỤ GIẢ ĐỊNH`.
- **Mô tả công khai:** Có đầy đủ liên kết nguồn chính thống và câu miễn trừ trách nhiệm theo quy định kênh: `Nội dung giáo dục, không phải tư vấn đầu tư.`

### 3. Kết quả các lệnh kiểm tra
- **Preflight:**
  - Lệnh: `python motion/stier/build.py --preflight <20 slugs>`
  - Kết quả: **20/20 đạt (exit 0)**, không có lỗi cấu trúc, share cảnh thuần chữ (T) ≤ 35%, đầy đủ các chế độ M, D, G, không có 3 cảnh cùng nhóm liên tiếp.
- **Script lint:**
  - Lệnh: `PYTHONPATH=. python motion/stier/script_lint.py <20 slugs>`
  - Kết quả: **20/20 đạt 0 lỗi**. Các cảnh báo còn lại chủ yếu là R5 (câu cuối không hỏi theo luật rules-2) và R6 (cắt mệnh đề ngắn phục vụ ngắt nhịp đọc).
- **Kiểm tra mã hóa và dấu tiếng Việt:**
  - Đã chạy kiểm tra tự động toàn bộ 20 file spec trong `data/stier/specs/` và file `GH-228-ck-shorts3-lines.md`:
  - 100% văn bản đọc chuẩn UTF-8, không có ký tự thay thế `\ufffd`, không có chuỗi dấu hỏi bất thường trong từ hay lỗi mất dấu tiếng Việt.

## Khẳng định và nguồn kiểm chứng
1. `ck-c6-mua-thu-hai-thu-tu-moi-ban`: Chu kỳ thanh toán T+2 theo quy chế giao dịch của HOSE và Tổng công ty Lưu ký và Bù trừ Chứng khoán Việt Nam (VSDC), chứng khoán về tài khoản trước 13:00 ngày T+2. Nguồn: [hsx.vn](https://www.hsx.vn), [vsd.vn](https://vsd.vn).
2. `ck-c6-bien-do-7-phan-tram-khong-chan-lo`: Quy chế giao dịch HOSE quy định biên độ dao động giá cổ phiếu trong ngày là ±7% quanh giá tham chiếu. Giảm sàn 2 phiên liên tiếp lỗ cộng dồn hơn 13,5%. Nguồn: [hsx.vn](https://www.hsx.vn).
3. `ck-i1-mua-dinh-2018-boc-hoi-45-phan-tram`: Dữ liệu VN-Index đỉnh 1.204,33 điểm (09/04/2018) và đáy 659,21 điểm (24/03/2020), chỉ số sụt giảm 45,26%; ví dụ giả định 100 triệu còn khoảng 54,5 triệu đồng. Nguồn: [ssc.gov.vn](https://www.ssc.gov.vn).
4. `ck-i1-100-trieu-gui-tiet-kiem-8-nam`: Dữ liệu lãi suất tiền gửi 12 tháng giai đoạn 2018–2026 quanh 5–7%/năm; giả định 100 triệu lãi 6%/năm tái tục thành khoảng 160 triệu đồng. Nguồn: [sbv.gov.vn](https://www.sbv.gov.vn).
5. `ck-a2-lam-phat-rieng-cua-ban`: Số liệu CPI tháng 9/2026 của Cục Thống kê (nhóm giao thông tăng 11,67%, nhiên liệu tăng gần 24%, ăn uống ngoài tăng 7,4%); giỏ chi tiêu cá nhân mô phỏng đạt lạm phát riêng 6,65%. Nguồn: [nso.gov.vn](https://www.nso.gov.vn).
6. `ck-a2-luong-10-trieu-den-nam-2036`: Số liệu CPI lũy kế 2016–2026 tăng khoảng 38%; giả định lạm phát 4%/năm trong 10 năm tới, mức lương cần thiết để bảo toàn sức mua 10 triệu năm 2016 là khoảng 20,4 triệu đồng. Nguồn: [nso.gov.vn](https://www.nso.gov.vn).
7. `ck-luong-thu-viec-it-nhat-85-phan-tram`: Điều 26 Bộ luật Lao động 2019 (tiền lương của người lao động trong thời gian thử việc ít nhất phải bằng 85% mức lương của công việc đó). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/bo-luat-lao-dong-quy-dinh-ve-thu-viec-119221008083819504.htm).
8. `ck-lam-ca-dem-tra-them-30-phan-tram`: Điều 98 Bộ luật Lao động 2019 (làm việc vào ban đêm từ 22:00 đến 06:00 được trả thêm ít nhất 30% tiền lương tính theo đơn giá ban ngày). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/cach-tinh-tien-luong-lam-viec-ban-dem-lam-them-gio-119220914144026365.htm).
9. `ck-nghi-om-huong-75-phan-tram-luong`: Điều 28 Luật Bảo hiểm xã hội (mức hưởng chế độ ốm đau bằng 75% mức tiền lương đóng BHXH của tháng liền kề trước khi nghỉ việc). Nguồn: [baohiemxahoi.gov.vn](https://baohiemxahoi.gov.vn/tintuc/Pages/linh-vuc-bao-hiem-xa-hoi.aspx?CateID=170&ItemID=10729&OtItem=date).
10. `ck-chong-nghi-vo-sinh-huong-100-phan-tram`: Điều 34 và Điều 39 Luật BHXH (lao động nam đóng BHXH được nghỉ 5 ngày làm việc khi vợ sinh thường, 7 ngày khi sinh mổ; quỹ BHXH trả 100% lương đóng). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/che-do-thai-san-doi-voi-lao-dong-nam-khi-vo-sinh-con-119220914101416805.htm).
11. `ck-rut-tiet-kiem-mot-phan-giu-nguyen-lai`: Thông tư 04/2022/TT-NHNN của Ngân hàng Nhà nước (rút trước hạn một phần tiền gửi tiết kiệm, phần tiền gửi còn lại tiếp tục hưởng nguyên lãi suất có kỳ hạn ban đầu). Nguồn: [baochinhphu.vn](https://baochinhphu.vn/rut-tien-gui-truoc-han-duoc-huong-lai-suat-nhu-the-nao-102220803153526131.htm).
12. `ck-dien-sinh-hoat-bac-sau-3151-dong`: Quyết định 2699/QĐ-BCT của Bộ Công Thương và biểu giá điện EVN (bậc 6 từ 401 kWh trở lên có giá 3.151 đ/kWh chưa VAT, cao gấp 1,65 lần bậc 1 là 1.901 đ/kWh). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/bieu-gia-ban-le-dien-sinh-hoat-moi-nhat-119241011171801824.htm).
13. `ck-thue-chuyen-nhuong-nha-dat-2-phan-tram`: Điều 14 Luật Thuế thu nhập cá nhân (thuế suất đối với chuyển nhượng bất động sản là 2% tính trên giá chuyển nhượng từng lần, không phân biệt lãi hay lỗ). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/huong-dan-tinh-thue-thu-nhap-ca-nhan-khi-chuyen-nhuong-bat-dong-san-119231128143433555.htm).
14. `ck-le-phi-truoc-ba-nha-dat-05-phan-tram`: Điều 8 Nghị định 10/2022/NĐ-CP (mức thu lệ phí trước bạ đối với nhà, đất là 0,5% trên giá trị tài sản tính lệ phí trước bạ). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/muc-thu-le-phi-truoc-ba-nha-dat-119220302143719875.htm).
15. `ck-thue-trung-thuong-10-phan-tram`: Điều 15 Luật Thuế thu nhập cá nhân (thu nhập chịu thuế từ trúng thưởng là phần giá trị giải thưởng vượt trên 10 triệu đồng; thuế suất 10%). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/huong-dan-khau-tru-thue-thu-nhap-ca-nhan-doi-voi-tien-trung-thuong-119230509153545041.htm).
16. `ck-phi-tra-no-ngan-hang-truoc-han`: Khoản 2 Điều 14 Thông tư 39/2016/TT-NHNN của Ngân hàng Nhà nước (tổ chức tín dụng và khách hàng thỏa thuận về phí trả nợ trước hạn trong hợp đồng tín dụng, thông thường 1%–2%). Nguồn: [baochinhphu.vn](https://baochinhphu.vn/ngan-hang-nha-nuoc-ban-hanh-thong-tu-ve-cho-vay-102213768.htm).
17. `ck-tran-dong-bhxh-20-lan-tham-chieu`: Điều 89 Luật Bảo hiểm xã hội và Nghị định 73/2024/NĐ-CP (tiền lương tháng đóng BHXH bắt buộc tối đa bằng 20 lần mức tham chiếu 2,34 triệu = 46,8 triệu đồng/tháng). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/muc-dong-bao-hiem-xa-hoi-bat-buoc-moi-nhat-119240702111843702.htm).
18. `ck-phep-nam-chua-nghi-duoc-tra-tien`: Khoản 3 Điều 113 Bộ luật Lao động 2019 (người lao động do thôi việc, mất việc làm mà chưa nghỉ hoặc chưa nghỉ hết ngày phép hằng năm thì được người sử dụng lao động thanh toán tiền lương cho những ngày chưa nghỉ). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/quy-dinh-ve-nghi-hang-nam-phep-nam-119221102094254848.htm).
19. `ck-giam-2-phan-tram-thue-gtgt`: Nghị định 72/2024/NĐ-CP của Chính phủ (giảm 2% thuế suất thuế GTGT từ 10% xuống 8% đối với các nhóm hàng hóa, dịch vụ theo quy định). Nguồn: [baochinhphu.vn](https://baochinhphu.vn/chinh-phu-ban-hanh-nghi-dinh-giam-2-thue-vat-102240630193433611.htm).
20. `ck-tran-lai-suat-vay-dan-su-20-phan-tram`: Khoản 1 Điều 468 Bộ luật Dân sự 2015 (lãi suất vay do các bên thỏa thuận không được vượt quá 20%/năm của khoản tiền vay; phần vượt quá không có hiệu lực). Nguồn: [xaydungchinhsach.chinhphu.vn](https://xaydungchinhsach.chinhphu.vn/quy-dinh-ve-lai-suat-vay-theo-bo-luat-dan-su-119230613144804368.htm).

## Tuân thủ quy tắc xưởng
- **Không render:** Tuân thủ nghiêm ngặt brief, không chạy render video hay thumbnail. Do đó không tạo clip sheet hay thumbnail mới cho lô này.
- **Không đăng & không đổi lịch:** Không chạy các script upload, enqueue, không đọc thư mục credential, không ghi vào cơ sở dữ liệu `state.sqlite`. Các mốc `publish_at` chỉ lưu trữ trong spec JSON.
- **Không can thiệp git:** Không thực hiện bất kỳ thao tác `git commit`, `push`, `checkout`, `stash`, hay `reset`.