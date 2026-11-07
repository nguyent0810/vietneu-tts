# Handoff: Lead PM của MIM / CK / CL (phiên MimCk), 05/11/2026, bản chiều

## Cập nhật bàn giao mới nhất: sau khi kết nối lại

- Phiên trước có sandbox chỉ đọc và mạng bị chặn; GitHub đọc được khi cấp quyền riêng. Môi trường vừa báo unrestricted và mạng được bật; phiên kế tiếp cần kiểm tra quyền thực tế, không dựa vào cấu hình cũ.
- GitHub kiểm tra lại: #159, #145, #144, #157, #169 còn mở. Main local tại 63b60fc489d3d6176c585cf1c57e431a792ffe53. Cần kiểm lại GitHub và việc đang chạy trước khi giao tiếp.
- #145: đã tạo worktree `_merge/wt-145-short-preflight`, nhánh `lead/145-short-preflight`, từ 63b60fc; brief `creator_v2/docs/pm/tickets/GH-145-agy-brief.md` chưa được Git theo dõi. Agy được gọi nhưng trả `Individual quota reached`, reset sau khoảng 94h59m tại thời điểm thử. Không có thay đổi code; không giao lại Agy cho đến khi kiểm quota. Lead quyết định cách tiếp theo theo nguyên tắc model và owner của chủ kênh.
- #159 PR 3: đã tạo worktree sạch `_merge/wt-159-pr3`, nhánh `lead/159-pr3-make-video`, từ 63b60fc. Chưa viết brief, chưa khởi chạy Claude Sonnet, chưa sửa code. Kiểm phạm vi dữ liệu được phép đưa vào tài khoản công ty trước khi giao; không gửi toàn repo, log hoặc nội dung riêng.
- #157: đã khởi chạy Grok ở chế độ plan, yêu cầu chỉ đọc bằng chứng GitHub công khai và không sửa gì. Lượt đó còn chạy khi bàn giao; output sơ bộ nói PR #158 có thể xử lý hai lỗi, nhưng chưa có kết luận hoặc review độc lập. Không coi nhận định sơ bộ là bằng chứng đã kiểm. Kết quả chưa được lưu vào file; kiểm tra tiến trình/phiên Grok hoặc thực hiện lại kiểm chứng nếu cần, tránh chạy trùng khi nó còn hoạt động.
- #144 và #169 chưa giao, chưa sửa. Grokbot giữ Packaging Intelligence, không chạy nghiên cứu trùng. Quota các agent khác chưa biết. Sản xuất tiếp tục tạm dừng; merge và mở lại sản xuất theo các quyết định đã ghi trong handoff.
- Chủ kênh yêu cầu mở lại phiên: đọc handoff này, kiểm trạng thái thực tế rồi tiếp tục điều phối; báo rõ owner, bằng chứng, blocker và quota đã biết.

## Kiểm tra kết nối lại ngày 05/11

- GitHub CLI đã kết nối và đọc được issue, PR. #159, #169, #145, #144 và #157 còn mở; chưa có PR mở cho PR 3 của #159.
- CI main tại 63b60fc489d3d6176c585cf1c57e431a792ffe53 thành công (run 41964394395); chưa kết luận toàn bộ nguyên nhân #157 đã được xử lý.
- Chưa giao agent trong lần kiểm tra này; quota từng agent và các job nền chưa được xác minh đầy đủ. Sản xuất vẫn tạm dừng theo quyết định trước.

## Bàn giao phiên kế tiếp: quyết định mới nhất

Chủ kênh yêu cầu agent kế tiếp tiếp tục điều phối theo phân công dưới đây. Các chỉ dẫn cũ bên dưới trái với mục này là lịch sử. Đợt này chưa khởi chạy agent, chưa tạo worktree hay PR, chưa có kết quả thực thi; không báo là đã giao hoặc đã xong. Kiểm lại GitHub, các job và quota đọc được trước khi khởi chạy; không đoán quota.

