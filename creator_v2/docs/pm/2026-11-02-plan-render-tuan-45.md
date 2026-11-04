# Nháp plan render tuần 45 (03–09/11/2026), MIM và CK

Nháp để chủ kênh duyệt, **chưa giao ai, chưa render, chưa đụng lịch**. Căn cứ: `docs/pm/2026-11-02-thang-thua-tuan-44.md` (số thô ở `output/analysis/week44/`). Mọi hook là giả thuyết cần đo lại; số liệu Studio tuần 44 chưa có.

## 1. Nguyên tắc rút từ tuần 44

1. Khung 0–3 s phải có **một mâu thuẫn cụ thể**: CK = hai khoản tiền đối nghịch cùng một vật (317 ↔ 154 triệu); MIM = người **có tên** nói điều trái kết quả.
2. Không render thêm: Short chứng khoán chung / giải thích cơ chế (CK C2), nhân vật vô danh ở câu mở (MIM), danh sách phí không có cặp số.
3. Mọi số trong hook phải có dòng trong `factcheck.md`/`results.json`; số tự giả định ghi VÍ DỤ GIẢ ĐỊNH (luật CK).
4. Mỗi Short gắn nhãn S (tự trọn vẹn) hoặc L (kéo Long, có điều tiếp theo thật). Không dùng Short như trailer.
5. Một Long mỗi lần, chỉ sau khi chủ kênh duyệt kịch bản (`CLAUDE.md`).

## 2. Cái đã có sẵn, không cần render (chỉ cần chủ kênh quyết xếp lịch)

- CK có 19 spec đã có `final.mp4` nhưng **chưa vào hàng chờ**: 7 bài `ck-b4-*` (xe), `ck-b1-muoi-nam-sau`, `ck-b1-thuong-tru-nha-thue`, 6 bài `ck-c3-*` (nến), `ck-bang-tran-thue-nha`, `ck-c2-gia-san-gioi-han-gi`. Hàng chờ CK hết 12/11, trống 13/11–22/11. Nhóm có cặp số rõ trong câu đầu (`ck-b4-bay-tram-thanh-tam-tram` "700 → 800 triệu", `ck-b4-tra-gop-them-184-trieu`, `ck-b1-muoi-nam-sau`) nên đi trước; nhóm `ck-c3-*` (đếm nến) giữ sau và không dồn một ngày.
- MIM có 106 Short chờ tới 04/12, không còn spec rảnh. Hàng chờ đã nhiều nhân vật có tên (Kasparov, Jennings, Watson). MIM **không cần thêm Short mới**; việc render của MIM là Long và Short đi kèm.

## 3. Danh sách render đề xuất (xếp theo tác động kỳ vọng)

Mốc đo chung (từ số tuần 44; CK dùng nhóm tuổi 0–1,5 / 1,5–3 / 3–6 ngày, trung vị 111 / 514 / 607; MIM 332 / 745 / 807):
- **24 h:** view ≥ trung vị nhóm 0–1,5 ngày của kênh (CK 111, MIM 332).
- **72 h:** view ≥ trung vị nhóm 1,5–3 ngày (CK 514, MIM 745) và "xem / lướt qua" ≥ mức trung vị kênh khi Studio đọc được (EVR proxy chỉ tham khảo).
- **7 ngày:** CK ≥ 692 (trung vị cụm nhà ở tuần 44), MIM ≥ 800 (cụm Lee Sedol 830). Sub/1.000 view ≥ 0,7.
- **Thua rõ** (ghi vào `so-that-bai.md`): 72 h dưới 60% mốc, hoặc dưới 193 view (CK, ngưỡng dừng cũ).

### A. CK, 4 Short bám Long đang lên sóng (ưu tiên 1: hàng chờ trống 13–22/11, cơ chế đã có bằng chứng)

