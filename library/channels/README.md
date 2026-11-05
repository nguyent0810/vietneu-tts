# Hồ sơ kênh (`library/channels/`)

Thư mục chứa hồ sơ cấu hình kênh (`*.yaml`). Lưu ý: các file `.yaml` tại đây được định dạng là JSON hợp lệ để tương thích với bộ nạp `channel_profile.py` (`json.loads`).

## Khối Packaging là METADATA

> **Quyết định PO (05/11/2026, audit #140):**
> Khối `"packaging"` trong các hồ sơ kênh (`bud.yaml`, `fs.yaml`, `lich_su.yaml`, v.v.) hoàn toàn là **METADATA** phục vụ biên tập và tài liệu tham khảo.
> **Runtime / pipeline sản xuất KHÔNG đọc hay phụ thuộc vào khối này.**
> Dữ liệu trong các file được giữ nguyên, không thay đổi logic runtime.