- #159 PR 3: owner Claude Sonnet theo chỉ định của chủ kênh, làm cửa dựng chung trong worktree riêng theo thiết kế đã duyệt; test chọn renderer sáu kênh, fail-closed và dry-run. Sonnet là lựa chọn thử, chưa chứng minh phù hợp với task này. Codex ở phiên độc lập review diff và chạy test; Grok kiểm chứng render sau khi code sẵn sàng. Bằng chứng gồm diff, lệnh/test, contact sheet và số đo âm thanh; chưa khẳng định render sáu kênh khả thi khi chưa kiểm media và môi trường. Claude dùng tài khoản công ty: chỉ cung cấp dữ liệu được phép, không tự chuyển toàn bộ repo/log/nội dung riêng. Xác minh khả năng giao và phạm vi dữ liệu trước khi khởi chạy.
- #145: owner Agy trong worktree riêng, tùy quota và môi trường. Nghiệm thu ba điểm issue yêu cầu: cảnh lạ bị từ chối từ nguồn danh sách duy nhất, lỗi JS làm render thất bại, phát hiện khung đứng hình; nộp diff, test hồi quy và bằng chứng. Reviewer phiên độc lập kiểm code và test; đánh giá nguy cơ báo nhầm với cảnh tĩnh hợp lệ.
- #169: owner Codex Terra trong worktree riêng sau khi xác định giao diện API và điểm giao với #145/#159. Dùng client giả kiểm lịch YouTube và chuẩn hóa UTC, không đổi lịch hay ghi DB; reviewer độc lập kiểm các đường upload/reschedule và trường hợp lỗi API. Chỉ chạy đồng thời khi không tranh chấp file và quota cho phép.
- #144: owner Codex Luna nếu model đã chứng minh phù hợp và còn quota; sửa chạy trực tiếp và rà script motion tương tự, test subprocess, nộp diff và kết quả. Nếu chưa xác minh năng lực/quota, để chờ; không suy đoán.
- #157: owner Grok kiểm độc lập run CI, test và nguyên nhân từng lỗi, nộp bằng chứng và kết luận; CI main run 41964394395 xanh, nhưng một run xanh không chứng minh lỗi chập chờn đã hết. Lead kiểm chứng trước khi đề xuất cập nhật issue.
- Grokbot tiếp tục phụ trách Packaging Intelligence; không chạy nghiên cứu trùng. Không có agent nào được tính là đã nhận việc trong mục này.
- AGENTS.md của creator_v2 cấm agent sản xuất sửa code dùng chung và thao tác Git; brief phải tôn trọng phạm vi áp dụng, xác định cơ chế được phép trước khi tạo worktree hay giao sửa các file đó. Không tự coi handoff là quyền bỏ qua các giới hạn này.
- Trước khi khởi chạy: xác minh quota đọc được, job hiện hữu, phạm vi file độc lập, quyền và môi trường render; giữ dự phòng review. Sau hai vòng sửa không đạt thì dừng, phân tích nguyên nhân và đổi cách làm. Không merge hoặc mở lại sản xuất khi chưa có quyết định cần thiết.
- Ưu tiên hành động tiếp: đọc quy định và issue/PR mới nhất; kiểm tra cơ chế giao Claude/Agy/Grok và quyền dữ liệu; viết brief có owner, đầu ra, tiêu chí và bằng chứng, rồi khởi chạy các việc độc lập khi điều kiện cho phép. Báo rõ việc nào đã giao, đang chạy, bị chặn hoặc chưa khởi chạy.

## Cập nhật điều phối: phiên Lead Codex

