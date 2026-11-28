# Spec JSON (một short)

```json
{
  "id": "fs_2027_sinhcon",              // duy nhất; job ở hyperframes_short/jobs/<id>/
  "channel": "fs",                      // sổ đa dạng: output/cl_staging/<channel>/studio_ledger.json
  "theme": "tet-poster",                // studio/themes/<theme>.json
  "kicker": "SINH CON NĂM 2027",        // nhãn mono góc trên (y 110-180)
  "foot": "Kiến thức truyền thống · để tham khảo", // chân trang (y <= 1473)
  "lines": ["Con sinh năm **2027** đều mệnh **Thiên Hà Thủy**.", "..."],   // **x** = từ nhấn (màu accent + phụ đề)
  "tts": true, "voice_series": "fs",    // hoặc "voice": {"wav": "...wav", "manifest": "...json (segments)"}
  "scenes": [ { "device": "hook_poster", "line": 0, "...": "..." }, { "device": "split", "line": 1, "seam": "zoom", "...": "..." } ],
  "loop": true,                         // móc quay lại ở 0,45s cuối (khung cuối ~ khung đầu)
  "seam": "curve",                      // ghi đè seam mặc định của theme
  "capGroup": 5,                        // số từ mỗi cụm phụ đề
  "tail": 3.0,                          // giây giữ hình cuối (BẮT BUỘC >= 3.0s cho khung cuối tự dò)
  "audio": {
    "bgm_gain_db": -20.0,               // BGM -20 dB LUFS dưới giọng đọc (chuẩn BUD & FS)
    "bell": "tibetan_singing_bowl_cc0", // chuông điểm nhấn ở giây 0
    "bell_gain": 0.22
  },
  "out": "output/cl_staging/fs/out/fs_2027_sinhcon.mp4",
  "credits": ["Ảnh: Bảo tàng CMA (cma:147588, CC0)", "Chuông: Freesound #193022 (CC0)"]
}
```

## Vùng hiển thị chuẩn 1080×1920 trong Spec
- **Tiêu đề**: Nằm trong khoảng $y = 110 - 400$. Kicker top 64; tiêu đề chính chữ $\ge 64\text{px}$.
- **Khối nội dung**: Nằm trong khoảng $y = 430 - 1440$. Độ phủ an toàn $\ge 85\%$ ($x$ trong $60 - 940$, $cover \ge 880\text{px}$). Không để khoảng trống dọc nào $> 250\text{px}$.
- **Chân trang & CTA**: Bottom $\le 1473\text{px}$.
- **Phụ đề (Captions)**: Đặt dưới $y = 1490$.
- **Giữ khung cuối (Hold Frame)**: `tail` $\ge 3.0\text{s}$ đứng yên hoàn toàn để khán giả kịp pause/lưu lại.

## Cảnh
- `device` (bắt buộc), `line` = câu mà cảnh bắt đầu (cảnh kéo tới khi cảnh sau bắt đầu, -0,12s), `seam` (curve | side | zoom | inv | blur | hard),
  `ghost` = chữ nền mờ khổng lồ của cảnh (""= không).
- Trường riêng từng thiết bị: `references/devices.md`.

## Mốc thời gian (anchor)
Mọi khoá kết thúc bằng `at`/`At` và các mảng như `flips` nhận:
- `[câu, "từ"]` hoặc `[câu, "từ", lần]`: thời điểm từ đó được đọc (hf_align bám năng lượng âm thanh thật). So khớp tiền tố, bỏ dấu câu, giữ dấu tiếng Việt.
- `[câu, 0.5]`: tỉ lệ trong câu (số thực). `số` = giây tuyệt đối.
- Không thấy từ -> **build dừng** và báo câu/từ (không âm thầm rơi về đầu câu).

## Đầu ra của build
`jobs/<id>/index.html` (engine inline + phiên bản), `plan.json` (cửa sổ cảnh, cảnh báo đa dạng), `qa.json`, `qa_sheet.jpg`,
mp4 + `.render.json` (theme, engine, bgm, ghi nguồn) ở `out`.

## Hook 1 giây

Stay đi cùng view (short ≥ 100 view, 28 ngày): r khoảng 0,52 (BUD), khoảng 0,51 (FS). Giây đầu quyết định người xem có ở lại.

- Khung đầu phải có vật, người, hành động hoặc năm sinh nhìn thấy được.
- Gợi ý tiêu đề chứa danh từ cụ thể: vật chùa, bộ phận tượng, hành động của tăng, năm sinh, tên chi, hoặc ngày.
- Cảnh báo biên tập khuôn "X có phải là Y?" khi X là khái niệm trừu tượng (chánh niệm, buông bỏ, vô thường, từ bi, trung đạo, nhân quả, thái cực, ngũ hành, …). "Có phải là" vẫn được khi X nhìn thấy được, như địa ngục.

Đạt:

- "Vì sao nhà sư cạo tóc?" — stay 53%
- "Địa ngục có phải là bản án vĩnh viễn?" — stay 51%
- "1984, 1985: mệnh Hải Trung Kim" — stay 63%

Không đạt (stay 9–15%):

- "Chánh niệm có phải là mặc kệ ngày mai?" — 13%
- "Thương con có phải là làm hết cho con?" — 11%
- "Thái cực sinh lưỡng nghi nghĩa là gì?" — 11%
- "Phong thủy, Tử Vi, Bát Tự có phải là một?" — 14%
- "Vì sao Phật ví giáo pháp như chiếc bè?" — 9%. "Giới không uống rượu là để giữ điều gì?" — 11%. Mở bằng giáo lý. Giây đầu vẫn phải là vật, người hoặc hành động đang xảy ra.

Kiểm plan trước khi chốt:

```bash
.venv/bin/python library/tools/hook_lint.py <plan.json>
.venv/bin/python library/tools/hook_lint.py --unpublished
```

Nguồn runtime: `library/tools/hook_lint.py`, dữ liệu `library/tools/hook_terms.json`. `TRUU_TUONG`/`KHONG_DANH_TU_CU_THE` chỉ gợi ý; chỉ `KHUNG_DAU_TRONG` chặn hình cũ (exit1). Chuẩn lời và profile: [audio-script §8–9](../../../../docs/script/audio-script.md#8-chọn-hồ-sơ-chỉ-đọc-phần-khác-lõi).


### Nhịp và lời đọc FS/BUD
Không tạo `cuts` để chia shot dưới 3 giây; nếu có shot dưới 3 giây thì cảnh báo khi lint/render. Cảnh dài dùng cine/pan/parallax chậm thay vì cắt vụn. FS mở bằng lời luận trực tiếp, không rào đón; chỉ một lời “tham khảo” ở cuối kịch bản. BUD kể nhẹ nhàng, nhân văn và giàu chuyện; lời Phật phải đối chiếu kinh. Short phải có hook kịch tính/nghịch lý trong 3 giây đầu, không chào hay rào đón.
