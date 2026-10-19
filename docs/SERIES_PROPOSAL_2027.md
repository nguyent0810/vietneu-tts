# Đề xuất chuỗi video Long / Short (kênh `fs` — Astro Việt Insights) đến Tết Đinh Mùi 2027

Người viết: Claude (Code), 16/10/2026. Dành cho agent Lead và người dùng. **Đây là đề xuất, chưa có code nào được đổi.**
Đọc cùng [`ANALYTICS_REVIEW_2026-10.md`](ANALYTICS_REVIEW_2026-10.md) (đối chiếu số liệu 28 ngày với code).

## 0. Độ tin cậy của đề xuất
| Loại | Nguồn | Mức |
|---|---|---|
| Số liệu kênh (view, ở lại xem, series nào tốt) | bản tóm tắt người dùng dán, **chưa kiểm lại** | Trung bình |
| Cấu trúc Long, khung chương, luật TTS | skill `long-script`, `hf_batch_render.py` | Cao (đã dùng ở sản xuất) |
| Dữ kiện lịch (Tết, Tam Tai, Kim Lâu, ngày hoàng đạo/trực) | Tính bằng code: `output/cl_staging/long/amlich.py`, `canchi.py`, `tuvi_year.py` và `output/cl_staging/grok/tools/ngaytot.py` (lọc hoàng đạo/trực/Tam Nương/Nguyệt kỵ/Dương Công); KHÔNG dùng `vnlunar` | **Cao** (toàn bộ dữ kiện tính bằng code nội bộ dự án; `vnlunar` sai thần/trực/nạp âm nên không dùng) |
| Nhu cầu tìm kiếm theo mùa | **không có dữ liệu xu hướng** (không gọi được YouTube/Google Trends ở môi trường này) | Thấp: chỉ là suy luận từ ba video 2027 đã nổ |
| Quan hệ Thái Tuế chi tiết | Tính bằng code: `canchi.py` (`thai_tue`, `TAM_HOP`, `LUC_HOP`, `LUC_XUNG`, `LUC_HAI`, `TAM_HINH`, `LUC_PHA`) | **Cao** (đã chuẩn hoá theo code dự án; lược bỏ bảng sao hạn chưa kiểm) |

## 1. Ràng buộc quyết định cách chia chuỗi
1. **Mùng 1 Tết Đinh Mùi = thứ Bảy 6/2/2027** (tính bằng `amlich.py`, `canchi.py`, `ngaytot.py`: âm lịch 1/1/2027 Đinh Mùi, ngày Bính Thìn, hoàng đạo Kim Quỹ, trực Mãn, tiết Lập xuân). Tính từ 19/10/2026 còn **110 ngày** (từ 16/10 là 113 ngày). Các chủ đề gắn Tết có hạn sử dụng; chủ đề "tuổi X năm 2027" sống cả năm.
2. **Nội dung lặp / sản xuất hàng loạt** ảnh hưởng YPP. Mỗi video trong một chuỗi phải khác nhau về *dữ kiện tính ra*, không chỉ đổi tên con giáp. Mỗi chuỗi dưới đây có cột "cái làm mỗi video khác nhau".
3. **Hedge bắt buộc** ("theo quan niệm / theo lịch pháp truyền thống…", `creator_specs/PRODUCTION_CREATOR_PROMPT_v1.md:70`). Giữ hedge nhưng xoay vòng nhiều mẫu câu.
4. **Cổng short v2/v3** bật từ 14/11 và 18/11 (`hf_batch_render.py:295,353`): câu 1 ≤ 22 tiếng, câu 2 không định nghĩa, 68–88 tiếng (~21–27 giây) cho FS, không từ giật gân, có `insight` và qua `hf_novelty`. Mọi chuỗi Short dưới đây thiết kế theo luật này ngay từ bây giờ.
5. **Nút thắt YPP có thể là người đăng ký** (+95/28 ngày), không chỉ giờ xem. Mỗi chuỗi cần một lý do để người xem đăng ký (xem tiếp tuổi mình, xem cả bộ).
6. Quota hiện là 5 Short/ngày (`twice_weekly_batch.py:85`). Đề xuất cơ cấu ở mục 5.

## 2. Dữ kiện đã tính / kiểm chứng (dùng làm "xương sống" cho chuỗi)

