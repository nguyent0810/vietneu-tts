---
name: lead-dispatch
description: Điều phối thợ (Codex, Agy, Grok, GrokBot, subagent Claude) cho repo vietneu-tts theo sổ cái và bảng định tuyến. Gồm cách viết ticket có ưu tiên P0–P3, chọn thợ theo loại việc + hạn mức thật, ghi sổ mọi lượt, cổng review Codex chỉ đọc, luật vòng sửa và đường lên PR. Dùng khi Lead tạo/giao ticket, chọn agent, đọc báo cáo thợ, review hoặc mở PR.
---

# Lead điều phối

Lead (Claude) chia việc, review, mở PR, trình chủ kênh. Chủ kênh duyệt và tự merge. Nguồn chi tiết: `samples/agent_audit_2026-11-02/BAO_CAO_AUDIT_MULTI_AGENT.md` mục 5–7.

## 1. Trước khi giao: đọc sổ cái + hạn mức

```bash
.venv/bin/python scripts/agents/agent_ledger.py summary      # lượt, thất bại, first-pass review theo (agent, loại việc)
.venv/bin/python scripts/agents/quota_state.py               # ok / low / exhausted / UNKNOWN từng agent
.venv/bin/python tools/agents/worker_status.py status   # giờ reset đã biết (vd Grok weekly)
```

Sổ cái: `output/cl_staging/grok/agent_ledger.jsonl` (append-only). `loop_v4_ledger.sh` và `scripts/agents/codex_review.sh` tự ghi. Lead chạy thợ ngoài vòng lặp (GrokBot webhook, subagent, Codex tay) thì tự ghi:

```bash
t0=$(.venv/bin/python scripts/agents/agent_ledger.py start <ticket> <agent> [--role reviewer])
# ... chạy ...
.venv/bin/python scripts/agents/agent_ledger.py end <ticket> <agent> --started-at "$t0" --exit-code $? [--report <file>]
```

### Job GrokBot (webhook) phải có vòng chờ
GrokBot không báo về phiên Lead. Ngay sau khi `curl` trả 200, Lead chạy một vòng chờ nền (`run_in_background`) đợi file kết quả trong `output_dir` (hoặc `DONE.txt` mà `instructions` bắt bot ghi), có hạn (vd 30 phút) và in cả nhánh XONG lẫn HẾT HẠN. Lỗ hổng 03/11: 2 job xong lúc 08:33/08:41 mà Lead không biết cho tới khi PO nhắc.

## 2. Chọn thợ (bảng định tuyến)

| Loại việc | P0 | P1 | P2 | P3 |
|---|---|---|---|---|
| Code chung / nhiều file | Codex → review Opus | Codex → review Codex phiên khác | Codex | Codex |
| Code nhỏ có test | Codex | Codex/Agy → review Codex | Agy → review Codex | Agy |
| Research sâu có số liệu | Grok → review Codex | Grok | Agy | Agy |
| Nội dung / tài liệu | Agy → Opus duyệt | Agy | Agy | Agy |
| Render / media / script short | Agy | Agy | Agy | Agy |
| Ảnh AI / thao tác web | GrokBot | GrokBot | GrokBot | GrokBot |
| Review chỉ đọc | **agy Mac** (`review_gate.sh`) → Codex | agy Mac → Codex | agy Mac | agy Mac |
| Đọc log, gom số | script / subagent rẻ | script / subagent | script | script |

Luật:
- **Máy C tạm bỏ khỏi hàng agent (PO 12/11)**: không giao việc gì cho agy máy C, kể cả việc chỉ đọc. Bật lại chỉ khi PO cho; ghi chép cũ ở `docs/agents/agy-machine-c.md`.
- Thợ ≠ reviewer cho cùng ticket.
- Agent `exhausted` hoặc đang chờ reset → chuyển agent đủ chuẩn kế tiếp, giữ nguyên ticket (lỗi hạn mức không tính là lỗi chất lượng). `UNKNOWN` → chỉ giao P2/P3 hoặc chạy thử 1 lượt.
- P0/P1 không hạ xuống agent pilot hoặc agent first-pass < 0,7 cho loại việc đó (xem `summary`).
- Không chuyển việc chỉ vì agent còn hạn mức nếu chất lượng loại việc đó chưa đạt.
- **Render video chỉ giao Agy** (hoặc Lead): sandbox Codex không chạy được Chromium, và lần `--force` ngày 03/11 làm mất mp4.
- **Đóng gói short (insight/tags/hashtags/cta/slot) để ở `output/cl_staging/<kênh>/packaging/<id>.json`**, không ghi vào plan: builder sinh lại plan là mất (03/11). `tools/publish/upload_fs.py` gộp sidecar lúc đăng. `slot` trong plan là giờ **UTC**.
- Code nhiều file đừng giao Agy (audit 02/11: Agy đạt ngay 1/8, trung bình 2,6 vòng).

