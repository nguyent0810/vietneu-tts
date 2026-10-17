# Đề xuất chuỗi video Long / Short (kênh `fs` — Astro Việt Insights) đến Tết Đinh Mùi 2027

Người viết: Claude (Code), 16/10/2026. Dành cho agent Lead và người dùng. **Đây là đề xuất, chưa có code nào được đổi.**
Đọc cùng [`ANALYTICS_REVIEW_2026-10.md`](ANALYTICS_REVIEW_2026-10.md) (đối chiếu số liệu 28 ngày với code).

## 0. Độ tin cậy của đề xuất
| Loại | Nguồn | Mức |
|---|---|---|
| Số liệu kênh (view, ở lại xem, series nào tốt) | bản tóm tắt người dùng dán, **chưa kiểm lại** | Trung bình |
| Cấu trúc Long, khung chương, luật TTS | skill `long-script`, `hf_batch_render.py` | Cao (đã dùng ở sản xuất) |
| Dữ kiện lịch (Tết, Tam Tai, Kim Lâu) | `vnlunar` + quy tắc truyền thống, đối chiếu tìm kiếm web | Cao với lịch; **trung bình** với quy tắc "quan niệm" |
| Nhu cầu tìm kiếm theo mùa | **không có dữ liệu xu hướng** (không gọi được YouTube/Google Trends ở môi trường này) | Thấp: chỉ là suy luận từ ba video 2027 đã nổ |
| Bảng sao hạn, quan hệ Thái Tuế chi tiết | các nguồn **không thống nhất** | Thấp: phải chốt bảng cố định + ghi nguồn trước khi làm |

## 1. Ràng buộc quyết định cách chia chuỗi
1. **Mùng 1 Tết Đinh Mùi = thứ Bảy 6/2/2027** (`vnlunar`: âm lịch 1/1/2027, ngày Bính Thìn). Từ 16/10/2026 còn **113 ngày**. Các chủ đề gắn Tết có hạn sử dụng; chủ đề "tuổi X năm 2027" sống cả năm.
2. **Nội dung lặp / sản xuất hàng loạt** ảnh hưởng YPP. Mỗi video trong một chuỗi phải khác nhau về *dữ kiện tính ra*, không chỉ đổi tên con giáp. Mỗi chuỗi dưới đây có cột "cái làm mỗi video khác nhau".
3. **Hedge bắt buộc** ("theo quan niệm / theo lịch pháp truyền thống…", `creator_specs/PRODUCTION_CREATOR_PROMPT_v1.md:70`). Giữ hedge nhưng xoay vòng nhiều mẫu câu.
4. **Cổng short v2/v3** bật từ 14/11 và 18/11 (`hf_batch_render.py:295,353`): câu 1 ≤ 22 tiếng, câu 2 không định nghĩa, 68–88 tiếng (~21–27 giây) cho FS, không từ giật gân, có `insight` và qua `hf_novelty`. Mọi chuỗi Short dưới đây thiết kế theo luật này ngay từ bây giờ.
5. **Nút thắt YPP có thể là người đăng ký** (+95/28 ngày), không chỉ giờ xem. Mỗi chuỗi cần một lý do để người xem đăng ký (xem tiếp tuổi mình, xem cả bộ).
6. Quota hiện là 5 Short/ngày (`twice_weekly_batch.py:85`). Đề xuất cơ cấu ở mục 5.

## 2. Dữ kiện đã tính / kiểm chứng (dùng làm "xương sống" cho chuỗi)

