# Nghiên cứu CTR Thumbnail Long FS: Nguyên nhân, Số liệu và Luật Đóng Gói

Ngày 11/11/2026 · Nghiên cứu số liệu kênh Studio & Analytics API · Tham chiếu: Issue #282

## 1. Kết luận chính

1. **Không có "hiệu ứng Mùi/Mão":** Ở kỳ 10–11/2026, 3 Long Mùi/Mão có CTR trung vị 7,72% (theo impressions: 7,76%). 6 Long nêu một tuổi khác có trung vị 8,20% (theo impressions: 7,99%). Trong loạt 2025 cùng khuôn DO25, Mão (3,96%) và Mùi (5,34%) thậm chí thấp hơn trung vị 8 tuổi còn lại (5,84%).
2. **Yếu tố quyết định là "một tuổi làm mỏ neo" kết hợp nhu cầu tìm kiếm (Search):**
   - Long nêu đúng một tuổi/can chi có CTR theo impressions **≈ 8%**.
   - Long chủ đề chung chỉ đạt **≈ 4,5%** (n = 9 và 11).
   - Tương quan giữa CTR và tỉ lệ view từ Search rất chặt: Pearson $r = 0,87$, Spearman $0,81$ ($n = 16$, Long 10/2026). Khán giả gõ "tuổi Mùi 2027" thấy thumbnail ghi to "TUỔI MÙI 2027" sẽ bấm.
3. **Khuôn thumbnail không giải thích hit Mão `nliSWRjMWzg` (9,6% / 63k imp):**
   - Ba Long Mão, Tuất, Mùi trong loạt Nửa Cuối 2026 dùng cùng một khuôn THUYMAC (giấy vàng thuỷ mặc, thư pháp). Kết quả: Mão 9,6%, Tuất 3,9%, Mùi chỉ ~234 view. Khác biệt nằm ở tiêu đề ("Sự Thật Gây Sốc…"), thời điểm ra mắt và vòng Suggested tự nuôi (44% Suggested, 51% Browse).
4. **Đối chứng cùng khuôn AIVANG (tháng 11/2026):** Long Mão tháng 10 âm (`_2CrJOu-tjA`) đạt 8,26% trên 6,4k impressions sau 3 ngày; trong khi 2 Long cùng tuần cùng khuôn chỉ đạt 4,71% (3 con giáp) và 4,34% (ngày tốt). Con vật cận mặt nhìn thẳng có lực hút vượt trội.
5. **Kênh Phật giáo (BUD):** 13 Long tháng 10–11 nằm gọn trong dải 2,0–4,1%, không có cơ chế "tra cứu theo tuổi". BUD chỉ có tín hiệu yếu ở tên riêng nổi tiếng (Đường Tăng 4,11%, Konagamana 13,5%).

## 2. Số liệu so sánh nhóm

### Long FS 10–11/2026 ($n = 20$, $\ge 500$ impressions)

| Nhóm | $n$ | CTR trung vị | CTR theo impressions |
|---|---|---|---|
| Mùi / Mão (Io70, VwEt, _2Cr) | 3 | 7,72% | 7,76% |
| Một tuổi khác (Tuất, Sửu, Tý, Quý Hợi, Giáp Tý, Ất Sửu) | 6 | 8,20% | 7,99% |
| Không nêu một tuổi (chủ đề chung, nhân vật) | 11 | 4,34% | 4,47% |
| Kiểu NAVY (Search trung vị 36% view) | 9 | 7,75% | 7,45% |
| Kiểu AICN (Search trung vị 8% view) | 8 | 2,57% | 3,71% |
| Kiểu AIVANG | 3 | 4,71% | 6,68% |

### Loạt 2025 cùng khuôn DO25 (lifetime)

| Nhóm | $n$ | CTR trung vị | CTR theo impressions |
|---|---|---|---|
| Mùi + Mão | 2 | 4,65% | 4,98% |
| 8 tuổi còn lại | 8 | 5,84% | 5,48% |

## 3. Hệ thống luật thumbnail Long FS (L1–L6)

| # | Luật | Bằng chứng thực nghiệm | Độ chắc |
|---|---|---|---|
| **L1** | **Long tra cứu theo tuổi:** Tên tuổi/can chi + năm là dòng chữ to nhất, đứng đầu, $\le 4$ từ (ví dụ: `TUỔI MÙI 2027`, `ĐINH MÙI 1967`). Dùng đúng từ khoá người dùng gõ tìm. | Một tuổi $\approx 8\%$ so với chủ đề chung $\approx 4,5\%$. Tương quan Search share với CTR $r = 0,87$ ($n = 16$). | Vừa |
| **L2** | **Chủ thể linh vật:** Một con vật cận mặt, mắt nhìn thẳng, chiếm $\ge 40\%$ khung ở nửa phải. Không dùng cảnh nhiều người nhỏ hay kiến trúc cho Long theo tuổi. | Cả 5 Long một tuổi có mặt con vật cận đều $\ge 7,7\%$ (Tuất, Sửu, Tý, Mùi 2027, Mão T10). | Thấp–vừa |
| **L3** | **Long chủ đề chung (nhà, cưới, bàn thờ...):** Dòng phụ phải là câu hỏi tra cứu cá nhân ("năm sinh nào...?", "tuổi bạn...?"), kèm năm. | NAVY chung có câu hỏi năm sinh đạt 4,7–7,9%; chung không neo chỉ đạt 2,1–2,4% ($n = 6$). | Thấp |
| **L4** | **Số lượng chữ:** Tổng chữ $\le 9$ từ, $\le 2$ cỡ chữ. Bỏ các dòng chữ li ti. | 8 thumbnail $\ge 7,7\%$ đều có 5–9 từ và $\le 2$ cỡ chữ. | Thấp |
| **L5** | **Không kỳ vọng đổi thumbnail cứu được chủ đề thuần Browse:** Chủ đề tư liệu/nhân vật (Tả Ao, Huế, Tần Thuỷ Hoàng) ở mức 1,4–2,3% dù có tên mỏ neo. Cần chọn chủ đề có lượng tìm kiếm trước. | Cùng khuôn THUYMAC/DO25 mà CTR chênh 2–2,5 lần. | Vừa |
| **L6** | **Quy tắc đo lường:** Chỉ kết luận khi có $\ge 1.500$ impressions trong cùng cửa sổ tuổi video. Không so video Search với video Browse. Thay thumbnail giữa đời phải ghi mốc để tách dữ liệu. | Tuổi video làm lệch số rõ rệt (Io70: trọn đời 7,7% so với 11,6% ở cửa sổ 28d muộn). | Cao |

## 4. Giới hạn dữ liệu

- Số liệu FS dừng tại snapshot 09/11/2026.
- Impressions và CTR theo nguồn chỉ có ở cấp kênh, chia lượt xem qua API tới 03/11.
- Một số video bị đổi thumbnail hoặc title giữa đời khiến CTR bị trộn.
- $n = 20$ Long kỳ mới là cỡ mẫu vừa phải; các luật L2–L4 cần tiếp tục kiểm chứng qua Test & Compare.
