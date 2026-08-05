-- Buộc GÓI bằng chứng phải thuộc đúng LẦN PHÂN TÍCH và đúng KÊNH của yêu cầu.
--
-- Trước migration này, `cursor_analysis_request` kiểm tra ba thứ ĐỘC LẬP nhau:
--   * kênh thuộc workspace
--   * lần phân tích thuộc (workspace, kênh)
--   * gói thuộc workspace            <-- chỉ có vậy
--
-- Không ràng buộc nào nối GÓI với LẦN PHÂN TÍCH hay KÊNH. Hệ quả: trong cùng
-- một workspace, có thể ghi một yêu cầu nói "lần chạy B của kênh B đã phân tích
-- gói P" trong khi P thực ra là gói của kênh A, lần chạy A. Mọi khoá ngoại đều
-- hợp lệ, và nguồn gốc được lưu lại là SAI — đúng loại lỗi mà toàn bộ chuỗi
-- provenance sinh ra để ngăn.
--
-- Thứ tự bắt buộc: tạo UNIQUE trước, rồi mới ADD FOREIGN KEY tham chiếu nó.

ALTER TABLE "analysis_package"
  ADD CONSTRAINT "analysis_package_id_ws_run_channel_key"
  UNIQUE ("id", "workspace_id", "analysis_run_id", "channel_id");
--> statement-breakpoint

ALTER TABLE "cursor_analysis_request"
  DROP CONSTRAINT IF EXISTS "cursor_request_package_workspace_fk";
--> statement-breakpoint

ALTER TABLE "cursor_analysis_request"
  ADD CONSTRAINT "cursor_request_package_lineage_fk"
  FOREIGN KEY ("analysis_package_id", "workspace_id", "analysis_run_id", "channel_id")
  REFERENCES "analysis_package" ("id", "workspace_id", "analysis_run_id", "channel_id")
  ON DELETE RESTRICT;
