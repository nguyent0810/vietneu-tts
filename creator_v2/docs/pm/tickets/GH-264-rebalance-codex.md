# GH-264 — Cân lại nhịp cảnh của 12 Short CL (Codex)

## Vấn đề
Bản render ngày 11/11 có cảnh đứng quá lâu. Đo bằng `output/stier/<slug>/timing.json`, thời lượng từng cảnh tính bằng giây:

| Slug | Thời lượng các cảnh (giây) |
|---|---|
| cl-a-manila-1762 | hero 16.2 · 2.9 · 2.3 · 9.2 |
| cl-a-oppert-1868 | 2.6 · **19.2** · 3.9 · 6.0 |
| cl-a-phaulkon-1688 | 2.5 · 4.5 · **15.8** · 9.3 |
| cl-a-vien-minh-vien-1860 | hero **11.6** · 2.9 · 5.6 · 9.7 |
| cl-bao-s2-au-duong-tu | 2.1 · 11.1 · 3.1 · 12.6 · 2.5 |
| cl-a-nezumi-1831 | 4.3 · 10.0 · 4.8 · 11.9 |

Các bài còn lại tự đo.

Short cần đổi hình đều thì mới giữ được người xem.

## Phạm vi
12 slug:
- `cl-bao-s2-loi-cam`, `cl-bao-s2-song-hue-dan`, `cl-bao-s2-au-duong-tu`
- `cl-a-nezumi-1831`, `cl-a-oppert-1868`, `cl-a-vien-minh-vien-1860`, `cl-a-phaulkon-1688`, `cl-a-manila-1762`, `cl-a-mayrena-1888`
- `cl-dong-lang-min-1928`, `cl-dong-lang-da-min-chau`, `cl-dong-lang-tu-1947`

Riêng `cl-bao-s2-loi-cam`: Lead vừa đổi thứ tự câu, timing cũ không còn đúng. Ước thời điểm theo số từ, 3,3 từ/giây.

## Việc
Chỉ sửa `scenes` (`at`, `label.at`, các mốc con trong `items`). Có thể thêm cảnh, theo luật bên dưới. **Không sửa `lines`.**

Mục tiêu:
- Hero (cảnh 0) dài 2–6 giây.
- Cảnh ảnh (`photo`, `evidence`, `hero`...) dài tối đa 7 giây.
- Cảnh `timeline`, `ledger` có mốc con đổi chữ thì dài tối đa 11 giây, mỗi mốc con cách nhau ≥ 2 giây.
- Không cảnh nào dưới 2 giây.
- Dùng đủ các ảnh trong `imgs`. Ảnh nào chưa có cảnh thì thêm cảnh `photo` (kb in/out, `focus` hợp lý). Một ảnh có thể xuất hiện hai lần nếu thiếu hình; khi đó lần hai đổi `kb` hoặc `focus`.
- Neo vào câu có nội dung khớp ảnh hoặc nhãn: tên người, nơi chốn, tài liệu. Nhãn trên ảnh phải nói đúng điều đang đọc lúc ảnh hiện.
- Loại cảnh chỉ lấy từ bảng trong `motion/stier/README.md`. `timeline` dùng `items[{year,text,at}]`.

## Kiểm
- `build.py --preflight` OK cả 12 bài.
- In bảng thời lượng cảnh (đo từ `timing.json`, riêng loi-cam thì ước lượng) trước và sau khi sửa.
- Ghi bằng Python utf-8, `ensure_ascii=False`, `indent=1`. Grep không có `?` thay chữ có dấu.

## Ràng buộc
Chỉ ghi 12 spec và báo cáo. Không render, không commit.

## Báo cáo
`docs/pm/tickets/GH-264-rebalance-report.md`: bảng trước/sau cho từng bài, và cảnh nào thêm mới, ảnh gì.
