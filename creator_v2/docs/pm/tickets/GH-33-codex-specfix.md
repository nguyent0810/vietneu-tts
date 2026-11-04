# GH-33 · Codex: sửa 12 spec bị build chặn + thêm `--preflight` để lỗi này không lặp lại

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/33. Báo cáo render: `docs/pm/tickets/GH-33-render-report.md`. Cả 12 slug đều bị `build.py` chặn trước khi render, vì ba lỗi:

1. **Độ dài** (`build.py:641`): 189–237 từ, trong khi khung là 55–135.
2. **`say` rỗng**, ký hiệu chưa phiên âm: E5, RON 92, E10, TPU, OTP, CVE, RAM, USD, kWh…
3. **`mix_lint`** (`build.py:384`):
   - thiếu cảnh M (ảnh/video cộng đồng);
   - 3 cảnh liền nhau cùng kiểu;
   - kiểu D chiếm > 60% thời lượng;
   - chữ thuần T > 35%.

**Nguyên nhân gốc:** `script_lint.py` không kiểm ba luật này. Vòng spec trước báo "0 lỗi" nhưng build vẫn chặn.

## Được ghi
- 12 spec `data/stier/specs/<slug>.json` (danh sách trong `GH-33-specs-report.md`)
- `motion/stier/build.py`: chỉ thêm `--preflight`, không đổi ngưỡng hay luật nào
- `tests/test_stier_preflight.py`
- báo cáo `docs/pm/tickets/GH-33-specfix-report.md`

**Không:** đổi ngưỡng 55–135 hay luật `mix_lint`; render; TTS; upload; commit; đụng `hf_batch_render`.

## Việc
1. **Thêm `python motion/stier/build.py <slug> [...] --preflight`.** Chạy mọi kiểm tra trước render mà không cần TTS hay mạng:
   - độ dài;
   - luật kết câu của rules-2;
   - cấm "~" trước số;
   - neo chữ: chữ neo phải có trong câu;
   - ký hiệu hoặc viết tắt chưa có trong `say`;
   - `mix_lint` và `bud_layout_lint` nếu áp dụng.

   Thời gian cảnh lấy ước lượng 3,3 từ/giây theo chỉ số từ, giống `script_lint`. Tái dùng đúng các hàm hiện có, không viết luật thứ hai. In LỖI, thoát mã 1 nếu có lỗi. Có test cho các trường hợp trên.
2. **Sửa 12 spec, giữ nguyên:** `title`, hook `lines[0]`, chữ khung 0, các con số và nguồn đã kiểm.
   - Rút lời đọc còn **100–125 từ** (khoảng 30–38 s): bỏ chi tiết phụ, giữ một insight và câu chốt. Câu viết cho tai, mỗi câu một hơi.
   - Thêm `say` cho mọi ký hiệu và viết tắt: E5 → "e năm", RON → "rôn", TPU → "tê pê u", OTP → "ô tê pê", CVE → "xê vê e", kWh → "ki lô oát giờ", USD → "đô la" hoặc "u ét đê" theo ngữ cảnh, …
   - Dựng lại `scenes` cho qua `mix_lint`:
     - có ≥ 1 cảnh M: clip Pexels (`vid`) hoặc ảnh Commons tự do;
     - có D và G;
     - không 3 cảnh liền cùng kiểu;
     - D ≤ 60%, T ≤ 35%.
   - Look xoay qua `motion/stier/looks.py`.
   - CK: clip không có logo hay ticker. Chọn clip Pexels kiểu tay cầm tiền, cây xăng, công tơ điện, quầy vàng… không lộ thương hiệu.
3. Chạy `--preflight` và `script_lint.py` cho cả 12: **0 LỖI ở cả hai**. Thêm một kiểm tra chéo: thời lượng ước lượng 25–40 s.

## Báo cáo
Mỗi slug ghi:
- số từ trước/sau;
- `say` đã thêm;
- chuỗi kiểu cảnh (vd. `[M D G T M D]`);
- kết quả `preflight` và `lint`.

Ghi rõ các câu đã cắt, để Lead kiểm không mất dữ kiện chính.