**Tính bằng code** (`output/cl_staging/long/amlich.py`, `canchi.py`, `tuvi_year.py` và `output/cl_staging/grok/tools/ngaytot.py`; chạy lại được; **KHÔNG dùng `vnlunar`** vì luật dự án xác định `vnlunar` sai thần, trực, nạp âm):
- Năm 2027 = **Đinh Mùi**, mùng 1 Tết **6/2/2027** (ngày Bính Thìn, hoàng đạo Kim Quỹ, trực Mãn, tiết Lập xuân).
- Mệnh nạp âm: `canchi.nap_am(2027)` = **Thiên Hà Thủy** (hành Thủy).
  - **Lưu ý quan trọng về nạp âm:** Không dùng `vnlunar.get_full_info()["year_element"]` vì nó trả `Hỏa` (hành của Can Đinh), không phải nạp âm. Toàn bộ nạp âm của 60 Giáp Tý được tính chuẩn theo bảng Lục Thập Hoa Giáp trong `canchi.py`.
- **Tam Tai theo năm** (chu kỳ 3 năm theo nhóm tam hợp, tính từ chi của năm bằng `tuvi_year.py` / `canchi.py`):

  | Nhóm tuổi (tam hợp) | Gặp Tam Tai trong các năm | Trạng thái |
  |---|---|---|
  | Thân, Tý, Thìn | Dần Mão Thìn | 2022–2024 (đã qua) |
  | **Hợi, Mão, Mùi** | Tỵ Ngọ Mùi | **2025–2027 (2027 là năm thứ ba, cuối)** |
  | Dần, Ngọ, Tuất | Thân Dậu Tuất | **2028–2030 (bắt đầu từ 2028)** |
  | Tỵ, Dậu, Sửu | Hợi Tý Sửu | 2031–2033 |

  - Danh sách 13 năm sinh thuộc nhóm Tam Tai năm 2027 (khoảng 1957–2009, tính bằng `canchi.years_of`):
    - Tuổi Hợi: 1959, 1971, 1983, 1995, 2007
    - Tuổi Mão: 1963, 1975, 1987, 1999
    - Tuổi Mùi: 1967, 1979, 1991, 2003
    - Tổng hợp: 1959, 1963, 1967, 1971, 1975, 1979, 1983, 1987, 1991, 1995, 1999, 2003, 2007. Hai "móc" trọng tâm: *năm cuối của Tam Tai (hết hạn thế nào?)* và *2028 tuổi nào bắt đầu*.
- **Kim Lâu 2027** (tính bằng code `tuvi_year.tuoi(y, 2027) % 9 in (1, 3, 6, 8)`):
  - Dư 1: Kim Lâu Thân; Dư 3: Kim Lâu Thê; Dư 6: Kim Lâu Tử; Dư 8: Kim Lâu Lục Súc.
  - Danh sách 24 năm sinh (1957–2009) phạm Kim Lâu năm 2027:
    1957, 1959, 1962, 1964, 1966, 1968, 1971, 1973, 1975, 1977, 1980, 1982, 1984, 1986, 1989, 1991, 1993, 1995, 1998, 2000, 2002, 2004, 2007, 2009.
  - **Lưu ý framing:** Cách tính dân gian có biến thể (xây nhà tính tuổi gia chủ nam, cưới hỏi tính tuổi nữ), kịch bản luôn hedge "theo quan niệm dân gian / tham khảo".
- **Quan hệ với chi Mùi năm 2027** (tính bằng code từ `canchi.py`):
  - Tam hợp: Hợi – Mão – Mùi
  - Lục hợp: Ngọ – Mùi
  - Lục xung: Sửu – Mùi (xung Thái Tuế)
  - Lục hại: Tý – Mùi (hại Thái Tuế)
  - Tam hình: Sửu – Tuất – Mùi (hình Thái Tuế)
  - Lục phá: Tuất – Mùi (phá Thái Tuế)
  - Trực Thái Tuế: Mùi (năm tuổi)