Nguồn: `data/long/<topic>/`. Long công khai trước Short ít nhất 1 ngày để gắn "Video liên quan" (issue #14). Mỗi Long tối đa 1 Short/ngày.

| # | Short (nhãn) | Long, ngày công khai | Hook 3 giây (câu mở + hình mở) | Nguồn số |
|---|---|---|---|---|
| A1 | `ck-s-thue-448-34` (L) | `ck-e5-thue-tncn-2026`, 13/11 | Câu: "Cùng lương hai mươi lăm triệu: năm 2025 nộp bốn trăm bốn mươi tám nghìn thuế, năm 2026 còn ba mươi bốn nghìn." Hình: hai phiếu lương, "2025 · 448.000" và "2026 · 34.000", số đếm giảm từ 448 xuống 34, nền clip tay cầm bảng lương không mặt người | `results.json` `table_k_vnd["25"]["1"]` (1 người phụ thuộc, lương gộp = lương đóng BH): ghi rõ giả định; kiểm lại trong `factcheck.md` trước khi dùng |
| A2 | `ck-s-rut-bhxh-200` (L) | `ck-e6-luong-huu-rut-mot-lan`, 15/11 | Câu: "Hai trăm triệu cầm ngay năm 2027, hay lương hưu bắt đầu năm 2051?" Hình: hai thẻ "2027 · 200 TRIỆU" và "2051 · LƯƠNG HƯU" cạnh nhau, VÍ DỤ GIẢ ĐỊNH (chị Hạnh, lương đóng 10 triệu, 10 năm) | `factcheck.md` của e6. **Không dùng "4,8 triệu lượt rút" làm hook**: factcheck ghi KHÔNG KIỂM ĐƯỢC bản gốc. Không "nên rút" |
| A3 | `ck-s-bhyt-94-40` (S) | `ck-f2-vien-phi-bhyt`, 20/11 | Câu: "Chín mươi bốn phẩy hai chín phần trăm dân số có thẻ bảo hiểm y tế. Vậy mà khoảng bốn mươi phần trăm chi y tế vẫn là tiền túi." Hình: số 94,29% lấp đầy vòng tròn rồi "40%" đập lên chính vị trí đó (cắt khớp, mục 4) | baohiemxahoi.gov.vn trong `factcheck.md` f2 (dòng 7, 16, 19). Hai chỉ số toàn hệ thống, không phải một hoá đơn |
| A4 | `ck-s-100-trieu-dinh-2018` (L) | `ck-i1-100-trieu-tiet-kiem-hay-vnindex`, 19/11 | Câu: "Một trăm triệu mua VN-Index đúng đỉnh chín tháng tư năm 2018. Hai năm sau, còn khoảng năm mươi tư phẩy năm triệu." Hình: "100 TRIỆU → 54,5 TRIỆU" trên đồ thị đường tự vẽ (`chart.js`) | `data/long/ck-i1.../` mục CH00, CH02 (24/03/2020 ≈ 54,52 triệu). Ghi "mô phỏng quá khứ, không dự báo"; không kết luận gì về lợi nhuận tương lai |

Tiêu đề (≤ 60 ký tự, tiếng Việt có dấu, không clickbait sai sự thật; từ khoá tìm kiếm thật in nghiêng):

| # | Phương án 1 | Phương án 2 | Phương án 3 |
|---|---|---|---|
| A1 | Lương 25 triệu: thuế 2025 là 448 nghìn, 2026 còn 34 nghìn (57) | Cùng lương 25 triệu, thuế giảm hơn 13 lần: vì sao? (50) | Lương 25 triệu nộp *thuế TNCN 2026* bao nhiêu? (44) |
| A2 | 200 triệu *rút BHXH một lần* hay lương hưu từ năm 2051? (khoảng 55) | Rút BHXH một lần 200 triệu: nhận ngay hay chờ 2051? (51) | Đóng BHXH 10 năm lương 10 triệu: rút hay chờ hưu? (49) |
| A3 | 94% dân số có thẻ BHYT, nhưng 40% chi y tế là tiền túi (52) | Có thẻ BHYT mà tiền túi vẫn chiếm khoảng 40% chi y tế (khoảng 52) | Vì sao có bảo hiểm y tế mà vẫn tự trả gần nửa? (46) |
| A4 | 100 triệu đúng đỉnh 2018, hai năm sau còn 54,5 triệu (52) | Mua đúng đỉnh 2018: 100 triệu còn 54,5 triệu năm 2020 (53) | 100 triệu mua VN-Index đúng đỉnh 2018: còn bao nhiêu? (53) |

Ghi chú: "13 lần" ở A1 là 448 ÷ 34 ≈ 13,2; chỉ dùng nếu `factcheck` xác nhận. Từ khoá "thuế TNCN 2026", "rút BHXH một lần", "bảo hiểm y tế" là cụm có trong tiêu đề Long và brief; **chưa đo xu hướng tìm kiếm** (ghi "chưa đo", đừng coi là đã kiểm).

Đo riêng cho A: lượt xem Long từ nguồn "Video liên quan"/Shorts trong Studio của Long, 7 ngày sau Short (baseline: bằng 0).

### B. Long CK: `ck-g1-thuong-tet-2027` (ưu tiên 2, có hạn trước 05/12)

- **Điều kiện trước dựng:** chủ kênh duyệt `script.md` (issue #17 W1); kiểm xong 3 mục brief còn hở: văn bản gốc thuế với thưởng, số hiệu nghị quyết giảm trừ gia cảnh, văn bản lịch nghỉ Tết 2027. Chưa đo xu hướng tìm kiếm "thưởng Tết": đo trước khi chọn ngày đăng.
- **Hook 3 s:** câu "Thưởng Tết năm ngoái bình quân tám phẩy sáu chín triệu. Về tay bạn còn bao nhiêu?"; hình: phong bao "20 TRIỆU" đếm xuống "18,4 TRIỆU" (VÍ DỤ GIẢ ĐỊNH, phần thuế ≈ 1,62 triệu, brief). Cặp số đối nghịch cùng một vật, đúng cơ chế mục 1.
- **Tiêu đề:** (1) Thưởng Tết 20 Triệu Về Tay Bao Nhiêu Sau Thuế? (46) · (2) Thưởng Tết 8,69 Triệu: Còn Lại Bao Nhiêu Vào Tháng 3? (53) · (3) Thưởng Tết 2027: Trừ Thuế, Chi Tết, Còn Bao Nhiêu? (50).
- **Đo:** 24 h CTR ≥ 2% và hiển thị ≥ 1.000 (mốc #15); 72 h AVD ≥ 3:00; 7 ngày hiển thị và sub/1.000 view.

### C. Long MIM: một bài, sau khi B xong (ưu tiên 3)

Chọn **M4 `mim-deepfake-lua-dao-2025`** trước M2/M3, vì nhóm AI/lừa đảo là nhóm MIM ưu tiên (60%), và nghiên cứu đã mở nguồn; M5 (Luật AI) tạm hoãn: research chưa mở được cổng chính thức, brief cũng chưa duyệt tên/hook.
- **Điều kiện:** duyệt kịch bản; kiểm vụ Long Biên 28/3/2025 (1,3 tỷ) và số A05 (hơn 4.200 vụ, khoảng 8.000 tỷ) với nguồn sơ cấp.
- **Hook 3 s:** câu "Ngày hai mươi tám tháng ba năm 2025, một phụ nữ ở Long Biên mất hơn một phẩy ba tỷ đồng trong một cuộc gọi video." Hình: điện thoại đặt trên bàn, **không mặt người** (bộ lọc `DENY` clip người, retro 28/10), số đếm lên "1,3 TỶ". Gương mặt giả chỉ dùng ảnh AI theo luật "dáng gốc, quay lưng" hoặc đồ hoạ.
- **Tiêu đề:** (1) Cuộc Gọi Video Giả Mặt: Vụ Mất 1,3 Tỷ Ở Long Biên (49) · (2) 10 Giây Đầu Cuộc Gọi Deepfake: Dấu Hiệu Nào Lộ Ra? (50) · (3) Lừa Đảo Trực Tuyến 2025: 8.000 Tỷ Và Vai Trò Deepfake (53). Phương án (2) hứa "10 giây": chỉ giữ nếu kịch bản có nội dung đó.
- **Short đi kèm (sau Long công khai, chờ kết quả pilot MIM 13–18/11 theo brief):** S "Cuộc gọi video giả: 3 dấu hiệu" (49: "Cuộc gọi video giả: 3 dấu hiệu để nhận ra", chỉ dùng nếu 3 dấu hiệu có nguồn); L "28/3/2025, Long Biên" kể tới lúc chuyển tiền rồi để câu hỏi.
- **Đo:** như B; M2 (Berners-Lee, hook "Vague, but exciting" từ ghi chú của sếp, người có tên + lời trích, đúng cơ chế 1) là bài kế tiếp. Short L đi kèm M2: "Tháng 3/1989, sếp của Tim Berners-Lee đọc đề xuất tạo ra Web và viết ba chữ lên đó." Tiêu đề: “Mơ hồ nhưng thú vị”: ghi chú đầu tiên về Web, 1989 (51) · Web suýt là hàng có phí: chuyện năm 1989 và 1993 (48) · Người Tạo Ra Web Không Đăng Ký Sáng Chế: Vì Sao? (48). Ảnh bản đề xuất CERN: kiểm giấy phép trước; nếu không PD thì dựng bằng cảnh `quote` gõ máy chữ.

## 4. Kỹ thuật dựng áp được vào engine hiện tại

Đã kiểm trong code: Short (`motion/hf/assets/engine/casefile.js` + `beat.js`) **đã có** chuyển cảnh whip/zoom/up/swipe/flash (khoảng dòng 692–699), push-in clip 1,08→1,0 (dòng 674), cửa sổ clip `win` (dòng 673), 14 hiệu ứng chữ `BEAT` gồm `hold` (nền cho khung 0) và `SLAM.zoom`. Long (`casewide.js`) có bảng `TR` (dòng 1116: push, zoom, wipe, iris, blurfade) và Ken Burns ở `photoFramed`. Vì vậy **thiếu hụt không nằm ở hiệu ứng chữ** (ghi tuần 44, mục 4 dòng 8); thêm hiệu ứng chữ mới chỉ nên làm nếu có lý do khác. Các thay đổi nhỏ dưới đây đều **tuỳ chọn, sau khi chủ kênh duyệt, giao Codex** (code), agy (render).

| # | Kỹ thuật (skill) | Áp vào | File / hàm sẽ đổi | Dùng cho | Chi phí |
|---|---|---|---|---|---|
| T1 | **Cặp số đối nghịch trong khung 0** (`hyperframes-creative`: mỗi cảnh một động từ; hook là thông điệp, không phải bố cục) | Thẻ `split` hỗ trợ số lớn thay vì ảnh: `a:{big,label,at}`, `b:{…}`, `sign` | `casefile.js` `B.split` (dòng 433); style trong `casefile.css`; `build.py` kiểm khoá spec | A1, A2, A4, B | vừa |
| T2 | **Đếm kèm phóng cỡ** (`rules/counting-dynamic-scale`) | Số đếm lớn dần trong lúc đếm; hậu tố trượt vào sau khi dừng | `casefile.js` `B.counter` (dòng 182, thêm `grow`, dùng cùng tween với `o`); `casewide.js` `B.counter` (dòng ~358). Giữ `tabular-nums` ở `.count` | A1, A4, B (448→34, 100→54,5, 20→18,4) | nhỏ |
| T3 | **Punch-in khi số lộ** (`hyperframes-keyframes`: punch-in = scale + dịch trên wrapper không có timing, set cho cú cứng) | Thẻ `<video>` nền hiện chỉ có đẩy chậm; thêm `punch:[{at,k}]` (set scale k tại từ neo, hồi 0,3 s) | `casefile.js` khối `if (s.vid)` (dòng 671–685); thêm khoá vào bộ kiểm spec trong `build.py` | A1, A3 (nhấn đúng chữ "34"/"40%") | nhỏ |
| T4 | **Cắt khớp** (`hyperframes-keyframes`: match cut giữ hình học, hướng, vận tốc; không tự tìm khung khớp) | Hai cảnh `counter` liền nhau cùng `top`, cùng cỡ, `fade:0`, chỉ đổi số và màu | **Không cần đổi engine**: chỉ ghi spec (`B.counter` đã có `top`; `show()` nhận `s.fade`). Thêm một ví dụ vào `motion/stier/README.md` | A3 (94,29% → 40%) | gần 0 |
| T5 | **Zoom-out lộ chi tiết** (`blueprints/zoom-out-workspace-reveal`) | Mở sát vào vật (phong bao, điện thoại), lùi ra để lộ số; thay cho đẩy vào mặc định ở cảnh 0 | `casefile.js` dòng 674 (đặt `scale` đầu 1,35 → 1,0 trong 0,8 s khi `s.zoomOut`); tương đương `hero.intro` ở dòng 72 | B, C (cảnh 0 Long cũng dùng `photoFramed.zoom`) | nhỏ |
| T6 | **Từ khoá phát sáng theo mốc từ** (`rules/asr-keyword-glow`) | Chữ nhấn trong phụ đề (`.cw.acc`) sáng + phóng 6–8% đúng lúc đọc rồi hạ về mức nghỉ | `casefile.js` dòng 710–716; `casewide.js` khối phụ đề (~dòng 1135) | mọi Short: không ảnh hưởng nội dung, chỉ làm số hiện rõ khi tắt tiếng | nhỏ |
| T7 | **Clip nhường chỗ cho số** (`blueprints/video-text-pivot`) | Cảnh 0 clip toàn khung → cảnh 1 cùng clip co vào cửa sổ `win:"top"`, số lên dưới | `casefile.js` khối `if (s.win)` (dòng 673) cần nhận trạng thái đầu từ cảnh trước | A2, A3 | vừa; chỉ làm sau khi T1–T6 có số đo |
| T8 | **Whip theo hướng chuyển động** | Thêm `whip` vào bảng `TR` của Long (x ±140 kèm blur 14–18 px, như Short) | `casewide.js` `TR` (dòng 1116) và `pickTr` | B, C (Long) | nhỏ |
| T9 | **Âm thanh / grade** (`media-use`) | Chỉ khi `clip_sheet.py` cho thấy clip Pexels phẳng hoặc lệch màu: một lần chỉnh màu cho cảnh 0; SFX tại cú punch (T3) đã có mốc trong `motion/stier/sfx.py` | `motion/stier/sfx.py` (thêm tick cho `punch`); không thêm LUT riêng | A, B | nhỏ |
| T10 | **Mạch kể và dữ kiện truy nguồn** (`hyperframes-creative/story-spine`, `faceless-explainer`) | Với Long: bảng "Bước lập luận" + "5 câu trước khi viết" đã có; thêm cột "hình thật hay đồ hoạ" trong `script.md` để cổng ảnh A10 bắt sớm | `data/long/<topic>/script.md` mẫu; không đổi code | B, C | gần 0 |

Thứ tự đề xuất: T4 (miễn phí) và T2 → T1 → T3/T6 → các mục còn lại. Mỗi thay đổi cần một Short thử và so khung hình với bản chưa đổi; **không** áp hàng loạt lên Short đang chờ lịch.

Thử nghiệm một biến: để A/B sạch, 4 Short A dùng cùng look, cùng giờ lên sóng (19:00 VN, khung ổn của tuần 44), nên T-kỹ thuật chỉ áp ở **một nửa số bài** (A1, A3: có T2/T3/T4; A2, A4: chỉ cặp số tĩnh). Ghi vào bài nào có kỹ thuật nào trong spec để đọc sau.

## 5. Cổng phải qua (không hạ ngưỡng)

- **Short MIM/CK:** `mix_lint` (`motion/stier/build.py` dòng 384: có cảnh clip, số liệu, sơ đồ; chữ thuần ≤ 35%; không 3 cảnh liền cùng kiểu; cảnh ≤ 11 s), `acc_lint`, `render_preflight` (retro 28/10). Chữ trên nền trống ≤ 22% và không quá 17 s liên tục (`motion/long/floor.py` hằng `MIM_CK_*`). Clip: chạy `motion/long/clip_sheet.py`, xem tờ soát, **không** emblem/ticker/tên công ty (CK) và không mặt người nhận ra được (bộ lọc `DENY` của `clips.py`). Tên ngân hàng/hãng/mã cổ phiếu cấm; không "nên mua/bán"; câu miễn trừ trong mô tả; quét mô tả không còn `CẦN KIỂM`, `<>`, `data`, `long`.
- **Long:** `docs/codex/long-rules.md`: A4 (phần tử thứ hai ≤ 1 s sau mở cảnh), A7 (cảnh 2,5–9 s), A8 (ảnh ≤ 3 lần), A9 (`ledger` giới hạn dòng), A10 (`img_sheet.py` và `clip_sheet.py` xem rồi mới `--ok`), A11 (bảng `factcheck.md` theo chương, `factcheck_lint` sạch), A12 (nhánh chứa `origin/main` trước render thật, `final`, `publish`). Thêm: `studio_lint.py <topic> --strict` 0 lỗi, `script_lines.py` qua integrity, `python scripts/long_gate.py <topic> --min-syl 1900` in ĐẠT, SRT bằng `motion/long/srt.py`, thẻ chương dùng `no`/`k` (không `number`), `hud` đủ, `SAY` và `spec.youtube` điền ngay từ đầu, lỗi cũ đã ghi (câu đệm, một khuôn cảnh cho mọi chương, clip lặp). Ảnh AI: prompt vào `ai_prompts.md`, chủ kênh nhờ bot tạo, người thật chỉ vẽ dáng gốc quay lưng, `"credit": false`.
- **Floor theo kênh:** MIM/CK dùng ngưỡng riêng (≤ 22% chữ nền trống, ≤ 17 s); không dùng ngưỡng CL 20+ phút và không hạ ngưỡng để qua một video.
- **Chủ kênh duyệt trước:** kịch bản Long (một Long mỗi lần); không upload/enqueue/đổi lịch nằm ngoài tài liệu này.

## 6. Việc cần chủ kênh quyết định

1. Có xếp lịch 3–5 Short CK đã render sẵn (mục 2) vào 13–22/11 trước khi render mới không?
2. Có giữ 3 Short C2 trong hàng chờ CK (03–05/11) hay chờ số 72 h? (chỉ nêu, chưa đổi gì.)
3. Duyệt thứ tự Long: CK G1 trước (hạn 05/12), MIM M4 sau; M5 hoãn.
4. Duyệt kỹ thuật T1–T6 (giao Codex sửa code, agy render thử một Short mỗi kỹ thuật).
5. Có chấp nhận khung giờ MIM 06:30 VN là biến cần kiểm (mục 1 của tài liệu thắng/thua), chưa đổi?

## 7. Giới hạn của nháp này

Chưa kiểm xu hướng tìm kiếm cho bất kỳ từ khoá nào; chưa xem khung hình thật của các Short tuần 44; số tuần 44 thiếu CTR/giữ chân; hook mới là giả thuyết. Ba hook có số (A1, A4, B) lấy từ `results.json`/brief, cần đối chiếu `factcheck.md` trước khi viết spec.
