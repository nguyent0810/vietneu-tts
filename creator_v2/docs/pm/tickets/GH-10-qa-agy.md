# GH-10 · QA cảnh `mim-jobs-1985`: danh sách lỗi theo scene ID (agy)

Issue: https://github.com/nguyent0810/Youtube_Creator_V2/issues/10

**Không render bản thật.** Không sửa `data/long/**`, engine hay code. Không đăng, không commit.

## Được ghi

- `output/long/mim-jobs-1985/qa/**` (ảnh bằng chứng)
- báo cáo `docs/pm/tickets/GH-10-qa-report.md`

## Bối cảnh

Cảnh đã được viết lại sau lần soát trước của bạn (`docs/pm/tickets/YCV-ju9q-M1-render-report.md`).

- Số liệu hiện tại: 127 cảnh, 19 clip, 12 ảnh; chữ trên nền trống 13,67%; `long_gate` ĐẠT.
- HTML 9 chương ở `output/long/mim-jobs-1985/`. Spec chương ở `data/long/mim-jobs-1985/chNN.json`.

## Việc

1. Soát **từng cảnh**. Scene ID = `chNN#i`, trong đó `i` là chỉ số trong mảng `scenes` của `chNN.json`, đếm từ 0.
2. Kiểm tra từng nhóm:
   - **Kỹ thuật:**
     - chữ tràn hoặc bị cắt;
     - crop ảnh dọc làm mất mặt hay mất chủ thể (xem `focus`);
     - asset thiếu hoặc là stand-in;
     - neo sai thời điểm so với lời đọc (đối chiếu `timing.json`);
     - màn trống quá 1 giây;
     - clip lộ logo hoặc chữ đọc được (xem `qa_clips.jpg`).
   - **Nội dung:**
     - chữ trên màn hình mất dấu tiếng Việt;
     - chữ là đoạn đầu câu bị cắt lửng;
     - đơn vị hoặc số sai so với `script.md` và `factcheck.md`;
     - hình không khớp nghĩa câu;
     - hai nút `org` trùng chữ;
     - ảnh AI dùng sai chỗ, hoặc thiếu `"credit": false`.
   - **Nguồn:** ảnh ngoài AI phải là PD, CC0 hoặc CC BY và có ghi công.
3. **Bằng chứng:** khung hình hoặc trích dẫn `data.js`/`chNN.json`.
   - Có thể chụp khung bằng `npx -y -p node@22 -p hyperframes@0.8.75 hyperframes snapshot` hoặc `check --at`, hoặc `build_long.py mim-jobs-1985 render chNN --draft` cho riêng chương cần xem. Không chạy `final`.
   - Lưu ảnh bằng chứng vào `output/long/mim-jobs-1985/qa/`.

## Báo cáo

Ghi `docs/pm/tickets/GH-10-qa-report.md`, dạng bảng:

| scene ID | mốc giây | severity | loại | mô tả | bằng chứng (file hoặc trích) | đề xuất sửa |

Severity có 3 mức:
- **chặn:** sai sự thật, mất mặt người hay chủ thể, chữ cắt hoặc tràn, mất asset;
- **nên sửa;**
- **nhỏ.**

Cuối báo cáo ghi tổng số lỗi theo từng severity.