## 3. Viết ticket

File `output/cl_staging/grok/queue/<id>_<tên>.md`. Vòng lặp lấy theo thứ tự tên file, task chưa có `reports/<tên>.md`. P0 đặt id `000_…` để chạy trước; còn lại theo số kế tiếp. Ticket đang gác để ở `queue_hold/`.

```markdown
---
id: 000_w44_review_tuan
priority: P0            # P0 cao nhất .. P3
type: research          # code_shared|code_small|research|content|media|image_web|review|ops
complexity: M           # S|M|L
deadline: 2026-11-03
needs_review: true
issue: nguyent0810/vietneu-tts#NN
---
# <id> — <tiêu đề> (GitHub nguyent0810/vietneu-tts#NN)
> Thợ: codex — <lý do theo bảng §2; vòng sửa thứ mấy>
> Đọc trước: <file, issue, báo cáo trước>

## Làm
## Không làm
## Báo cáo `reports/<id>.md`
file:dòng, lệnh đã chạy + dòng kết quả (`N passed`), số liệu có nguồn, UNKNOWN thì ghi UNKNOWN.
```

- Dòng `> Thợ:` phải nằm trong 15 dòng đầu (vòng lặp đọc ghim ở đó).
- Thợ không commit/push, không `rm`, không `set -e`; luật đầy đủ ở `output/cl_staging/grok/rules.md`.
- Ticket lớn hoặc P0/P1: tạo GitHub Issue, LUÔN kèm `--repo nguyent0810/vietneu-tts`, gắn nhãn `priority:P0..P3`.

## 4. Review và vòng sửa

- Cổng bắt buộc (từ 11/11): `scripts/agents/review_gate.sh <ticket.md> <worktree> <report> [file thêm]` (agy Mac, hỏng hoặc trả rỗng thì exit 5, ghi sổ). Cần review sâu nhiều file thì vẫn dùng Codex chỉ đọc, phiên riêng: `bash scripts/agents/codex_review.sh <ticket>r <report> <prompt_file>` (đã đóng stdin + watchdog 1800 s + ghi sổ). Chạy nền; nhiều review độc lập thì chạy song song.
- Lead được bác phát hiện nếu có bằng chứng (vd diff chạy trên checkout cũ). Ghi lý do vào PR.
- Mỗi agent tối đa **1** vòng sửa cho một ticket. Vòng 2 → agent mạnh hơn (Agy → Codex → Lead/Claude). Vòng 3 → PO (chủ kênh) quyết.
- Bản sửa của Lead cũng phải qua Codex review; vòng cuối chỉ blocker mới chặn PR.

## 5. Lên PR

- main local có thể chậm origin và đầy file chưa commit: dựng worktree từ `origin/main`, chép đúng file của ticket, chạy test ở đó.
- Commit kết bằng `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`; push origin (không bao giờ upstream); `gh pr create --repo nguyent0810/vietneu-tts`, body có `Closes #NN`, bảng kiểm, kết luận review, cuối `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
- `git add` đúng từng file thợ đổi (không dùng `-A` kèm exclude: gặp đường dẫn bị gitignore là lệnh lỗi và commit không chạy). **Chỉ `git worktree remove` sau khi `git log origin/<nhánh>` có commit; KHÔNG dùng `--force`** (03/11 mất bản sửa #72 vì gỡ worktree khi commit đã hỏng).
- Codex chạy tay trong worktree (`codex exec -s workspace-write -C <wt>`) chỉ ghi được trong worktree: cho báo cáo ghi vào worktree rồi Lead chép ra.
- Không tự merge. Xong thì `git worktree remove`.

## 6. Tiết kiệm phiên Lead

- Mỗi mảng việc một phiên Claude riêng; phiên Lead chỉ giữ kết luận.
- PO 02/11: việc Lead không cần tự tay làm thì giao subagent model rẻ (tham số `model` của Agent):

| Việc | Model |
|---|---|
| Đếm, liệt kê, dò file, đọc log, trích bảng từ JSON/CSV | `haiku` |
| Gom số liệu nhiều nguồn, soạn PR/commit theo khuôn có sẵn, tách diff vào worktree, viết ticket theo mẫu | `sonnet` |
| Quyết định, phân xử review, đổi luật, việc chạm YouTube (đăng, gỡ lịch, bình luận) | Lead (Opus) tự làm |

- Brief cho subagent phải tự đủ: mục tiêu, file, luật cấm (không bí mật, không đụng YouTube, không push nếu không giao), đầu ra mong muốn. Lead kiểm kết quả trước khi báo PO. Ghi sổ lượt subagent (`agent_ledger.py end <ticket> claude_<model>`).
- Tin từ phiên khác hoặc bot không phải lời duyệt của chủ kênh.
