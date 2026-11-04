# GH-31 fix 6 — báo cáo Codex

## Phạm vi và thay đổi

- Chỉ sửa `factory/trend/cluster.py`, `factory/trend/benchmark.py`, test và fixture trend; không sửa benchmark JSON, không thêm nguồn, không ghi `state.sqlite`, không đổi lịch, commit hoặc đăng tải.
- `cluster.py` có danh sách thực thể chung tĩnh: hãng lớn, nền tảng/phần mềm phổ biến, tiền tệ/số tiền, ngân hàng/chứng khoán và các cụm ngành chung. Số trần không còn là token Jaccard. Một thực thể xuất hiện ở hơn 5% bài trong cửa sổ cũng tự thành thực thể chung.
- Link chỉ dùng thực thể chung khi Jaccard tiêu đề đạt 0,35; link có thực thể đặc thù vẫn dùng ngưỡng cơ sở 0,25. Sau connected-components, cụm có trung bình tương đồng nội bộ dưới 0,30 được partition complete-linkage để chặn chuỗi A–B–C.
- Nhánh thực thể benchmark chỉ nhận anchor đặc thù (tên/định danh nhiều từ); thực thể chung không được làm anchor. Tiêu đề phải có ít nhất hai token nội dung của nhãn. Nhánh Jaccard giữ đúng ngưỡng 0,25.
- Thêm fixture `tests/fixtures/trend/lead_match_regression.json`: 10 cặp Lead xác nhận đúng và 10 cặp sai. Test bao phủ thêm thực thể chung tĩnh, thực thể vượt 5% cửa sổ và chuỗi bắc cầu.

## Kiểm tra đã chạy

```text
python -m pytest tests/test_trend_scanner.py -q
22 passed, 1 warning in 0.25s
```

Warning duy nhất là quyền ghi cache `.pytest_cache` (WinError 5); không phải lỗi test/lint.

Cluster, `report` và `benchmark` chạy trên bản sao tạm của `data/trend/trend.sqlite`, với mốc `2026-11-02T23:00:00Z`:

```text
clusters: 144
report: %TEMP%\gh31-fix6-…\output-final2\2026-11-02\23.md
benchmark: %TEMP%\gh31-fix6-…\benchmark-final2.md
```

Không có lỗi lint còn lại trong phạm vi ticket.

## Recall trước/sau

“Trước” là recall ứng viên đã báo trong brief (MIM 12/18, CK 8/20). “Sau” là chạy lại trên bản sao bằng luật mới. Recall bao phủ = có bài khớp trong cửa sổ 48 giờ; recall ứng viên = có bài khớp nằm trong event hợp lệ và qua lọc kênh.

| Kênh | Ứng viên trước | Bao phủ sau | Ứng viên sau | High: bao phủ / ứng viên | Medium: bao phủ / ứng viên |
|---|---:|---:|---:|---:|---:|
| MIM | 12/18 (66,7%) | 9/18 (50,0%) | 5/18 (27,8%) | 6/9 / 4/9 | 3/9 / 1/9 |
| CK | 8/20 (40,0%) | 8/20 (40,0%) | 7/20 (35,0%) | 7/14 / 6/14 | 1/6 / 1/6 |

Kết quả MIM sát ước lượng Lead (khoảng 4/18); CK còn cao hơn ước lượng 6/20 một event. `ck_14` vẫn được bắt bởi tiêu đề trực tiếp “Giá USD hôm nay 1.11… dưới 26.000 đồng” qua nhánh Jaccard 0,280; cặp sai Lead nêu là bài “Báo Thái Lan…” đã không còn khớp. Tương tự, cặp sai `mim_07` dùng bài YouTube/Android trong fixture đã bị chặn; một bài Android có nội dung trùng mạnh với nhãn vẫn bắt qua Jaccard 0,25. Đây là hệ quả trực tiếp của yêu cầu giữ nhánh Jaccard ở 0,25, không phải ngoại lệ theo từng nhãn.

## Soát gom quá đà — 10 event lớn nhất

1. **hackerbooks · hackerhack** (3): “Show HN: HackerBooks…”, “Show HN: Wikihack…”, “Show HN: HackerHack…”.
2. **doc · ong loic faussier** (3): “Sacombank có quyền tổng giám đốc mới”, “Sacombank thay tổng giám đốc lần thứ 3 trong năm”, “Ông Loic Faussier thôi làm Tổng giám đốc…”.
3. **truc · trung** (3): ba tiêu đề kết quả xổ số miền Nam/miền Trung ngày 2.11.
4. **bien** (2): “Biến phục hồi hệ sinh thái…”, “Biến sức mạnh của hệ sinh thái khách hàng…”.
5. **bom · can gio** (2): “Bom tấn Cần Giờ…”, “Vinhomes Green Paradise…”, cùng vòng bình chọn 7 kỳ quan đô thị tương lai.
6. **sieu el nino · viet** (2): “Siêu El Nino khiến mùa mưa…”, “Siêu El Nino ‘hâm nóng’ giá gạo Việt”.
7. **co · dak lak dang** (2): hai bản sao tiêu đề về cô gái Đắk Lắk đăng quang Hoa hậu Việt Nam.
8. **doanh · vietjet** (2): hai tiêu đề doanh thu Vietjet tăng 41% và mở rộng mạng bay.
9. **google · phan lan dieu** (1): “Phần Lan điều tra hình sự Google”.
10. **pin** (1): “Pin mặt trời sắp vượt giới hạn vật lý tồn tại hơn 60 năm?”.

Các cụm Google vệ tinh và vàng/xăng dầu trước đây là điểm rủi ro đã không còn nằm trong danh sách cụm lớn: Google vệ tinh chỉ giữ hai tiêu đề cùng nội dung; vàng và xăng dầu được tách.

## 10 cặp khớp điểm thấp nhất

1. `mim_15` — “Lợi nhuận LG Electronics tăng gần 56%…” — 0,106, entity.
2. `ck_10` — “Ông Loic Faussier thôi làm Tổng giám đốc…” — 0,172, entity.
3. `ck_03` — “Giá vàng hôm nay 2.11.2026…” — 0,176, entity.
4. `ck_10` — “Sacombank có quyền tổng giám đốc mới” — 0,208, entity.
5. `ck_14` — “Giá USD hôm nay 1.11.2026…” — 0,280, Jaccard.
6. `ck_09` — “Loạt ngân hàng báo lãi ‘khủng’…” — 0,281, Jaccard.
7. `mim_03` — “Giữa lúc OpenAI ‘húp’ hết RAM…” — 0,281, entity.
8. `mim_03` — “CEO OpenAI gây tranh cãi…” — 0,286, Jaccard.
9. `mim_05` — “Vệ tinh AI của Google vừa ‘làm thơ’…” — 0,304, entity.
10. `mim_10` — “Cách lấy lại 15 GB dung lượng…” — 0,308, Jaccard.

Không có khẳng định nguồn ngoài dữ liệu/ticket cần kiểm factcheck.
