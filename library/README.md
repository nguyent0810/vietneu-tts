# Thư viện kỹ thuật dựng video

Tạo snapshot định kỳ:

```sh
python3 library/tools/inventory.py fetch
python3 library/tools/inventory.py build
python3 library/tools/inventory.py report --offline
```

`fetch` tải metadata/dữ liệu văn bản GitHub về `chunks_cache/library_src/`, không tải video/ảnh. Lỗi từng nguồn được ghi vào báo cáo; `--offline` chỉ dùng cache. `build` chuẩn hóa, gắn nhãn theo `inventory/taxonomy.json` và khử trùng chính xác + gần trùng (Jaccard shingle ký tự 5-gram; ngưỡng mặc định 0.8). `report` cập nhật `inventory/{records,clusters}.jsonl`, `techniques.json`, `inventory/report.md` và báo cáo epic.

Thêm nguồn bằng adapter Python trả record theo `record(...)` trong `inventory.py`; pipeline tagging/dedup/report dùng chung, không cần sửa cấu trúc đầu ra. Taxonomy có thể mở rộng bằng cách thêm kỹ thuật và từ khóa vào JSON.

Ví dụ crontab hằng ngày lúc 03:15 (giờ máy):

```cron
15 3 * * * cd /path/to/repo && python3 library/tools/inventory.py fetch && python3 library/tools/inventory.py report --offline >> library/inventory/cron.log 2>&1
```
