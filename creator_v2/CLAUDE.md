# creator_v2 (yt-factory)

Xưởng dựng video YouTube cho kênh CL ("Into The Killer's Mind"), MIM (Mind in the Machine) và CK (Biểu Đồ Biết Nói). Chủ kênh đọc tiếng Việt.

Code này chuyển từ repo `Youtube_Creator_V2` sang ngày 03/11/2026 (issue #100). Mọi đường dẫn trong file này tính từ thư mục `creator_v2/`: chạy lệnh từ đây.

## Luật không được phá

- **Cải thiện là thêm vào hệ thống đang chạy tốt, không thay nó.** Sáu Long đã đăng (yakuza, mafia, shanghai, ripper, kowloon, golden) là chuẩn. Trước khi đổi cách làm, dựng thử một chương và so với chương tương ứng của `golden`.
- **Không đăng, không đặt lịch, không gỡ lịch, không xóa video khi chủ kênh chưa nói rõ.** Luôn upload private kèm `publishAt`. Video đã đăng thì để yên. Chỉ Lead (Claude điều phối) được upload, và chỉ khi chủ kênh ra lệnh; agent sản xuất không bao giờ upload (`AGENTS.md`).
- **Mỗi lần chỉ làm một Long**, và chỉ sau khi chủ kênh duyệt kế hoạch. Kịch bản do Lead duyệt (chủ kênh 11/11/2026: "OK đổi để nhanh hơn"). Không dựng hàng loạt: YouTube coi nội dung sản xuất hàng loạt theo khuôn là spam (`motion/long/RESEARCH-million-views.md`).
- Chỉ dùng tư liệu tự do (`motion/long/SOURCES.md`). Không clip phim, không bịa lời trích THẬT (thoại phỏng dựng có nhãn cho nhân vật lịch sử đã mất được phép từ 16/11, storytelling-guide §14 mục 7).
- **Ảnh AI phỏng tác nhân vật rõ mặt được phép từ 17/11/2026** (chủ kênh: "cho phép phỏng tác hình ảnh nhân vật rõ mặt dựa theo tư liệu để làm cho video sinh động, nghệ thuật hơn, bỏ rule không rõ mặt người"). Làm theo storytelling-guide **§15**: mặt và cảnh dựa trên tư liệu có nguồn, phong cách tranh rõ ràng, nhãn PHỎNG DỰNG trên hình, khai nội dung tổng hợp khi đăng. Người còn sống vẫn không có ảnh AI rõ mặt. Ảnh/clip AI minh họa chung (tag `minh_hoa_chung`, kho `library/tools/assets.py`, #198) dùng như cũ.
- Không in bí mật (token, khóa API) ra màn hình hay vào file.

## Quy trình một Long (đủ cả 8 bước, không bước nào tự bỏ)

1. **Chọn đề tài**: viết `data/long/<topic>/plan.md` (vì sao đề tài này, cold open, các vòng lặp mở). Trước khi gửi plan cho chủ kênh, chạy `python scripts/plan_sources.py <topic> --write`; plan chỉ do model mạnh viết (không giao Gemini Flash), số ảnh đếm bằng API Commons (#291). Chờ chủ kênh duyệt.
2. **Tư liệu trước, chữ sau**: `motion/long/research_long.py` và `media_search.py` → `output/long/<topic>/research.json`, soi contact sheet. Không đủ khoảng 50 ảnh tự do thì đổi đề tài.
3. **Kịch bản** `script.md`: độ dài theo câu chuyện, không cố định số phút hay số chương (chủ kênh 18/11/2026: "độ dài dài ngắn phụ thuộc vào nội dung câu chuyện, không cần cố định"; Vidocq ~43 phút được duyệt). Chỉ còn sàn tối thiểu của `floor.py`. Viết theo `docs/pm/storytelling-guide.md` **§14** (chủ kênh 15–16/11/2026, đè lên §13): trục là nhân vật + cái giá, không phải nguồn; người kể (Sonnet hoặc agy Gemini) được phóng tác điện ảnh; người soát (model còn lại) **chỉ** sửa chỗ nói tới tư liệu (tên, năm, số, chức danh, ai làm gì, lời trích) và không bịa lời/cảm xúc người còn sống — không cắt chất kể. Codex không viết/không soát lời tiếng Việt. **Lead duyệt** sau bước đó; không chờ chủ kênh (từ 11/11/2026). Chủ kênh vẫn xem bản dựng ở bước 8.
   - **Cơ chế văn xuôi (#476, chủ kênh 17/11/2026):** người kể (agy Gemini) viết văn xuôi tự do `prose.md` (mẫu giọng + dossier + số phút mỗi chương, không lint), độ dài theo câu chuyện. `python scripts/prose_to_script.py prose.md script.md` chỉ tách ở cuối câu, không đổi chữ ([PD]…[/PD] → `{pd}`); TTS đọc nguyên câu (bản A). Không giới hạn độ dài câu, cả trong brief lẫn trong code: số chữ trong brief làm người viết ép câu cụt. Viết và đọc thử CH00–CH01 trước (`python scripts/tts_sample.py <topic> script.md CH00 CH01` → `output/long/<topic>/tts_test/`), chủ kênh nghe duyệt rồi mới viết các chương còn lại.
4. **Cảnh viết tay** trong `gen_scenes.py` (+ `gen_scenes2.py`), theo mẫu `data/long/golden/`: mỗi câu gắn với ảnh, bản đồ, hồ sơ, biểu đồ, sketch hoặc b-roll. `scenes_from.py` chỉ cho ra bộ khung nháp (`"auto": true`), không phải cảnh.
5. **Giọng**: `build_long.py <topic> takes 3` → `stt_takes.py` → `pick` → `tts`.
6. **`html`**, rồi `render chNN --draft` vài chương để soi, rồi `render`, rồi `final`.
7. **QA bằng mắt** trên contact sheet từng chương. Sửa, render lại chương hỏng.
8. **Báo chủ kênh**, đề xuất lịch. Họ đồng ý thì ghi `"approved": "<ngày> — <lời duyệt>"` vào spec rồi mới chạy `publish_long.py`.

## Các cổng tự động (đừng tắt, đừng lách)

- `motion/long/floor.py`: sàn sản xuất. Từ chối `render`, `final`, `publish` khi kịch bản dưới 5.000 âm tiết, dưới 40 ảnh, dưới 30 cảnh b-roll, dưới 14 loại cảnh, kinetic trên 38% / chữ nền trống trên 12% cho Long legacy, hoặc còn cảnh `auto`. Ngưỡng lấy từ sáu Long đã đăng. **Bị chặn nghĩa là video chưa đạt, không phải cổng sai**: bổ sung tư liệu và kịch bản, đừng hạ ngưỡng.
- **Ngân sách chữ & lặp ảnh (076):** Long mới theo `_legacy_topics.json` (#275) dùng `tools/visual_mix.py`: chữ >12% giây cảnh báo, >15% lỗi; `spec.text_budget_reason` hạ lỗi chữ thành cảnh báo. Kinetic/slam/quote/question là thẻ chữ toàn màn hình kể cả có ảnh/clip nền; date/counter chỉ tính khi nền trống. Chữ khoá overlay trên cảnh ảnh/clip, thẻ chương, bảng tra và đồ hoạ dữ liệu không tính. Ảnh tĩnh >4 lượt cảnh báo, >6 lỗi, crop/camera/layout không đổi danh tính; style #258 tách danh tính. <4 file ảnh khác nhau/phút chỉ cảnh báo. Long cũ/Short chỉ in số của cổng mới; bước `html` in bảng phân bố, ghi rõ khi ước thời lượng. Không đổi cổng 120s đầu.
- Thiếu hình: tham khảo 8 bậc **clip có phép/PD → AI phỏng tác (§15) → ảnh pano/camera/parallax → đồ hoạ dữ liệu → map/timeline/org → vật thể tư liệu → style #258 → minh hoạ chung**; kiểm kê tư liệu trước khi viết cảnh. Xem `docs/pm/storytelling-guide.md`, mục Ngân sách chữ & lặp ảnh.
- `motion/variety.py audit`: nhạc nền và look phải khác ba video gần nhất.
- `motion/long/lint_html.py`, `craft.py`: lỗi con dấu, tiêu đề thẻ, clip HDR.

## Sự cố 11/10/2026 (lý do có file này)

Một phiên được nhờ "cải thiện" đã dựng bốn Long (escobar, capone, bulger, namcam) trong 100 phút: bỏ bước tư liệu, kịch bản 1.300–2.100 âm tiết (7–11 phút), 94% cảnh là bốn từ đầu câu trên nền đen, rồi đặt lịch public cả bốn. Chủ kênh phải gỡ lịch và làm lại. Tự động hóa việc viết cảnh là mục tiêu đúng, nhưng đầu ra phải qua được `floor.py` và mắt chủ kênh trước khi thành video.

## Quản lý việc: GitHub Issues (từ 29/10/2026)

GitHub Issues của `nguyent0810/vietneu-tts` là nơi quản lý việc duy nhất (chủ kênh quyết định 29/10; từ 03/11 dùng chung repo này). Không dựng hệ thống song song. Issue cũ của V2 được chuyển dần sang đây (#100 bước 6).
- **Repo PUBLIC:** issue và comment không được chứa khóa, token, đường dẫn credentials hay ghi chú nội bộ nhạy cảm.
- **Mọi lệnh `gh` luôn kèm `--repo nguyent0810/vietneu-tts`**: `gh` mặc định trỏ repo upstream (25/10 từng tạo nhầm issue ở đó).
- **Đầu phiên:** `gh issue list --repo nguyent0810/vietneu-tts`.
- **Việc kéo dài hơn một phiên hoặc có mốc ngày:** `gh issue create --repo nguyent0810/vietneu-tts --title "[P<0-4>] …" --body-file …`. Ghi mục tiêu, các bước dạng checklist và tiêu chí đạt.
- **Tiến độ:** `gh issue comment <số> --repo nguyent0810/vietneu-tts`. Xong việc: `gh issue close <số> --repo nguyent0810/vietneu-tts`.

## Điều phối agent (từ 28/10/2026)

Claude điều phối, review và duyệt. Các agent CLI trên máy làm việc theo issue: Codex (`codex exec`), agy (`agy -p`), Grok (`grok -p`). Với Long, Codex sửa cảnh, agy QA và render, Claude review rồi duyệt (chủ kênh, 29/10).

- **Giao việc:**
  1. Viết brief `docs/pm/tickets/GH-<số>-<agent>.md`, ghi rõ phạm vi, file được ghi và file báo cáo.
  2. Chạy `python scripts/agent_ticket.py GH-<số> --brief <brief> --expect <báo cáo> --agents codex,agy,grok`. Script tự comment tiến độ vào issue.
- **Fallback:** agent hết quota, lỗi hoặc không ghi báo cáo thì script tự chuyển agent kế tiếp. Hỏng cả danh sách thì có cờ `docs/pm/tickets/<id>.FALLBACK_CLAUDE` và thoát mã 3; khi đó Claude giao cho subagent của mình. Long vẫn dùng `scripts/codex_ticket.py`, script này có snapshot và rollback.
- **Thứ tự ưu tiên (chủ kênh 06/11):** giao agent ngoài họ Claude trước (Codex, agy với model Gemini, Grok). Opus chỉ điều phối và review; subagent Sonnet/Haiku chỉ khi danh sách đó hỏng hoặc cần kiểm chéo. Chọn agent theo loại việc ở `docs/pm/model-routing.md`. Quota agy tính theo từng model: dùng `--agents …,agy:<model>`.
- **Máy C: không dùng** (chủ kênh 12/11/2026: "Bỏ agy trên máy C khỏi list agent"). Agy trên máy C hay mất đăng nhập qua SSH. Việc chỉ đọc (review, viết lời, soát sự thật) giao agy Gemini trên máy này, hết hạn mức thì subagent Sonnet.
- **Chọn agent:** code, spec và test giao Codex. Codex **không render** (chủ kênh chọn 28/10): sandbox Windows của Codex chặn npm cache và `spawn` (Node 22, Chrome, ffmpeg), nên render và các lệnh `npx hyperframes` giao agy hoặc Grok. Phân tích giao agy hoặc Grok. agy chạy không người trông bằng `--sandbox --dangerously-skip-permissions` (chủ kênh cho phép 28/10, AI Learning cũng dùng vậy), nên brief phải ghi rõ file nào được ghi.
- **Tự sinh issue:** đọc báo cáo của agent, thấy việc cần làm thì Claude tạo issue mới, gắn label `auto` và ghi issue nguồn trong mô tả.
  - Được tự giao: phân tích, sửa code hoặc công cụ, viết spec, dựng nháp.
  - Phải chờ chủ kênh duyệt: đăng, đặt lịch, gỡ hay thay video đã đăng, đổi kế hoạch nội dung, mọi thứ ra ngoài.
- **Agent không bao giờ:** đăng, enqueue, commit, đổi lịch, hoặc thấy `YT_CREDS_DIR`.
- **Quyền tự duyệt:** agy chạy với `--sandbox --dangerously-skip-permissions`, Grok chạy với `--always-approve`. Chủ kênh cho phép cả hai từ 28/10.
- **Chốt chặn** (theo review ChatGPT 28/10, `docs/pm/2026-10-28-huong-lam-mim-ck.chatgpt-review.md`):
  - tối đa 5 issue label `auto` đang mở; vượt thì gộp hoặc chờ;
  - mỗi brief có input, output, tiêu chí đạt và file báo cáo cố định;
  - agent không tự xác nhận "đạt": Claude kiểm số hoặc khung hình bằng chứng trước khi đóng issue;
  - việc đổi trạng thái đăng (upload, lịch, thay video) không bao giờ đi qua fallback tự động.
