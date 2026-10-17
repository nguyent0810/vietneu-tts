# VieNeu Studio (desktop tool sản xuất video)

Công cụ biến nội dung đầu vào thành video có lời đọc tiếng Việt cho nhiều kênh YouTube, theo bộ luật riêng của từng kênh.

## Ngôn ngữ

### Kênh và luật

**Kênh**:
Một kênh YouTube mà tool sản xuất video cho (ví dụ FS – Phong Thủy, BUD – Phật giáo).
_Avoid_: channel, domain, topic

**Ruleset**:
Bộ luật của một kênh: giọng đọc, phong cách hình, luật kịch bản, luật đăng, ngưỡng kiểm tra. Thêm kênh mới bằng cách thêm ruleset, không sửa code.
_Avoid_: profile, config, preset kênh

**Chuỗi**:
Một dòng nội dung lặp lại trong một kênh, có cùng cách tìm dữ kiện và cùng khuôn kể (ví dụ "Năm sinh + mệnh", "Tuổi X năm 2027").
_Avoid_: lane, series, category

### Nội dung

**Dữ kiện**:
Thông tin tính bằng thuật toán hoặc tra từ nguồn cố định, dùng làm căn cứ cho kịch bản (can chi, nạp âm, Tam Tai, số kinh).
_Avoid_: facts, data

**Kịch bản**:
Các dòng lời đọc của một video, theo thứ tự đọc.
_Avoid_: script, lời thoại

**Spec dựng**:
Mô tả cảnh, hình, chữ và mốc thời gian của một video, dùng để dựng hình.
_Avoid_: plan, composition

**Cảnh**:
Một đoạn hình liên tục trong spec dựng (chữ, ảnh, video hoặc sơ đồ), có mốc bắt đầu và kết thúc; không bắt buộc trùng ranh giới câu.
_Avoid_: scene, beat, shot

**Lớp phủ**:
Phần hình đặt chồng lên cảnh chính (chữ thêm, sticker, B-roll đè lên lời đọc).
_Avoid_: overlay, layer

**Chỉnh tay**:
Thay đổi do người vận hành làm trực tiếp trên một cảnh hoặc lớp phủ; được giữ nguyên khi tool tự dựng lại.
_Avoid_: override, manual edit

**Dự án**:
Một video đang được làm trong tool, từ đầu vào tới bản xuất.
_Avoid_: job, episode

### Vận hành

**Người vận hành**:
Người dùng tool để làm video; không cần biết lập trình.
_Avoid_: user, editor, dev

**Điểm duyệt**:
Chỗ quy trình dừng chờ người vận hành xác nhận (duyệt kịch bản, duyệt ảnh tư liệu). Ruleset có thể tắt để chạy tự động hoàn toàn.
_Avoid_: checkpoint, gate

**Nhà cung cấp LLM**:
Nguồn mô hình ngôn ngữ mà tool gọi cho các bước cần viết hoặc phán đoán: một API, hoặc một agent CLI cài trên máy.
_Avoid_: AI, model, agent
