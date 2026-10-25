# Theme

Theme = `hyperframes_short/studio/themes/<id>.json`: nguyên tử thiết kế cố định (màu, font, tính cách chuyển động), bố cục tự do theo thiết bị.
"Atoms are sacred · composition is free · numbers come from the script." (hyperframes-creative presets)

## Trường
```json
{ "id": "tet-poster", "label": "...",
  "fonts": "https://fonts.googleapis.com/css2?...",          // nguồn để `studio.py fonts` tải woff2 về studio/fonts (render dùng file cục bộ);
                                                             // MỌI họ font phải có subset vietnamese -- lệnh in "THIẾU tiếng Việt" nếu không
  "vars": { "ground","ground2","card","ink","ink-soft","soft-text","accent","accent2","on-accent","on-accent2","glow","glow-soft",
            "line","ghost","ghost-accent","shadow","cap-dim","radius","seal-bg","quote-weight","display-weight",
            "font-display","font-body","font-mono","font-quote","font-cjk","bloom","grain" },
  "motion": { "entry","exit","move","draw","accent","speed","overshoot","blur" },   // speed > 1 = chậm hơn; overshoot = số lần được nảy
  "seam": "curve|side|zoom|inv|blur|hard", "accents": [...],
  "sfx": { "open": [tên, gain, tên, gain], "seam", "stamp", "tick", "land" },     // tên trong hf_sfx: bell bowl chime gong woodblock tick whoosh brush paper
  "bgm": "fs|bud" }                                                               // pool hf_music
```
Luật màu: một accent; mọi hex có trong vars (không hex trong device); contrast WCAG AA (check tự kiểm); không gradient tuyến tính toàn khung trên nền tối (banding H.264).

## 1. Vibe từng kênh & "Chữ ký" hình riêng
- **Phong Thủy (FS)**:
  - Tông màu: Nền chàm huyền bí hoặc đỏ son – vàng kim (`tet-poster`, `son-mai`).
  - Yếu tố thị giác: Bát quái/Thái cực mờ sau bảng dữ liệu, dấu son niêm ấn, núi non phong cảnh thủy mặc.
  - "Chữ ký" hình: Mỗi bài có một nét nhận diện riêng (la bàn Hậu Thiên 3D nghiêng 32°, sơ đồ chỉ tay bàn tay nét vàng có đốt, dải hạt ngũ hành xoay vòng...), không lặp lại nguyên xi giữa 2 bài kề nhau.
- **Phật Giáo (BUD)**:
  - Tông màu: Nâu trầm / vàng nghệ ấm cúng (`saffron`), tạo cảm giác trang nghiêm thanh tịnh.
  - Yếu tố thị giác: Bánh xe Pháp luân mờ sau bảng, hoa sen nở đáy, khói hương, ánh nến lung linh.
  - **ẢNH THẬT tượng Phật (Luật 17)**: Dùng ảnh thật tượng Phật, phù điêu, tranh cổ từ bảo tàng công cộng CC0 (CMA, Met, AIC) hoặc Wikimedia Commons. **Cấm vẽ mặt Đức Phật bằng code, hoạt hình, biếm họa.** Từ 23/10/2026 được dùng ảnh AI (ChatGPT, Flow) có mặt Đức Phật khi mặt không méo và trang nghiêm (docs/adr/0004). Không đặt chữ đè lên mặt tượng, không cắt ngang đầu, camera phóng chậm 1.00 $\rightarrow$ 1.04.

## 2. Quy chuẩn Âm thanh theo kênh
- **BUD**:
  - Nhạc thiền tĩnh lặng, không lời, không trống (`CATALOG["bud"]`: White Lotus, Peace of Mind, That Zen Moment...).
  - Mức âm lượng: **$-20\text{ dB}$ LUFS dưới giọng đọc** (chênh lệch đúng $20.0\text{ dB}$).
  - Nhạc vào trước giọng $0,5 - 1\text{s}$ (`adelay=600|600`).
  - Ở 3s cuối: Nhạc giảm dần nhưng giữ nhẹ $\sim 40\%$ âm lượng nền cho tới hết khung đứng (`afade=t=out:st=dur-3:d=3:silence=0.4`), không tắt phụt.
  - Điểm nhấn: 1 tiếng chuông xoay Tây Tạng CC0 (Tibetan singing bowl) ở giây 0 hoặc trước câu Phật dạy.
- **FS**:
  - Nhạc phương Đông chậm, huyền bí (`CATALOG["fs"]`).
  - **BỎ Asian Drums cho dạng bảng tĩnh** vì nhịp trống dồn dập gây mất tập trung khi đọc bảng. Có tiếng gió/chuông gió nhẹ khi đóng dấu son.
- **Xoay vòng chống spam YouTube**: Không để bản nhạc nào chiếm $> 35\%$ số short trong 7 ngày gần nhất. Ghi sổ `bgm_shorts.json`.

## 3. Theme đã có trong hệ thống
| id | Dùng cho | Nền | Font (display / body / mono) | Chuyển động |
|---|---|---|---|---|
| `tet-poster` | FS chủ lực (tuổi, năm, Tết) | giấy sáng, đỏ #C32F27, sơn mài #780116, vàng (chỉ quầng) | Playfair Display 900 / Be Vietnam Pro / JetBrains Mono | expo.out, seam curve, 1 lần nảy |
| `son-mai` | FS cao cấp, sao hạn, đêm | đen ấm #0E0B0C, kem #F3E9D2, đỏ son, vàng kim | Playfair Display / Be Vietnam Pro / Chivo Mono | power3, chậm 1,15, seam blur |
| `saffron` | BUD chủ lực | giấy da #ECE6D8, mực chàm #1B2566, nghệ #B5651D, quầng #E09F3E | Newsreader / Be Vietnam Pro / JetBrains Mono | êm, chậm 1,25, **0 nảy**, seam blur |
| `blueprint` | khoa học, giải thích | kem #F0EBDE + lưới, cobalt #1F2BE0 (hai màu) | Newsreader / Be Vietnam Pro / JetBrains Mono | expo, seam side |
| `archive` | lịch sử | giấy cũ #E8DCC8, mực nâu, huyết dụ #9E2A2B | Old Standard TT / Spectral / Xanh Mono | power2, chậm, 0 nảy, seam blur |

## Font tiếng Việt (bắt buộc kiểm)
- **Không có tiếng Việt**: Shrikhand, Libre Baskerville, Instrument Serif, Bebas Neue, DM Mono, Bodoni Moda, Fredoka, Archivo Black, Caveat (cả họ hw-* registry), Lato, Poppins, DM Sans, Outfit, Figtree, Permanent Marker, Courier Prime, Menlo.
- **Thay thế chuẩn**: Sansita Swashed, Spectral, Newsreader, Phudu / Vina Sans (Việt), JetBrains Mono, Libre Bodoni, Baloo 2, Archivo 900 wdth125, Be Vietnam Pro.
- **Kiểm tra**: Render chuỗi test "ĐỪNG NGỦ QUÊN · Ầ Ẫ Ỗ Ữ Ự Ợ Ặ Ộ · Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi" ở cỡ và độ đậm display.
