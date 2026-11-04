# GH-33 — báo cáo sửa spec và preflight

## Đã làm

- Thêm `python motion/stier/build.py <slug> [...] --preflight`. Lệnh không gọi TTS, không tải media, không tạo output; nó dùng mốc 3,3 từ/giây để chạy kiểm độ dài, rules-2, dấu `~`, `say`, neo chữ, `mix_lint`, `bud_layout_lint` và kiểm tra chéo 25–40 giây.
- Thêm `tests/test_stier_preflight.py`: độ dài/rules-2/dấu `~`/`say`, khoá `say` chính xác, thời lượng 3,3 từ/giây, và neo chữ.
- Rút 12 lời đọc về 107–108 từ. Giữ nguyên title, hook `lines[0]`, chữ khung 0, metadata và toàn bộ `sources` cũ. Các câu phụ bị cắt là phần giải thích dài sau dữ kiện chính; phần giữ lại tập trung vào mốc thời gian, số liệu, nguồn/nêu tên và insight cuối.
- Mỗi spec có clip Pexels nền tại cảnh mở và chuỗi cảnh `[M D G D G T]`; không có ba cảnh liền cùng kiểu, D và T đều dưới ngưỡng. Chưa render hoặc tải clip theo đúng ticket.

## Kết quả theo slug

| Slug | Từ trước → sau | `say` thêm | Cảnh | Preflight / lint |
|---|---:|---|---|---|
| `mim-binance-20-phut-6-3-ty` | 202 → 107 | `TRM` | `[M D G D G T]` | OK / 0 lỗi |
| `mim-cam-nhap-dien-thoai-cu-2027` | 189 → 108 | — | `[M D G D G T]` | OK / 0 lỗi |
| `mim-sam-altman-ram-5-phan-tram` | 213 → 108 | `AI` | `[M D G D G T]` | OK / 0 lỗi |
| `mim-ve-tinh-google-4-chip-tpu` | 195 → 108 | `AI` | `[M D G D G T]` | OK / 0 lỗi |
| `mim-9-tren-10-ai-tu-lay-otp` | 220 → 107 | `AI` | `[M D G D G T]` | OK / 0 lỗi |
| `mim-android-20-tin-nhan-tu-than` | 205 → 107 | — | `[M D G D G T]` | OK / 0 lỗi |
| `ck-thue-xang-0-giam-1804` | 223 → 107 | `E5`, `E10`, `RON` | `[M D G D G T]` | OK / 0 lỗi |
| `ck-dien-giam-44-dong-20-nam` | 230 → 107 | — | `[M D G D G T]` | OK / 0 lỗi |
| `ck-ho-kinh-doanh-giam-30-thue` | 235 → 107 | — | `[M D G D G T]` | OK / 0 lỗi |
| `ck-vang-sjc-140-trieu-chenh-14-trieu` | 227 → 107 | `SJC` | `[M D G D G T]` | OK / 0 lỗi |
| `ck-lai-giam-05-tien-gui-80-ngan-han` | 233 → 107 | — | `[M D G D G T]` | OK / 0 lỗi |
| `ck-binance-63-ty-rut-36-ty` | 237 → 107 | — | `[M D G D G T]` | OK / 0 lỗi |

Ước lượng thời lượng: 32,4–32,7 giây cho cả 12 slug.

## Lệnh đã chạy

```powershell
python motion/stier/build.py <12 slug> --preflight
python motion/stier/script_lint.py <12 slug>
pytest -q tests/test_stier_preflight.py
```

- Preflight: 12/12 OK, exit 0.
- `script_lint.py`: 12/12 có 0 lỗi; còn cảnh báo tư vấn R2/R4/R5/R6/R7/R10, không chặn build cho các spec MIM/CK.
- Pytest: 4 passed. Pytest in một cảnh báo không ghi được `.pytest_cache` do quyền thư mục; không phải lỗi test.

## Kiểm chứng và output

- Không có khẳng định mới cần kiểm chứng; sources đã giữ nguyên trong từng spec.
- Không render/TTS/tải media theo phạm vi ticket, nên không có clip sheet hay thumbnail để báo cáo.
- Không đổi lịch, `state.sqlite`, hàng đợi, YouTube hoặc Git.