- **BẢNG LỊCH MÙNG 1 ĐẾN MÙNG 10 TẾT ĐINH MÙI (06/02/2027 – 15/02/2027)**
  *(Nguồn: tính bằng `output/cl_staging/grok/tools/ngaytot.py`, `amlich.py`, `canchi.py`)*

  | Ngày DL | Ngày ÂL | Can Chi | Thần | Hoàng/Hắc | Trực | Kỵ (Tam Nương/Nguyệt kỵ/Dương Công) | Việc hợp | Tuổi xung | Giờ hoàng đạo |
  |---|---|---|---|---|---|---|---|---|---|
  | 06/02/2027 | 1/1 | Bính Thìn | Kim Quỹ | Hoàng đạo | Mãn | Không | đi dạo (xuất hành nhẹ) | Tuất | Dần, Thìn, Tỵ, Thân, Dậu, Hợi |
  | 07/02/2027 | 2/1 | Đinh Tỵ | Kim Đường | Hoàng đạo | Bình | Không | di chuyển | Hợi | Sửu, Thìn, Ngọ, Mùi, Tuất, Hợi |
  | 08/02/2027 | 3/1 | Mậu Ngọ | Bạch Hổ | Hắc đạo | Định | Tam Nương | giao dịch, đính hôn | Tý | Tý, Sửu, Mão, Ngọ, Thân, Dậu |
  | 09/02/2027 | 4/1 | Kỷ Mùi | Ngọc Đường | Hoàng đạo | Chấp | Không | ký giấy tờ | Sửu | Dần, Mão, Tỵ, Thân, Tuất, Hợi |
  | 10/02/2027 | 5/1 | Canh Thân | Thiên Lao | Hắc đạo | Phá | Nguyệt kỵ | phá dỡ | Dần | Tý, Sửu, Thìn, Tỵ, Mùi, Tuất |
  | 11/02/2027 | 6/1 | Tân Dậu | Nguyên Vũ | Hắc đạo | Nguy | Không | cúng lễ | Mão | Tý, Dần, Mão, Ngọ, Mùi, Dậu |
  | 12/02/2027 | 7/1 | Nhâm Tuất | Tư Mệnh | Hoàng đạo | Thành | Tam Nương | cưới hỏi, khai trương, làm nhà | Thìn | Dần, Thìn, Tỵ, Thân, Dậu, Hợi |
  | 13/02/2027 | 8/1 | Quý Hợi | Câu Trần | Hắc đạo | Thu | Không | thu xếp, nhận việc | Tỵ | Sửu, Thìn, Ngọ, Mùi, Tuất, Hợi |
  | 14/02/2027 | 9/1 | Giáp Tý | Thanh Long | Hoàng đạo | Khai | Không | cưới hỏi, khai trương, làm nhà, nhập trạch | Ngọ | Tý, Sửu, Mão, Ngọ, Thân, Dậu |
  | 15/02/2027 | 10/1 | Ất Sửu | Minh Đường | Hoàng đạo | Bế | Không | lập kế hoạch | Mùi | Dần, Mão, Tỵ, Thân, Tuất, Hợi |

- **BẢNG NGÀY TỐT SAU TẾT THÁNG 2/2027 (CHO KHAI TRƯƠNG, CƯỚI HỎI, LÀM NHÀ, NHẬP TRẠCH)**
  *(Nguồn: lọc qua `output/cl_staging/grok/tools/ngaytot.py`: hoàng đạo, trực Thành/Khai, loại trừ Tam Nương, Nguyệt kỵ, Dương Công)*

  | Ngày DL | Ngày ÂL | Can Chi | Thần | Trực | Tuổi xung | Việc hợp (không phạm kỵ) | Giờ hoàng đạo |
  |---|---|---|---|---|---|---|---|
  | 14/02/2027 | 9/1 | Giáp Tý | Thanh Long | Khai | Ngọ | Khai trương, cưới hỏi, làm nhà, nhập trạch | Tý, Sửu, Mão, Ngọ, Thân, Dậu |
  | 24/02/2027 | 19/1 | Giáp Tuất | Tư Mệnh | Thành | Thìn | Khai trương, cưới hỏi, làm nhà | Dần, Thìn, Tỵ, Thân, Dậu, Hợi |
  | 26/02/2027 | 21/1 | Bính Tý | Thanh Long | Khai | Ngọ | Khai trương, cưới hỏi, làm nhà, nhập trạch | Tý, Sửu, Mão, Ngọ, Thân, Dậu |

  *Ghi chú:* Ngày 12/02/2027 (7/1 ÂL) tuy là ngày hoàng đạo Tư Mệnh trực Thành nhưng trùng ngày Tam Nương nên bị loại khỏi danh sách ngày tốt theo chuẩn `ngaytot.py`. Trước Tết có ngày 01/02/2027 (25/12 ÂL) hợp, nhưng rơi trước Tết nên không đưa vào kịch bản sau Tết.
- **Xoá dữ kiện chưa kiểm:** Toàn bộ bảng Cửu Diệu (sao hạn nam/nữ) và các dữ kiện không tính lại được bằng code dự án đã được lược bỏ khỏi tài liệu, tuân thủ nguyên tắc không để số liệu chưa kiểm chứng.

