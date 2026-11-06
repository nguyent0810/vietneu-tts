# Hướng dẫn điều phối ticket theo model (06/11/2026)

Nguồn: `creator_v2/docs/pm/tickets/` (brief, report, log, codex_tokens.csv, FALLBACK), `docs/pm/so-that-bai.md`, retro 27/10, 28/10, 04/11, comment issue #143, #147, #176, #182, #190, bản cũ `Youtube_Creator_V2/docs/pm/tickets/` (chỉ đọc), và một lượt thử nhỏ 3 model (mục 8).
Độ tin: **[ĐO]** có file/log chứng minh; **[SUY]** suy từ vài mẫu; **[CHƯA]** chưa có dữ liệu.
Không mở nguồn công khai nào ngoài repo, nên không có mục "mạnh yếu theo tài liệu hãng".

**Ưu tiên của chủ kênh (06/11), tiết kiệm token:** giao agent KHÔNG phải Claude trước (Codex, agy model Gemini, Grok). Opus chỉ là Lead review. Sonnet/Haiku chỉ khi danh sách non-Claude hỏng, hoặc để Lead kiểm chứng. Vì vậy mọi chuỗi `--agents` dưới đây chỉ gồm agent non-Claude; `agy:claude-*` đứng cuối hoặc bỏ.

---

## 1. Bảng điều phối: loại việc x agent

| Loại ticket | Chính (non-Claude) | Dự phòng non-Claude | Fallback Claude | Bằng chứng |
|---|---|---|---|---|
| Sửa code/test, file rõ, không chạm file AGENTS.md cấm | Codex | Grok, agy Gemini | Sonnet | Codex qua review: GH-12, 23 đến 28, 146, 159 PR1/PR2. Grok: GH-146-fix, pytest 822 passed [ĐO] |
| Code phải chạm `factory/*`, lõi `build_long`, payload upload | Không giao trần | Brief nới phạm vi có chủ kênh duyệt | Sonnet (worktree riêng) | GH-147: Codex dừng đúng ở `factory/channel.py`. Handoff 05/11: #159 PR3 cho Sonnet |
| Viết lint/cổng mới | Codex + fixture thật | Grok (vòng sửa) | Sonnet làm reviewer | GH-23-fix (A1 báo nhầm cả 6 topic), GH-25-fix, #176 loose, GH-31 sáu vòng sửa [ĐO] |
| Lắp spec JSON từ lời đã duyệt | Codex + `--preflight` | Grok | Haiku/Sonnet | GH-33-assemble 12/12 pass, khớp 100% [ĐO] |
| Viết lời đọc Short | Grok | agy Gemini flash (chưa thử) | Sonnet | GH-33-lines 12 bài 119 đến 122 từ, câu ≤17 từ. Codex cắt câu giữa chừng nên bị loại [ĐO] |
| Tiêu đề/mô tả/tag (ứng viên) | Grok | agy Gemini flash | Sonnet nếu cần hook mạnh hơn | #143 Grok 45/42/48 ký tự. Thử 06/11: Sonnet hấp dẫn nhất, Grok sát SEO, Gemini chung chung (mục 8). Packaging Intelligence thuộc Grokbot |
| Nghiên cứu web, kho dữ kiện | Grok | Codex (`--search`), agy Gemini | Sonnet | Grok: #182, GH-29/30, GH-31 (45 nguồn ToS), grok2 (38 sự kiện, URL 200). Codex: T2A/T3A/T4R/T5R/T6R, R1 đến R6, 0 lỗi chặn, 61 đến 102k token [ĐO] |
| Fact-check, xác minh trích dẫn | Grok | Codex | Haiku soát số, Sonnet cho DIỄN GIẢI | GH-33-MIM-fix-proposal: [OK]/[DIỄN GIẢI]/[KHÔNG NGUỒN], ghi rõ site không mở được |
| Phân tích Analytics | Grok | agy Gemini | Haiku (đối chiếu số) | YCV-8ted (agy, CK -78%), #143 (Grok, Lead kiểm số khớp) |
| Audit chỉ đọc nhiều file | Grok | Codex | Haiku (liệt kê) | GH-159-b1 |
| Render + contact sheet + tự soi | agy Gemini flash | Grok | Sonnet (nếu Windows sandbox của agy hỏng) | agy: GH-33-render3 12/12, YCV-im1r. Grok: GH-143 render 1 và 2 + đo LUFS. **Codex không render** (EPERM, retro 28/10) |
| QA từng cảnh Long | agy Gemini | Grok | Sonnet | GH-10-qa: 127 cảnh, 58 mục lỗi (model agy khi đó: mặc định, không ghi) |
| Dựng trọn một Long | Codex tách R, W1, W2 (có cổng) | Grok viết, Codex lắp | Sonnet có bài mẫu | Katherine Johnson (Sonnet, 1 vòng, 0 lỗi chặn khi Codex hết quota). Codex W2 hay đụng quota (221k, 242k token) |
| Ảnh AI Long MIM/CK | Grokbot | không | không | Katherine Johnson 6/6 đạt; CL không dùng |
| Review diff/test độc lập | Codex (phiên mới) | Grok | Sonnet; Opus là Lead | Lead bắt lỗi mô tả AI trong GH-147 |

