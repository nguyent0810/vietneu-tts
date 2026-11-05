# Components Registry (Tham khảo)

> **Trạng thái:** KHÔNG DÙNG trong runtime Studio (PO duyệt 05/11/2026, audit #140).

- Studio dựng composition trực tiếp từ danh sách thiết bị/device (`studio.py` và `hyperframes_short/studio/devices/`).
- Các component registry trong thư mục này (`constellation-hub.html`, `grain-overlay.html`, `ink-bleed-reveal.html`, `particle-text-dissolve.html`, `text-shimmer.html`, v.v.) hiện chỉ dùng để **tham khảo** mẫu hiệu ứng, không được nạp hay gọi tự động bởi runtime/pipeline sản xuất.
- Sẽ xét lại việc tích hợp khi có nhu cầu cụ thể.
- Ngoại lệ đang chờ: PR #142 (nháp) nối `ink-bleed-reveal` và `text-shimmer` vào Studio dạng opt-in. Chỉ quyết sau khi A/B trên kênh VSD (sau khi VSD đăng đủ 24/24).