## 3. Chuỗi Short (mỗi video 68–88 tiếng, ~21–27 giây)

Hook luôn là *năm sinh / con giáp cụ thể ở khung đầu* (bản phân tích: tiêu đề có năm sinh giữ chân 50–73%).

| # | Chuỗi | Số video | Mẫu hook (câu 1) | **Cái làm mỗi video khác nhau** (tính bằng code) | Giả thuyết cần kiểm |
|---|---|---|---|---|---|
| S1 | **Tuổi X năm 2027** | 12 (mỗi chi) | "Tuổi Mão năm 2027 còn Tam Tai không?" | quan hệ chi X với Mùi (tam hợp/lục hợp/xung/không), Tam Tai có/không + năm thứ mấy, 2 năm sinh cụ thể cùng chi | Hook "có phạm không?" giữ chân tốt hơn hook liệt kê |
| S2 | **Tam Tai: ai hết, ai bắt đầu** | 5 (3 video "năm cuối" cho Hợi, Mão, Mùi; 1 video "2028 bắt đầu" cho Dần/Ngọ/Tuất; 1 tổng quan) | "2027 là năm cuối Tam Tai của 3 tuổi này." | bảng chu kỳ ở trên, danh sách năm sinh cụ thể, năm tới ai tới lượt | Ba video đã nổ ở kênh là cùng chủ đề; chuỗi này khai thác sâu |
| S3 | **Năm sinh + mệnh trong năm 2027** (mở rộng series "1978, 1979 Thiên Thượng Hỏa" đang tốt) | tối đa 30 (mỗi nạp âm), làm dần theo cohort đông trước | "1978, 1979 mệnh Thiên Thượng Hỏa: 2027 hợp hay khắc?" | quan hệ ngũ hành của *nạp âm tuổi* với *Thiên Hà Thủy* (sinh/khắc/bình), 2 năm sinh cụ thể | Series tốt nhất hiện tại; thêm 2027 để có lý do đăng lại mà không lặp |
| S4 | **Kim Lâu 2027: năm sinh nào?** | 3 (xây nhà / cưới hỏi / "có phải kiêng tuyệt đối không?") | "Năm 2027, những năm sinh này phạm Kim Lâu." | danh sách năm sinh Kim Lâu theo tuổi mụ, ví dụ theo từng ngữ cảnh | Nhu cầu "làm nhà/cưới năm 2027" mạnh trước Tết |
| S5 | **Xông đất Tết Đinh Mùi** | 12 (theo tuổi gia chủ) | "Gia chủ tuổi Sửu nên mời tuổi nào xông đất 2027?" | tam hợp/lục hợp của chi gia chủ **và** chi Mùi, tuổi tránh (xung), 2 năm sinh cụ thể mỗi nhóm | Hạn sử dụng: đăng **15/12 → 5/2**; ngoài khoảng đó giá trị giảm mạnh |
| S6 | **Lịch Tết gộp** (thay lịch ngày) | 1–2 tuần/lần | "Mùng 1 đến mùng 10 Tết 2027: ngày nào làm việc gì?" | ngày/giờ từ `amlich.py`, `canchi.py`, `ngaytot.py` cho đúng mùng 1–10, 1 video gộp thay vì 10 video | Thay chuỗi lịch ngày: ít video hơn, nhiều giá trị hơn |
| S7 | **Cặp tuổi** (evergreen, nền) | 6 | "Tuổi Mão và tuổi Dậu có hợp lấy nhau không?" | quan hệ chi, mệnh nạp âm, 2 năm sinh cụ thể | Giữ một chút evergreen khi hết mùa 2027 |

**Cắt / giảm** (khớp bản phân tích 28 ngày: 13–400 view): Kinh Dịch/hào/quẻ, Can–Tài tinh trừu tượng, cung hoàng đạo phương Tây. Lịch ngày hằng ngày chuyển thành S6 gộp.

## 4. Chuỗi Long (FS)

