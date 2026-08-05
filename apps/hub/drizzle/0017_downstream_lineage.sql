-- Buộc KẾT QUẢ, KIỂM ĐỊNH và BẢN KÊ phải thuộc cùng một lần phân tích.
--
-- Migration 0016 mới chỉ nối yêu cầu -> gói. Các bảng phía sau vẫn kiểm tra
-- ĐỘC LẬP: kết quả trỏ tới một execution, một request và một channel, mỗi cái
-- chỉ cần cùng workspace. Trong cùng workspace W vẫn ghi được:
--
--   result{ execution = của lần chạy B, request = của kênh A, channel = A }
--
-- Mọi khoá ngoại hợp lệ, và payload của A được trình bày như kết quả của lần
-- chạy B. Nguồn gốc trông đầy đủ nhưng sai.
--
-- Cách đóng: gắn analysis_run_id vào cả ba bảng rồi ràng buộc phức hợp, để
-- execution và request buộc phải cùng một lần phân tích (và cùng kênh).
--
-- parent_execution_id trước đó KHÔNG có khoá ngoại nào — chuỗi retry có thể trỏ
-- tới một execution không liên quan hoặc một UUID không tồn tại.

ALTER TABLE "cursor_analysis_result" ADD COLUMN IF NOT EXISTS "analysis_run_id" uuid;
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest" ADD COLUMN IF NOT EXISTS "analysis_run_id" uuid;
--> statement-breakpoint
ALTER TABLE "analysis_validation" ADD COLUMN IF NOT EXISTS "analysis_run_id" uuid;
--> statement-breakpoint

-- Trigger bất biến chặn mọi UPDATE lên hai bảng này — kể cả lần ghi bù cột mới
-- của chính migration. Tắt trong phạm vi migration rồi bật lại ngay.
ALTER TABLE "cursor_analysis_result" DISABLE TRIGGER "cursor_result_immutability";
--> statement-breakpoint
ALTER TABLE "analysis_validation" DISABLE TRIGGER "analysis_validation_immutability";
--> statement-breakpoint

UPDATE "cursor_analysis_result" r SET "analysis_run_id" = e."analysis_run_id"
  FROM "llm_execution" e WHERE e."id" = r."llm_execution_id" AND r."analysis_run_id" IS NULL;
--> statement-breakpoint
UPDATE "cursor_execution_manifest" m SET "analysis_run_id" = e."analysis_run_id"
  FROM "llm_execution" e WHERE e."id" = m."llm_execution_id" AND m."analysis_run_id" IS NULL;
--> statement-breakpoint
UPDATE "analysis_validation" v SET "analysis_run_id" = e."analysis_run_id"
  FROM "llm_execution" e WHERE e."id" = v."llm_execution_id" AND v."analysis_run_id" IS NULL;
--> statement-breakpoint

ALTER TABLE "cursor_analysis_result" ENABLE TRIGGER "cursor_result_immutability";
--> statement-breakpoint
ALTER TABLE "analysis_validation" ENABLE TRIGGER "analysis_validation_immutability";
--> statement-breakpoint

ALTER TABLE "cursor_analysis_result" ALTER COLUMN "analysis_run_id" SET NOT NULL;
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest" ALTER COLUMN "analysis_run_id" SET NOT NULL;
--> statement-breakpoint
ALTER TABLE "analysis_validation" ALTER COLUMN "analysis_run_id" SET NOT NULL;
--> statement-breakpoint

-- Đích cho các khoá ngoại phức hợp. Phải tạo TRƯỚC khi tham chiếu.
ALTER TABLE "llm_execution" DROP CONSTRAINT IF EXISTS "llm_execution_id_ws_run_key";
--> statement-breakpoint
ALTER TABLE "llm_execution"
  ADD CONSTRAINT "llm_execution_id_ws_run_key" UNIQUE ("id", "workspace_id", "analysis_run_id");
--> statement-breakpoint
ALTER TABLE "cursor_analysis_request" DROP CONSTRAINT IF EXISTS "cursor_request_id_ws_run_channel_key";
--> statement-breakpoint
ALTER TABLE "cursor_analysis_request"
  ADD CONSTRAINT "cursor_request_id_ws_run_channel_key"
  UNIQUE ("id", "workspace_id", "analysis_run_id", "channel_id");
--> statement-breakpoint
-- Bản kê tham chiếu (id, workspace, run) — BA cột, nên cần một UNIQUE riêng cho
-- đúng bộ ba đó. Thiếu nó, PostgreSQL từ chối khoá ngoại với thông báo "no
-- unique constraint matching given keys".
ALTER TABLE "cursor_analysis_request" DROP CONSTRAINT IF EXISTS "cursor_request_id_ws_run_key";
--> statement-breakpoint
ALTER TABLE "cursor_analysis_request"
  ADD CONSTRAINT "cursor_request_id_ws_run_key"
  UNIQUE ("id", "workspace_id", "analysis_run_id");
--> statement-breakpoint