- Chủ kênh giao Lead Codex quản lý trực tiếp và toàn quyền điều phối MIM, CK, CL; không cần liên hệ các phiên quản lý kênh khác. Các chỉ dẫn cũ yêu cầu liên hệ Learn AI hoặc agent CL không còn là bước bắt buộc. Khả năng truy cập dữ liệu/credentials CL vẫn cần xác minh riêng.
- Chủ kênh giao Codex làm Lead/PM. Mỗi việc có một owner, đầu ra, tiêu chí nghiệm thu và bằng chứng; việc rủi ro đáng kể phải có reviewer ở phiên độc lập, trực tiếp kiểm nguồn, diff, test hoặc artifact. Sau hai vòng sửa không đạt, tìm nguyên nhân và đổi cách giao. Các chỉ dẫn cũ về Claude làm Lead và tự chuyển Codex sang Grok được thay bằng nguyên tắc này.
- Codex làm code/test/tích hợp; Agy nhận nhánh độc lập; Grok nghiên cứu/kiểm chứng; Grokbot giữ Packaging Intelligence; Claude chỉ review khó hoặc góc nhìn khác, với dữ liệu được phép đưa vào tài khoản công ty. Luna cho việc nhỏ rõ, Terra cho mức vừa, Sol cho việc khó, dựa trên năng lực đã chứng minh. Không chạy nghiên cứu trùng Grokbot. Code dùng worktree riêng; chỉ song song việc độc lập.
- Trước mỗi đợt kiểm quota nếu đọc được, giữ dự phòng review/sự cố và không đoán. Báo owner, bằng chứng, blocker, quyết định cần chủ kênh và quota đã biết.
- Đã đọc `creator_v2/AGENTS.md` và các `CLAUDE.md` liên quan. Thử `gh issue list` và `gh pr list` với đúng repo đều thất bại vì proxy từ chối kết nối; mở GitHub qua công cụ web cũng thất bại. Chưa xác minh trạng thái issue/PR hiện tại, chưa phân công hay chạy agent. Không suy diễn trạng thái hiện tại từ bản bàn giao này.
- Máy có lệnh Codex, Agy, Grok; chưa tìm thấy lệnh Grokbot. Chưa có số liệu quota đáng tin cậy. Trạng thái cũ Codex hết quota lúc 10:30 chỉ là lịch sử, không phải số liệu hiện tại.
- Khi kết nối GitHub được khôi phục: kiểm issue/PR và việc đang chạy trước; sau đó lập brief riêng cho PR 3 #159 và các việc độc lập #169, #145, #144 theo ưu tiên thực tế. Chỉ chỉ định reviewer độc lập khi có người và quota phù hợp. PR 3 cần render đối chiếu, review artifact, CI đúng commit cuối và chủ kênh duyệt merge; sản xuất vẫn tạm dừng đến khi chủ kênh quyết định mở lại.

Bản này thay `%TEMP%\handoff-mimck-pm-2026-11-05.md` (sáng 05/11) và bản 04/11. Đọc bản này trước. Trả lời chủ kênh bằng tiếng Việt, ngắn gọn, kèm link issue/PR.

**Tóm tắt điểm mới so với bản sáng:**
- PR 2 của #159 (#166) và #146 (#168) đã merge.
- `main` local ở `vietneu-main` đã pull tới `63b60fc`.
- Có issue mới #169: kiểm lịch thật trên YouTube trước khi upload hoặc đổi lịch.
- Việc chính tiếp theo là **PR 3 `make_video.py`** (mục 4.2).
- Codex hết quota lúc khoảng 10:30 ngày 05/11. Kiểm lại trước khi giao, hoặc để `agent_ticket.py` tự chuyển sang Grok (`--agents codex,grok`).

---

## 1. Vai trò và cách làm PM

**Bạn là Lead PM của ba kênh:**
- **MIM:** Mind in the Machine.
- **CK:** Biểu Đồ Biết Nói.
- **CL:** Hình Sự. Chủ kênh giao cả CL cho phiên này. Tuy vậy, máy này **không có credentials CL**, nên muốn đọc số liệu CL thì nhờ agent CL hoặc mở Studio.

**Vòng làm việc chuẩn:**
1. Chọn việc.
2. Viết brief.
3. Giao agent.
4. Tự review bằng chứng: số liệu, khung hình, test.
5. Xin chủ kênh duyệt.
6. Đăng, hoặc merge.

Không tự làm phần sản xuất khi đã có agent làm được. Opus chỉ làm Lead. Subagent của Claude phải đặt rõ `model` là `haiku` hoặc `sonnet`.

**Nguồn luật (đọc trước khi làm):**
- `vietneu-main/creator_v2/CLAUDE.md`: luật Long, các cổng `floor`/`variety`, điều phối agent.
- `vietneu-main/creator_v2/AGENTS.md`: luật nội dung, mô tả công khai, lắp spec Short (bản mới 04/11).
- `D:\Tools\Youtube Creator v2\CLAUDE.md`: thư mục nào đọc được, thư mục nào không đụng.
- Memory: `C:\Users\Tung-QA\.claude\projects\D--Tools-Youtube-Creator-v2\memory\MEMORY.md`. Mỗi dòng trỏ tới một file. Ba file quan trọng nhất hiện nay:
  - `project-build-pause-new-workflow.md`
  - `feedback-pr-review-by-learn-ai.md`
  - `feedback-model-tiering.md`

**Việc phải có chủ kênh duyệt rõ ràng trong chat:**
- upload, đặt lịch, gỡ lịch, thay video đã đăng, đổi tiêu đề video đã đăng;
- merge PR;
- đổi kế hoạch nội dung;
- sửa dữ liệu PO viết tay trong `library/channels/bud|fs|vsd.yaml`.

