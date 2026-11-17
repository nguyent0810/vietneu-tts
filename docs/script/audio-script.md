# Lời đọc chung — 075b

PO 17/11/2026; áp theo kênh + khuôn + engine. Đọc phần này trước, rồi chỉ đọc hồ sơ liên quan.

## 1. Phạm vi và thứ tự quyết định
Chỉ thị PO/user đang hiệu lực đúng phạm vi → luật nguồn/kênh đúng miền → hợp đồng kỹ thuật engine → dữ liệu quan sát kèm giới hạn → mặc định biên tập → kỹ thuật ngoài. Luật thao tác/bảo mật thuộc quy trình, không phải văn phong.

**Câu** là một ý trọn để nghe; **dòng TTS** là đơn vị engine phát; **beat** là bước ý/diễn biến; **tiếng đọc** tính số sau mở rộng cách đọc, khác **token** tách bằng khoảng trắng. Thời lượng giọng thuần khác thời lượng có pause/tail.

## 2. Hợp đồng giao lời
**Lõi 1.** Viết câu trọn, mặc định một dòng một câu. Câu ngắn tự đủ nghĩa vẫn tốt; không ngắt bằng phẩy cuối dòng để chiều caption.
**Lõi 2.** Tách lời sạch khỏi nguồn, hướng hình, timing và voice. URL, JSON, `{pd}`, `[PAUSE]` nằm ngoài lời sau adapter. Đậm/HOA phục vụ hình, không bảo đảm nhấn giọng.

Giao script + notes nguồn/điểm chưa chắc + kênh/khuôn/engine + cấu hình giọng và ngày đang có. Không thêm trường bắt buộc chỉ để đủ mẫu này.

## 3. Viết cho một người nghe
**Lõi 3.** Cho nghe rõ ai làm gì, vì sao ý sau nối ý trước. Dùng từ quen, giải thuật ngữ tại nơi cần; gọi “bạn” khi hợp giọng.
**Lõi 4.** Viết tên và số theo cách giọng cần đọc. Làm tròn lượng để nghe nhưng giữ đúng định danh/năm sinh; mã kinh/giờ chính xác ưu tiên hình và notes. Không mặc định mọi kênh cần nhân vật hay câu hỏi tu từ.

## 4. Lời hứa và tiến triển
**Lõi 5.** Lời mở khớp điều tiêu đề hứa và có câu trả cụ thể. Mỗi đoạn thêm diễn biến, lý do, chứng cứ hoặc hệ quả; Short tự có giá trị. Bảng tra trả sớm, truyện trả theo diễn tiến. Chỉ đúng câu đáp khi tự soát; khớp từ khoá không chứng minh đã trả lời.

## 5. Nhịp câu và khoảng lặng
**Lõi 6.** Độ dài câu đi theo ý, lặng đi theo điểm đọng. Xen nhịp; nghe cả đoạn để phát hiện chuỗi vụn hay đều, không đệm câu cho đủ quota. Long BUD/FS giữ trần 35 tiếng đọc/câu; một dòng nhiều câu chỉ được gợi ý sửa, không tự gộp 45 tiếng.

PO 17/11 bỏ ép câu mười tiếng/ba giây trong hai phút mở. Cổng HÌNH giữ nguyên: 120 giây đầu ảnh/clip động ≤8s, cảnh tĩnh ≤4s; chữ nền trống ≤1,5s. Lập hình theo ý và kiểm timing thật ở workflow hình; không sửa code pace_gate/hf_qa để giải quyết lời.

## 6. Sự thật, diễn giải và phỏng dựng
**Lõi 7.** Sự thật cứng/lời trích truy được nguồn; giữ mức chắc chắn làm đổi nghĩa. Nguồn chi tiết ở notes/hình/mô tả; bớt rào nguồn lặp không có nghĩa bỏ khung truyền thống hay lời khai.
**Lõi 8.** Giữ quyền kể theo đúng miền: sự thật; bối cảnh/cảm giác phỏng dựng; giọng người kể. Gợi ý dùng cảnh, tương phản và callback để tăng chất kể. Nhãn không biến sự kiện bịa thành thật. Luật BUD, người còn sống và CK nằm trong hồ sơ; không tạo lint mới để xét phỏng dựng.

## 7. Viết → tự chấm → sửa
**Lõi 9.** Chọn ngân sách theo giọng đã đo; kiểm bằng âm thanh đúng bản, không lấy một tốc độ chung. [Bảng tốc độ](voice-rates.md) phân tiếng giọng thuần/cả nghỉ; `tiếng dự kiến = phút × tốc độ cả nghỉ cùng cấu hình`. Giọng chưa có mẫu: ghi ước lượng, chưa gọi là đo.

Chốt brief nhỏ (người nghe, một lời hứa, dữ kiện chính, profile); viết; đọc/ở phiên sản xuất nghe mở–số/tên–đỉnh–kết không nhìn hình; ghi một ý đọng lại. Chọn tối đa ba điểm yếu, ghi trước→sau + lý do + dữ kiện giữ; kiểm lại phần đổi. Có thể làm hai vòng để quản lý công sức, không phải hạn mức chất lượng. Lead review theo routing đang có.

