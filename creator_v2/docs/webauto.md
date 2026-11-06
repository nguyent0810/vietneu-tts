# webauto: lệnh tự động hoá trình duyệt dùng lại được

`python -m webauto <công cụ> <lệnh>` chạy lại **một chuỗi bước cố định** trên các trang không có API (Google Flow, ChatGPT, Muse AI, TikTok Studio). Không có LLM trong vòng lặp: script mở trang, điền, bấm, chờ, tải về, lưu file. Nhờ đó tốn 0 token cho phần thao tác, và hợp luật README ("Pha sản xuất không được phép cần LLM").

```
python -m webauto --help
python -m webauto flow generate --mode video --prompts-file clips.txt --duration 6 --out output/webauto/flow
python -m webauto chatgpt images --prompts-file images.txt --out output/webauto/chatgpt
python -m webauto chatgpt ask --file docs/pm/some-retro.md          # review, lưu <file>.chatgpt-review.md
python -m webauto muse research --questions q.txt --out docs/research/2026-10-28-muse.md
python -m webauto tiktok list
```

## Cài đặt

```
pip install -e ".[webauto]"        # playwright, mcp, pillow, opencv-python-headless
python -m playwright install chrome   # chỉ khi máy chưa có Chrome
```

| Công cụ | Chạy bằng | Cần gì |
|---|---|---|
| `flow` | Playwright, profile riêng `~/.webauto/profiles/flow` | `webauto flow login` một lần (đăng nhập Google, rồi **đóng hẳn** cửa sổ Chrome). Chrome còn chạy nền sẽ khoá profile. |
| `chatgpt`, `muse`, `tiktok` | [Browsentic](https://browsentic.com) điều khiển Chrome thật đã đăng nhập | Extension Browsentic đã ghép cặp; Chrome mở, cửa sổ ở phía trước; tab đã đăng nhập sẵn trang đích. |

## Đăng nhập

Các trang đều cần tài khoản đã đăng nhập. webauto **không bao giờ tự nhập mật khẩu, không giải captcha và không né bước kiểm tra "bạn là người"** (Cloudflare của ChatGPT, xác minh 2 bước của Google...). Việc đó là của chủ tài khoản.

- Ngay sau khi mở trang, mỗi công cụ kiểm tra đã đăng nhập chưa (Flow: nút "Dự án mới" và không bị chuyển sang `accounts.google.com`; ChatGPT: không còn nút "Log in / Sign up" và không có bước "Verify you are human"; Muse: có ô chat; TikTok Studio và YouTube Studio: không bị chuyển sang trang đăng nhập).
- Nếu chưa đăng nhập, lệnh **in hướng dẫn, giữ nguyên cửa sổ Chrome, chờ bạn tự đăng nhập hoặc tự xử lý bước xác minh rồi tự chạy tiếp**. Thời gian chờ đặt bằng cờ toàn cục `--wait-login SECONDS` (mặc định 120, đặt trước tên công cụ: `python -m webauto --wait-login 300 chatgpt images ...`). `--wait-login 0` thì báo lỗi ngay kèm hướng dẫn, phù hợp khi chạy không người trông.
- `flow` dùng profile Chrome riêng của webauto: chạy `python -m webauto flow login` một lần (hoặc để `flow generate` tự chờ bạn đăng nhập trong cửa sổ nó mở). Các công cụ còn lại dùng Chrome thật của bạn qua Browsentic, nên chỉ cần đã đăng nhập sẵn trong Chrome đó.
- Phiên đăng nhập hết hạn giữa chừng (ví dụ ChatGPT đòi đăng nhập lại) được xử lý ở lần mở trang kế tiếp theo cùng cách trên.

Đổi chỗ lưu profile bằng biến `WEBAUTO_HOME`. Đổi lệnh chạy Browsentic bằng `WEBAUTO_BROWSENTIC_CMD` (mặc định `npx -y browsentic@latest mcp`). Profile chứa cookie đăng nhập nên **nằm ngoài repo**, không bao giờ commit.

## Lệnh

### `flow generate`
Tạo ảnh hoặc video trong một dự án Flow mới, tải về `<tên>_<n>_...`.
- `--mode image|video` (mặc định image). Mặc định model: Nano Banana Pro (ảnh), Omni 1.1 Flash (video). `--model` nhận một đoạn tên model: `--model "Omni 1.2"` chọn Omni 1.2 Flash, `--model "Omni 1.1"` chọn Omni 1.1 Flash. Danh sách model video ngày 06/11/2026: Omni 1.2 Flash, Omni 1.1 Flash, Veo 3.1 - Lite, Veo 3.1 - Fast, Veo 3.1 - Quality. Lệnh chọn model **trước** rồi mới chọn tỉ lệ, độ phân giải, độ dài, vì các nút này đổi theo model: Omni 1.2 Flash không có nút độ dài (lệnh in "model has no 8s option" và để model tự quyết), Omni 1.1 Flash có 4/6/8/10s. Dòng `settings:` in kèm số credit Flow báo ("Generating will use N credits"). Video "failed to generate" thì lệnh dừng ngay thay vì chờ hết `--timeout`.
- `--count 1-4` số kết quả mỗi prompt (mặc định 1), `--duration 4|6|8|10` giây (video, mặc định 6), `--ratio`, `--res`, `--quality 720p|1080p|4K` (chất lượng tải; 720p là bản gốc).
- `--image khung_dau.png` (video): ảnh làm **khung bắt đầu** (image-to-video). Một ảnh dùng cho mọi prompt trong lần chạy.
- `--headless`: chạy không mở cửa sổ Chrome (đã thử 28/10/2026 trên macOS: 1 ảnh Nano Banana Pro 16:9 trong 35 giây, Flow không chặn). Profile phải đã đăng nhập: chạy ẩn thì không chờ đăng nhập mà báo lỗi ngay, khi đó chạy `flow login` rồi thử lại. Profile vẫn bị khoá nếu còn cửa sổ Flow khác đang mở.
- `--session FILE` (hoặc biến `WEBAUTO_FLOW_SESSION`): dùng phiên đăng nhập đã xuất ra file thay cho profile, dành cho máy chủ không có cửa sổ để đăng nhập. Tạo file trên máy đã đăng nhập bằng `python -m webauto flow export-session --out <file>`; file được ghi quyền chỉ-chủ (600). **File này đăng nhập được Google thay bạn**: không commit, không gửi ai, chép sang máy chủ bằng `scp` rồi `chmod 600`. Phiên hết hạn thì xuất lại.
- Linux: không có Google Chrome cho ARM, nên trên Linux `flow` dùng Chromium của Playwright (`python -m playwright install chromium`). Đã thử 28/10/2026 trên Oracle Ubuntu 24.04 aarch64: `flow generate --headless --session ...` ra 1 ảnh Nano Banana Pro 16:9 trong 36 giây; phiên trên Mac vẫn đăng nhập sau khi xuất.
- `--image-size 1K|2K` (ảnh): cỡ tải về. `1K` là bản gốc 1376×768 (dọc 768×1376), lấy thẳng `src` của ô ảnh (trùng từng byte với menu Download > 1K), chạy ẩn được. `2K` đi qua menu của ô ảnh > Download > "2K Upscaled": Flow phóng lên 2752×1536 rồi tự tải về, mất thêm khoảng 15 giây mỗi ảnh và **không tốn credit** (đo 06/11/2026: 390 credit trước và sau 4 lần tải 2K). **2K cần cửa sổ Chrome**: chạy `--headless` thì Flow báo "Upscaling failed!" (bước reCAPTCHA của Flow), nên mặc định là `2K` khi có cửa sổ và `1K` khi `--headless`; `--image-size 2K --headless` dừng ngay kèm hướng dẫn. 4K có trong menu nhưng bị khoá ("Upgrade", cần gói cao hơn) nên lệnh không nhận. File 2K có đuôi `_2K`, ví dụ `rice_1_5af1a83b_2K.jpg`. Chạy lô: `python -m webauto flow generate --mode image --ratio 16:9 --prompts-file prompts.txt --out <thư mục> --keep-raw` (mỗi lần chạy một tỉ lệ; 9:16 thì chạy lần nữa với `--ratio 9:16`). Đo 06/11: khoảng 50 giây cho một lần chạy một ảnh 2K (mở dự án ~10 giây, tạo ảnh ~22 giây, phóng 2K ~15 giây).
- `--strip-mark {crop,fill,off}` (mặc định `crop`). Gỡ dấu ✦ Gemini ở góc phải dưới. Ảnh vừa tải từ Flow luôn có dấu ở một chỗ cố định tính bằng **pixel theo cạnh dài**, không theo từng chiều (đo lại 06/11/2026 bằng so khớp mẫu trên cùng một ảnh ở 1K và 2K, cả 16:9 lẫn 9:16):
  - 1K (cạnh dài 1376): tâm cách mép phải 97 px, mép dưới 98 px, cạnh dấu khoảng 55 px, **cả ảnh ngang lẫn ảnh dọc**. Cỡ khác dưới 2000 px thì nhân theo cạnh dài / 1376. (Trước 06/11 công thức tính theo từng chiều nên với ảnh dọc 768×1376 hộp nằm sai chỗ; dấu vẫn mất chỉ vì cắt dư phần đáy.)
  - 2K (cạnh dài 2752): Flow **đóng dấu mới sau khi phóng**, không phải dấu 1K phóng ×2: cạnh dấu vẫn khoảng 55 px, tâm cách mép phải 113 px, mép dưới 114 px.
  
  `crop` lấy hộp đó cộng lề an toàn 8 px (theo tỉ lệ ở 1K) mỗi phía, rồi giữ khung lớn nhất tính từ góc trái trên, **kết thúc bên trái hộp hoặc phía trên hộp** (chỉ cần một trong hai; chỉ áp cho 4 cỡ đã đo: 1376×768, 768×1376, 2752×1536, 1536×2752, sai số ±2 px). Cỡ hoặc tỉ lệ chưa đo (1:1, 4:3, 3:4, ảnh lạ) thì cắt **cả** mép phải **lẫn** mép dưới, và hộp là hợp của hộp tỉ lệ với hộp 1K đo bằng pixel (97/98 px), vì chưa biết dấu nằm đâu ở cỡ đó; giữ tỉ lệ khung gốc (sai số ≤ 1 px), **kể cả khi không dò thấy dấu**. Nếu dò thấy hộp lớn hơn thì cắt theo hợp của hai hộp. Kích thước sau khi cắt: 1K ngang 1376×768 → 1242×693, 1K dọc → 693×1242, 2K ngang 2752×1536 → **2602×1452**, 2K dọc → **1452×2602** (trước 06/11: 1K ngang còn 1136×634, 1K dọc 659×1180). Video giữ nguyên luật cũ: hộp `fixed_mark_box` (tính theo từng chiều) và cắt **cả** mép phải **lẫn** mép dưới, rồi phóng lại về cỡ gốc. Lý do: video tải 1080p (đo 06/11) có dấu đóng mới, tâm cách mép phải và mép dưới khoảng 180 px, rộng khoảng 70 px, **nằm ngoài** hộp cố định; chỉ nhờ cắt hai mép (1920×1080 → 1586×892) mà dấu mất. `--strip-mark delogo` ở 1080p vì vậy vá sai chỗ, dùng `crop`. `fill` giữ nguyên kích thước và vá bằng inpaint, nhưng chỉ khi dò thấy dấu; không thấy thì in cảnh báo và không sửa file. `off` để nguyên dấu.
- `--keep-raw`: khi file thực sự đổi, giữ bản vừa tải thành `<tên>_raw.jpg`. `crop` trên ảnh Flow luôn đổi file nên luôn có bản `_raw`. `fill` không thấy dấu thì không tạo file phụ và không ghi đè.
- Giới hạn: `fill` có thể để vệt nhòe (lối gạch, cạnh nến, nếp lụa). Dấu đè lên mép gỗ hoặc dốc xám–trắng thì `find_mark` thấy; dấu vắt qua khung tranh tối và tường kem thì vẫn không thấy — `crop` vẫn cắt được nhờ hộp cố định, `fill` thì bỏ qua và cảnh báo. `crop` bỏ hẳn mép phải hoặc mép dưới (và một phần mép kia để giữ tỉ lệ). Gọi cắt lần hai trên ảnh đã cắt sẽ cắt tiếp một góc (dấu không còn ở chỗ cũ); `flow generate` chỉ cắt một lần, ngay sau khi tải. `strip_mark` không gắn cờ ảnh Flow thì giữ hành vi cũ: không thấy dấu thì không sửa. Cần `pillow` và `opencv-python-headless` (có trong extra `webauto`); thiếu thì lệnh dừng và không ghi đè.
- File prompt: mỗi dòng `tên | prompt` hoặc chỉ `prompt` (đặt tên `001_<tóm-tắt>`), dòng `#` và dòng trống bị bỏ.
- Flow có thể tính credit (xem dòng "Generating will use N credits" trong popup cài đặt). Video tốn đáng kể: Omni 1.1 Flash 8s x2 báo 24 credit; ảnh Nano Banana 2.1 báo 0 credit; ảnh Nano Banana Pro (mặc định) cũng miễn phí, còn video Omni Flash 8s tốn 10 credit mỗi video (chủ tài khoản xác nhận 28/10/2026). Đo 06/11/2026 (đếm credit trong menu tài khoản trước/sau): Omni 1.2 Flash x1 báo và trừ **24 credit** mỗi clip (text-to-video lẫn image-to-video, dài 7,93 s, 24 fps), Omni 1.1 Flash 8s x1 báo 12, Veo 3.1 - Fast báo 20; tải video 1080p (phóng từ bản gốc 720p) **không** trừ thêm; clip "failed to generate" không trừ. Tải ảnh 2K không trừ. Một clip Omni 1.2 mất khoảng 2 phút từ lúc mở dự án tới file 1080p đã cắt dấu.

### `chatgpt images`
Mỗi prompt tạo một ảnh bằng ChatGPT (gửi "Create an image: …"), lưu `<tên>.png`. File đã có thì bỏ qua, nên chạy lại sau khi gián đoạn không tạo trùng. Cần quy tắc Browsentic `file-download` = Allow. `--wait`, `--gap`, `--limit`.

### `chatgpt ask`
Gửi `--prompt`, hoặc nhờ review một `--file` (kèm `--instruction`, mặc định là yêu cầu review phản biện tiếng Việt), rồi **lưu câu trả lời thành markdown cho agent đọc**. `--from-chat URL` chỉ đọc lại một cuộc trò chuyện đã có (không gửi gì), dùng khi lần chạy trước bị ngắt.

### `muse research`
Hỏi Muse AI (muse.ai) một danh sách câu hỏi trong **một side chat mới**, chờ từng câu trả lời xong và gom tất cả vào một file markdown. Câu trả lời lấy bằng nút "…" > Copy rồi đọc clipboard Windows (đọc văn bản trang không đủ tin cậy với câu trả lời dài). `--adopt-first` dùng tab/side chat đang mở nếu câu 1 đã gửi tay.

### `tiktok list | create | update | delete`
Thao tác trên kênh **đang chạy thật**, nên có chốt (xem CLAUDE.md: không đăng, không xoá khi chủ kênh chưa nói rõ):
- `create`: mặc định **riêng tư** ("Only you"), không bao giờ đặt lịch. Đăng friends/công khai cần `--allow-public`. Mô tả luôn có tiền tố `--marker` (mặc định `TEST-CRUD`).
- `delete`: cần `--id`; từ chối nếu bài không phải "Only me" (trừ `--allow-public`) hoặc nếu không có **đúng một** dòng khớp id. TikTok giữ bài đã xoá 30 ngày (Activity center > Recently deleted).
- `update`: **chưa kiểm chứng** (xem dưới).

### `studio collect` / `studio summarize`
Gom **mọi số liệu của YouTube Studio** về file, để LLM đọc bản tổng hợp thay vì tự mở Studio (tốn token). Chỉ đọc, không đổi gì trên Studio.

```
python -m webauto studio collect                       # kênh Studio đang mở, mọi báo cáo, 5 kỳ
python -m webauto studio channels                      # các kênh của mọi tài khoản Google đã đăng nhập trong Chrome
python -m webauto studio collect --channel all         # lần lượt từng kênh, mỗi kênh một thư mục
python -m webauto studio collect --channel "biểu đồ" --periods 28d,lifetime --reports videos,daily,traffic_source
python -m webauto studio summarize --dir output/webauto/studio/<kênh>/<ngày>   # gộp lại thư mục đã thu
```

Chọn kênh: `--channel` nhận `all`, một phần tên kênh, mã `UC...` hoặc số `authuser`. Script mở `studio.youtube.com/?authuser=0,1,2...` (mỗi số là một tài khoản Google đã đăng nhập trong Chrome, như trong nút chuyển tài khoản của Studio), đọc mã và tên kênh, dừng khi số tiếp theo quay về kênh đã gặp; mọi URL xuất số liệu đều gắn `authuser` của kênh đó, nên không cần bấm chuyển tài khoản. Không có `--channel` thì lấy kênh Studio đang mở như trước. Mỗi tài khoản Google mới thấy kênh đầu tiên mà Studio mở cho nó.

Cách làm: với mỗi (báo cáo, kỳ) script mở URL **Chế độ nâng cao** của Studio (URL tham số hoá đầy đủ: kênh, kỳ, chỉ số, chiều), bấm "Xuất chế độ xem hiện tại" > `.csv`, giải nén. Dùng cái này thay vì Analytics API (`factory/analytics.py`) vì Studio có số mà API không trả (lượt hiển thị, CTR hình thu nhỏ, bảng theo từng video, các chiều khán giả), và một lần xuất là đủ mọi dòng.

- **Báo cáo** (`--reports`): `videos` (bảng từng video, 7 chỉ số), `daily` (theo ngày), `traffic_source`, `geography`, `content_type`, `playlist`, `city`, `age`, `gender`, `new_vs_returning`, `subscription_status`, `subscription_source`, `youtube_product`, `device`, `operating_system`. `videos` thu cho cả 5 kỳ (`7d,28d,90d,365d,lifetime`), `daily` cho 4 kỳ, các chiều còn lại cho `28d` và `lifetime`.
- **Đầu ra** trong `<out>/<kênh>/<ngày>/`: `raw/<báo-cáo>__<kỳ>/{table,chart,totals}.csv` (CSV gốc của Studio), `manifest.json` (báo cáo nào lấy được, báo cáo nào không và vì sao), và bản tổng hợp:
  - `summary.md`: **file để đưa cho LLM** (gọn, khoảng 15 KB cho kênh ~140 video và 14 chiều, so với hơn 200 KB CSV gốc): tổng kênh theo kỳ, phân bố lượt xem, short vs long, lượt xem theo tuổi video, xu hướng theo ngày, top/bottom video theo views, CTR, giữ chân, sub/1k views, các bảng theo chiều.
  - `summary.json`: toàn bộ số. `videos.csv`: một dòng mỗi video, đủ chỉ số mọi kỳ, cho công cụ khác.
- **Mã Studio** cho kỳ/chiều không có tài liệu. Đã xác nhận: kỳ `week`, `4_weeks`, `quarter`, `year`, `lifetime`; chiều `VIDEO`, `DAY`, `TRAFFIC_SOURCE_TYPE`. Các chiều khác script thử lần lượt từ danh sách ứng viên (mã sai thì trang trắng, nút xuất không hiện) và lưu mã chạy được vào `~/.webauto/studio_catalog.json`. `--refresh-catalog` để dò lại. Báo cáo nào không lấy được vẫn được ghi trong `summary.md` mục "Không lấy được".
- **Traffic source** thử riêng bộ chỉ số Views + Thumbnail impressions + CTR trước bộ đầy đủ và cache; nếu Studio xuất các cột này thì summary giữ lại chúng. Nếu lần xuất không trả các cột, chúng sẽ vắng mặt trong summary.
- **City / lifetime** có thể không tải được file dù báo cáo khác của cùng chiều chạy được. Khi hai lần bấm xuất không tạo file, lỗi được ghi trong `manifest.json` và mục "Không lấy được"; hiện không có HTML/DOM lưu để xác định nguyên nhân sâu hơn.
- **Giới hạn 500 dòng**: Studio chỉ xuất 500 video đứng đầu mỗi bảng (dòng chú thích "Showing top 500 results"). Khi bị cắt, `summary.md` có cảnh báo; dòng "tổng kênh" vẫn đủ nhưng xếp hạng và phân bố chỉ trên 500 video đó.
- "Short" trong tổng hợp là quy ước của script (video dài tối đa 180 giây), không phải nhãn của YouTube.
- Cần quy tắc Browsentic `file-download` = Allow. Mỗi lần xuất mở một tab mới và dùng cú bấm thật: Chrome chỉ cho một lần tải tự động mỗi thao tác người dùng và âm thầm từ chối các lần sau ("Nothing downloaded").

## Đã kiểm chứng và chưa kiểm chứng

| | Trạng thái |
|---|---|
| `flow generate` ảnh, video, image-to-video | Đã chạy thật. |
| `chatgpt images`, `chatgpt ask` (kể cả `--from-chat`) | Đã chạy thật. |
| `muse research` | Chạy thật ở chế độ `--adopt-first`. Luồng tự mở side chat mới **chưa** kiểm chứng đủ. |
| `tiktok list`, `tiktok delete` | Đã chạy thật (xoá một bài test Only me). |
| `tiktok create` | Các bước đã chạy tay (tạo bài test Only me); chưa chạy bằng lệnh này. |
| `tiktok update` | Chưa thành công: text gõ vào được nhưng caption trên máy chủ không đổi. TikTok chỉ cho sửa caption một lần mỗi ngày mỗi bài, nên lần Save đầu có thể đã dùng hết lượt. |
| `studio collect` / `summarize` | Đã chạy thật trên một kênh: 35/35 báo cáo (14 chiều, 5 kỳ) lấy được, tổng hợp ra `summary.md` ~14 KB từ hơn 200 KB CSV. Mã kỳ/chiều đọc từ bộ chọn của Studio. Mới thử trên một kênh, một ngôn ngữ giao diện (tiếng Việt; CSV luôn tiêu đề tiếng Anh). |
| Xử lý đăng nhập (`--wait-login`) | Test logic đạt; đường **đã đăng nhập** chạy tốt trên cả 5 công cụ. Đường **chưa đăng nhập** chưa thử trên trang thật (dấu hiệu nhận biết dựa trên giao diện đã thấy, có thể cần chỉnh khi trang đổi). |

## Bài học (đừng lặp lại)

- **ChatGPT chặn Chrome do script mở** bằng Cloudflare "verify you are human", tick xong vẫn hiện lại. Không né. Dùng Chrome thật qua Browsentic.
- **Browsentic từ chối thay người duyệt.** Hành động bị chặn (gửi form bằng phím Enter, tải file, đính file) từ client MCP bị từ chối cho tới khi chủ máy đặt quy tắc sang Allow trong Browsentic > Guardrails. Gửi tin bằng cách **bấm nút**, không nhấn Enter.
- **Danh sách chat/bảng chỉ vẽ phần gần khung nhìn.** Cắt câu trả lời theo vị trí câu hỏi trong văn bản trang sẽ hỏng khi câu trả lời dài. Dùng Copy + clipboard, hoặc so sánh nội dung ổn định theo thời gian.
- **Browsentic che chuỗi số dài** trong kết quả (`⟦card:…⟧`): đường dẫn file tải về và vài id video bị che. Lấy "file mới nhất trong thư mục tải", đừng tin `savedTo`; nhận diện bài TikTok bằng id chưa bị che hoặc tiêu đề.
- **Trình soạn thảo caption của TikTok bỏ qua `fillInput`**: giá trị quay về mặc định khi đăng. Phải gõ bằng phím thật (`typeText`).
- **Ảnh chụp màn hình có thể chậm một nhịp** hoặc không phản ánh vùng cuộn bên trong; kiểm tra trạng thái bằng DOM/văn bản trước khi bấm việc không hoàn tác được.
- **Bấm theo toạ độ vào khung menu** có thể trúng mục giữa (Download); bấm đúng mục, hoặc dùng selector của mục.
- **Flow: thông báo góc phải trên ("Your image has been downloaded!") che nút Account/Settings**, làm cú bấm sau chờ hết giờ. Sau mỗi lần tải qua menu phải bấm "Dismiss" và Escape hết lớp phủ (`close_overlays`). Nút "More options" đầu tiên trên trang là của bộ sưu tập, không phải của ô ảnh: luôn tìm nút trong đúng ô (`flow-grid-tile-container` chứa `img[data-media-id]`).
- **Flow 2K chạy ẩn thì hỏng** ("Upscaling failed!"), không cố lách bước kiểm tra đó: dùng cửa sổ, hoặc tải 1K.
- Mỗi lần chạy `flow generate` tạo một **dự án Flow mới** và mỗi video tốn credit; dọn dự án thừa trong Flow.

## Thêm một công cụ mới

1. Tạo `webauto/<ten>.py` với hàm `add_parser(sub)` (đặt `set_defaults(func=...)` cho từng lệnh) và đưa vào `TOOLS` trong `webauto/cli.py`.
2. Import `mcp`/`playwright` **bên trong hàm** để `--help` chạy được trên máy chưa cài.
3. Dùng `webauto.browsentic.browser()` cho Chrome thật, `webauto.common` cho đọc file prompt và ghi markdown (`write_md` luôn gắn ghi chú "chưa kiểm chứng").
4. Hành động không hoàn tác được (đăng, xoá, thanh toán) phải có chốt mặc định an toàn và một cờ `--allow-…` rõ ràng; tách điều kiện chốt thành hàm thuần để viết test (`tests/test_webauto.py`).
