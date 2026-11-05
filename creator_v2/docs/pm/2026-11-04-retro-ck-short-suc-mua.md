# Retro CK Short `ck-them-10-trieu-gio-bot-mot-mon` (GH-143), 04/11/2026

Đã đăng: https://youtu.be/OIkDM-qgNu4, private, hẹn 07/11/2026 12:00 VN ("Lãi 10 triệu một năm, sao vẫn hụt 2,7 triệu sức mua?"). Video đã đăng để yên; retro này chỉ sửa quy trình. Nguồn đối chiếu: retro 28/10 (`2026-10-28-retro-ck-pilot-short.md`), retro 03/11 (`2026-11-03-retro-ck-shorts-pilot.md`), báo cáo GH-143, spec, `state.sqlite` (chỉ đọc), `data/variety/*.json`.

## Bảng sự cố

| # | Sự cố | Nguyên nhân gốc | Biện pháp phòng | Trạng thái | LẶP? |
|---|---|---|---|---|---|
| 1 | Hai cảnh `"type":"clip"`: preflight OK, render mã 0, video đứng hình 34 s | Spec dùng loại cảnh không có trong engine (`casefile.js` ném "loại cảnh lạ"). `build.py` chỉ gắn footage khi cảnh có `clip: pexels:<id>`, và `mix_lint` chỉ đếm `vid`/`clip` không rỗng, không kiểm loại cảnh hợp lệ. Ticket mô tả cảnh là "clip" nên Codex lắp đúng chữ ticket. Không có kiểm sau render xem hình có đổi | (a) Luật: không có type `clip`, cảnh footage = kinetic + `clip` (README, AGENTS). (b) Báo cáo render phải so khung cách nhau ≥ 2 s. (c) Code: preflight đối chiếu `scene.type` với bảng loại cảnh của `casefile.js`; build thất bại khi trang có lỗi JS; phát hiện đứng hình (so khung ở vài mốc, chênh pixel ≈ 0 thì lỗi) | (a)(b) đã làm; (c) đề xuất, thuộc #145 | Một phần: 28/10 P3 đã chỉ ra contact sheet làm tay là cổng duy nhất, đề xuất bật `check_gate` cho CK/MIM, chưa làm |
| 2 | `script_lint.py` lỗi import `factory.console` | Chạy trực tiếp mà repo root không có trong `sys.path` | Dùng `PYTHONPATH=.` cho tới khi sửa; lỗi import không phải lý do bỏ lint (AGENTS). Code: `motion/stier/script_lint.py` ~dòng 183, thêm repo root vào `sys.path` như các CLI khác | Luật đã ghi; sửa code thuộc #144 | Không |
| 3 | Grok viết số lẻ đọc khó (262,725 triệu, 2.725.000 đồng), câu 8 gượng | Brief yêu cầu số "chính xác" mà không tách lời đọc khỏi chữ trên màn hình; không có lint số lẻ cho Short CK; không có bước đọc to câu cuối | Luật "lời đọc số tròn, số chính xác chỉ trên màn hình" (AGENTS đã có "viết cho tai", nay nhắc lại ở mục lắp spec). Mẫu brief Grok phải ghi: mỗi số trong lời tối đa 3 chữ số có nghĩa. Code đề xuất: `script_lint.py` cảnh báo số ≥ 4 chữ số có nghĩa hoặc dạng `x.xxx.xxx` trong `lines` | Luật đã làm; lint đề xuất | Họ lỗi lặp: 28/10 P7 và 03/11 C3 (số trong lời lệch/khó kiểm), chưa có lint. Không phải lỗi y hệt |
| 4 | Slot 04/11 19:00 lỡ, dời 07/11 12:00 | Bắt đầu sản xuất ~14:00 cho slot 19:00 cùng ngày; 2 vòng render (vòng 1 hỏng do #1) + QA + chờ duyệt kéo tới 20:16; `upload_one.py:93` chặn giờ hẹn < 30 phút | Luật lead time: slot cùng ngày cần xong QA và duyệt trước giờ hẹn ≥ 3 giờ, không thì dời slot từ đầu (README mục "Lịch và thời gian dựng"). Code đề xuất: `build.py --preflight --slot <giờ>` cảnh báo khi `now + 3h` > slot | Luật đã làm; cảnh báo code đề xuất | Không. Vòng render thừa gốc từ #1 |
| 5 | 05/11 12:00 và 19:00 VN mỗi giờ có 2 Short CK hẹn trùng | Không công cụ nào kiểm trùng `publish_at` cùng kênh. `enqueue_ck.py`/`upload_one.py` chỉ kiểm giờ quá khứ (< 30 phút). Các bản thay (`-v2`, `-r2`) giữ giờ của bản gốc nhưng sổ không có trạng thái "đã thay" | Luật: liệt kê `publish_at` cùng kênh trước khi chọn giờ (README). Code: chặn trong `motion/stier/upload_one.py` (quanh dòng 91–93) và `enqueue_ck.py`/`enqueue_mim.py`: từ chối khi đã có item cùng kênh, `stage != failed`, cùng `publish_at`, trừ khi truyền `--replaces <slug>`; thêm stage hoặc cột `replaced_by` trong `factory/store.py` | Luật đã làm; code là issue mới (mục đề xuất) | **LẶP**: 28/10 P8(c) đã đề xuất bộ cảnh báo hai item cùng kênh cùng `publish_at`, chưa làm. Đọc sổ chỉ-đọc 04/11: còn trùng 05/11 05:00Z (`ck-e2-bang-tra-quy-khan-cap` + `ck-dien-giam-44-dong-20-nam-v2`) và 05/11 12:00Z (`ck-c2-ban-lo-van-nop-thue` + `ck-ho-kinh-doanh-giam-30-thue`). 03/11 cũng trùng 2 cặp (đã qua). 08/11 và 09/11 là cặp gốc + `-r2` cùng giờ (gốc vẫn `published`: đúng P8 chưa xử lý) |
| 6 | Build sửa `short_looks.json` và `ck_music.json` | `build.py` ghi sổ đa dạng theo thiết kế (look + chữ ký cảnh, nhạc). Brief Grok cấm ghi các sổ nên Grok hoàn nguyên | Kiểm: `short_looks.json` ĐÚNG, mục cuối là CK, slug này, look `blueprint`, sig `T M D G D G D M T` khớp 9 cảnh trong spec. `ck_music.json` KHÔNG có slug này (đã hoàn nguyên), nên `variety.py audit` cho các video sau không thấy nhạc `no_frills_salsa.mp3` của nó (bài này đã dùng ở `ck-3-trieu-mua-duoc-bao-nhieu`, `ck-barber-odean-su-chu-y`, `ck-b4-thang-muoi-ba`). Phòng: brief agent render không được cấm ghi `data/variety/*.json`, vì đó là đầu ra hợp lệ của build (AGENTS) | Luật đã ghi; bổ sung sổ chờ Lead | Không |
| 7 | Hai nhãn "VÍ DỤ GIẢ ĐỊNH" (cảnh 260 triệu, khoản thiếu) hơi nhỏ | Luật chỉ yêu cầu có nhãn, không có ngưỡng nhìn thấy, chỉ soi bằng mắt khi QA | Luật: nhãn phải đọc rõ ở khung rộng 360 px, nhỏ hơn dòng phụ cùng cảnh thì tăng cỡ (AGENTS). Code đề xuất: lint nhãn giả định có cỡ ≥ dòng phụ, hoặc engine tự đặt cỡ cố định cho nhãn này | Luật đã làm; code đề xuất | **LẶP** một phần: 28/10 mục 1 đã hỏi chủ kênh chốt luật nhãn (chỉ lần đầu hay mọi cảnh), chưa có kết luận bằng văn bản; nay vấn đề là độ nổi của nhãn |

## Lỗi LẶP (lỗi quy trình)

1. **Trùng `publish_at` cùng kênh (sự cố 5):** đề xuất P8(c) 28/10 chưa thành code, 03/11 lại trùng, nay vẫn còn 2 cặp trùng. Lần thứ ba, nên đặt P1.
2. **Kiểm bằng mắt là cổng duy nhất (sự cố 1):** `check_gate` cho CK/MIM (28/10 P3) chưa bật; lỗi nặng nhất (video đứng hình) qua preflight và chỉ lộ nhờ tờ khung.
3. **Luật nhãn "VÍ DỤ GIẢ ĐỊNH" (sự cố 7):** câu hỏi 28/10 chưa có kết luận.
4. **Số trong lời không kiểm bằng code (sự cố 3):** cùng họ với 03/11 C3 và 28/10 P7.

## File đã sửa

- `AGENTS.md`: thêm mục "Lắp spec Short (rút từ retro 04/11/2026, GH-143)" (không có type `clip`, loại cảnh chỉ lấy từ bảng README, so khung sau render, `PYTHONPATH=.` cho script_lint, số tròn trong lời, nhãn giả định đọc rõ, không hoàn nguyên sổ variety).
- `motion/stier/README.md`: đoạn "Cảnh có footage" và mục "Lịch và thời gian dựng một Short (luật Lead)": lead time ≥ 3 giờ, không dùng giờ đã có item cùng kênh.
- `docs/pm/2026-11-04-retro-ck-short-suc-mua.md`: file này.

Không sửa code, `state.sqlite`, lịch, sổ variety. Không upload, không commit.

## Đề xuất code (để Lead giao Codex)

1. **#145 (đã có)**, bổ sung phạm vi: `motion/stier/build.py` `preflight()` (~dòng 684) kiểm `scene.type` thuộc tập loại cảnh của `casefile.js`; đọc console trang khi render và thoát khác 0 nếu có lỗi JS; phát hiện đứng hình sau render (lấy khung mỗi ~3 s, chênh pixel quá nhỏ thì lỗi).
2. **#144 (đã có)**, bổ sung: `motion/stier/script_lint.py` ~dòng 183 thêm repo root vào `sys.path`; kèm cảnh báo số ≥ 4 chữ số có nghĩa trong `lines`.
3. **Issue mới đề xuất:** `[P1] Chặn hai item cùng kênh trùng publish_at (enqueue + upload) và thêm stage "replaced"`. File: `motion/stier/upload_one.py` (~dòng 91–93), `enqueue_ck.py`, `enqueue_mim.py`, `factory/store.py` (`STAGES`/cột `replaced_by`). Đạt khi: test chặn trùng giờ, cho phép với `--replaces <slug>`, bản gốc chuyển `replaced`, báo cáo lịch cảnh báo trùng.
4. **Issue mới đề xuất (nhỏ):** `[P2] Preflight Short cảnh báo lead time slot (--slot) và nhãn giả định quá nhỏ`. File: `motion/stier/build.py` `preflight()`.
5. **Việc Lead/chủ kênh (không làm trong retro này):** sửa lịch hai giờ trùng 05/11 (chờ chủ kênh); thêm `{"slug": "ck-them-10-trieu-gio-bot-mot-mon", "file": "no_frills_salsa.mp3"}` vào `data/variety/ck_music.json`; chủ kênh chốt luật nhãn giả định (mọi cảnh hay chỉ lần đầu).
