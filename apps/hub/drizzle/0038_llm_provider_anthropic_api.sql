-- 0038 — thêm ANTHROPIC_API vào enum nhà cung cấp.
--
-- Vì sao cần: `llm_provider` hiện chỉ có ('CURSOR_CLI', 'CODEX_CLI'). Mọi hàng
-- `llm_execution` đều phải khai nhà cung cấp, nên nếu không thêm giá trị này thì
-- một lô chạy bằng Anthropic API KHÔNG ghi được vào database — không phải "ghi
-- sai", mà là chặn ngay ở tầng kiểu.
--
-- Vì sao THÊM chứ không đổi: enum là hợp đồng của dữ liệu đã có. 32 hàng
-- COMPOSITE trong database CHÍNH và toàn bộ lô thăm dò đều mang 'CURSOR_CLI';
-- đổi tên hay bỏ giá trị cũ sẽ làm hỏng chính bằng chứng mà các lô ấy để lại.
--
-- Đây là thay đổi CỘNG THÊM thuần tuý: không trigger nào, không ràng buộc nào,
-- không hàng nào bị đụng tới. Nó không thể làm đỏ một lô đang chạy.
--
-- HỆ QUẢ VỀ ĐO ĐẠC, ghi ở đây để không ai gộp nhầm: một lô chạy bằng
-- ANTHROPIC_API là lô RIÊNG. Nó không gộp được với lô CURSOR_CLI, đúng theo quy
-- tắc đã áp cho việc đổi bản runtime của `cursor-agent` — đổi người phân tích
-- còn nặng hơn đổi bản cài đặt.

ALTER TYPE "llm_provider" ADD VALUE IF NOT EXISTS 'ANTHROPIC_API';
