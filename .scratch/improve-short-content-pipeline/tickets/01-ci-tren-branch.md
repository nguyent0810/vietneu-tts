# 01: CI chạy trên branch + tách nhóm test Windows / CI

**Spec:** `../spec.md` (Testing Decisions — Môi trường). Quyết định: D51, D55.

**What to build:** Mỗi lần push lên `feat/improve-short-content-pipeline` (và các branch feature sau này), CI chạy bộ test Python như trên `main`. Các test phụ thuộc khoá chỉ có trên Unix (registry/runner) được đánh dấu rõ là nhóm CI/container, để người chạy trên Windows biết trước test nào bị bỏ qua và vì sao, thay vì gặp lỗi import khó hiểu.

**Blocked by:** None (can start immediately)

**Prerequisite vận hành cho:** 04, 05a, 05b, 06 (cần CI để chạy test registry/runner). Không phải dependency của unit test độc lập.

**Status:** ready-for-agent

- [ ] Push lên branch feature kích hoạt job test Python trên CI Ubuntu
- [ ] Test phụ thuộc khoá Unix có một marker thống nhất; trên Windows chúng được skip kèm lý do rõ ràng
- [ ] Chạy bộ test trên Windows không có lỗi collection do thiếu module chỉ có trên Unix
- [ ] Có hướng dẫn ngắn cách chạy nhóm test CI trong container (máy dev có Docker, không có WSL distro)
- [ ] Không đổi hành vi của job CI hiện có cho `main`
