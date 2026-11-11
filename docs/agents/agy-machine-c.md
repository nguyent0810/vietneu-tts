# Điều phối agy trên máy C (bể hạn mức thứ hai)

Từ 11/11/2026, PO cho chạy agy trên máy C, đăng nhập bằng một **tài khoản Google khác** với Mac. Như vậy máy C có bể hạn mức riêng gồm Gemini, Claude/GPT và Argon, tách khỏi agy trên Mac.
Tài liệu này dành cho mọi Lead đang điều phối repo, gồm cả Lead V2 (creator_v2: CL, MIM, CK).

## Máy và đường kết nối
| | |
|---|---|
| Máy | Windows 11, `DESKTOP-IOHT12L`, user Windows `du bi` |
| Tailscale | tên máy `may-c`, IP 100.65.218.98. Máy B `desktop-2ja218a` cùng tailnet nhưng **không đụng tới**. |
| SSH | alias `C-ts` qua Tailscale và `C` qua LAN 192.168.0.221, khai trong `~/.ssh/config` của Mac. Cả hai dùng khoá riêng và kiểm vân tay máy. |
| Kiểm nhanh | `ssh C-ts hostname` phải ra `DESKTOP-IOHT12L` |

## Máy C nhận việc gì
Chỉ nhận **việc chỉ đọc**: Lead gửi chữ sang, máy C trả chữ về. **Không clone repo, không có token GitHub hay khoá nào trên máy C.**

| Việc | Model | Lệnh |
|---|---|---|
| Cổng review bắt buộc cho ticket/PR của thợ | `gemini-3.8-flash-high` | `scripts/agents/review_gate.sh` |
| Viết lời đọc Long/Short theo `long-script/references/writer-brief.md` | `gemini-4-argon-high`, dự phòng `claude-sonnet-5-5` | `scripts/agents/agy_c.sh` |
| Soát sự thật kịch bản, đối chiếu với gói nghiên cứu | Flash hoặc Argon | `agy_c.sh` |
| Nháp đóng gói (title, chữ thumbnail, mô tả). Lead chấm, PO duyệt. | Argon | `agy_c.sh` |

**Không giao cho máy C:**
- ticket sửa code (repo chưa chạy trên Windows);
- render, Grok Bot, Flow hay bất cứ việc gì cần trình duyệt;
- việc cần khoá YouTube hoặc API.

Máy C cũng là hạ tầng test của QA, nên không mở port, không dùng Docker, không đọc `D:\qa-*`. Xem thêm ràng buộc QA trong ADR/ghi chú máy C.

## Cách gọi
```bash
# Một prompt bất kỳ -> câu trả lời (exit 0 = SUCCESS; 3 = mất kết nối/chưa đăng nhập; 4 = agy báo lỗi)
scripts/agents/agy_c.sh prompt.txt [model] > ketqua.md

# Cổng review: gom ticket + diff worktree + file đính kèm, máy C trước, hỏng thì agy Mac
scripts/agents/review_gate.sh queue/034b.md output/worktrees/wt_034 reports/review_034b.md [file thêm...]

# Hạn mức máy C (cache riêng heartbeat/agy_quota_c.json)
python scripts/agents/agy_route.py quota --host c
python scripts/agents/agy_route.py pick TICKET.md --host c
```

**Điểm then chốt:**
- **Lead gom file bằng shell** (`git diff > p.txt`, `cat brief.md >> p.txt`), không đọc nội dung vào ngữ cảnh của mình. Như vậy token của Lead chỉ tốn cho dòng lệnh và phần kết quả trả về.
- Đính kèm sẵn cũng tiết kiệm hạn mức máy C hơn để agy tự đọc repo: một lượt là xong, không tốn thêm các lượt gọi công cụ.
- Prompt review phải mở đầu bằng "KHÔNG gọi bất kỳ công cụ/lệnh/đọc file nào…". Thiếu câu này, agy dễ cố gọi công cụ rồi hỏng.
- Prompt đi qua **stdin** dạng stream-json `{"event":"user","message":{"role":"user","content":...}}`. Không truyền prompt qua dòng lệnh vì Windows giới hạn khoảng 32 nghìn ký tự.
- `gemini-3.8-flash-high` không chạy được với `--effort low`.
- Thời gian tham khảo: prompt 18 KB mất khoảng 220 giây.

## Thứ tự định tuyến
1. Việc chỉ đọc: **máy C trước**, để dành hạn mức Mac cho thợ sửa code.
2. Máy C hỏng (tắt máy, mất Tailscale, mất đăng nhập, hạn mức dưới ngưỡng trong `agy_route`): chuyển agy Mac.
3. Cả hai hỏng: Lead dùng sub-agent hoặc chờ. Không bỏ qua cổng review.

Mọi lượt đều ghi `agent_ledger.py` với agent `agy_c` hoặc `agy_local`, vai `reviewer`.

## Đăng nhập agy trên máy C: bẫy và cách làm lại
Khi chạy qua SSH, Windows không mở được kho mật khẩu hệ thống ("OS credential manager unavailable"). Agy khi đó lưu phiên vào file `C:\Users\Du bi\AppData\Roaming\antigravity\plugin-secrets.json`. Vì vậy:
- **Đăng nhập agy trên màn hình máy C không giúp được phiên SSH.**
- Phải đăng nhập **bên trong một phiên SSH**. PO tự làm trong Terminal của Mac, không gõ trong khung chat:
  `ssh C-ts` → `agy "-p=hello"` → mở link trên trình duyệt Mac → đăng nhập tài khoản Google thứ hai → dán mã vào Terminal.
- Chỉ cần làm một lần, agy tự gia hạn. Phải làm lại khi Google thu hồi phiên (đổi mật khẩu, gỡ quyền, hoặc để lâu không dùng). Lúc đó `agy_c.sh` sẽ trả exit 3 kèm dòng "chưa đăng nhập?".
- Không bao giờ dán link OAuth hay mã xác thực vào chat hoặc log.

### Đã giải quyết (11/11): phiên đăng nhập phải tạo qua SSH bằng khoá, từ Mac
- **Lần 1 hỏng:** phiên dùng được khoảng 15 phút, rồi mất khi phiên dùng để đăng nhập đóng lại. Nghi là lần đó đăng nhập không qua SSH bằng khoá, ví dụ ngay trên màn hình máy C hoặc SSH bằng mật khẩu.
- **Lần 2 đạt:** PO chạy `ssh -o PreferredAuthentications=publickey C-ts` từ Terminal của Mac, rồi `agy "-p=hello"`. Lead đóng hẳn phiên đó (`taskkill` tiến trình sshd của phiên) rồi gọi lại, agy vẫn chạy.
- **Mẹo kiểm:** muốn biết phiên đăng nhập còn treo hay không thì liệt kê các `sshd.exe` kèm tiến trình con. Phiên có `conhost.exe` là cửa sổ dòng lệnh của người dùng còn mở.
- Phiên mất lần nữa thì làm lại đúng các bước trên. Không đăng nhập agy ngay trên màn hình máy C.
- Khi máy C hỏng, `review_gate.sh` tự chuyển sang agy Mac. Đã thử thật ngày 11/11.