Bài học từ kênh: Người dùng vẫn **ƯU TIÊN Long ≥ 30 phút** để nội dung sinh động, phong phú, có chiều sâu (bỏ lý do "≥ 30 phút để có quảng cáo giữa" vì quảng cáo giữa chỉ cần ≥ 8 phút; cả hai kênh CHƯA bật kiếm tiền). Long phải đến từ **tìm kiếm/gợi ý**, và phải *trả đáp án trong 2 câu đầu* (luật 2–4, `long-script`). Không dừng lên lịch video 30+ phút và không ưu tiên bản ngắn 6–15 phút; tập trung tối ưu 2 phút đầu và các mốc re-hook 25/50/75% để tăng giữ chân; đo lường bằng tập 1 FS (Sw0e7MEybxo, 16/10) và BUD (_CPkVkUOc50, 18/10).

| # | Chuỗi | Độ dài | Cấu trúc (theo `formats.md`) | Số video | Ghi chú |
|---|---|---|---|---|---|
| L1 | **Tuổi X năm 2027 — chuyên sâu** | 30–45 phút | cold open có con số của tuổi X → trả ngay "2027 tuổi X thế nào" → 3–4 chương: Thái Tuế/Tam Tai, tháng cần để ý, việc nên làm → bảng tra trên màn hình | 3 (Mùi, Hợi, Mão — nhóm Tam Tai năm cuối) | Giữ thời lượng ≥ 30 phút theo ưu tiên người dùng |
| L2 | **Tử vi trọn đời tuổi X + 2027** (format (b)) | 35–45 phút | đúng khung `formats.md` §3 | 2 (cùng hai tuổi của L1 để so được) | Đối thủ "Quý Hợi 1983" 30–58 phút, 75–350 nghìn view; tách nam/nữ **trong cùng chương** |
| L3 | **Làm nhà / cưới hỏi / sinh con năm 2027: 10 câu hỏi** (format (c)) | 40–50 phút | mỗi câu hỏi = một chương, tiêu đề đúng chữ người ta gõ tìm, trả trong 2 câu đầu: Kim Lâu, Hoang Ốc, tuổi hợp làm nhà, năm sinh con | 1–2 | Mẫu "lọ hoa bàn thờ" 36–47 phút/425 nghìn view; chủ đề có nhu cầu thật, dễ gắn S4 |
| L4 | **Tết Đinh Mùi 2027: cúng giao thừa, mâm cúng, ngày giờ tốt** (format (c)) | 40–50 phút | hỏi-đáp phong tục + ngày giờ tốt tính bằng `amlich.py`, `canchi.py`, `ngaytot.py` | 1 | Đăng trước 15/12; hạn sử dụng ngắn, ưu tiên sau L1 |

**Định hướng triển khai Long:** Giữ các bản Long 30+ phút làm trọng tâm theo định hướng của người dùng. Không dừng lên lịch video 30+ phút; tập trung sửa 2 phút đầu và các mốc re-hook 25/50/75% để tăng tỉ lệ giữ chân. Đo lường hiệu quả qua tập 1 FS (Sw0e7MEybxo, 16/10) và BUD (_CPkVkUOc50, 18/10). Các video dài đã lên lịch (khoảng 20) nên xếp lại theo thứ tự trên.

**Nối Short → Long:** mỗi Short S1/S2 có "Video liên quan" tới L1 cùng tuổi (thủ công hoặc qua API); mô tả ghi mục lục chương.

## 5. Cơ cấu 5 Short/ngày đề xuất (thử 2 tuần, đo, rồi chỉnh)
| Giai đoạn | S1+S2+S3 | S4 | S5 | S6 | S7 | Nền khác |
|---|---|---|---|---|---|---|
| 17/10 → 13/11 (trước cổng v2) | 3 | 1 | – | 1 gộp theo tuần | – | 0 |
| 14/11 → 14/12 | 3 | 1 | 1 | gộp | – | 0 |
| 15/12 → 5/2 (mùa Tết) | 2 | – | 2 | 1 | – | – |
| Sau 6/2 | 3 | – | – | – | 1–2 | 1–2 |

Nguồn cung: S1 12 + S2 5 + S3 ≤ 30 + S4 3 + S5 12 + S7 6 ≈ **68 video** — đủ cho khoảng 14 ngày ở nhịp 5/ngày hoặc khoảng 4 tuần ở nhịp 2–3/ngày. Vì vậy cơ cấu trên phải đi cùng việc sản xuất thêm biến thể (xem mục 8), không thể chạy 5/ngày liên tục chỉ bằng ngần ấy video.

