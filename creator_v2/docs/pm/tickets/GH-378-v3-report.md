# Báo cáo ticket GH-378-v3: Viết lại lời Long CL cl-hoang-kim-vinh theo cách mới (§14)

**Ngày thực hiện:** 15/11/2026  
**Người thực hiện:** agy Gemini (vai người kể theo #430)  
**Brief:** `docs/pm/tickets/GH-378-v3-brief.md`  
**File kịch bản xuất bản:** `data/long/cl-hoang-kim-vinh/script.v3.md` (không ghi đè `script.md`)

---

## 1. Trục kể và văn phong (§14 Storytelling Guide)

- **Trục nhân vật:** Hoàng Kim Vinh — từ cậu bé mặt rỗ học việc đóng tranh, leo lên vị trí thám tử người Hoa cấp cao nhất tô giới Pháp, bắt tay thế giới ngầm thâu tóm đường dây thuốc phiện Bến Thượng Hải, ngông cuồng đánh con quân phiệt dẫn đến mất ghế, lui về nhường đệ tử Đỗ Nguyệt Sanh rồi tham gia cuộc thanh trừng đẫm máu 1927, mua lại lâu đài Đại Thế Giới, và cuối đời gánh chịu cái giá nhục nhã: tự thú và cầm chổi quét rác trước cửa cơ ngơi năm xưa.
- **Cấu trúc 14 chương (CH00–CH13):** Bỏ hoàn toàn cấu trúc lộ trình cũ ("bốn mốc, bốn cách kể"). Mỗi chương là một chặng diễn tiến của nhân vật: Tình thế → Lựa chọn → Hệ quả → Câu hỏi/hệ quả kéo sang chương sau.
- **Cú twist đối chiếu:** Chỉ dùng một lần ở CH09 đối chiếu mục Hoàng Kim Vinh trong cuốn sách *Hải Thượng Danh Nhân Truyện* (1930) tô vẽ một nhà từ thiện đạo mạo, với sự thật trần trụi từ hai mục của Đỗ Nguyệt Sanh và Trương Khiếu Lâm trong cùng cuốn sách thừa nhận một đêm huyết chiến thanh trừng 1927.
- **Phỏng dựng cảnh `{pd}`:** 7 cảnh phỏng dựng không khí/cảm xúc (bến cảng Hoàng Phố cuối thế kỷ 19, phòng kín phiên xử ngầm, hỗn loạn ở rạp hát, xà lim quân sự tối tăm, giả lú lẫn trong phòng tối, suy đoán lý do ở lại). Mọi cảnh đều có lời báo hiệu ("hãy hình dung", "có lẽ"), không bịa con số, sự kiện hay lời trích.
- **Rào nguồn:** Giảm sâu từ 26,15% (bản cũ) xuống còn 1,70% (5 câu / 294 câu). Loại bỏ toàn bộ các câu siêu hình so sánh nguồn ("Wikipedia tiếng Anh ghi", "bách khoa tiếng Trung chép", "hai bản lệch nhau"). Nguồn được đẩy lên đồ họa màn hình.

---

## 2. Cold Open (CH00 - Cửa sổ sốc 40 giây)

- **Giây 0–5 (3 câu đầu):** Đập ngay vào khoảnh khắc bi kịch mùa đông 1951 — ông già ngoài tám mươi tuổi cầm chổi quét rác trước cửa Đại Thế Giới, người qua đường thảng thốt nhận ra gương mặt rỗ của cựu ông trùm số một Bến Thượng Hải.
- **Câu 4 (trước câu 5, trước giây 8):** Nêu câu hỏi nghịch lý/hậu quả: *"Làm sao một viên đốc sát trưởng khét tiếng lại kết thúc cuộc đời bên một cây chổi quét đường?"*
- **Trước giây 15:** Bằng chứng đối lập — ngày 20/5/1951 hai tờ báo lớn đăng bản tự thú với câu trích nguyên văn: *» Nguyện thẳng thắn thú nhận và hối lỗi trước nhân dân. [TRÍCH DỊCH]*
- **Quy tắc giữ chân:** Không chào hỏi, không giới thiệu kênh, không đọc lộ trình trước 30 giây.

---

## 3. Ba phương án tiêu đề (Mẫu survival ≤ 60 ký tự)

1. **Phương án 1 (57 ký tự):**
   `Trùm Bến Thượng Hải: Cuối Đời Tự Thú Và Cầm Chổi Quét Rác`
   - *Đối tượng:* Hoàng Kim Vinh (ông trùm Bến Thượng Hải)
   - *Bi kịch / Cái giá:* Từ quyền lực tột đỉnh đến kẻ phải tự thú và cầm chổi quét rác.
2. **Phương án 2 (58 ký tự):**
   `Thám Tử Tô Giới Lên Ông Trùm: Cái Giá Của Quyền Lực Hai Mặt`
   - *Đối tượng:* Hoàng Kim Vinh
   - *Nghịch lý:* Viên cảnh sát thực dân kiêm thủ lĩnh thế giới ngầm.
3. **Phương án 3 (56 ký tự):**
   `Đêm Mất Sạch Quyền Lực Vì Một Cô Đào Hát Ở Bến Thượng Hải`
   - *Đối tượng:* Hoàng Kim Vinh
   - *Tình thế ngặt:* Quyết định ngông cuồng năm 1924 làm sụp đổ ngai vàng cảnh sát.

---

## 4. Kết quả kiểm tra kỹ thuật (Python)

Toàn bộ các cổng kiểm tra kỹ thuật được chạy trên nội dung mới `data/long/cl-hoang-kim-vinh/script.v3.md`:

| Chỉ số / Cổng kiểm | Yêu cầu brief | Kết quả đạt được | Đánh giá |
|---|---|---|---|
| **Tổng số âm tiết** | 5.600 – 6.800 | **6.359 âm tiết** | **ĐẠT** |
| **Số chương** | 13 – 14 chương | **14 chương (CH00–CH13)** | **ĐẠT** |
| **Độ dài mỗi câu** | ≤ 32 âm tiết | **0 câu > 32 âm tiết** (Max: 27 âm tiết) | **ĐẠT** |
| **Tỉ lệ rào nguồn** | ≤ 8% | **1,70% (5 / 294 câu)** | **ĐẠT** |
| **Cảnh phỏng dựng `{pd}`** | Báo lời + nhãn `{pd}` | **7 cảnh** | **ĐẠT** |
| **`sl.gate(chs)`** | `gate == []` | **0 lỗi** | **ĐẠT** |
| **`cr.audio_problems(chs)`**| `audio_problems == []` | **0 lỗi** | **ĐẠT** |
| **`sl.beat_warnings(chs)`** | Cảnh báo nhịp 30s | **0 cảnh báo** (100% cửa sổ có beat) | **ĐẠT** |
| **Xưng hô & Ngắt giọng** | Có "bạn", có `‖` | **Đủ "bạn", nhiều điểm nghỉ dài `‖`** | **ĐẠT** |

---

## 5. Tuân thủ luật repo và AGENTS.md

- Không upload, không sửa đổi, không xóa dữ liệu trên YouTube.
- Không ghi `state.sqlite`.
- Không đụng git: không commit, không push, không reset/checkout.
- Không sửa code dùng chung (`motion/hf/assets/engine/*`, `build_long.py`, v.v.).
- Không render hay gọi TTS (đúng phạm vi kịch bản của ticket).
- Ghi toàn bộ file tiếng Việt bằng Python `encoding="utf-8"`, không dùng PowerShell.