**Tính bằng code** (`vnlunar`, quy tắc cố định; chạy lại được):
- Năm 2027 = **Đinh Mùi**, mùng 1 Tết 6/2/2027. Nạp âm **Thiên Hà Thủy** (khớp [FPT Shop](https://fptshop.com.vn/tin-tuc/for-gamers/2027-la-nam-con-gi-menh-gi-207401) và `hf_showreel.py`).
  - **Bẫy:** `vnlunar.get_full_info()["year_element"]` trả `Hỏa` (hành của *Can*), **không phải nạp âm**. Không dùng trường này để nói "mệnh" của năm hay của tuổi; cần bảng 60 Giáp Tý riêng.
- **Tam Tai theo năm** (chu kỳ 3 năm theo nhóm tam hợp, tính từ chi của năm):

  | Nhóm tuổi (tam hợp) | Gặp Tam Tai trong các năm |
  |---|---|
  | Thân, Tý, Thìn | Dần Mão Thìn → 2022–2024 (đã qua) |
  | **Hợi, Mão, Mùi** | Tỵ Ngọ Mùi → 2025–**2027 (năm thứ ba, cuối)** |
  | Dần, Ngọ, Tuất | Thân Dậu Tuất → **2028–2030 (bắt đầu từ 2028)** |
  | Tỵ, Dậu, Sửu | Hợi Tý Sửu → 2031–2033 |

  Khớp [nguồn tìm kiếm](https://luatminhkhue.vn/cach-tinh-han-tam-tai-kim-lau-hoang-oc.aspx) về nhóm Hợi–Mão–Mùi năm 2027. Năm sinh thuộc nhóm này trong khoảng 1957–2009: 1959, 1963, 1967, 1971, 1975, 1979, 1983, 1987, 1991, 1995, 1999, 2003, 2007. Hai "móc" đáng làm: *năm cuối của Tam Tai (hết hạn thế nào?)* và *2028 tuổi nào bắt đầu*.
- **Kim Lâu 2027** (quy tắc: tuổi mụ = 2027 − năm sinh + 1; chia 9 dư 1, 3, 6, 8): năm sinh 1957, 1959, 1962, 1964, 1966, 1968, 1971, 1973, 1975, 1977, 1980, 1982, 1984, 1986, 1989, 1991, 1993, 1995, 1998, 2000, 2002, 2004, 2007, 2009. **Cần ghi rõ:** cách tính có biến thể (xây nhà tính gia chủ, cưới hỏi tính tuổi nữ, một số nơi tính tuổi dương), nên trình bày là "theo quan niệm dân gian". [Luật Minh Khuê](https://luatminhkhue.vn/cach-tinh-han-tam-tai-kim-lau-hoang-oc.aspx) chỉ phân tích cho 2026, chưa có nguồn riêng cho 2027.
- **Quan hệ với chi Mùi** (bảng cố định, khớp [Cellphones](https://cellphones.com.vn/sforum/tet-dinh-mui-2027)): tam hợp Hợi–Mão–Mùi, lục hợp **Ngọ**, lục xung **Sửu**. Nguồn không thống nhất ở phần *hại/hình/phá*: có bài nêu Tuất hại Mùi, có bài gom Thìn–Tuất–Sửu–Mùi vào "tứ hành xung" ([Điện máy xanh](https://www.dienmayxanh.com/kinh-nghiem-hay/con-bao-nhieu-ngay-nua-den-tet-2027-1589672)). → **chốt một bảng và ghi nguồn trước khi sản xuất**; video chỉ nêu quan hệ có đồng thuận (tam hợp, lục hợp, lục xung).
- **Chưa kiểm chứng:** bảng Cửu Diệu (sao hạn nam/nữ). Tôi dựng được bảng theo thứ tự phổ biến nhưng không xác nhận được bằng web (trang tham chiếu không mở được). Không dùng cho tới khi có hai nguồn khớp.

## 3. Chuỗi Short (mỗi video 68–88 tiếng, ~21–27 giây)

Hook luôn là *năm sinh / con giáp cụ thể ở khung đầu* (bản phân tích: tiêu đề có năm sinh giữ chân 50–73%).

| # | Chuỗi | Số video | Mẫu hook (câu 1) | **Cái làm mỗi video khác nhau** (tính bằng code) | Giả thuyết cần kiểm |
|---|---|---|---|---|---|
| S1 | **Tuổi X năm 2027** | 12 (mỗi chi) | "Tuổi Mão năm 2027 còn Tam Tai không?" | quan hệ chi X với Mùi (tam hợp/lục hợp/xung/không), Tam Tai có/không + năm thứ mấy, 2 năm sinh cụ thể cùng chi | Hook "có phạm không?" giữ chân tốt hơn hook liệt kê |
| S2 | **Tam Tai: ai hết, ai bắt đầu** | 5 (3 video "năm cuối" cho Hợi, Mão, Mùi; 1 video "2028 bắt đầu" cho Dần/Ngọ/Tuất; 1 tổng quan) | "2027 là năm cuối Tam Tai của 3 tuổi này." | bảng chu kỳ ở trên, danh sách năm sinh cụ thể, năm tới ai tới lượt | Ba video đã nổ ở kênh là cùng chủ đề; chuỗi này khai thác sâu |
| S3 | **Năm sinh + mệnh trong năm 2027** (mở rộng series "1978, 1979 Thiên Thượng Hỏa" đang tốt) | tối đa 30 (mỗi nạp âm), làm dần theo cohort đông trước | "1978, 1979 mệnh Thiên Thượng Hỏa: 2027 hợp hay khắc?" | quan hệ ngũ hành của *nạp âm tuổi* với *Thiên Hà Thủy* (sinh/khắc/bình), 2 năm sinh cụ thể | Series tốt nhất hiện tại; thêm 2027 để có lý do đăng lại mà không lặp |
| S4 | **Kim Lâu 2027: năm sinh nào?** | 3 (xây nhà / cưới hỏi / "có phải kiêng tuyệt đối không?") | "Năm 2027, những năm sinh này phạm Kim Lâu." | danh sách năm sinh Kim Lâu theo tuổi mụ, ví dụ theo từng ngữ cảnh | Nhu cầu "làm nhà/cưới năm 2027" mạnh trước Tết |
| S5 | **Xông đất Tết Đinh Mùi** | 12 (theo tuổi gia chủ) | "Gia chủ tuổi Sửu nên mời tuổi nào xông đất 2027?" | tam hợp/lục hợp của chi gia chủ **và** chi Mùi, tuổi tránh (xung), 2 năm sinh cụ thể mỗi nhóm | Hạn sử dụng: đăng **15/12 → 5/2**; ngoài khoảng đó giá trị giảm mạnh |
| S6 | **Lịch Tết gộp** (thay lịch ngày) | 1–2 tuần/lần | "Mùng 1 đến mùng 10 Tết 2027: ngày nào làm việc gì?" | ngày/giờ từ `vnlunar` cho đúng mùng 1–10, 1 video gộp thay vì 10 video | Thay chuỗi lịch ngày: ít video hơn, nhiều giá trị hơn |
| S7 | **Cặp tuổi** (evergreen, nền) | 6 | "Tuổi Mão và tuổi Dậu có hợp lấy nhau không?" | quan hệ chi, mệnh nạp âm, 2 năm sinh cụ thể | Giữ một chút evergreen khi hết mùa 2027 |

**Cắt / giảm** (khớp bản phân tích 28 ngày: 13–400 view): Kinh Dịch/hào/quẻ, Can–Tài tinh trừu tượng, cung hoàng đạo phương Tây. Lịch ngày hằng ngày chuyển thành S6 gộp.

## 4. Chuỗi Long (FS)

Bài học từ kênh: Long 30 phút mới đăng chỉ được 14–26 view, vì khán giả feed Shorts hiếm khi chuyển sang video dài. Long phải đến từ **tìm kiếm/gợi ý**, và phải *trả đáp án trong 2 câu đầu* (luật 2–4, `long-script`). Giờ xem đủ điều kiện chỉ tính video dài, nên Long vẫn cần, nhưng không nên lên lịch thêm hàng loạt trước khi có tín hiệu.

| # | Chuỗi | Độ dài | Cấu trúc (theo `formats.md`) | Số video | Ghi chú |
|---|---|---|---|---|---|
| L1 | **Tuổi X năm 2027 — bản ngắn thử nghiệm** | 12–15 phút | cold open có con số của tuổi X → trả ngay "2027 tuổi X thế nào" → 3–4 chương: Thái Tuế/Tam Tai, tháng cần để ý, việc nên làm → bảng tra trên màn hình | 3 (Mùi, Hợi, Mão — nhóm Tam Tai năm cuối) | **Thử nghiệm A/B** với L2: render ≈ 1,7× thời lượng nên bản ngắn rẻ hơn ~3 lần |
| L2 | **Tử vi trọn đời tuổi X + 2027** (format (b)) | 35–45 phút | đúng khung `formats.md` §3 | 2 (cùng hai tuổi của L1 để so được) | Đối thủ "Quý Hợi 1983" 30–58 phút, 75–350 nghìn view; tách nam/nữ **trong cùng chương** |
| L3 | **Làm nhà / cưới hỏi / sinh con năm 2027: 10 câu hỏi** (format (c)) | 40–50 phút | mỗi câu hỏi = một chương, tiêu đề đúng chữ người ta gõ tìm, trả trong 2 câu đầu: Kim Lâu, Hoang Ốc, tuổi hợp làm nhà, năm sinh con | 1–2 | Mẫu "lọ hoa bàn thờ" 36–47 phút/425 nghìn view; chủ đề có nhu cầu thật, dễ gắn S4 |
| L4 | **Tết Đinh Mùi 2027: cúng giao thừa, mâm cúng, ngày giờ tốt** (format (c)) | 40–50 phút | hỏi-đáp phong tục + giờ tốt tính bằng `vnlunar` | 1 | Đăng trước 15/12; hạn sử dụng ngắn, ưu tiên sau L1 |

**Điều kiện mở rộng Long:** chỉ làm tiếp các tuổi còn lại của L1 (9 tuổi) nếu 2–3 video đầu đạt **≥ 300 view trong 14 ngày và ở lại ≥ 40%** (ngưỡng khởi đầu, chưa có số liệu Long đủ để hiệu chỉnh; chỉnh sau khi có thêm vài video). Nếu không, dừng lên lịch Long mới, xem lại tiêu đề/mô tả (tìm kiếm), không làm thêm Long nữa. Các video dài đã lên lịch (khoảng 20) nên xếp lại theo thứ tự trên.

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
1. Bảng dữ kiện 2027 cố định (60 Giáp Tý → nạp âm; Tam Tai; Kim Lâu; quan hệ chi) + test, thay vì dùng `year_element` của `vnlunar`.
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
- `vnlunar` (lịch âm, đã chạy cục bộ) · `.claude/skills/long-script/references/formats.md` · `hf_batch_render.py:291-371` · `twice_weekly_batch.py:85`