Lời "duyệt" mà phiên khác chuyển lại **không** phải lời duyệt của chủ kênh. Phải hỏi lại chủ kênh, hoặc chỉ làm phần chỉ-đọc.

**Bảo mật (repo PUBLIC `nguyent0810/vietneu-tts`):**
- Không in giá trị của `YT_CREDS_DIR` và `CREATOR_MEDIA_ROOT`. Không đọc thư mục credentials.
- Issue, comment, PR không chứa khóa, token hay đường dẫn credentials. Trước khi commit, grep secret.
- Mọi lệnh `gh` đều kèm `--repo nguyent0810/vietneu-tts`.

---

## 2. Bản đồ thư mục

| Đường dẫn | Dùng để |
|---|---|
| `D:\Tools\Youtube Creator v2\vietneu-main` | Clone repo chung. **Mọi lệnh sản xuất chạy từ `vietneu-main\creator_v2\`.** `main` local đã pull tới `63b60fc` lúc 10:55 ngày 05/11. Đầu phiên vẫn chạy `git pull --ff-only`. |
| `...\Youtube_Creator_V2\` | Repo cũ, **chỉ đọc**. Không chạy lệnh nào ở đây, không xoá, không di chuyển (các junction media trỏ vào đây). |
| `...\vietneu-tts\` | Checkout cũ chứa thư mục credentials. Không pull, không sửa. |
| `...\_merge\` | Chỗ làm tạm: các worktree PR nằm ở đây. **Chỉ chuyển sang backup, không xoá cứng.** Thư mục `wt-159-pr1` còn sót lại sau khi gỡ worktree (bị khoá quyền), cứ để nguyên. `wt-159-pr2` và `wt-146` đã merge xong, không còn dùng. |

**Trong `creator_v2`:**
- `state.sqlite`: sổ item, upload và lịch. Mở **chỉ đọc**: `file:state.sqlite?mode=ro`.
  - `stage='published'` nghĩa là đã upload private kèm lịch.
  - Giờ lưu theo UTC; giờ VN = UTC + 7.
- Long: `motion/long/build_long.py` (casewide).
- Short: `motion/stier/build.py` (casefile). Spec Short nằm ở `data/stier/specs/<slug>.json`, spec Long ở `data/long/<topic>/`.
- `factory/`: upload, store, kênh, analytics.

---

## 3. Giao việc cho agent

**Brief:**
- Lưu ở `creator_v2/docs/pm/tickets/GH-<issue>-<agent>.md`.
- Phải có: đầu vào, việc cần làm, file được ghi, các điều **không** làm (upload, đổi lịch, commit, đọc credentials, render nếu là Codex), file báo cáo cố định, và yêu cầu "câu trả lời cuối tối đa 3 dòng".
- Xem mẫu tốt: `GH-159-pr1-codex.md`, `GH-143-grok-ck-render2.md`.

**Chạy:** từ `creator_v2/`, chạy nền (background):
```
python scripts/agent_ticket.py GH-<n> --brief <md> --expect <report.md> --agents codex,grok --timeout 3600
```
Agent hỏng thì script tự chuyển sang agent kế tiếp. Hỏng hết thì có file `.FALLBACK_CLAUDE`, khi đó giao subagent của Claude.

**Ngoại lệ quan trọng:** `agent_ticket.py` chạy Codex với `-C creator_v2`, nên Codex **không ghi được file ở gốc repo** (`library/`, `tests/` gốc). Việc ở gốc repo thì chạy Codex trực tiếp trong worktree (xem các lệnh đã dùng cho PR 1 và PR 2 của #159):
```
codex exec -s workspace-write -C "<worktree>" -c 'model_reasoning_effort="high"' -o <...last.txt> "Đọc và làm đúng brief <path>…"
```

**Chọn agent:**
- Code, spec, test: **Codex**. Codex không render được (sandbox chặn Node, Chrome, ffmpeg) và cũng không chạy được nhiều test (lỗi thư mục tạm, `fcntl`). Lead phải tự chạy lại test.
- Render, QA khung hình, phân tích: **Grok**. **agy** hay hết quota, kiểm trước khi giao.
- Grok viết lời, Codex lắp spec.

**Review:**
- Không tin chữ "đạt" trong báo cáo agent. Tự kiểm ngẫu nhiên các trích dẫn file:dòng, tự chạy test, tự xem khung hình.
- Gặp lỗi test thì chạy cùng bộ test trên main sạch (một worktree detach) để tách lỗi có sẵn khỏi lỗi mới.

**Shell trên máy này:**
- Bash không có sẵn biến môi trường của user. Nạp **không in ra**:
  ```
  export YT_CREDS_DIR="$(powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('YT_CREDS_DIR','User')" | tr -d '\r')"
  ```
  Làm tương tự cho `CREATOR_MEDIA_ROOT`.
- Lỗi in tiếng Việt thì thêm `PYTHONIOENCODING=utf-8`. Chạy `script_lint` cần `PYTHONPATH=.` (#144).

**Phiên "Learn AI":**
- Là Lead BUD/FS/VSD, chạy trên Mac. Địa chỉ nhắn: `bridge:session_01NY7ncXgfc3vwbXJzNdGK9A`, dùng SendMessage.
- **Mọi PR mới đều nhắn họ review.** Họ chưa có quyền comment GitHub, nên chép review của họ vào PR.
- PR đụng `library/`, `hf_*` hoặc `hyperframes_short/` thì họ review. PR đụng `creator_v2/` thì mình tự review.

**PR:**
- Nhánh tên `mimck/...`, tách từ `origin/main` mới.
- **Chờ CI xanh trên đúng commit mới nhất rồi mới merge** (kiểm `headSha` của run). Ngày 05/11 từng merge #156 trước khi CI chạy.
- Commit kết thúc bằng dòng `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Mô tả PR kết thúc bằng dòng 🤖 Generated with Claude Code.