Phiếu tự soát 0 thiếu/sai · 1 có nhưng yếu · 2 rõ/nghe được; cho phép “không áp” có lý do. **Không tổng điểm, không điểm sàn, không cổng.**

| Mục | Bằng chứng tự chỉ ra |
|---|---|
| Lời hứa/người nghe | Câu mở và câu đáp |
| Tiến triển | Ý/diễn biến mới của từng đoạn |
| Nghe hiểu | Chủ thể, đại từ, tên/số/đơn vị |
| Nhịp | Chỗ vụn/đều, điểm lặng |
| Giọng | Đúng hồ sơ kênh |
| Nguồn/miền sáng tạo | Claim, quote, số, khung/nhãn |
| TTS/thời lượng | Giọng, bộ đếm, clock, lint thực chạy |
| Kết | Trả lời mở, callback/CTA khi phù hợp |

## 8. Chọn hồ sơ, chỉ đọc phần khác lõi
[BUD](profiles/bud.md) · [FS](profiles/fs.md) · [FS lookup](profiles/fs-lookup.md) · [VSD](profiles/vsd.md) · [CL](profiles/cl.md) · [MIM](profiles/mim.md) · [CK](profiles/ck.md) · [Long chuẩn](profiles/long-standard.md) · [Long nhân vật](profiles/long-nhan-vat.md) · [Tuyển tập/Q&A](profiles/tuyen-tap-qa.md) · [Đêm nghe](profiles/night.md) · [Short kể](profiles/short-story.md) · [Short thắng 9–18s](profiles/short-win-9-18.md) · [V2 phỏng dựng](profiles/v2-narrative.md).

## 9. Adapter và mức kiểm
HBR: `script[]`, `chap`, `tts.*`, `day`; V2: script/lines, `{pd}`/marks được adapter gỡ, `publish_at`. `effective_date` ưu tiên effective_date → day → publish_at, so ngày ISO; ngày mâu thuẫn cần Lead phân loại, không thêm cổng metadata. Short thiếu ngày dùng luật câu trọn mới, không ngầm coi là bài cũ.

Long `cau_tron` là LỖI khi có khoá `tts.pause_ctx` (hoặc `pause_ctx` ở row; kể cả rỗng), hoặc ngày ≥ `AUDIO_SCRIPT_FROM` trong `audio_script_rules.py`; trước đó CB. **Lead điền ngày merge thật vào hằng hiện để None trước merge**, không hồi tố ngày nghiên cứu. Short giữ mốc 29/11 đã duyệt. Clock nháp HBR còn token/185; `--rate` có thể chọn theo bảng giọng. Segments cùng số dòng chưa chứng minh cùng chữ/giọng: kiểm bản ghi trước khi gọi timing cuối.

Danh mục audio chặn của đường HBR/shortbuild: **10 nhóm**, không tính cổng hình hay schema/render:

| Nhóm | Scope |
|---|---|
| `cau_dai` | Long >35 tiếng đọc/câu |
| `nhieu_chi` | ≥4 tên chi/dòng; giữ kiểm hiện có |
| `ten_con_vat` | Gọi tuổi FS bằng tên con vật |
| `tts_khoa_dong` | Override pause/tempo trỏ sai dòng |
| `tts_van_tay_lech` | Fingerprint dòng không khớp |
| `cau_tron` | Dòng kết phẩy; hiệu lực như trên |
| `markup_leak` | URL/JSON key/{pd}/[PAUSE] trong lời; Short dùng integrity có sẵn |
| Lặp nguyên văn | Integrity Short hiện có; Long có điệp/motif nên không thêm chặn |
| Nguồn BUD thiếu | Guard BUD hiện có; không coi có URL là lời Phật đã đúng kinh |
| Toàn vẹn lời hiện có | `voices` sai số lượng/nhãn và ký hiệu kỹ thuật sót trong integrity |

Long lookup/tuyển tập, quota nhịp, rào nguồn, CTA, hook trừu tượng, ngân sách token v2/định nghĩa/insight/novelty, tone regex đều **CB/gợi ý**, không chặn văn phong. Hook `KHUNG_DAU_TRONG` là kiểm hình cũ, vẫn giữ; studio/pace_gate/hf_qa không đổi. Nguồn kinh vẫn do người kiểm với receipt, không tạo suy luận máy mới. V2 có preflight legacy riêng, xem [ma trận](lint-matrix.md); không tuyên bố đã đồng bộ code engine chưa được giao.

## 10. Bằng chứng và lịch sử
[075a](../research/2026-11-17-audio-script-research.md) phân biệt ĐO/QS/PO/KT/GT; số stay/retention cũ không chứng minh nhân quả. [Phụ lục X01–X20](conflicts-075b.md) ghi từng lựa chọn và luật cũ được thay, không xoá lịch sử. Pilot sau review giữ nguồn/giọng, chỉ đổi cách viết; so cùng kênh/khuôn/tuổi video/traffic. Không gọi lint xanh là tăng retention.
