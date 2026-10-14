-- Buộc LẦN CHẠY CHA của một retry phải thuộc CÙNG lần phân tích.
--
-- 0017 gắn khoá ngoại cho parent_execution_id nhưng chỉ theo (id, workspace_id).
-- Thiếu analysis_run_id, nên một bản kê của lần chạy B/kênh B vẫn khai được cha
-- là execution của lần chạy A/kênh A trong cùng workspace, với mọi khoá ngoại
-- hợp lệ. Chuỗi retry khi ấy bắc ngang hai lần phân tích — đúng kiểu trộn nguồn
-- gốc mà 0017 sinh ra để ngăn.

ALTER TABLE "cursor_execution_manifest"
  DROP CONSTRAINT IF EXISTS "cursor_manifest_parent_execution_fk";
--> statement-breakpoint

ALTER TABLE "cursor_execution_manifest"
  ADD CONSTRAINT "cursor_manifest_parent_execution_run_fk"
  FOREIGN KEY ("parent_execution_id", "workspace_id", "analysis_run_id")
  REFERENCES "llm_execution" ("id", "workspace_id", "analysis_run_id")
  ON DELETE RESTRICT;
