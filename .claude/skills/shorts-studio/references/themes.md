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

## Đã có
| id | Dùng cho | Nền | Font (display / body / mono) | Chuyển động |
|---|---|---|---|---|
| `tet-poster` | FS chủ lực (tuổi, năm, Tết) | giấy sáng, đỏ #C32F27, sơn mài #780116, vàng (chỉ quầng) | Playfair Display 900 / Be Vietnam Pro / JetBrains Mono | expo.out, seam curve, 1 lần nảy |
| `son-mai` | FS cao cấp, sao hạn, đêm | đen ấm #0E0B0C, kem #F3E9D2, đỏ son, vàng kim | Playfair Display / Be Vietnam Pro / Chivo Mono | power3, chậm 1,15, seam blur |
| `saffron` | BUD chủ lực | giấy da #ECE6D8, mực chàm #1B2566, nghệ #B5651D, quầng #E09F3E | Newsreader / Be Vietnam Pro / JetBrains Mono | êm, chậm 1,25, **0 nảy**, seam blur |
| `blueprint` | khoa học, giải thích | kem #F0EBDE + lưới, cobalt #1F2BE0 (hai màu) | Newsreader / Be Vietnam Pro / JetBrains Mono | expo, seam side |
| `archive` | lịch sử | giấy cũ #E8DCC8, mực nâu, huyết dụ #9E2A2B | Old Standard TT / Spectral / Xanh Mono | power2, chậm, 0 nảy, seam blur |

## Đề xuất thêm (đã có token + font kiểm subset: research/D_design_audio.md §2)
`lich-bloc` (bảng năm sinh, coral + Phudu), `dong-ho` (tranh dân gian, Archivo wdth125 + Alegreya), `thien-mac` (thiền thủy mặc, Cormorant + dấu son),
`forest-editorial` (sức khỏe), `hoang-cung` (triều đại), `ledger-gold` (tài chính), `dossier-noir` (pháp luật), `broadside-alarm` (cảnh báo/sự thật), `tinh-tu` (trời đêm).

## Font tiếng Việt (bắt buộc kiểm)
Không có tiếng Việt: Shrikhand, Libre Baskerville, Instrument Serif, Bebas Neue, DM Mono, Bodoni Moda, Fredoka, Archivo Black, Caveat (cả họ hw-* registry),
Lato, Poppins, DM Sans, Outfit, Figtree, Permanent Marker, Courier Prime, Menlo. Thay: Sansita Swashed, Spectral, Newsreader, Phudu / Vina Sans (Việt),
JetBrains Mono, Libre Bodoni, Baloo 2, Archivo 900 wdth125.
Kiểm: render thẻ "ĐỪNG NGỦ QUÊN · Ầ Ẫ Ỗ Ữ Ự Ợ Ặ Ộ · Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi" ở cỡ/độ đậm display, cả hoa lẫn thường.

## Đa dạng trong cùng theme (không phá thương hiệu)
Giữ màu + font; xoay: thiết bị móc (sổ kênh), chữ nền mờ, seam phụ, một "điểm nhấn" (vàng trong chữ / chữ 3D / hạt / glitch -- tối đa một họ mỗi video,
khác video trước). Hai video liền nhau khác nhau ít nhất 2 trong: móc, theme, seam phụ, điểm nhấn.