---

## 4. Trạng thái lúc bàn giao

### Sản xuất đang TẠM DỪNG
Chủ kênh quyết định ngày 05/11: không dựng Long hoặc Short mới cho MIM/CK/CL cho tới **PR 3 của #159** (`make_video.py`). Video đã upload và hẹn lịch thì giữ nguyên. Chi tiết trong memory `project-build-pause-new-workflow.md`.

### #159: hợp nhất một workflow cho 6 kênh (đang làm chính)
- Issue: https://github.com/nguyent0810/vietneu-tts/issues/159
- Thiết kế đã duyệt: `creator_v2/docs/pm/2026-11-05-thiet-ke-mot-workflow.md`. Lộ trình ở mục 5, các quyết định của chủ kênh ở mục 6.
- B1 kiểm kê: `creator_v2/docs/pm/tickets/GH-159-b1-report.md`. Phần chỉ có trên Mac và các ràng buộc schema: `GH-159-mac-builders.md`.
- **PR 1 (#165): đã merge.** Có `library/tools/channel_profile.py`, `mim/ck/cl.yaml`, đổi `lich_su`/`vsd`, bỏ `_external.yaml`, `load_profile` fail-closed.
- **PR 2 (#166): đã merge** (`4bcc5fc`, CI xanh trên `14eba77`, Learn AI APPROVE).
  - Long MIM/CK/CL lấy giọng, theme và màu từ hồ sơ kênh. Giá trị vẫn như bảng cũ, có test snapshot.
  - Spec không ghi kênh thì báo lỗi, không còn tự hiểu là CL. 9 spec CL đã có `"channel": "CL"`.
  - `channel_table.py` nạp `channel_profile` theo đường dẫn file, **không đụng `sys.path`**, vì gốc repo có `hf_geo`/`hf_align` trùng tên.
  - Worktree `_merge/wt-159-pr2` không còn dùng. Muốn dọn thì chuyển sang backup, không xoá cứng.

### 4.2 Việc tiếp theo: PR 3 `make_video.py` (ưu tiên số 1)
Thiết kế ở mục 4 và 5 của `2026-11-05-thiet-ke-mot-workflow.md`. Làm theo thứ tự:
1. Tạo worktree `_merge/wt-159-pr3` từ `origin/main`, nhánh `mimck/159-pr3-make-video`.
2. Viết brief `creator_v2/docs/pm/tickets/GH-159-pr3-codex.md`, theo mẫu `GH-159-pr1-codex.md` và `GH-159-pr2-codex.md`. Nội dung:
   - `make_video.py <long|short> <spec | plan --only id> [--channel X]`, theo luồng `resolve(item) → load(id) → dung[kind].engine`.
   - Đăng ký bốn renderer: `casewide` → `motion/long/build_long.py`, `casefile` → `motion/stier/build.py`, `hf_batch` → `hf_batch_render.py`, `studio` → `studio.py`.
   - **Chỉ là cửa chung**: gọi đúng renderer đang chạy tốt, không đổi hình. Dừng trước upload.
   - Hồ sơ hoặc kênh không rõ thì fail-closed.
   - Test: chọn đúng renderer cho từng kênh, kênh lạ thì báo lỗi, và `--dry` in ra lệnh sẽ chạy.
3. Nếu file nằm ở gốc repo, chạy Codex trực tiếp trong worktree (mục 3, "Ngoại lệ quan trọng"). Không dùng `agent_ticket.py` trong trường hợp này.
4. Review diff, tự chạy `creator_v2/tests` và `tests/test_channel_profile.py`, so với main sạch.
5. **Giao Grok render so sánh** (brief riêng `GH-159-pr3-grok-render.md`):
   - một chương `golden` qua `make_video` (casewide), so với bản đã đăng;
   - một Short mỗi kênh: MIM, CK, CL qua casefile;
   - BUD/FS dùng plan của một Short đã hẹn, **không đăng lại**. Phần BUD/FS/VSD chạy trên Mac, nên nhờ Learn AI.
   - Đầu ra: tờ khung hình trước/sau, LUFS, và xác nhận cache TTS không đọc lại.
   - Lead tự xem tờ khung hình, không tin chữ "đạt".
6. Mở PR. PR đụng `library/` hoặc `hf_*` thì nhắn Learn AI review. Chờ CI xanh trên commit cuối, rồi xin chủ kênh duyệt merge.
7. Merge xong thì **hỏi chủ kênh có mở lại sản xuất MIM/CK/CL không** (mục 6.4 của thiết kế). Không tự mở lại.

### 4.3 Sau PR 3
  - PR 2b: giọng BUD/FS vào `voice_profile`. Bên Learn AI làm.
  - PR 4: cổng kiểm theo tên và `luat_noi_dung`.
  - PR 5: kho ảnh chung.
  - PR 6: dọn trùng `webauto`/`hf_align`/`hf_geo`.
  - B3: gộp engine. **Intro, thẻ thương hiệu, thẻ chương, endcard của hai luồng vẫn chưa gộp**: casewide có `brand`/`chapter`/`endcard`; longform có `teaser`/`endcard`; `opening_library` chưa nối.
  - B4: một entry point và tài liệu skill.

### Chuyển giao 3 kênh: chủ kênh đã chốt ngày 05/11
**Phiên MimCk tiếp tục vận hành MIM/CK/CL** cho tới khi workflow hợp nhất đủ nền tảng để phiên Learn AI kế thừa. Memory: `project-mimck-handover-to-learn-ai.md`.

Bốn điều kiện để chuyển giao:
1. PR 3 `make_video` dựng được cả 6 kênh.
2. Đã gộp intro, endcard và thẻ thương hiệu (B3).
3. Phía kế thừa truy cập được `state.sqlite`, media và credentials.
4. Có tài liệu bàn giao.

Khi đủ cả bốn, đề xuất chuyển giao và chờ chủ kênh duyệt. Không tự chuyển giao.

### Việc vận hành còn mở
| Việc | Ở đâu | Chờ gì |
|---|---|---|
| Ba thử nghiệm đổi tiêu đề: Sholes (MIM), Whitey (CL), mua–thuê (CK) | `creator_v2/docs/pm/2026-11-04-de-xuat-noi-dung-3-kenh.md`, issue #143 | Chủ kênh duyệt riêng từng video, và phải có **mức nền CTR theo nguồn** trước khi đổi |
| Số liệu Studio | Đã gửi chủ kênh danh sách cần xuất CSV (Advanced mode, Long/Shorts theo video, nguồn traffic, CTR, shown-in-feed, đối soát giờ xem, baseline của 3 video thử tiêu đề) | Chủ kênh gửi đường dẫn thư mục, rồi giao agent đọc và cập nhật đề xuất |
| Bộ thu số liệu 24h/72h/7d bằng API | Bảng `video_metrics` mới có 4 dòng | Giao Codex viết. Không cần duyệt vì chỉ là phân tích |
| Short CK `ck-them-10-trieu-gio-bot-mot-mon` | Đã upload private, hẹn 07/11 12:00 VN (`OIkDM-qgNu4`). Retro: `creator_v2/docs/pm/2026-11-04-retro-ck-short-suc-mua.md` | Xong |
| Hai cặp Short CK trùng giờ ngày 05/11 | Đã dời `dien-giam` sang 17:30 và `ho-kinh-doanh` sang 22:00 | Xong |
| #147: không in nhãn ảnh AI MIM/CK, không nhắc AI trong mô tả | Đã merge ở #156 | Còn render thử một chương có ảnh AI (ck-f3) sau khi mở lại sản xuất |
| #146: chặn trùng `publish_at` | **Đã merge #168** (`63b60fc`). Có một hàm kiểm ở mọi cửa ghi giờ. Video đã vào `upload_log` thì giờ trong sổ là chuẩn | Xong. 8 cặp gốc/`-r2` (08–22/11) trong `item` vẫn ghi cùng giờ, nhưng đúng là chỉ bản `-r2` giữ lịch. Không sửa DB |
| #169: kiểm lịch thật trên YouTube trước khi upload hoặc đổi lịch, ưu tiên CL | https://github.com/nguyent0810/vietneu-tts/issues/169 (theo review của Learn AI cho #168; các lưu ý cũng ghi ở #159) | Giao Codex, không cần duyệt (code + test, client giả). Làm song song với PR 3 |
| #145: preflight bỏ qua loại cảnh lạ, video đứng hình (P1) | GitHub issue | Giao Codex. Nên xong trước khi mở lại sản xuất Short |
| #144: lint import (P2) | GitHub issue | Giao Codex, việc nhỏ |
| #157: CI main có 3 lỗi có sẵn | GitHub issue | Hiện CI xanh trên #166 và #168. Kiểm xem issue còn đúng không, rồi đóng hoặc cập nhật |
| Kho tài sản dùng chung | Thiết kế ở ticket 142 bên Learn AI | Họ gửi schema chốt, rồi giao Codex xuất manifest MIM/CK từ các sidecar |

Đầu phiên mới, chạy:
```
gh issue list --repo nguyent0810/vietneu-tts
gh pr list --repo nguyent0810/vietneu-tts
```

---

## 5. Bài học ngày 04–05/11, không được lặp lại
- Cảnh Short không có `"type": "clip"`. Footage phải là `kinetic` cộng trường `"clip": "pexels:<id>"`. Preflight báo OK chưa chứng minh được gì: **phải xem tờ khung hình** (#145).
- Slot trong ngày phải xong cả duyệt trước giờ hẹn ít nhất 3 giờ. `upload_one.py` chặn giờ hẹn cách hiện tại dưới 30 phút.
- Trước khi chọn giờ hẹn, liệt kê `publish_at` của kênh để tránh trùng (#146).
- Sau mỗi đợt upload, chạy một subagent retro (sonnet). Video đã đăng thì để yên, nhưng phải sửa tận gốc nguyên nhân.
- Đang có job ghi file trong một worktree thì không merge hay đổi nhánh worktree đó.
- Khi review một cổng kiểm mới, **chạy nó trên DB thật mở chỉ đọc**. Test xanh không đủ: ở #146, nhờ chạy trên DB thật mới thấy 8 cặp gốc/`-r2` bị chặn nhầm.
- `gh pr merge --match-head-commit` cần SHA đầy đủ 40 ký tự (`git rev-parse HEAD`).
- Khi thay một bảng bằng dữ liệu: test **snapshot bảng cũ**. Bỏ các khối rỗng `{}` (công cụ BUD/FS hiểu rỗng là "đã cấu hình"). Hồ sơ hỏng thì phải **fail-closed**.

---

## 6. Skill nên dùng
- `mattpocock-skills:pr`: viết mô tả PR cho các PR tiếp theo của #159.
- `mattpocock-skills:code-review` hoặc `code-review`: tự review diff của Codex trước khi mở PR.
- `mattpocock-skills:diagnosing-bugs`: khi render hoặc test lỗi khó hiểu (ví dụ video đứng hình).
- `mattpocock-skills:research`: khi cần giao nghiên cứu nguồn sơ cấp, ví dụ dữ kiện cho Short.
- `hyperframes-cli` hoặc `hyperframes`: chỉ khi phải tự chẩn đoán render HyperFrames. Bình thường giao Grok.
- `anthropic-skills:consolidate-memory`: dọn memory khi index dài; một số file cũ đã lỗi thời so với #159.
