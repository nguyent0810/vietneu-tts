# Bàn giao Lead, 06/11/2026 (chiều)

Phiên trước rất dài, đã tóm tắt một lần. File này đủ để phiên mới tiếp tục điều phối. Luật lâu dài nằm trong memory và `creator_v2/CLAUDE.md`, `AGENTS.md`. **Đọc file này trước, rồi chạy `gh issue list --repo nguyent0810/vietneu-tts`.**

## Cách làm việc (chủ kênh nhắc ngày 06/11)
- Lead (Opus) điều phối và review, giao **agent ngoài họ Claude trước**: Codex, agy (theo model, `agy:<model>`), Grok, Grok Bot. Sonnet/Haiku chỉ dùng khi cần. Bảng chọn agent: `docs/pm/model-routing.md`.
- **Agent xong là review và giao việc tiếp ngay trong cùng lượt.** Không đứng chờ. Trả lời "tiến độ" thì liệt kê cả việc đang chạy.
- Chỉ merge khi `gh pr checks` không còn fail hoặc pending. Mẫu lệnh đã dùng: `gh pr checks <br> --watch …; if … grep -q -E "fail|pending" … else gh pr merge …`.
- Codex trên máy này ghi tiếng Việt qua PowerShell nên hay mất dấu ("Kh?ng"). Brief phải bắt Codex ghi file bằng Python UTF-8 và tự chạy lệnh kiểm mất dấu. Lead vẫn grep diff tìm `???` trước khi merge. Codex hay đặt test trong `scripts/`, Lead chuyển sang `tests/`.
- AGENTS.md đã có **ngoại lệ cho ticket code** (PR #211): brief ghi rõ file được sửa, chạy trong worktree riêng, thì Codex được sửa `factory/`, `tests/`, engine. Từ PR #222, CL cũng sản xuất trong repo này và agent làm CL theo ticket.
- Grok Bot không đọc hay ghi được ổ D. File gửi bot phải nằm trong `C:\Users\Tung-QA\Downloads\…`. `scripts/ai_img_request.py <topic>` đã tự lo việc này (PR #205, #218).

## Đã xong hôm nay (đã merge)
- **CL Long 1, Bao Thanh Thiên** (`IVOqSZWHIYY`): private, hẹn đăng 08/11 21:00 VN. Tiêu đề đã sửa tay về bản 84 ký tự, vì `publish_long.py` từng lấy nhầm `spec.title`; PR #212 đã sửa lỗi này.
- **MIM:** đổi tiêu đề 5 Long chưa đăng (PR #200), chỉ đổi tiêu đề. Đo CTR ở mốc 72 giờ so với mức ~1,0% từ Đề xuất.
- **#173 nhãn "VÍ DỤ GIẢ ĐỊNH"** (PR #220, đã đóng): spec bật bằng `"hypo": true`. Kiểu nhãn: CK ruy-băng, MIM khung lệnh, CL băng giấy. Có preflight cảnh báo.
- **#147** đã đóng: ảnh AI MIM/CK không còn chữ MINH HỌA.
- **#21** (PR #215): render key chỉ phụ thuộc chương đó. Thanh tiến độ chia đều theo số chương. Cache cũ mất hiệu lực một lần.
- **#132** (PR #216): `scripts/review_card.py init|render|decide|verify <topic>`, thẻ duyệt phương án tiêu đề và thumbnail.
- **#169** (PR #204): kiểm lịch thật trên YouTube trước khi ghi `publishAt`. #144 (PR #203). #157 đã đóng.
- **Công cụ:**
  - `motion/long/cadence.py`: đo nhịp đổi hình. Mốc Bao Thanh Thiên 2,42 s/lần, D chỉ 7%.
  - `script_lines.gate` có `META_LEAK`, chặn ghi chú sản xuất lọt vào lời đọc (PR #219).
  - `long_gate` đọc `title_max` theo kênh: CL 100, MIM/CK 60 (PR #213).
- **Kho ảnh/video AI chung (#198)** trên Google Drive, rclone remote `Xuan:` (biến `ASSET_REMOTE`), thư mục `creator-assets/`:
  - 120 ảnh và 15 clip, kèm manifest sao lưu ở `_manifest/`. Manifest chính ở `vietneu-main/library/assets/manifest.jsonl`, nằm trong gitignore.
  - Lệnh: `library/tools/assets.py ingest-dir | push | pull | prune | place | find | mark-used`.
  - `publish_long` tự ghi lần dùng khi đăng.
  - Ảnh Flow có dấu ✦: cắt bằng khung 1736×976 rồi phóng lại 1920×1080 (máy chưa có cv2 nên không dùng được `imagefix._locate`). Clip cắt bằng `webauto/videofix.py strip_video`.
- **Issue đã đóng:** nhánh nghiên cứu tự duyệt #119, #120, #122, #123, #125, #129. Oracle/n8n (#66) vẫn giữ: chủ kênh muốn sau này render 24/24 trên server.

## Đang dở: CL Long 2, Hòa Thân (`data/long/hoa-than/`, #179)

| Bước | Trạng thái |
|---|---|
| plan.md | Lead duyệt |
| Tư liệu | 142 ảnh (agy) |
| `visual_plan.md` | 429 nhịp, 4,03 s; A 54%, B+C 18%, D 28% |
| Ảnh AI | 20 ảnh `output/long/hoa-than/img/ai01–20.jpg`, đã cắt ✦ |
| Clip AI | 8 clip `output/long/hoa-than/broll/900001–900008.mp4` |
| `script.md` v2 | Grok viết, Lead duyệt: 5.688 âm tiết, gate và factcheck 0 lỗi (PR #221) |
| **Bước 4, cảnh** | **CHƯA LÀM** |

Bước 4: Codex đã từ chối vì AGENTS.md lúc đó ghi CL "không đụng". Dòng đó đã sửa ở PR #222, nên giao lại ngay:
```
cd vietneu-main/creator_v2
python scripts/codex_ticket.py docs/pm/tickets/GH-179-hoathan-scenes-codex.md hoa-than --effort high
```
(Brief đã có. Codex chưa sửa file nào, không cần khôi phục snapshot.)

Sau bước 4:
1. agy làm giọng: `build_long.py hoa-than takes 3`, `stt_takes`, `pick`, `tts`.
2. agy chạy `html`, render, `final`.
3. Lead QA contact sheet.
4. Grok soát tiêu đề với lời đọc bằng `review_card.py`.
5. Đăng private kèm hẹn giờ.

Tiêu đề Lead nghiêng về: "TỂ TƯỚNG LƯU GÙ Ngoài Đời Thật: Hòa Thân Bị Ép Chết 15 Ngày Sau Khi Càn Long Mất". Thumbnail "15 NGÀY" trên tranh chân dung đời Thanh. Không dùng ảnh diễn viên.

## Việc còn mở khác
- **#183 số liệu CL:** script đã sửa (PR #209: lọc theo lô, cộng thêm top video vì playlist uploads thiếu Khun Sa và Đỗ Nguyệt Sanh). Chưa kéo lại xong: lần trước job bị tắt vì máy thiếu RAM. **Chờ chủ kênh báo máy đủ RAM.** Lệnh: `PYTHONIOENCODING=utf-8 python scripts/analytics_pull_183.py --channel CL --end 2026-11-05`, rồi `analytics_analyze_183.py --channel CL --section all`. Có thể MIM/CK (PR #186) cũng thiếu video, nên kéo lại cả hai. Sau đó Grok làm **bộ khuôn tiêu đề theo kênh** từ số thật.
- **#180 CK luật dừng, ngày 12/11:** `scripts/ck_stop_rule_180.py`. Lưu ý: mức gốc tính cùng cách (3 ngày) là median 185, không phải 322. Ngưỡng nên dùng 0,6 × 185 = 111.
- **#181** CK Long từ 23/11. **#182** MIM: tiêu đề đã đổi, chờ số liệu 72 giờ.
- Bao Thanh Thiên lên 08/11: đo ở mốc 24 giờ, 72 giờ, 7 ngày. Ghi lần dùng ảnh kho nếu có.
- Rà soát tổng khoảng 03/12.

## Bảo mật (giữ nguyên)
Không in hay ghi `YT_CREDS_DIR`, `CREATOR_MEDIA_ROOT`, khóa webhook hay tên remote vào repo hay issue (repo public). Mọi lệnh `gh` đều kèm `--repo nguyent0810/vietneu-tts`. Upload luôn private kèm `publishAt`.