## 6. Đo lường và tiêu chí dừng
- Theo từng video: lượt xem, **% ở lại xem** (xuất từ Studio; API không có), giờ xem, người đăng ký, ghi kèm *chuỗi / lane / chiến lược hook*. Hiện registry không lưu (xem báo cáo analytics mục 4.4).
- Thử A/B hook trong S1 (12 video): luân phiên 3 kiểu hook (câu hỏi "có phạm không?", con số, tình huống cụ thể). Cần ≥ 4 video mỗi kiểu mới so được.
- Dừng / nới theo chuỗi sau **6 video**: giữ nếu trung vị view ≥ 2× baseline kênh (~1.000) *và* ở lại ≥ 50%; thu hẹp nếu dưới baseline ở cả hai chỉ số.

## 7. Rủi ro
1. **Mẫu lặp**: S1/S5 12 video cùng khuôn. Giảm bằng (a) cột "cái làm khác nhau" ở mục 3, (b) bảng hedge xoay vòng, (c) kiểm `hf_novelty` + so khớp câu mở giữa các video.
2. **Quan niệm không thống nhất giữa nguồn** (Kim Lâu, Thái Tuế, sao hạn): chỉ nói điều có đồng thuận, ghi "theo quan niệm", không phán định tốt/xấu tuyệt đối (spec cấm).
3. **Hạn sử dụng** của S5/L4: nếu trễ sau 5/2 gần như vô giá trị.
4. **Chưa có dữ liệu xu hướng tìm kiếm** để xếp thứ tự tuổi trong S1/L1; thứ tự đề xuất (Tam Tai trước) dựa trên ba video 2027 đã nổ, không phải khối lượng tìm kiếm.

## 8. Việc cần làm trong repo (chưa làm, đề nghị Lead giao)
1. Bảng dữ kiện 2027 cố định (60 Giáp Tý → nạp âm; Tam Tai; Kim Lâu; quan hệ chi) + test trong `output/cl_staging/long/canchi.py`, `tuvi_year.py`, `amlich.py` và `output/cl_staging/grok/tools/ngaytot.py`, tuyệt đối không dùng `vnlunar`.
2. Generator S1/S2/S3/S5 dùng bảng trên, chung `short_judge_panel_engine`, kèm lane/series/hook vào registry.
3. Danh sách mẫu câu hedge xoay vòng + kiểm lặp.
4. Đổi quota theo chuỗi (hiện cố định 5/ngày ở `twice_weekly_batch.py:85`).
5. Builder `build_X.py` cho L1/L2/L3/L4 (mẫu `build_B20.py`, `build_F20.py` ở `output/`, chưa có trong repo tracked).

## 9. BUD (kênh Phật giáo) — tóm tắt, bằng chứng yếu hơn
Phân tích 28 ngày chỉ nói về kênh FS, nên đề xuất cho BUD chỉ dựa trên ghi chú trong repo, **chưa có số liệu BUD mới**:
- **Long**: giữ hai format đã có khung (`formats.md`): (a) tuyển tập Truyện Tiền Thân 45–60 phút (5–8 truyện theo một chủ đề, đối chiếu `hf_sutta.py ja<N>`); (d) "Đêm nghe lời Phật dạy" 90 phút (chưa có số giữ chân của kênh). Mỗi 2–3 video đầu nên là thử nghiệm.
- **Short**: tiếp tục công thức v2; cần số liệu BUD cùng kiểu bản phân tích FS trước khi đề xuất chuỗi cụ thể. Gợi ý xin từ Studio: cùng bảng 28 ngày như FS.

## Nguồn
- [FPT Shop — 2027 là năm con gì, mệnh gì](https://fptshop.com.vn/tin-tuc/for-gamers/2027-la-nam-con-gi-menh-gi-207401)
- [Luật Minh Khuê — cách tính hạn Tam Tai, Kim Lâu, Hoang Ốc](https://luatminhkhue.vn/cach-tinh-han-tam-tai-kim-lau-hoang-oc.aspx)
- [Cellphones — Tết Đinh Mùi 2027](https://cellphones.com.vn/sforum/tet-dinh-mui-2027)
- [Điện máy xanh — còn bao nhiêu ngày nữa đến Tết 2027](https://www.dienmayxanh.com/kinh-nghiem-hay/con-bao-nhieu-ngay-nua-den-tet-2027-1589672)
- Code dự án (`output/cl_staging/long/amlich.py`, `output/cl_staging/long/canchi.py`, `output/cl_staging/long/tuvi_year.py`, `output/cl_staging/grok/tools/ngaytot.py`) · `.claude/skills/long-script/references/formats.md` · `hf_batch_render.py:291-371` · `twice_weekly_batch.py:85`