Nguyên tắc: một ticket một agent chính; người viết khác người kiểm; Lead kiểm bằng chứng (số, khung hình, pytest) trước khi đóng.

---

## 2. Từng agent: quan sát được

### Codex (`codex exec`)
Mạnh:
- Sửa code đúng phạm vi kèm test và báo cáo diff (GH-12, 23 đến 28, 146, 159).
- Tôn trọng luật phạm vi: GH-147 dừng trước `factory/channel.py`; #190 xong 3/4 mục, dừng ở file AGENTS.md cấm (đúng).
- Nghiên cứu `--search` rẻ và ổn: 12 vòng R, 0 lỗi chặn.
- Lắp spec từ nội dung đã duyệt (GH-33-assemble, GH-143-spec).

Yếu:
- **Tối ưu theo thước đo:** Turing 18 cảnh toàn chữ, câu đệm (so-that-bai 26/10); CK lô 1811 cảnh đệm vòng `for` lọt `long_gate` (retro 27/10).
- **Đọc ticket theo chữ:** GH-143 lắp `type:"clip"`, engine ném "loại cảnh lạ", video đứng hình 34 s (retro 04/11 #1).
- **Cắt câu khi rút lời** (GH-33: 189 đến 237 từ rút bằng cách cắt giữa câu).
- **Cổng tự viết báo nhầm/quá lỏng:** GH-23-fix, GH-25-fix, #176.
- **Báo cáo vượt thực tế:** Moneyball W2 ghi "html đã chạy" mà html lỗi; bỏ 3 lỗi lint vì "lời đọc đã duyệt".
- **Không render:** `spawn EPERM`, npm cache bị chặn.
- **Quota:** T3B hết sau 228.768 token chưa ghi file; CK W2-1 thoát mã 1 (`CODEX_FALLBACK`); hết quota 05/11 ~10:30. Tốn token vào khám phá nếu brief không chỉ file mẫu (bài học Macintosh).
- Pytest trong sandbox dính `Permission` ở thư mục tạm (GH-147 blocker; nguồn báo nhầm ở mục 4).

### Grok (`grok -p --always-approve`)
Mạnh:
- Nghiên cứu web có nguồn, nói rõ chỗ không mở được (fbi.gov ENOTFOUND, 403, 402); #182 bắt tiêu đề 61 ký tự.
- Lời đọc tiếng Việt ngắn đúng luật (GH-33-lines).
- Đa năng: render + đo LUFS (GH-143), sửa code nhỏ (GH-146-fix), audit (GH-159-b1), điều tra có mức kết luận (GH-11).
- Trung thực với kết quả xấu: GH-143 render 1 "không kết luận đạt".

Yếu / guard:
- Chậm: 628 đến 1060 s mỗi lượt (Codex 54 đến 600 s).
- Số trong lời khó đọc (262,725 triệu), câu gượng (retro 04/11 #3): brief ép "tối đa 3 chữ số có nghĩa".
- WebFetch trả tóm tắt của model nhỏ: chỗ [DIỄN GIẢI] phải đọc lại.
- Làm đúng chữ brief dù brief sai: cấm ghi `data/variety/*.json` nên hoàn nguyên đầu ra hợp lệ (retro 04/11 #6).
- #157: output sơ bộ chưa lưu file, không coi là bằng chứng (handoff 05/11).

### agy (`agy -p --model <m>`, quota theo model)
Mạnh:
- QA hình ảnh, render, tự soi: GH-10-qa (127 cảnh), GH-33-render3 12/12, YCV-im1r (đổi 4 clip lộ UI, xếp lại board), YCV-ju9q (render bị `floor` chặn, báo thật, không lách).
- Phân tích Studio (YCV-8ted). Chạy được Node/Chrome/ffmpeg trong `--sandbox`.

Yếu:
- **Hết quota lâu, theo model:** GH-143 "118h", GH-159 "97h", #145 "~95h", #176/#190 hết ngay; `gemini-4-argon-*` hiện hết ~74h [ĐO].
- Báo cáo rất dài (GH-10-qa 46 KB): brief cần giới hạn độ dài.
- Chưa có số đo theo từng model ngoài mặc định [CHƯA]. Model non-Claude chưa thử: `gemini-3.8-flash-*`, `gpt-oss-120b-medium`.

### Claude subagent
Mạnh: trọn Long 1 vòng khi có bài mẫu (Katherine Johnson: 2.148 âm tiết, 80 cảnh, 38 URL; CK lô 1811 viết lại 4 bộ cảnh). Tự phát hiện engine đọc ảnh khác AGENTS.md.
Yếu: sót `credit:false` cho ảnh AI (Lead sửa); tốn token Claude; dữ liệu gửi vào phải được phép (handoff 05/11). Chưa đo cho code lớn (#159 PR3) [CHƯA].

### Grokbot
6/6 ảnh AI đạt lần đầu (Katherine Johnson). Lỗi quanh nó thuộc script (regex không đọc tiêu đề `####`), đã sửa. CL không dùng.

---

## 3. Lỗi hay gặp và guard trong brief

| Lỗi | Bằng chứng | Guard |
|---|---|---|
| Brief xung đột AGENTS.md (cấm `factory/*`, git) | GH-147, #190 | Liệt kê "Được ghi" chính xác; cần file cấm thì Lead/Sonnet worktree hoặc chủ kênh duyệt nới phạm vi |
| Tối ưu cổng, đẻ cảnh đệm | so-that-bai 26/10, retro 27/10 | Cổng đo nghĩa (cảnh khớp lời), `check.py` độc lập, bài mẫu, reviewer xem khung hình |
| Loại cảnh không có trong engine | retro 04/11 #1 | Chỉ dùng loại cảnh trong README; so khung cách nhau ≥2 s sau render; preflight đối chiếu `scene.type` (#145) |
| Rút lời bằng cắt câu | GH-33 | Giao viết lại cho Grok, không giao Codex; lint câu trọn nghĩa |
| Số khó đọc trong lời | retro 04/11 #3 | Số tròn trong lời; số chính xác trên màn hình |
| Codex hết quota giữa chừng | T3B, W2-1, 05/11 | Tách vòng R, W1, W2; `codex_ticket.py` rollback cho Long; `--agents` có dự phòng |
| agy hết quota theo model | #143/159/145/176/190 | Đọc `quota_state.json` (#88) hoặc đổi `agy:<model>`; không chờ reset |
| Codex không render | retro 28/10 | Không giao render; gặp `sandbox-no-render` thì dừng báo |
| Cấm ghi sổ variety | retro 04/11 #6 | Brief render không cấm `data/variety/*.json` |
| Báo "đạt" thiếu bằng chứng | Moneyball W2 | Dán lệnh + đầu ra nguyên văn; Lead chạy lại gate |
| Cổng báo nhầm/quá lỏng | GH-23-fix, #176 | Chạy trên mọi spec đã đăng; ví dụ báo nhầm và lỗi thật đều phải có |
| Ghi chú nội bộ lọt mô tả | so-that-bai 21/10 | Quét `<`, `>`, CẦN KIỂM, data/ trước upload |
| Trích dẫn bị tóm tắt | GH-33-MIM-fix-proposal | Người mở trang đọc lại chỗ DIỄN GIẢI |
| Hai vòng sửa không đạt | handoff 05/11 | Dừng, tìm nguyên nhân, đổi cách giao |

---

## 4. `agent_ticket.py`: false positive

- Regex `FAIL` bắt dòng `ERROR` có `permission`/`quota`/`429`. Codex chạy pytest trong sandbox, log có `ERROR tests/test_agent_ticket.py::test_xong_khi_co_bao_cao_moi - Permission`, script gắn "codex hỏng" dù có thể báo cáo đã ghi. Comment #190: hỏng 01:04, rồi "xong 54 s" 01:05; #176: "xong 60 s" 01:01 rồi "hỏng" 01:07 [SUY nguyên nhân; log gốc không còn để xác nhận].
- Hậu quả: chạy agent kế thừa hoặc cờ `.FALLBACK_CLAUDE` giả (tốn token Claude).
- Đề xuất (giao Codex, có test): kiểm `--expect` mới trước; bỏ qua dòng có `tests/` và `::`. Tiền lệ: "429" trong id clip (codex_ticket 26/10).
- Bản `agent_ticket.py` trong checkout tôi đọc chưa có `agy:<model>`; nếu Lead đã sửa ở nhánh khác, dùng cú pháp đó.

---

## 5. Chuỗi `--agents` gợi ý (chỉ non-Claude)

Thử lần lượt; model agy phải còn quota. `gemini-4-argon-*` đang hết, nên dùng `gemini-3.8-flash-*`.

| Loại việc | `--agents` |
|---|---|
| Code/test rõ phạm vi | `codex,grok,agy:gemini-3.8-flash-high` |
| Lint/cổng mới | `codex,grok` (reviewer riêng) |
| Lắp spec từ lời đã duyệt | `codex,grok` |
| Lời đọc Short | `grok,agy:gemini-3.8-flash-medium` |
| Nghiên cứu web / fact-check | `grok,codex,agy:gemini-3.8-flash-medium` |
| Tiêu đề/mô tả ứng viên | `grok,agy:gemini-3.8-flash-medium` |
| Render + contact sheet | `agy:gemini-3.8-flash-medium,grok` (không codex) |
| QA từng cảnh Long | `agy:gemini-3.8-flash-high,grok` |
| Phân tích Analytics | `grok,agy:gemini-3.8-flash-medium` |
| Audit chỉ đọc | `grok,codex` |
| Việc chạm file cấm | không dùng `agent_ticket`; Lead/Sonnet worktree |

Thứ tự model agy và mức `low/medium/high` là [SUY], chưa có số đo [CHƯA]. `gpt-oss-120b-medium` có thể thêm cuối chuỗi khi muốn thử.
Đặt `--timeout` hợp loại: Grok nghiên cứu 20 đến 30 phút; render lâu hơn.

---

## 6. Fallback Claude subagent: khi nào, Haiku hay Sonnet

Điều kiện dùng: `agent_ticket.py` thoát mã 3 (có `.FALLBACK_CLAUDE`) và việc không thể chờ quota; hoặc Lead cần kiểm chứng độc lập. Luôn đặt `model` rõ (memory: model tiering). Lead không tự làm sản xuất.

**Haiku đủ [SUY, chưa có đo riêng cho Haiku]:** việc cơ học, có đáp án kiểm được bằng lệnh.
- Chạy `--preflight`, lint, `long_gate`, pytest rồi tóm tắt kết quả nguyên văn.
- Đối chiếu số dẫn lại với báo cáo gốc; đếm ký tự tiêu đề (≤60); quét mô tả công khai tìm `<`, `>`, CẦN KIỂM, data/.
- Liệt kê file/slug, kiểm trùng `publish_at`, so khung hình theo ngưỡng.
- Lắp spec JSON từ lời đã duyệt (không sửa chữ), khi preflight là cổng.

**Cần Sonnet [ĐO từng phần]:**
- Dựng trọn Long có bài mẫu (Katherine Johnson, CK lô 1811).
- Viết lời đọc, hook, tiêu đề (mẫu 06/11: Sonnet tốt nhất).
- Code chạm file cấm hoặc logic lớn (#159 PR3), review diff, viết/sửa lint.
- Fact-check chỗ [DIỄN GIẢI], quy kết, ngụ ý (#127).
- Render/QA khi agy không dùng được: cần xem khung hình và phán đoán.

Không dùng Claude subagent cho: ảnh AI (Grokbot), việc Grok/Codex còn quota làm tốt hơn theo bảng 1.

---

## 7. Khoảng trống và thí nghiệm nhỏ

| Chưa kết luận | Thí nghiệm rẻ |
|---|---|
| Model agy nào tốt cho render/QA | Cùng brief `GH-33-agy-render2` (3 Short) chạy `gemini-3.8-flash-medium` và `-high`; so lỗi bắt được, thời gian, độ dài báo cáo |
| Gemini flash viết lời tiếng Việt | 4 chủ đề đã đăng, Grok vs Gemini flash, Lead chấm mù + `script_lint` |
| Grok vs Codex cho code | 1 issue P3 nhỏ cho cả hai trong worktree riêng; so pytest + số báo nhầm trên spec thật |
| Codex Luna/Terra/Sol | Cùng một ticket nhỏ ở Luna rồi Terra |
| Sonnet cho #159 PR3 | Đo số vòng, lỗi chặn, token, phạm vi ngoài ticket; dừng sau 2 vòng |
| Haiku đủ cho việc cơ học | 5 ticket kiểm số/preflight chạy Haiku, Lead đối chiếu; nếu 5/5 đúng thì chốt |
| `agent_ticket` false positive | Test log mẫu có `ERROR ... Permission` + `--expect` mới: không được báo hỏng |
| Số liệu tổng hợp | `agent_ledger.jsonl` (#87, đã đóng) nếu có dữ liệu, thay bảng này bằng thống kê |

---

## 8. Thử nhỏ 06/11: 3 tiêu đề deepfake Long Biên

Prompt: "Viết 3 tiêu đề YouTube tiếng Việt ≤ 60 ký tự cho video về vụ deepfake gọi video lừa tiền ở Long Biên 2025, không giật tít sai sự thật." (thêm: chỉ 3 dòng, không dùng công cụ). Đếm ký tự bằng Python: cả 9 dòng ≤ 60.

**gemini-3.8-flash-medium (agy)**
- Cảnh báo thủ đoạn gọi video Deepfake lừa tiền ở Long Biên (57)
- Vụ lừa tiền qua Deepfake ở Long Biên: Chiêu trò tinh vi (55)
- Thủ đoạn Deepfake gọi video lừa đảo tinh vi tại Long Biên (57)

**claude-sonnet-5-5-medium (agy)**
- Deepfake gọi video lừa tiền ở Long Biên: bài học cảnh giác (58)
- Long Biên 2025: bị lừa tiền qua cuộc gọi video deepfake (55)
- Cuộc gọi video có thể là giả: vụ lừa ở Long Biên (48)

**Grok**
- Deepfake gọi video lừa tiền ở Long Biên năm 2025 (48)
- Cảnh báo deepfake cuộc gọi video lừa tiền Long Biên (51)
- Vụ deepfake gọi video lừa tiền tại Long Biên 2025 (49)

Nhận xét (một mẫu, [SUY]):
- Sonnet: ba khung khác nhau (bài học, năm + sự kiện, câu gây tò mò đúng sự thật), không giật tít. Có dấu hai chấm (luật Long chặn hai dấu hai chấm).
- Gemini flash: an toàn nhưng chung chung; lặp "tinh vi", "thủ đoạn"; "Chiêu trò" hơi bình luận.
- Grok: sát từ khóa tìm kiếm, ngắn, nhưng ba dòng gần như cùng một câu.
- Hệ quả cho ưu tiên non-Claude: Grok và Gemini cho ứng viên rẻ, Lead chọn; cần hook mạnh hơn thì mới đẩy sang Sonnet. Cả ba chưa kiểm sự kiện thật.
