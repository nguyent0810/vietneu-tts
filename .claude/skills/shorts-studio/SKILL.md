---
name: shorts-studio
description: Dựng short dọc 9:16 có lời đọc tiếng Việt cho BẤT KỲ kênh/chủ đề nào bằng HyperFrames -- bộ thiết bị hình (device) dùng lại được, khối registry đã cài sẵn, nhiều theme, luật đa dạng chống rập khuôn, và cổng QA kiểm duyệt khắt khe. Dùng khi làm short mới cho kênh FS, BUD hoặc kênh mới, khi cần đổi phong cách hay kiểm tra bố cục & âm thanh.
---

# Shorts Studio (HFS)

Một short = **một file spec JSON** $\rightarrow$ `studio.py` dựng job HyperFrames (một composition, một timeline GSAP paused), render, trộn âm thanh, chạy QA.
Engine: `hyperframes_short/studio/` (core.js, base.css, devices/*.js, themes/*.json). Builder: `studio.py` (gốc repo).

---

## 1. Vibe từng kênh & "Chữ ký" hình riêng

Mỗi video phải có một **"chữ ký" hình riêng**, không để 2 video kề nhau lặp lại cùng một phong cách hay hiệu ứng thị giác:
- **Phong Thủy (FS)**: Nền chàm huyền bí hoặc đỏ son – vàng kim (`tet-poster`, `son-mai`), bát quái/Thái cực mờ sau bảng, dấu son niêm ấn, núi non thủy mặc. Biến chuyển qua la bàn Hậu Thiên xoay 3D, sơ đồ bàn tay chỉ tay nét vàng, hoặc dải hạt ngũ hành.
- **Phật Giáo (BUD)**: Nền nâu trầm / vàng nghệ ấm cúng (`saffron`), hoa sen nở đáy, ánh nến lung linh.
  - **ẢNH THẬT tượng Phật (Luật 17)**: Sử dụng ảnh thật tượng Phật, phù điêu, tranh cổ từ bảo tàng công cộng CC0 (CMA, Met, AIC) hoặc Wikimedia Commons. **Cấm vẽ mặt Đức Phật bằng code, hoạt hình, biếm họa.** Từ 23/10/2026 được dùng ảnh AI (ChatGPT, Flow) có mặt Đức Phật khi mặt không méo và trang nghiêm (docs/adr/0004). Sử dụng trang nghiêm: không đặt chữ đè lên mặt tượng, không cắt ngang đầu tượng, chuyển động máy chậm (scale 1.00 $\rightarrow$ 1.04).

---

## 2. Quy chuẩn Bố cục 1080×1920

Toàn bộ bố cục dọc 9:16 phải tuân thủ nghiêm ngặt các mốc tọa độ hiển thị:
- **Tiêu đề (Header)**: Vùng $y = 110 - 400$. Chip danh mục top 64, tiêu đề 2 dòng đậm nét (cỡ chữ $\ge 64\text{px}$).
- **Nội dung chính (Body)**: Vùng $y = 430 - 1440$. Phủ $\ge 85\%$ bề ngang an toàn ($x$ trong $60 - 940$, $cover \ge 880\text{px}$).
- **Khoảng trống dọc**: Tuyệt đối không để khoảng trống dọc nào $> 250\text{px}$ giữa các thành phần.
- **Cỡ chữ**: Nội dung/giải nghĩa $\ge 36\text{px}$; chữ số chính/năm sinh $\ge 90\text{px}$.
- **Phụ đề**: Nằm hoàn toàn dưới $y = 1490$ (tránh đè nút Shorts bên phải và vùng điều khiển).
- **Khung cuối (Hold Frame)**: Đứng yên tuyệt đối $\ge 3$ giây ở cuối video (`mean abs difference` $\le 0.05$) để người xem kịp pause và chụp màn hình.
- **Mỹ thuật BUD**: Tuyệt đối không đè chữ/bảng lên mặt tượng Phật.

---

## 3. Quy chuẩn Âm thanh (Audio Mixing)

- **Phật Giáo (BUD)**:
  - Nhạc thiền tĩnh lặng, không lời, không trống (`hf_music.CATALOG["bud"]`: White Lotus, Peace of Mind, That Zen Moment...).
  - Mức nhạc khoảng **$-20\text{ dB}$ LUFS dưới giọng đọc** (chênh lệch đúng $-20.0\text{ dB}$, vd giọng $-18\text{ LUFS}$ thì nhạc $-38\text{ LUFS}$).
  - Nhạc vào trước giọng đọc $0,5 - 1\text{s}$ (`adelay=600|600`).
  - Ở 3 giây cuối, nhạc giảm dần nhưng giữ nhẹ $\sim 40\%$ âm lượng nền cho tới hết video (`afade=t=out:st=dur-3:d=3:silence=0.4`), không tắt phụt.
  - **Điểm nhấn**: 1 tiếng chuông xoay Tây Tạng CC0 (Tibetan singing bowl) ở giây 0 hoặc trước câu Phật dạy.
- **Phong Thủy (FS)**: Nhạc phương Đông chậm, huyền bí (`CATALOG["fs"]`). **BỎ Asian Drums cho dạng bảng tĩnh**. Có tiếng gió/chuông gió nhẹ khi đóng dấu son.
- **Xoay vòng chống spam YouTube**: Không để bản nhạc nào chiếm $> 35\%$ số short trong 7 ngày gần nhất trên kênh. Ghi sổ `bgm_shorts.json`.

---

## 4. Dạng thắng & Dạng đã thua (Định hướng nội dung)

### Dạng thắng (Tập trung sản xuất):
1. **Bảng tự dò (10–15s)**: Hook tìm kiếm $\rightarrow$ Bảng tuổi/năm/chi/ngày $\rightarrow$ Khung cuối giữ $\ge 3\text{s}$ + CTA lưu/pause.
2. **Lời Phật 9 giây (9–12s)**: Tượng Phật chậm (1.00 $\rightarrow$ 1.04) $\rightarrow$ Câu kinh hiện theo giọng $\rightarrow$ Nguồn Pháp Cú $\rightarrow$ Khung đứng $\ge 3\text{s}$.
3. **Nhân quả trong kinh (75–120s)**: Mở bằng cảnh cao trào nhất $\rightarrow$ Lùi lại kể $\rightarrow$ Cú lật nhân quả $\rightarrow$ 1 câu Phật dạy $\rightarrow$ Câu hỏi chiêm nghiệm.
4. **Biểu tượng – trả lời nhanh (12–18s)**: Ảnh tượng/pháp khí hero $\rightarrow$ Câu hỏi chi tiết lạ $\rightarrow$ Trả lời 1–2 dòng + spotlight chỉ vào chi tiết.
5. **Chỉ tay / nhân tướng (8–12s)**: Hook tự kiểm (*"Bạn có đường này không?"*) $\rightarrow$ Sơ đồ bàn tay nét vàng + đèn soi $\rightarrow$ Thẻ giải nghĩa tham khảo.
6. **"N con giáp tháng tới" (10–15s)**: Bảng 12 chi có N ô sáng theo tam hợp/lục hợp với chi tháng (tính bằng code) $\rightarrow$ Không hứa tiền.

### Dạng đã thua (KHÔNG làm lại):
- Hỏi – giảng lý thuyết 20–35s (khô khan, tụt view).
- Hoạt hình Tiền Thân kể tóm tắt (thiếu cao trào, không cú lật).
- Cung hoàng đạo phương Tây (lệch tệp khán giả).
- Giọng dọa nạt (*"hậu họa"*, *"tai ương"*) hoặc hứa tiền bạc (*"giàu ngầm"*).

### Hook 1 giây

Giây đầu phải nhìn thấy vật, người, hành động hoặc năm sinh. Tiêu đề phải có danh từ cụ thể (vật chùa, bộ phận tượng, hành động của tăng, năm sinh, tên chi, ngày). Cấm khuôn "X có phải là Y?" khi X là khái niệm trừu tượng.

Đạt: "Vì sao nhà sư cạo tóc?" (53%), "Địa ngục có phải là bản án vĩnh viễn?" (51%), "1984, 1985: mệnh Hải Trung Kim" (63%).

Không đạt: "Chánh niệm có phải là mặc kệ ngày mai?" (13%), "Thương con có phải là làm hết cho con?" (11%), "Thái cực sinh lưỡng nghi nghĩa là gì?" (11%), "Phong thủy, Tử Vi, Bát Tự có phải là một?" (14%).

Ví dụ đầy đủ và lệnh kiểm: [references/spec.md](references/spec.md).

---

## 5. Khối Registry HyperFrames đã cài sẵn

Lead đã cài sẵn các khối registry vào thư mục `hyperframes_short/compositions/`:
- **Components**:
  - `components/ink-bleed-reveal`: Lộ diện loang mực truyền thống cho tiêu đề và tranh thủy mặc.
  - `components/text-shimmer`: Vệt sáng quét qua chữ tiêu đề hoặc từ khóa.
  - `components/grain-overlay`: Phủ hạt phim vintage tăng chiều sâu (chú ý: CSS keyframes không seek-safe, dùng thận trọng).
  - `components/particle-text-dissolve`: Tụ hạt / tan hạt vàng tạo chữ.
  - `components/constellation-hub`: Đồ thị sao / vòng liên kết chòm sao/ngũ hành.
- **Compositions**:
  - `ui-3d-reveal.html`: Lật thẻ 3D phối cảnh cho bảng danh sách.
  - `lens-flare.html`: Lóe sáng ống kính.
- > [!WARNING]
  > **CẢNH BÁO SHADER**: Khối `lens-flare` sử dụng WebGPU shader canvas (`data-requires-webgpu data-no-timeline`), cần render thử trước trên môi trường thực tế để tránh crash headless browser.
- > [!CAUTION]
  > **Luật 18**: Thợ **KHÔNG chạy `hyperframes add`** (chế độ tự động bị chặn). Khi cần khối registry mới, ghi tên khối vào báo cáo để Lead cài đặt.

---

## 6. Quy trình Đạo diễn & Dựng bài

1. **Brief**: Kênh (FS/BUD), chủ đề, mục tiêu, luật kênh. Số liệu tính bằng code (`tuvi_year.py`, `canchi.py`, `amlich.py`), lời kinh đối chiếu `hf_sutta.py`.
2. **Kịch bản**: 6–8 câu (với dạng 30s) hoặc 1–3 câu (với dạng 9–15s). Câu 1 theo mục Hook 1 giây.
3. **Beat sheet & Thiết bị**: Khung 0 đủ nghĩa; $\ge 3$ khung khác nhau; không lặp khung/trục liền kề; ảnh stock/tượng không để trơ trọi.
4. **Theme**: Chọn theo kênh (`tet-poster`, `son-mai` cho FS; `saffron` cho BUD).
5. **Spec JSON**: Khai báo vùng an toàn, anchor thời gian, âm thanh (-20 dB LUFS, chuông CC0).
6. **Bộ kiểm bắt buộc (QA Gate)**:
   - Tràn chữ: `overflow n=0`, font900 có mặt.
   - Top $\ge 40$ ở 4 mốc (10%, 35%, 65%, cuối).
   - Đo khoảng trống dọc ($gap \le 250\text{px}$) và độ phủ ngang an toàn ($cover \ge 85\%$).
   - Soát hiển thị ở $1080\times 1920$ và $168\text{px}$ (thumbnail mobile đọc rõ tiêu đề và tên hàng).
   - Dựng tờ ảnh tại 4 mốc: 25%, 50%, 75%, cuối.
   - **Mở xem và mô tả thật từng ảnh (Luật 15 & 17)**: Nhìn tận mắt, mô tả thật những gì thấy vào báo cáo.
   - Hook: `hook_lint.py` trên plan, exit 0 (cờ và danh sách từ trong `references/spec.md`).
7. **Bàn giao**: mp4 + `.render.json` tại `output/cl_staging/studio_out/` (hoặc thư mục task); ghi sổ `bgm_shorts.json`.

---

## Lệnh thực thi

```bash
# Xem thiết bị và theme có sẵn
.venv/bin/python studio.py devices
.venv/bin/python studio.py themes

# Build và kiểm tra QA spec
.venv/bin/python studio.py build output/cl_staging/studio_specs/<id>.json --render --qa [--strict]
```
Mẫu spec tham khảo: `examples/demo_fs_sinhcon.json` (`tet-poster`), `demo_bud_batchanhdao.json` (`saffron`).
Chi tiết kỹ thuật sâu xem tại `references/`: [themes.md](file://references/themes.md), [qa.md](file://references/qa.md), [devices.md](file://references/devices.md), [spec.md](file://references/spec.md).
