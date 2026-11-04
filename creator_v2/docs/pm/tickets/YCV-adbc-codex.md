# YCV-adbc · Cổng phủ hình và danh sách chỗ cần bù ảnh cho Long MIM/CK (Codex)

## Bối cảnh

Đọc trước `docs/pm/2026-10-29-anh-tinh-long-mim-ck.md`. Số liệu chính:
- 82–87% thời lượng Long là đồ họa và chữ.
- Nhiều video có 40–55% thời lượng chỉ là chữ.
- Có đoạn dài 45–72 giây liền không có ảnh hay clip.
- Cách đo nằm trong mục "Cách đo" của file trên. Dùng đúng cách đó.

Công cụ sinh prompt ảnh của vietneu: `.ref/vietneu-main/library/tools/prompt_builder.py`.
- Đi kèm `library/assets/lexicon/chung.json` và mẫu kênh `library/channels/_thu_lich_su.yaml`, `_mau.yaml`.
- Prompt sinh ra tất định, không gọi LLM.
- Tool đang đọc đường dẫn `output/cl_staging/...` của repo bên đó.
- Chỉ đọc, **không sửa gì trong `.ref/`**.

## Việc

1. **Viết `motion/long/coverage_lint.py`.**
   - Đo theo từng Long `mim-*` và `ck-*`:
     - phần trăm thời lượng chỉ có chữ;
     - các đoạn liền không có hình, mỗi đoạn kèm câu bắt đầu và kết thúc;
     - ảnh tĩnh dài quá 8 giây.
   - Ngưỡng nháp, đặt ở đầu file:
     - không có đoạn nào quá 25 giây không có hình;
     - phần chỉ chữ không quá 30%;
     - ảnh tĩnh không quá 8 giây.
   - Gọi: `python motion/long/coverage_lint.py <topic>` hoặc `--all`; thoát mã 1 khi vượt ngưỡng.
   - Chạy trên 54 Long cũ. Đề xuất ngưỡng chính thức sao cho các video tốt nhất qua được: `ck-f1`, `ck-i1`, `mim-qwerty`, `mim-flappy-bird`, `mim-ai-jobs`.
2. **Lập danh sách chỗ cần bù** cho 2 Long thử: `mim-ai-hallucinate` và `ck-d2-fomo`.
   - Mỗi đoạn không có hình dài quá 25 giây cần một hoặc hai hình.
   - Ghi `output/long/<topic>/coverage_gaps.json`, mỗi mục gồm:
     - chương, câu, lời đọc;
     - gợi ý từ khóa tìm ảnh tự do: Wikimedia/Openverse là PD, CC0 hoặc CC BY; Pexels chỉ dùng cho clip;
     - prompt ảnh AI dự phòng, sinh bằng luật của `prompt_builder`, có thể viết adapter `motion/long/ai_prompt.py` đọc lexicon và hồ sơ bên dưới.
3. **Viết nháp hồ sơ kênh** theo mẫu `_thu_lich_su.yaml`: `docs/pm/ai-image/mim.yaml` và `docs/pm/ai-image/ck.yaml`.
   - Mỗi hồ sơ có khối phong cách, chủ thể hay gặp và cụm cấm.
   - Cả hai kênh cấm chữ, số, logo, giao diện ứng dụng và mặt người nhận ra được.
   - CK cấm thêm tên ngân hàng, công ty chứng khoán, hãng xe, mã cổ phiếu và biểu tượng sàn.
   - MIM tránh hình người nổi tiếng thật.
4. **Test:** `tests/test_long_coverage.py`, dùng dữ liệu giả.

## Giới hạn

- Chỉ được ghi các file sau:
  - `motion/long/coverage_lint.py`
  - `motion/long/ai_prompt.py`
  - `tests/test_long_coverage.py`
  - `output/long/*/coverage_gaps.json`
  - `docs/pm/ai-image/*.yaml`
  - báo cáo
- **Không gọi** Grok Bot, webhook hay bất kỳ API sinh ảnh nào. Claude sinh ảnh sau khi review.
- Không render, không đăng, không commit, không sửa `data/long/**`. Không áp cho CL.
- Một agent khác đang viết `motion/long/scene_rules.py`: không đụng vào file đó.

## Báo cáo

Ghi `docs/pm/tickets/YCV-adbc-report.md`, gồm:
- bảng 54 Long theo ngưỡng nháp;
- ngưỡng đề xuất và lý do;
- số chỗ cần bù của 2 Long thử, kèm 3 prompt mẫu mỗi kênh;
- kết quả `pytest`.