-- KẾT QUẢ: execution và request phải cùng lần chạy; request phải cùng kênh.
ALTER TABLE "cursor_analysis_result"
  DROP CONSTRAINT IF EXISTS "cursor_result_execution_workspace_fk";
--> statement-breakpoint
ALTER TABLE "cursor_analysis_result" DROP CONSTRAINT IF EXISTS "cursor_result_execution_run_fk";
--> statement-breakpoint
ALTER TABLE "cursor_analysis_result"
  ADD CONSTRAINT "cursor_result_execution_run_fk"
  FOREIGN KEY ("llm_execution_id", "workspace_id", "analysis_run_id")
  REFERENCES "llm_execution" ("id", "workspace_id", "analysis_run_id") ON DELETE RESTRICT;
--> statement-breakpoint
ALTER TABLE "cursor_analysis_result"
  DROP CONSTRAINT IF EXISTS "cursor_result_request_workspace_fk";
--> statement-breakpoint
ALTER TABLE "cursor_analysis_result" DROP CONSTRAINT IF EXISTS "cursor_result_request_run_channel_fk";
--> statement-breakpoint
ALTER TABLE "cursor_analysis_result"
  ADD CONSTRAINT "cursor_result_request_run_channel_fk"
  FOREIGN KEY ("request_id", "workspace_id", "analysis_run_id", "channel_id")
  REFERENCES "cursor_analysis_request" ("id", "workspace_id", "analysis_run_id", "channel_id")
  ON DELETE RESTRICT;
--> statement-breakpoint

-- BẢN KÊ: execution và request phải cùng lần chạy.
ALTER TABLE "cursor_execution_manifest"
  DROP CONSTRAINT IF EXISTS "cursor_manifest_execution_workspace_fk";
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest" DROP CONSTRAINT IF EXISTS "cursor_manifest_execution_run_fk";
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest"
  ADD CONSTRAINT "cursor_manifest_execution_run_fk"
  FOREIGN KEY ("llm_execution_id", "workspace_id", "analysis_run_id")
  REFERENCES "llm_execution" ("id", "workspace_id", "analysis_run_id") ON DELETE RESTRICT;
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest"
  DROP CONSTRAINT IF EXISTS "cursor_manifest_request_workspace_fk";
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest" DROP CONSTRAINT IF EXISTS "cursor_manifest_request_run_fk";
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest"
  ADD CONSTRAINT "cursor_manifest_request_run_fk"
  FOREIGN KEY ("request_id", "workspace_id", "analysis_run_id")
  REFERENCES "cursor_analysis_request" ("id", "workspace_id", "analysis_run_id")
  ON DELETE RESTRICT;
--> statement-breakpoint

-- Chuỗi retry phải trỏ tới execution CÓ THẬT, cùng workspace.
ALTER TABLE "cursor_execution_manifest" DROP CONSTRAINT IF EXISTS "cursor_manifest_parent_execution_fk";
--> statement-breakpoint
ALTER TABLE "cursor_execution_manifest"
  ADD CONSTRAINT "cursor_manifest_parent_execution_fk"
  FOREIGN KEY ("parent_execution_id", "workspace_id")
  REFERENCES "llm_execution" ("id", "workspace_id") ON DELETE RESTRICT;
--> statement-breakpoint

-- KIỂM ĐỊNH: execution phải cùng lần chạy; kênh phải là kênh của lần chạy đó.
ALTER TABLE "analysis_validation"
  DROP CONSTRAINT IF EXISTS "analysis_validation_execution_workspace_fk";
--> statement-breakpoint
ALTER TABLE "analysis_validation" DROP CONSTRAINT IF EXISTS "analysis_validation_execution_run_fk";
--> statement-breakpoint
ALTER TABLE "analysis_validation"
  ADD CONSTRAINT "analysis_validation_execution_run_fk"
  FOREIGN KEY ("llm_execution_id", "workspace_id", "analysis_run_id")
  REFERENCES "llm_execution" ("id", "workspace_id", "analysis_run_id") ON DELETE RESTRICT;
--> statement-breakpoint
ALTER TABLE "analysis_validation" DROP CONSTRAINT IF EXISTS "analysis_validation_run_channel_fk";
--> statement-breakpoint
ALTER TABLE "analysis_validation"
  ADD CONSTRAINT "analysis_validation_run_channel_fk"
  FOREIGN KEY ("analysis_run_id", "workspace_id", "channel_id")
  REFERENCES "analysis_run" ("id", "workspace_id", "channel_id") ON DELETE RESTRICT;
--> statement-breakpoint

-- KẾT QUẢ: kênh cũng phải là kênh của lần chạy đó.
ALTER TABLE "cursor_analysis_result" DROP CONSTRAINT IF EXISTS "cursor_result_run_channel_fk";
--> statement-breakpoint
ALTER TABLE "cursor_analysis_result"
  ADD CONSTRAINT "cursor_result_run_channel_fk"
  FOREIGN KEY ("analysis_run_id", "workspace_id", "channel_id")
  REFERENCES "analysis_run" ("id", "workspace_id", "channel_id") ON DELETE RESTRICT;
