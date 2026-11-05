# GH-147 · Codex: Long MIM/CK bỏ nhãn "ẢNH MINH HỌA" trên ảnh AI

Issue: https://github.com/nguyent0810/vietneu-tts/issues/147. Đọc kỹ luật mới trong issue và `../docs/adr/0004-thu-bac-nguon-hinh-va-anh-ai.md` (phần Hệ quả).

**Hạn:** 60 phút.

## Hiện trạng
- Khoảng 65 file `data/long/*/gen_scenes*.py` có helper `photo()`. Với ảnh AI (`img` bắt đầu bằng `ai`), helper gắn `illus: AIL` ("ẢNH MINH HỌA"), `credit: False`, `tone: "color"`.
- Engine `motion/hf/assets/engine/casewide.js:75` in `s.illus` lên khung.
- Một số cảnh còn đặt `illus="ẢNH MINH HỌA · …"` cho **ảnh thật**, ví dụ máy cùng loại. Các nhãn này phải **giữ**.

## Việc
1. **Gỡ nhãn ở bước dựng, một chỗ chung, không sửa 65 file gen_scenes.**
   - Trong `motion/long/build_long.py`, ở chỗ nạp hoặc ghép cảnh trước khi sinh HTML, làm như sau với topic kênh MIM/CK (xác định kênh như cách file đang làm, ví dụ `_channels()`): cảnh nào có ảnh AI thì bỏ trường `illus`.
     - Nhận biết ảnh AI theo tên `aiNN` và/hoặc sidecar `img/aiNN.json` có `file` bắt đầu bằng `EXT:ai`.
   - Giữ `credit: False`. Không để engine in "ẢNH: TƯ LIỆU" cho ảnh AI.
   - Không đụng CL: các topic CL như `bulger`, `capone`… giữ nguyên hành vi cũ.
   - Không đổi `illus` của ảnh thật, và không đổi nhãn "VIDEO MINH HỌA" của clip.
2. **Mô tả video.** Topic MIM/CK có dùng ảnh AI thì `description.txt` (ở chỗ đang sinh file này) phải có đúng một dòng "Một số hình minh hoạ được tạo bằng AI.". Không thêm trùng nếu dòng đã có.
3. **Khai báo nội dung tổng hợp.** Spec Long có trường tùy chọn `"synthetic_realistic": true`. Khi có trường này, `publish_long.py` gửi `status.containsSyntheticMedia = true` lúc upload. Mặc định không gửi.
   - Không gọi API trong test, chỉ kiểm payload.
4. **Tài liệu.**
   - Sửa `docs/codex/long-rules.md` (dòng ~41 và ~158), `docs/codex/long-cheatsheet.md` (dòng ~28), `AGENTS.md` (mục Ảnh) cho đúng luật mới.
   - `docs/pm/2026-10-28-webauto-ap-dung.md` và `docs/pm/2026-10-29-anh-tinh-long-mim-ck.md`: thêm một dòng "thay bởi #147", không viết lại.
5. **Test** trong `tests/`:
   - ảnh AI MIM/CK → không còn `illus`, `credit` vẫn False;
   - ảnh thật có `illus` → giữ nguyên;
   - topic CL → giữ nguyên;
   - dòng mô tả được thêm đúng một lần;
   - payload có hoặc không có `containsSyntheticMedia` theo spec.

   Chạy `python -m pytest tests -q`.

## Được ghi
`motion/long/build_long.py`, `motion/long/publish_long.py`, file test mới trong `tests/`, các tài liệu kể ở mục 4, báo cáo `docs/pm/tickets/GH-147-codex-report.md`.

**Không:**
- sửa `data/long/*/gen_scenes*.py`, engine JS hoặc CSS;
- render;
- upload, đổi lịch;
- commit;
- đọc credentials.

## Báo cáo
- Diff tóm tắt từng file.
- Kết quả pytest (dán dòng cuối).
- Cách nhận biết ảnh AI đã chọn.
- Topic MIM/CK nào chưa upload có ảnh AI (liệt kê).

Câu trả lời cuối: tối đa 3 dòng.
